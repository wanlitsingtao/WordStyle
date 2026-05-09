# WordStyle - 智能文档转换工具 📄

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-orange.svg)](https://fastapi.tiangolo.com/)

一个功能强大的Word文档格式自动化工具，专为标书制作和文档标准化设计。支持样式转换、语气优化、批量处理，并提供Web界面和完整的用户管理系统。

---

## ✨ 核心功能

### 🎯 文档转换引擎
- **智能样式映射**：自动识别并转换文档样式，保持格式一致性
- **祈使语气优化**：自动将招标要求转换为投标人口吻（"必须"→"将"）
- **应答句自动插入**：在标题后智能插入标准应答语句
- **表格和图片处理**：完整保留表格结构、合并单元格、图片和Visio对象
- **批量转换**：支持同时处理多个文档，提升工作效率

### 🌐 Web应用（生产级）
- **微信扫码登录**：集成微信OAuth，一键登录
- **用户管理系统**：完整的注册、登录、额度管理
- **按量付费**：段落数计费，灵活充值
- **实时进度追踪**：前台/后台双模式，随时查看转换进度
- **历史记录**：持久化保存所有转换记录
- **评论反馈系统**：用户可提交需求和建议

### 💻 桌面GUI（离线版）
- **Tkinter图形界面**：无需浏览器，本地运行
- **单文件/批量模式**：灵活选择处理方式
- **自定义样式映射**：精细控制转换规则
- **实时日志显示**：详细记录转换过程

---

## 🚀 快速开始

### 方式一：Web版本（推荐）

#### 1. 安装依赖
```bash
pip install -r requirements_web.txt
```

#### 2. 启动应用
```bash
# Windows
启动Web应用.bat

# 或手动启动
streamlit run app.py --server.port 8501
```

#### 3. 访问应用
打开浏览器访问：http://localhost:8501

---

### 方式二：桌面GUI版本

#### 1. 安装依赖
```bash
pip install python-docx Pillow
```

#### 2. 启动应用
```bash
# Windows
启动转换工具.bat

# 或手动启动
python doc_converter_gui.py
```

---

## 📦 部署方案

我们提供三种部署方案，满足不同场景需求：

### 方案A：本地单机部署（个人使用）
- ✅ 零成本
- ✅ 简单易用
- ❌ 不支持多用户
- 📖 适合：个人或小团队内部使用

### 方案B：云端免费部署（小规模商用）
- ✅ 完全免费
- ✅ 公网访问
- ✅ 完整用户系统
- ⏱️ 15分钟部署
- 📖 详细指南：[QUICK_DEPLOY.md](QUICK_DEPLOY.md)

**架构**：
```
Streamlit Cloud (前端) → Render (后端API) → Supabase (数据库)
```

### 方案C：生产级部署（大规模商用）
- ✅ 高性能
- ✅ 高可用
- ✅ 真实微信支付
- 💰 ¥100-300/月
- 📖 详细指南：[DATABASE_COMPARISON_AND_UPGRADE.md](DATABASE_COMPARISON_AND_UPGRADE.md)

**架构选项**：
- 云服务器 + Docker
- Serverless架构（Vercel + Railway + Supabase Pro）

---

## 🏗️ 技术栈

### 前端
- **Streamlit**: Web UI框架
- **HTML/CSS**: 自定义样式

### 后端
- **FastAPI**: RESTful API框架
- **SQLAlchemy**: ORM数据库操作
- **Pydantic**: 数据验证

### 数据库
- **SQLite**: 本地开发（轻量级）
- **PostgreSQL**: 生产环境（通过Supabase）

### 文档处理
- **python-docx**: Word文档解析和生成
- **Pillow**: 图片处理

### 认证与支付
- **微信OAuth**: 扫码登录
- **个人收款码**: 简易充值方案
- **JWT**: Token认证

---

## 📁 项目结构

```
WordStyle/
├── app.py                      # Streamlit主应用（Web版）
├── doc_converter.py            # 核心转换引擎
├── doc_converter_gui.py        # Tkinter桌面GUI
├── task_manager.py             # 任务管理（SQLite）
├── user_manager.py             # 用户管理
├── comments_manager.py         # 评论和反馈管理
├── config.py                   # 配置管理
├── utils.py                    # 工具函数
│
├── backend/                    # 后端API服务
│   ├── app/
│   │   ├── main.py            # FastAPI入口
│   │   ├── models.py          # 数据模型
│   │   ├── schemas.py         # Pydantic schema
│   │   ├── api/               # API路由
│   │   └── core/              # 核心配置
│   ├── init_db.py             # 数据库初始化
│   └── requirements.txt       # 后端依赖
│
├── conversion_results/         # 转换结果存储
├── uploads/                    # 临时上传文件
│
├── README.md                   # 本文档
├── QUICK_DEPLOY.md            # 快速部署指南
├── DATABASE_COMPARISON_AND_UPGRADE.md  # 数据库对比与升级方案
├── requirements.txt           # 桌面版依赖
├── requirements_web.txt       # Web版依赖
└── .gitignore                 # Git忽略规则
```

---

## 📊 数据库结构

项目支持两种数据库方案：

### 本地SQLite（单机版）
- 1个表：`conversion_tasks`
- 轻量级，无需配置
- 适合个人使用

### PostgreSQL（生产版）
- 4个表：`users`, `orders`, `conversion_tasks`, `system_config`
- 完整用户管理和订单系统
- 支持高并发和分布式部署

📖 详细对比：[DATABASE_COMPARISON_AND_UPGRADE.md](DATABASE_COMPARISON_AND_UPGRADE.md)

---

## 🔧 配置说明

### 环境变量（后端）

创建 `backend/.env` 文件：

```env
# 数据库连接
DATABASE_URL=postgresql://user:pass@host/dbname

# JWT密钥（生产环境请使用强随机字符串）
SECRET_KEY=your-secret-key-here

# CORS允许的来源
ALLOWED_ORIGINS=https://*.streamlit.app,http://localhost:8501

# 调试模式（生产环境设为false）
DEBUG=false
```

### 系统配置（动态调整）

通过 `system_config` 表管理：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `free_paragraphs_on_first_login` | 10000 | 新用户免费额度 |
| `min_recharge_amount` | 1.0 | 最低充值金额（元） |
| `paragraph_price` | 0.001 | 每段落价格（元） |

---

## 📝 使用示例

### Web版操作流程

1. **微信扫码登录**
   - 点击"微信登录"按钮
   - 扫描二维码
   - 自动获取用户信息

2. **上传文档**
   - 拖拽或选择源文档（支持多选）
   - 上传模板文档
   - 系统自动分析样式和段落数

3. **开始转换**
   - 点击"开始转换"
   - 实时查看进度条
   - 可切换为后台模式

4. **下载结果**
   - 转换完成后自动显示下载链接
   - 支持批量下载
   - 文件保留7天

### 桌面版操作流程

1. **选择文件**
   - 单文件模式：选择一个源文档
   - 多文件模式：批量选择多个文档

2. **配置选项**
   - ☑ 祈使语气转换
   - ☑ 插入应答句
   - ☐ 自定义样式映射（单文件模式）

3. **开始转换**
   - 查看实时日志
   - 等待完成提示

---

## 🎨 界面预览

### Web版主要功能
- 👤 用户信息中心（余额、统计）
- 📋 转换历史对话框
- 💡 需求反馈对话框
- 📊 实时进度追踪
- 💬 评论区互动

### 桌面版界面
- 📂 文件选择器
- ⚙️ 转换配置面板
- 📝 实时日志显示
- 🎯 样式映射对话框

---

## 🐛 常见问题

### Q: 为什么图片没有自动调整大小？
**A**: 请确保已安装Pillow库：`pip install Pillow`

### Q: 转换后的表格格式不正确？
**A**: 
1. 检查模板文档是否包含所需样式
2. 查看错误日志文件（`*_err.log`）
3. 使用自定义样式映射手动指定

### Q: Web版无法连接后端API？
**A**:
1. 确认后端服务已启动
2. 检查`.streamlit/secrets.toml`中的URL配置
3. 查看浏览器控制台是否有CORS错误

### Q: 如何修改免费额度？
**A**: 编辑 `config.py` 中的 `FREE_PARAGRAPHS_ON_FIRST_LOGIN` 常量，或通过后端API修改 `system_config` 表。

### Q: 支持哪些Word版本？
**A**: 支持 `.docx` 格式（Word 2007+），不支持旧版 `.doc` 格式。

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- 📧 Email: [your-email@example.com]
- 💬 微信: [your-wechat-id]
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/WordStyle/issues)

---

## 🙏 致谢

感谢以下开源项目：
- [Streamlit](https://streamlit.io/) - Web UI框架
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能API框架
- [python-docx](https://python-docx.readthedocs.io/) - Word文档处理
- [Supabase](https://supabase.com/) - 开源Firebase替代品

---

**⭐ 如果这个项目对你有帮助，请给个Star！**

最后更新：2026-05-07  
版本：v1.0.0
