#!/usr/bin/env python3
import os
from flask import Flask, request
import subprocess
import threading

# 这段代码用于从硬件端获取音频文件，并将其保存到指定目录，然后异步处理。

app = Flask(__name__)
# 注释文件大小限制，允许上传任意大小的音频文件
# app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
UPLOAD_FOLDER = r'C:\Users\95718\Desktop\vscode\Program\memory_bread\Doramon_MemoryBread\audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def start_main_process(file_path):
    """启动main.py作为子进程"""
    try:
        print(f"🔄 启动main.py处理音频文件: {os.path.basename(file_path)}")
        
        # 设置UTF-8编码环境变量
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = '0'
        
        result = subprocess.run(
            ['python', 'main.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=300,
            env=env,  # 添加环境变量
            encoding='utf-8'  # 指定编码
        )
        
        if result.returncode == 0:
            print(f"✅ main.py执行完成: {os.path.basename(file_path)}")
            print(f"📄 执行输出: {result.stdout}")
        else:
            print(f"❌ main.py执行失败: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ main.py执行超时")
    except Exception as e:
        print(f"❌ 启动main.py时出错: {e}")

@app.route('/audio', methods=['POST'])
def upload_audio(): 
    """接收音频文件并异步处理"""
    # Flask自动解析HTTP请求
    # request.files 包含所有上传的文件
    # request.form 包含所有表单数据
    if 'audio' not in request.files:
        print(f'Failed to receive audio file: No audio file provided. Request form data: {request.form.to_dict()}, Request files: {list(request.files.keys())}')
        return 'No audio file provided', 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        print(f'Failed to receive audio file: No selected file. Request form data: {request.form.to_dict()}, File field name: audio, File details: {audio_file}')
        return 'No selected file', 400
    
    if audio_file:
        import itertools
        assfilename = itertools.count(0)
        exfilename = 'audio'
        
        # 生成唯一文件名
        while True:
            filename = f'{exfilename}{next(assfilename)}.wav'
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if not os.path.exists(file_path):
                # 保存文件
                audio_file.save(file_path)
                print(f'✅ 文件保存成功: {filename}')
                
                # 异步启动main.py处理音频文件
                processing_thread = threading.Thread(
                    target=start_main_process,
                    args=(file_path,),
                    daemon=True
                )
                processing_thread.start()
                print(f'🚀 已启动异步处理线程处理: {filename}')
                
                return f'Audio file uploaded and main.py started: {filename}', 200

if __name__ == '__main__':
    print("🎵 音频服务器启动中...")
    print("📡 服务器将接收音频文件并自动处理")
    print("🔗 硬件设备请发送POST请求到: http://服务器IP:5002/audio")
    print("⚡ 每个音频文件将异步启动main.py进行处理")
    
    # 硬件设备 → POST请求 → http://服务器:5002/audio
    # 请求包含：
    # - 文件数据（在'audio'字段中）
    # - 可能的表单数据
    app.run(host='0.0.0.0', port=5002, debug=True)