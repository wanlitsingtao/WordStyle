#!/usr/bin/env python3
"""
数据库迁移回滚脚本
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
env_file = Path(__file__).parent / '.env'
load_dotenv(env_file)

from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command

db_url = os.getenv("DATABASE_URL")

# 创建 Alembic 配置
alembic_cfg = Config(str(Path(__file__).parent / "alembic.ini"))
alembic_cfg.set_main_option("sqlalchemy.url", db_url.replace('%', '%%'))

print("🔄 正在回滚数据库到版本 001...")

try:
    command.downgrade(alembic_cfg, "001")
    print("✅ 回滚成功！")
except Exception as e:
    print(f"❌ 回滚失败: {e}")
    sys.exit(1)

# 验证回滚结果
print("\n🔍 验证数据库状态...")
engine = create_engine(db_url)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'id'
    """))
    rows = result.fetchall()
    print(f"users 表 id 字段: {rows}")

print("\n✅ 回滚完成，可以重新执行迁移。")
