#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试vLLM Meta Llama 3.3 70B模型
"""

import requests
import json
import time

def test_vllm_model():
    """
    测试vLLM模型API
    """
    # 模型配置
    config = {
        "endpoint": "http://10.2.4.153:80/v1",
        "model": "ibnzterrell/Meta-Llama-3.3-70B-Instruct-AWQ-INT4"
    }
    
    print("🚀 开始测试vLLM Meta Llama 3.3 70B模型")
    print("=" * 60)
    print(f"📡 端点: {config['endpoint']}")
    print(f"🤖 模型: {config['model']}")
    print("=" * 60)
    
    # 测试消息
    test_messages = [
        {
            "role": "user",
            "content": "你好！请简单介绍一下你自己。"
        }
    ]
    
    # 构造请求数据
    request_data = {
        "model": config["model"],
        "messages": test_messages,
        "max_tokens": 512,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        print("📤 发送请求...")
        print(f"💬 用户消息: {test_messages[0]['content']}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 发送POST请求
        response = requests.post(
            f"{config['endpoint']}/chat/completions",
            headers={
                "Content-Type": "application/json",
            },
            json=request_data,
            timeout=60
        )
        
        # 记录响应时间
        response_time = time.time() - start_time
        
        print(f"⏱️  响应时间: {response_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # 提取模型回复
            if "choices" in result and len(result["choices"]) > 0:
                assistant_message = result["choices"][0]["message"]["content"]
                
                print("✅ 模型响应成功!")
                print("-" * 40)
                print("🤖 Llama 3.3回复:")
                print(f"📝 {assistant_message}")
                print("-" * 40)
                
                # 显示一些统计信息
                if "usage" in result:
                    usage = result["usage"]
                    print("📈 使用统计:")
                    print(f"   输入tokens: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"   输出tokens: {usage.get('completion_tokens', 'N/A')}")
                    print(f"   总计tokens: {usage.get('total_tokens', 'N/A')}")
                
                return True
            else:
                print("❌ 响应格式错误: 没有找到choices")
                return False
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        print("💡 提示: 模型可能需要更多时间加载或推理")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        print("💡 提示: 请检查网络连接和端点地址是否正确")
        return False
        
    except Exception as e:
        print(f"❌ 出现未知错误: {e}")
        return False


def test_model_info():
    """
    获取模型信息
    """
    endpoint = "http://10.2.4.153:80/v1"
    
    try:
        print("\n🔍 获取模型信息...")
        response = requests.get(f"{endpoint}/models", timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print("📋 可用模型列表:")
            if "data" in models:
                for model in models["data"]:
                    print(f"   • {model.get('id', 'Unknown')}")
            else:
                print("   (无法获取模型列表)")
        else:
            print(f"❌ 无法获取模型信息: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 获取模型信息时出错: {e}")


def test_advanced_conversation():
    """
    测试更复杂的对话
    """
    config = {
        "endpoint": "http://10.2.4.153:80/v1",
        "model": "ibnzterrell/Meta-Llama-3.3-70B-Instruct-AWQ-INT4"
    }
    
    print("\n🧠 测试高级对话能力...")
    
    # 更复杂的测试问题
    test_questions = [
        "请用Python写一个计算斐波那契数列的函数，要求使用递归实现。",
        "解释一下什么是机器学习中的过拟合，以及如何防止过拟合？",
        "如果你是一个项目经理，如何管理一个5人的开发团队？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 测试问题 {i}: {question}")
        
        request_data = {
            "model": config["model"],
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{config['endpoint']}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=request_data,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0]["message"]["content"]
                    print(f"✅ 回答 ({response_time:.2f}s):")
                    print(f"🤖 {answer[:200]}{'...' if len(answer) > 200 else ''}")
                else:
                    print("❌ 响应格式错误")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    print("🔬 vLLM Meta Llama 3.3 70B 模型测试")
    print("=" * 60)
    
    # 基础连接测试
    success = test_vllm_model()
    
    if success:
        # 获取模型信息
        test_model_info()
        
        # 高级对话测试
        test_advanced_conversation()
        
        print("\n🎉 测试完成!")
    else:
        print("\n❌ 基础测试失败，跳过后续测试")
    
    print("=" * 60) 