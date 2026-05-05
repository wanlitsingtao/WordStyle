# -*- coding: utf-8 -*-
"""
支付 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, Order
from app.schemas import CreateOrderRequest, OrderResponse, OrderStatusResponse

router = APIRouter()

@router.post("/create-order", response_model=OrderResponse)
def create_order(
    order_data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建充值订单
    
    Args:
        order_data: 订单信息
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        订单信息和支付链接/二维码
    """
    # 计算段落数（100段落 = 0.1元）
    paragraphs = int(order_data.amount / 0.001)
    
    # 生成订单号
    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    # 创建订单记录
    new_order = Order(
        order_no=order_no,
        user_id=current_user.id,
        amount=order_data.amount,
        paragraphs=paragraphs,
        package_label=order_data.package_label,
        status="PENDING",
        payment_method=None
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # TODO: 调用微信支付或支付宝 API 生成支付链接
    # 这里返回模拟数据，实际应该调用支付 SDK
    
    payment_url = f"https://pay.example.com/pay/{order_no}"
    qr_code = f"data:image/png;base64,MOCK_QR_CODE_FOR_{order_no}"
    
    return OrderResponse(
        order_no=new_order.order_no,
        user_id=new_order.user_id,
        amount=new_order.amount,
        paragraphs=new_order.paragraphs,
        package_label=new_order.package_label,
        status=new_order.status,
        payment_method=new_order.payment_method,
        payment_url=payment_url,
        qr_code=qr_code,
        created_at=new_order.created_at
    )

@router.get("/{order_no}/status", response_model=OrderStatusResponse)
def get_order_status(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询订单状态"""
    order = db.query(Order).filter(Order.order_no == order_no).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return OrderStatusResponse(
        order_no=order.order_no,
        status=order.status,
        amount=order.amount,
        paragraphs=order.paragraphs,
        paid_at=order.paid_at
    )

@router.post("/wechat/callback")
async def wechat_payment_callback(request: Request, db: Session = Depends(get_db)):
    """
    微信支付回调
    
    注意：这是由微信服务器调用的接口
    """
    # TODO: 验证签名
    # TODO: 解析回调数据
    # TODO: 更新订单状态
    # TODO: 为用户充值
    
    # 示例处理逻辑
    data = await request.json()
    order_no = data.get("out_trade_no")
    transaction_id = data.get("transaction_id")
    
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if order and order.status == "PENDING":
        order.status = "PAID"
        order.transaction_id = transaction_id
        order.payment_method = "WECHAT"
        order.paid_at = datetime.utcnow()
        
        # 为用户充值
        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            user.balance += order.amount
            user.paragraphs_remaining += order.paragraphs
        
        db.commit()
    
    return {"code": "SUCCESS", "message": "OK"}

@router.post("/alipay/callback")
async def alipay_payment_callback(request: Request, db: Session = Depends(get_db)):
    """
    支付宝回调
    
    注意：这是由支付宝服务器调用的接口
    """
    # TODO: 验证签名
    # TODO: 解析回调数据
    # TODO: 更新订单状态
    # TODO: 为用户充值
    
    form_data = await request.form()
    order_no = form_data.get("out_trade_no")
    transaction_id = form_data.get("trade_no")
    
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if order and order.status == "PENDING":
        order.status = "PAID"
        order.transaction_id = transaction_id
        order.payment_method = "ALIPAY"
        order.paid_at = datetime.utcnow()
        
        # 为用户充值
        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            user.balance += order.amount
            user.paragraphs_remaining += order.paragraphs
        
        db.commit()
    
    return "success"
