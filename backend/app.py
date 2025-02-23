from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import os
from typing import Tuple, Dict, Any
from llm_interface import LLMInterface, DialogueContext

app = Flask(__name__)
CORS(app)

# 确保存储对话记录的目录存在
if not os.path.exists('chat_logs'):
    os.makedirs('chat_logs')

# 初始化LLM接口和对话上下文
llm = LLMInterface()
dialogue_context = DialogueContext()

def get_today_chat_logs():
    """获取今天的聊天记录"""
    filename = f"chat_logs/chat_{datetime.now().strftime('%Y%m%d')}.json"
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                messages = []
                for log in logs:
                    # 添加用户消息
                    messages.append({
                        'id': f"{log['timestamp']}_user",
                        'content': log['message'],
                        'sender': log['user'],
                        'timestamp': log['timestamp']
                    })
                    # 添加AI回应
                    if log.get('ai_response'):  # 检查ai_response是否存在
                        ai_response = log['ai_response']
                        # 确保ai_response是字典类型
                        if isinstance(ai_response, dict):
                            # 根据用户身份选择对应的回应
                            responses = ai_response.get('responses', {})
                            analysis = ai_response.get('analysis', {})
                            current_response = responses.get('to_others', '')
                            
                            if log['user'] == analysis.get('attacker'):
                                current_response = responses.get('to_attacker', '')
                            elif log['user'] == analysis.get('victim'):
                                current_response = responses.get('to_victim', '')
                            
                            messages.append({
                                'id': f"{log['timestamp']}_ai",
                                'content': current_response,
                                'sender': 'AI助手',
                                'timestamp': log['timestamp'],
                                'aiResponse': {
                                    'is_anomaly': ai_response.get('is_anomaly', False),
                                    'reason': ai_response.get('reason', ''),
                                    'analysis': analysis,
                                    'responses': responses,
                                    'response': current_response
                                }
                            })
                return messages
        return []
    except Exception as e:
        print(f"读取对话记录时出错: {str(e)}")
        return []

def save_chat_log(user: str, message: str, ai_response: Dict[str, Any]):
    """保存对话记录到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 根据用户身份选择对应的回应
    analysis = ai_response['analysis']
    responses = ai_response['responses']
    
    if user == analysis.get('attacker'):
        current_response = responses['to_attacker']
    elif user == analysis.get('victim'):
        current_response = responses['to_victim']
    else:
        current_response = responses['to_others']
    
    log_entry = {
        'timestamp': timestamp,
        'user': user,
        'message': message,
        'ai_response': {
            'response': current_response,
            'is_anomaly': ai_response['is_anomaly'],
            'reason': ai_response['reason'],
            'analysis': analysis,
            'responses': responses
        }
    }
    
    filename = f"chat_logs/chat_{datetime.now().strftime('%Y%m%d')}.json"
    
    try:
        # 读取现有记录
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # 添加新记录
        logs.append(log_entry)
        
        # 保存所有记录
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"保存对话记录时出错: {str(e)}")

def detect_anomaly(message: str, current_user: str) -> Tuple[bool, str, Dict[str, Any]]:
    """检测对话是否存在异常"""
    try:
        context = dialogue_context.get_context()
        # 调用LLM接口进行分析
        return llm.analyze_dialogue(context, message)
    except Exception as e:
        print(f"检测异常时出错: {str(e)}")
        return False, "", {
            "analysis": {"attacker": "", "victim": ""},
            "responses": {
                "to_attacker": "抱歉，检测过程出现错误。",
                "to_victim": "抱歉，检测过程出现错误。",
                "to_others": "抱歉，检测过程出现错误。"
            }
        }

# def generate_ai_response(user: str, message: str, is_anomaly: bool, anomaly_reason: str) -> str:
#     """使用LLM生成回应"""
#     context = dialogue_context.get_context()
#     _, _, response = llm.analyze_dialogue(context, message)
#     return response

def clear_chat_logs():
    """清空今天的聊天记录"""
    filename = f"chat_logs/chat_{datetime.now().strftime('%Y%m%d')}.json"
    try:
        # 创建空的JSON文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("聊天记录已清空")
    except Exception as e:
        print(f"清空聊天记录时出错: {str(e)}")

@app.route('/chat/history', methods=['GET'])
def get_history():
    """获取历史聊天记录"""
    try:
        messages = get_today_chat_logs()
        # print("返回的历史消息:", messages)  # 添加调试日志
        return jsonify({'messages': messages})
    except Exception as e:
        print(f"获取历史记录时出错: {str(e)}")  # 添加错误日志
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user = data.get('user')
        message = data.get('message')
        
        if not user or not message:
            return jsonify({'error': '缺少必要参数'}), 400
        
        if message.lower() == "clear":
            clear_chat_logs()
            dialogue_context.history = []
            return jsonify({
                'response': "历史记录已清空",
                'is_anomaly': False,
                'reason': ""
            })
        
        dialogue_context.add_message({
            'user': user,
            'message': message
        })
        
        # 检测异常并获取回应，传入当前用户
        is_anomaly, reason, result = detect_anomaly(message, user)

        print("is_anomaly:",is_anomaly)
        print("reason:",reason)
        print("result:",result)
        
        # 根据当前用户角色选择合适的回应
        analysis = result['analysis']
        responses = result['responses']
        
        # 根据用户身份选择对应的回应
        if user == analysis.get('attacker'):
            current_response = responses['to_attacker']
        elif user == analysis.get('victim'):
            current_response = responses['to_victim']
        else:
            current_response = responses['to_others']
        
        # 保存对话记录
        save_chat_log(user, message, {
            'is_anomaly': is_anomaly,
            'reason': reason,
            'analysis': analysis,
            'responses': responses
        })
        
        return jsonify({
            'response': current_response,
            'is_anomaly': is_anomaly,
            'reason': reason,
            'analysis': analysis,
            'responses': responses
        })
        
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 