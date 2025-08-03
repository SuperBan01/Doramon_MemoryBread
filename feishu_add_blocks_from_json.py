import json
import requests

def insert_block_to_document():
    # API 端点
    url = "https://open.feishu.cn/open-apis/docx/v1/documents/ZJpKd5fTUofk2txadqAcKpBKnkc/blocks/QVIOdsGpvoEJklxRDulcPa55n5g/descendant"
    
    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer u-e.sr1XUAx02W5OiP0DbzV7057JeBk12XWwG04kqGw9pL'
    }
    
    # 请求参数
    params = {
        'document_revision_id': -1
    }
    
    # 从JSON文件读取请求体数据
    try:
        with open('valid_document.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("错误: 找不到 valid_document.json 文件")
        return
    except json.JSONDecodeError as e:
        print(f"错误: JSON文件格式不正确 - {e}")
        return
    
    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, params=params, json=data)
        
        # 打印响应状态码
        print(f"状态码: {response.status_code}")
        
        # 打印响应头
        print("响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # 打印响应体
        print("\n响应体:")
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(response.text)
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    insert_block_to_document()