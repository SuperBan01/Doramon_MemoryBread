# -*- coding: utf-8 -*-
import sys
import io
from ai_analyzer import analyze_interview, read_sample_file
from feishu_writer import write_analysis_to_feishu_smart
from voice2txt import get_audio_text
from format_generator import generate_and_save_markdown
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
    analysis = analyze_interview(text)
    
    if analysis.startswith(("网络请求错误", "调用AI API时出错", "AI未返回")):
        print(f"❌ AI分析失败: {analysis}")
        return
    
    # 3. 生成并保存Markdown文件
    print("📝 生成飞书适配的Markdown文件...")
    success, markdown_content, message = generate_and_save_markdown(analysis)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"⚠️ {message}")
    
    # 4. 写入飞书
    print("📝 写入飞书...")
    success, message = write_analysis_to_feishu_smart(analysis)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    main()