# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib.parse
from config import XFYUN_APPID, XFYUN_SECRET_KEY

class VoiceRecognizer:
    """讯飞语音识别"""
    
    def __init__(self, appid, secret_key):
        self.appid = appid
        self.secret_key = secret_key
        self.host = 'https://raasr.xfyun.cn/v2/api'
    
    def _sign(self, ts):
        """生成签名"""
        md5 = hashlib.md5((self.appid + ts).encode()).hexdigest()
        return base64.b64encode(
            hmac.new(self.secret_key.encode(), md5.encode(), hashlib.sha1).digest()
        ).decode()
    
    def recognize(self, audio_path):
        """识别音频文件"""
        ts = str(int(time.time()))
        sign = self._sign(ts)
            
        # 检查音频文件
        if not os.path.exists(audio_path):
            raise Exception(f"音频文件不存在: {audio_path}")
            
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            raise Exception(f"音频文件为空: {audio_path}")
            
        print(f"音频文件大小: {file_size} bytes")
            
        # 上传音频
        with open(audio_path, 'rb') as f:
            data = f.read()
            
        params = {
            'appId': self.appid, 'signa': sign, 'ts': ts,
            'fileSize': len(data), 'fileName': os.path.basename(audio_path), 'duration': '200'
        }
            
        print(f"上传参数: {params}")
            
        resp = requests.post(
            f"{self.host}/upload?{urllib.parse.urlencode(params)}",
            headers={"Content-type": "application/json"}, data=data
        )
            
        upload_result = resp.json()
        print(f"上传响应: {upload_result}")
            
        if upload_result.get('code') != '000000':
            raise Exception(f"上传失败: {upload_result.get('descInfo', '未知错误')}")
            
        order_id = upload_result['content']['orderId']
            
        # 获取结果 - 添加状态检查逻辑
        params = {'appId': self.appid, 'signa': sign, 'ts': ts, 'orderId': order_id, 'resultType': 'transfer,predict'}
            
        while True:
            resp = requests.post(
                f"{self.host}/getResult?{urllib.parse.urlencode(params)}",
                headers={"Content-type": "application/json"}
            )
            result = resp.json()
            print(f"查询响应: {result}")
                
            if result.get('code') != '000000':
                raise Exception(f"查询失败: {result.get('descInfo', '未知错误')}")
                
            status = result['content']['orderInfo']['status']
            print(f"识别状态: {status}")
                
            if status == 4:  # 完成
                return self._extract_text(result)
            elif status == 3:  # 处理中
                print("识别处理中，等待5秒...")
                time.sleep(5)
            elif status == -1:
                # 检查是否有识别结果
                if result['content'].get('orderResult'):
                    return self._extract_text(result)  # 有结果就返回
                else:
                    error_msg = result['content']['orderInfo'].get('failType', '未知错误')
                    raise Exception(f"识别失败: {error_msg}")
            else:
                raise Exception(f"未知状态: {status}")
    def _extract_text(self, result):
        """提取文本"""
        try:
            order_result = json.loads(result['content']['orderResult'])
            text = ''
            for item in order_result.get('lattice', []):
                json_1best = json.loads(item.get('json_1best', '{}'))
                for ws_list in json_1best.get('st', {}).get('rt', []):
                    for ws in ws_list.get('ws', []):
                        for cw in ws.get('cw', []):
                            text += cw.get('w', '')
            return text
        except:
            return ''

def get_latest_audio_file(audio_dir="audio"):
    """获取最新的音频文件"""
    if not os.path.exists(audio_dir):
        return None
    
    audio_files = []
    for root, _, files in os.walk(audio_dir):
        for file in files:
            if file.lower().endswith(('.wav', '.mp3', '.m4a')):
                file_path = os.path.join(root, file)
                audio_files.append((file_path, os.path.getmtime(file_path)))
    
    if not audio_files:
        return None
    
    # 按修改时间排序，返回最新的
    return max(audio_files, key=lambda x: x[1])[0] # 返回最新的文件的完整路径字符串

def process_latest_audio(appid, secret_key, audio_dir="audio", output_dir="sample"):
    """只处理最新的音频文件"""
    latest_file = get_latest_audio_file(audio_dir) # 获取最新的音频文件的完整路径
    if not latest_file:
        print(f"在 {audio_dir} 中没有找到音频文件")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    recognizer = VoiceRecognizer(appid, secret_key) # 创建讯飞音频类对象
    
    print(f"处理最新文件: {latest_file}")
    
    try:
        text = recognizer.recognize(latest_file) # 调讯飞api返回处理后的文本给变量
        filename = os.path.splitext(os.path.basename(latest_file))[0] # 获取存储文本的文件夹并写入
        output_path = os.path.join(output_dir, f"{filename}_transcription.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"保存至: {output_path}")
        return text,output_path
    except Exception as e:
        print(f"处理失败: {e}")
        return None

def get_audio_text_path(appid, secret_key):
    """获取最新音频的转录文本和路径"""
    return process_latest_audio(appid, secret_key)

if __name__ == '__main__':
    appid, secret_key = XFYUN_APPID, XFYUN_SECRET_KEY
    process_latest_audio(appid, secret_key)
