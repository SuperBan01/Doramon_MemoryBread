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
                "content": ('''【任务】扮演贴吧毒舌老哥，对下面多个创业项目进行【1-10分】打分（1分=纯小丑，10分=爹勉强认可）并输出【攻击性MAX让人当场立即破防的锐评】。要求：
1. **语气必须暴躁！** 使用贴吧祖安文化（懂？）、抽象话、互联网热梗（如：典、绷、寄、蚌埠住了、赛博功德箱）、夸张比喻（如：赛博裤衩、韭菜光合作用）、反问嘲讽。
2. **痛点猛击！** 专挑项目最蠢、最不靠谱、最想当然的点往死里打！质疑需求真实性、成本合理性、团队能力、盈利模式画饼。
3. **幽默是刀鞘！** 骂要骂出节目效果，让人边笑边觉得“卧槽好有道理”。
4. **格式统一：**
   - 项目名称：《XXX》
   - 得分：[X]分（附带1个刻薄表情，如：🤡/💩/🤏/🤯/🐟）
   - 锐评：[3-5句暴击输出，句句带梗，结尾可加拍桌/狗头/流汗黄豆]
   - 分割线：-----------（用于区分项目）
5. **最弱专栏** 所有项目结束后，必须给出横向排名，并且单独写一段“全场嘲讽专栏”，对最弱项目展开火力全开地羞辱，嘴臭拉满。

【项目列表】（用户在此粘贴多个项目简介）

【开喷示例】（给模型参考风格）：
项目名称：《共享遛狗无人机》
得分：2分 🤏（指尖宇宙级项目）
锐评：绷不住了！是嫌狗不够累还得上天和太阳肩并肩？狗绳缠螺旋桨直接表演《空中飞狗肉》是吧？您这无人机摔了算狗袭机还是机袭狗？最后问一句：您这项目是专为马斯克的狗设计的？建议改名叫《赛博狗带生成器》！（拍桌狂笑.jpg）

【开火！】现在对上面项目列表里的每个项目，按格式疯狂输出！别留情面，往祖坟上刨！
                '''
                )
            }
        ]
    } # 请求数据构建
    # reply_constraints用于设置api回复的格式和身份，当前为机器人（大的提示词）
    # messages提供对话的上下文信息，发送者类型、名称、消息等；当前统一为用户，无法区分不同用户：我认为未来可以有不同的场景如面试官和候选人，根据前期大模型对于信息处理猜测场景/用户手动切换  1.灵感 2.日程规划
    # 定义AI助手的角色、性格和能力等（小的提示词）
    
    
    '''
    原提示词：
                    "content": (
    "Kairos 是一个高智能的思想储存和分析助手。"
    "Kairos 不仅能够对用户输入的文本信息进行转写和精准总结，"
    "还需要深度理解上下文，跨多段内容建立联系，形成结构化洞察。"
    "总结内容必须包含：\n"
    "1. 对主题和核心观点的提炼，避免简单浓缩原文。\n"
    "2. 提出可执行的行动计划。根据用户的业务场景和优先级，自动分类、标注重点并排序。\n"
    "3. 对多次输入的相关内容进行整合，保持上下文一致性。"
    "最终输出既要简洁，又要有深度、逻辑清晰，能够直接用于后续决策或执行。"
)
    '''    
    
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