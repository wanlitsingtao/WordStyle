# -*- coding: utf-8 -*-
"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# 创建数据库引擎
connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif settings.DATABASE_URL.startswith("postgresql"):
    # Render 环境配置：强制使用 IPv4
    # 通过在 URL 中直接指定 IPv4 地址或使用连接池器
    if os.getenv("RENDER"):
        # 在 Render 环境中，使用连接池器（PgBouncer）
        # 连接池器支持 IPv4 且连接更稳定
        original_url = settings.DATABASE_URL
        # 将直接连接转换为连接池连接
        # 格式: postgresql://user:pass@host:5432/db -> postgresql://user:pass@aws-0-region.pooler.supabase.com:6543/db
        if "supabase.co" in original_url and ":5432" in original_url:
            # 提取项目名称（数据库主机名中的标识符）
            host_part = original_url.split("@")[-1].split("/")[0]
            project_id = host_part.replace("db.", "").replace(".supabase.co", "")
            
            # 使用连接池器 URL
            pooler_url = original_url.replace(
                f"db.{project_id}.supabase.co:5432",
                f"aws-0-ap-southeast-1.pooler.supabase.com:6543"
            )
            print(f"✅ Render 环境：使用连接池器")
            print(f"   原始 URL: {original_url[:60]}...")
            print(f"   池化 URL: {pooler_url[:60]}...")
            
            # 更新数据库 URL
            settings.DATABASE_URL = pooler_url

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """
    获取数据库会话
    
    Yields:
        SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
