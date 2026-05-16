# -*- coding: utf-8 -*-
"""
FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, users, conversions, wechat_auth, admin, feedback, monitoring
import logging

logger = logging.getLogger(__name__)


def run_migrations():
    """
    运行数据库迁移（Alembic）
    
    注意：此函数会在应用启动时自动执行，确保数据库结构与代码模型同步。
    如果迁移失败，应用仍会启动，但会在日志中记录错误。
    """
    try:
        from alembic.config import Config
        from alembic import command
        import os
        
        logger.info("正在检查数据库迁移...")
        alembic_cfg = Config("alembic.ini")
        
        # 从环境变量读取 DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # 转义 % 字符，避免 ConfigParser 插值问题
            escaped_url = database_url.replace('%', '%%')
            alembic_cfg.set_main_option('sqlalchemy.url', escaped_url)
            logger.info("✅ Alembic 使用环境变量 DATABASE_URL")
        
        # 先尝试 stamp head 解决多 head 冲突
        try:
            logger.info("📝 标记当前 Alembic 版本...")
            command.stamp(alembic_cfg, "head")
            logger.info("✅ Stamp 成功")
        except Exception as stamp_error:
            logger.warning(f"⚠️ Stamp 失败（可能数据库为空）: {stamp_error}")
        
        # 执行数据库迁移
        logger.info("🔄 执行数据库迁移...")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ 数据库迁移完成")
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        logger.warning("应用将继续启动，但请检查数据库状态")
        # 不抛出异常，允许应用继续启动

def create_application() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="文档转换平台 API",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置 CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    application.include_router(auth.router, prefix="/api/auth", tags=["认证"])
    application.include_router(wechat_auth.router, prefix="/api/wechat", tags=["微信登录"])
    application.include_router(users.router, prefix="/api/users", tags=["用户"])
    application.include_router(conversions.router, prefix="/api/conversions", tags=["转换"])
    application.include_router(admin.router, prefix="/api/admin", tags=["管理员"])
    application.include_router(feedback.router, prefix="/api/feedback", tags=["用户反馈"])
    application.include_router(monitoring.router, prefix="/monitoring", tags=["监控"])
    
    # 健康检查（同时支持 GET 和 POST，兼容 UptimeRobot 只能发送 POST 的限制）
    @application.get("/health")
    @application.post("/health")
    def health_check():
        return {"status": "healthy"}
    
    @application.get("/")
    def root():
        return {
            "message": f"{settings.APP_NAME} API",
            "version": settings.APP_VERSION,
            "docs": "/docs"
        }
    
    return application

# 创建应用实例
app = create_application()

# 注册启动事件 - 自动运行数据库迁移
@app.on_event("startup")
def startup_event():
    """应用启动时执行的任务"""
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    run_migrations()
