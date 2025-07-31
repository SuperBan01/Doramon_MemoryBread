from ai_analyzer import analyze_interview, read_sample_file
from feishu_writer import write_analysis_to_feishu
import os

def main():
    """主程序流程"""
    print("🥖 Doramon记忆面包处理开始...")
    
    # 1. 读取访谈文件 - 修改这里
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(current_dir, "sample", "sample1")
    print(f"📖 正在读取文件: {sample_path}")
    
    interview_text = read_sample_file(sample_path)
    if interview_text.startswith("错误") or interview_text.startswith("读取文件失败"):
        print(f"❌ {interview_text}")
        return
    
    print(f"✅ 文件读取成功，内容长度: {len(interview_text)} 字符")
    
    # 2. AI分析
    print("🤖 正在调用AI进行分析...")
    analysis_result = analyze_interview(interview_text)
    
    if analysis_result.startswith(("网络请求错误", "调用AI API时出错", "AI未返回")):
        print(f"❌ AI分析失败: {analysis_result}")
        return
    
    print("✅ AI分析完成")
    print(f"📋 完整分析结果:\n{analysis_result}")
       
    # 3. 写入飞书
    print("📝 正在写入飞书文档...")
    success, message = write_analysis_to_feishu(analysis_result)
    
    if success:
        print(f"✅ {message}")
        print("🎉 记忆面包处理完成！经验包已成功消化并存储到飞书文档中")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    main()