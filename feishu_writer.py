import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from datetime import datetime
from config import FEISHU_USER_TOKEN, FEISHU_DOCUMENT_ID, BLOCK_DOCUMENT_ID, FEISHU_APP_ID, FEISHU_APP_SECRET
from format_generator import generate_feishu_format

def convert_to_lark_blocks(format_json):
    """将生成的JSON格式转换为lark SDK格式"""
    blocks = []
    
    for item in format_json.get('children', []):
        block_type = item.get('block_type', 'paragraph')
        
        if block_type == 'paragraph':
            content = item['paragraph']['elements'][0]['text_run']['content']
            block = Block.builder() \
                .block_type(2) \
                .text(Text.builder()
                    .elements([TextElement.builder()
                        .text_run(TextRun.builder()
                            .content(content)
                            .build())
                        .build()])
                    .build()) \
                .build()
            blocks.append(block)
        print("blocks:", blocks) # 调试用，查看有没有成功转换为对应的response里的block飞书格式
    
    return blocks

def write_analysis_to_feishu_smart(analysis_result):
    """智能写入分析结果到飞书文档"""
    try:
        client = lark.Client.builder().app_id(FEISHU_APP_ID).app_secret(FEISHU_APP_SECRET).build()
        
        # 生成格式
        format_json = generate_feishu_format(analysis_result)
        blocks = convert_to_lark_blocks(format_json)
        
        # 构建请求，.children(blocks) 中的 blocks 变量为大模型生成的“根据内容自动选择合适的飞书文档格式和结构”
        request = CreateDocumentBlockChildrenRequest.builder() \
            .document_id(FEISHU_DOCUMENT_ID) \
            .block_id(BLOCK_DOCUMENT_ID) \
            .document_revision_id(-1) \
            .user_id_type("user_id") \
            .request_body(CreateDocumentBlockChildrenRequestBody.builder()
                .children(blocks)
                .index(0)
                .build()) \
            .build()
        
        option = lark.RequestOption.builder().user_access_token(FEISHU_USER_TOKEN).build()
        response = client.docx.v1.document_block_children.create(request, option)
        
        if response.success():
            return True, "智能格式内容已成功写入飞书文档"
        else:
            return False, f"写入失败: {response.msg}"
            
    except Exception as e:
        return False, f"飞书API调用出错: {str(e)}"

# 保留原有函数
def write_analysis_to_feishu(analysis_result):
    """原有的简单写入方法，以传统固定方式写入"""
    try:
        client = lark.Client.builder() \
            .enable_set_token(True) \
            .build()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_content = f"""✨ 记忆面包分析报告 - {timestamp}

📝 AI分析结果：
{analysis_result}

🥖 处理完成，经验包已消化！
"""  # 此处为要写入飞书的内容:注释词+analysis_result
        
        # 使用构建器模式创建一个复杂的飞书文档请求对象，其本质就是写入内容:
        # 每次写入新内容都需要重新构建一个request ，但我们可以优化这个过程;未来能否让ai自动设计这种写入过程
        # - 📍 在哪里写 ： document_id + block_id 指定位置
        # - 📝 写什么内容 ： content(formatted_content) 指定文本
        # - 🎨 用什么格式 ： block_type 、颜色、样式等
        # - 📌 插在哪个位置 ： index(0) 指定插入顺序
        
        # \ 是行连接符，用于将一行代码分成多行书写：
        #         请求（Request）
        # └── 请求体（RequestBody）
        #     └── 子块数组（Children）
        #         └── 块（Block）
        #             └── 文本（Text）
        #                 └── 元素数组（Elements）
        #                     └── 文本元素（TextElement）
        #                         └── 文本运行（TextRun）
        #                             ├── 内容（Content）
        #                             └── 样式（Style）
        request = CreateDocumentBlockChildrenRequest.builder() \
            .document_id(FEISHU_DOCUMENT_ID) \
            .block_id(BLOCK_DOCUMENT_ID) \
            .document_revision_id(-1) \
            .user_id_type("user_id") \
            .request_body(CreateDocumentBlockChildrenRequestBody.builder()
                .children([Block.builder()
                    .block_type(2)  # 块类型：2表示文本块
                    .text(Text.builder()
                        .style(TextStyle.builder().build())  # 使用默认文本样式
                        .elements([TextElement.builder()
                            .text_run(TextRun.builder()
                                .content(formatted_content)  # 要写入的实际内容
                                .text_element_style(TextElementStyle.builder()
                                    .background_color(1)  # 背景颜色：1=默认色
                                    .text_color(1)        # 文字颜色：1=默认色
                                    .build())
                                .build())
                            .build()])
                        .build())
                    .build()])
                .index(0)  # 插入位置：0=最前面
                .build()) \
            .build()
        
        option = lark.RequestOption.builder().user_access_token(FEISHU_USER_TOKEN).build() # 用户访问令牌、权限等
        response = client.docx.v1.document_block_children.create(request, option) # 发送请求创建块（写入）
        
        if response.success():
            return True, "成功写入飞书文档"
        else:
            return False, f"写入失败: code={response.code}, msg={response.msg}"
            
    except Exception as e:
        return False, f"飞书API调用出错: {str(e)}"