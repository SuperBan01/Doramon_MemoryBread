import requests
import json
from config import XUNFEI_APP_ID, XUNFEI_API_KEY, XUNFEI_API_SECRET
import hashlib
import hmac
import base64
from datetime import datetime
from urllib.parse import urlencode

def generate_feishu_format(text_content): # test_content为输入的文本内容,传入的为analysis_result，即AI分析文本的结果
    """使用Spark 4.0 Ultra生成飞书文档格式"""
    try:
        # 构建专业的提示词
        prompt = f"""
你是一个专业的文档格式设计师。请根据以下文本内容，设计一个结构化的飞书文档格式。

要求：
1. 分析文本内容的主题和结构
2. 合理使用标题层级（heading1, heading2）
3. 将内容组织成段落（paragraph）
4. 如果有列表项，使用bullet_list
5. 重要信息可以使用quote块

文本内容：
{text_content}

请严格按照以下JSON格式输出，不要添加任何其他文字：
{{
  "children": [
    {{
      "block_type": "heading1",
      "heading1": {{
        "elements": [{{"text_run": {{"content": "主标题"}}}}]
      }}
    }},
    {{
      "block_type": "paragraph",
      "paragraph": {{
        "elements": [{{"text_run": {{"content": "段落内容"}}}}]
      }}
    }}
  ]
}}
"""
        
        # 调用Spark 4.0 Ultra API，它的输出为字典类型的API响应结果，提取纯文本后为block块的内容
        response = call_spark_api(prompt)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            # 解析JSON响应
            try:
                format_json = json.loads(content)
                return format_json
                print(format_json)
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    format_json = json.loads(json_match.group())
                    return format_json
        
        # 如果API调用失败，返回默认格式
        return get_default_format(text_content)
        
    except Exception as e:
        print(f"格式生成错误: {e}")
        return get_default_format(text_content)

def call_spark_api(prompt):
    """调用讯飞Spark 4.0 Ultra API"""
    try:
        # API配置
        url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
        
        # 构建请求头
        headers = {
            "Authorization": f"Bearer {XUNFEI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 构建请求体
        data = {
            "model": "4.0Ultra",
            "messages": [
                {
                    "role": "user",
                    "content": prompt # prompt里实际上除了提示词信息还含有analysis_result即AI分析文本后的信息
                }
            ],
            "stream": False,
            "max_tokens": 2048,
            "temperature": 0.3
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API调用失败: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        print(f"API调用异常: {e}")
        return None

def get_default_format(text_content):
    """获取默认格式（备用方案）"""
    lines = text_content.strip().split('\n')
    children = []
    
    # 添加主标题
    children.append({
        "block_type": "heading1",
        "heading1": {
            "elements": [{"text_run": {"content": "AI分析报告"}}]
        }
    })
    
    # 添加内容段落
    for line in lines:
        if line.strip():
            children.append({
                "block_type": "paragraph",
                "paragraph": {
                    "elements": [{"text_run": {"content": line.strip()}}]
                }
            })
    
    return {"children": children}