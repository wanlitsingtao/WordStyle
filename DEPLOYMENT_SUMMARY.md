# WordStyle 公网部署方案 - 快速开始指南

## 📋 方案说明

本方案为你提供了**完整的、按步骤可操作的**公网部署升级路径，采用"清空重建"策略，确保部署过程简单可靠。

### 技术架构

```
┌─────────────────────────────────────────────────────┐
│                  用户访问层                          │
│  ┌──────────────────┐    ┌──────────────────┐      │
│  │   主应用前端      │    │   管理后台前端    │      │
│  │ Streamlit Cloud  │    │ Streamlit Cloud  │      │
│  └────────┬─────────┘    └────────┬─────────┘      │
│           │                       │                 │
│           └───────────┬───────────┘                 │
│                       │                             │
├───────────────────────┼─────────────────────────────┤
│                   API层                              │
│           ┌───────────▼───────────┐                 │
│           │   FastAPI 后端        │                 │
│           │   Render 部署         │                 │
│           └───────────┬───────────┘                 │
│                       │                             │
├───────────────────────┼─────────────────────────────┤
│                  数据层                              │
│  ┌──────────────────┐    ┌──────────────────┐      │
│  │  PostgreSQL DB   │    │   Storage Bucket  │      │
│  │   Supabase       │    │   Supabase        │      │
│  └──────────────────┘    └──────────────────┘      │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始（5分钟）

### 第1步：运行准备脚本

双击运行项目根目录的：
```
deploy_prepare.bat
```

这个脚本会：
- ✅ 检查Python和Git环境
- ✅ 自动备份本地数据
- ✅ 验证配置文件模板
- ✅ 显示下一步操作指南

---

### 第2步：阅读完整方案

打开并仔细阅读：
```
DEPLOYMENT_UPGRADE_PLAN.md
```

这是**41页的完整部署方案**，包含：
- 📖 详细的服务注册步骤
- 🔧 完整的配置示例
- 📊 数据库初始化SQL脚本
- 🆘 全面的故障排查手册
- 💰 成本分析和优化建议

---

### 第3步：使用检查清单

打印或打开：
```
deploy_checklist.md
```

这是一个**逐步检查清单**，帮助你：
- ✓ 系统地完成每个部署步骤
- ✓ 确保不遗漏任何关键配置
- ✓ 记录部署进度
- ✓ 最终验证所有功能

---

## 📁 文件说明

### 核心文档

| 文件名 | 用途 | 大小 |
|--------|------|------|
| `DEPLOYMENT_UPGRADE_PLAN.md` | **完整部署方案**（必读） | 41KB |
| `deploy_checklist.md` | **逐步检查清单**（跟着做） | 15KB |
| `DEPLOYMENT_SUMMARY.md` | 本文档（快速开始） | - |

### 配置文件模板

| 文件名 | 用途 | 使用时复制到 |
|--------|------|-------------|
| `backend/.env.production.template` | 后端环境变量模板 | `backend/.env.production` |
| `.streamlit/secrets.toml.template` | 主应用Secrets模板 | `.streamlit/secrets.toml` |
| `.streamlit/secrets_admin.toml.template` | 管理后台Secrets模板 | `.streamlit/secrets_admin.toml` |

### 工具脚本

| 文件名 | 功能 |
|--------|------|
| `deploy_prepare.bat` | 部署准备脚本（一键执行） |
| `backend/init_supabase.py` | Supabase数据库初始化和验证 |
| `backend/test_supabase_connection.py` | 数据库连接测试脚本 |

### 代码模块

| 文件名 | 功能 |
|--------|------|
| `backend/app/utils/supabase_storage.py` | Supabase文件存储工具 |

---

## 🎯 部署流程概览

### 阶段一：准备工作（30分钟）

1. **注册外部服务**
   - Supabase（数据库+存储）
   - Render（后端部署）
   - Streamlit Cloud（前端部署）
   - UptimeRobot（可选，保持活跃）

2. **初始化Supabase**
   - 创建PostgreSQL数据库
   - 执行SQL脚本创建表结构
   - 创建Storage Bucket

3. **备份本地数据**
   - 运行 `deploy_prepare.bat` 自动备份

---

### 阶段二：配置更新（1小时）

1. **配置后端环境变量**
   ```bash
   cd backend
   copy .env.production.template .env.production
   # 编辑 .env.production 填写实际值
   ```

2. **配置前端Secrets**
   ```bash
   copy .streamlit\secrets.toml.template .streamlit\secrets.toml
   copy .streamlit\secrets_admin.toml.template .streamlit\secrets_admin.toml
   # 编辑这两个文件填写实际值
   ```

3. **测试数据库连接**
   ```bash
   cd backend
   python init_supabase.py
   ```

4. **提交代码到GitHub**
   ```bash
   git add .
   git commit -m "准备公网部署"
   git push origin main
   ```

---

### 阶段三：部署后端（40分钟）

1. **在Render创建Web Service**
   - 连接GitHub仓库
   - 配置构建命令和启动命令
   - 添加环境变量

2. **等待部署完成**
   - 查看Logs确认启动成功
   - 测试健康检查端点

3. **验证API功能**
   - 访问 `/docs` 查看API文档
   - 测试数据库连接

---

### 阶段四：部署前端（30分钟）

1. **在Streamlit Cloud部署主应用**
   - 选择仓库和入口文件（app.py）
   - 配置Secrets

2. **在Streamlit Cloud部署管理后台**
   - 选择仓库和入口文件（admin_web.py）
   - 配置Secrets

3. **验证前端功能**
   - 访问主应用
   - 访问管理后台

---

### 阶段五：测试验证（30分钟）

按照 `deploy_checklist.md` 第五阶段逐项测试：
- 用户登录
- 文档转换
- 数据持久化
- 管理后台功能
- API连接

---

### 阶段六：后续优化（20分钟）

1. **配置UptimeRobot**
   - 每5分钟ping一次后端
   - 保持Render服务活跃

2. **设置监控**
   - 查看Render Logs
   - 查看Streamlit Logs
   - 查看Supabase Dashboard

3. **整理文档**
   - 记录所有URL和密码
   - 备份配置文件

---

## ⏱️ 预计时间

| 阶段 | 预计时间 | 备注 |
|------|---------|------|
| 准备工作 | 30分钟 | 首次需要注册账号 |
| 配置更新 | 1小时 | 仔细填写配置 |
| 部署后端 | 40分钟 | 包含等待部署时间 |
| 部署前端 | 30分钟 | 两个应用分别部署 |
| 测试验证 | 30分钟 | 全面功能测试 |
| 后续优化 | 20分钟 | 监控和文档整理 |
| **总计** | **约3.5小时** | 首次部署 |

**后续部署**（代码更新后）：约15分钟（自动CI/CD）

---

## 💰 成本分析

### 免费方案（推荐初期使用）

| 服务 | 免费额度 | 月成本 |
|------|---------|--------|
| Streamlit Cloud | 1000小时/月 | ¥0 |
| Render | 750小时/月 | ¥0 |
| Supabase | 500MB + 1GB存储 | ¥0 |
| UptimeRobot | 50个监控 | ¥0 |
| **总计** | | **¥0/月** |

**适用场景：**
- MVP验证阶段
- 日活用户 < 100
- 月转换次数 < 1000

---

### 付费方案（用户增长后）

| 服务 | 升级方案 | 月成本 |
|------|---------|--------|
| Render | Starter | ~¥50 |
| Supabase | Pro | ~¥180 |
| Redis（可选） | Upstash | ~¥70 |
| **总计** | | **~¥300/月** |

**触发条件：**
- Render运行时长不足
- 数据库超过500MB
- 需要缓存加速

---

## 🆘 常见问题

### Q1: 部署失败怎么办？

**A:** 参考 `DEPLOYMENT_UPGRADE_PLAN.md` 中的"故障排查手册"章节，包含5个常见问题的详细解决方案。

---

### Q2: 需要修改哪些配置？

**A:** 主要修改3个文件：
1. `backend/.env.production` - 后端环境变量
2. `.streamlit/secrets.toml` - 主应用Secrets
3. `.streamlit/secrets_admin.toml` - 管理后台Secrets

所有配置项都在模板文件中有详细说明。

---

### Q3: 数据安全吗？

**A:** 
- ✅ Supabase提供企业级安全防护
- ✅ 自动每日备份
- ✅ HTTPS加密传输
- ✅ JWT Token认证
- ⚠️ 注意保管好API Key和密码

---

### Q4: 可以自定义域名吗？

**A:** 
- Streamlit Cloud免费版不支持自定义域名
- Render免费版支持自定义域名
- 如需自定义域名，需升级到付费方案

---

### Q5: 性能如何？

**A:** 
- 页面加载：< 3秒（配合UptimeRobot）
- API响应：< 2秒
- 转换任务：异步处理，立即返回
- 并发支持：可处理10+并发用户

---

## 📞 获取帮助

### 官方文档
- **Supabase**: https://supabase.com/docs
- **Render**: https://render.com/docs
- **Streamlit**: https://docs.streamlit.io

### 项目文档
- **DEPLOYMENT_UPGRADE_PLAN.md** - 完整部署方案（41页）
- **deploy_checklist.md** - 逐步检查清单
- **README.md** - 项目总体说明

### 技术支持
- GitHub Issues: 提交问题和Bug报告
- 项目Wiki: 查看常见问题解答

---

## ✅ 下一步行动

### 立即执行

1. **运行准备脚本**
   ```bash
   deploy_prepare.bat
   ```

2. **阅读完整方案**
   ```
   打开 DEPLOYMENT_UPGRADE_PLAN.md
   ```

3. **注册外部服务**
   - Supabase
   - Render
   - Streamlit Cloud

---

### 一周内

1. **完成部署**
   - 按照检查清单逐步执行
   - 记录遇到的问题和解决方案

2. **测试验证**
   - 邀请朋友试用
   - 收集反馈

3. **监控运行**
   - 每天检查服务状态
   - 查看日志和性能指标

---

### 一个月内

1. **优化改进**
   - 修复发现的Bug
   - 根据反馈调整功能

2. **评估升级**
   - 根据使用情况决定是否升级付费方案
   - 集成真实支付系统

3. **扩展功能**
   - 添加更多高级功能
   - 优化用户体验

---

## 🎉 祝你部署顺利！

本方案已经过精心设计，确保每个步骤都清晰明确。只要按照检查清单逐步执行，就能成功完成公网部署。

**记住：**
- 📖 先阅读完整方案
- ✓ 使用检查清单跟踪进度
- 🆘 遇到问题查阅故障排查章节
- 💬 随时记录问题和解决方案

**部署成功后，你的应用将拥有：**
- ✅ 全球可访问的公网地址
- ✅ 企业级的数据安全保障
- ✅ 自动备份和恢复能力
- ✅ 专业的监控和日志系统
- ✅ 可扩展的架构设计

---

**最后更新**: 2026-05-09  
**版本**: v3.0  
**维护者**: WordStyle Team

**祝你好运！** 🚀
