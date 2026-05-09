# 管理后台迁移指南

## 📋 概述

本文档说明如何从旧的 `admin_dashboard.py`（基于JSON）迁移到新的 `admin_web.py`（基于PostgreSQL）。

---

## 🔄 迁移原因

### 旧版问题

1. **数据源不一致**
   - admin_dashboard.py 读取本地 JSON 文件
   - 前端应用使用 PostgreSQL 数据库
   - 两者完全独立，无法看到真实数据

2. **功能不完整**
   - 用户管理：仅演示，未实现真实保存
   - 任务管理：无此功能
   - 订单管理：无此功能
   - 配置管理：仅读取，无法修改

3. **维护困难**
   - JSON 文件容易损坏
   - 不支持并发访问
   - 无事务保证

### 新版优势

1. **数据实时同步**
   - 直接连接 PostgreSQL
   - 显示真实的生产数据
   - 所有操作立即生效

2. **功能完整**
   - ✅ 用户管理（增删改查）
   - ✅ 任务管理（监控、状态修改）
   - ✅ 订单管理（支付、退款）
   - ✅ 系统配置（实时修改）
   - ✅ 数据看板（可视化统计）

3. **生产级可靠**
   - 数据库事务保证
   - 支持并发访问
   - 自动错误处理

---

## 🚀 迁移步骤

### 步骤1：停止旧版管理后台

如果正在运行 `admin_dashboard.py`，请先停止它：

```bash
# 在运行 admin_dashboard.py 的终端中按 Ctrl+C
```

### 步骤2：启动新版管理后台

**方式1：使用启动脚本（推荐）**

双击运行：
```
启动管理后台.bat
```

**方式2：命令行启动**

```bash
.venv\Scripts\python.exe -m streamlit run admin_web.py --server.port=8503
```

### 步骤3：访问新后台

打开浏览器访问：**http://localhost:8503**

### 步骤4：验证数据

1. 点击"📊 数据看板"
2. 查看是否显示真实的统计数据
3. 点击"👥 用户管理"
4. 确认能看到通过前端应用注册的用户

---

## 📊 功能对比表

| 功能模块 | admin_dashboard.py (旧) | admin_web.py (新) | 迁移状态 |
|---------|------------------------|-------------------|---------|
| **数据源** | 本地JSON文件 | PostgreSQL数据库 | ✅ 已迁移 |
| **用户管理** | 仅查看（演示） | 完整CRUD操作 | ✅ 已增强 |
| **转换任务** | ❌ 无此功能 | 实时监控和管理 | ✅ 新增 |
| **订单管理** | ❌ 无此功能 | 支付和退款管理 | ✅ 新增 |
| **系统配置** | 仅读取 | 可编辑保存 | ✅ 已增强 |
| **数据看板** | 简单统计 | 可视化图表 | ✅ 已增强 |
| **搜索筛选** | 基础搜索 | 高级筛选+排序 | ✅ 已增强 |
| **分页显示** | ❌ 无分页 | 支持分页 | ✅ 新增 |

---

## ⚠️ 重要注意事项

### 1. 旧版文件保留

**不要删除** `admin_dashboard.py`，暂时保留作为备份。

建议重命名：
```bash
# Windows PowerShell
Rename-Item admin_dashboard.py admin_dashboard_OLD.py

# Linux/Mac
mv admin_dashboard.py admin_dashboard_OLD.py
```

### 2. JSON文件处理

旧的 JSON 文件（user_data.json, feedback_data.json等）仍然被后端API使用：

- `feedback_data.json` - 后端反馈API仍在使用
- `comments_data.json` - 评论数据（如仍在使用）

**建议**：
- 暂时保留这些文件
- 未来可以将这些数据迁移到PostgreSQL
- 修改后端API使用数据库而非JSON

### 3. 数据一致性

由于旧版和新版使用不同的数据源，可能存在数据不一致：

| 数据类型 | 旧版位置 | 新版位置 | 是否一致 |
|---------|---------|---------|---------|
| 用户数据 | user_data.json | PostgreSQL users表 | ❌ 不一致 |
| 反馈数据 | feedback_data.json | 仍使用JSON | ✅ 一致 |
| 评论数据 | comments_data.json | 仍使用JSON | ✅ 一致 |
| 转换任务 | 无 | PostgreSQL conversion_tasks表 | N/A |
| 订单数据 | 无 | PostgreSQL orders表 | N/A |

**解决方案**：
- 以新版（PostgreSQL）为准
- 旧版JSON数据仅供参考
- 如需合并，需要手动迁移

---

## 🔧 常见问题

### Q1: 新版看不到我之前的测试数据？

**原因**：旧版读取的是 `user_data.json`，新版读取的是 PostgreSQL。

**解决**：
- 这是正常现象
- 新版的才是真实的生产数据
- 如果需要查看旧数据，可以继续使用旧版（但不推荐）

### Q2: 如何在两个版本之间切换？

**方法**：
```bash
# 启动旧版（端口8502）
streamlit run admin_dashboard.py --server.port=8502

# 启动新版（端口8503）
streamlit run admin_web.py --server.port=8503
```

然后分别访问：
- 旧版：http://localhost:8502
- 新版：http://localhost:8503

### Q3: 新版启动失败怎么办？

**检查清单**：

1. **虚拟环境是否正确**
   ```bash
   # 检查Python路径
   .venv\Scripts\python.exe --version
   ```

2. **依赖库是否安装**
   ```bash
   # 安装缺失的库
   .venv\Scripts\pip.exe install streamlit sqlalchemy psycopg2-binary
   ```

3. **数据库连接是否正常**
   ```bash
   # 测试数据库连接
   .venv\Scripts\python.exe check_db_status.py
   ```

4. **PostgreSQL是否运行**
   ```bash
   # Windows服务检查
   Get-Service postgresql*
   ```

### Q4: 能否同时运行两个版本？

**可以**，但需要使用不同端口：

```bash
# 终端1：旧版
streamlit run admin_dashboard.py --server.port=8502

# 终端2：新版
streamlit run admin_web.py --server.port=8503
```

**注意**：
- 两个版本显示的数据不同
- 建议只使用新版
- 旧版仅用于参考

---

## 📝 迁移检查清单

完成以下检查，确保迁移成功：

- [ ] 旧版管理后台已停止
- [ ] 新版管理后台已启动
- [ ] 浏览器能访问 http://localhost:8503
- [ ] 数据看板显示正确的统计数据
- [ ] 用户管理能看到真实用户
- [ ] 转换任务列表有数据
- [ ] 订单管理能看到订单记录
- [ ] 系统配置可以修改并保存
- [ ] 搜索和筛选功能正常
- [ ] 用户操作（调整余额/段落数）能生效

---

## 🎯 后续优化建议

### 1. 统一数据源

将剩余的JSON数据迁移到PostgreSQL：

- [ ] feedback_data.json → PostgreSQL feedbacks表
- [ ] comments_data.json → PostgreSQL comments表

### 2. 添加身份验证

为管理后台添加登录认证：

```python
# 示例：简单的密码保护
ADMIN_PASSWORD = "your_secure_password"

password = st.text_input("管理员密码", type="password")
if password != ADMIN_PASSWORD:
    st.error("密码错误")
    st.stop()
```

### 3. 添加操作日志

记录所有管理操作：

```python
# 创建操作日志表
class AdminLog(Base):
    __tablename__ = "admin_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    admin_user = Column(String(100))
    action = Column(String(50))  # UPDATE_USER, UPDATE_ORDER, etc.
    target_id = Column(String(64))
    old_value = Column(Text)
    new_value = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
```

### 4. 性能优化

- [ ] 为常用查询字段添加索引
- [ ] 实现缓存机制（Redis）
- [ ] 优化大数据量分页

---

## 📞 需要帮助？

如果在迁移过程中遇到问题：

1. 查看控制台错误信息
2. 检查 `app.log` 日志文件
3. 运行诊断脚本：
   ```bash
   .venv\Scripts\python.exe check_db_status.py
   ```
4. 联系开发团队

---

## ✅ 迁移完成标志

当您看到以下内容时，表示迁移成功：

- ✅ 新版管理后台正常运行
- ✅ 能看到真实的生产数据
- ✅ 所有功能模块正常工作
- ✅ 可以进行用户、任务、订单管理
- ✅ 系统配置可以修改并保存

**恭喜！您已成功迁移到新版Web管理后台！**

---

**文档版本**: v1.0  
**创建日期**: 2026-05-07  
**适用版本**: WordStyle Pro v2.9.0+
