import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from datetime import datetime
from config import FEISHU_USER_TOKEN, FEISHU_DOCUMENT_ID

def write_analysis_to_feishu(analysis_result):
    """将分析结果写入飞书文档"""
    try:
        client = lark.Client.builder() \
            .enable_set_token(True) \
            .build()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_content = f"""✨ 记忆面包分析报告 - {timestamp}

📝 AI分析结果：
{analysis_result}

🥖 处理完成，经验包已消化！
"""
        
        request = CreateDocumentBlockChildrenRequest.builder() \
            .document_id(FEISHU_DOCUMENT_ID) \
            .block_id(FEISHU_DOCUMENT_ID) \
            .document_revision_id(-1) \
            .user_id_type("user_id") \
            .request_body(CreateDocumentBlockChildrenRequestBody.builder()
                .children([Block.builder()
                    .block_type(2)
                    .text(Text.builder()
                        .style(TextStyle.builder().build())
                        .elements([TextElement.builder()
                            .text_run(TextRun.builder()
                                .content(formatted_content)
                                .text_element_style(TextElementStyle.builder()
                                    .background_color(1)
                                    .text_color(1)
                                    .build())
                                .build())
                            .build()])
                        .build())
                    .build()])
                .index(0)
                .build()) \
            .build()
        
        option = lark.RequestOption.builder().user_access_token(FEISHU_USER_TOKEN).build()
        response = client.docx.v1.document_block_children.create(request, option)
        
        if response.success():
            return True, "成功写入飞书文档"
        else:
            return False, f"写入失败: code={response.code}, msg={response.msg}"
            
    except Exception as e:
        return False, f"飞书API调用出错: {str(e)}"