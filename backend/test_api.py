# -*- coding: utf-8 -*-
"""
API 测试脚本 - 测试后端 API 功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("\n1️⃣  测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    assert response.status_code == 200
    print("   ✅ 通过")

def test_register():
    """测试用户注册"""
    print("\n2️⃣  测试用户注册...")
    user_data = {
        "email": "test@example.com",
        "password": "test123456",
        "username": "测试用户"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 201:
        print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("   ✅ 通过")
        return response.json()
    elif response.status_code == 400:
        print(f"   ⚠️  用户已存在，跳过注册")
        return None
    else:
        print(f"   ❌ 失败: {response.json()}")
        return None

def test_login(email, password):
    """测试用户登录"""
    print("\n3️⃣  测试用户登录...")
    login_data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Token: {data['access_token'][:50]}...")
        print(f"   用户: {data['user']['email']}")
        print("   ✅ 通过")
        return data['access_token']
    else:
        print(f"   ❌ 失败: {response.json()}")
        return None

def test_get_profile(token):
    """测试获取用户信息"""
    print("\n4️⃣  测试获取用户信息...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("   ✅ 通过")
        return response.json()
    else:
        print(f"   ❌ 失败: {response.json()}")
        return None

def test_create_order(token):
    """测试创建订单"""
    print("\n5️⃣  测试创建充值订单...")
    headers = {"Authorization": f"Bearer {token}"}
    order_data = {
        "amount": 9.9,
        "package_label": "基础版"
    }
    response = requests.post(f"{BASE_URL}/api/payments/create-order", headers=headers, json=order_data)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   订单号: {data['order_no']}")
        print(f"   金额: ¥{data['amount']}")
        print(f"   段落数: {data['paragraphs']}")
        print("   ✅ 通过")
        return data
    else:
        print(f"   ❌ 失败: {response.json()}")
        return None

def main():
    print("=" * 60)
    print("  WordStyle Pro Backend - API 测试")
    print("=" * 60)
    
    try:
        # 1. 健康检查
        test_health()
        
        # 2. 用户注册
        register_result = test_register()
        
        # 3. 用户登录
        token = test_login("test@example.com", "test123456")
        if not token:
            print("\n❌ 登录失败，无法继续测试")
            return
        
        # 4. 获取用户信息
        user_info = test_get_profile(token)
        
        # 5. 创建订单
        order = test_create_order(token)
        
        print("\n" + "=" * 60)
        print("  ✅ 所有测试通过！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("   请确保后端服务正在运行: python run_dev.py")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
