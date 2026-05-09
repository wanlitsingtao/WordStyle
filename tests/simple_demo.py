# -*- coding: utf-8 -*-
"""
简化版Demo测试 - 避免编码问题
"""
import requests
import time


def test_api():
    """测试API健康检查"""
    print("\n[测试1] API健康检查")
    print("-" * 50)
    
    try:
        start = time.time()
        response = requests.get("http://localhost:8000/health", timeout=5)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] 状态码: {response.status_code}")
            print(f"[PASS] 响应: {data}")
            print(f"[PASS] 响应时间: {elapsed:.0f}ms")
            return True
        else:
            print(f"[FAIL] HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_monitoring():
    """测试监控端点"""
    print("\n[测试2] 监控指标")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:8000/monitoring/metrics/summary", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] 获取成功")
            for key, value in data.items():
                print(f"  {key}: {value}")
            return True
        else:
            print(f"[FAIL] HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def main():
    print("="*50)
    print("  WordStyle 自动化测试 Demo")
    print("="*50)
    
    results = []
    results.append(test_api())
    results.append(test_monitoring())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"结果: {passed}/{total} 通过")
    print("="*50)


if __name__ == "__main__":
    main()
