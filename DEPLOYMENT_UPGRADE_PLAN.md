# 🚀 WordStyle 公网部署升级方案 v3.0

## 📋 方案概述

本方案基于当前项目的完整技术路线，提供从本地开发环境到公网部署的**一站式升级路径**。

### 架构对比

| 组件 | 当前状态（本地） | 目标状态（公网） |
|------|----------------|----------------|
| 前端 | Streamlit (localhost:8501) | Streamlit Cloud (公网HTTPS) |
| 管理后台 | Streamlit (localhost:8503) | Streamlit Cloud (独立应用) |
| 后端 | FastAPI (localhost:8000) | Render/Railway (公网API) |
| 数据库 | SQLite (本地文件) | Supabase PostgreSQL (云端) |
| 文件存储 | 本地目录 | Supabase Storage (云端) |
| 缓存 | 内存缓存 | Redis (可选，付费升级) |

---

## ⚠️ 重要提示

### 采用"清空重建"策略的原因
1. **避免配置冲突**: 旧的环境变量、数据库连接可能干扰新部署
2. **确保数据一致性**: 从SQLite迁移到PostgreSQL需要重新初始化
3. **简化流程**: 直接创建新环境比迁移更可靠
4. **成本可控**: 当前用户数据量小，重建成本低

### 执行前确认清单
- [ ] 已备份本地重要数据（user_data.json, comments_data.json）
- [ ] 已记录当前的系统配置参数
- [ ] 准备好GitHub账号（代码托管）
- [ ] 准备好邮箱（接收服务通知）
- [ ] 预计耗时：**2-3小时**（首次部署）

---

## 📦 第一步：准备工作（30分钟）

### 1.1 注册必需的外部服务

#### A. Supabase（数据库 + 文件存储）⭐ 核心服务

**为什么选择Supabase？**
- ✅ 免费额度充足（500MB数据库 + 1GB存储）
- ✅ 自带PostgreSQL + 文件存储 + 身份验证
- ✅ 自动备份，无需运维
- ✅ 全球CDN加速

**注册步骤：**
1. 访问 https://supabase.com
2. 点击 **"Start your project"** → 使用 **GitHub** 登录
3. 点击 **"New project"**
4. 填写信息：
   ```
   Project name: wordstyle
   Database Password: [设置强密码，务必保存！]
   Region: Singapore（离中国最近，延迟最低）
   ```
5. 点击 **"Create new project"**
6. 等待1-2分钟初始化完成

**获取关键信息：**
1. 左侧菜单 → **Settings** → **Database**
2. 找到 "Connection string" → 选择 **URI** 标签
3. 复制连接字符串，格式如下：
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
4. 左侧菜单 → **Settings** → **API**
5. 复制以下两项：
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbG...`（以eyJ开头的长字符串）

**⚠️ 安全提醒：**
- 数据库密码请妥善保存（建议使用密码管理器）
- API Key不要提交到Git仓库

---

#### B. Render（后端部署）⭐ 核心服务

**为什么选择Render？**
- ✅ 免费套餐750小时/月（足够单应用运行）
- ✅ 自动HTTPS证书
- ✅ 支持Docker部署
- ✅ 与GitHub集成，自动CI/CD

**注册步骤：**
1. 访问 https://render.com
2. 点击 **"Get Started for Free"**
3. 使用 **GitHub** 登录
4. 授权访问你的代码仓库

---

#### C. Streamlit Cloud（前端部署）⭐ 核心服务

**为什么选择Streamlit Cloud？**
- ✅ 专为Streamlit优化，零配置
- ✅ 每月1000小时免费额度
- ✅ 自动HTTPS
- ✅ 与GitHub无缝集成

**注册步骤：**
1. 访问 https://share.streamlit.io
2. 点击 **"Sign up with GitHub"**
3. 授权访问你的代码仓库

---

#### D. UptimeRobot（保持活跃，可选但推荐）

**为什么需要UptimeRobot？**
- Render免费版15分钟无请求会休眠
- UptimeRobot每5分钟ping一次，保持服务活跃
- 完全免费

**注册步骤：**
1. 访问 https://uptimerobot.com
2. 点击 **"Sign Up Free"**
3. 使用邮箱注册
4. 后续部署完成后配置监控

---

### 1.2 初始化Supabase数据库

#### A. 创建数据库表结构

1. Supabase控制台 → 左侧菜单 → **SQL Editor**
2. 点击 **"New query"**
3. 复制以下完整SQL脚本并执行：

```sql
-- ============================================
-- WordStyle 数据库初始化脚本 v3.0
-- ============================================

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wechat_openid VARCHAR(128) UNIQUE,
    wechat_nickname VARCHAR(100),
    wechat_avatar VARCHAR(500),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100),
    password_hash VARCHAR(255),
    balance FLOAT DEFAULT 0.0,
    paragraphs_remaining INTEGER DEFAULT 10000,
    total_converted INTEGER DEFAULT 0,
    total_paragraphs_used INTEGER DEFAULT 0,
    last_free_quota_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE users IS '用户信息表';
COMMENT ON COLUMN users.wechat_openid IS '微信OpenID（唯一标识）';
COMMENT ON COLUMN users.balance IS '账户余额（元）';
COMMENT ON COLUMN users.paragraphs_remaining IS '剩余可用段落数';

-- ============================================
-- 2. 充值订单表
-- ============================================
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_no VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    paragraphs INTEGER NOT NULL,
    package_label VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING',
    payment_method VARCHAR(20),
    transaction_id VARCHAR(128),
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE orders IS '充值订单表';
COMMENT ON COLUMN orders.status IS '订单状态：PENDING/PAID/FAILED/REFUNDED';
COMMENT ON COLUMN orders.payment_method IS '支付方式：WECHAT/ALIPAY';

-- ============================================
-- 3. 转换任务表
-- ============================================
CREATE TABLE conversion_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255),
    paragraphs INTEGER,
    cost FLOAT,
    status VARCHAR(20) DEFAULT 'PENDING',
    progress INTEGER DEFAULT 0,
    output_files TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE conversion_tasks IS '文档转换任务表';
COMMENT ON COLUMN conversion_tasks.status IS '任务状态：PENDING/PROCESSING/COMPLETED/FAILED';
COMMENT ON COLUMN conversion_tasks.output_files IS '输出文件路径（JSON格式）';

-- ============================================
-- 4. 系统配置表
-- ============================================
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE system_config IS '系统配置表（动态配置）';

-- 插入默认配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('free_paragraphs_daily', '10000', '每日免费段落数'),
('min_recharge_amount', '1.0', '最低充值金额(元)'),
('paragraph_price', '0.001', '每段落价格(元)'),
('admin_contact', '微信号：your_wechat_id', '管理员联系方式');

-- ============================================
-- 5. 评论表
-- ============================================
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50),
    username VARCHAR(100),
    content TEXT NOT NULL,
    rating INTEGER DEFAULT 5,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE comments IS '用户评论表';

-- ============================================
-- 6. 反馈表
-- ============================================
CREATE TABLE feedbacks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50),
    feedback_type VARCHAR(20),
    title VARCHAR(200),
    description TEXT,
    contact VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    reply TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE feedbacks IS '用户反馈表';
COMMENT ON COLUMN feedbacks.status IS '反馈状态：pending/processing/resolved';

-- ============================================
-- 7. 样式映射表
-- ============================================
CREATE TABLE style_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    source_style VARCHAR(255) NOT NULL,
    target_style VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, filename, source_style)
);

COMMENT ON TABLE style_mappings IS '用户自定义样式映射表';

-- ============================================
-- 创建索引（提升查询性能）
-- ============================================
CREATE INDEX idx_users_wechat_openid ON users(wechat_openid);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_tasks_user_id ON conversion_tasks(user_id);
CREATE INDEX idx_tasks_task_id ON conversion_tasks(task_id);
CREATE INDEX idx_tasks_status ON conversion_tasks(status);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_feedbacks_user_id ON feedbacks(user_id);
CREATE INDEX idx_style_mappings_user_id ON style_mappings(user_id);

-- ============================================
-- 验证初始化结果
-- ============================================
SELECT 'Tables created successfully' AS status;
SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = 'public';
SELECT COUNT(*) AS config_count FROM system_config;
```

4. 点击右下角 **"Run"** 按钮
5. 看到 "Success. No rows returned" 表示成功
6. 验证：应该看到 `table_count = 7`, `config_count = 4`

---

#### B. 创建文件存储Bucket

1. Supabase控制台 → 左侧菜单 → **Storage**
2. 点击 **"New bucket"**
3. 填写：
   ```
   Name: conversion-results
   Public bucket: ✅ 勾选（允许公开访问）
   File size limit: 50 MB
   Allowed MIME types: application/vnd.openxmlformats-officedocument.wordprocessingml.document
   ```
4. 点击 **"Create bucket"**

**验证：**
- 在Storage页面应该能看到 `conversion-results` bucket

---

### 1.3 备份本地数据（可选）

如果本地有重要测试数据，执行备份：

```bash
# 在项目根目录执行
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp data/user_data.json backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "No user data to backup"
cp data/comments_data.json backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "No comments data to backup"
echo "Backup completed!"
```

**注意：** 公网部署后会使用云端数据库，本地JSON文件不再使用。

---

## 🔧 第二步：更新项目配置（1小时）

### 2.1 创建环境变量模板

#### A. 后端环境变量

创建文件：`backend/.env.production`

```env
# ============================================
# WordStyle 后端生产环境配置
# ============================================

# 应用配置
APP_NAME=WordStyle Pro
APP_VERSION=3.0.0
DEBUG=false

# 数据库配置（替换为你的Supabase连接字符串）
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# Supabase配置
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbG...[你的anon public key]

# JWT认证配置
SECRET_KEY=[生成一个随机密钥，见下方说明]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS配置（允许Streamlit Cloud访问）
ALLOWED_ORIGINS=https://*.streamlit.app,http://localhost:8501

# 文件上传配置
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=52428800  # 50MB

# 微信支付配置（后期填写）
WECHAT_APP_ID=
WECHAT_MCH_ID=
WECHAT_API_KEY=
WECHAT_NOTIFY_URL=https://your-backend.onrender.com/api/payments/wechat/callback

# 支付宝配置（后期填写）
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=
ALIPAY_NOTIFY_URL=https://your-backend.onrender.com/api/payments/alipay/callback
```

**生成SECRET_KEY的方法：**
```bash
# Python方式
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或者访问在线生成器
# https://randomkeygen.com/CodeIgniter%20Encryption%20Key%20Generator
```

---

#### B. 前端Secrets模板

创建文件：`.streamlit/secrets.toml.template`

```toml
# ============================================
# WordStyle 前端Secrets配置模板
# 使用时复制为 .streamlit/secrets.toml 并填写实际值
# ============================================

[backend]
url = "https://wordstyle-backend.onrender.com"  # 替换为你的Render后端地址

[supabase]
url = "https://xxxxx.supabase.co"  # 替换为你的Supabase项目URL
key = "eyJhbG..."  # 替换为你的Supabase anon public key

[admin]
contact = "微信号：your_wechat_id"  # 管理员联系方式
```

---

### 2.2 更新后端依赖

检查并更新文件：`backend/requirements.txt`

```txt
# ============================================
# Web框架
# ============================================
fastapi==0.110.0
uvicorn[standard]==0.27.0

# ============================================
# 数据库
# ============================================
sqlalchemy==2.0.25
psycopg2-binary==2.9.9  # PostgreSQL驱动
alembic==1.13.1

# ============================================
# Supabase客户端
# ============================================
supabase==2.3.4

# ============================================
# 认证与安全
# ============================================
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pyjwt==2.8.0

# ============================================
# 工具库
# ============================================
python-dotenv==1.0.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# ============================================
# HTTP请求
# ============================================
requests==2.31.0
httpx==0.26.0

# ============================================
# 微信相关（可选，后期启用）
# ============================================
# wechatpy==1.8.18
# cryptography==41.0.7
```

---

### 2.3 创建数据库初始化脚本

创建文件：`backend/init_supabase.py`

```python
#!/usr/bin/env python3
"""
WordStyle Supabase数据库初始化脚本

功能：
1. 验证数据库连接
2. 检查表结构是否完整
3. 插入默认配置（如果不存在）
4. 显示初始化报告
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models import Base, SystemConfig
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_database_url():
    """获取数据库连接URL"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ 错误：未设置 DATABASE_URL 环境变量")
        print("\n请在 backend/.env.production 中配置 DATABASE_URL")
        print("格式：postgresql://postgres:password@db.xxx.supabase.co:5432/postgres")
        sys.exit(1)
    return db_url

def check_connection(db_url):
    """检查数据库连接"""
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")
        return engine
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n请检查：")
        print("1. DATABASE_URL 格式是否正确")
        print("2. 密码是否包含特殊字符（需要URL编码）")
        print("3. Supabase项目是否已创建")
        sys.exit(1)

def check_tables(engine):
    """检查表结构"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        'users', 'orders', 'conversion_tasks', 
        'system_config', 'comments', 'feedbacks', 'style_mappings'
    ]
    
    missing_tables = [t for t in required_tables if t not in tables]
    
    if missing_tables:
        print(f"⚠️  缺少表: {', '.join(missing_tables)}")
        print("\n请先执行 SQL Editor 中的初始化脚本")
        return False
    else:
        print("✅ 所有必需的表已存在")
        return True

def init_default_config(engine):
    """初始化默认配置"""
    from sqlalchemy import text
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    defaults = {
        'free_paragraphs_daily': ('10000', '每日免费段落数'),
        'min_recharge_amount': ('1.0', '最低充值金额(元)'),
        'paragraph_price': ('0.001', '每段落价格(元)'),
        'admin_contact': ('微信号：your_wechat_id', '管理员联系方式'),
    }
    
    inserted = []
    for key, (value, desc) in defaults.items():
        existing = session.query(SystemConfig).filter_by(config_key=key).first()
        if not existing:
            config = SystemConfig(
                config_key=key,
                config_value=value,
                description=desc
            )
            session.add(config)
            inserted.append(key)
    
    if inserted:
        session.commit()
        print(f"✅ 已插入默认配置: {', '.join(inserted)}")
    else:
        print("ℹ️  默认配置已存在，跳过初始化")
    
    session.close()

def show_summary(engine):
    """显示初始化摘要"""
    from sqlalchemy import text
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("\n" + "="*50)
    print("📊 数据库初始化报告")
    print("="*50)
    
    # 统计表数量
    table_count = session.execute(text(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
    )).scalar()
    print(f"表总数: {table_count}")
    
    # 统计配置数量
    config_count = session.query(SystemConfig).count()
    print(f"系统配置数: {config_count}")
    
    # 列出所有表
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n表列表: {', '.join(tables)}")
    
    print("\n✅ 数据库初始化完成！")
    print("="*50)
    
    session.close()

if __name__ == "__main__":
    print("🚀 开始初始化Supabase数据库...\n")
    
    # 1. 获取数据库URL
    db_url = get_database_url()
    print(f"📡 连接到: {db_url[:50]}...")
    
    # 2. 检查连接
    engine = check_connection(db_url)
    
    # 3. 检查表结构
    if not check_tables(engine):
        print("\n❌ 初始化失败，请先执行SQL脚本创建表结构")
        sys.exit(1)
    
    # 4. 初始化默认配置
    init_default_config(engine)
    
    # 5. 显示摘要
    show_summary(engine)
```

---

### 2.4 创建Supabase文件上传工具

创建文件：`backend/app/utils/supabase_storage.py`

```python
"""
Supabase Storage 文件上传工具
"""
import os
from supabase import create_client, Client
from typing import Optional

# 全局Supabase客户端
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """获取Supabase客户端（单例模式）"""
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL 和 SUPABASE_KEY 必须配置")
        
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client

async def upload_file_to_supabase(file_path: str, user_id: str, bucket_name: str = "conversion-results") -> str:
    """
    上传文件到Supabase Storage
    
    Args:
        file_path: 本地文件路径
        user_id: 用户ID（用于组织文件目录）
        bucket_name: Storage Bucket名称
    
    Returns:
        文件的公开访问URL
    """
    client = get_supabase_client()
    
    # 生成存储路径
    filename = os.path.basename(file_path)
    storage_path = f"{user_id}/{filename}"
    
    # 读取文件内容
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # 上传文件
    response = client.storage.from_(bucket_name).upload(
        path=storage_path,
        file=file_content,
        file_options={
            "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "cache-control": "3600",
            "upsert": "true"  # 覆盖同名文件
        }
    )
    
    # 获取公开URL
    public_url = client.storage.from_(bucket_name).get_public_url(storage_path)
    
    return public_url

async def delete_file_from_supabase(storage_path: str, bucket_name: str = "conversion-results") -> bool:
    """
    从Supabase Storage删除文件
    
    Args:
        storage_path: 存储路径（如：user_id/filename.docx）
        bucket_name: Storage Bucket名称
    
    Returns:
        是否删除成功
    """
    client = get_supabase_client()
    
    try:
        client.storage.from_(bucket_name).remove([storage_path])
        return True
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False
```

---

### 2.5 更新后端API适配Supabase

需要在现有API中添加Supabase文件上传支持。

修改文件：`backend/app/api/conversions.py`

在文件顶部添加导入：
```python
from app.utils.supabase_storage import upload_file_to_supabase
```

在转换完成后上传文件到Supabase（约第150行附近）：
```python
# 原有代码：保存到本地
output_files = converter.convert(...)

# 新增：上传到Supabase
try:
    supabase_urls = []
    for output_file in output_files:
        if os.path.exists(output_file):
            url = await upload_file_to_supabase(output_file, str(current_user.id))
            supabase_urls.append(url)
    
    # 将Supabase URL保存到任务记录
    task.output_files = json.dumps({
        'local_paths': output_files,
        'supabase_urls': supabase_urls
    })
except Exception as e:
    print(f"上传到Supabase失败: {e}")
    # 即使上传失败，也保留本地路径
    task.output_files = json.dumps({'local_paths': output_files})
```

---

### 2.6 更新前端用户管理模块

当前前端使用本地JSON文件，需要改为调用后端API。

**注意：** 这个改动较大，建议分阶段进行：
1. **第一阶段**：保持现有JSON文件方式，仅后端使用Supabase
2. **第二阶段**：前端逐步迁移到后端API

为了简化首次部署，我们采用**第一阶段方案**，即：
- 前端继续使用本地JSON（Streamlit Cloud有持久化存储）
- 后端使用Supabase数据库
- 通过定期同步保持数据一致

这样可以降低部署复杂度，后续再优化。

---

## 🚀 第三步：部署后端到Render（40分钟）

### 3.1 准备代码仓库

确保代码已推送到GitHub：

```bash
# 在项目根目录执行
git add .
git commit -m "准备公网部署：更新配置文件和初始化脚本"
git push origin main
```

**重要：** 不要提交 `.env` 文件！确认 `.gitignore` 包含：
```
.env
.env.local
.env.production
*.pem
*.key
```

---

### 3.2 在Render创建Web Service

#### A. 创建服务

1. Render控制台 → Dashboard → 点击 **"New +"**
2. 选择 **"Web Service"**
3. 选择 **"Connect a repository"**
4. 选择你的 `WordStyle` GitHub仓库
5. 点击 **"Connect"**

#### B. 配置服务参数

填写以下配置：

```
Name: wordstyle-backend
Region: Singapore（选择离你最近的区域）
Branch: main
Root Directory: backend
Runtime: Python 3
```

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

点击 **"Advanced"** 展开高级选项：

**Health Check Path:**
```
/health
```

**Environment Variables（环境变量）:**

逐个添加以下变量（点击 "Add Environment Variable"）：

| Key | Value | 说明 |
|-----|-------|------|
| `DATABASE_URL` | `postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres` | 从Supabase复制 |
| `SECRET_KEY` | `[生成的随机密钥]` | 使用python生成 |
| `ALLOWED_ORIGINS` | `https://*.streamlit.app,http://localhost:8501` | CORS配置 |
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | Supabase项目URL |
| `SUPABASE_KEY` | `eyJhbG...` | Supabase anon key |
| `DEBUG` | `false` | 生产环境关闭调试 |
| `UPLOAD_DIR` | `/tmp/uploads` | Render临时目录 |

点击 **"Create Web Service"**

---

### 3.3 等待部署完成

1. 返回 **"Logs"** 标签页
2. 查看实时日志
3. 等待看到类似输出：
   ```
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:10000
   ```
4. 大约需要3-5分钟

**常见错误排查：**

❌ **错误1: ModuleNotFoundError**
- 原因：缺少依赖
- 解决：检查 `requirements.txt` 是否包含所有包

❌ **错误2: Database connection failed**
- 原因：DATABASE_URL格式错误
- 解决：检查密码是否包含特殊字符（需要URL编码）

❌ **错误3: Port binding failed**
- 原因：端口配置错误
- 解决：确保使用 `$PORT` 环境变量

---

### 3.4 测试后端

#### A. 健康检查

浏览器访问（替换为你的实际域名）：
```
https://wordstyle-backend.onrender.com/health
```

应返回：
```json
{"status": "healthy"}
```

#### B. API文档

访问：
```
https://wordstyle-backend.onrender.com/docs
```

应该看到Swagger UI界面，列出所有API端点。

#### C. 测试数据库连接

在API文档中找到 `GET /api/admin/stats`，点击 "Try it out" → "Execute"

如果返回统计数据，说明数据库连接正常。

---

## 🌍 第四步：部署前端到Streamlit Cloud（30分钟）

### 4.1 创建Secrets配置

#### A. 主应用Secrets

创建文件：`.streamlit/secrets.toml`（如果不存在）

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"  # 替换为你的Render后端地址

[supabase]
url = "https://xxxxx.supabase.co"  # 替换为你的Supabase URL
key = "eyJhbG..."  # 替换为你的Supabase anon key

[admin]
contact = "微信号：your_wechat_id"  # 管理员联系方式
```

**⚠️ 重要：** 不要将此文件提交到Git！

添加到 `.gitignore`：
```
.streamlit/secrets.toml
```

---

#### B. 管理后台Secrets

创建文件：`.streamlit/secrets_admin.toml`

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"

[admin]
username = "admin"  # 管理员用户名
password = "your_secure_password"  # 管理员密码
```

---

### 4.2 部署主应用到Streamlit Cloud

#### A. 创建应用

1. 访问 https://share.streamlit.io
2. 点击 **"New app"**
3. 填写配置：
   ```
   Repository: 选择你的 WordStyle 仓库
   Branch: main
   Main file path: app.py
   App URL: wordstyle-app（可以自定义）
   ```
4. 点击 **"Deploy!"**

#### B. 配置Secrets

1. 部署开始后，点击左侧 **"Settings"**
2. 找到 **"Secrets"** 部分
3. 点击 **"Edit secrets"**
4. 粘贴以下内容（修改为实际值）：

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"

[supabase]
url = "https://xxxxx.supabase.co"
key = "eyJhbG..."

[admin]
contact = "微信号：your_wechat_id"
```

5. 点击 **"Save"**

#### C. 等待部署完成

1. 返回 **"Manage app"** 标签
2. 查看部署日志
3. 等待看到 "Successfully deployed!"
4. 大约需要2-3分钟

---

### 4.3 部署管理后台到Streamlit Cloud

管理后台需要作为**独立应用**部署。

#### A. 创建独立应用

1. Streamlit Cloud → 点击 **"New app"**
2. 填写配置：
   ```
   Repository: 选择你的 WordStyle 仓库
   Branch: main
   Main file path: admin_web.py
   App URL: wordstyle-admin（可以自定义）
   ```
3. 点击 **"Deploy!"**

#### B. 配置Secrets

1. Settings → Secrets → Edit secrets
2. 粘贴：

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"

[admin]
username = "admin"
password = "your_secure_password"
```

3. 点击 **"Save"**

---

## ✅ 第五步：测试与验证（30分钟）

### 5.1 访问应用

打开浏览器访问：

- **主应用**: `https://wordstyle-app.streamlit.app`
- **管理后台**: `https://wordstyle-admin.streamlit.app`
- **后端API**: `https://wordstyle-backend.onrender.com/docs`

---

### 5.2 功能测试清单

#### A. 主应用测试

- [ ] 页面正常加载
- [ ] 显示微信扫码登录按钮
- [ ] 模拟扫码后显示用户信息
- [ ] 显示免费额度（10000段）
- [ ] 上传Word文档（测试文件）
- [ ] 点击"开始转换"
- [ ] 转换进度正常显示
- [ ] 下载转换结果
- [ ] 查看转换历史
- [ ] 提交反馈
- [ ] 评论区正常显示

#### B. 管理后台测试

- [ ] 管理员登录成功
- [ ] 数据看板显示统计信息
- [ ] 用户列表正常加载
- [ ] 任务监控实时更新
- [ ] 订单列表正常显示
- [ ] 系统配置可以修改
- [ ] 反馈管理功能正常

#### C. API连接测试

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 执行操作时观察API请求
4. 确认没有CORS错误
5. 确认响应时间 < 3秒

---

### 5.3 数据持久化测试

1. 在主应用执行一次转换
2. 刷新页面（F5）
3. 确认：
   - [ ] 转换历史已保存
   - [ ] 剩余段落已扣减
   - [ ] 用户信息未丢失

---

### 5.4 压力测试（可选）

使用多个浏览器窗口同时访问，测试并发性能。

---

## 🔧 第六步：后续优化（20分钟）

### 6.1 配置UptimeRobot保持活跃

Render免费版15分钟无请求会休眠，使用UptimeRobot解决：

1. 访问 https://uptimerobot.com
2. 登录后点击 **"Add New Monitor"**
3. 填写：
   ```
   Monitor Type: HTTP(s)
   Friendly Name: WordStyle Backend
   URL: https://wordstyle-backend.onrender.com/health
   Monitoring Interval: Every 5 minutes
   ```
4. 点击 **"Create Monitor"**

这样每5分钟会自动ping一次，保持服务活跃。

---

### 6.2 监控与日志

#### A. 后端监控

- **Render Logs**: Render Dashboard → 选择服务 → Logs标签
- **API性能**: 访问 `/monitoring/metrics` 端点

#### B. 前端监控

- **Streamlit Logs**: Streamlit Dashboard → 选择应用 → Logs

#### C. 数据库监控

- **Supabase Dashboard**: 查看数据库使用情况
- **Storage Usage**: 查看文件存储用量

---

### 6.3 备份策略

#### A. 数据库备份

Supabase自动每日备份，无需手动操作。

**手动备份方法：**
1. Supabase控制台 → Database → Backups
2. 点击 "Create backup"

#### B. 文件存储备份

定期下载重要文件到本地：
```bash
# 使用Supabase CLI
supabase storage download conversion-results ./backup/
```

#### C. 代码备份

GitHub自动版本控制，确保定期push。

---

## 📊 资源与成本分析

### 免费方案（初期推荐）

| 服务 | 免费额度 | 实际使用 | 成本 |
|------|---------|---------|------|
| Streamlit Cloud | 1000小时/月 | ~720小时（2个应用） | ¥0 |
| Render | 750小时/月 | ~720小时（配合UptimeRobot） | ¥0 |
| Supabase | 500MB数据库 + 1GB存储 | 初期<100MB | ¥0 |
| UptimeRobot | 50个监控 | 1个监控 | ¥0 |
| **总计** | | | **¥0/月** |

**适用场景：**
- MVP验证阶段
- 日活跃用户 < 100
- 月转换次数 < 1000

---

### 付费方案（用户增长后）

当免费额度不足时，考虑升级：

| 服务 | 升级方案 | 成本 | 触发条件 |
|------|---------|------|---------|
| Render | Starter ($7/月) | ~¥50/月 | 需要更多运行时长 |
| Supabase | Pro ($25/月) | ~¥180/月 | 数据库超过500MB |
| Redis | Upstash ($10/月) | ~¥70/月 | 需要缓存加速 |
| **总计** | | **~¥300/月** | |

**升级建议：**
- 先升级Render（最影响用户体验）
- 其次升级Supabase（数据存储瓶颈）
- Redis可选（性能优化）

---

## 🆘 故障排查手册

### 问题1：后端部署失败

**症状：** Render Logs显示错误

**排查步骤：**

1. **检查依赖安装**
   ```
   查看日志中是否有 "Successfully installed" 
   如果没有，检查 requirements.txt 格式
   ```

2. **检查环境变量**
   ```
   确认所有必需变量已配置
   特别检查 DATABASE_URL 格式
   ```

3. **检查数据库连接**
   ```
   在Render Logs中搜索 "database"
   如果有连接错误，检查密码是否正确
   ```

4. **检查端口绑定**
   ```
   确认 Start Command 使用 $PORT
   不要硬编码端口号
   ```

**解决方案：**
- 修复错误后，点击 "Manual Deploy" 重新部署

---

### 问题2：前端无法连接后端

**症状：** 页面显示连接错误或CORS错误

**排查步骤：**

1. **检查secrets.toml**
   ```toml
   [backend]
   url = "https://wordstyle-backend.onrender.com"  # 确认URL正确
   ```

2. **检查后端CORS配置**
   ```
   后端环境变量 ALLOWED_ORIGINS 必须包含：
   https://*.streamlit.app
   ```

3. **检查浏览器控制台**
   ```
   F12 → Console 标签
   查看是否有 CORS 错误
   ```

4. **测试后端可达性**
   ```
   浏览器访问：https://wordstyle-backend.onrender.com/health
   应该返回 {"status":"healthy"}
   ```

**解决方案：**
- 修正secrets.toml后，在Streamlit Cloud点击 "Redeploy"

---

### 问题3：数据库连接失败

**症状：** 后端日志显示 "connection refused" 或 "authentication failed"

**排查步骤：**

1. **验证DATABASE_URL格式**
   ```
   postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres
   ```

2. **检查密码特殊字符**
   ```
   如果密码包含 @ : / 等字符，需要URL编码
   例如：@ 编码为 %40
   ```

3. **测试本地连接**
   ```bash
   # 安装psql客户端
   psql "postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres"
   ```

4. **检查Supabase项目状态**
   ```
   Supabase控制台 → 确认项目处于 "Active" 状态
   ```

**解决方案：**
- 修正DATABASE_URL后，在Render点击 "Manual Deploy"

---

### 问题4：文件上传/下载失败

**症状：** 转换后无法下载文件

**排查步骤：**

1. **检查Supabase Storage Bucket**
   ```
   Supabase控制台 → Storage
   确认 conversion-results bucket 已创建
   确认 Public bucket 已勾选
   ```

2. **检查文件权限**
   ```
   Bucket → Policies
   确认有 "Public read access" 策略
   ```

3. **检查文件大小**
   ```
   确认文件 < 50MB
   检查 MAX_FILE_SIZE 配置
   ```

4. **查看Supabase Logs**
   ```
   Supabase控制台 → Logs
   搜索 "storage" 相关错误
   ```

**解决方案：**
- 创建Bucket或修正权限后重试

---

### 问题5：Streamlit应用启动失败

**症状：** Streamlit Cloud显示 "Error starting app"

**排查步骤：**

1. **检查依赖**
   ```
   确认 requirements.txt 或 requirements_web.txt 包含所有依赖
   ```

2. **检查入口文件**
   ```
   确认 Main file path 正确（app.py 或 admin_web.py）
   ```

3. **检查Secrets格式**
   ```
   确认 secrets.toml 格式正确（TOML语法）
   ```

4. **查看部署日志**
   ```
   Streamlit Dashboard → Logs
   查看详细错误信息
   ```

**解决方案：**
- 修复错误后，点击 "Redeploy"

---

## 📝 最终检查清单

### 准备阶段
- [ ] 已注册Supabase账号并创建项目
- [ ] 已执行数据库初始化SQL脚本
- [ ] 已创建Storage Bucket（conversion-results）
- [ ] 已获取Supabase URL和API Key
- [ ] 已注册Render账号
- [ ] 已注册Streamlit Cloud账号
- [ ] 已注册UptimeRobot账号（可选）
- [ ] 已备份本地重要数据

### 后端部署
- [ ] 已创建 backend/.env.production 配置文件
- [ ] 已生成SECRET_KEY并配置
- [ ] 已配置DATABASE_URL（Supabase连接字符串）
- [ ] 已配置SUPABASE_URL和SUPABASE_KEY
- [ ] 已配置ALLOWED_ORIGINS包含streamlit.app
- [ ] 代码已推送到GitHub
- [ ] 已在Render创建Web Service
- [ ] 已配置所有环境变量
- [ ] 后端健康检查通过（/health返回healthy）
- [ ] API文档可访问（/docs）

### 前端部署
- [ ] 已创建 .streamlit/secrets.toml
- [ ] 已配置backend.url为Render后端地址
- [ ] 已配置supabase.url和supabase.key
- [ ] .streamlit/secrets.toml 已加入 .gitignore
- [ ] 主应用（app.py）已部署到Streamlit Cloud
- [ ] 管理后台（admin_web.py）已部署到Streamlit Cloud
- [ ] 两个应用都已配置Secrets
- [ ] 主应用可正常访问
- [ ] 管理后台可正常访问

### 功能测试
- [ ] 微信扫码登录功能正常
- [ ] 免费额度正常发放（10000段）
- [ ] 文件上传功能正常
- [ ] 文档转换功能正常
- [ ] 转换进度显示正常
- [ ] 文件下载功能正常
- [ ] 转换历史记录正常
- [ ] 用户余额扣减正常
- [ ] 管理后台数据统计正常
- [ ] 评论区功能正常
- [ ] 反馈提交功能正常

### 性能测试
- [ ] 页面加载时间 < 3秒
- [ ] API响应时间 < 2秒
- [ ] 转换任务提交后立即返回
- [ ] 多用户并发访问无异常

### 优化配置
- [ ] 已配置UptimeRobot监控后端
- [ ] 已测试UptimeRobot ping成功
- [ ] 已记录所有服务的登录信息
- [ ] 已保存所有API Key和密码

---

## 🎉 部署完成！

恭喜！您的WordStyle应用已成功部署到公网，任何人都可以访问了。

### 应用地址

- **主应用**：`https://wordstyle-app.streamlit.app`
- **管理后台**：`https://wordstyle-admin.streamlit.app`
- **后端API**：`https://wordstyle-backend.onrender.com`
- **API文档**：`https://wordstyle-backend.onrender.com/docs`

### 下一步行动

**立即执行：**
1. 分享给朋友试用，收集反馈
2. 监控服务运行状态（每天检查一次）
3. 记录用户使用情况

**一周内：**
1. 修复发现的Bug
2. 优化用户体验
3. 根据反馈调整功能

**一个月内：**
1. 评估是否需要升级到付费方案
2. 集成真实的微信支付/支付宝
3. 添加更多高级功能

---

## 📞 获取帮助

### 官方文档
- **Supabase**: https://supabase.com/docs
- **Render**: https://render.com/docs
- **Streamlit**: https://docs.streamlit.io

### 项目文档
- **README.md**: 项目总体说明
- **DEPLOYMENT_GUIDE.md**: 详细部署指南
- **PUBLIC_DEPLOYMENT_GUIDE.md**: 公网部署指南（旧版）

### 社区支持
- **GitHub Issues**: 提交问题和Bug报告
- **Stack Overflow**: 技术问题搜索

---

**最后更新**: 2026-05-09  
**版本**: v3.0  
**基于**: Streamlit + FastAPI + Supabase + Render  
**维护者**: WordStyle Team

---

## 📌 附录：常用命令速查

### 本地开发

```bash
# 启动后端
cd backend
python run_dev.py

# 启动主应用
streamlit run app.py

# 启动管理后台
streamlit run admin_web.py

# 初始化Supabase数据库
cd backend
python init_supabase.py
```

### Git操作

```bash
# 提交更改
git add .
git commit -m "描述性提交信息"
git push origin main

# 查看状态
git status
git log --oneline
```

### 部署检查

```bash
# 测试后端健康检查
curl https://wordstyle-backend.onrender.com/health

# 测试API文档
curl https://wordstyle-backend.onrender.com/docs

# 检查环境变量（Render控制台）
# 手动在Dashboard查看
```

---

**祝您部署顺利！** 🚀
