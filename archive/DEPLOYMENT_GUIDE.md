# WordStyle 公网部署完整指南

## 📊 方案对比

| 方案 | 月成本 | 复杂度 | 适用场景 | 推荐度 |
|------|--------|--------|----------|--------|
| **完全免费** | ¥0 | ⭐⭐ | MVP验证/个人项目 | ⭐⭐⭐⭐⭐ |
| **超低成本VPS** | ¥5-10 | ⭐⭐⭐ | 小规模商用 | ⭐⭐⭐⭐ |
| **混合云方案** | ¥0-50 | ⭐⭐⭐⭐ | 生产环境 | ⭐⭐⭐⭐⭐ |

---

## 🎯 方案一:完全免费部署(推荐)

### 架构设计

```
┌──────────────┐
│   用户浏览器   │
└──────┬───────┘
       │ HTTPS
       ↓
┌──────────────┐      ┌────────────────┐
│ Streamlit    │──────│ Render/Railway  │
│ Cloud        │ API  │ (FastAPI后端)   │
│ (前端免费)    │      │ (后端免费层)     │
└──────────────┘      └───────┬────────┘
                              │
                              ↓
                     ┌────────────────┐
                     │   Supabase     │
                     │ (PostgreSQL +  │
                     │  Storage 免费)  │
                     └────────────────┘
```

### 第一步:准备Supabase数据库(5分钟)

#### 1.1 注册Supabase
1. 访问 https://supabase.com
2. 点击"Start your project"
3. 使用GitHub账号登录
4. 创建新项目:
   - Project name: `wordstyle`
   - Database Password: 设置强密码(保存好!)
   - Region: 选择离用户最近的(如`Singapore`)

#### 1.2 获取数据库连接信息
进入项目后,点击左侧"Settings" → "Database":
```
Host: db.xxxxx.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: 你设置的密码
```

#### 1.3 初始化数据库表
进入"SQL Editor",执行以下SQL:

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wechat_openid VARCHAR(128) UNIQUE,
    wechat_nickname VARCHAR(100),
    wechat_avatar VARCHAR(500),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(100),
    password_hash VARCHAR(255),
    balance FLOAT DEFAULT 0.0,
    paragraphs_remaining INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_no VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    amount FLOAT NOT NULL,
    paragraphs INTEGER NOT NULL,
    package_label VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING',
    payment_method VARCHAR(20),
    transaction_id VARCHAR(128),
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 转换任务表
CREATE TABLE conversion_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
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

-- 系统配置表
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入默认配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('free_paragraphs_on_first_login', '10000', '新用户首次登录赠送的免费段落数'),
('min_recharge_amount', '1.0', '最低充值金额(元)'),
('paragraph_price', '0.001', '每段落价格(元)');

-- 创建索引
CREATE INDEX idx_users_wechat_openid ON users(wechat_openid);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_tasks_user_id ON conversion_tasks(user_id);
CREATE INDEX idx_tasks_task_id ON conversion_tasks(task_id);
```

#### 1.4 配置Storage(用于存储转换后的文件)
1. 左侧菜单点击"Storage"
2. 点击"New bucket"
3. Bucket name: `conversion-results`
4. Public bucket: ✅ 勾选(允许公开访问)
5. 点击"Create bucket"

---

### 第二步:部署后端到Render(10分钟)

#### 2.1 准备后端代码

在项目根目录创建 `render.yaml`:

```yaml
services:
  - type: web
    name: wordstyle-backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: wordstyle-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ALLOWED_ORIGINS
        value: "https://*.streamlit.app,https://wordstyle.onrender.com"
      - key: DEBUG
        value: "false"
```

#### 2.2 修改后端配置

编辑 `backend/app/core/config.py`:

```python
import os
from typing import List

class Settings:
    # 应用配置
    APP_NAME = "WordStyle Pro"
    APP_VERSION = "1.0.0"
    
    # 数据库配置(从环境变量读取)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wordstyle.db")
    
    # JWT配置
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # CORS配置
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    
    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # 支付配置(后续填写)
    WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
    WECHAT_MCH_ID = os.getenv("WECHAT_MCH_ID", "")
    WECHAT_API_KEY = os.getenv("WECHAT_API_KEY", "")
    
    # 文件上传配置
    UPLOAD_DIR = "/tmp/uploads"
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

settings = Settings()
```

#### 2.3 注册并部署到Render

1. 访问 https://render.com
2. 使用GitHub账号登录
3. 点击"New +" → "Web Service"
4. 连接你的GitHub仓库
5. 配置:
   - Name: `wordstyle-backend`
   - Region: `Singapore`(离中国最近)
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. 添加环境变量(在"Environment"标签页):
```
DATABASE_URL=postgresql://postgres:密码@db.xxxxx.supabase.co:5432/postgres
SECRET_KEY=生成一个随机字符串(可以用https://randomkeygen.com)
ALLOWED_ORIGINS=https://*.streamlit.app
DEBUG=false
```

7. 点击"Create Web Service"
8. 等待部署完成(约3-5分钟)
9. 记录分配的域名,如: `https://wordstyle-backend.onrender.com`

---

### 第三步:部署前端到Streamlit Cloud(5分钟)

#### 3.1 准备Streamlit应用

在项目根目录创建 `.streamlit/secrets.toml`:

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"
```

修改 `app.py` 顶部配置:

```python
# 从secrets读取后端URL
if st.secrets.get("backend"):
    BACKEND_URL = st.secrets["backend"]["url"]
else:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
```

#### 3.2 创建requirements.txt

在项目根目录确保有 `requirements.txt`:

```
streamlit>=1.28.0
python-docx>=0.8.11
Pillow>=9.0.0
requests>=2.31.0
```

#### 3.3 部署到Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 点击"New app"
3. 配置:
   - Repository: 选择你的GitHub仓库
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: 自定义,如 `wordstyle-app`

4. 点击"Deploy!"
5. 等待部署完成(约2-3分钟)
6. 访问: `https://wordstyle-app.streamlit.app`

---

### 第四步:测试与验证(5分钟)

#### 4.1 健康检查
访问: `https://wordstyle-backend.onrender.com/health`
应该返回: `{"status":"healthy"}`

#### 4.2 API文档
访问: `https://wordstyle-backend.onrender.com/docs`
应该看到Swagger UI界面

#### 4.3 功能测试
1. 打开前端: `https://wordstyle-app.streamlit.app`
2. 测试微信扫码登录
3. 测试文档上传和转换
4. 测试余额查询

---

## 💰 方案二:超低成本VPS部署

### 适用场景
- 需要更稳定的服务
- 计划商业化运营
- 需要国内访问速度优化

### 第一步:购买服务器

#### 推荐服务商

**腾讯云轻量应用服务器**(新用户最优惠)
- 配置: 2核2G, 60GB SSD, 5Mbps
- 价格: 首年¥60-88
- 链接: https://cloud.tencent.com/act/lighthouse

**阿里云轻量应用服务器**
- 配置: 2核2G, 40GB SSD, 3Mbps
- 价格: 首年¥99
- 链接: https://www.aliyun.com/activity/light

**选择系统**: Ubuntu 20.04 LTS

### 第二步:域名购买(可选)

**推荐**: 阿里云万网
- .top域名: ¥8-10/年
- .xyz域名: ¥10-15/年
- .cn域名: ¥35-40/年(需实名认证)

### 第三步:服务器配置

SSH连接到服务器:
```bash
ssh root@你的服务器IP
```

安装必要软件:
```bash
# 更新系统
apt update && apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | bash
systemctl enable docker
systemctl start docker

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 安装Nginx
apt install nginx -y
```

### 第四步:部署应用

上传项目文件到服务器:
```bash
# 本地执行
scp -r E:\LingMa\WordStyle root@服务器IP:/opt/wordstyle
```

服务器上执行:
```bash
cd /opt/wordstyle/backend

# 创建.env文件
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@db:5432/wordstyle
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://你的域名.com
DEBUG=false
EOF

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 第五步:配置Nginx反向代理

创建 `/etc/nginx/sites-available/wordstyle`:

```nginx
server {
    listen 80;
    server_name 你的域名.com www.你的域名.com;

    # 前端(Streamlit运行在8501端口)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置:
```bash
ln -s /etc/nginx/sites-available/wordstyle /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 第六步:配置SSL证书(Let's Encrypt免费)

```bash
# 安装Certbot
apt install certbot python3-certbot-nginx -y

# 获取证书
certbot --nginx -d 你的域名.com -d www.你的域名.com

# 自动续期
crontab -e
# 添加: 0 0 1 * * certbot renew --quiet
```

---

## 🔧 关键配置说明

### 环境变量清单

```bash
# 必需配置
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=随机字符串(至少32字符)
ALLOWED_ORIGINS=https://你的域名.com

# 可选配置
DEBUG=false
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=52428800  # 50MB

# 支付配置(后期添加)
WECHAT_APP_ID=
WECHAT_MCH_ID=
WECHAT_API_KEY=
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
```

### CORS配置

确保后端允许前端域名访问:

```python
# backend/app/core/config.py
ALLOWED_ORIGINS = "https://wordstyle-app.streamlit.app,https://你的域名.com"
```

---

## 📊 费用明细

### 方案一:完全免费

| 服务 | 费用 | 备注 |
|------|------|------|
| Streamlit Cloud | ¥0 | 每月1000小时运行时 |
| Render.com | ¥0 | 750小时免费额度 |
| Supabase | ¥0 | 500MB数据库+1GB存储 |
| 域名 | ¥0 | 使用免费子域名 |
| **总计** | **¥0/月** | - |

### 方案二:超低成本

| 项目 | 首年 | 续费 |
|------|------|------|
| VPS(腾讯云) | ¥60-88 | ¥300-400 |
| 域名(.top) | ¥8-10 | ¥8-10 |
| SSL证书 | ¥0 | ¥0 |
| **总计** | **¥68-98** | **¥308-410/年** |

---

## ⚠️ 注意事项

### 免费方案限制

1. **Render.com**
   - 15分钟无请求会休眠
   - 首次访问需要30秒唤醒
   - 每月750小时免费额度(足够单人使用)

2. **Streamlit Cloud**
   - 每月1000小时运行时
   - 不支持自定义域名(免费版)
   - 公共仓库必须开源

3. **Supabase**
   - 500MB数据库空间
   - 1GB文件存储
   - 50,000次API请求/月

### 性能优化建议

1. **减少冷启动时间**
   - 使用UptimeRobot免费监控,每5分钟ping一次
   - 网站: https://uptimerobot.com

2. **文件存储优化**
   - 转换完成后立即提供下载
   - 定期清理临时文件
   - 使用Supabase Storage替代本地存储

3. **数据库优化**
   - 定期清理过期任务记录
   - 使用连接池
   - 添加适当的索引

---

## 🚀 快速开始命令

### 本地测试

```bash
# 启动后端
cd backend
python run_dev.py

# 启动前端(新窗口)
streamlit run app.py
```

### 部署检查清单

- [ ] Supabase数据库已创建并初始化
- [ ] 后端已部署到Render/Railway
- [ ] 前端已部署到Streamlit Cloud
- [ ] CORS配置正确
- [ ] 数据库连接正常
- [ ] API文档可访问
- [ ] 微信扫码登录测试通过
- [ ] 文档转换功能测试通过
- [ ] 余额扣减逻辑测试通过

---

## 🆘 常见问题

### Q1: Render部署后访问很慢?
**A**: 这是免费层的特性。解决方案:
1. 使用UptimeRobot保持活跃
2. 升级到付费版($7/月)
3. 切换到Railway.app(同样免费但更快)

### Q2: Streamlit无法连接后端?
**A**: 检查CORS配置:
```python
# 确保ALLOWED_ORIGINS包含Streamlit域名
ALLOWED_ORIGINS = "https://*.streamlit.app"
```

### Q3: 数据库连接失败?
**A**: 检查:
1. DATABASE_URL格式是否正确
2. Supabase防火墙是否允许外部访问
3. 密码是否正确(注意特殊字符转义)

### Q4: 如何备份数据?
**A**: Supabase提供自动备份:
1. Settings → Database → Backups
2. 启用Point-in-time recovery
3. 或手动导出: `pg_dump`命令

### Q5: 如何监控服务状态?
**A**: 
- Render自带监控面板
- 使用UptimeRobot监控可用性
- 使用Sentry监控错误(免费层)

---

## 📞 技术支持

遇到问题可以:
1. 查看API文档: `/docs`
2. 检查后端日志: Render Dashboard → Logs
3. 查看前端日志: Streamlit → Manage app → Logs
4. 数据库问题: Supabase → SQL Editor

---

**祝您部署成功!** 🎉

最后更新: 2026-05-05
