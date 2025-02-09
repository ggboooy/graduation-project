from typing import Tuple
from flask import request, jsonify
from graduation-project.backend.dialogue_context import DialogueContext
from graduation-project.backend.llm import LLM

app = Flask(__name__)

def detect_anomaly(message: str) -> Tuple[bool, str, str]:
    """使用LLM检测对话是否异常，同时返回回应"""
    context = dialogue_context.get_context()
    is_anomaly, reason, response = llm.analyze_dialogue(context, message)
    return is_anomaly, reason, response

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
        
        # 检测异常并获取回应
        is_anomaly, anomaly_reason, ai_response = detect_anomaly(message)
        
        # 保存对话记录
        save_chat_log(user, message, ai_response)
        
        return jsonify({
            'response': ai_response,
            'is_anomaly': is_anomaly,
            'anomaly_reason': anomaly_reason
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 