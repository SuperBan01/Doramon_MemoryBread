import requests
import json
from config import XUNFEI_API_KEY
from datetime import datetime
import os
import glob
from ai_analyzer import analyze_interview
def call_spark_api(prompt):
    """调用讯飞Spark 4.0 Ultra API"""
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {XUNFEI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "4.0Ultra",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "max_tokens": 2048,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices']:
                return result
        print(f"API调用失败: {response.status_code}")
        return None
    except Exception as e:
        print(f"API调用异常: {e}")
        return None

def generate_markdown_content(text_content):
    """生成纯markdown内容"""
    prompt = f"""
        你是一名专业的**信息架构设计师和写作专家**，请根据以下输入文本，**自主分析内容并重构为优质的 Markdown 文档**。

        ---

        ### 输出目标

        1. 输出 **必须是 Markdown 格式**，能够清晰展示文本的主题、层级、重点信息。
        2. Markdown 输出将被保存为.md文件，因此**结构必须合理，语义明确**。
        3. **严禁输出任何解释性文字、JSON格式或代码块标记**，只输出纯Markdown内容。

        ---
        
        ### 内容处理原则
        
        1. **智能提取**：从输入文本中提取关键信息、核心观点和重要细节
        2. **逻辑重构**：按照主题相关性重新组织内容，而非简单按原文顺序排列
        3. **层次分明**：确保标题层级合理，内容归属清晰
        4. **可读性优先**：优化段落长度和结构，提升阅读体验

        ### Markdown 设计要求

        1. **标题结构**：
        - 用 `# 一级标题` 表示核心主题。
        - 用 `## 二级标题` 表示分主题。
        - 如果有需要，支持 `### 三级标题`，但不宜过多。
        2. **段落组织**：
        - 每个自然段单独成段，避免过长。
        - 段落应围绕标题展开，条理清晰。
        3. **列表信息**：
        - 无序列表：`- 列表项`，用于罗列并列信息。
        - 有序列表：`1. 列表项`，用于有顺序的步骤。
        4. **重点提示**：
        - 引用：`> 引用内容`，用于强调关键信息或注意事项。
        - 粗体：`**加粗**` 表示重要关键词。
        - 斜体：`*斜体*` 表示次要强调。
        - 链接：`[链接文字](https://example.com)` 用于外部信息。
        5. 保持逻辑分层，**标题—段落—列表—引用**形成合理的结构树。

        ---

        ### 严格输出要求

        1. 输出必须是**纯 Markdown 文本**，不要包含 JSON、注释、解释或额外文字。
        2. Markdown 内容需要有良好的阅读体验，适当使用标题、列表和引用，避免纯文本堆砌。
        3. 不要简单按原文顺序照搬，而是要进行逻辑整理，使结构更合理。
        4. 如果输入文本为空，输出空字符串（`""`）。

        ---

        ### 输入文本：
        {text_content}

        ---

        """
    
    try:
        response = call_spark_api(prompt)
        if response and 'choices' in response:
            return response['choices'][0]['message']['content'].strip()
        return get_default_markdown(text_content)
    except Exception as e:
        print(f"Markdown生成错误: {e}")
        return get_default_markdown(text_content)

def get_default_markdown(text_content):
    """获取默认markdown格式（备用方案）"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""# AI分析报告

> 生成时间: {timestamp}

## 分析内容

{text_content}

---

*由Doramon记忆面包系统自动生成*
"""

def save_markdown_to_file(markdown_content, filename=None):
    """将markdown内容保存到sample_md文件夹"""
    try:
        os.makedirs("sample_md", exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{timestamp}.md"
        
        if not filename.endswith('.md'):
            filename += '.md'
        
        file_path = os.path.join("sample_md", filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return True, file_path  # 直接返回文件路径而不是消息
    except Exception as e:
        return False, f"保存Markdown文件失败: {str(e)}"

def generate_and_save_markdown(text_content, filename=None):
    """生成markdown内容并保存到文件"""
    try:
        markdown_content = generate_markdown_content(text_content)
        success, path = save_markdown_to_file(markdown_content, filename)
        return success, markdown_content, path  # 返回路径而不是消息
    except Exception as e:
        return False, "", f"生成和保存Markdown失败: {str(e)}"

def get_latest_sample_file():
    """获取sample文件夹中最新的文件"""
    try:
        if not os.path.exists("sample"):
            return None, "sample文件夹不存在"
        
        files = glob.glob(os.path.join("sample", "*"))
        if not files:
            return None, "sample文件夹为空"
        
        return max(files, key=os.path.getmtime), None
    except Exception as e:
        return None, f"获取最新文件失败: {str(e)}"

def read_sample_file(file_path):
    """读取sample文件夹中的文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"错误：文件 {file_path} 不存在"
    except Exception as e:
        return f"读取文件失败: {str(e)}"

def main():
    """主测试流程"""
    print("🧪 Format Generator 完整流程测试开始...")
    
    # 获取sample文件夹中最新的文件
    latest_file, error = get_latest_sample_file() 
    if error:
        print(f"❌ {error}")
        return
    
    print(f"📄 找到最新文件: {latest_file}")
    
    # 读取sample文件夹中最新的文件
    content = read_sample_file(latest_file)
    if content.startswith('错误'):
        print(f"❌ {content}")
        return
    
    print(f"📖 原始文件内容长度: {len(content)} 字符")
    
    # AI分析，结果存储在analysis_result变量中
    print("\n🤖 步骤1: AI分析文本中...")
    analysis_result = content
    try:
        result = analyze_interview(content)
        if not result.startswith(("网络请求错误", "调用AI API时出错", "AI未返回")):
            analysis_result = result
            print(f"✅ AI分析完成，结果长度: {len(analysis_result)} 字符")
        else:
            print(f"❌ AI分析失败: {result}")
    except Exception as e:
        print(f"⚠️ AI分析出错: {e}，使用原始文本继续测试")
    
    # Markdown格式化
    print("\n📝 步骤2: 将AI分析结果转换为Markdown格式...")
    base_name = os.path.basename(latest_file)
    output_filename = f"analyzed_{base_name.replace('.txt', '.md')}" # 存储md的文件夹地址
    
    success, markdown_content, path = generate_and_save_markdown(analysis_result, output_filename)
    
    if success:
        print(f"✅ Markdown文件已保存到: {path}")
        print(f"📄 最终Markdown内容预览:\n{markdown_content[:300]}...")
        print("\n📊 流程总结:")
        print(f"   📁 输入文件: {latest_file}")
        print(f"   📏 原始内容: {len(content)} 字符")
        print(f"   🤖 AI分析结果: {len(analysis_result)} 字符")
        print(f"   📝 最终Markdown: {len(markdown_content)} 字符")
        print(f"   💾 输出文件: {path}")
    else:
        print(f"❌ Markdown生成失败: {path}")
    
    print("\n🎉 完整流程测试完成！")

if __name__ == '__main__':
    main()