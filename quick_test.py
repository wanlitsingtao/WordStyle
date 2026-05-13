# -*- coding: utf-8 -*-
"""
快速测试 - 只测试一个API端点
"""
import requests
import time

BACKEND_URL = "https://wordstyle-backend.onrender.com"

print("测试Render后端API连接...")
print(f"目标: {BACKEND_URL}\n")

# 测试获取用户列表
print("正在请求: GET /api/admin/users?limit=1")
start_time = time.time()

try:
    response = requests.get(f"{BACKEND_URL}/api/admin/users?limit=1", timeout=15)
    elapsed = time.time() - start_time
    
    print(f"\n响应时间: {elapsed:.2f}秒")
    print(f"状态码: {response.status_code}")
    print(f"响应头 Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if response.status_code == 200:
        print("\n✅ API工作正常!")
        try:
            data = response.json()
            users = data.get('users', [])
            print(f"获取到 {len(users)} 个用户")
            if users:
                print(f"第一个用户: ID={users[0].get('id')}, 余额={users[0].get('balance')}")
        except Exception as e:
            print(f"JSON解析错误: {e}")
            print(f"响应内容: {response.text[:200]}")
            
    elif response.status_code == 500:
        print("\n❌ 服务器内部错误 (500)")
        print(f"响应内容: {response.text}")
        print("\n可能原因:")
        print("1. Render还在重新部署中（请等待2-5分钟）")
        print("2. 环境变量配置有误")
        print("3. 数据库连接失败")
        print("\n建议操作:")
        print("- 登录Render控制台查看应用状态和日志")
        print("- 确认环境变量已保存且应用已重新部署")
        
    else:
        print(f"\n⚠️ 其他错误: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print(f"\n❌ 请求超时（超过15秒）")
    print("可能原因: Render服务未启动或网络问题")
    
except Exception as e:
    print(f"\n❌ 请求异常: {type(e).__name__}: {e}")
