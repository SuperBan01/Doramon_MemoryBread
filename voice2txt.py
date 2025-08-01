# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'


def extract_chinese_text(result):
    """
    从讯飞语音识别结果中提取纯中文文本
    """
    try:
        order_result = json.loads(result['content']['orderResult'])
        lattice = order_result.get('lattice', [])
        text = ''
        for item in lattice:
            json_1best = json.loads(item.get('json_1best', '{}'))
            rt = json_1best.get('st', {}).get('rt', [])
            for ws_list in rt:
                for ws in ws_list.get('ws', []):
                    for cw in ws.get('cw', []):
                        text += cw.get('w', '')
        return text
    except Exception as e:
        print(f"解析结果时出错: {e}")
        return ''

class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        """
        初始化讯飞语音识别API请求类
        """
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        """
        生成API请求签名
        """
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa


    def upload(self):
        """
        向讯飞服务器发送请求，返回结果为请求是否成功
        """
        print("上传部分：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url =lfasr_host + api_upload+"?"+urllib.parse.urlencode(param_dict),
                                headers = {"Content-type":"application/json"},data=data)
        print("upload_url:",response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result


    def get_result(self):
        """
        获取语音识别结果，为一系列很多富有格式的内容；通过提取中文方法获取真实文本
        集成了有上面的上传音频的函数
        """
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict['orderId'] = orderId
        param_dict['resultType'] = "transfer,predict"
        print("")
        print("查询部分：")
        print("get result参数：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            # print(result)
            status = result['content']['orderInfo']['status']
            print("status=",status)
            if status == 4:
                break
            time.sleep(5)
        # print("get_result resp:",result)
        chinese_text = extract_chinese_text(result)
        print("纯中文文本输出：", chinese_text)
        return result

    def save_result_to_file(self, result):
        """
        将识别结果保存到文件
        """
        file_name = os.path.basename(self.upload_file_path)
        base_name = os.path.splitext(file_name)[0]
        output_path = os.path.join("sample", f"{base_name}_transcription.txt")
        try:
            chinese_text = extract_chinese_text(result)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(chinese_text)
            print(f"结果已保存至 {output_path}")
        except Exception as e:
            print(f"保存结果时出错: {e}")


def process_audio_files(appid, secret_key):
    """
    批量处理audio文件夹下的所有音频文件
    集成了上面获取请求结果（包含上传音频到api）、存储文本信息到文件夹下的函数
    """
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        print(f"音频文件夹 {audio_dir} 不存在")
        return
    
    if not os.path.exists("sample"):
        os.makedirs("sample")

    for root, dirs, files in os.walk(audio_dir):
        for file in files:
            # 可根据实际支持的音频格式修改
            if file.endswith(('.wav', '.mp3', '.m4a')):
                file_path = os.path.join(root, file)
                print(f"正在处理文件: {file_path}")
                api = RequestApi(appid, secret_key, file_path)
                result = api.get_result()
                api.save_result_to_file(result)


def get_audio_text(appid, secret_key):
    """
    获取音频转换的文本，整合音频处理和文本读取
    """
    audio_dir = "audio"
    if not os.path.exists(audio_dir) or not os.listdir(audio_dir):
        return None
    
    # 直接使用批处理函数
    print("🎵 处理音频文件...")
    process_audio_files(appid, secret_key)
    
    # 读取生成的转录文件
    sample_dir = "sample"
    texts = []
    if os.path.exists(sample_dir):
        for file in os.listdir(sample_dir):
            if file.endswith('_transcription.txt'):
                file_path = os.path.join(sample_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    texts.append(f"=== {file} ===\n{f.read()}")
    
    return "\n\n".join(texts) if texts else None

# 输入讯飞开放平台的appid，secret_key和待转写的文件路径
if __name__ == '__main__':
    # 处理 audio 文件夹下所有音频文件
    process_audio_files(
        appid="3dd9e7d8",
        secret_key="170dab85113975c26483e0fcd8c43601"
    )
