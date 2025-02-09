from typing import Tuple, List, Dict
import json
import ollama # type: ignore

class DialogueContext:
    def __init__(self, max_history: int = 5):
        self.history = []
        self.max_history = max_history
    
    def add_message(self, message: Dict):
        self.history.append(message)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context(self) -> str:
        """将历史对话格式化为文本"""
        context = []
        for msg in self.history:
            context.append(f"{msg['user']}: {msg['message']}")
        return "\n".join(context)

class LLMInterface:
    def __init__(self):
        # 在这里初始化您的本地大模型
        # 例如:
        # self.model = AutoModelForCausalLM.from_pretrained("your_model_path")
        # self.tokenizer = AutoTokenizer.from_pretrained("your_model_path")
        pass
    
    def analyze_dialogue(self, context: str, current_message: str) -> Tuple[bool, str, str]:
        """分析对话内容，检测异常并生成回应"""
        # 构建提示模板
        prompt = f"""你是一个专门负责检测和干预异常对话的AI助手。请分析以下对话内容，并严格按照要求的JSON格式输出。

对话内容:
历史对话上下文:
{context}

当前消息:
{current_message}

异常行为类型：
1. 不当用语或辱骂
2. 人身攻击
3. 不当情绪表达
4. 打断或干扰他人发言
5. 偏离学习主题
6. 消极或不配合的态度

请直接输出以下格式的JSON（不要包含任何其他内容）:
{{
    "is_anomaly": true/false,
    "reason": "检测到异常时说明原因，没有异常则留空",
    "response": "给出适当的回应。如果检测到异常，应该礼貌但坚定地指出问题并进行干预；如果没有异常，给出积极的反馈"
}}

注意：
1. 只输出JSON格式内容，不要有其他文字
2. 不要包含<think>等标记
3. JSON中的布尔值必须是true或false，不要使用引号
4. reason在没有异常时应为空字符串
"""
        try:
            # 调用本地大模型进行分析
            result = ollama.chat(
                model="deepseek-r1:7b",
                stream=False,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0}
            )
            
            # 从result中提取message内容
            response_text = result['message']['content'].strip()
            print("AI原始响应:", response_text)
            
            # 尝试解析JSON响应
            try:
                # 如果响应包含多余的内容，尝试提取JSON部分
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                
                parsed_result = json.loads(response_text)
                
                # 确保布尔值正确
                is_anomaly = bool(parsed_result.get("is_anomaly", False))
                reason = str(parsed_result.get("reason", ""))
                response = str(parsed_result.get("response", "我没有检测到异常，请继续保持良好的交流氛围。"))
                
                return (is_anomaly, reason, response)
                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")
                print("问题响应:", response_text)
                # 如果无法解析JSON，返回默认值
                return (
                    False,
                    "",
                    "继续保持良好的学习氛围"
                )
                
        except Exception as e:
            print(f"调用AI模型时出错: {str(e)}")
            # 发生错误时返回默认值
            return (
                False,
                "",
                "抱歉，我现在无法正确分析对话，请稍后再试。"
            ) 