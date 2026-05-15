# -*- coding: utf-8 -*-
"""
Alembic 配置
"""
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 加载 .env 文件（如果存在）
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded .env file: {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed, skipping .env loading")

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base
from app.models import User, ConversionTask, SystemConfig, Comment, Feedback, StyleMapping

# this is the Alembic Config object
config = context.config

# 从环境变量读取 DATABASE_URL（Render 部署）
database_url = os.getenv('DATABASE_URL')
if database_url:
    # 转义 % 字符，避免 ConfigParser 将其视为插值语法
    escaped_url = database_url.replace('%', '%%')
    config.set_main_option('sqlalchemy.url', escaped_url)
    print(f"✅ Alembic using DATABASE_URL from environment")
else:
    print(f"⚠️ DATABASE_URL not found, using alembic.ini config")

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
