# 🚀 WordStyle 公网部署升级方案 v2.0

## 📋 方案概述

本方案基于当前项目的技术路线，提供从本地开发环境到公网部署的完整升级路径。

### 当前架构 vs 目标架构

| 组件 | 当前状态 | 目标状态 |
|------|---------|---------|
| 前端 | Streamlit (本地) | Streamlit Cloud (公网) |
| 后端 | FastAPI (本地) | Render/ Railway (公网) |
| 数据库 | SQLite + JSON | Supabase PostgreSQL |
| 文件存储 | 本地文件系统 | Supabase Storage |

---

## ️ 重要提示

**本方案采用"清空重建"策略，原因：**
1. 避免旧配置冲突
2. 确保数据结构一致性
3. 简化迁移流程
4. 当前用户数据量小，迁移成本低

**执行前请确认：**
- [ ] 已备份重要数据（用户数据、评论数据）
- [ ] 已记录当前的配置参数
- [ ] 准备好所需的外部服务账号

---

## 📦 第一步：准备工作（30分钟）

### 1.1 注册外部服务账号

#### A. Supabase (数据库 + 文件存储)
1. 访问 https://supabase.com
2. 使用 GitHub 账号登录
3. 点击 **New Project**
4. 填写：
   - **Project name**: `wordstyle`
   - **Database Password**: 设置强密码（**务必保存！**）
   - **Region**: `Singapore`（离中国最近）
5. 等待1-2分钟初始化

#### B. Render (后端部署)
1. 访问 https://render.com
2. 使用 GitHub 账号登录
3. 授权访问你的代码仓库

#### C. Streamlit Cloud (前端部署)
1. 访问 https://share.streamlit.io
2. 使用 GitHub 账号登录

---

### 1.2 初始化 Supabase 数据库

#### A. 获取数据库连接信息
1. 左侧菜单 → **Settings** → **Database**
2. 找到 "Connection string" → 选择 **URI** 标签
3. 复制连接字符串，格式如下：
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

#### B. 创建数据库表结构

1. 左侧菜单 → **SQL Editor** → **New query**
2. 复制以下 SQL 脚本：

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) UNIQUE NOT NULL,
    balance FLOAT DEFAULT 0.0,
    paragraphs_remaining INTEGER DEFAULT 10000,
    total_converted INTEGER DEFAULT 0,
    total_paragraphs_used INTEGER DEFAULT 0,
    last_free_quota_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 充值历史表
CREATE TABLE recharge_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    amount FLOAT NOT NULL,
    paragraphs INTEGER NOT NULL,
    package_label VARCHAR(100),
    payment_method VARCHAR(20),
    transaction_id VARCHAR(128),
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 转换历史表
CREATE TABLE conversion_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255),
    paragraphs_charged INTEGER,
    cost FLOAT,
    success BOOLEAN DEFAULT TRUE,
    mode VARCHAR(20),
    output_file_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 评论表
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50),
    username VARCHAR(100),
    content TEXT NOT NULL,
    rating INTEGER DEFAULT 5,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 反馈表
CREATE TABLE feedbacks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50),
    feedback_type VARCHAR(20),
    title VARCHAR(200),
    description TEXT,
    contact VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 系统配置表
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 样式映射表
CREATE TABLE style_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    source_style VARCHAR(255) NOT NULL,
    target_style VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, filename, source_style)
);

-- 转换任务表（后台任务）
CREATE TABLE conversion_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(50) NOT NULL,
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

-- 插入默认配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('free_paragraphs_daily', '10000', '每日免费段落数'),
('min_recharge_amount', '1.0', '最低充值金额(元)'),
('paragraph_price', '0.001', '每段落价格(元)'),
('admin_contact', '微信号：your_wechat_id', '管理员联系方式');

-- 创建索引
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_recharge_user_id ON recharge_history(user_id);
CREATE INDEX idx_conversion_user_id ON conversion_history(user_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_feedbacks_user_id ON feedbacks(user_id);
CREATE INDEX idx_style_mappings_user_id ON style_mappings(user_id);
CREATE INDEX idx_tasks_user_id ON conversion_tasks(user_id);
```

3. 点击右下角 **Run** 按钮
4. 看到 "Success" 表示成功

#### C. 创建文件存储 Bucket
1. 左侧菜单 → **Storage** → **New bucket**
2. 填写：
   - **Name**: `conversion-results`
   - **Public bucket**: ✅ 勾选
3. 点击 **Create bucket**

#### D. 获取 Supabase API Key
1. 左侧菜单 → **Settings** → **API**
2. 复制 **anon public** 密钥（以 `eyJ` 开头）
3. 复制 **Project URL**（以 `https://` 开头，以 `.supabase.co` 结尾）

---

### 1.3 备份本地数据

创建备份脚本，保留重要的用户数据：

```bash
# 在项目根目录执行
mkdir -p backup_$(date +%Y%m%d)
cp user_data.json backup_$(date +%Y%m%d)/
cp comments_data.json backup_$(date +%Y%m%d)/
cp conversion_tasks.db backup_$(date +%Y%m%d)/
cp config.py backup_$(date +%Y%m%d)/
```

---

## 🔧 第二步：后端升级（2小时）

### 2.1 更新后端数据库适配

当前后端已支持 PostgreSQL，需要适配 Supabase。

#### A. 更新 backend/.env 文件

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# 安全配置
SECRET_KEY=your_random_secret_key_here

# CORS配置
ALLOWED_ORIGINS=https://*.streamlit.app,http://localhost:8501

# Supabase配置
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# 调试模式
DEBUG=false
```

#### B. 创建数据库初始化脚本

文件：`backend/init_supabase.py`

```python
#!/usr/bin/env python3
"""
初始化 Supabase 数据库表结构
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ 错误：未设置 DATABASE_URL 环境变量")
    exit(1)

# 创建引擎
engine = create_engine(DATABASE_URL)

# 创建所有表
print("正在创建数据库表...")
Base.metadata.create_all(engine)
print("✅ 数据库表创建成功！")

# 插入默认配置
from app.models import SystemConfig
from sqlalchemy.orm import Session

with Session(engine) as session:
    # 检查是否已有配置
    existing = session.query(SystemConfig).first()
    if not existing:
        defaults = [
            SystemConfig(config_key='free_paragraphs_daily', config_value='10000', description='每日免费段落数'),
            SystemConfig(config_key='min_recharge_amount', config_value='1.0', description='最低充值金额'),
            SystemConfig(config_key='paragraph_price', config_value='0.001', description='每段落价格'),
            SystemConfig(config_key='admin_contact', config_value='微信号：your_wechat_id', description='管理员联系方式'),
        ]
        session.add_all(defaults)
        session.commit()
        print("✅ 默认配置已插入！")
    else:
        print("️  配置已存在，跳过初始化")
```

#### C. 更新后端 API 支持 Supabase 文件存储

需要在 `backend/app/api/files.py` 中添加 Supabase 上传功能：

```python
from supabase import create_client, Client

# 初始化 Supabase 客户端
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

async def upload_file_to_supabase(file_path: str, user_id: str) -> str:
    """上传文件到 Supabase Storage"""
    filename = os.path.basename(file_path)
    storage_path = f"{user_id}/{filename}"
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    response = supabase.storage.from_('conversion-results').upload(
        path=storage_path,
        file=file_content,
        file_options={"content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    )
    
    # 获取公开URL
    public_url = supabase.storage.from_('conversion-results').get_public_url(storage_path)
    return public_url
```

---

### 2.2 更新后端依赖

文件：`backend/requirements.txt`

```txt
# Web框架
fastapi==0.110.0
uvicorn[standard]==0.27.0

# 数据库
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Supabase
supabase==2.3.4

# 工具
python-dotenv==1.0.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0

# 微信相关（如需要）
wechatpy==1.8.18
cryptography==41.0.7

# 其他
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

---

### 2.3 测试后端

```bash
# 进入backend目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_supabase.py

# 启动后端服务
python run_dev.py

# 测试健康检查
curl http://localhost:8000/health

# 访问API文档
# 浏览器打开：http://localhost:8000/docs
```

---

##  第三步：前端适配（1小时）

### 3.1 更新前端用户数据管理

当前前端使用本地JSON文件，需要改为调用后端API。

#### A. 更新 user_manager.py

文件：`user_manager.py`

```python
"""
用户管理模块 - 适配后端API版本
"""
import requests
import os
from datetime import datetime
from config import BACKEND_URL

class UserManager:
    """用户管理类（通过后端API操作）"""
    
    def __init__(self):
        self.backend_url = BACKEND_URL
    
    def get_user_data(self, user_id: str) -> dict:
        """获取用户数据"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/users/{user_id}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return self._get_default_user_data(user_id)
        except:
            return self._get_default_user_data(user_id)
    
    def save_user_data(self, user_data: dict) -> bool:
        """保存用户数据"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/users/update",
                json=user_data,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def deduct_paragraphs(self, user_id: str, paragraphs: int) -> bool:
        """扣除段落数"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/users/deduct",
                json={"user_id": user_id, "paragraphs": paragraphs},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def add_conversion_record(self, user_id: str, record: dict) -> bool:
        """添加转换记录"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/conversions/add",
                json={"user_id": user_id, **record},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def _get_default_user_data(self, user_id: str) -> dict:
        """获取默认用户数据"""
        return {
            'user_id': user_id,
            'balance': 0.0,
            'paragraphs_remaining': 10000,
            'total_converted': 0,
            'total_paragraphs_used': 0,
            'last_free_quota_date': None,
            'conversion_history': []
        }

# 全局实例
user_manager = UserManager()

# 保持向后兼容的函数接口
def load_user_data(user_id: str = None) -> dict:
    """加载用户数据（兼容旧接口）"""
    if user_id is None:
        import streamlit as st
        user_id = st.session_state.user_id
    return user_manager.get_user_data(user_id)

def save_user_data(user_data: dict) -> bool:
    """保存用户数据（兼容旧接口）"""
    return user_manager.save_user_data(user_data)

def deduct_paragraphs(paragraphs: int, user_id: str = None) -> bool:
    """扣除段落数（兼容旧接口）"""
    if user_id is None:
        import streamlit as st
        user_id = st.session_state.user_id
    return user_manager.deduct_paragraphs(user_id, paragraphs)

def add_conversion_record(user_id: str = None, **kwargs) -> bool:
    """添加转换记录（兼容旧接口）"""
    if user_id is None:
        import streamlit as st
        user_id = st.session_state.user_id
    return user_manager.add_conversion_record(user_id, kwargs)

def claim_free_paragraphs(user_id: str = None) -> int:
    """领取每日免费额度"""
    if user_id is None:
        import streamlit as st
        user_id = st.session_state.user_id
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/users/claim-free",
            json={"user_id": user_id},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('paragraphs_added', 0)
        return 0
    except:
        return 0
```

#### B. 更新 app.py 中的相关导入

在 `app.py` 第 55-59 行，确认导入已更新：

```python
# 导入用户管理
from user_manager import (
    load_user_data, save_user_data, claim_free_paragraphs,
    deduct_paragraphs, add_conversion_record
)
```

---

### 3.2 更新文件下载功能

前端需要从 Supabase 下载转换后的文件，而不是本地文件。

```python
# 在 app.py 的下载部分（约第1470行）
for output_file in output_files:
    if os.path.exists(output_file):
        with open(output_file, 'rb') as f:
            file_name = os.path.basename(output_file)
            st.download_button(
                label=f"📥 下载: {file_name}",
                data=f.read(),
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        # 上传到Supabase（后台任务）
        try:
            upload_file_to_supabase(output_file, st.session_state.user_id)
        except:
            pass
```

---

### 3.3 配置前端环境变量

创建 `.streamlit/secrets.toml` 文件：

```toml
[backend]
url = "https://your-backend.onrender.com"

[supabase]
url = "https://xxxxx.supabase.co"
key = "your_supabase_anon_key"
```

---

## 🚀 第四步：部署后端到 Render（30分钟）

### 4.1 推送代码到 GitHub

```bash
# 确保所有更改已提交
git add .
git commit -m "升级到Supabase数据库，准备公网部署"
git push origin main
```

### 4.2 在 Render 创建 Web Service

1. 访问 https://render.com
2. Dashboard → **New +** → **Web Service**
3. 选择 **Connect a repository**
4. 选择你的 `WordStyle` 仓库
5. 配置服务：

```
Name: wordstyle-backend
Region: Singapore
Branch: main
Root Directory: backend
Runtime: Python 3
```

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. 点击 **Advanced** 添加环境变量：

```
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=https://*.streamlit.app
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_key
DEBUG=false
```

7. 点击 **Create Web Service**

### 4.3 等待部署完成

查看 Logs 标签，等待看到：
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:10000
```

### 4.4 测试后端

访问：`https://wordstyle-backend.onrender.com/health`

应返回：`{"status":"healthy"}`

---

## 🌍 第五步：部署前端到 Streamlit Cloud（20分钟）

### 5.1 在 Streamlit Cloud 创建应用

1. 访问 https://share.streamlit.io
2. 点击 **New app**
3. 填写：
   - **Repository**: 选择你的 `WordStyle` 仓库
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: `wordstyle-app`（自定义）
4. 点击 **Deploy!**

### 5.2 配置 Secrets

1. 部署完成后，点击左侧 **Settings**
2. 找到 **Secrets** → **Edit secrets**
3. 粘贴：

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"

[supabase]
url = "https://xxxxx.supabase.co"
key = "your_supabase_anon_key"
```

4. 点击 **Save**

### 5.3 等待部署完成

查看部署日志，等待看到 "Successfully deployed!"

---

## ✅ 第六步：测试与验证（30分钟）

### 6.1 访问应用

打开浏览器访问：`https://wordstyle-app.streamlit.app`

### 6.2 功能测试清单

- [ ] 页面正常加载
- [ ] 显示用户信息（剩余段落、累计转换）
- [ ] 每日免费额度正常发放
- [ ] 上传 Word 文档
- [ ] 开始转换
- [ ] 转换进度正常显示
- [ ] 下载转换结果
- [ ] 查看转换历史
- [ ] 提交反馈
- [ ] 评论区正常显示

### 6.3 API 连接测试

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 执行操作时观察 API 请求
4. 确认没有 CORS 错误

### 6.4 数据持久化测试

1. 执行一次转换
2. 刷新页面
3. 确认转换历史已保存
4. 确认剩余段落已扣减

---

##  第七步：后续优化

### 7.1 保持 Render 活跃

Render 免费版15分钟无请求会休眠，使用 UptimeRobot 保持活跃：

1. 访问 https://uptimerobot.com
2. 注册账号
3. 添加 Monitor：
   - **URL**: `https://wordstyle-backend.onrender.com/health`
   - **Interval**: Every 5 minutes

### 7.2 监控与日志

- **后端日志**: Render Dashboard → Logs
- **前端日志**: Streamlit Dashboard → Logs
- **数据库**: Supabase Dashboard → Logs
- **API 监控**: 使用 Sentry 或 Logtail

### 7.3 备份策略

- **数据库**: Supabase 自动每日备份
- **文件存储**: Supabase Storage 支持版本控制
- **代码**: GitHub 自动版本控制

---

## 📊 资源与成本

### 免费方案（初期）

| 服务 | 免费额度 | 成本 |
|------|---------|------|
| Streamlit Cloud | 1000小时/月 | ¥0 |
| Render | 750小时/月 | ¥0 |
| Supabase | 500MB数据库 + 1GB存储 | ¥0 |
| **总计** | | **¥0/月** |

### 付费方案（用户增长后）

| 服务 | 升级方案 | 成本 |
|------|---------|------|
| Render | Starter ($7/月) | ~¥50/月 |
| Supabase | Pro ($25/月) | ~¥180/月 |
| **总计** | | **~¥230/月** |

---

## 🆘 故障排查

### 问题1：后端部署失败

**症状**: Render Logs 显示错误

**解决**:
1. 检查 DATABASE_URL 格式是否正确
2. 确认 requirements.txt 包含所有依赖
3. 查看详细错误日志

### 问题2：前端无法连接后端

**症状**: 页面显示连接错误

**解决**:
1. 检查 secrets.toml 中的 URL 是否正确
2. 确认后端 ALLOWED_ORIGINS 包含 streamlit.app
3. 查看浏览器控制台是否有 CORS 错误

### 问题3：数据库连接失败

**症状**: 后端日志显示数据库连接错误

**解决**:
1. 确认 Supabase 项目已创建
2. 检查密码是否正确（注意特殊字符）
3. 确认 SQL 脚本已成功执行

### 问题4：文件上传失败

**症状**: 转换后无法下载文件

**解决**:
1. 检查 Supabase Storage Bucket 是否创建
2. 确认 Bucket 权限设置为 Public
3. 查看 Supabase Storage 日志

---

## 📝 部署检查清单

### 准备阶段
- [ ] 已注册 Supabase 账号
- [ ] 已创建 Supabase 项目
- [ ] 已执行数据库初始化 SQL
- [ ] 已创建 Storage Bucket
- [ ] 已获取 Supabase API Key
- [ ] 已注册 Render 账号
- [ ] 已注册 Streamlit Cloud 账号
- [ ] 已备份本地数据

### 后端部署
- [ ] 已更新 backend/.env 配置
- [ ] 已更新 requirements.txt
- [ ] 已推送代码到 GitHub
- [ ] 已在 Render 创建 Web Service
- [ ] 已配置环境变量
- [ ] 后端健康检查通过

### 前端部署
- [ ] 已更新 user_manager.py
- [ ] 已创建 .streamlit/secrets.toml
- [ ] 已在 Streamlit Cloud 创建应用
- [ ] 已配置 Secrets
- [ ] 前端应用正常运行

### 测试验证
- [ ] 页面正常加载
- [ ] 用户数据正常显示
- [ ] 免费额度正常发放
- [ ] 文件上传正常
- [ ] 转换功能正常
- [ ] 数据持久化正常
- [ ] 文件下载正常

### 优化配置
- [ ] 已配置 UptimeRobot
- [ ] 已设置监控告警
- [ ] 已配置日志收集

---

## 🎉 完成！

恭喜！您的 WordStyle 应用已成功部署到公网，任何人都可以访问了。

**应用地址：**
- 前端：`https://wordstyle-app.streamlit.app`
- 后端 API：`https://wordstyle-backend.onrender.com`
- API 文档：`https://wordstyle-backend.onrender.com/docs`

---

**最后更新**: 2026-05-09
**版本**: v2.0
**基于**: 当前项目技术路线（Streamlit + FastAPI + Supabase）
