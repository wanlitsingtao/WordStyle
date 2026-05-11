# -*- coding: utf-8 -*-
"""
诊断脚本：检查当前环境的数据源配置
"""
import os
import sys

print("=" * 60)
print("🔍 WordStyle 数据源配置诊断")
print("=" * 60)

# 检查环境变量
print("\n1️⃣  环境变量检查:")
print(f"   USE_SUPABASE = {os.getenv('USE_SUPABASE', '未设置')}")
print(f"   DATABASE_URL = {'已设置' if os.getenv('DATABASE_URL') else '未设置'}")

if os.getenv('DATABASE_URL'):
    db_url = os.getenv('DATABASE_URL')
    # 隐藏密码部分
    if '@' in db_url:
        parts = db_url.split('@')
        print(f"   DATABASE_URL (部分) = {parts[0].split(':')[0]}://***@{parts[1][:50]}...")

# 导入配置
sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_SOURCE, USE_SUPABASE, DATABASE_URL

print("\n2️⃣  config.py 配置:")
print(f"   USE_SUPABASE = {USE_SUPABASE}")
print(f"   DATABASE_URL = {'已设置' if DATABASE_URL else '未设置'}")
print(f"   DATA_SOURCE = {DATA_SOURCE}")

# 测试数据加载
print("\n3️⃣  数据加载测试:")
try:
    from data_manager import load_all_users_data, get_data_source
    
    actual_source = get_data_source()
    print(f"   实际数据源: {actual_source}")
    
    users = load_all_users_data()
    print(f"   加载的用户数量: {len(users)}")
    
    if len(users) > 0:
        print(f"   第一个用户: {users[0].get('user_id', 'N/A')}")
    else:
        print("   ⚠️  警告: 没有加载到任何用户数据")
        
        if actual_source == 'supabase':
            print("\n   💡 提示: 如果使用 Supabase 模式但没有数据，可能原因:")
            print("      - 数据库中确实没有用户")
            print("      - DATABASE_URL 配置错误")
            print("      - 数据库表不存在或未迁移")
        else:
            print("\n   💡 提示: 当前使用本地模式，请检查:")
            print("      - user_data.json 文件是否存在")
            print("      - 是否需要设置 USE_SUPABASE=true")
            
except Exception as e:
    print(f"   ❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
