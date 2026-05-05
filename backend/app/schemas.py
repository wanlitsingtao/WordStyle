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
    password: str = Field(..., min_length=6, description="密码至少6位")
    username: Optional[str] = None

class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """用户信息响应"""
    id: UUID
    email: str
    username: Optional[str]
    balance: float
    paragraphs_remaining: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserUpdate(BaseModel):
    """更新用户信息"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None

# ==================== 微信扫码登录相关 ====================

class WechatLoginRequest(BaseModel):
    """微信扫码登录请求"""
    scene_id: str

class UserInfo(BaseModel):
    """用户信息（微信登录）"""
    id: UUID
    wechat_openid: Optional[str] = None
    wechat_nickname: Optional[str] = None
    wechat_avatar: Optional[str] = None
    balance: float
    paragraphs_remaining: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WechatLoginResponse(BaseModel):
    """微信扫码登录响应"""
    status: str  # scanning, scanned, confirmed, success, expired
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user_info: Optional[UserInfo] = None
    message: str

# ==================== 支付相关 ====================

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    amount: float = Field(..., gt=0, description="充值金额必须大于0")
    package_label: str

class OrderResponse(BaseModel):
    """订单响应"""
    order_no: str
    user_id: UUID
    amount: float
    paragraphs: int
    package_label: Optional[str]
    status: str
    payment_method: Optional[str]
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderStatusResponse(BaseModel):
    """订单状态响应"""
    order_no: str
    status: str
    amount: float
    paragraphs: int
    paid_at: Optional[datetime]

# ==================== 转换相关 ====================

class StartConversionRequest(BaseModel):
    """开始转换请求"""
    filename: str
    paragraphs: int

class ConversionTaskResponse(BaseModel):
    """转换任务响应"""
    task_id: str
    user_id: UUID
    filename: str
    paragraphs: Optional[int]
    cost: Optional[float]
    status: str
    progress: int
    output_files: Optional[List[str]]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ConversionHistoryResponse(BaseModel):
    """转换历史响应"""
    tasks: List[ConversionTaskResponse]
    total: int
