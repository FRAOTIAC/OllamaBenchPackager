#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车载语音助手 - 抗干扰测试脚本
自动化执行各种迷惑性输入测试，验证模型的抗干扰能力
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class VehicleAssistantTester:
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "vehicle-assistant"):
        """
        初始化测试器
        
        Args:
            base_url: Ollama 服务地址
            model_name: 模型名称
        """
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/api/generate"
        self.test_results = []
        
    def test_single_input(self, test_input: str, expected_object: Optional[str] = None, expected_operation: Optional[str] = None) -> Dict[str, Any]:
        """
        测试单个输入
        
        Args:
            test_input: 测试输入文本
            expected_object: 期望的车辆对象
            expected_operation: 期望的操作
            
        Returns:
            测试结果字典
        """
        try:
            # 发送请求
            response = requests.post(
                self.api_url,
                json={
                    'model': self.model_name,
                    'prompt': test_input,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                model_response = result.get('response', '')
                
                # 尝试解析JSON
                try:
                    parsed_response = json.loads(model_response)
                    
                    # 验证字段
                    has_u_message = 'u_message' in parsed_response
                    has_veh_object = 'veh_object' in parsed_response
                    has_veh_operation = 'veh_operation' in parsed_response
                    
                    # 验证预期结果
                    object_match = True
                    operation_match = True
                    
                    if expected_object:
                        object_match = parsed_response.get('veh_object') == expected_object
                    
                    if expected_operation:
                        operation_match = parsed_response.get('veh_operation') == expected_operation
                    
                    return {
                        'status': 'success',
                        'input': test_input,
                        'output': parsed_response,
                        'has_complete_fields': has_u_message and has_veh_object and has_veh_operation,
                        'object_match': object_match,
                        'operation_match': operation_match,
                        'expected_object': expected_object,
                        'expected_operation': expected_operation,
                        'response_time': response.elapsed.total_seconds()
                    }
                    
                except json.JSONDecodeError:
                    return {
                        'status': 'json_error',
                        'input': test_input,
                        'raw_output': model_response,
                        'error': 'JSON 解析失败'
                    }
                    
            else:
                return {
                    'status': 'http_error',
                    'input': test_input,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except requests.RequestException as e:
            return {
                'status': 'network_error',
                'input': test_input,
                'error': str(e)
            }
    
    def run_interference_tests(self) -> List[Dict[str, Any]]:
        """
        运行抗干扰测试套件
        
        Returns:
            测试结果列表
        """
        test_cases = [
            {
                'name': '闲聊夹杂指令',
                'input': '今天天气真好啊，阳光明媚的，不过车里有点闷，你说我们是不是应该把车窗打开透透气？对了，你知道今天股市怎么样吗？',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '否定句干扰',
                'input': '我不想开空调，也不想关灯，但是现在车里空气不太好，还是把车窗打开吧，不过等会儿到了目的地记得关上。',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '多重条件混合',
                'input': '如果外面没有下雨的话，而且风不是很大，温度也合适，那么我们就把车窗打开一点点，让新鲜空气进来，但是如果有灰尘就算了。',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '时间延迟指令',
                'input': '等会儿到了红绿灯的时候，记得提醒我给老婆打个电话，还有就是趁这个时候把车窗打开通通风，因为刚才有人在车里抽烟。',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '反向逻辑',
                'input': '车窗关着的时候总觉得憋得慌，特别是夏天，所以我觉得不应该一直关着，你觉得呢？帮我把车窗打开好吗？',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '包含其他车辆功能',
                'input': '现在车里温度还可以，空调也不用开，灯光也够亮，就是觉得有点闷，把车窗打开让空气流通一下，音响声音也不用调。',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '情景描述',
                'input': '刚才路过一个工地，车里进了好多灰尘，现在想开车窗吹吹风，但是又怕外面的空气质量不好，算了还是开一下吧，把车窗打开。',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '询问式干扰',
                'input': '你觉得现在这个天气适合开车窗吗？我觉得挺合适的，空气也不错，要不我们把车窗打开？你觉得呢？还是说开空调比较好？',
                'expected_object': 'car_window',
                'expected_operation': 'open'
            },
            {
                'name': '空调相关迷惑性输入',
                'input': '外面太阳好大，车里感觉像蒸笼一样，我觉得不开空调肯定不行，你说对吧？赶紧把空调打开吧，不然要热死了。',
                'expected_object': 'air_switch',
                'expected_operation': 'open'
            },
            {
                'name': '灯光相关迷惑性输入',
                'input': '天色有点暗了，路上车也多，安全起见我觉得应该开灯，不过是开近光灯还是远光灯呢？算了，先开近光灯吧，毕竟市区里不能开远光。',
                'expected_object': 'lbeam_control',
                'expected_operation': 'open'
            }
        ]
        
        results = []
        
        print("🚗 开始车载语音助手抗干扰测试...")
        print("=" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试用例 {i}: {test_case['name']}")
            print(f"输入: {test_case['input']}")
            
            # 执行测试
            result = self.test_single_input(
                test_case['input'],
                test_case.get('expected_object'),
                test_case.get('expected_operation')
            )
            
            result['test_name'] = test_case['name']
            result['test_number'] = i
            results.append(result)
            
            # 显示结果
            if result['status'] == 'success':
                print(f"✅ 状态: 成功")
                print(f"🤖 助手回复: {result['output'].get('u_message', 'N/A')}")
                print(f"🔧 车辆对象: {result['output'].get('veh_object', 'N/A')}")
                print(f"⚙️ 操作指令: {result['output'].get('veh_operation', 'N/A')}")
                print(f"⏱️ 响应时间: {result['response_time']:.2f}s")
                
                # 验证结果
                if result['has_complete_fields']:
                    print("✅ JSON 格式完整")
                else:
                    print("❌ JSON 格式不完整")
                    
                if result['object_match']:
                    print("✅ 车辆对象匹配")
                else:
                    print(f"❌ 车辆对象不匹配 (期望: {result['expected_object']}, 实际: {result['output'].get('veh_object')})")
                    
                if result['operation_match']:
                    print("✅ 操作指令匹配")
                else:
                    print(f"❌ 操作指令不匹配 (期望: {result['expected_operation']}, 实际: {result['output'].get('veh_operation')})")
                    
            else:
                print(f"❌ 状态: 失败 - {result['error']}")
                if 'raw_output' in result:
                    print(f"原始输出: {result['raw_output']}")
            
            print("-" * 60)
            
            # 避免请求过快
            time.sleep(0.5)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        生成测试报告
        
        Args:
            results: 测试结果列表
            
        Returns:
            测试报告字符串
        """
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['status'] == 'success')
        complete_json_tests = sum(1 for r in results if r.get('has_complete_fields', False))
        object_match_tests = sum(1 for r in results if r.get('object_match', False))
        operation_match_tests = sum(1 for r in results if r.get('operation_match', False))
        
        report = f"""
🚗 车载语音助手抗干扰测试报告
{'=' * 50}

📊 总体统计:
- 测试总数: {total_tests}
- 成功测试: {successful_tests} ({successful_tests/total_tests*100:.1f}%)
- JSON格式完整: {complete_json_tests} ({complete_json_tests/total_tests*100:.1f}%)
- 车辆对象匹配: {object_match_tests} ({object_match_tests/total_tests*100:.1f}%)
- 操作指令匹配: {operation_match_tests} ({operation_match_tests/total_tests*100:.1f}%)

🔍 详细结果:
"""
        
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            report += f"\n{status_icon} {result['test_name']}: {result['status']}"
            
            if result['status'] == 'success':
                accuracy_score = sum([
                    result.get('has_complete_fields', False),
                    result.get('object_match', False),
                    result.get('operation_match', False)
                ]) / 3 * 100
                report += f" (准确率: {accuracy_score:.1f}%)"
        
        report += f"\n\n📈 测试结论:\n"
        
        if successful_tests == total_tests:
            report += "🎉 所有测试通过！模型抗干扰能力表现优秀。"
        elif successful_tests >= total_tests * 0.8:
            report += "👍 大部分测试通过，模型抗干扰能力良好，可考虑优化失败的测试用例。"
        elif successful_tests >= total_tests * 0.5:
            report += "⚠️ 部分测试通过，模型抗干扰能力一般，建议调整提示词或增加训练示例。"
        else:
            report += "❌ 大部分测试失败，模型抗干扰能力需要改进，建议重新设计提示词。"
        
        report += f"\n\n📝 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        report += f"\n🔧 测试模型: {self.model_name}"
        report += f"\n🌐 服务地址: {self.base_url}"
        
        return report
    
    def save_results(self, results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        保存测试结果到文件
        
        Args:
            results: 测试结果列表
            filename: 保存文件名
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"车载助手_抗干扰测试结果_{timestamp}.json"
        
        test_data = {
            'test_info': {
                'model': self.model_name,
                'base_url': self.base_url,
                'test_time': datetime.now().isoformat(),
                'total_tests': len(results)
            },
            'results': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        return filename


def main():
    """主函数"""
    print("🚗 车载语音助手抗干扰测试工具")
    print("=" * 50)
    
    # 用户输入配置
    base_url = input("请输入 Ollama 服务地址 (默认: http://localhost:11434): ").strip()
    if not base_url:
        base_url = "http://localhost:11434"
    
    model_name = input("请输入模型名称 (默认: vehicle-assistant): ").strip()
    if not model_name:
        model_name = "vehicle-assistant"
    
    # 创建测试器
    tester = VehicleAssistantTester(base_url, model_name)
    
    # 运行测试
    try:
        results = tester.run_interference_tests()
        
        # 生成报告
        report = tester.generate_report(results)
        print("\n" + report)
        
        # 保存结果
        filename = tester.save_results(results)
        print(f"\n💾 测试结果已保存到: {filename}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    main() 