# -*- coding: utf-8 -*-
"""
统一数据访问层 - 支持双模式（SQLite/Supabase）
自动检测环境并选择合适的数据源
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 导入配置
sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_SOURCE, DATABASE_URL, USER_DATA_FILE, TASKS_DB_FILE

# ==================== 本地模式导入 ====================
if DATA_SOURCE == "local":
    from user_manager import (
        load_user_data as _load_user,
        save_user_data as _save_user,
        load_all_users_data as _load_all_users,
        claim_free_paragraphs as _claim_free,
        recharge_user as _recharge_user,
        deduct_paragraphs as _deduct_paragraphs,
        add_conversion_record as _add_conversion_record,
        get_user_stats as _get_user_stats,
        generate_user_id as _generate_user_id,
    )
    from task_manager import (
        create_task as _create_task,
        update_task_status as _update_task_status,
        complete_task as _complete_task,
        fail_task as _fail_task,
        get_all_tasks as _get_all_tasks,
        get_task_stats as _get_task_stats,
        register_or_login_user as _register_user,
        get_user_active_task as _get_user_active_task,
        get_user_completed_tasks as _get_user_completed_tasks,
        has_active_task as _has_active_task,
        cleanup_expired_tasks as _cleanup_expired_tasks,
    )
    print(f"✅ 数据访问层初始化：本地模式 (SQLite + JSON)")

# ==================== Supabase 模式导入 ====================
elif DATA_SOURCE == "supabase":
    try:
        # 添加 backend 路径
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from app.core.database import SessionLocal
        from app.models import User, ConversionTask
        
        def _load_user(user_id: str) -> Dict[str, Any]:
            """从 Supabase 加载用户数据"""
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        'user_id': user.id,
                        'balance': float(user.balance or 0),
                        'paragraphs_remaining': int(user.paragraphs_remaining or 0),
                        'paragraphs_used': int(user.total_paragraphs_used or 0),
                        'total_converted': int(user.total_converted or 0),
                        'is_active': bool(user.is_active),
                        'created_at': user.created_at.isoformat() if user.created_at else '',
                        'last_login': user.last_login.isoformat() if user.last_login else '',
                    }
                return None
            finally:
                db.close()
        
        def _save_user(user_data: Dict[str, Any], user_id: str = None):
            """保存用户数据到 Supabase"""
            # Supabase 模式下，用户数据通过 ORM 管理
            # 此函数主要用于兼容性，实际保存在其他地方处理
            pass
        
        def _load_all_users() -> List[Dict[str, Any]]:
            """从 Supabase 加载所有用户"""
            db = SessionLocal()
            try:
                users = db.query(User).all()
                return [
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
            finally:
                db.close()
        
        def _register_user(user_id: str, user_data: Dict[str, Any]):
            """注册或更新用户到 Supabase"""
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # 更新现有用户
                    user.balance = user_data.get('balance', 0)
                    user.paragraphs_remaining = user_data.get('paragraphs_remaining', 0)
                    user.total_paragraphs_used = user_data.get('paragraphs_used', 0)
                    user.total_converted = user_data.get('total_converted', 0)
                    user.last_login = datetime.now()
                else:
                    # 创建新用户
                    user = User(
                        id=user_id,
                        balance=user_data.get('balance', 0),
                        paragraphs_remaining=user_data.get('paragraphs_remaining', 0),
                        total_paragraphs_used=user_data.get('paragraphs_used', 0),
                        total_converted=user_data.get('total_converted', 0),
                        is_active=True,
                        created_at=datetime.now(),
                        last_login=datetime.now(),
                    )
                    db.add(user)
                db.commit()
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()
        
        def _create_task(*args, **kwargs):
            """创建任务（Supabase 模式）"""
            # TODO: 实现 Supabase 任务创建
            pass
        
        def _complete_task(*args, **kwargs):
            """完成任务（Supabase 模式）"""
            # TODO: 实现 Supabase 任务完成
            pass
        
        def _fail_task(*args, **kwargs):
            """标记任务失败（Supabase 模式）"""
            # TODO: 实现 Supabase 任务失败
            pass
        
        def _get_all_tasks(status_filter=None, limit=100, offset=0):
            """获取所有任务（Supabase 模式）"""
            db = SessionLocal()
            try:
                query = db.query(ConversionTask)
                if status_filter and status_filter != 'ALL':
                    query = query.filter(ConversionTask.status == status_filter)
                
                tasks = query.order_by(ConversionTask.created_at.desc()).limit(limit).offset(offset).all()
                
                return [
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
            finally:
                db.close()
        
        def _get_task_stats():
            """获取任务统计（Supabase 模式）"""
            db = SessionLocal()
            try:
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
            finally:
                db.close()
        
        # 用户管理相关函数（Supabase 模式 - 完整实现）
        def _claim_free(user_id=None):
            """领取免费段落（Supabase 模式）"""
            from config import FREE_PARAGRAPHS_DAILY
            
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.paragraphs_remaining += FREE_PARAGRAPHS_DAILY
                    db.commit()
                    return FREE_PARAGRAPHS_DAILY
                return 0
            except Exception as e:
                db.rollback()
                print(f"⚠️ 领取免费段落失败: {e}")
                return 0
            finally:
                db.close()
        
        def _recharge_user(amount, package_label, user_id=None):
            """充值用户（Supabase 模式）"""
            # 计算段落数：1元 = 1000段落
            paragraphs = int(amount * 1000)
            
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.balance += amount
                    user.paragraphs_remaining += paragraphs
                    db.commit()
                    return {
                        'success': True,
                        'amount': amount,
                        'paragraphs': paragraphs,
                        'new_balance': user.balance,
                        'new_paragraphs': user.paragraphs_remaining
                    }
                return {'success': False, 'error': '用户不存在'}
            except Exception as e:
                db.rollback()
                print(f"⚠️ 充值失败: {e}")
                return {'success': False, 'error': str(e)}
            finally:
                db.close()
        
        def _deduct_paragraphs(paragraphs, user_id=None):
            """扣除段落（Supabase 模式）"""
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    if user.paragraphs_remaining >= paragraphs:
                        user.paragraphs_remaining -= paragraphs
                        db.commit()
                        return True
                    else:
                        return False  # 余额不足
                return False
            except Exception as e:
                db.rollback()
                print(f"⚠️ 扣除段落失败: {e}")
                return False
            finally:
                db.close()
        
        def _add_conversion_record(files_count, success_count, failed_count, user_id=None):
            """添加转换记录（Supabase 模式）"""
            # Supabase 模式下，转换记录通过 ConversionTask 表管理
            # 此函数主要用于兼容性，实际在任务完成时自动记录
            pass
        
        def _get_user_stats(user_id=None):
            """获取用户统计（Supabase 模式）"""
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        'user_id': str(user.id),
                        'balance': float(user.balance or 0),
                        'paragraphs_remaining': int(user.paragraphs_remaining or 0),
                        'is_active': bool(user.is_active),
                        'created_at': user.created_at.isoformat() if user.created_at else '',
                    }
                return {}
            finally:
                db.close()
        
        def _generate_user_id():
            """生成用户ID（Supabase 模式）"""
            import uuid
            return str(uuid.uuid4())
        
        def _create_task(task_id, user_id, filename, file_count=1, paragraphs=0, cost=0.0):
            """创建任务（Supabase 模式）"""
            db = SessionLocal()
            try:
                task = ConversionTask(
                    task_id=task_id,
                    user_id=user_id,
                    filename=filename,
                    file_count=file_count,
                    paragraphs=paragraphs,
                    cost=cost,
                    status='PENDING',
                    progress=0
                )
                db.add(task)
                db.commit()
                return task_id
            except Exception as e:
                db.rollback()
                print(f"⚠️ 创建任务失败: {e}")
                return None
            finally:
                db.close()
        
        def _update_task_status(task_id, status, progress=None, error_message=None):
            """更新任务状态（Supabase 模式）"""
            db = SessionLocal()
            try:
                task = db.query(ConversionTask).filter(ConversionTask.task_id == task_id).first()
                if task:
                    task.status = status
                    if progress is not None:
                        task.progress = progress
                    if error_message is not None:
                        task.error_message = error_message
                    if status == 'COMPLETED':
                        task.completed_at = datetime.now()
                    db.commit()
                    return True
                return False
            except Exception as e:
                db.rollback()
                print(f"⚠️ 更新任务状态失败: {e}")
                return False
            finally:
                db.close()
        
        def _complete_task(task_id):
            """完成任务（Supabase 模式）"""
            return _update_task_status(task_id, 'COMPLETED', progress=100)
        
        def _fail_task(task_id, error_message=""):
            """标记任务失败（Supabase 模式）"""
            return _update_task_status(task_id, 'FAILED', error_message=error_message)
        
        def _get_user_active_task(user_id):
            """获取用户活动任务（Supabase 模式）"""
            db = SessionLocal()
            try:
                task = db.query(ConversionTask).filter(
                    ConversionTask.user_id == user_id,
                    ConversionTask.status.in_(['PENDING', 'PROCESSING'])
                ).first()
                return task
            finally:
                db.close()
        
        def _get_user_completed_tasks(user_id, limit=20):
            """获取用户已完成任务（Supabase 模式）"""
            db = SessionLocal()
            try:
                tasks = db.query(ConversionTask).filter(
                    ConversionTask.user_id == user_id,
                    ConversionTask.status == 'COMPLETED'
                ).order_by(ConversionTask.created_at.desc()).limit(limit).all()
                
                return [
                    {
                        'task_id': t.task_id,
                        'filename': t.filename,
                        'paragraphs': t.paragraphs,
                        'cost': float(t.cost or 0),
                        'created_at': t.created_at.isoformat() if t.created_at else '',
                        'completed_at': t.completed_at.isoformat() if t.completed_at else '',
                    }
                    for t in tasks
                ]
            finally:
                db.close()
        
        def _has_active_task(user_id):
            """检查用户是否有活动任务（Supabase 模式）"""
            return _get_user_active_task(user_id) is not None
        
        def _cleanup_expired_tasks():
            """清理过期任务（Supabase 模式）"""
            from config import TASK_EXPIRY_DAYS
            from datetime import timedelta
            
            db = SessionLocal()
            try:
                expiry_date = datetime.now() - timedelta(days=TASK_EXPIRY_DAYS)
                deleted = db.query(ConversionTask).filter(
                    ConversionTask.created_at < expiry_date,
                    ConversionTask.status == 'COMPLETED'
                ).delete()
                db.commit()
                return deleted
            except Exception as e:
                db.rollback()
                print(f"⚠️ 清理过期任务失败: {e}")
                return 0
            finally:
                db.close()
        
        print(f"✅ 数据访问层初始化：Supabase 模式 (PostgreSQL)")
    
    except ImportError as e:
        print(f"⚠️ Supabase 模式初始化失败: {e}")
        print("   回退到本地模式")
        DATA_SOURCE = "local"
        from user_manager import (
            load_user_data as _load_user,
            save_user_data as _save_user,
            load_all_users_data as _load_all_users,
        )
        from task_manager import (
            create_task as _create_task,
            complete_task as _complete_task,
            fail_task as _fail_task,
            get_all_tasks as _get_all_tasks,
            get_task_stats as _get_task_stats,
            register_or_login_user as _register_user,
        )

# ==================== 统一 API ====================

def load_user_data(user_id: str) -> Optional[Dict[str, Any]]:
    """加载用户数据"""
    return _load_user(user_id)

def save_user_data(user_data: Dict[str, Any], user_id: str = None):
    """保存用户数据"""
    return _save_user(user_data, user_id)

def load_all_users_data() -> List[Dict[str, Any]]:
    """加载所有用户数据"""
    return _load_all_users()

def register_or_login_user(user_id: str, user_data: Dict[str, Any]):
    """注册用户或更新登录时间"""
    return _register_user(user_id, user_data)

def claim_free_paragraphs(user_id=None):
    """领取免费段落"""
    return _claim_free(user_id)

def recharge_user(amount, package_label, user_id=None):
    """充值用户"""
    return _recharge_user(amount, package_label, user_id)

def deduct_paragraphs(paragraphs, user_id=None):
    """扣除段落"""
    return _deduct_paragraphs(paragraphs, user_id)

def add_conversion_record(files_count, success_count, failed_count, user_id=None):
    """添加转换记录"""
    return _add_conversion_record(files_count, success_count, failed_count, user_id)

def get_user_stats(user_id=None):
    """获取用户统计"""
    return _get_user_stats(user_id)

def generate_user_id():
    """生成用户ID"""
    return _generate_user_id()

def create_task(*args, **kwargs):
    """创建转换任务"""
    return _create_task(*args, **kwargs)

def update_task_status(*args, **kwargs):
    """更新任务状态"""
    return _update_task_status(*args, **kwargs)

def complete_task(*args, **kwargs):
    """标记任务完成"""
    return _complete_task(*args, **kwargs)

def fail_task(*args, **kwargs):
    """标记任务失败"""
    return _fail_task(*args, **kwargs)

def get_all_tasks(status_filter=None, limit=100, offset=0):
    """获取所有任务"""
    return _get_all_tasks(status_filter=status_filter, limit=limit, offset=offset)

def get_task_stats():
    """获取任务统计"""
    return _get_task_stats()

def get_user_active_task(user_id):
    """获取用户活动任务"""
    return _get_user_active_task(user_id)

def get_user_completed_tasks(user_id, limit=20):
    """获取用户已完成任务"""
    return _get_user_completed_tasks(user_id, limit)

def has_active_task(user_id):
    """检查用户是否有活动任务"""
    return _has_active_task(user_id)

def cleanup_expired_tasks():
    """清理过期任务"""
    return _cleanup_expired_tasks()

# ==================== 导出当前数据源类型 ====================
def get_data_source():
    """获取当前数据源类型"""
    return DATA_SOURCE
