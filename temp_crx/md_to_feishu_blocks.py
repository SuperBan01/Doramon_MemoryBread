# 这是crx写的md转飞书所需的json格式的文件代码，没啥用。

import json
import os
import glob
from datetime import datetime
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *


# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development
# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用

def read_latest_md():
    md_files = glob.glob(os.path.join(os.path.dirname(__file__), 'sample_md', '*.md'))
    if not md_files:
        return None
    latest_file = max(md_files, key=os.path.getmtime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        return f.read()

def save_blocks_to_file(blocks_data):
    """保存blocks数据到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"feishu_blocks_{timestamp}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(blocks_data, f, indent=2, ensure_ascii=False)
    
    print(f"Blocks已保存到: {filename}")
    return filepath

def md_to_feishu_blocks():
    # 创建client
    client = lark.Client.builder() \
        .app_id("cli_a8e5444630b9101c") \
        .app_secret("gJ5012ZVxV0BQMKEWB3tHcTVrTmlX5qu") \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: ConvertDocumentRequest = ConvertDocumentRequest.builder() \
        .request_body(ConvertDocumentRequestBody.builder()
            .content_type("markdown")
            .content(md_content)
            .build()) \
        .build()

    # 发起请求
    response: ConvertDocumentResponse = client.docx.v1.document.convert(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.docx.v1.document.convert failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    blocks_data = json.loads(lark.JSON.marshal(response.data))
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    
    # 保存blocks到文件
    save_blocks_to_file(blocks_data)    
    
if __name__ == "__main__":
    md_to_feishu_blocks()