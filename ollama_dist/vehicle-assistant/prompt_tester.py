#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车载语音助手 Prompt 测试验证工具
用于测试不同prompt版本对各种模型的效果
"""

import json
import time
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class ModelType(Enum):
    """模型类型枚举"""
    SMALL = "small"  # 1.5b-3b
    MEDIUM = "medium"  # 7b
    LARGE = "large"  # 8b+

@dataclass
class TestCase:
    """测试用例数据结构"""
    input_text: str
    expected_veh_object: str
    expected_veh_operation: str
    description: str = ""

@dataclass
class TestResult:
    """测试结果数据结构"""
    input_text: str
    raw_output: str
    parsed_json: Optional[Dict] = None
    is_valid_json: bool = False
    has_all_fields: bool = False
    correct_mapping: bool = False
    u_message_quality: int = 0  # 1-5分
    errors: List[str] = field(default_factory=list)

class PromptTester:
    """Prompt测试器"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.prompts = self._load_prompts()
    
    def _load_test_cases(self) -> List[TestCase]:
        """加载测试用例"""
        return [
            # 基础功能测试
            TestCase("把空调打开", "air_switch", "open", "空调开关-打开"),
            TestCase("关闭空调", "air_switch", "close", "空调开关-关闭"),
            TestCase("空调开大点", "air_volume", "up", "空调风量-调大"),
            TestCase("空调开小点", "air_volume", "down", "空调风量-调小"),
            TestCase("温度调高点", "air_temp", "up", "空调温度-调高"),
            TestCase("温度调低点", "air_temp", "down", "空调温度-调低"),
            TestCase("打开车窗", "car_window", "open", "车窗控制-打开"),
            TestCase("关闭车窗", "car_window", "close", "车窗控制-关闭"),
            TestCase("车窗升起来", "car_window", "up", "车窗控制-升起"),
            TestCase("车窗降下去", "car_window", "down", "车窗控制-降下"),
            TestCase("打开远光灯", "hbeam_control", "open", "远光灯-打开"),
            TestCase("关闭远光灯", "hbeam_control", "close", "远光灯-关闭"),
            TestCase("开启近光灯", "lbeam_control", "open", "近光灯-打开"),
            TestCase("关闭近光灯", "lbeam_control", "close", "近光灯-关闭"),
            
            # 同义词测试
            TestCase("把风量调大", "air_volume", "up", "同义词-风量调大"),
            TestCase("暖气热一点", "air_temp", "up", "同义词-暖气调高"),
            TestCase("制冷调强", "air_temp", "down", "同义词-制冷调强"),
            TestCase("窗户开一下", "car_window", "open", "同义词-窗户打开"),
            TestCase("大灯关掉", "hbeam_control", "close", "同义词-大灯关闭"),
            TestCase("远光关了", "hbeam_control", "close", "同义词-远光关闭"),
            
            # 边界测试
            TestCase("调节空调", "air_temp", "up", "边界-模糊指令"),
            TestCase("开灯", "lbeam_control", "open", "边界-不明确指令"),
            TestCase("关窗", "car_window", "close", "边界-简短指令"),
        ]
    
    def _load_prompts(self) -> Dict[str, str]:
        """加载不同版本的prompt"""
        return {
            "basic": """你是车载语音助手，将用户指令转换为JSON格式。

输出格式：{"u_message":"回复内容","veh_object":"功能","veh_operation":"操作"}

功能选项：
- air_switch(空调开关) air_volume(空调风量) air_temp(空调温度) 
- car_window(车窗) dms_control(驾驶员检测) poslgt_control(位置灯)
- hbeam_control(远光灯) lbeam_control(近光灯)

操作选项：
- open(打开) close(关闭) up(调大) down(调小)
- 注意：up/down只能用于air_volume、air_temp、car_window

回复要求：语气活泼，20-40字，每次句式不同

示例：
Q：把空调打开
A：{"u_message":"嗖——空调启动啦！凉风正往你这边吹呢～","veh_object":"air_switch","veh_operation":"open"}

Q：空调开小点  
A：{"u_message":"好的好的，空调调小啦！现在风力刚刚好，不会吹得你东倒西歪～","veh_object":"air_volume","veh_operation":"down"}

严格按JSON格式输出，不输出其他内容。""",
            
            "enhanced": """你是一个智能车载语音助手，专门负责理解用户的车辆控制指令并提供友好的回应。

## 重要区分说明：
- "风量大/小"、"风开大/小"、"空调开大/小" → air_volume + up/down
- "温度高/低"、"热一点/冷一点"、"暖气/制冷" → air_temp + up/down
- "空调开/关" → air_switch + open/close

## 输出格式规范
{"u_message":"用户反馈信息","veh_object":"车辆功能标识","veh_operation":"操作指令"}

### 参数说明
**veh_object 可选值：**
- air_switch: 空调开关控制
- air_volume: 空调风量调节  
- air_temp: 空调温度调节
- car_window: 车窗升降控制
- dms_control: 驾驶员状态检测系统
- poslgt_control: 位置灯控制
- hbeam_control: 远光灯控制
- lbeam_control: 近光灯控制

**veh_operation 可选值：**
- open: 打开/启动功能
- close: 关闭/停止功能  
- up: 调大/调高/升起（仅适用于air_volume、air_temp、car_window）
- down: 调小/调低/降下（仅适用于air_volume、air_temp、car_window）

### 多场景示例
Q：把空调打开
A：{"u_message":"嗖——空调已经启动啦！凉风正往你这边吹呢，感觉如何？","veh_object":"air_switch","veh_operation":"open"}

Q：空调开小点
A：{"u_message":"好的好的，空调已经调小啦！现在风力刚刚好，不会吹得你东倒西歪～","veh_object":"air_volume","veh_operation":"down"}

Q：温度调高点
A：{"u_message":"好的好的，空调温度已经调高，现在应该更舒服了，是不是暖洋洋的？","veh_object":"air_temp","veh_operation":"up"}

Q：把风量调大
A：{"u_message":"马上为您调大空调风量！呼呼呼～现在凉爽多了吧？","veh_object":"air_volume","veh_operation":"up"}

请严格按照JSON格式输出，不包含任何其他内容。""",
            
            "strict": """你是车载语音助手，只负责车辆控制功能。

任务：用户说话 → 输出JSON

JSON格式：{"u_message":"回复","veh_object":"功能","veh_operation":"操作"}

功能列表（只能选这些）：
air_switch, air_volume, air_temp, car_window, dms_control, poslgt_control, hbeam_control, lbeam_control

操作列表（只能选这些）：
open, close, up, down

规则：
1. 只输出JSON，不输出其他
2. 必须选择合适的功能和操作
3. 回复要友好简短

示例：
用户："把车窗关上" → {"u_message":"车窗已关闭","veh_object":"car_window","veh_operation":"close"}
用户："打开空调" → {"u_message":"空调已启动","veh_object":"air_switch","veh_operation":"open"}
用户："空调开大点" → {"u_message":"风量已调大","veh_object":"air_volume","veh_operation":"up"}"""
        }
    
    def validate_json_output(self, output: str) -> TestResult:
        """验证JSON输出格式"""
        result = TestResult(
            input_text="",
            raw_output=output.strip()
        )
        
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', output.strip())
        if not json_match:
            result.errors.append("未找到JSON格式")
            return result
        
        json_str = json_match.group()
        
        # 验证JSON格式
        try:
            parsed = json.loads(json_str)
            result.parsed_json = parsed
            result.is_valid_json = True
        except json.JSONDecodeError as e:
            result.errors.append(f"JSON解析错误: {e}")
            return result
        
        # 验证字段完整性
        required_fields = ["u_message", "veh_object", "veh_operation"]
        missing_fields = [field for field in required_fields if field not in parsed]
        
        if missing_fields:
            result.errors.append(f"缺少字段: {missing_fields}")
        else:
            result.has_all_fields = True
        
        return result
    
    def check_mapping_accuracy(self, result: TestResult, expected_obj: str, expected_op: str) -> bool:
        """检查映射准确性"""
        if result.parsed_json is None:
            return False
        
        parsed_json = result.parsed_json
        actual_obj = parsed_json.get("veh_object")
        actual_op = parsed_json.get("veh_operation")
        
        if actual_obj == expected_obj and actual_op == expected_op:
            result.correct_mapping = True
            return True
        
        result.errors.append(f"映射错误: 期望({expected_obj}, {expected_op}), 实际({actual_obj}, {actual_op})")
        return False
    
    def evaluate_u_message_quality(self, u_message: str) -> int:
        """评估u_message质量 (1-5分)"""
        if not u_message:
            return 1
        
        score = 3  # 基础分
        
        # 长度合适 (20-50字)
        if 20 <= len(u_message) <= 50:
            score += 1
        
        # 包含拟声词或活泼表达
        if any(word in u_message for word in ["嗖", "咔嚓", "呼", "哈", "嘿", "好的好的", "～", "！"]):
            score += 1
        
        # 包含互动性语言
        if any(word in u_message for word in ["感觉", "是不是", "怎么样", "如何", "吧", "呢"]):
            score += 1
        
        # 过长扣分
        if len(u_message) > 60:
            score -= 1
        
        return max(1, min(5, score))
    
    def simulate_model_response(self, prompt: str, user_input: str) -> str:
        """模拟模型响应（实际使用时替换为真实模型调用）"""
        # 这里应该是真实的模型调用
        # 为了演示，我们返回一个模拟的响应
        
        # 简单的规则匹配模拟
        if "空调" in user_input and "打开" in user_input:
            return '{"u_message":"空调已启动，凉风正往你这边吹呢～","veh_object":"air_switch","veh_operation":"open"}'
        elif "空调" in user_input and ("大" in user_input or "开大" in user_input):
            return '{"u_message":"风量已调大，现在更凉爽了！","veh_object":"air_volume","veh_operation":"up"}'
        elif "车窗" in user_input and "关" in user_input:
            return '{"u_message":"车窗已关闭，车内更安静了！","veh_object":"car_window","veh_operation":"close"}'
        else:
            return '{"u_message":"指令已执行","veh_object":"air_switch","veh_operation":"open"}'
    
    def run_test(self, prompt_name: str, model_type: ModelType = ModelType.MEDIUM) -> Dict:
        """运行测试"""
        if prompt_name not in self.prompts:
            raise ValueError(f"未找到prompt: {prompt_name}")
        
        prompt = self.prompts[prompt_name]
        results = []
        
        print(f"\n=== 测试开始: {prompt_name} ({model_type.value}) ===")
        
        for i, test_case in enumerate(self.test_cases):
            print(f"\n[{i+1}/{len(self.test_cases)}] 测试: {test_case.description}")
            print(f"输入: {test_case.input_text}")
            
            # 模拟模型调用
            raw_output = self.simulate_model_response(prompt, test_case.input_text)
            print(f"输出: {raw_output}")
            
            # 验证输出
            result = self.validate_json_output(raw_output)
            result.input_text = test_case.input_text
            
            # 检查映射准确性
            if result.has_all_fields:
                self.check_mapping_accuracy(result, test_case.expected_veh_object, test_case.expected_veh_operation)
                
                # 评估u_message质量
                u_msg = result.parsed_json.get("u_message", "")
                result.u_message_quality = self.evaluate_u_message_quality(u_msg)
            
            results.append(result)
            
            # 显示结果
            status = "✅" if result.correct_mapping else "❌"
            print(f"结果: {status} {'正确' if result.correct_mapping else '错误'}")
            if result.errors:
                print(f"错误: {', '.join(result.errors)}")
        
        # 生成总结报告
        return self._generate_report(prompt_name, results)
    
    def _generate_report(self, prompt_name: str, results: List[TestResult]) -> Dict:
        """生成测试报告"""
        total_tests = len(results)
        valid_json_count = sum(1 for r in results if r.is_valid_json)
        complete_fields_count = sum(1 for r in results if r.has_all_fields)
        correct_mapping_count = sum(1 for r in results if r.correct_mapping)
        
        avg_quality = sum(r.u_message_quality for r in results) / total_tests if total_tests > 0 else 0
        
        report = {
            "prompt_name": prompt_name,
            "total_tests": total_tests,
            "json_format_rate": valid_json_count / total_tests * 100,
            "field_completeness_rate": complete_fields_count / total_tests * 100,
            "mapping_accuracy_rate": correct_mapping_count / total_tests * 100,
            "avg_u_message_quality": round(avg_quality, 2),
            "details": results
        }
        
        print(f"\n=== 测试报告: {prompt_name} ===")
        print(f"总测试数: {total_tests}")
        print(f"JSON格式正确率: {report['json_format_rate']:.1f}%")
        print(f"字段完整性: {report['field_completeness_rate']:.1f}%")
        print(f"映射准确率: {report['mapping_accuracy_rate']:.1f}%")
        print(f"平均u_message质量: {report['avg_u_message_quality']:.1f}/5.0")
        
        return report
    
    def compare_prompts(self, prompt_names: List[str]) -> Dict:
        """比较不同prompt的效果"""
        print("=== Prompt 对比测试 ===")
        
        reports = {}
        for prompt_name in prompt_names:
            if prompt_name in self.prompts:
                reports[prompt_name] = self.run_test(prompt_name)
        
        # 生成对比报告
        print("\n=== 对比总结 ===")
        print(f"{'Prompt':<15} {'JSON率':<8} {'完整性':<8} {'准确率':<8} {'质量':<8}")
        print("-" * 60)
        
        for name, report in reports.items():
            print(f"{name:<15} {report['json_format_rate']:<7.1f}% {report['field_completeness_rate']:<7.1f}% {report['mapping_accuracy_rate']:<7.1f}% {report['avg_u_message_quality']:<7.1f}")
        
        return reports

def main():
    """主函数"""
    tester = PromptTester()
    
    # 运行单个测试
    print("运行基础版本测试...")
    tester.run_test("basic")
    
    # 运行对比测试
    print("\n" + "="*60)
    print("运行对比测试...")
    tester.compare_prompts(["basic", "enhanced", "strict"])

if __name__ == "__main__":
    main() 