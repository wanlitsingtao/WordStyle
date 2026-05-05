# -*- coding: utf-8 -*-
"""
最小化生产级后端 API 示例
展示如何实现用户认证和支付功能
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
import json
from pathlib import Path

# ==================== 配置 ====================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 数据文件路径（生产环境应使用数据库）
USERS_FILE = Path("users.json")
ORDERS_FILE = Path("orders.json")

# ==================== FastAPI 应用 ====================
app = FastAPI(
    title="文档转换平台 API",
    description="生产级文档转换平台后端 API",
    version="1.0.0"
)

# ==================== 数据模型 ====================
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str]
    balance: float
    paragraphs_remaining: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class CreateOrderRequest(BaseModel):
    amount: float
    package_label: str

class OrderResponse(BaseModel):
    order_no: str
    amount: float
    paragraphs: int
    status: str
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None

# ==================== 辅助函数 ====================
def load_users():
    """加载用户数据"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """保存用户数据"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_orders():
    """加载订单数据"""
    if ORDERS_FILE.exists():
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_orders(orders):
    """保存订单数据"""
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def hash_password(password: str) -> str:
    """密码加密"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(authorization: str = Header(...)):
    """获取当前用户（从 Token）"""
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        users = load_users()
        user = users.get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# ==================== API 端点 ====================

@app.get("/")
def read_root():
    return {"message": "文档转换平台 API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- 认证接口 ---

@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserRegister):
    """用户注册"""
    users = load_users()
    
    # 检查邮箱是否已注册
    for u in users.values():
        if u['email'] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建新用户
    user_id = str(uuid.uuid4())
    new_user = {
        'id': user_id,
        'email': user_data.email,
        'username': user_data.username or user_data.email.split('@')[0],
        'password_hash': hash_password(user_data.password),
        'balance': 0.0,
        'paragraphs_remaining': 0,
        'created_at': datetime.now().isoformat()
    }
    
    users[user_id] = new_user
    save_users(users)
    
    return UserResponse(
        id=user_id,
        email=new_user['email'],
        username=new_user['username'],
        balance=new_user['balance'],
        paragraphs_remaining=new_user['paragraphs_remaining']
    )

@app.post("/api/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    """用户登录"""
    users = load_users()
    
    # 查找用户
    user = None
    for u in users.values():
        if u['email'] == credentials.email:
            user = u
            break
    
    if user is None or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # 生成 Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['id']}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            balance=user['balance'],
            paragraphs_remaining=user['paragraphs_remaining']
        )
    )

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user['id'],
        email=current_user['email'],
        username=current_user['username'],
        balance=current_user['balance'],
        paragraphs_remaining=current_user['paragraphs_remaining']
    )

# --- 支付接口 ---

@app.post("/api/payments/create-order", response_model=OrderResponse)
def create_order(order_data: CreateOrderRequest, current_user: dict = Depends(get_current_user)):
    """创建充值订单"""
    # 计算段落数（100段落 = 0.1元）
    paragraphs = int(order_data.amount / 0.001)
    
    # 创建订单
    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    order = {
        'order_no': order_no,
        'user_id': current_user['id'],
        'amount': order_data.amount,
        'paragraphs': paragraphs,
        'package_label': order_data.package_label,
        'status': 'PENDING',
        'created_at': datetime.now().isoformat()
    }
    
    orders = load_orders()
    orders[order_no] = order
    save_orders(orders)
    
    # TODO: 调用微信支付/支付宝 API 生成支付链接或二维码
    # 这里返回模拟数据
    payment_url = f"https://pay.example.com/pay/{order_no}"
    qr_code = f"data:image/png;base64,MOCK_QR_CODE_FOR_{order_no}"
    
    return OrderResponse(
        order_no=order_no,
        amount=order_data.amount,
        paragraphs=paragraphs,
        status='PENDING',
        payment_url=payment_url,
        qr_code=qr_code
    )

@app.get("/api/payments/{order_no}/status")
def get_order_status(order_no: str, current_user: dict = Depends(get_current_user)):
    """查询订单状态"""
    orders = load_orders()
    order = orders.get(order_no)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        'order_no': order['order_no'],
        'status': order['status'],
        'amount': order['amount'],
        'paragraphs': order['paragraphs'],
        'paid_at': order.get('paid_at')
    }

@app.post("/api/payments/wechat/callback")
def wechat_payment_callback():
    """微信支付回调（由微信服务器调用）"""
    # TODO: 验证签名
    # TODO: 更新订单状态
    # TODO: 为用户充值
    
    return {"code": "SUCCESS", "message": "OK"}

@app.post("/api/payments/alipay/callback")
def alipay_payment_callback():
    """支付宝回调（由支付宝服务器调用）"""
    # TODO: 验证签名
    # TODO: 更新订单状态
    # TODO: 为用户充值
    
    return {"success": True}

# --- 用户余额接口 ---

@app.get("/api/users/balance")
def get_balance(current_user: dict = Depends(get_current_user)):
    """查询用户余额"""
    return {
        'balance': current_user['balance'],
        'paragraphs_remaining': current_user['paragraphs_remaining']
    }

# ==================== 启动命令 ====================
"""
运行方式：
1. 安装依赖：pip install fastapi uvicorn pyjwt bcrypt pydantic[email]
2. 启动服务：uvicorn main:app --reload --host 0.0.0.0 --port 8000
3. 访问文档：http://localhost:8000/docs
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
