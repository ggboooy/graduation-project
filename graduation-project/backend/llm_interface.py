from typing import Tuple
import json

class LLMInterface:
    def analyze_dialogue(self, context: str, current_message: str) -> Tuple[bool, str, str]:
        """分析对话内容，检测异常并生成回应"""
        prompt = f"""你是一个专门负责检测和干预异常对话的AI助手。请仔细分析对话内容，特别关注最近的对话上下文。

对话内容:
历史对话上下文:
{context}

当前消息:
{current_message}

请特别注意：
1. 重点关注最近的对话内容
2. 如果发现不当言论，要给出明确的干预
3. 如果检测到自伤倾向，要给出关怀和建议
4. 回应要针对性强，不要泛泛而谈

请直接输出以下格式的JSON（不要包含任何其他内容）:
{{
    "is_anomaly": true/false,
    "reason": "检测到异常时说明原因，没有异常则留空",
    "response": "给出一个恰当的回应，要针对当前的具体情况"
}}

注意：
1. 只输出一个JSON对象
2. 不要包含<think>等标记
3. 不要有任何其他输出
4. 回应要体现出对上下文的理解
"""
        try:
            result = ollama.chat(
                model="deepseek-r1:7b",
                stream=False,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0}
            )
            
            response_text = result['message']['content'].strip()
            
            # 如果包含多个JSON，只取第一个
            if '```json' in response_text:
                json_parts = response_text.split('```json')
                for part in json_parts:
                    if '}' in part:
                        response_text = part.split('}')[0] + '}'
                        break
            
            try:
                parsed_result = json.loads(response_text)
                is_anomaly = bool(parsed_result.get("is_anomaly", False))
                reason = str(parsed_result.get("reason", ""))
                
                # 根据是否检测到异常返回不同的回应
                if not is_anomaly:
                    response = "我没有检测到异常，请继续保持良好的交流氛围。"
                else:
                    response = str(parsed_result.get("response", ""))
                    if not response.strip():
                        response = "检测到异常，请注意您的表达方式。"
                
                return (is_anomaly, reason, response)
                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")
                return (False, "", "我没有检测到异常，请继续保持良好的交流氛围。")
            
        except Exception as e:
            print(f"调用AI模型时出错: {str(e)}")
            return (False, "", "我没有检测到异常，请继续保持良好的交流氛围。") 