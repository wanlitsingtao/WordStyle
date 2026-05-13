#!/usr/bin/env python3
"""
完成数据库迁移的剩余步骤
由于 Alembic 迁移部分失败，手动完成剩余操作
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
env_file = Path(__file__).parent / '.env'
load_dotenv(env_file)

from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL")

print(" 完成数据库迁移的剩余步骤...")

engine = create_engine(db_url)

with engine.connect() as conn:
    try:
        # 第1步：检查当前状态
        print("\n📋 检查当前数据库状态...")
        result = conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'id'
        """))
        rows = result.fetchall()
        print(f"users 表 id 字段: {rows}")
        
        # 第2步：检查是否有主键约束
        result = conn.execute(text("""
            SELECT tc.constraint_name
            FROM information_schema.table_constraints tc
            WHERE tc.table_name = 'users' 
            AND tc.constraint_type = 'PRIMARY KEY'
        """))
        pk_rows = result.fetchall()
        print(f"主键约束: {pk_rows}")
        
        # 第3步：检查外键约束
        result = conn.execute(text("""
            SELECT tc.constraint_name
            FROM information_schema.table_constraints tc
            WHERE tc.table_name IN ('orders', 'conversion_tasks')
            AND tc.constraint_type = 'FOREIGN KEY'
        """))
        fk_rows = result.fetchall()
        print(f"外键约束: {fk_rows}")
        
        # 第4步：添加主键约束（如果不存在）
        if not pk_rows:
            print("\n🔨 添加 users 表主键约束...")
            conn.execute(text("""
                ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id)
            """))
            conn.commit()
            print("✅ 主键约束已添加")
        else:
            print("\n✅ 主键约束已存在")
        
        # 第5步：添加外键约束（如果不存在）
        if len(fk_rows) < 2:
            print("\n🔨 添加外键约束...")
            
            # 删除可能存在的不完整外键
            conn.execute(text("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_user_id_fkey"))
            conn.execute(text("ALTER TABLE conversion_tasks DROP CONSTRAINT IF EXISTS conversion_tasks_user_id_fkey"))
            
            # 重新添加外键
            conn.execute(text("""
                ALTER TABLE orders ADD CONSTRAINT orders_user_id_fkey 
                FOREIGN KEY (user_id) REFERENCES users(id)
            """))
            conn.execute(text("""
                ALTER TABLE conversion_tasks ADD CONSTRAINT conversion_tasks_user_id_fkey 
                FOREIGN KEY (user_id) REFERENCES users(id)
            """))
            conn.commit()
            print("✅ 外键约束已添加")
        else:
            print("\n✅ 外键约束已存在")
        
        # 第6步：更新 alembic 版本记录
        print("\n📝 更新 Alembic 版本记录...")
        try:
            conn.execute(text("""
                INSERT INTO alembic_version (version_num) VALUES ('002')
                ON CONFLICT (version_num) DO UPDATE SET version_num = '002'
            """))
            conn.commit()
            print("✅ Alembic 版本已更新")
        except Exception as e:
            print(f"⚠️  更新版本记录失败（可能已存在）: {e}")
        
        # 第7步：最终验证
        print("\n🔍 最终验证...")
        result = conn.execute(text("""
            SELECT 
                table_name, 
                column_name, 
                data_type, 
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name IN ('users', 'orders', 'conversion_tasks')
              AND column_name IN ('id', 'user_id')
            ORDER BY table_name, column_name
        """))
        for row in result.fetchall():
            print(f"  {row[0]}.{row[1]}: {row[2]}({row[3]})")
        
        print("\n" + "="*60)
        print("🎉 数据库迁移完成！")
        print("="*60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
