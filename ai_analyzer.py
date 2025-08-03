import requests
from config import MINIMAX_GROUP_ID, MINIMAX_API_KEY
from voice2txt import get_audio_text_path
from config import XFYUN_APPID, XFYUN_SECRET_KEY

def analyze_interview(text):
    """调用MiniMax API分析访谈内容"""
    url = f"https://api.minimaxi.com/v1/text/chatcompletion_pro?GroupId={MINIMAX_GROUP_ID}" # api接口地址
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}", 
        "Content-Type": "application/json"
    } # http请求头：身份验证+json格式
    
    payload = {
        "model": "MiniMax-Text-01",
        "tokens_to_generate": 8192,
        "reply_constraints": {"sender_type": "BOT", "sender_name": "Kairos"},
        "messages": [
            {"sender_type": "USER", "sender_name": "用户", "text": text}
        ],
        "bot_setting": [
            {
                "bot_name": "Kairos",
                "content": "Kairos是一个思想储存助手。kairos可以总结用户输入的文本信息，判断总结里面灵感生成的片刻，然后总结相应的灵感，并且生成围绕灵感需要进一步所做的执行操作。"
            }
        ]
    } # 请求数据构建
    # reply_constraints用于设置api回复的格式和身份，当前为机器人（大的提示词）
    # messages提供对话的上下文信息，发送者类型、名称、消息等；当前统一为用户，无法区分不同用户：我认为未来可以有不同的场景如面试官和候选人，根据前期大模型对于信息处理猜测场景/用户手动切换  1.灵感 2.日程规划
    # 定义AI助手的角色、性格和能力等（小的提示词）
    
    try:
        response = requests.post(url, headers=headers, json=payload) # 发送POST请求到API，json=payload ：将payload自动转换为JSON格式发送
        response.raise_for_status()  # 抛出HTTP错误
        response_data = response.json() #将响应内容转换为json格式
        
        print(response_data)
        return response_data.get("reply", "AI未返回分析结果") #安全地获取字典中的"reply"键值
            
    except requests.exceptions.RequestException as e:
        return f"网络请求错误: {str(e)}"
    except Exception as e:
        return f"调用AI API时出错: {str(e)}"

def read_sample_file(file_path):  # 实际上没用到，因为直接传的文件内容test
    """读取样本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "错误：文件不存在"
    except Exception as e:
        return f"读取文件失败: {str(e)}"  
    
if __name__ == '__main__':
    text,output_path = get_audio_text_path(XFYUN_APPID, XFYUN_SECRET_KEY) # 实现音频转文本并保存到对应文件夹
    analysis = analyze_interview(text) # 调用minimax api让ai对原文本进行总结，处理的结果存储到analysis变量