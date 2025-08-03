# 此代码为crx测试所用，可能可以的方案，暂时未待验证

import json
import glob
import os
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from config import FEISHU_USER_TOKEN

def read_feishu_blocks():
    """读取飞书blocks JSON文件"""
    file_path = r"C:\Users\95718\Desktop\vscode\Program\memory_bread\Doramon_MemoryBread\feishu_blocks_20250803_154555.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data
def read_latest_md(): # 读取md代码
    md_files = glob.glob(os.path.join(os.path.dirname(__file__), 'sample_md', '*.md'))
    if not md_files:
        return None
    latest_file = max(md_files, key=os.path.getmtime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        return f.read()

''' 
我发现问题了，md转json的时候，系统会自动为每个block分配一个block_id
；然而，这个block_id并非我们的文档中的每个块的block_id。所以即便我们把格式转化为更新块的函数所需的格式以后，这个block_id也对不上
'''
def convert_feishu_blocks_to_requests(blocks) -> Dict:
    """
    将飞书 markdown JSON 的 blocks 转换为批量更新接口参数
    """
    requests = []

    for block in blocks:
        # 使用属性访问而不是字典访问
        block_id = block.block_id if hasattr(block, 'block_id') else None
        block_type = block.block_type if hasattr(block, 'block_type') else None
        
        if not block_id or block_type is None:
            continue
            
        # 1. 文本 & 标题类
        if block_type in [2, 3, 4, 5, 6, 7, 8]:  # 普通文本/标题
            text_obj = None
            if hasattr(block, 'text'):
                text_obj = block.text
            elif hasattr(block, 'heading1'):
                text_obj = block.heading1
            elif hasattr(block, 'heading2'):
                text_obj = block.heading2
            elif hasattr(block, 'heading3'):
                text_obj = block.heading3
            elif hasattr(block, 'heading4'):
                text_obj = block.heading4
            elif hasattr(block, 'heading5'):
                text_obj = block.heading5
            elif hasattr(block, 'heading6'):
                text_obj = block.heading6
                
            if text_obj and hasattr(text_obj, 'elements'):
                elements = []
                for el in text_obj.elements:
                    if hasattr(el, 'text_run'):
                        elements.append({
                            "text_run": {
                                "content": el.text_run.content,
                                "text_element_style": getattr(el.text_run, 'text_element_style', {})
                            }
                        })
                if elements:
                    requests.append({
                        "block_id": block_id,
                        "update_text_elements": {
                            "elements": elements
                        }
                    })

        # 2. 列表类（bullet / ordered）
        elif block_type in [12, 13]:
            list_obj = None
            if hasattr(block, 'bullet'):
                list_obj = block.bullet
            elif hasattr(block, 'ordered'):
                list_obj = block.ordered
                
            if list_obj and hasattr(list_obj, 'elements'):
                elements = []
                for el in list_obj.elements:
                    if hasattr(el, 'text_run'):
                        elements.append({
                            "text_run": {
                                "content": el.text_run.content,
                                "text_element_style": getattr(el.text_run, 'text_element_style', {})
                            }
                        })
                if elements:
                    requests.append({
                        "block_id": block_id,
                        "update_text_elements": {
                            "elements": elements
                        }
                    })

        # 3. 代码块
        elif block_type == 14:
            if hasattr(block, 'code'):
                code_obj = block.code
                if hasattr(code_obj, 'elements'):
                    elements = []
                    for el in code_obj.elements:
                        if hasattr(el, 'text_run'):
                            elements.append({
                                "text_run": {
                                    "content": el.text_run.content,
                                    "text_element_style": getattr(el.text_run, 'text_element_style', {})
                                }
                            })
                    if elements:
                        requests.append({
                            "block_id": block_id,
                            "update_text_elements": {
                                "elements": elements
                            }
                        })

        # 4. 引用
        elif block_type == 15:
            if hasattr(block, 'quote'):
                quote_obj = block.quote
                if hasattr(quote_obj, 'elements'):
                    elements = []
                    for el in quote_obj.elements:
                        if hasattr(el, 'text_run'):
                            elements.append({
                                "text_run": {
                                    "content": el.text_run.content,
                                    "text_element_style": getattr(el.text_run, 'text_element_style', {})
                                }
                            })
                    if elements:
                        requests.append({
                            "block_id": block_id,
                            "update_text_elements": {
                                "elements": elements
                            }
                        })

        # 5. 表格（支持单元格合并）
        elif block_type == 31:
            if hasattr(block, 'table'):
                table_obj = block.table
                if hasattr(table_obj, 'property'):
                    property_obj = table_obj.property
                    merge_info_list = getattr(property_obj, 'merge_info', [])
                    row_size = getattr(property_obj, 'row_size', 0)
                    col_size = getattr(property_obj, 'column_size', 0)

                    # 遍历 merge_info 生成合并指令
                    for idx, merge_info in enumerate(merge_info_list):
                        row_span = getattr(merge_info, 'row_span', 1)
                        col_span = getattr(merge_info, 'col_span', 1)
                        if row_span > 1 or col_span > 1:
                            row_idx = idx // col_size
                            col_idx = idx % col_size
                            requests.append({
                                "block_id": block_id,
                                "merge_table_cells": {
                                    "row_start_index": row_idx,
                                    "row_end_index": row_idx + row_span - 1,
                                    "column_start_index": col_idx,
                                    "column_end_index": col_idx + col_span - 1
                                }
                            })

        # 6. 其他类型可按需扩展（图片、任务等）

    return {"requests": requests}


class FeishuWriter:
    """飞书文档操作类"""
    
    def __init__(self):
        """初始化飞书客户端"""
        self.client = lark.Client.builder() \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()
        self.user_token = FEISHU_USER_TOKEN
        self.document_id = FEISHU_DOCUMENT_ID
        self.block_id = BLOCK_DOCUMENT_ID
    
    def create_document(self, folder_token="Z4ZrfFYRRlxV3Ldn1guc6xacn4c", title="doc_crx"):
        """创建飞书文档"""
        # 构造请求对象
        request: CreateDocumentRequest = CreateDocumentRequest.builder() \
            .request_body(CreateDocumentRequestBody.builder()
                .folder_token(folder_token)
                .title(title)
                .build()) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().user_access_token(self.user_token).build()
        response: CreateDocumentResponse = self.client.docx.v1.document.create(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.docx.v1.document.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data

    def create_document_block(self):
        """创建文档块"""
        # 构造请求对象
        request: CreateDocumentBlockChildrenRequest = CreateDocumentBlockChildrenRequest.builder() \
            .document_id(self.document_id) \
            .block_id(self.block_id) \
            .document_revision_id(-1) \
            .request_body(CreateDocumentBlockChildrenRequestBody.builder()
                .children([Block.builder()
                    .block_type(2)
                    .text(Text.builder()
                        .style(TextStyle.builder()
                            .build())
                        .elements([TextElement.builder()
                            .text_run(TextRun.builder()
                                .content("test")
                                .text_element_style(TextElementStyle.builder()
                                    .background_color(14)
                                    .text_color(5)
                                    .build())
                                .build())
                            .build(), 
                            TextElement.builder()
                            .text_run(TextRun.builder()
                                .content("crx")
                                .text_element_style(TextElementStyle.builder()
                                    .bold(True)
                                    .background_color(14)
                                    .text_color(5)
                                    .build())
                                .build())
                            .build()
                            ])
                        .build())
                    .build()
                    ])
                .index(0)
                .build()) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().user_access_token(self.user_token).build()
        response: CreateDocumentBlockChildrenResponse = self.client.docx.v1.document_block_children.create(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.docx.v1.document_block_children.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data

    def patch_document_block(self, content_data):
        """更新文档块内容"""
        # 构造请求对象
        request: PatchDocumentBlockRequest = PatchDocumentBlockRequest.builder() \
            .document_id(self.document_id) \
            .block_id(self.block_id) \
            .document_revision_id(-1) \
            .user_id_type("open_id") \
            .request_body(UpdateBlockRequest.builder()
                .update_text_elements(UpdateTextElementsRequest.builder()
                    .elements([TextElement.builder()
                        .mention_user(MentionUser.builder()
                            .user_id("ou_01e817402136fccbc4332504ee01401a")
                            .build())
                        .build(), 
                        TextElement.builder()
                        .text_run(TextRun.builder()
                            .content("正式")
                            .text_element_style(TextElementStyle.builder()
                                .bold(True)
                                .italic(True)
                                .strikethrough(True)
                                .underline(True)
                                .background_color(2)
                                .text_color(2)
                                .build())
                            .build())
                        .build(), 
                        TextElement.builder()
                        .text_run(TextRun.builder()
                            .content(content_data)
                            .text_element_style(TextElementStyle.builder()
                                .italic(True)
                                .build())
                            .build())
                        .build()
                        ])
                    .build())
                .build()) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().user_access_token(self.user_token).build()
        response: PatchDocumentBlockResponse = self.client.docx.v1.document_block.patch(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.docx.v1.document_block.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return None

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data
    
    def batch_update_document_block(self, requests_data):
        """批量更新文档块"""
        # 构造请求对象
        request: BatchUpdateDocumentBlockRequest = BatchUpdateDocumentBlockRequest.builder() \
            .document_id(self.document_id) \
            .document_revision_id(-1) \
            .request_body(BatchUpdateDocumentBlockRequestBody.builder()
                .requests(requests_data)
                .build()) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().user_access_token(self.user_token).build()
        response: BatchUpdateDocumentBlockResponse = self.client.docx.v1.document_block.batch_update(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.docx.v1.document_block.batch_update failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return None
            
        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data
        
    def md2json(self, block_data_md):
        # 构造请求对象
        request: ConvertDocumentRequest = ConvertDocumentRequest.builder() \
            .user_id_type("user_id") \
            .request_body(ConvertDocumentRequestBody.builder()
                .content_type("markdown")
                .content(block_data_md)
                .build()) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().user_access_token(self.user_token).build()
        response: ConvertDocumentResponse = self.client.docx.v1.document.convert(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.docx.v1.document.convert failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        # lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data

if __name__ == "__main__":
    # 读取数据
    # blocks_data = read_feishu_blocks()
    # block_data_json = json.dumps(blocks_data, ensure_ascii=False, indent=2)
    # print(block_data_json)
    
    block_data_md = read_latest_md()
    # print(block_data_json)
    
    # 这里现在有些循环论证，既要用FeishuWriter类，里面需要FEISHU_DOCUMENT_ID等参数作为init，然而又要调里面方法作为获取FEISHU_DOCUMENT_ID
    # feishu_writer = FeishuWriter()
    # response_data = feishu_writer.create_document()
    # FEISHU_DOCUMENT_ID = response_data.document.document_id
    # BLOCK_DOCUMENT_ID = FEISHU_DOCUMENT_ID
    # feishu_writer.create_document_block()
    # 如果我们真的成功创建了该文档下的第一个块，那么我们接下来需要考虑接着这个块下创建嵌入块，再获取其返回值下的每一个块的id
    # 然后新写一个feishu_writer.md2json(block_data_md)函数，可以针对每一个块的id生成对应的json文档
    # 再block_data_json = feishu_writer.md2json(block_data_md)，block_data_json_true = block_data_json.blocks
    # 再result = convert_feishu_blocks_to_requests(block_data_json_true)得到符合更新块标准的json数据
    # 最后调用feishu_writer.batch_update_document_block(result)批量更新块
    
    
    
    
    # block_data_json = feishu_writer.md2json(block_data_md) # md转json会为每个块赋予一个block_id，而这是自动分配的不是我们创建的文档中的块
    # # print(block_data_json)
    # block_data_json_true = block_data_json.blocks
    # # print(block_data_json_true)
    # result = convert_feishu_blocks_to_requests(block_data_json_true)
    # print(result)
    
    


    # feishu_writer.patch_document_block(block_data_json)
    # feishu_writer.batch_update_document_block(result)
    
    
    
