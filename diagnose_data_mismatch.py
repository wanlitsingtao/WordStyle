#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断用户数据不一致问题
"""
import json
from pathlib import Path

print("=" * 60)
print("🔍 诊断用户数据不一致问题")
print("=" * 60)
print()

# 读取数据库
data_file = Path("user_data.json")
with open(data_file, 'r', encoding='utf-8') as f:
    db_data = json.load(f)

user_id = '7801ac509e2e'
db_user = db_data.get(user_id, {})

print("📊 数据库中的数据:")
print(f"  剩余段落: {db_user.get('paragraphs_remaining', 0)}")
print(f"  累计转换: {db_user.get('total_converted', 0)}")
print(f"  最后领取日期: {db_user.get('last_free_quota_date', '')}")
print(f"  转换历史条数: {len(db_user.get('conversion_history', []))}")
print()

print("⚠️  您报告的前端显示数据:")
print(f"  剩余段落: 493")
print(f"  累计转换: 8")
print()

# 计算差异
db_paragraphs = db_user.get('paragraphs_remaining', 0)
db_conversions = db_user.get('total_converted', 0)

front_paragraphs = 493
front_conversions = 8

print("📈 差异分析:")
print(f"  段落数差异: {db_paragraphs} (数据库) vs {front_paragraphs} (前端)")
print(f"  转换次数差异: {db_conversions} (数据库) vs {front_conversions} (前端)")
print()

if db_paragraphs != front_paragraphs or db_conversions != front_conversions:
    print("❌ 数据不一致！")
    print()
    print("可能的原因:")
    print("  1. 前端显示的是旧缓存数据")
    print("  2. 最近的5次转换没有正确保存到数据库")
    print("  3. 使用了不同的user_id")
    print()
    print("建议操作:")
    print("  1. 刷新前端页面（Ctrl+F5 强制刷新）")
    print("  2. 检查是否有转换失败的日志")
    print("  3. 确认当前使用的user_id是否正确")
else:
    print("✅ 数据一致")

print()
print("=" * 60)
