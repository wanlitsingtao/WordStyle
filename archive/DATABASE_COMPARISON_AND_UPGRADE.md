# 数据库结构对比与升级方案

## 📊 一、当前数据库结构分析

### 1.1 本地SQLite数据库（task_manager.py）

**文件位置**: `conversion_tasks.db`

**表结构**:
```sql
CREATE TABLE IF NOT EXISTS conversion_tasks (
    task_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_count INTEGER DEFAULT 1,
    paragraphs INTEGER,
    cost REAL,
    status TEXT DEFAULT 'PENDING',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    output_files TEXT,
    error_message TEXT,
    expires_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_user_status ON conversion_tasks(user_id, status);
CREATE INDEX idx_expires ON conversion_tasks(expires_at);
```

**特点**:
- ✅ 轻量级，适合单机部署
- ✅ 无需额外配置
- ❌ 不支持并发访问
- ❌ 不支持分布式部署
- ❌ 缺少用户管理、订单管理等完整功能

---

### 1.2 后端PostgreSQL数据库（backend/app/models.py）

**支持数据库**: PostgreSQL（生产环境）/ SQLite（开发环境）

**表结构**:

#### 1) users - 用户表
```sql
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

-- 索引
CREATE INDEX idx_users_wechat_openid ON users(wechat_openid);
CREATE INDEX idx_users_email ON users(email);
```

#### 2) orders - 订单表
```sql
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

-- 索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_no ON orders(order_no);
```

#### 3) conversion_tasks - 转换任务表
```sql
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

-- 索引
CREATE INDEX idx_tasks_user_id ON conversion_tasks(user_id);
CREATE INDEX idx_tasks_task_id ON conversion_tasks(task_id);
```

#### 4) system_config - 系统配置表
```sql
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 默认配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('free_paragraphs_on_first_login', '10000', '新用户首次登录赠送的免费段落数'),
('min_recharge_amount', '1.0', '最低充值金额(元)'),
('paragraph_price', '0.001', '每段落价格(元)');
```

**特点**:
- ✅ 完整的用户管理系统
- ✅ 订单管理和支付集成
- ✅ 支持高并发访问
- ✅ 支持分布式部署
- ✅ 完善的索引优化
- ❌ 需要PostgreSQL服务器或Supabase服务

---

## 🔍 二、数据库结构差异对比

| 特性 | 本地SQLite | 后端PostgreSQL |
|------|-----------|---------------|
| **数据库类型** | SQLite | PostgreSQL / SQLite |
| **表数量** | 1个表 | 4个表 |
| **用户管理** | ❌ 无 | ✅ 完整（微信+邮箱） |
| **订单管理** | ❌ 无 | ✅ 完整 |
| **系统配置** | ❌ 硬编码 | ✅ 动态配置 |
| **主键类型** | TEXT | UUID |
| **时间戳** | TIMESTAMP | TIMESTAMP WITH TIME ZONE |
| **外键约束** | ❌ 无 | ✅ 有 |
| **索引数量** | 2个 | 6个 |
| **适用场景** | 单机测试 | 生产环境 |
| **并发支持** | ❌ 差 | ✅ 好 |

### 主要差异点：

1. **任务表字段差异**:
   - 本地: `file_count`, `started_at`, `expires_at`
   - 后端: 无这些字段

2. **用户ID类型**:
   - 本地: TEXT字符串
   - 后端: UUID类型

3. **时间处理**:
   - 本地: 简单TIMESTAMP
   - 后端: 带时区的TIMESTAMP WITH TIME ZONE

4. **数据完整性**:
   - 本地: 无外键约束
   - 后端: 严格的外键关系

---

## 🚀 三、完整升级方案

### 方案选择建议

根据您的需求和资源，提供以下三种方案：

---

### 方案A：保持现状（推荐用于个人使用）

**适用场景**:
- 个人使用或小团队内部使用
- 不需要在线支付功能
- 单台机器运行
- 用户量 < 10人

**优点**:
- ✅ 零成本
- ✅ 部署简单
- ✅ 维护方便
- ✅ 无需外部依赖

**缺点**:
- ❌ 不支持多机部署
- ❌ 不支持真正的在线支付
- ❌ 数据无法云端备份

**实施步骤**:
1. 清理无关文件（已提供cleanup_for_github.py脚本）
2. 提交到GitHub
3. 继续使用本地SQLite数据库
4. 通过手动方式管理用户额度

**成本**: ¥0/月

---

### 方案B：混合模式（推荐用于小规模商用）

**适用场景**:
- 小范围公开使用
- 需要简单的用户管理
- 用户量 10-100人
- 预算有限

**架构**:
```
前端 (Streamlit Cloud) → 后端 (Render免费版) → 数据库 (Supabase免费版)
```

**优点**:
- ✅ 完全免费
- ✅ 支持真正的用户注册登录
- ✅ 支持微信扫码登录
- ✅ 数据云端备份
- ✅ 可公网访问

**缺点**:
- ❌ Render免费版15分钟休眠（可用UptimeRobot解决）
- ❌ Supabase免费版有配额限制
- ❌ 需要配置环境变量

**实施步骤**:

#### 第1步：准备Supabase数据库（5分钟）
1. 注册 https://supabase.com
2. 创建新项目
3. 执行QUICK_DEPLOY.md中的SQL脚本
4. 获取DATABASE_URL

#### 第2步：部署后端到Render（7分钟）
1. 注册 https://render.com
2. 连接GitHub仓库
3. 配置环境变量：
   - DATABASE_URL
   - SECRET_KEY
   - ALLOWED_ORIGINS
4. 等待部署完成

#### 第3步：部署前端到Streamlit Cloud（3分钟）
1. 注册 https://share.streamlit.io
2. 连接GitHub仓库
3. 配置Secrets（后端URL）
4. 等待部署完成

#### 第4步：配置UptimeRobot（2分钟）
1. 注册 https://uptimerobot.com
2. 添加监控：`https://your-backend.onrender.com/health`
3. 设置5分钟间隔

**总耗时**: 约17分钟

**成本**: ¥0/月

**详细指南**: 参见 `QUICK_DEPLOY.md`

---

### 方案C：生产级部署（推荐用于正式商用）

**适用场景**:
- 大规模公开使用
- 需要稳定可靠的服务
- 用户量 > 100人
- 需要集成真实微信支付

**架构选项**:

#### 选项C1：云服务器 + Docker
```
阿里云/腾讯云 ECS (¥100-300/月)
├── Nginx (反向代理)
├── Backend API (Docker容器)
├── Frontend (Streamlit)
└── PostgreSQL (Docker容器)
```

**优点**:
- ✅ 完全可控
- ✅ 性能最优
- ✅ 可自定义配置
- ✅ 支持真实微信支付

**缺点**:
- ❌ 需要运维知识
- ❌ 需要备案域名
- ❌ 成本较高

**成本**: ¥100-300/月

#### 选项C2：Serverless架构
```
Vercel (前端) + Railway (后端) + Supabase Pro (数据库)
```

**优点**:
- ✅ 自动扩缩容
- ✅ 无需运维
- ✅ 按使用量付费

**缺点**:
- ❌ 冷启动延迟
- ❌ 调试困难

**成本**: ¥50-200/月（根据用量）

---

## 📋 四、推荐实施路径

### 阶段1：立即执行（今天）

1. **清理项目文件**
   ```bash
   python cleanup_for_github.py
   ```

2. **更新.gitignore**
   - 确保包含所有敏感文件和临时文件

3. **提交到GitHub**
   ```bash
   git add .
   git commit -m "Initial commit - WordStyle v1.0"
   git push origin main
   ```

4. **创建Release标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

### 阶段2：短期目标（1周内）

1. **采用方案B部署**
   - 按照QUICK_DEPLOY.md完成部署
   - 测试所有功能正常
   - 邀请5-10个朋友试用

2. **收集反馈**
   - 记录用户遇到的问题
   - 统计使用情况
   - 评估是否需要升级

### 阶段3：中期规划（1个月内）

根据使用情况决定：

**如果用户量 < 50人**:
- 继续使用方案B
- 优化用户体验
- 完善文档

**如果用户量 > 50人且增长迅速**:
- 考虑升级到方案C
- 集成真实微信支付
- 购买域名和SSL证书

---

## 🔧 五、技术迁移指南

### 从SQLite迁移到PostgreSQL

如果您决定从本地SQLite迁移到PostgreSQL，需要以下步骤：

#### 1. 数据导出
```python
# export_sqlite_data.py
import sqlite3
import json

conn = sqlite3.connect('conversion_tasks.db')
cursor = conn.cursor()

# 导出所有任务数据
cursor.execute("SELECT * FROM conversion_tasks")
tasks = cursor.fetchall()

with open('tasks_export.json', 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

conn.close()
print(f"已导出 {len(tasks)} 条任务记录")
```

#### 2. 数据导入
```python
# import_to_postgresql.py
from sqlalchemy import create_engine
from backend.app.models import Base, ConversionTask, User
from backend.app.core.database import SessionLocal
import json
import uuid

engine = create_engine("postgresql://user:pass@host/dbname")
Base.metadata.create_all(engine)

db = SessionLocal()

with open('tasks_export.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

for task_data in tasks:
    # 转换数据格式
    new_task = ConversionTask(
        task_id=task_data[0],
        user_id=str(uuid.uuid4()),  # 需要关联到实际用户
        filename=task_data[2],
        paragraphs=task_data[4],
        cost=task_data[5],
        status=task_data[6],
        progress=task_data[7],
        output_files=task_data[10],
        error_message=task_data[11]
    )
    db.add(new_task)

db.commit()
db.close()
print(f"已导入 {len(tasks)} 条任务记录")
```

#### 3. 代码适配
修改app.py中的数据库调用：
```python
# 之前（SQLite）
from task_manager import create_task, get_task_status

# 之后（PostgreSQL via Backend API）
import requests

BACKEND_URL = "https://your-backend.onrender.com"

def create_task_api(user_id, filename, paragraphs):
    response = requests.post(
        f"{BACKEND_URL}/api/tasks",
        json={
            "user_id": user_id,
            "filename": filename,
            "paragraphs": paragraphs
        }
    )
    return response.json()
```

---

## ⚠️ 六、注意事项

### 数据安全

1. **永远不要提交以下文件到GitHub**:
   - `.env` 文件（包含密钥）
   - `user_data.json`（用户隐私数据）
   - `*.db` 文件（数据库文件）
   - `conversion_results/`（用户上传的文件）
   - `uploads/`（临时上传文件）

2. **环境变量管理**:
   - 使用 `.env.example` 作为模板
   - 在README中说明需要配置的变量
   - 不要在代码中硬编码密钥

### 版本控制

1. **Git分支策略**:
   ```
   main          - 生产环境（稳定版本）
   develop       - 开发环境（最新功能）
   feature/*     - 功能分支
   hotfix/*      - 紧急修复
   ```

2. **提交规范**:
   ```bash
   git commit -m "feat: 添加微信扫码登录功能"
   git commit -m "fix: 修复转换进度条显示问题"
   git commit -m "docs: 更新部署文档"
   ```

### 备份策略

1. **本地备份**（如果使用SQLite）:
   ```bash
   # 每天凌晨2点备份
   0 2 * * * cp conversion_tasks.db backups/conversion_tasks_$(date +\%Y\%m\%d).db
   ```

2. **云端备份**（如果使用Supabase）:
   - Supabase自动每日备份
   - 可手动触发备份
   - 保留最近7天的备份

---

## 📞 七、支持与帮助

### 遇到问题？

1. **查看文档**:
   - `README.md` - 项目介绍
   - `QUICK_DEPLOY.md` - 快速部署指南
   - `DEPLOYMENT_GUIDE.md` - 详细部署指南

2. **检查日志**:
   - 前端: Streamlit控制台
   - 后端: Render Logs
   - 数据库: Supabase Logs

3. **常见问题**:
   - GitHub Issues页面
   - Stack Overflow
   - 官方文档

### 联系方式

- GitHub: [您的GitHub用户名]/WordStyle
- Email: [您的邮箱]
- 微信: [您的微信号]

---

**最后更新**: 2026-05-07  
**文档版本**: v1.0
