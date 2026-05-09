# WordStyle Pro - Web管理后台

## 🎯 简介

这是WordStyle Pro的**全新Web管理后台**，基于PostgreSQL数据库开发，提供完整的用户管理、任务监控、订单管理和系统配置功能。

---

## ✨ 主要特性

- ✅ **实时数据**：直接连接PostgreSQL，显示真实生产数据
- ✅ **五大模块**：数据看板、用户管理、任务管理、订单管理、系统配置
- ✅ **操作便捷**：搜索、筛选、分页、批量操作
- ✅ **可视化统计**：关键指标卡片和图表展示
- ✅ **响应式设计**：适配各种屏幕尺寸

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd e:\LingMa\WordStyle\backend
..\.venv\Scripts\pip.exe install -r requirements.txt
```

### 2. 启动管理后台

**方式1：双击启动脚本（推荐）**
```
启动管理后台.bat
```

**方式2：命令行启动**
```bash
.venv\Scripts\python.exe -m streamlit run admin_web.py --server.port=8503
```

### 3. 访问地址

打开浏览器：**http://localhost:8503**

---

## 📊 功能模块

### 1️⃣ 数据看板
- 关键指标：用户数、任务数、收入、成功率
- 任务状态分布统计
- 最近活动展示

### 2️⃣ 用户管理
- 搜索和筛选用户
- 调整剩余段落数
- 调整账户余额
- 启用/禁用账户

### 3️⃣ 转换任务管理
- 实时监控任务状态
- 按状态和日期筛选
- 标记任务完成/失败
- 查看错误信息

### 4️⃣ 订单管理
- 查看所有订单记录
- 标记为已支付（自动增加用户段落）
- 标记为退款（自动扣除用户段落）
- 查看交易详情

### 5️⃣ 系统配置
- 设置首次登录赠送段落数
- 管理所有系统配置项
- 实时保存并生效

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [ADMIN_WEB_GUIDE.md](ADMIN_WEB_GUIDE.md) | 完整使用指南 |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | 从旧版迁移指南 |
| [WEB_ADMIN_COMPLETION_REPORT.md](WEB_ADMIN_COMPLETION_REPORT.md) | 开发完成报告 |

---

## 🔧 技术栈

- **前端框架**: Streamlit
- **后端API**: FastAPI
- **数据库**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **部署**: Render + Streamlit Cloud

---

## ⚠️ 注意事项

1. **不要公开暴露管理后台** - 仅在内网或本地访问
2. **定期备份数据库** - 防止数据丢失
3. **谨慎操作用户数据** - 避免误操作
4. **确保依赖已安装** - 运行前检查requirements.txt

---

## 🆘 常见问题

**Q: 看不到数据？**
- 检查PostgreSQL是否运行
- 检查backend/.env配置
- 运行 `test_admin.py` 诊断

**Q: 启动失败？**
- 确认虚拟环境正确
- 安装缺失的依赖库
- 检查端口8503是否被占用

**Q: 修改配置不生效？**
- 点击"保存配置"按钮
- 刷新页面查看最新数据

---

## 📞 技术支持

遇到问题请：
1. 查看控制台错误日志
2. 检查 app.log 文件
3. 运行诊断脚本：`.venv\Scripts\python.exe test_admin.py`

---

**版本**: v2.9.0  
**最后更新**: 2026-05-07  
**许可证**: MIT
