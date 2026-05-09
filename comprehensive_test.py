#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面自测脚本 - 检查系统功能和性能
"""
import json
import os
from datetime import datetime

print("=" * 60)
print("🔍 WordStyle 系统全面自测")
print("=" * 60)
print()

# 1. 检查用户数据
print("1️⃣  检查用户数据持久化...")
try:
    with open('user_data.json', 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    
    print(f"   ✅ 用户数据文件存在")
    print(f"   📊 用户总数: {len(user_data)}")
    
    for uid, data in user_data.items():
        print(f"\n   用户 {uid[:12]}...:")
        print(f"     - 剩余段落: {data.get('paragraphs_remaining', 0)}")
        print(f"     - 最后领取日期: {data.get('last_free_quota_date', '')}")
        print(f"     - 累计转换: {data.get('total_converted', 0)}")
        print(f"     - 转换历史条数: {len(data.get('conversion_history', []))}")
        
        # 检查数据一致性
        if data.get('total_converted', 0) != len(data.get('conversion_history', [])):
            print(f"     ⚠️  警告: total_converted ({data.get('total_converted', 0)}) 与历史记录条数 ({len(data.get('conversion_history', []))}) 不一致！")
        
        # 检查免费额度是否今天已领取
        today = datetime.now().strftime('%Y-%m-%d')
        last_date = data.get('last_free_quota_date', '')
        if last_date != today:
            print(f"     ⚠️  警告: 今天尚未领取免费额度（最后领取: {last_date}）")
        else:
            print(f"     ✅ 今日免费额度已领取")
            
except Exception as e:
    print(f"   ❌ 错误: {e}")

print()

# 2. 检查核心文件
print("2️⃣  检查核心文件...")
core_files = [
    'app.py',
    'doc_converter.py',
    'config.py',
    'utils.py',
    'user_manager.py',
    'comments_manager.py',
]

for file in core_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"   ✅ {file} ({size:,} bytes)")
    else:
        print(f"   ❌ {file} 不存在！")

print()

# 3. 检查代码语法
print("3️⃣  检查代码语法...")
import subprocess

python_files = ['app.py', 'doc_converter.py', 'config.py', 'utils.py', 'user_manager.py']
for file in python_files:
    try:
        result = subprocess.run(
            ['python', '-m', 'py_compile', file],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   ✅ {file} 语法正确")
        else:
            print(f"   ❌ {file} 语法错误: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  {file} 检查失败: {e}")

print()

# 4. 检查临时文件
print("4️⃣  检查临时文件...")
temp_files = [f for f in os.listdir('.') if f.startswith('temp_')]
if temp_files:
    print(f"   ⚠️  发现 {len(temp_files)} 个临时文件:")
    for f in temp_files[:5]:  # 只显示前5个
        print(f"     - {f}")
    if len(temp_files) > 5:
        print(f"     ... 还有 {len(temp_files) - 5} 个")
else:
    print(f"   ✅ 没有临时文件")

print()

# 5. 检查日志文件
print("5️⃣  检查日志文件...")
log_files = [f for f in os.listdir('.') if f.endswith('.log')]
if log_files:
    print(f"   ⚠️  发现 {len(log_files)} 个日志文件:")
    for f in log_files[:5]:
        size = os.path.getsize(f)
        print(f"     - {f} ({size:,} bytes)")
    if len(log_files) > 5:
        print(f"     ... 还有 {len(log_files) - 5} 个")
else:
    print(f"   ✅ 没有日志文件")

print()

# 6. 检查配置
print("6️⃣  检查配置...")
try:
    from config import FREE_PARAGRAPHS_DAILY, PARAGRAPH_PRICE
    print(f"   ✅ 每日免费额度: {FREE_PARAGRAPHS_DAILY}")
    print(f"   ✅ 每段落价格: ¥{PARAGRAPH_PRICE}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")

print()

# 7. 检查变量定义问题
print("7️⃣  检查常见变量定义问题...")
issues = []

# 检查 app.py 中是否有未定义的变量
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # 检查 total_files 是否在需要时已定义
    if 'total_files' in content:
        # 查找所有使用 total_files 的地方
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'total_files' in line and '=' not in line.split('total_files')[0].split('=')[-1]:
                # 这行使用了 total_files，检查前面是否已定义
                # 简单检查：看前面是否有 total_files = 
                found_definition = False
                for j in range(max(0, i-50), i):
                    if 'total_files' in lines[j] and '=' in lines[j]:
                        found_definition = True
                        break
                if not found_definition and 'def ' not in line:
                    issues.append(f"   ⚠️  第{i}行可能使用了未定义的 total_files")
    
    if not issues:
        print(f"   ✅ 未发现明显的变量定义问题")
    else:
        for issue in issues:
            print(issue)

print()

# 8. 总结
print("=" * 60)
print("📋 自测总结")
print("=" * 60)
print()
print("✅ 基本检查完成")
print()
print("💡 建议:")
print("   1. 如果发现数据不一致，请检查转换逻辑是否正确保存")
print("   2. 如果临时文件过多，请检查清理机制是否正常工作")
print("   3. 定期备份 user_data.json 文件")
print()
