#!/usr/bin/env python3
"""
车载语音助手 V2 - 优化版
针对0.5b小模型优化，支持多轮对话和JSON工具调用
"""

import json
import re
from typing import Any, Dict, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from loguru import logger
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory


class VehicleAssistant:
    """车载语音助手主类"""

    # 车辆功能定义
    VEHICLE_FUNCTIONS = {
        "air_switch": "空调开关",
        "air_volume": "空调风量",
        "air_temp": "空调温度",
        "car_window": "车窗",
        "dms_control": "驾驶员检测",
        "poslgt_control": "位置灯",
        "hbeam_control": "远光灯",
        "lbeam_control": "近光灯",
    }

    # 操作定义
    OPERATIONS = {
        "open": "打开",
        "close": "关闭",
        "up": "调大/调高",
        "down": "调小/调低",
    }

    # 只有这些功能支持up/down操作
    ADJUSTABLE_FUNCTIONS = {"air_volume", "air_temp", "car_window"}

    def __init__(self, model_name: str = "qwen3:0.6b"):
        """初始化车载助手"""
        self.model = OllamaLLM(model=model_name)
        self.vehicle_state = {}  # 车辆状态跟踪
        self.conversation_history = []  # 对话历史
        self.max_context_length = 3  # 最大上下文轮数

        # 针对小模型优化的约束性提示词模板，加入了示例
        self.template = """你是车载语音助手，任务是精确地将用户指令转换为JSON格式。

# 功能列表 (veh_object)
- air_switch
- air_volume
- air_temp
- car_window
- dms_control
- poslgt_control
- hbeam_control
- lbeam_control

# 操作列表 (veh_operation)
- open 打开
- close 关闭
- up 调大/调高 (仅支持 air_volume, air_temp)
- down 调小/调低 (仅支持 air_volume, air_temp)

# 规则
1. 必须从上面的列表中选择 veh_object 和 veh_operation。
2. `up` 或 `down` 操作只能用于 `air_volume`, `air_temp`。
3. 如果指令模糊(如"开灯")，优先选择最常用的 `lbeam_control` (近光灯)。
4. 生成一个简短友好的 `u_message` 来确认操作。
5. 严格按照 {{"u_message":"","veh_object":"","veh_operation":""}} 格式输出，不要添加任何额外文本。

# 示例
- 用户: "打开车灯" -> {{"u_message":"好的，已为您打开近光灯。","veh_object":"lbeam_control","veh_operation":"open"}}
- 用户: "关掉大灯" -> {{"u_message":"好的，已为您关闭远光灯。","veh_object":"hbeam_control","veh_operation":"close"}}
- 用户: "空调开大点" -> {{"u_message":"好的，已将空调风量调大。","veh_object":"air_volume","veh_operation":"up"}}

# 当前状态
车辆状态: {vehicle_state}
对话历史: {context}

# 用户指令
用户: {question}

# 输出
/no_think
"""

        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.chain = self.prompt | self.model

    def _compress_context(self) -> str:
        """压缩对话上下文，适应小模型的短上下文限制"""
        if not self.conversation_history:
            return ""

        # 只保留最近的几轮对话
        recent_history = self.conversation_history[-self.max_context_length :]

        # 压缩格式：User: 指令 -> 操作结果
        compressed = []
        for item in recent_history:
            user_input = item.get("user_input", "")
            veh_object = item.get("veh_object", "")
            veh_operation = item.get("veh_operation", "")

            if veh_object and veh_operation:
                compressed.append(f"User: {user_input} -> {veh_object}:{veh_operation}")

        return " | ".join(compressed)

    def _format_vehicle_state(self) -> str:
        """格式化车辆状态信息"""
        if not self.vehicle_state:
            return "无"

        state_items = []
        for func, status in self.vehicle_state.items():
            func_name = self.VEHICLE_FUNCTIONS.get(func, func)
            state_items.append(f"{func_name}:{status}")

        return ",".join(state_items)

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        更健壮的JSON响应解析器。
        可以处理 <think> 标签和 markdown JSON 代码块。
        """
        try:
            # 1. 移除 think 标签（如果有的话）
            response = re.sub(
                r"<think>.*?</think>", "", response, flags=re.DOTALL
            ).strip()

            # 2. 查找 markdown JSON 块
            json_match = re.search(
                r"```json\s*(\{.*?\})\s*```", response, flags=re.DOTALL
            )
            json_str = ""
            if json_match:
                json_str = json_match.group(1)
            else:
                # 3. 如果没有 markdown 块，直接查找 JSON 对象
                json_match = re.search(r"\{.*\}", response, flags=re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)

            if not json_str:
                logger.warning(f"响应中未找到有效的JSON部分: {response}")
                return None

            parsed = json.loads(json_str)

            # 验证必需字段及其值不为空
            required_fields = ["u_message", "veh_object", "veh_operation"]
            if all(field in parsed and parsed[field] for field in required_fields):
                return parsed

            logger.warning(f"解析后的JSON缺少必要字段或字段值为空: {parsed}")
            return None

        except json.JSONDecodeError:
            # 在解析失败时，记录下准备解析的字符串，方便调试
            logger.error(f"JSON解析错误, 原始字符串: '{json_str}'")
            return None
        except Exception as e:
            logger.error(f"解析响应时发生未知错误: {e}, 响应: {response}")
            return None

    def _validate_command(self, veh_object: str, veh_operation: str) -> bool:
        """验证指令的有效性"""
        # 检查功能是否存在
        if veh_object not in self.VEHICLE_FUNCTIONS:
            logger.warning(f"未知的车辆功能: {veh_object}")
            return False

        # 检查操作是否存在
        if veh_operation not in self.OPERATIONS:
            logger.warning(f"未知的操作: {veh_operation}")
            return False

        # 检查up/down操作是否只用于可调节功能
        if (
            veh_operation in ["up", "down"]
            and veh_object not in self.ADJUSTABLE_FUNCTIONS
        ):
            logger.warning(f"功能 {veh_object} 不支持 {veh_operation} 操作")
            return False

        return True

    def _update_vehicle_state(self, veh_object: str, veh_operation: str):
        """更新车辆状态"""
        if veh_operation == "open":
            self.vehicle_state[veh_object] = "开启"
        elif veh_operation == "close":
            self.vehicle_state[veh_object] = "关闭"
        elif veh_operation == "up":
            current = self.vehicle_state.get(veh_object, "中等")
            if current == "低":
                self.vehicle_state[veh_object] = "中等"
            else:
                self.vehicle_state[veh_object] = "高"
        elif veh_operation == "down":
            current = self.vehicle_state.get(veh_object, "中等")
            if current == "高":
                self.vehicle_state[veh_object] = "中等"
            else:
                self.vehicle_state[veh_object] = "低"

    def process_command(self, user_input: str) -> Dict[str, Any]:
        """处理用户指令"""
        try:
            # 准备上下文
            context = self._compress_context()
            vehicle_state = self._format_vehicle_state()

            # 调用模型 (流式)
            stream = self.chain.stream(
                {
                    "context": context,
                    "vehicle_state": vehicle_state,
                    "question": user_input,
                }
            )

            print("🤖 助手: ", end="", flush=True)
            response = ""
            for chunk in stream:
                print(chunk, end="", flush=True)
                response += chunk
            print()  # Newline after stream ends

            logger.info(f"模型原始响应: {response}")

            # 解析JSON
            parsed_response = self._parse_json_response(response)

            if parsed_response:
                veh_object = parsed_response["veh_object"]
                veh_operation = parsed_response["veh_operation"]
                u_message = parsed_response["u_message"]

                # 验证指令
                if self._validate_command(veh_object, veh_operation):
                    # 更新状态
                    self._update_vehicle_state(veh_object, veh_operation)

                    # 记录对话历史
                    self.conversation_history.append(
                        {
                            "user_input": user_input,
                            "veh_object": veh_object,
                            "veh_operation": veh_operation,
                            "u_message": u_message,
                        }
                    )

                    # 限制历史记录长度
                    if len(self.conversation_history) > self.max_context_length:
                        self.conversation_history.pop(0)

                    return {
                        "response": u_message,
                        "tool_call": parsed_response,
                        "success": True,
                    }
                else:
                    error_msg = "抱歉，我不理解这个指令，请再试一次～"
                    # 流式输出可能已经输出了部分内容，我们在这里补全一句提示
                    # 打印一个换行符来分隔错误的流式输出和我们的错误信息
                    print(f"🤖 助手: {error_msg}")
                    return {
                        "response": error_msg,
                        "tool_call": None,
                        "success": False,
                    }
            else:
                error_msg = "抱歉，我遇到了一些问题，请再试一次～"
                # 同样，在流式输出后补充错误信息
                print(f"🤖 助手: {error_msg}")
                return {
                    "response": error_msg,
                    "tool_call": None,
                    "success": False,
                }

        except Exception as e:
            logger.error(f"处理指令时发生错误: {e}")
            error_msg = "系统出现错误，请稍后再试～"
            print(f"🤖 助手: {error_msg}")
            return {
                "response": error_msg,
                "tool_call": None,
                "success": False,
            }

    def _warmup_model(self):
        """预热模型，减少首次响应延迟"""
        logger.info("正在预热模型，请稍候...")
        try:
            # 使用一个简单的、通用的提示词来预热
            self.model.invoke("你好")
            logger.info("✅ 模型预热完成！")
        except Exception as e:
            logger.error(f"模型预热失败: {e}")

    def start_conversation(self):
        """启动对话循环"""
        logger.info("🚗 车载语音助手已启动！")
        logger.info("支持的功能：空调、车窗、灯光控制等")
        logger.info("提示: 使用 ↑ 和 ↓ 箭头可以浏览历史指令。")
        logger.info("输入 'exit' 或 'quit' 退出")
        logger.info("-" * 50)

        history = InMemoryHistory()

        while True:
            try:
                user_input = prompt("\n🎤 您: ", history=history).strip()

                if user_input.lower() in ["exit", "quit", "bye", "退出"]:
                    logger.info("👋 再见！祝您行车愉快！")
                    break

                if not user_input:
                    continue

                # 处理指令 (现在 process_command 会自己打印流式响应)
                result = self.process_command(user_input)

                # 仅在成功时显示工具调用和状态
                if result["success"]:
                    if result["tool_call"]:
                        tool_call = result["tool_call"]
                        print(
                            f"🔧 工具调用: {tool_call['veh_object']} -> {tool_call['veh_operation']}"
                        )

                    # 显示当前状态
                    if self.vehicle_state:
                        print(f"📊 当前状态: {self._format_vehicle_state()}")

            except KeyboardInterrupt:
                logger.info("\n👋 再见！祝您行车愉快！")
                break
            except Exception as e:
                logger.error(f"对话过程中发生错误: {e}")
                print("🤖 助手: 系统出现错误，请稍后再试～")


def main():
    """主函数"""
    assistant = VehicleAssistant()
    assistant._warmup_model()
    assistant.start_conversation()


if __name__ == "__main__":
    main()
