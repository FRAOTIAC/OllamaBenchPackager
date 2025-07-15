#!/usr/bin/env python3
"""
车载语音助手测试文件
测试核心功能：指令识别、JSON输出、多轮对话
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

from loguru import logger

from vehicle_assistant_v2 import VehicleAssistant

# from va_assistant import VehicleAssistant


def test_basic_commands():
    """测试基础指令"""
    print("=" * 50)
    print("🧪 测试基础指令")
    print("=" * 50)

    assistant = VehicleAssistant()

    # 基础测试用例
    test_cases = [
        "把空调打开",
        "关闭空调",
        "空调开大点",
        "空调开小点",
        "温度调高点",
        "温度调低点",
        "打开车窗",
        "关闭车窗",
        "车窗升起来",
        "车窗降下去",
        "打开远光灯",
        "关闭远光灯",
        "开启近光灯",
        "关闭近光灯",
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case}")
        result = assistant.process_command(test_case)

        print(f"   回复: {result['response']}")
        if result["success"]:
            tool_call = result["tool_call"]
            print(
                f"   工具调用: {tool_call['veh_object']} -> {tool_call['veh_operation']}"
            )
            results.append(
                {
                    "input": test_case,
                    "success": True,
                    "veh_object": tool_call["veh_object"],
                    "veh_operation": tool_call["veh_operation"],
                }
            )
        else:
            print(f"   ❌ 失败")
            results.append({"input": test_case, "success": False})

    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    success_rate = success_count / total_count * 100

    print(f"\n📊 基础指令测试结果:")
    print(f"   成功: {success_count}/{total_count} ({success_rate:.1f}%)")

    return results


def test_multi_turn_conversation():
    """测试多轮对话"""
    print("\n" + "=" * 50)
    print("🧪 测试多轮对话")
    print("=" * 50)

    assistant = VehicleAssistant()

    # 多轮对话测试用例
    conversation_steps = [
        "打开空调",
        "调大风量",
        "温度调低点",
        "关闭车窗",
        "打开远光灯",
    ]

    print("模拟多轮对话场景...")
    for i, step in enumerate(conversation_steps, 1):
        print(f"\n第{i}轮:")
        print(f"用户: {step}")

        result = assistant.process_command(step)
        print(f"助手: {result['response']}")

        if result["success"]:
            tool_call = result["tool_call"]
            print(
                f"工具调用: {tool_call['veh_object']} -> {tool_call['veh_operation']}"
            )

        # 显示当前状态
        print(f"当前状态: {assistant._format_vehicle_state()}")

        # 显示上下文压缩
        context = assistant._compress_context()
        if context:
            print(f"上下文: {context}")

    print(f"\n📊 多轮对话测试完成，共{len(conversation_steps)}轮")


def test_context_management():
    """测试上下文管理"""
    print("\n" + "=" * 50)
    print("🧪 测试上下文管理")
    print("=" * 50)

    assistant = VehicleAssistant()

    # 超出上下文长度的测试
    long_conversation = [
        "打开空调",
        "调大风量",
        "温度调高",
        "关闭车窗",
        "打开远光灯",
        "关闭近光灯",
        "开启位置灯",
    ]

    print("测试上下文长度限制...")
    for i, command in enumerate(long_conversation, 1):
        print(f"\n第{i}轮: {command}")
        result = assistant.process_command(command)

        if result["success"]:
            tool_call = result["tool_call"]
            print(
                f"工具调用: {tool_call['veh_object']} -> {tool_call['veh_operation']}"
            )

        # 显示上下文长度
        history_length = len(assistant.conversation_history)
        print(f"历史记录长度: {history_length}")

        # 显示压缩后的上下文
        compressed_context = assistant._compress_context()
        if compressed_context:
            print(f"压缩上下文: {compressed_context}")

    print(f"\n📊 上下文管理测试完成")
    print(f"   最大历史记录长度: {assistant.max_context_length}")
    print(f"   实际历史记录长度: {len(assistant.conversation_history)}")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 50)
    print("🧪 测试错误处理")
    print("=" * 50)

    assistant = VehicleAssistant()

    # 错误测试用例
    error_cases = [
        "调节空调",  # 模糊指令
        "开灯",  # 不明确指令
        "关窗",  # 简短指令
        "温度",  # 单词指令
        "播放音乐",  # 不支持的功能
        "你好",  # 非指令
    ]

    print("测试错误处理...")
    for i, error_case in enumerate(error_cases, 1):
        print(f"\n{i}. 测试: {error_case}")
        result = assistant.process_command(error_case)

        print(f"   回复: {result['response']}")
        print(f"   成功: {result['success']}")

        if result["tool_call"]:
            tool_call = result["tool_call"]
            print(f"   工具调用: {tool_call}")

    print(f"\n📊 错误处理测试完成")


def test_json_parsing():
    """测试JSON解析功能"""
    print("\n" + "=" * 50)
    print("🧪 测试JSON解析")
    print("=" * 50)

    assistant = VehicleAssistant()

    # 测试不同的JSON格式
    test_responses = [
        '{"u_message":"空调已开启","veh_object":"air_switch","veh_operation":"open"}',
        '{\n  "u_message": "空调已开启",\n  "veh_object": "air_switch",\n  "veh_operation": "open"\n}',
        '好的！{"u_message":"空调已开启","veh_object":"air_switch","veh_operation":"open"}',
        '{"u_message":"空调已开启","veh_object":"air_switch","veh_operation":"open"} 完成！',
        '{"u_message":"空调已开启"}',  # 缺少字段
        "空调已开启",  # 非JSON格式
    ]

    print("测试JSON解析...")
    for i, response in enumerate(test_responses, 1):
        print(f"\n{i}. 测试响应: {response}")
        parsed = assistant._parse_json_response(response)

        if parsed:
            print(f"   解析成功: {parsed}")
        else:
            print(f"   解析失败")

    print(f"\n📊 JSON解析测试完成")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始车载语音助手测试")
    print("=" * 60)

    try:
        # 运行所有测试
        test_basic_commands()
        test_multi_turn_conversation()
        test_context_management()
        test_error_handling()
        test_json_parsing()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        logger.error(f"测试错误: {e}")


if __name__ == "__main__":
    run_all_tests()
