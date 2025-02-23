from typing import Tuple, List, Dict, Any
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
    
    def analyze_dialogue(self, context: str, current_message: str) -> Tuple[bool, str, Dict[str, Any]]:
        """分析对话内容，检测异常并生成回应"""
        prompt = f"""你是一个专门负责检测和干预异常对话的AI助手。请仔细分析对话内容，特别关注最近的对话上下文。

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

请特别注意：
1. 重点关注最近的对话内容
2. 需要针对不同角色生成不同的回应：
   - 对攻击者：指出问题并进行教育性劝阻
   - 对被攻击者：提供安慰和支持
   - 对其他人：引导正确的讨论方向
3. 如果检测到自伤倾向，要立即表达关心并建议寻求帮助
4. 如果是正常对话，只需返回固定回复

请直接输出以下格式的JSON（不要包含任何其他内容）:
{{
    "is_anomaly": true/false,
    "reason": "检测到异常时说明原因，没有异常则留空",
    "analysis": {{
        "attacker": "攻击者的用户名，如果没有攻击行为则留空",
        "victim": "被攻击者的用户名，如果没有攻击行为则留空"
    }},
    "responses": {{
        "to_attacker": "对攻击者的劝阻回应",
        "to_victim": "对被攻击者的安慰回应",
        "to_others": "对其他人的引导回应"
    }}
}}
"""
        try:
            # 调用本地大模型进行分析
            result = ollama.chat(
                model="deepseek-r1",
                stream=False,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0}
            )
            
            response_text = result['message']['content'].strip()
            
            try:
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                
                parsed_result = json.loads(response_text)
                
                # 提取结果
                is_anomaly = bool(parsed_result.get("is_anomaly", False))
                reason = str(parsed_result.get("reason", ""))
                analysis = parsed_result.get("analysis", {})
                responses = parsed_result.get("responses", {})
                
                # 如果不是异常对话，使用默认回应
                if not is_anomaly:
                    default_response = "我没有检测到异常，请继续保持良好的交流氛围。"
                    responses = {
                        "to_attacker": default_response,
                        "to_victim": default_response,
                        "to_others": default_response
                    }
                    analysis = {"attacker": "", "victim": ""}
                
                return (is_anomaly, reason, {
                    "analysis": analysis,
                    "responses": responses
                })
                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")
                return (
                    False,
                    "",
                    {
                        "analysis": {"attacker": "", "victim": ""},
                        "responses": {
                            "to_attacker": "继续保持良好的学习氛围",
                            "to_victim": "继续保持良好的学习氛围",
                            "to_others": "继续保持良好的学习氛围"
                        }
                    }
                )
                
        except Exception as e:
            print(f"调用AI模型时出错: {str(e)}")
            return (
                False,
                "",
                {
                    "analysis": {"attacker": "", "victim": ""},
                    "responses": {
                        "to_attacker": "抱歉，我现在无法正确分析对话，请稍后再试。",
                        "to_victim": "抱歉，我现在无法正确分析对话，请稍后再试。",
                        "to_others": "抱歉，我现在无法正确分析对话，请稍后再试。"
                    }
                }
            ) 