# -*- coding: utf-8 -*-
"""
管理员 API 路由 - 系统配置管理
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import SystemConfig, User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ConfigUpdate(BaseModel):
    """配置更新请求"""
    config_value: str
    description: Optional[str] = None

class FreeParagraphsConfig(BaseModel):
    """免费段落数配置"""
    free_paragraphs: int
    description: Optional[str] = "新用户首次登录赠送的免费段落数"

@router.get("/config/free-paragraphs")
def get_free_paragraphs_config(db: Session = Depends(get_db)):
    """获取免费段落数配置"""
    config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "free_paragraphs_on_first_login"
    ).first()
    
    if not config:
        # 如果不存在，创建默认配置
        config = SystemConfig(
            config_key="free_paragraphs_on_first_login",
            config_value="10000",
            description="新用户首次登录赠送的免费段落数"
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return {
        "config_key": config.config_key,
        "config_value": int(config.config_value),
        "description": config.description,
        "updated_at": config.updated_at
    }

@router.put("/config/free-paragraphs")
def update_free_paragraphs_config(
    config_data: FreeParagraphsConfig,
    db: Session = Depends(get_db)
):
    """
    更新免费段落数配置
    
    Args:
        config_data: 新的配置值
        
    Returns:
        更新后的配置
    """
    if config_data.free_paragraphs < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="免费段落数不能为负数"
        )
    
    config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "free_paragraphs_on_first_login"
    ).first()
    
    if not config:
        config = SystemConfig(
            config_key="free_paragraphs_on_first_login",
            config_value=str(config_data.free_paragraphs),
            description=config_data.description or "新用户首次登录赠送的免费段落数"
        )
        db.add(config)
    else:
        config.config_value = str(config_data.free_paragraphs)
        if config_data.description:
            config.description = config_data.description
    
    db.commit()
    db.refresh(config)
    
    return {
        "message": f"免费段落数配置已更新为 {config_data.free_paragraphs} 段",
        "config_key": config.config_key,
        "config_value": int(config.config_value),
        "description": config.description,
        "updated_at": config.updated_at
    }

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """获取系统统计信息"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # 总充值金额
    from app.models import Order
    from sqlalchemy import func
    total_revenue = db.query(func.sum(Order.amount)).filter(
        Order.status == "PAID"
    ).scalar() or 0.0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_revenue": float(total_revenue),
        "message": "系统统计信息"
    }
