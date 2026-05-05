# -*- coding: utf-8 -*-
"""
微信扫码登录 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import time
import hashlib
from app.core.database import get_db
from app.core.security import create_access_token
from app.models import User, SystemConfig
from app.schemas import WechatLoginRequest, WechatLoginResponse, UserInfo

router = APIRouter()

# 模拟微信OAuth服务（生产环境需要接入真实的微信开放平台）
class MockWechatService:
    """模拟微信服务 - 用于开发测试"""
    
    @staticmethod
    def generate_qr_code(scene_id: str) -> dict:
        """生成二维码（返回二维码URL和scene_id）"""
        # 实际应该调用微信接口生成带参数的二维码
        return {
            "qr_code_url": f"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=mock_{scene_id}",
            "scene_id": scene_id,
            "expire_seconds": 300  # 5分钟过期
        }
    
    @staticmethod
    def check_login_status(scene_id: str) -> dict:
        """检查扫码状态（模拟用户扫码并确认登录）"""
        # 实际应该查询微信服务器的回调结果
        # 这里模拟：如果scene_id存在，则认为已扫码
        return {
            "status": "scanned",  # scanned, confirmed, expired
            "openid": f"mock_openid_{scene_id[-8:]}",
            "nickname": "微信用户",
            "avatar": "https://thirdwx.qlogo.cn/mmopen/mock_avatar.jpg"
        }

wechat_service = MockWechatService()

@router.post("/generate-qr", response_model=dict)
def generate_wechat_qr(db: Session = Depends(get_db)):
    """
    生成微信登录二维码
    
    Returns:
        二维码URL和scene_id
    """
    # 生成唯一的scene_id
    scene_id = f"login_{uuid.uuid4().hex[:16]}"
    
    # 生成二维码
    qr_info = wechat_service.generate_qr_code(scene_id)
    
    return {
        "qr_code_url": qr_info["qr_code_url"],
        "scene_id": scene_id,
        "expire_seconds": qr_info["expire_seconds"],
        "message": "请使用微信扫描二维码登录"
    }

@router.get("/check-status/{scene_id}", response_model=WechatLoginResponse)
def check_wechat_login_status(
    scene_id: str,
    db: Session = Depends(get_db)
):
    """
    检查微信扫码登录状态
    
    Args:
        scene_id: 二维码场景ID
        
    Returns:
        登录状态和用户信息（如果已登录）
    """
    # 检查扫码状态
    scan_status = wechat_service.check_login_status(scene_id)
    
    if scan_status["status"] == "expired":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="二维码已过期，请重新生成"
        )
    
    if scan_status["status"] != "confirmed":
        return WechatLoginResponse(
            status=scan_status["status"],
            message="等待扫码" if scan_status["status"] == "scanned" else "请使用微信扫码"
        )
    
    # 用户已确认登录，查找或创建用户
    openid = scan_status["openid"]
    user = db.query(User).filter(User.wechat_openid == openid).first()
    
    if not user:
        # 首次登录，创建新用户并赠送免费额度
        free_paragraphs = get_free_paragraphs_config(db)
        
        user = User(
            wechat_openid=openid,
            wechat_nickname=scan_status["nickname"],
            wechat_avatar=scan_status["avatar"],
            paragraphs_remaining=free_paragraphs,
            balance=0.0,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        login_message = f"欢迎！已赠送您 {free_paragraphs} 段免费额度"
    else:
        # 老用户，更新昵称和头像
        user.wechat_nickname = scan_status["nickname"]
        user.wechat_avatar = scan_status["avatar"]
        db.commit()
        db.refresh(user)
        
        login_message = f"欢迎回来，{user.wechat_nickname or '用户'}"
    
    # 生成JWT Token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return WechatLoginResponse(
        status="success",
        access_token=access_token,
        token_type="bearer",
        user_info=UserInfo(
            id=user.id,
            wechat_openid=user.wechat_openid,
            wechat_nickname=user.wechat_nickname,
            wechat_avatar=user.wechat_avatar,
            balance=user.balance,
            paragraphs_remaining=user.paragraphs_remaining,
            created_at=user.created_at
        ),
        message=login_message
    )

def get_free_paragraphs_config(db: Session) -> int:
    """获取免费段落数配置"""
    config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "free_paragraphs_on_first_login"
    ).first()
    
    if config:
        return int(config.config_value)
    
    # 默认值：10000段
    return 10000

@router.get("/config/free-paragraphs")
def get_free_paragraphs_config_api(db: Session = Depends(get_db)):
    """获取免费段落数配置（公开接口）"""
    free_paragraphs = get_free_paragraphs_config(db)
    return {
        "free_paragraphs": free_paragraphs,
        "message": f"新用户首次登录赠送 {free_paragraphs} 段免费额度"
    }
