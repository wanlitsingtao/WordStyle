# 部署前检查清单

## 📋 准备阶段

### 1. 代码准备
- [ ] 确认 `backend/requirements.txt` 包含所有依赖
- [ ] 确认根目录 `requirements.txt` 包含Streamlit依赖
- [ ] 确认 `app.py` 可以正常读取后端URL配置
- [ ] 确认 `.gitignore` 已排除敏感文件(.env, secrets.toml等)

### 2. 数据库准备(Supabase)
- [ ] 注册Supabase账号: https://supabase.com
- [ ] 创建新项目
- [ ] 记录数据库连接信息(Host, Port, Password)
- [ ] 执行SQL初始化脚本(见DEPLOYMENT_GUIDE.md)
- [ ] 创建Storage Bucket: `conversion-results`
- [ ] 测试数据库连接

### 3. 后端配置
- [ ] 修改 `backend/app/core/config.py` 支持环境变量
- [ ] 生成SECRET_KEY (使用 https://randomkeygen.com)
- [ ] 设置ALLOWED_ORIGINS包含前端域名
- [ ] 创建 `backend/.env.example` 模板文件

### 4. 前端配置
- [ ] 创建 `.streamlit/secrets.toml` (从secrets.toml.example复制)
- [ ] 填写后端API URL
- [ ] 测试本地连接: `streamlit run app.py`

---

## 🚀 部署阶段

### 第一步: 部署后端到Render

#### 1.1 注册与配置
- [ ] 访问 https://render.com 并注册
- [ ] 连接GitHub仓库
- [ ] 点击 "New +" → "Web Service"

#### 1.2 服务配置
- [ ] Name: `wordstyle-backend`
- [ ] Region: `Singapore`
- [ ] Branch: `main`
- [ ] Root Directory: `backend`
- [ ] Runtime: `Python 3`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 1.3 环境变量设置
在Render Dashboard添加以下环境变量:
- [ ] `DATABASE_URL`: Supabase连接字符串
- [ ] `SECRET_KEY`: 随机生成的密钥
- [ ] `ALLOWED_ORIGINS`: `https://*.streamlit.app`
- [ ] `DEBUG`: `false`

#### 1.4 部署验证
- [ ] 等待部署完成(约3-5分钟)
- [ ] 访问健康检查: `https://wordstyle-backend.onrender.com/health`
- [ ] 访问API文档: `https://wordstyle-backend.onrender.com/docs`
- [ ] 记录后端URL供前端使用

---

### 第二步: 部署前端到Streamlit Cloud

#### 2.1 注册与配置
- [ ] 访问 https://share.streamlit.io
- [ ] 使用GitHub账号登录
- [ ] 点击 "New app"

#### 2.2 应用配置
- [ ] Repository: 选择你的GitHub仓库
- [ ] Branch: `main`
- [ ] Main file path: `app.py`
- [ ] App URL: `wordstyle-app`(自定义)

#### 2.3 Secrets配置
在Streamlit Dashboard的Secrets中添加:
```toml
[backend]
url = "https://wordstyle-backend.onrender.com"
```

#### 2.4 部署验证
- [ ] 等待部署完成(约2-3分钟)
- [ ] 访问: `https://wordstyle-app.streamlit.app`
- [ ] 测试页面加载
- [ ] 测试后端API连接

---

## ✅ 测试阶段

### 功能测试清单

#### 1. 用户认证
- [ ] 微信扫码登录功能正常
- [ ] 新用户首次登录获得免费额度
- [ ] 老用户登录显示正确余额
- [ ] Token刷新机制正常

#### 2. 文档转换
- [ ] 上传Word文档成功
- [ ] 转换任务创建成功
- [ ] 转换进度实时更新
- [ ] 下载转换结果正常
- [ ] 余额扣减正确

#### 3. 支付充值(如已集成)
- [ ] 创建充值订单成功
- [ ] 显示收款码正常
- [ ] 上传付款截图成功
- [ ] 管理员审核后余额更新

#### 4. 错误处理
- [ ] 网络错误提示友好
- [ ] 余额不足时阻止转换
- [ ] 文件格式校验正常
- [ ] 大文件上传限制生效

---

## 🔧 优化阶段

### 性能优化
- [ ] 配置UptimeRobot保持Render活跃(https://uptimerobot.com)
- [ ] 设置定期清理过期任务
- [ ] 启用数据库查询缓存
- [ ] 压缩上传文件

### 监控配置
- [ ] Render Dashboard查看日志
- [ ] Streamlit Dashboard查看使用情况
- [ ] Supabase查看数据库统计
- [ ] 配置错误告警(可选)

### 安全加固
- [ ] 确认HTTPS已启用
- [ ] 确认SECRET_KEY足够复杂
- [ ] 确认CORS配置正确
- [ ] 确认数据库密码强度
- [ ] 定期更新依赖包

---

## 📊 上线后维护

### 日常维护
- [ ] 每周检查服务状态
- [ ] 每月清理过期数据
- [ ] 每季度更新依赖包
- [ ] 备份重要数据

### 监控指标
- [ ] API响应时间 < 500ms
- [ ] 服务可用性 > 99%
- [ ] 错误率 < 1%
- [ ] 用户转化率追踪

---

## 🆘 故障排查

### 常见问题速查

**问题1: 后端无法启动**
- 检查Render Logs
- 验证DATABASE_URL格式
- 确认requirements.txt完整

**问题2: 前端无法连接后端**
- 检查CORS配置
- 验证ALLOWED_ORIGINS
- 检查浏览器控制台错误

**问题3: 数据库连接失败**
- 验证Supabase防火墙设置
- 检查密码是否正确
- 确认网络连通性

**问题4: 文件上传失败**
- 检查文件大小限制
- 验证Storage权限
- 查看后端日志

---

## 📞 获取帮助

- 部署指南: `DEPLOYMENT_GUIDE.md`
- API文档: `https://your-backend.onrender.com/docs`
- Supabase文档: https://supabase.com/docs
- Render文档: https://render.com/docs
- Streamlit文档: https://docs.streamlit.io

---

**最后更新**: 2026-05-05
