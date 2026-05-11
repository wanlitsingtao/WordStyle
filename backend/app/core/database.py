# -*- coding: utf-8 -*-
"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

# 创建数据库引擎
connect_args = {}
final_url = settings.DATABASE_URL

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif settings.DATABASE_URL.startswith("postgresql"):
    # Supabase 环境配置：自动处理连接池器
    original_url = settings.DATABASE_URL
    final_url = original_url
    
    # 检测 Supabase 连接池器地址（可能因网络限制无法访问）
    if "pooler.supabase.com" in original_url:
        # 尝试从连接池器地址转换为直连地址
        # 连接池器格式: {project_id}.pooler.supabase.com:6543
        # 直连格式: db.{project_id}.supabase.co:5432
        if ".pooler.supabase.com" in original_url:
            # 提取项目 ID
            host_part = original_url.split("@")[-1].split(":")[0]  # 如: cgfdhubkklpyvjgezeeq.pooler.supabase.com
            project_id = host_part.replace(".pooler.supabase.com", "")
            
            # 提取用户名（连接池器格式: postgres.{project_id}）
            user_part = original_url.split("://")[1].split("@")[0]
            # 转换为直连用户名
            direct_user = user_part.replace(f"postgres.{project_id}", "postgres")
            
            # 构建直连 URL
            final_url = original_url.replace(
                f"{project_id}.pooler.supabase.com:6543",
                f"db.{project_id}.supabase.co:5432"
            ).replace(f"{user_part}@", f"{direct_user}@")
            
            logger.info(f"✅ 检测到 Supabase 连接池器，自动切换为直连地址（Streamlit Cloud 兼容）")
            logger.info(f"   池化 URL: {original_url[:60]}...")
            logger.info(f"   直连 URL: {final_url[:60]}...")
    
    # 情况 2: 已经是连接池器但端口错误 (*.pooler.supabase.com:5432)
    elif "pooler.supabase.com:5432" in original_url:
        # 只需修正端口号
        final_url = original_url.replace(":5432", ":6543")
        logger.info(f"✅ 检测到连接池器端口错误，已修正为 6543")
    
    if final_url != original_url:
        logger.info(f"   原始 URL: {settings.DATABASE_URL[:60]}...")
        logger.info(f"   最终 URL: {final_url[:60]}...")

logger.info(f"🔗 数据库引擎创建 - URL: {final_url[:60]}...")
engine = create_engine(final_url, connect_args=connect_args)

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
