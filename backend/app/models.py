# -*- coding: utf-8 -*-
"""
数据模型定义
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base
from sqlalchemy import TypeDecorator

# SQLite 兼容的 UUID 类型
class UUID(TypeDecorator):
    impl = String(36)  # UUID 字符串长度为 36
    cache_ok = True
    
    def __init__(self, as_uuid=False):
        super().__init__()
        self.as_uuid = as_uuid
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        if self.as_uuid and isinstance(value, str):
            return uuid.UUID(value)
        return value

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 微信扫码登录相关字段
    wechat_openid = Column(String(128), unique=True, nullable=True, index=True)  # 微信OpenID
    wechat_nickname = Column(String(100))  # 微信昵称
    wechat_avatar = Column(String(500))  # 微信头像URL
    # 兼容传统邮箱登录（可选）
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100))
    password_hash = Column(String(255), nullable=True)  # 改为可空，微信扫码无需密码
    balance = Column(Float, default=0.0)
    paragraphs_remaining = Column(Integer, default=0)
    # 统计字段
    total_paragraphs_used = Column(Integer, default=0)  # 累计使用的段落数
    total_converted = Column(Integer, default=0)  # 累计转换的文件数
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.email}>"

class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_no = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    paragraphs = Column(Integer, nullable=False)
    package_label = Column(String(100))
    status = Column(String(20), default="PENDING")  # PENDING, PAID, FAILED, REFUNDED
    payment_method = Column(String(20))  # WECHAT, ALIPAY
    transaction_id = Column(String(128))  # 支付平台交易号
    paid_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Order {self.order_no}>"

class ConversionTask(Base):
    """转换任务模型"""
    __tablename__ = "conversion_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255))
    paragraphs = Column(Integer)
    cost = Column(Float)
    status = Column(String(20), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    progress = Column(Integer, default=0)
    output_files = Column(Text)  # JSON 字符串，SQLite 不支持 JSONB
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<ConversionTask {self.task_id}>"

class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=False)
    description = Column(String(500))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemConfig {self.config_key}>"
