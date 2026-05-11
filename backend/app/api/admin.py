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

@router.get("/users")
def get_users_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": db.query(User).count(),
        "users": [
            {
                'user_id': u.id,
                'balance': float(u.balance or 0),
                'paragraphs_remaining': int(u.paragraphs_remaining or 0),
                'paragraphs_used': int(u.total_paragraphs_used or 0),
                'total_converted': int(u.total_converted or 0),
                'is_active': bool(u.is_active),
                'created_at': u.created_at.isoformat() if u.created_at else '',
                'last_login': u.last_login.isoformat() if u.last_login else '',
            }
            for u in users
        ]
    }

@router.get("/tasks")
def get_tasks_list(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    from app.models import ConversionTask
    
    query = db.query(ConversionTask)
    if status_filter and status_filter != 'ALL':
        query = query.filter(ConversionTask.status == status_filter)
    
    tasks = query.order_by(ConversionTask.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "total": total,
        "tasks": [
            {
                'task_id': t.task_id,
                'user_id': t.user_id,
                'filename': t.filename,
                'file_count': t.file_count,
                'paragraphs': t.paragraphs,
                'cost': float(t.cost or 0),
                'status': t.status,
                'progress': t.progress,
                'created_at': t.created_at.isoformat() if t.created_at else '',
                'completed_at': t.completed_at.isoformat() if t.completed_at else '',
                'error_message': t.error_message,
            }
            for t in tasks
        ]
    }

@router.get("/task-stats")
def get_task_statistics(db: Session = Depends(get_db)):
    """获取任务统计信息"""
    from app.models import ConversionTask
    
    total = db.query(ConversionTask).count()
    completed = db.query(ConversionTask).filter(
        ConversionTask.status == 'COMPLETED'
    ).count()
    processing = db.query(ConversionTask).filter(
        ConversionTask.status == 'PROCESSING'
    ).count()
    pending = db.query(ConversionTask).filter(
        ConversionTask.status == 'PENDING'
    ).count()
    failed = db.query(ConversionTask).filter(
        ConversionTask.status == 'FAILED'
    ).count()
    
    return {
        'total_tasks': total,
        'completed_tasks': completed,
        'processing_tasks': processing,
        'pending_tasks': pending,
        'failed_tasks': failed,
    }
