#!/usr/bin/env python3
import os
from flask import Flask, request

app = Flask(__name__)
# 移除文件大小限制，允许上传任意大小的音频文件
# app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
UPLOAD_FOLDER = '/Users/shorpen/编程/landingpage-doromon/backend/voice'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/voice', methods=['POST'])
def upload_audio():
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
        while True:
            filename = f'{exfilename}{next(assfilename)}.wav'
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if not os.path.exists(file_path):
                audio_file.save(file_path)
                print(f'Successfully received and saved audio file: {filename}')
                return 'File uploaded successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)