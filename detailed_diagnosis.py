# -*- coding: utf-8 -*-
"""
详细诊断 - 测试所有API端点并捕获详细错误
"""
import requests
import json

BACKEND_URL = "https://wordstyle-backend.onrender.com"

print("="*70)
print("WordStyle 后端 API 详细诊断")
print("="*70)

endpoints_to_test = [
    ("GET", "/health", None, "健康检查"),
    ("GET", "/api/admin/users?limit=1", None, "获取用户列表"),
    ("GET", "/docs", None, "API文档"),
]

for method, path, data, description in endpoints_to_test:
    print(f"\n{'='*70}")
    print(f"测试: {description}")
    print(f"请求: {method} {BACKEND_URL}{path}")
    print(f"{'='*70}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{path}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{BACKEND_URL}{path}", json=data, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"响应时间: {response.elapsed.total_seconds():.2f}秒")
        
        if response.status_code == 200:
            print(f"✅ 成功")
            if 'application/json' in response.headers.get('content-type', ''):
                try:
                    data = response.json()
                    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                except:
                    print(f"响应内容: {response.text[:500]}")
            else:
                print(f"响应内容: {response.text[:500]}")
                
        elif response.status_code == 500:
            print(f"❌ 服务器内部错误 (500)")
            print(f"响应内容: {response.text}")
            print(f"\n⚠️ 重要提示:")
            print(f"   这通常意味着:")
            print(f"   1. Render还在重新部署中（请等待2-5分钟）")
            print(f"   2. 数据库连接失败（检查DATABASE_URL是否正确）")
            print(f"   3. 代码启动时出错（需要查看Render Logs）")
            
        else:
            print(f"⚠️ 其他状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（超过10秒）")
        print(f"   可能原因: Render服务未启动或网络问题")
        
    except Exception as e:
        print(f"❌ 请求异常: {type(e).__name__}: {e}")

print(f"\n{'='*70}")
print("诊断完成")
print(f"{'='*70}")
print(f"\n📋 下一步建议:")
print(f"1. 登录 Render 控制台: https://dashboard.render.com")
print(f"2. 查看应用状态是否为 'Live'（绿色）")
print(f"3. 点击 'Logs' 标签页，查看最近的错误日志")
print(f"4. 寻找包含以下关键词的错误:")
print(f"   - DatabaseError")
print(f"   - OperationalError") 
print(f"   - connection refused")
print(f"   - authentication failed")
print(f"   - ImportError")
print(f"5. 将完整的错误日志提供给我进行进一步分析")
