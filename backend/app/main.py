# -*- coding: utf-8 -*-
"""
FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, users, payments, conversions, wechat_auth, admin, test_payment, feedback

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
    application.include_router(payments.router, prefix="/api/payments", tags=["支付"])
    application.include_router(conversions.router, prefix="/api/conversions", tags=["转换"])
    application.include_router(admin.router, prefix="/api/admin", tags=["管理员"])
    application.include_router(test_payment.router, prefix="/api/test-payment", tags=["测试支付"])
    application.include_router(feedback.router, prefix="/api/feedback", tags=["用户反馈"])
    
    # 健康检查
    @application.get("/health")
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

app = create_application()
