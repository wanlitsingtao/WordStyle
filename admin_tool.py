# -*- coding: utf-8 -*-
"""
管理员工具 - 用户管理
用于手动管理用户余额和查看系统状态
"""
import json
from pathlib import Path
from datetime import datetime

DATA_FILE = "user_data.json"

def load_all_users():
    """加载所有用户数据"""
    data_file = Path(DATA_FILE)
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_all_users(all_data):
    """保存所有用户数据"""
    data_file = Path(DATA_FILE)
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

def list_users():
    """列出所有用户"""
    all_data = load_all_users()
    
    if not all_data:
        print("暂无用户数据")
        return
    
    print("\n" + "="*80)
    print("用户列表")
    print("="*80)
    print(f"{'用户ID':<15} {'余额(元)':<12} {'剩余段落':<12} {'转换文档':<10} {'最后充值时间'}")
    print("-"*80)
    
    for user_id, data in all_data.items():
        balance = data.get('balance', 0.0)
        paragraphs = data.get('paragraphs_remaining', 0)
        converted = data.get('total_converted', 0)
        
        # 获取最后充值时间
        recharge_history = data.get('recharge_history', [])
        last_recharge = "无"
        if recharge_history:
            last_recharge = recharge_history[-1].get('time', '未知')
        
        print(f"{user_id:<15} {balance:<12.2f} {paragraphs:<12,} {converted:<10} {last_recharge}")
    
    print("="*80)
    print(f"总用户数: {len(all_data)}")
    print()

def add_balance(user_id, amount, paragraphs=None):
    """为用户添加余额"""
    all_data = load_all_users()
    
    if user_id not in all_data:
        print(f"❌ 用户 {user_id} 不存在")
        return False
    
    # 计算段落数（如果未指定）
    if paragraphs is None:
        paragraphs = int(amount / 0.001)  # 每个段落0.001元
    
    # 更新余额
    all_data[user_id]['balance'] += amount
    all_data[user_id]['paragraphs_remaining'] += paragraphs
    
    # 记录充值历史
    recharge_record = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'amount': amount,
        'paragraphs': paragraphs,
        'package': '管理员手动充值',
        'operator': 'admin'
    }
    all_data[user_id]['recharge_history'].append(recharge_record)
    
    save_all_users(all_data)
    
    print(f"✅ 成功为用户 {user_id} 添加:")
    print(f"   余额: ¥{amount:.2f}")
    print(f"   段落: {paragraphs:,}")
    print(f"   当前总余额: ¥{all_data[user_id]['balance']:.2f}")
    print(f"   当前总段落: {all_data[user_id]['paragraphs_remaining']:,}")
    
    return True

def reset_user(user_id):
    """重置用户数据"""
    all_data = load_all_users()
    
    if user_id not in all_data:
        print(f"❌ 用户 {user_id} 不存在")
        return False
    
    confirm = input(f"⚠️ 确认要重置用户 {user_id} 的所有数据吗？(yes/no): ")
    if confirm.lower() != 'yes':
        print("已取消")
        return False
    
    all_data[user_id] = {
        'balance': 0.0,
        'paragraphs_remaining': 0,
        'total_converted': 0,
        'total_paragraphs_used': 0,
        'recharge_history': [],
        'conversion_history': []
    }
    
    save_all_users(all_data)
    print(f"✅ 用户 {user_id} 的数据已重置")
    return True

def show_user_detail(user_id):
    """显示用户详细信息"""
    all_data = load_all_users()
    
    if user_id not in all_data:
        print(f"❌ 用户 {user_id} 不存在")
        return
    
    data = all_data[user_id]
    
    print("\n" + "="*80)
    print(f"用户详情: {user_id}")
    print("="*80)
    print(f"余额: ¥{data.get('balance', 0.0):.2f}")
    print(f"剩余段落: {data.get('paragraphs_remaining', 0):,}")
    print(f"累计转换文档: {data.get('total_converted', 0)}")
    print(f"累计使用段落: {data.get('total_paragraphs_used', 0):,}")
    
    # 显示充值历史
    recharge_history = data.get('recharge_history', [])
    print(f"\n充值历史 ({len(recharge_history)} 次):")
    print("-"*80)
    for record in recharge_history[-5:]:  # 显示最近5次
        print(f"  {record['time']} - ¥{record['amount']:.2f} ({record['paragraphs']:,}段落) - {record.get('package', '未知')}")
    
    # 显示转换历史
    conversion_history = data.get('conversion_history', [])
    print(f"\n转换历史 (最近 {min(5, len(conversion_history))} 次):")
    print("-"*80)
    for record in conversion_history[-5:]:
        print(f"  {record['time']} - {record['files']}文件, {record['success']}成功, "
              f"{record.get('paragraphs_charged', 0):,}段落, ¥{record.get('cost', 0):.2f}")
    
    print("="*80)
    print()

def main():
    """主菜单"""
    while True:
        print("\n" + "="*80)
        print("管理员工具 - 用户管理")
        print("="*80)
        print("1. 查看所有用户")
        print("2. 查看用户详情")
        print("3. 为用户充值")
        print("4. 重置用户数据")
        print("5. 退出")
        print("="*80)
        
        choice = input("\n请选择操作 (1-5): ").strip()
        
        if choice == '1':
            list_users()
        
        elif choice == '2':
            user_id = input("请输入用户ID: ").strip()
            show_user_detail(user_id)
        
        elif choice == '3':
            user_id = input("请输入用户ID: ").strip()
            try:
                amount = float(input("请输入充值金额 (元): ").strip())
                paragraphs = input("请输入段落数 (直接回车自动计算): ").strip()
                paragraphs = int(paragraphs) if paragraphs else None
                
                add_balance(user_id, amount, paragraphs)
            except ValueError as e:
                print(f"❌ 输入错误: {e}")
        
        elif choice == '4':
            user_id = input("请输入用户ID: ").strip()
            reset_user(user_id)
        
        elif choice == '5':
            print("再见！")
            break
        
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
