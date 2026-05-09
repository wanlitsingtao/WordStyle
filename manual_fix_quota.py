#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动修复用户7801ac509e2e的免费额度
将今天的日期设置为最后领取日期，并重置段落数为10000
"""
import json
from datetime import datetime

user_id = '7801ac509e2e'
today = datetime.now().strftime('%Y-%m-%d')

print(f"=== 手动修复用户 {user_id} 的免费额度 ===\n")
print(f"今日日期: {today}\n")

# 读取用户数据
with open('user_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

user = data.get(user_id, {})

print(f"修复前:")
print(f"  剩余段落: {user.get('paragraphs_remaining', 0)}")
print(f"  最后领取日期: {user.get('last_free_quota_date', '')}")
print(f"  累计转换: {user.get('total_converted', 0)}")
print()

# 更新数据
user['paragraphs_remaining'] = 10000
user['last_free_quota_date'] = today

# 添加领取记录
if 'free_quota_history' not in user:
    user['free_quota_history'] = []

user['free_quota_history'].append({
    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'amount': 10000,
    'type': 'daily_free_quota',
    'date': today
})

data[user_id] = user

# 保存数据
with open('user_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"修复后:")
print(f"  剩余段落: {user.get('paragraphs_remaining', 0)}")
print(f"  最后领取日期: {user.get('last_free_quota_date', '')}")
print(f"  累计转换: {user.get('total_converted', 0)}")
print()
print("✅ 修复完成！")
