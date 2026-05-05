# -*- coding: utf-8 -*-
"""
文档转换 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, ConversionTask
from app.schemas import StartConversionRequest, ConversionTaskResponse, ConversionHistoryResponse

router = APIRouter()

@router.post("/start", response_model=ConversionTaskResponse)
def start_conversion(
    conversion_data: StartConversionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    开始文档转换
    
    Args:
        conversion_data: 转换参数
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        转换任务信息
    """
    # 检查余额是否充足
    cost = conversion_data.paragraphs * 0.001  # 每段落 0.001 元
    
    if current_user.balance < cost:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient balance. Required: ¥{cost:.2f}, Available: ¥{current_user.balance:.2f}"
        )
    
    # 生成任务 ID
    task_id = f"TASK{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    # 创建转换任务
    new_task = ConversionTask(
        task_id=task_id,
        user_id=current_user.id,
        filename=conversion_data.filename,
        paragraphs=conversion_data.paragraphs,
        cost=cost,
        status="PENDING",
        progress=0
    )
    
    db.add(new_task)
    
    # 扣除余额
    current_user.balance -= cost
    current_user.paragraphs_remaining -= conversion_data.paragraphs
    
    db.commit()
    db.refresh(new_task)
    
    # TODO: 启动异步转换任务（使用 Celery）
    # from app.tasks.conversion_tasks import convert_document
    # convert_document.delay(task_id, conversion_data.filename)
    
    return ConversionTaskResponse(
        task_id=new_task.task_id,
        user_id=new_task.user_id,
        filename=new_task.filename,
        paragraphs=new_task.paragraphs,
        cost=new_task.cost,
        status=new_task.status,
        progress=new_task.progress,
        output_files=new_task.output_files,
        error_message=new_task.error_message,
        created_at=new_task.created_at,
        completed_at=new_task.completed_at
    )

@router.get("/{task_id}/status", response_model=ConversionTaskResponse)
def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询转换任务状态"""
    task = db.query(ConversionTask).filter(ConversionTask.task_id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ConversionTaskResponse(
        task_id=task.task_id,
        user_id=task.user_id,
        filename=task.filename,
        paragraphs=task.paragraphs,
        cost=task.cost,
        status=task.status,
        progress=task.progress,
        output_files=task.output_files,
        error_message=task.error_message,
        created_at=task.created_at,
        completed_at=task.completed_at
    )

@router.get("/history", response_model=ConversionHistoryResponse)
def get_conversion_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """获取转换历史"""
    tasks = (
        db.query(ConversionTask)
        .filter(ConversionTask.user_id == current_user.id)
        .order_by(ConversionTask.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    total = (
        db.query(ConversionTask)
        .filter(ConversionTask.user_id == current_user.id)
        .count()
    )
    
    return ConversionHistoryResponse(
        tasks=[ConversionTaskResponse.from_orm(task) for task in tasks],
        total=total
    )

@router.get("/{task_id}/download")
def download_result(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载转换结果"""
    task = db.query(ConversionTask).filter(ConversionTask.task_id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if task.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    # TODO: 返回文件下载链接
    # 实际应该从对象存储（MinIO/S3）获取文件
    
    return {
        "message": "Download endpoint - implement file serving logic",
        "output_files": task.output_files
    }
