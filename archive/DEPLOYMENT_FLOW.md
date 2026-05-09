# WordStyle 公网部署完整方案

## 🎯 核心推荐:完全免费方案

### 技术架构图

```
┌─────────────────┐
│   用户浏览器     │
└────────┬────────┘
         │ HTTPS (自动)
         ↓
┌──────────────────────┐
│  Streamlit Cloud      │  ← 前端托管(免费)
│  wordstyle-app.       │     • 自动HTTPS
│  streamlit.app        │     • 全球CDN
│                       │     • 1000小时/月
└────────┬─────────────┘
         │ API调用
         ↓
┌──────────────────────┐
│  Render.com           │  ← 后端API(免费)
│  wordstyle-backend.   │     • FastAPI服务
│  onrender.com         │     • 750小时/月
│                       │     • 自动扩缩容
└────────┬─────────────┘
         │ SQL查询
         ↓
┌──────────────────────┐
│  Supabase             │  ← 数据库+存储(免费)
│  • PostgreSQL         │     • 500MB数据库
│  • Storage(文件)      │     • 1GB文件存储
│  • Auth(认证)         │     • 5万次API/月
└──────────────────────┘
```

**总成本**: ¥0/月 🎉

---

## 📦 已为您准备的文件

### 📖 部署文档(3个)

| 文件名 | 用途 | 推荐阅读顺序 |
|--------|------|-------------|
| `QUICK_DEPLOY.md` | 15分钟快速开始 | ⭐⭐⭐ 第一个看 |
| `DEPLOYMENT_GUIDE.md` | 完整技术指南 | ⭐⭐ 深入了解 |
| `deploy_checklist.md` | 部署检查清单 | ⭐ 逐步确认 |

### ⚙️ 配置文件(5个)

| 文件名 | 用途 | 状态 |
|--------|------|------|
| `backend/render.yaml` | Render自动部署配置 | ✅ 已创建 |
| `backend/.env.example` | 后端环境变量模板 | ✅ 已更新 |
| `.streamlit/secrets.toml.example` | Streamlit配置模板 | ✅ 已创建 |
| `requirements.txt` | Python依赖清单 | ✅ 已更新 |
| `.gitignore` | Git忽略规则 | ✅ 已更新 |

### 📊 总结文档(2个)

| 文件名 | 内容 |
|--------|------|
| `部署方案总结.md` | 所有方案的对比和选择建议 |
| `本文件` | 快速导航和决策指南 |

---

## 🚀 三步快速部署

### Step 1: Supabase数据库 (5分钟)

**操作**:
1. 注册 https://supabase.com
2. 创建新项目,设置密码
3. 执行SQL初始化脚本(在`QUICK_DEPLOY.md`中)
4. 创建Storage Bucket

**产出**:
- ✅ 数据库连接字符串
- ✅ 初始化的数据表
- ✅ 文件存储空间

---

### Step 2: Render后端 (7分钟)

**操作**:
1. 注册 https://render.com
2. 连接GitHub仓库
3. 配置服务(名称、区域、构建命令)
4. 添加环境变量(DATABASE_URL, SECRET_KEY等)
5. 等待部署完成

**产出**:
- ✅ 后端API地址(如: `https://wordstyle-backend.onrender.com`)
- ✅ 健康检查通过
- ✅ API文档可访问

---

### Step 3: Streamlit前端 (3分钟)

**操作**:
1. 创建 `.streamlit/secrets.toml` 填写后端URL
2. 提交代码到GitHub
3. 访问 https://share.streamlit.io 部署
4. 配置Secrets

**产出**:
- ✅ 前端应用地址(如: `https://wordstyle-app.streamlit.app`)
- ✅ 成功连接后端API
- ✅ 页面正常加载

---

## ✅ 验证清单

部署完成后,逐一测试:

- [ ] 访问前端URL,页面正常显示
- [ ] 点击"微信扫码登录",生成二维码
- [ ] 模拟扫码后,显示用户信息和余额
- [ ] 上传Word文档,开始转换
- [ ] 转换进度实时更新
- [ ] 下载转换结果文件
- [ ] 余额正确扣减
- [ ] 访问后端API文档(`/docs`)正常

---

## 💡 关键提示

### 🔐 安全注意事项

1. **不要泄露密钥**
   - `.env` 文件不要提交到Git
   - `secrets.toml` 不要公开
   - SECRET_KEY使用强随机字符串

2. **CORS配置**
   ```python
   ALLOWED_ORIGINS = "https://*.streamlit.app"
   ```
   确保包含你的前端域名

3. **数据库密码**
   - 使用强密码(大小写+数字+特殊字符)
   - 不要在代码中硬编码
   - 定期更换

---

### ⚡ 性能优化

#### 防止Render休眠

Render免费版15分钟无请求会休眠,解决方案:

**使用UptimeRobot**(免费):
1. 访问 https://uptimerobot.com
2. 注册账号
3. 添加监控:
   - URL: `https://your-backend.onrender.com/health`
   - 间隔: 每5分钟
4. 完成!

这样每5分钟自动ping一次,保持服务活跃。

---

### 📊 资源限制说明

| 平台 | 免费额度 | 实际可用 |
|------|---------|---------|
| **Streamlit** | 1000小时/月 | ≈ 41天连续运行 |
| **Render** | 750小时/月 | ≈ 31天连续运行 |
| **Supabase** | 500MB数据库 | ≈ 10万条用户记录 |
| **Supabase** | 1GB存储 | ≈ 1000个文档 |
| **Supabase** | 5万次API/月 | ≈ 1600次/天 |

**结论**: 对于初期MVP验证,完全够用!

---

## 🔄 备选方案

如果免费方案不满足需求,可以考虑:

### 方案A: 混合升级(¥50/月)

- Streamlit Cloud(免费) + Render Pro($7/月) + Supabase Pro($25/月)
- 优势: 更稳定,无休眠,更大容量

### 方案B: VPS自建(¥300/年)

- 腾讯云轻量服务器(首年¥60-88)
- Docker Compose一键部署
- 优势: 完全控制,国内速度快

详见: `DEPLOYMENT_GUIDE.md`

---

## 🆘 故障排查速查

### 问题1: Render部署失败

**症状**: Build Failed

**解决**:
```bash
# 查看Logs标签的详细错误
# 常见原因:
1. requirements.txt缺少依赖 → 补充缺失的包
2. DATABASE_URL格式错误 → 检查特殊字符转义
3. Python版本不兼容 → 指定Python 3.11
```

---

### 问题2: CORS错误

**症状**: 浏览器控制台显示"CORS policy"错误

**解决**:
```python
# backend/app/core/config.py
ALLOWED_ORIGINS = "https://*.streamlit.app,https://你的域名.com"
```

确保包含前端域名,然后重新部署。

---

### 问题3: 数据库连接失败

**症状**: "Connection refused" 或 "Authentication failed"

**解决**:
1. 检查DATABASE_URL格式:
   ```
   postgresql://postgres:密码@host:5432/postgres
   ```
2. 确认密码正确(注意特殊字符URL编码)
3. 检查Supabase防火墙设置(Settings → Database → Network)

---

### 问题4: 页面加载慢

**症状**: 首次访问需要30秒以上

**原因**: Render免费版休眠

**解决**:
- 配置UptimeRobot保持活跃
- 或升级到Render Pro($7/月)

---

## 📈 上线后维护

### 日常监控

1. **服务可用性**
   - UptimeRobot监控(免费)
   - Render Dashboard查看状态

2. **日志检查**
   - Render → Logs标签
   - Streamlit → Manage app → Logs
   - Supabase → Logs标签

3. **数据统计**
   - Supabase → Table Editor查看用户数
   - 订单表查看收入
   - 任务表查看转换量

---

### 定期维护

**每周**:
- [ ] 检查服务状态
- [ ] 查看错误日志
- [ ] 清理过期任务记录

**每月**:
- [ ] 备份数据库(Supabase自动备份)
- [ ] 更新依赖包
- [ ] 分析用户反馈

**每季度**:
- [ ] 安全审计
- [ ] 性能优化
- [ ] 功能迭代规划

---

## 🎓 学习资源

### 官方文档
- [Supabase Docs](https://supabase.com/docs) - 数据库使用指南
- [Render Docs](https://render.com/docs) - 部署最佳实践
- [Streamlit Docs](https://docs.streamlit.io) - 前端开发教程

### 视频教程
- YouTube搜索: "Deploy Streamlit to Streamlit Cloud"
- Bilibili搜索: "Render部署教程"

### 社区支持
- [Stack Overflow](https://stackoverflow.com/questions/tagged/supabase)
- [Reddit r/Supabase](https://reddit.com/r/Supabase)
- [Streamlit论坛](https://discuss.streamlit.io)

---

## 🎯 立即行动

### 您现在有3个选择:

#### 选项1: 立即开始部署 ⭐ 推荐
打开 `QUICK_DEPLOY.md`,跟随15分钟快速指南。

#### 选项2: 先了解技术细节
阅读 `DEPLOYMENT_GUIDE.md`,深入了解架构和配置。

#### 选项3: 使用检查清单
打开 `deploy_checklist.md`,逐步确认每个步骤。

---

## 📞 需要帮助?

如果遇到任何问题:

1. **查看文档**
   - `QUICK_DEPLOY.md` - 常见问题解答
   - `DEPLOYMENT_GUIDE.md` - 详细故障排查

2. **检查日志**
   - Render → Logs
   - Streamlit → Logs
   - 浏览器F12控制台

3. **搜索解决方案**
   - Google搜索错误信息
   - Stack Overflow查找类似问题

4. **联系支持**
   - Supabase: support@supabase.com
   - Render: support@render.com
   - Streamlit: support@streamlit.io

---

## 🎉 总结

您现在拥有:
- ✅ **完整的部署方案** - 三种方案可选
- ✅ **详细的操作指南** - 15分钟快速上手
- ✅ **所有配置文件** - 开箱即用
- ✅ **故障排查手册** - 问题解决无忧
- ✅ **零成本启动** - 免费方案完全可行

**下一步**: 选择一个方案,开始部署吧!

祝您部署顺利! 🚀

---

**文档版本**: v1.0
**最后更新**: 2026-05-05
**适用项目**: WordStyle 文档转换平台
