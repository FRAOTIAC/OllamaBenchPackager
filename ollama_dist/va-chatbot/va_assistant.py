#! /usr/bin/env python3
"""
基于LangChain的车载语音助手改进版
支持链式处理、记忆功能、工具集成、RAG等高级特性
"""

from typing import Annotated

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from loguru import logger
from pydantic import BaseModel, Field
from vehicle_tools import VehicleToolManager


# 定义结构化输出
class VehicleAssistantOutput(BaseModel):
    response: str = Field(description="回复用户的消息")
    tool_calls: list[str] = Field(description="调用的工具名称")
    tool_call_arguments: list[dict] = Field(description="调用的工具参数")


class VehicleAssistant:
    """
    一个封装了车载语音助手所有逻辑的类。
    """

    def __init__(self, model_name: str = "qwen2:0.5b"):
        self.llm = self._configure_llm(model_name)
        self.prompt = self._create_prompt_template()

        tool_manager = VehicleToolManager()
        tools = tool_manager.available_tools

        model_with_tools = self.llm.bind_tools(tools)
        model_with_tools = model_with_tools.with_structured_output(
            VehicleAssistantOutput
        )

        self.chain = self.prompt | model_with_tools
        self._warm_up()

    def _configure_llm(self, model_name: str):
        """配置并返回Ollama LLM实例"""
        return ChatOllama(
            model=model_name,
            temperature=0.0,
            num_predict=256,
            reasoning=False,
            format="json",
        )

    def _create_prompt_template(self):
        """创建并返回聊天提示模板"""
        system = """
        你是一个车载语音助手。
        你的任务是根据用户的指令，调用合适的工具来控制车辆功能。
        请礼貌、简洁地回复用户，使用调用工具名称以及参数，以json格式返回。

        以下是一些示例：
        example_user_input: 打开空调
        example_response: {{"response": "好的，正在打开空调。", "tool_calls": "air_switch", "tool_call_ids": "air_switch_1", "tool_call_arguments": {{"air_switch": "on"}}}}
        example_user_input: 打开远光灯
        example_response: {{"response": "好的，正在打开远光灯。", "tool_calls": "hbeam_control", "tool_call_ids": "hbeam_control_1", "tool_call_arguments": {{"hbeam_control": "on"}}}}
        example_user_input: 打开近光灯
        example_response: {{"response": "好的，正在打开近光灯。", "tool_calls": "lbeam_control", "tool_call_ids": "lbeam_control_1", "tool_call_arguments": {{"lbeam_control": "on"}}}}
        """
        return ChatPromptTemplate.from_messages(
            [("system", system), ("human", "{input}")]
        )

    def _warm_up(self):
        """
        执行一次虚拟调用以预热模型，确保后续请求响应迅速。
        """
        logger.info("正在预热模型，首次启动可能需要一些时间...")
        try:
            # 使用一个简单无害的输入进行预热
            self.invoke("你好")
            logger.info("模型预热完成，车载助手已准备就绪。")
        except Exception as e:
            logger.error(f"模型预热失败: {e}")

    def invoke(self, query: str):
        """
        调用助手链并返回结果。
        """
        return self.chain.invoke({"input": query})


if __name__ == "__main__":
    assistant = VehicleAssistant(model_name="qwen3:0.6b")
    res = assistant.invoke("打开空调")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开远光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开近光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开空调")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开远光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开近光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开空调")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开远光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开近光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开空调")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开远光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开近光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开空调")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开远光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开近光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开空调")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开远光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开近光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开空调")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开远光灯")
    logger.info(res.model_dump_json())
    res = assistant.invoke("打开近光灯")
    logger.info(res.model_dump_json())
