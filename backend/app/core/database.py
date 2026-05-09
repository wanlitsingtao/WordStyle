# -*- coding: utf-8 -*-
"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import socket

# 创建数据库引擎
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif settings.DATABASE_URL.startswith("postgresql"):
    # 强制使用 IPv4，避免 Render 环境 IPv6 网络不可达问题
    try:
        import psycopg2
        # 解析主机名的 IPv4 地址
        url_parts = settings.DATABASE_URL.replace("postgresql://", "").split("@")
        host_port = url_parts[-1].split("/")[0] if "/" in url_parts[-1] else url_parts[-1]
        host = host_port.split(":")[0]
        ipv4_addr = socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
        connect_args["host"] = ipv4_addr
        print(f"✅ 数据库连接使用 IPv4: {ipv4_addr}")
    except Exception as e:
        print(f"⚠️  IPv4 解析失败，使用默认连接: {e}")

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
