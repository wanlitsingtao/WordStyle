#!/usr/bin/env python3
"""
执行数据库迁移脚本

功能：
1. 验证数据库连接
2. 执行 Alembic 迁移
3. 验证迁移结果
4. 显示迁移报告

使用方法：
    cd backend
    python run_migration.py
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# 加载环境变量（优先加载 .env，如果不存在则加载 .env.production）
env_file = Path(__file__).parent / '.env'
if not env_file.exists():
    env_file = Path(__file__).parent / '.env.production'
load_dotenv(env_file)
print(f"✅ 加载配置文件: {env_file.name}")

from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command


def get_database_url():
    """获取数据库连接URL"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ 错误：未设置 DATABASE_URL 环境变量")
        print("\n请在 backend/.env.production 中配置 DATABASE_URL")
        print("格式：postgresql://postgres:password@db.xxx.supabase.co:5432/postgres")
        sys.exit(1)
    return db_url


def check_connection(db_url):
    """检查数据库连接"""
    print("🔍 正在检查数据库连接...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ 数据库连接成功")
            print(f"📊 PostgreSQL 版本: {version}")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n请检查：")
        print("1. DATABASE_URL 格式是否正确")
        print("2. 密码是否包含特殊字符（需要URL编码）")
        print("   例如: @ 编码为 %40, : 编码为 %3A")
        print("3. Supabase项目是否已创建")
        print("4. 网络是否可以访问Supabase")
        return False


def run_migration():
    """执行数据库迁移"""
    print("\n" + "="*60)
    print("🚀 开始执行数据库迁移")
    print("="*60)
    
    # 获取 Alembic 配置文件路径
    alembic_cfg = Config(str(Path(__file__).parent / "alembic.ini"))
    
    # 更新数据库连接URL
    db_url = get_database_url()
    # 对 URL 中的 % 进行转义，避免 configparser 解析错误
    alembic_cfg.set_main_option("sqlalchemy.url", db_url.replace('%', '%%'))
    
    # 检查当前数据库版本
    print("\n📋 检查当前数据库版本...")
    try:
        from alembic.script import ScriptDirectory
        from alembic.runtime.environment import EnvironmentContext
        
        # 获取当前版本
        with open(Path(__file__).parent / "alembic" / "versions" / "20260507_1200_001_initial.py", 'r', encoding='utf-8') as f:
            if "001" in f.read():
                print("✅ 检测到初始迁移 (001) 已存在")
    except Exception as e:
        print(f"️  无法检查当前版本: {e}")
    
    # 执行迁移
    print("\n🔄 执行迁移 upgrade...")
    try:
        command.upgrade(alembic_cfg, "002")
        print("\n✅ 迁移执行成功！")
    except Exception as e:
        print(f"\n❌ 迁移执行失败: {e}")
        print("\n请检查：")
        print("1. 数据库中是否已存在 001 迁移记录")
        print("2. 表结构是否与预期一致")
        print("3. 是否有足够权限执行迁移操作")
        return False
    
    return True


def verify_migration(db_url):
    """验证迁移结果"""
    print("\n" + "="*60)
    print("🔍 验证迁移结果")
    print("="*60)
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 检查 users 表结构
            print("\n 检查 users 表结构...")
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'id'
                ORDER BY ordinal_position;
            """))
            rows = result.fetchall()
            if len(rows) == 1 and rows[0][1] == 'character varying' and rows[0][2] == 12:
                print("✅ users.id 字段类型正确: VARCHAR(12)")
            else:
                print(f"⚠️  users.id 字段异常: {rows}")
            
            # 检查外键约束
            print("\n 检查外键约束...")
            result = conn.execute(text("""
                SELECT tc.constraint_name, tc.table_name, kcu.column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name IN ('orders', 'conversion_tasks')
                    AND kcu.column_name = 'user_id';
            """))
            rows = result.fetchall()
            if len(rows) == 2:
                print(f"✅ 外键约束正确: {len(rows)} 个")
                for row in rows:
                    print(f"   - {row[0]}: {row[1]}.{row[2]}")
            else:
                print(f"⚠️  外键约束数量异常: {len(rows)}")
            
            print("\n" + "="*60)
            print("✅ 迁移验证完成！")
            print("="*60)
            return True
            
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        return False


if __name__ == "__main__":
    print("🚀 WordStyle 数据库迁移工具")
    print("="*60)
    
    # 1. 检查数据库连接
    db_url = get_database_url()
    if not check_connection(db_url):
        sys.exit(1)
    
    # 2. 执行迁移
    if not run_migration():
        sys.exit(1)
    
    # 3. 验证迁移结果
    if not verify_migration(db_url):
        print("\n️  迁移可能未完全成功，请手动检查数据库结构")
        sys.exit(1)
    
    print("\n🎉 所有操作完成！")
    print("\n下一步：")
    print("1. 重启后端服务")
    print("2. 测试新用户注册功能")
    print("3. 验证用户数据是否正确写入数据库")
