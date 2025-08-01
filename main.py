from ai_analyzer import analyze_interview, read_sample_file
from feishu_writer import write_analysis_to_feishu
from voice2txt import get_audio_text
from config import XFYUN_APPID, XFYUN_SECRET_KEY
import os

def main():
    """主流程：音频->文本->AI分析->飞书"""
    print("🥖 Doramon记忆面包开始处理...")
    
    # 1. 批量获取所有声音文件，处理为文本，放置在文本文件夹下
    # 未来可能是我们指定文件地址，或者每检测到有一个新的文件则进行处理
    text = get_audio_text(XFYUN_APPID, XFYUN_SECRET_KEY)
    
    if not text:
        print("📖 读取文本文件...")
        text = read_sample_file(os.path.join("sample", "sample1"))
    
    if not text or text.startswith(("错误", "读取文件失败")):
        print("❌ 获取文本失败")
        return
    
    # 2. AI分析
    print("🤖 AI分析中...")
    analysis = analyze_interview(text)
    
    if analysis.startswith(("网络请求错误", "调用AI API时出错", "AI未返回")):
        print(f"❌ AI分析失败: {analysis}")
        return
    
    # 3. 写入飞书
    print("📝 写入飞书...")
    success, message = write_analysis_to_feishu(analysis)
    
    if success:
        print("✅ 处理完成！")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    main()