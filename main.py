# -*- coding: utf-8 -*-
import sys
import io
from ai_analyzer import analyze_interview, read_sample_file
from voice2txt import get_audio_text_path
from format_generator import generate_and_save_markdown
import os
from upload_md import upload_file, create_import_task
from config import XFYUN_APPID, XFYUN_SECRET_KEY
import lark_oapi as lark
from lark_oapi.api.drive.v1 import *

def main():
    print("🥖 Doramon记忆面包开始处理...")
    
    # 1. 获取文本
    # text,output_path = get_audio_text_path(XFYUN_APPID, XFYUN_SECRET_KEY) # 实现音频转文本并保存到对应文件夹

    # 直接从文本sample文件夹路径下读取文本
    sample_folder = "sample"
    file_name = "项目路演测试文本.txt"
    file_path = os.path.join(sample_folder, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # 2. AI分析
    print("🤖 AI分析文本中...")
    analysis = analyze_interview(text) # 调用minimax api让ai对原文本进行总结，处理的结果存储到analysis变量
    
    if analysis.startswith(("网络请求错误", "调用AI API时出错", "AI未返回")):
        print(f"❌ AI分析失败: {analysis}")
        return    

    # 3. 生成并保存Markdown文件到sample文件夹下
    print("📝 生成飞书适配的Markdown文件...")
    success, markdown_content, path = generate_and_save_markdown(analysis) # 生成markdown内容并保存到文件夹下
    print(path)
        
    # 4. 写入飞书
    print("📝 写入飞书...")         
    # 配置飞书参数
    # file_path = r"C:\Users\95718\Desktop\vscode\Program\memory_bread\Doramon_MemoryBread\sample_md\analyzed_test_transcription.md"
    # file_name = "analyzed_test_transcription.md"
    file_path = path
    file_name = os.path.basename(file_path) # 未来会考虑使用AI分析的内容总结生成标题
    # file_name = f"记忆面包_{os.path.splitext(os.path.basename(file_path))[0]}"
    
    user_access_token = "u-fE2zVji5F8Y8TEaSD6d2R.007gWw11aVNW20lgiEw4_T"
    mount_key = "Z4ZrfFYRRlxV3Ldn1guc6xacn4c"  # 目标文件夹的key
    
    # 创建client
    # 使用 user_access_token 需开启 token 配置, 并在 request_option 中配置 token
    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 第一步：上传文件
    print("开始上传文件...")
    file_token = upload_file(client, file_path, file_name, user_access_token)
    
    if file_token is None:
        print("文件上传失败，终止流程")
        return
    
    # 第二步：创建导入任务
    print("开始创建导入任务...")
    import_result = create_import_task(client, file_token, mount_key, user_access_token)
    
    if import_result is None:
        print("导入任务创建失败")
        return
    
    print("整个流程执行完成！")

if __name__ == "__main__":
    main()