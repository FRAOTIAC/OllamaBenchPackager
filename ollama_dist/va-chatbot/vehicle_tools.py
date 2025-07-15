#! /usr/bin/env python3
"""
车载语音助手 V3 的工具集模块
"""
from typing import Literal

from langchain_core.tools import tool
from loguru import logger
from pydantic import BaseModel, Field

# --- Pydantic 输入模型定义 ---


class LightControlInput(BaseModel):
    light_type: Literal["lbeam", "hbeam", "poslgt"] = Field(
        "lbeam",
        description="要操作的灯光类型。'lbeam' (近光灯), 'hbeam' (远光灯), 'poslgt' (位置灯)。如果用户指令模糊，默认为 'lbeam'。",
    )


class AdjustAcInput(BaseModel):
    parameter: Literal["volume", "temp"] = Field(
        ..., description="要调节的空调参数。'volume' (风量) 或 'temp' (温度)。"
    )
    direction: Literal["up", "down"] = Field(
        ..., description="调节方向。'up' (调高/调大) 或 'down' (调小/调低)。"
    )


class WindowControlInput(BaseModel):
    operation: Literal["open", "close"] = Field(
        ...,
        description="要对车窗执行的操作。'open' (降下车窗) 或 'close' (升起车窗)。",
    )


class VehicleToolManager:
    """管理所有车辆工具和车辆状态的类"""

    def __init__(self):
        """初始化，定义车辆状态和可用工具列表"""
        self.vehicle_state = {}
        # 注意：这里我们直接将实例方法作为工具传递
        self.available_tools = [
            self.turn_on_light,
            self.turn_off_light,
            self.turn_on_ac,
            self.turn_off_ac,
            self.adjust_ac,
            self.operate_car_window,
            self.turn_on_dms,
            self.turn_off_dms,
        ]

    # --- 工具函数定义 (现在是方法) ---

    @tool(args_schema=LightControlInput)
    def turn_on_light(self, light_type: Literal["lbeam", "hbeam", "poslgt"]):
        """打开指定类型的车灯。当用户想要开灯时使用。"""
        light_map = {"lbeam": "近光灯", "hbeam": "远光灯", "poslgt": "位置灯"}
        light_name = light_map.get(light_type, "未知车灯")
        self.vehicle_state[f"{light_type}_control"] = "开启"
        logger.info(f"状态更新: {light_type}_control -> 开启")
        return f"好的，已为您打开{light_name}。"

    @tool(args_schema=LightControlInput)
    def turn_off_light(self, light_type: Literal["lbeam", "hbeam", "poslgt"]):
        """关闭指定类型的车灯。当用户想要关灯时使用。"""
        light_map = {"lbeam": "近光灯", "hbeam": "远光灯", "poslgt": "位置灯"}
        light_name = light_map.get(light_type, "未知车灯")
        self.vehicle_state[f"{light_type}_control"] = "关闭"
        logger.info(f"状态更新: {light_type}_control -> 关闭")
        return f"好的，已为您关闭{light_name}。"

    @tool
    def turn_on_ac(self):
        """打开空调。"""
        self.vehicle_state["air_switch"] = "开启"
        logger.info("状态更新: air_switch -> 开启")
        return "好的，空调已打开。"

    @tool
    def turn_off_ac(self):
        """关闭空调。"""
        self.vehicle_state["air_switch"] = "关闭"
        logger.info("状态更新: air_switch -> 关闭")
        return "好的，空调已关闭。"

    @tool(args_schema=AdjustAcInput)
    def adjust_ac(
        self, parameter: Literal["volume", "temp"], direction: Literal["up", "down"]
    ):
        """调节空调的温度或风量。"""
        param_map = {"volume": "风量", "temp": "温度"}
        direction_map = {
            "up": "大" if parameter == "volume" else "高",
            "down": "小" if parameter == "volume" else "低",
        }
        param_name = param_map.get(parameter)
        state_key = f"air_{parameter}"

        current_level = self.vehicle_state.get(state_key, "中")
        if direction == "up":
            new_level = "高" if current_level != "低" else "中"
        else:  # down
            new_level = "低" if current_level != "高" else "中"

        self.vehicle_state[state_key] = new_level
        logger.info(f"状态更新: {state_key} -> {new_level}")

        return f"好的，已将空调{param_name}调{direction_map[direction]}。"

    @tool(args_schema=WindowControlInput)
    def operate_car_window(self, operation: Literal["open", "close"]):
        """操作车窗。用于打开(降下)或关闭(升起)车窗。"""
        op_name = "打开" if operation == "open" else "关闭"
        self.vehicle_state["car_window"] = op_name
        logger.info(f"状态更新: car_window -> {op_name}")
        return f"好的，车窗已{op_name}。"

    @tool
    def turn_on_dms(self):
        """打开驾驶员疲劳检测系统(DMS)。"""
        self.vehicle_state["dms_control"] = "开启"
        logger.info("状态更新: dms_control -> 开启")
        return "好的，驾驶员检测系统已开启。"

    @tool
    def turn_off_dms(self):
        """关闭驾驶员疲劳检测系统(DMS)。"""
        self.vehicle_state["dms_control"] = "关闭"
        logger.info("状态更新: dms_control -> 关闭")
        return "好的，驾驶员检测系统已关闭。"
