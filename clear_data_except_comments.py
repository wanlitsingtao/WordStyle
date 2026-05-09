"""
清空数据库中除了评论数据外的其他数据
保留：comments_data.json
清空：user_data.json, conversion_tasks.db
"""

import json
from pathlib import Path
import sqlite3

def clear_user_data():
    """清空用户数据，保留结构"""
    user_file = Path("user_data.json")
    
    if user_file.exists():
        # 清空为空的JSON对象
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print(f"✅ 已清空用户数据文件: {user_file}")
    else:
        print(f"⚠️  用户数据文件不存在: {user_file}")

def clear_conversion_tasks():
    """清空转换任务数据库"""
    db_file = Path("conversion_tasks.db")
    
    if db_file.exists():
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # 清空每个表
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DELETE FROM {table_name};")
                print(f"  - 已清空表: {table_name}")
            
            conn.commit()
            conn.close()
            print(f"✅ 已清空转换任务数据库: {db_file}")
        except Exception as e:
            print(f"❌ 清空数据库失败: {e}")
    else:
        print(f"⚠️  转换任务数据库不存在: {db_file}")

def verify_comments_preserved():
    """验证评论数据是否保留"""
    comments_file = Path("comments_data.json")
    
    if comments_file.exists():
        with open(comments_file, 'r', encoding='utf-8') as f:
            try:
                comments = json.load(f)
                print(f"✅ 评论数据已保留，共 {len(comments)} 条评论")
            except:
                print(f"⚠️  评论数据文件格式错误")
    else:
        print(f"ℹ️  评论数据文件不存在（这是正常的，如果没有评论的话）")

def main():
    print("=" * 60)
    print("🗑️  开始清空数据（保留评论数据）")
    print("=" * 60)
    print()
    
    # 1. 清空用户数据
    print("📋 步骤 1: 清空用户数据...")
    clear_user_data()
    print()
    
    # 2. 清空转换任务数据库
    print("📋 步骤 2: 清空转换任务数据库...")
    clear_conversion_tasks()
    print()
    
    # 3. 验证评论数据
    print("📋 步骤 3: 验证评论数据...")
    verify_comments_preserved()
    print()
    
    print("=" * 60)
    print("✅ 数据清空完成！")
    print("=" * 60)
    print()
    print("📊 清空内容：")
    print("  - 用户数据（余额、段落数、转换记录等）")
    print("  - 转换任务历史记录")
    print()
    print("📊 保留内容：")
    print("  - 评论数据（comments_data.json）")
    print()
    print("💡 提示：刷新网页后，所有用户将重新获得免费额度")

if __name__ == "__main__":
    main()
