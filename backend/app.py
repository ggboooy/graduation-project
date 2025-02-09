from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import os
from typing import Tuple
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
                    if log['ai_response']:  # 只有当AI回应存在时才添加
                        messages.append({
                            'id': f"{log['timestamp']}_ai",
                            'content': log['ai_response'],
                            'sender': 'AI助手',
                            'timestamp': log['timestamp']
                        })
                return messages
        return []
    except Exception as e:
        print(f"读取对话记录时出错: {str(e)}")
        return []

def save_chat_log(user, message, ai_response):
    """保存对话记录到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'user': user,
        'message': message,
        'ai_response': ai_response
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

def detect_anomaly(message: str) -> Tuple[bool, str]:
    """使用LLM检测对话是否异常"""
    context = dialogue_context.get_context()
    is_anomaly, reason, _ = llm.analyze_dialogue(context, message)
    return is_anomaly, reason

def generate_ai_response(user: str, message: str, is_anomaly: bool, anomaly_reason: str) -> str:
    """使用LLM生成回应"""
    context = dialogue_context.get_context()
    _, _, response = llm.analyze_dialogue(context, message)
    return response

@app.route('/chat/history', methods=['GET'])
def get_history():
    """获取历史聊天记录"""
    try:
        messages = get_today_chat_logs()
        print("返回的历史消息:", messages)  # 添加调试日志
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
        
        # 添加消息到上下文
        dialogue_context.add_message({
            'user': user,
            'message': message
        })
        
        # 检测异常
        is_anomaly, anomaly_reason = detect_anomaly(message)
        
        # 生成AI回应
        ai_response = generate_ai_response(user, message, is_anomaly, anomaly_reason)
        
        # 保存对话记录
        save_chat_log(user, message, ai_response)
        
        return jsonify({
            'response': ai_response,
            'is_anomaly': is_anomaly,
            'anomaly_reason': anomaly_reason
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 