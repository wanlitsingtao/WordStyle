# 🚀 15分钟快速部署指南

## 方案选择

### ✅ 推荐:完全免费方案
- **成本**: ¥0/月
- **时间**: 15-20分钟
- **适合**: MVP验证、个人项目、小规模使用

---

## 第一步:准备Supabase数据库 (5分钟)

### 1.1 注册并创建项目

1. 访问 https://supabase.com
2. 点击 "Start your project" → 使用GitHub登录
3. 点击 "New project"
4. 填写:
   - **Project name**: `wordstyle`
   - **Database Password**: 设置一个强密码(**务必保存!**)
   - **Region**: 选择 `Singapore`(离中国最近)
5. 点击 "Create new project"

等待1-2分钟初始化完成。

### 1.2 获取数据库连接信息

1. 左侧菜单点击 **Settings** (齿轮图标)
2. 点击 **Database**
3. 找到 "Connection string" 部分
4. 选择 **URI** 标签
5. 复制类似这样的字符串:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

### 1.3 初始化数据库表

1. 左侧菜单点击 **SQL Editor**
2. 点击 **New query**
3. 复制粘贴以下完整SQL脚本:

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

4. 点击右下角 **Run** 按钮
5. 看到 "Success. No rows returned" 表示成功

### 1.4 创建文件存储

1. 左侧菜单点击 **Storage**
2. 点击 **New bucket**
3. 填写:
   - **Name**: `conversion-results`
   - **Public bucket**: ✅ 勾选
4. 点击 **Create bucket**

✅ **Supabase准备完成!** 保存好数据库连接字符串,下一步要用。

---

## 第二步:部署后端到Render (7分钟)

### 2.1 注册Render

1. 访问 https://render.com
2. 点击 **Get Started for Free**
3. 使用 **GitHub** 登录
4. 授权访问你的代码仓库

### 2.2 创建Web服务

1. 点击 Dashboard 中的 **New +**
2. 选择 **Web Service**
3. 选择 **Connect a repository**
4. 选择你的GitHub仓库 `WordStyle`
5. 点击 **Connect**

### 2.3 配置服务

填写以下配置:

```
Name: wordstyle-backend
Region: Singapore (选择离你最近的)
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

点击 **Advanced** 展开高级选项:

**Health Check Path**:
```
/health
```

点击 **Create Web Service**

### 2.4 添加环境变量

等待服务开始构建后:

1. 在服务页面点击 **Environment** 标签
2. 点击 **Add Environment Variable**
3. 逐个添加以下变量:

#### 变量1: DATABASE_URL
```
Key: DATABASE_URL
Value: postgresql://postgres:你的密码@db.xxxxx.supabase.co:5432/postgres
```
(使用第一步中从Supabase复制的连接字符串)

#### 变量2: SECRET_KEY
```
Key: SECRET_KEY
Value: (访问 https://randomkeygen.com 生成一个CodeIgniter密钥,复制过来)
```

#### 变量3: ALLOWED_ORIGINS
```
Key: ALLOWED_ORIGINS
Value: https://*.streamlit.app
```

#### 变量4: DEBUG
```
Key: DEBUG
Value: false
```

添加完成后,点击 **Save Changes**

### 2.5 等待部署完成

1. 返回 **Logs** 标签
2. 等待看到类似这样的日志:
   ```
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:10000
   ```
3. 大约需要3-5分钟

### 2.6 测试后端

1. 在浏览器访问(替换为你的实际域名):
   ```
   https://wordstyle-backend.onrender.com/health
   ```
2. 应该看到:
   ```json
   {"status":"healthy"}
   ```
3. 访问API文档:
   ```
   https://wordstyle-backend.onrender.com/docs
   ```

✅ **后端部署完成!** 记录你的后端URL,下一步要用。

---

## 第三步:部署前端到Streamlit Cloud (3分钟)

### 3.1 创建Secrets文件

在你的项目根目录创建 `.streamlit/secrets.toml`:

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"
```

**注意**: 将URL替换为你实际的Render后端地址。

### 3.2 提交代码到GitHub

```bash
git add .
git commit -m "准备部署到公网"
git push
```

### 3.3 部署到Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 点击 **New app**
3. 填写:
   - **Repository**: 选择你的 `WordStyle` 仓库
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: `wordstyle-app`(可以自定义)
4. 点击 **Deploy!**

### 3.4 配置Secrets

1. 在应用部署页面,点击左侧 **Settings**
2. 找到 **Secrets** 部分
3. 点击 **Edit secrets**
4. 粘贴以下内容(修改为你的后端URL):

```toml
[backend]
url = "https://wordstyle-backend.onrender.com"
```

5. 点击 **Save**

### 3.5 等待部署完成

1. 返回 **Manage app** 标签
2. 查看部署日志
3. 等待看到 "Successfully deployed!"
4. 大约需要2-3分钟

---

## ✅ 第四步:测试与验证 (2分钟)

### 4.1 访问应用

在浏览器打开:
```
https://wordstyle-app.streamlit.app
```

### 4.2 功能测试清单

- [ ] 页面正常加载
- [ ] 显示微信扫码登录按钮
- [ ] 点击生成二维码
- [ ] 模拟扫码后显示用户信息
- [ ] 显示免费额度(10000段)
- [ ] 上传Word文档
- [ ] 开始转换
- [ ] 下载转换结果

### 4.3 API连接测试

1. 打开浏览器开发者工具(F12)
2. 切换到 **Network** 标签
3. 执行操作时观察API请求
4. 确认没有CORS错误

---

## 🎉 部署完成!

恭喜!你的WordStyle应用已经成功部署到公网,任何人都可以访问了。

### 分享你的应用

- **前端地址**: `https://wordstyle-app.streamlit.app`
- **后端API**: `https://wordstyle-backend.onrender.com`
- **API文档**: `https://wordstyle-backend.onrender.com/docs`

---

## ⚠️ 重要提示

### 保持Render活跃

Render免费版15分钟无请求会休眠,首次访问需要30秒唤醒。

**解决方案**: 使用UptimeRobot免费监控

1. 访问 https://uptimerobot.com
2. 注册账号
3. 点击 **Add New Monitor**
4. 填写:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: WordStyle Backend
   - **URL**: `https://wordstyle-backend.onrender.com/health`
   - **Monitoring Interval**: Every 5 minutes
5. 点击 **Create Monitor**

这样每5分钟会自动ping一次,保持服务活跃。

---

## 📊 资源限制说明

### Streamlit Cloud (免费)
- ✅ 每月1000小时运行时
- ✅ 无限访问量
- ❌ 不支持自定义域名

### Render (免费)
- ✅ 每月750小时运行时
- ✅ 自动HTTPS
- ❌ 15分钟无请求会休眠(可用UptimeRobot解决)

### Supabase (免费)
- ✅ 500MB数据库空间
- ✅ 1GB文件存储
- ✅ 50,000次API请求/月
- ✅ 自动备份

对于初期用户量,这些限制完全够用。

---

## 🔧 后续优化

### 立即可做
- [ ] 配置UptimeRobot保持活跃
- [ ] 测试所有功能正常
- [ ] 分享给朋友试用

### 一周内
- [ ] 收集用户反馈
- [ ] 修复发现的问题
- [ ] 优化用户体验

### 一个月内
- [ ] 如果流量增长,考虑升级到付费方案
- [ ] 集成真实微信支付
- [ ] 添加更多功能

---

## 🆘 遇到问题?

### 常见问题速查

**Q: Render部署失败?**
- 检查Logs标签查看详细错误
- 确认DATABASE_URL格式正确
- 确认requirements.txt包含所有依赖

**Q: Streamlit无法连接后端?**
- 检查secrets.toml中的URL是否正确
- 确认后端ALLOWED_ORIGINS包含streamlit.app
- 查看浏览器控制台是否有CORS错误

**Q: 数据库连接失败?**
- 确认Supabase项目已创建
- 检查密码是否正确(注意特殊字符)
- 确认SQL脚本已成功执行

**Q: 页面加载很慢?**
- 这是Render免费版的特性
- 配置UptimeRobot保持活跃
- 考虑升级到付费版($7/月)

---

## 📞 获取帮助

- **完整部署指南**: `DEPLOYMENT_GUIDE.md`
- **检查清单**: `deploy_checklist.md`
- **API文档**: `https://your-backend.onrender.com/docs`
- **Supabase文档**: https://supabase.com/docs
- **Render文档**: https://render.com/docs
- **Streamlit文档**: https://docs.streamlit.io

---

**祝您使用愉快!** 🚀

最后更新: 2026-05-05
