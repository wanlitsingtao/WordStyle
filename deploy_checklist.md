# WordStyle 公网部署检查清单

## 📋 使用说明

本检查清单帮助你系统地完成公网部署，确保不遗漏任何关键步骤。

**建议：** 每完成一项就勾选，全部完成后再进行测试。

---

## 第一阶段：准备工作（预计30分钟）

### 1.1 注册外部服务账号

- [ ] **Supabase账号**
  - [ ] 访问 https://supabase.com
  - [ ] 使用GitHub登录
  - [ ] 创建新项目 `wordstyle`
  - [ ] 选择区域：Singapore
  - [ ] 设置数据库密码（**务必保存！**）
  - [ ] 等待项目初始化完成（1-2分钟）

- [ ] **Render账号**
  - [ ] 访问 https://render.com
  - [ ] 使用GitHub登录
  - [ ] 授权访问代码仓库

- [ ] **Streamlit Cloud账号**
  - [ ] 访问 https://share.streamlit.io
  - [ ] 使用GitHub登录
  - [ ] 授权访问代码仓库

- [ ] **UptimeRobot账号**（可选但推荐）
  - [ ] 访问 https://uptimerobot.com
  - [ ] 使用邮箱注册

---

### 1.2 获取Supabase关键信息

- [ ] **数据库连接字符串**
  - [ ] Supabase控制台 → Settings → Database
  - [ ] 找到 "Connection string" → URI标签
  - [ ] 复制完整字符串
  - [ ] 格式：`postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres`
  - [ ] **保存到安全位置**

- [ ] **Supabase API信息**
  - [ ] Supabase控制台 → Settings → API
  - [ ] 复制 Project URL：`https://xxxxx.supabase.co`
  - [ ] 复制 anon public key：`eyJhbG...`
  - [ ] **保存到安全位置**

---

### 1.3 初始化Supabase数据库

- [ ] **执行SQL脚本**
  - [ ] Supabase控制台 → SQL Editor → New query
  - [ ] 复制 DEPLOYMENT_UPGRADE_PLAN.md 中的完整SQL脚本
  - [ ] 粘贴到SQL Editor
  - [ ] 点击 "Run" 执行
  - [ ] 确认看到 "Success. No rows returned"

- [ ] **验证表结构**
  - [ ] 在SQL Editor中执行：
    ```sql
    SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
    ```
  - [ ] 确认返回 `table_count = 7`

- [ ] **验证默认配置**
  - [ ] 在SQL Editor中执行：
    ```sql
    SELECT * FROM system_config;
    ```
  - [ ] 确认返回4条配置记录

- [ ] **创建Storage Bucket**
  - [ ] Supabase控制台 → Storage → New bucket
  - [ ] 名称：`conversion-results`
  - [ ] 勾选 "Public bucket"
  - [ ] 点击 "Create bucket"
  - [ ] 确认Bucket创建成功

---

### 1.4 备份本地数据（可选）

- [ ] **备份用户数据**
  ```bash
  mkdir -p backup_$(date +%Y%m%d_%H%M%S)
  cp data/user_data.json backup_*/ 2>/dev/null || echo "无用户数据"
  cp data/comments_data.json backup_*/ 2>/dev/null || echo "无评论数据"
  ```

- [ ] **记录当前配置**
  - [ ] 记录 config.py 中的关键参数
  - [ ] 记录 ADMIN_CONTACT 联系方式

---

## 第二阶段：更新项目配置（预计1小时）

### 2.1 配置后端环境变量

- [ ] **复制模板文件**
  ```bash
  cd backend
  cp .env.production.template .env.production
  ```

- [ ] **编辑 .env.production**
  - [ ] 填写 DATABASE_URL（从Supabase复制）
  - [ ] 填写 SUPABASE_URL
  - [ ] 填写 SUPABASE_KEY
  - [ ] 生成并填写 SECRET_KEY
    ```bash
    python -c "import secrets; print(secrets.token_urlsafe(32))"
    ```
  - [ ] 确认 DEBUG=false
  - [ ] 确认 ALLOWED_ORIGINS 包含 `https://*.streamlit.app`

- [ ] **测试数据库连接**
  ```bash
  cd backend
  python init_supabase.py
  ```
  - [ ] 确认看到 "✅ 数据库连接成功"
  - [ ] 确认看到 "✅ 所有必需的表已存在"
  - [ ] 确认看到 "✅ 数据库初始化完成！"

---

### 2.2 配置前端Secrets

- [ ] **主应用Secrets**
  ```bash
  # 在项目根目录
  cp .streamlit/secrets.toml.template .streamlit/secrets.toml
  ```
  - [ ] 编辑 `.streamlit/secrets.toml`
  - [ ] 填写 backend.url（先留空，等Render部署后填写）
  - [ ] 填写 supabase.url
  - [ ] 填写 supabase.key
  - [ ] 填写 admin.contact

- [ ] **管理后台Secrets**
  ```bash
  cp .streamlit/secrets_admin.toml.template .streamlit/secrets_admin.toml
  ```
  - [ ] 编辑 `.streamlit/secrets_admin.toml`
  - [ ] 设置管理员用户名和密码
  - [ ] **密码建议使用强密码**

- [ ] **确认.gitignore配置**
  - [ ] 确认 `.gitignore` 包含：
    ```
    .env
    .env.production
    .streamlit/secrets.toml
    .streamlit/secrets_admin.toml
    ```

---

### 2.3 更新依赖文件

- [ ] **检查后端依赖**
  ```bash
  cd backend
  cat requirements.txt
  ```
  - [ ] 确认包含 `supabase==2.3.4`
  - [ ] 确认包含 `psycopg2-binary==2.9.9`

- [ ] **安装依赖测试**
  ```bash
  pip install -r requirements.txt
  ```
  - [ ] 确认所有依赖安装成功
  - [ ] 无报错信息

---

### 2.4 提交代码到GitHub

- [ ] **检查更改**
  ```bash
  git status
  ```
  - [ ] 确认没有提交敏感文件（.env, secrets.toml）

- [ ] **提交代码**
  ```bash
  git add .
  git commit -m "准备公网部署：更新配置文件和初始化脚本"
  git push origin main
  ```

- [ ] **验证推送**
  - [ ] 访问GitHub仓库
  - [ ] 确认最新提交已推送

---

## 第三阶段：部署后端到Render（预计40分钟）

### 3.1 创建Web Service

- [ ] **连接仓库**
  - [ ] Render控制台 → Dashboard → New + → Web Service
  - [ ] Connect a repository
  - [ ] 选择 WordStyle 仓库
  - [ ] 点击 Connect

- [ ] **配置服务参数**
  - [ ] Name: `wordstyle-backend`
  - [ ] Region: Singapore
  - [ ] Branch: main
  - [ ] Root Directory: `backend`
  - [ ] Runtime: Python 3

- [ ] **配置构建命令**
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

- [ ] **配置健康检查**
  - [ ] 点击 Advanced
  - [ ] Health Check Path: `/health`

---

### 3.2 配置环境变量

逐个添加以下环境变量（点击 Add Environment Variable）：

- [ ] **DATABASE_URL**
  - Key: `DATABASE_URL`
  - Value: `postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres`

- [ ] **SECRET_KEY**
  - Key: `SECRET_KEY`
  - Value: [之前生成的随机密钥]

- [ ] **ALLOWED_ORIGINS**
  - Key: `ALLOWED_ORIGINS`
  - Value: `https://*.streamlit.app,http://localhost:8501`

- [ ] **SUPABASE_URL**
  - Key: `SUPABASE_URL`
  - Value: `https://xxxxx.supabase.co`

- [ ] **SUPABASE_KEY**
  - Key: `SUPABASE_KEY`
  - Value: `eyJhbG...`

- [ ] **DEBUG**
  - Key: `DEBUG`
  - Value: `false`

- [ ] **UPLOAD_DIR**
  - Key: `UPLOAD_DIR`
  - Value: `/tmp/uploads`

- [ ] **保存配置**
  - [ ] 点击 Save Changes

---

### 3.3 等待部署完成

- [ ] **监控部署日志**
  - [ ] 切换到 Logs 标签
  - [ ] 观察实时日志输出
  - [ ] 等待看到 "Application startup complete"
  - [ ] 大约需要3-5分钟

- [ ] **处理部署错误**（如果有）
  - [ ] 查看错误日志
  - [ ] 根据 DEPLOYMENT_UPGRADE_PLAN.md 故障排查部分解决
  - [ ] 修复后点击 Manual Deploy 重新部署

---

### 3.4 测试后端

- [ ] **健康检查**
  - [ ] 浏览器访问：`https://wordstyle-backend.onrender.com/health`
  - [ ] 确认返回：`{"status":"healthy"}`

- [ ] **API文档**
  - [ ] 浏览器访问：`https://wordstyle-backend.onrender.com/docs`
  - [ ] 确认看到Swagger UI界面

- [ ] **测试数据库连接**
  - [ ] 在API文档中找到 GET /api/admin/stats
  - [ ] 点击 "Try it out" → "Execute"
  - [ ] 确认返回统计数据（不是错误）

- [ ] **记录后端URL**
  - [ ] 复制后端地址（如：`https://wordstyle-backend.onrender.com`）
  - [ ] 下一步要用

---

## 第四阶段：部署前端到Streamlit Cloud（预计30分钟）

### 4.1 更新前端Secrets

- [ ] **更新主应用Secrets**
  - [ ] 编辑 `.streamlit/secrets.toml`
  - [ ] 填写 backend.url 为Render后端地址
  - [ ] 再次确认supabase配置正确

- [ ] **提交更改**（如果需要）
  ```bash
  git add .streamlit/secrets.toml.template
  git commit -m "更新Secrets模板"
  git push
  ```
  **注意：** 不要提交实际的 secrets.toml 文件！

---

### 4.2 部署主应用

- [ ] **创建应用**
  - [ ] Streamlit Cloud → New app
  - [ ] Repository: 选择 WordStyle 仓库
  - [ ] Branch: main
  - [ ] Main file path: `app.py`
  - [ ] App URL: `wordstyle-app`（可自定义）
  - [ ] 点击 Deploy!

- [ ] **配置Secrets**
  - [ ] 部署开始后，点击 Settings
  - [ ] 找到 Secrets 部分
  - [ ] 点击 Edit secrets
  - [ ] 粘贴以下内容（修改为实际值）：
    ```toml
    [backend]
    url = "https://wordstyle-backend.onrender.com"
    
    [supabase]
    url = "https://xxxxx.supabase.co"
    key = "eyJhbG..."
    
    [admin]
    contact = "微信号：your_wechat_id"
    ```
  - [ ] 点击 Save

- [ ] **等待部署完成**
  - [ ] 返回 Manage app 标签
  - [ ] 查看部署日志
  - [ ] 等待 "Successfully deployed!"
  - [ ] 大约2-3分钟

---

### 4.3 部署管理后台

- [ ] **创建独立应用**
  - [ ] Streamlit Cloud → New app
  - [ ] Repository: 选择 WordStyle 仓库
  - [ ] Branch: main
  - [ ] Main file path: `admin_web.py`
  - [ ] App URL: `wordstyle-admin`（可自定义）
  - [ ] 点击 Deploy!

- [ ] **配置Secrets**
  - [ ] Settings → Secrets → Edit secrets
  - [ ] 粘贴：
    ```toml
    [backend]
    url = "https://wordstyle-backend.onrender.com"
    
    [admin]
    username = "admin"
    password = "your_secure_password"
    ```
  - [ ] 点击 Save

- [ ] **等待部署完成**
  - [ ] 查看部署日志
  - [ ] 等待 "Successfully deployed!"

---

## 第五阶段：测试与验证（预计30分钟）

### 5.1 访问应用

- [ ] **主应用**
  - [ ] 浏览器访问：`https://wordstyle-app.streamlit.app`
  - [ ] 确认页面正常加载

- [ ] **管理后台**
  - [ ] 浏览器访问：`https://wordstyle-admin.streamlit.app`
  - [ ] 确认页面正常加载

- [ ] **后端API**
  - [ ] 浏览器访问：`https://wordstyle-backend.onrender.com/docs`
  - [ ] 确认API文档可访问

---

### 5.2 功能测试

#### 主应用测试

- [ ] **用户登录**
  - [ ] 显示微信扫码登录按钮
  - [ ] 模拟扫码后显示用户信息
  - [ ] 显示剩余段落数（10000）

- [ ] **文档转换**
  - [ ] 上传测试Word文档
  - [ ] 点击"开始转换"
  - [ ] 转换进度正常显示
  - [ ] 下载转换结果成功

- [ ] **数据持久化**
  - [ ] 刷新页面（F5）
  - [ ] 确认转换历史已保存
  - [ ] 确认剩余段落已扣减

- [ ] **其他功能**
  - [ ] 评论区正常显示
  - [ ] 提交反馈功能正常
  - [ ] 充值页面可访问

---

#### 管理后台测试

- [ ] **管理员登录**
  - [ ] 输入用户名和密码
  - [ ] 登录成功

- [ ] **数据看板**
  - [ ] 显示用户总数
  - [ ] 显示任务总数
  - [ ] 显示收入统计

- [ ] **用户管理**
  - [ ] 用户列表正常加载
  - [ ] 可以查看用户详情

- [ ] **任务监控**
  - [ ] 任务列表实时更新
  - [ ] 可以看到任务状态

- [ ] **系统配置**
  - [ ] 可以修改配置参数
  - [ ] 修改后生效

---

### 5.3 API连接测试

- [ ] **打开开发者工具**
  - [ ] 浏览器按 F12
  - [ ] 切换到 Network 标签

- [ ] **执行操作**
  - [ ] 在主应用执行一次转换
  - [ ] 观察Network请求

- [ ] **检查结果**
  - [ ] 无CORS错误
  - [ ] API响应时间 < 3秒
  - [ ] 所有请求状态码为200或201

---

### 5.4 压力测试（可选）

- [ ] **并发测试**
  - [ ] 打开3-5个浏览器窗口
  - [ ] 同时执行转换操作
  - [ ] 确认无异常

- [ ] **长时间运行**
  - [ ] 保持页面打开30分钟
  - [ ] 确认无内存泄漏
  - [ ] 确认可正常操作

---

## 第六阶段：后续优化（预计20分钟）

### 6.1 配置UptimeRobot

- [ ] **添加监控**
  - [ ] UptimeRobot控制台 → Add New Monitor
  - [ ] Monitor Type: HTTP(s)
  - [ ] Friendly Name: WordStyle Backend
  - [ ] URL: `https://wordstyle-backend.onrender.com/health`
  - [ ] Monitoring Interval: Every 5 minutes
  - [ ] 点击 Create Monitor

- [ ] **验证监控**
  - [ ] 等待5分钟
  - [ ] 确认Monitor状态为 "Up"
  - [ ] 确认收到第一封监控邮件（可选）

---

### 6.2 监控与日志配置

- [ ] **后端日志**
  - [ ] 访问 Render Dashboard
  - [ ] 查看 Logs 标签
  - [ ] 确认日志正常记录

- [ ] **前端日志**
  - [ ] 访问 Streamlit Dashboard
  - [ ] 查看应用日志
  - [ ] 确认无错误

- [ ] **数据库监控**
  - [ ] Supabase控制台 → Database
  - [ ] 查看数据库使用情况
  - [ ] 确认资源充足

---

### 6.3 文档整理

- [ ] **记录关键信息**
  - [ ] 后端URL
  - [ ] 前端URL
  - [ ] 管理后台URL
  - [ ] Supabase项目ID
  - [ ] 管理员账号密码（保存在密码管理器）

- [ ] **备份配置文件**
  - [ ] 备份 .env.production（离线存储）
  - [ ] 备份 secrets.toml（离线存储）

- [ ] **更新README**
  - [ ] 添加公网访问地址
  - [ ] 添加部署说明链接

---

## ✅ 最终确认

### 部署完成确认

- [ ] 所有检查项已完成
- [ ] 所有功能测试通过
- [ ] 无已知Bug
- [ ] 监控已配置
- [ ] 文档已整理

### 分享应用

- [ ] 主应用地址：`https://wordstyle-app.streamlit.app`
- [ ] 管理后台地址：`https://wordstyle-admin.streamlit.app`
- [ ] 后端API地址：`https://wordstyle-backend.onrender.com`

### 下一步计划

**立即执行：**
- [ ] 分享给朋友试用
- [ ] 收集用户反馈
- [ ] 每天检查服务状态

**一周内：**
- [ ] 修复发现的Bug
- [ ] 优化用户体验
- [ ] 根据反馈调整功能

**一个月内：**
- [ ] 评估是否需要升级付费方案
- [ ] 集成真实微信支付
- [ ] 添加更多高级功能

---

## 📞 遇到问题？

### 快速排查

1. **后端部署失败** → 查看 Render Logs
2. **前端无法连接** → 检查 secrets.toml 和 CORS 配置
3. **数据库连接失败** → 检查 DATABASE_URL 格式
4. **文件上传失败** → 检查 Supabase Storage Bucket

### 详细指南

参考 `DEPLOYMENT_UPGRADE_PLAN.md` 中的故障排查章节。

---

**部署日期**: _______________  
**部署人员**: _______________  
**备注**: _______________

---

**恭喜完成部署！** 🎉
