# -*- coding: utf-8 -*-
"""
简化版支付测试 API - 用于演示完整支付流程
无需真实商户号，模拟完整的支付体验
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import json
from pathlib import Path
from typing import Optional

router = APIRouter()

# 数据文件路径
USER_DATA_FILE = Path("e:/LingMa/WordStyle/user_data.json")

class CreatePaymentRequest(BaseModel):
    """创建支付请求"""
    user_id: str
    amount: float
    paragraphs: int
    package_label: str

class PaymentResponse(BaseModel):
    """支付响应"""
    order_id: str
    qr_code_url: str
    user_id: str
    amount: float
    paragraphs: int
    status: str
    message: str

class SimulatePaymentRequest(BaseModel):
    """模拟支付请求"""
    order_id: str
    user_id: str

@router.post("/create", response_model=PaymentResponse)
def create_payment(request: CreatePaymentRequest):
    """
    创建支付订单
    
    生成订单并返回二维码URL（模拟）
    """
    # 生成订单ID
    order_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
    
    # 保存订单信息（内存中，生产环境应使用数据库）
    if not hasattr(create_payment, 'orders'):
        create_payment.orders = {}
    
    create_payment.orders[order_id] = {
        'order_id': order_id,
        'user_id': request.user_id,
        'amount': request.amount,
        'paragraphs': request.paragraphs,
        'package_label': request.package_label,
        'status': 'PENDING',
        'created_at': datetime.now().isoformat(),
        'paid_at': None
    }
    
    # 生成模拟二维码URL（包含订单信息）
    qr_data = {
        'order_id': order_id,
        'user_id': request.user_id,
        'amount': request.amount,
        'type': 'payment'
    }
    
    # 在实际应用中，这里应该调用微信支付API生成真实二维码
    # 当前使用占位图
    qr_code_url = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZjdmYWZjIi8+CiAgICA8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjYTBhZWMwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+CiAgICAgICAg5byA5aeL5LiJ5q+B5L2gCiAgICA8L3RleHQ+Cjwvc3ZnPg=="
    
    return PaymentResponse(
        order_id=order_id,
        qr_code_url=qr_code_url,
        user_id=request.user_id,
        amount=request.amount,
        paragraphs=request.paragraphs,
        status='PENDING',
        message=f"订单已创建，请扫描二维码支付 ¥{request.amount}"
    )

@router.post("/simulate-payment")
def simulate_payment(request: SimulatePaymentRequest):
    """
    模拟支付成功回调
    
    这是关键功能：模拟用户扫码支付后，微信服务器会回调这个接口
    在实际生产中，这应该是微信支付的notify_url
    """
    # 检查订单是否存在
    if not hasattr(create_payment, 'orders'):
        raise HTTPException(status_code=404, detail="订单不存在")
    
    order = create_payment.orders.get(request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 验证用户ID
    if order['user_id'] != request.user_id:
        raise HTTPException(status_code=400, detail="用户ID不匹配")
    
    # 更新订单状态
    order['status'] = 'PAID'
    order['paid_at'] = datetime.now().isoformat()
    
    # 充值到用户账户
    success = recharge_user(request.user_id, order['amount'], order['paragraphs'])
    
    if success:
        return {
            'success': True,
            'message': f"✅ 支付成功！已充值 {order['paragraphs']:,} 段",
            'order_id': request.order_id,
            'user_id': request.user_id,
            'amount': order['amount'],
            'paragraphs_added': order['paragraphs']
        }
    else:
        raise HTTPException(status_code=500, detail="充值失败")

@router.get("/check-status/{order_id}")
def check_payment_status(order_id: str):
    """
    检查支付状态
    
    前端可以轮询这个接口来检查支付是否完成
    """
    if not hasattr(create_payment, 'orders'):
        return {'status': 'NOT_FOUND'}
    
    order = create_payment.orders.get(order_id)
    if not order:
        return {'status': 'NOT_FOUND'}
    
    return {
        'order_id': order_id,
        'status': order['status'],
        'user_id': order['user_id'],
        'amount': order['amount'],
        'paragraphs': order['paragraphs'],
        'created_at': order['created_at'],
        'paid_at': order.get('paid_at')
    }

def recharge_user(user_id: str, amount: float, paragraphs: int) -> bool:
    """
    为用户充值
    
    直接修改 user_data.json 文件
    """
    try:
        # 读取用户数据
        if USER_DATA_FILE.exists():
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        else:
            all_data = {}
        
        # 初始化用户数据（如果不存在）
        if user_id not in all_data:
            all_data[user_id] = {
                'balance': 0.0,
                'paragraphs_remaining': 0,
                'total_converted': 0,
                'total_paragraphs_used': 0,
                'recharge_history': [],
                'conversion_history': []
            }
        
        # 充值
        all_data[user_id]['balance'] += amount
        all_data[user_id]['paragraphs_remaining'] += paragraphs
        
        # 添加充值记录
        recharge_record = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'amount': amount,
            'paragraphs': paragraphs,
            'order_id': f"PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'method': 'wechat_scan'
        }
        all_data[user_id]['recharge_history'].append(recharge_record)
        
        # 保存
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    except Exception as e:
        print(f"充值失败: {str(e)}")
        return False
