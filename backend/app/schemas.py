# -*- coding: utf-8 -*-
"""
Pydantic Schemas - 用于 API 请求和响应验证
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# ==================== 用户相关 ====================

class UserRegister(BaseModel):
    """用户注册请求"""
    email: EmailStr
    username: Optional[str] = None
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserUpdate(BaseModel):
    """用户更新请求"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    """用户信息响应（基于实际数据库结构）"""
    id: str  # 12位字符串用户ID
    username: Optional[str] = None
    balance: float = 0.0
    paragraphs_remaining: int = 0
    total_paragraphs_used: int = 0
    total_converted: int = 0
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserInfo(BaseModel):
    """微信用户信息"""
    id: str
    wechat_openid: Optional[str] = None
    wechat_nickname: Optional[str] = None
    wechat_avatar: Optional[str] = None
    balance: float = 0.0
    paragraphs_remaining: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    scene_id: str

class WechatLoginResponse(BaseModel):
    """微信登录响应"""
    status: str  # scanned, confirmed, success, expired
    message: Optional[str] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    user_info: Optional[UserInfo] = None

# ==================== 评论相关 ====================

class CommentResponse(BaseModel):
    """评论响应"""
    id: UUID
    user_id: Optional[str] = None
    username: Optional[str] = None
    content: str
    rating: int = 5
    likes: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== 反馈相关 ====================

class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: UUID
    user_id: Optional[str] = None
    feedback_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    contact: Optional[str] = None
    status: str = 'pending'
    reply: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==================== 样式映射相关 ====================

class StyleMappingResponse(BaseModel):
    """样式映射响应"""
    id: UUID
    user_id: str
    filename: str
    source_style: str
    target_style: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 订单相关已移除，直接进入转换任务相关

# ==================== 转换任务相关 ====================

class StartConversionRequest(BaseModel):
    """开始转换请求"""
    filename: str
    paragraphs: int = Field(..., gt=0)

class ConversionTaskResponse(BaseModel):
    """转换任务响应"""
    task_id: Optional[str] = None
    user_id: str
    filename: Optional[str] = None
    paragraphs: Optional[int] = None
    cost: Optional[float] = None
    status: str
    progress: int
    output_files: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConversionHistoryResponse(BaseModel):
    """转换历史响应"""
    tasks: List[ConversionTaskResponse]
    total: int

# ==================== 订单相关 ====================

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    paragraphs: int = Field(..., gt=0)

class OrderResponse(BaseModel):
    """订单响应"""
    order_no: str
    user_id: str
    paragraphs: int
    amount: float
    status: str
    qr_code_url: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True

class OrderStatusResponse(BaseModel):
    """订单状态响应"""
    order_no: str
    status: str
    paid_at: Optional[datetime] = None
