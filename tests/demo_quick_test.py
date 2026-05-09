# -*- coding: utf-8 -*-
"""
快速测试Demo - 展示自动化测试效果
运行此脚本查看自动化测试的实际效果
"""
import requests
import time
import sys


def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_step(step_num, text):
    """打印步骤"""
    print(f"\n[步骤 {step_num}] {text}")


def print_result(success, message):
    """打印结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")


def test_health_check():
    """测试1: 健康检查"""
    print_header("测试1: API健康检查")
    
    base_url = "http://localhost:8000"
    
    try:
        print_step(1, "发送健康检查请求...")
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        elapsed = (time.time() - start_time) * 1000
        
        print_step(2, "验证响应状态码...")
        assert response.status_code == 200, f"期望200, 实际{response.status_code}"
        print_result(True, f"状态码正确: {response.status_code}")
        
        print_step(3, "验证响应内容...")
        data = response.json()
        assert data["status"] == "healthy", f"期望healthy, 实际{data.get('status')}"
        print_result(True, f"状态正常: {data['status']}")
        
        print_step(4, "测量响应时间...")
        print_result(True, f"响应时间: {elapsed:.0f}ms")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_result(False, "无法连接到后端服务，请先启动应用")
        print("\n💡 提示: 运行以下命令启动后端:")
        print("   cd backend && uvicorn app.main:app --reload")
        return False
        
    except Exception as e:
        print_result(False, str(e))
        return False


def test_monitoring_metrics():
    """测试2: 监控指标"""
    print_header("测试2: 监控指标获取")
    
    base_url = "http://localhost:8000"
    
    try:
        print_step(1, "获取监控指标摘要...")
        response = requests.get(f"{base_url}/monitoring/metrics/summary", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "成功获取监控指标")
            print(f"\n📊 指标数据:")
            for key, value in data.items():
                print(f"   {key}: {value}")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, str(e))
        return False


def test_api_documentation():
    """测试3: API文档可访问性"""
    print_header("测试3: API文档访问")
    
    base_url = "http://localhost:8000"
    
    try:
        print_step(1, "访问Swagger UI文档...")
        response = requests.get(f"{base_url}/docs", timeout=5)
        
        if response.status_code == 200:
            print_result(True, "Swagger UI文档可访问")
            print(f"   URL: {base_url}/docs")
        else:
            print_result(False, f"文档访问失败: HTTP {response.status_code}")
            
        print_step(2, "访问ReDoc文档...")
        response = requests.get(f"{base_url}/redoc", timeout=5)
        
        if response.status_code == 200:
            print_result(True, "ReDoc文档可访问")
            print(f"   URL: {base_url}/redoc")
        else:
            print_result(False, f"文档访问失败: HTTP {response.status_code}")
        
        return True
        
    except Exception as e:
        print_result(False, str(e))
        return False


def test_frontend_access():
    """测试4: 前端应用访问"""
    print_header("测试4: 前端应用访问")
    
    frontend_url = "http://localhost:8501"
    
    try:
        print_step(1, "访问Streamlit应用...")
        response = requests.get(frontend_url, timeout=5)
        
        if response.status_code == 200:
            print_result(True, "前端应用可访问")
            print(f"   URL: {frontend_url}")
            
            # 检查页面标题
            content_str = response.content.decode('utf-8', errors='ignore')
            if "标书抄写神器" in content_str or "Streamlit" in content_str:
                print_result(True, "页面内容正确")
            else:
                print_result(False, "页面内容异常")
                
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result(False, "无法连接到前端服务")
        print("\n💡 提示: 运行以下命令启动前端:")
        print("   streamlit run app.py")
        return False
        
    except Exception as e:
        print_result(False, str(e))
        return False


def main():
    """主函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "自动化测试Demo - WordStyle项目" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    print("\n本Demo将演示基础的自动化测试功能")
    print("确保您的应用已启动后再运行此脚本\n")
    
    # 非交互模式,直接开始
    print("⏳ 3秒后开始测试...")
    time.sleep(3)
    
    results = []
    
    # 执行测试
    results.append(("API健康检查", test_health_check()))
    results.append(("监控指标获取", test_monitoring_metrics()))
    results.append(("API文档访问", test_api_documentation()))
    results.append(("前端应用访问", test_frontend_access()))
    
    # 汇总结果
    print_header("测试结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-"*60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查应用状态")
    
    print("\n" + "="*60)
    print("\n💡 下一步:")
    print("   1. 安装完整测试框架: pip install -r requirements-test.txt")
    print("   2. 运行完整测试套件: pytest tests/ -v")
    print("   3. 查看测试报告: pytest tests/ --html=report.html")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(0)
