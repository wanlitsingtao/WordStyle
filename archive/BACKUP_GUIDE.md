# LingMa 项目备份指南

> 本文档帮助你备份和恢复整个项目，包括代码、对话历史和配置。

---

## 📁 一、需要备份的文件

### **1. 核心代码文件**（必须备份）
```
e:\LingMa\
├── doc_converter.py          # 核心转换引擎
├── doc_converter_gui.py      # GUI 界面
├── app.py                    # Web 版（Streamlit）
├── requirements.txt          # 桌面版依赖
├── requirements_web.txt      # Web 版依赖
└── README_WEB.md             # Web 版文档
```

### **2. 配置文件**（可选）
```
├── user_data.json            # 用户额度数据（Web 版）
└── *.bat                     # 启动脚本
```

### **3. 对话历史**（重要参考）
```
C:\Users\wanli\.lingma\cache\projects\LingMa-45f45724\conversation-history\
└── ebb5dd7d.txt              # 当前对话历史
```

### **4. 测试文档**（可选，体积较大）
```
├── 8js1.docx
├── 8js2.docx
├── 8js3.docx
└── jn.docx
```

---

## 🚀 二、推荐备份方案

### **方案 A：Git + GitHub（强烈推荐）** ⭐⭐⭐⭐⭐

#### **首次设置：**
```bash
cd e:\LingMa

# 1. 初始化 Git
git init

# 2. 创建 .gitignore（排除不必要文件）
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo *.docx >> .gitignore
echo *.log >> .gitignore
echo nul >> .gitignore
echo ~$* >> .gitignore
echo user_data.json >> .gitignore

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "初始提交：文档转换工具 MVP v1.0"

# 5. 推送到 GitHub
git remote add origin https://github.com/你的用户名/LingMa.git
git push -u origin main
```

#### **日常使用：**
```bash
# 每次修改后提交
git add .
git commit -m "描述你的修改"
git push
```

#### **重装后恢复：**
```bash
git clone https://github.com/你的用户名/LingMa.git
cd LingMa
pip install -r requirements.txt
pip install -r requirements_web.txt
```

**优点：**
- ✅ 自动版本管理
- ✅ 可以随时回退
- ✅ 跨设备同步
- ✅ 免费（GitHub 私有仓库免费）
- ✅ 协作友好

---

### **方案 B：压缩包备份** ⭐⭐⭐

#### **创建备份脚本：** `backup.bat`
```batch
@echo off
set BACKUP_DIR=E:\Backups\LingMa
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo 正在备份...
tar -czf "%BACKUP_DIR%\LingMa_%TIMESTAMP%.tar.gz" ^
    --exclude="*.pyc" ^
    --exclude="__pycache__" ^
    --exclude=".git" ^
    --exclude="*.docx" ^
    --exclude="*.log" ^
    --exclude="nul" ^
    E:\LingMa\

echo 备份完成：%BACKUP_DIR%\LingMa_%TIMESTAMP%.tar.gz
pause
```

#### **使用方法：**
1. 双击运行 `backup.bat`
2. 备份文件保存在 `E:\Backups\LingMa\`
3. 建议每周备份一次

#### **重装后恢复：**
```bash
tar -xzf E:\Backups\LingMa\LingMa_20260425_120000.tar.gz -C E:\
```

---

### **方案 C：云盘同步** ⭐⭐⭐⭐

#### **支持的云服务：**
- OneDrive（Windows 自带）
- 百度网盘
- 坚果云
- Dropbox
- Google Drive

#### **操作步骤：**
1. 安装云盘客户端
2. 将 `E:\LingMa` 文件夹移动到云盘同步目录
   - 例如：`C:\Users\wanli\OneDrive\Projects\LingMa`
3. 等待同步完成

#### **重装后恢复：**
1. 安装云盘客户端
2. 登录账号
3. 文件会自动同步回来

**注意：**
- 建议在 `.gitignore` 中排除大文件（*.docx）
- 或者单独设置不同步测试文档

---

## 💬 三、对话历史备份

### **方法 1：手动复制**
```bash
# 复制对话历史到安全位置
copy "C:\Users\wanli\.lingma\cache\projects\LingMa-45f45724\conversation-history\ebb5dd7d.txt" E:\Backups\

# 或者重命名为有意义的名字
copy "C:\Users\wanli\.lingma\cache\projects\LingMa-45f45724\conversation-history\ebb5dd7d.txt" E:\Backups\LingMa_Conversation_20260425.txt
```

### **方法 2：导出项目总结**
让 AI 助手生成项目总结文档（包含技术决策、架构说明等）

---

## 🔧 四、环境配置备份

### **1. Python 版本**
```bash
python --version
# 记录版本号，例如：Python 3.9.7
```

### **2. 已安装的包**
```bash
pip freeze > requirements_full.txt
```

### **3. 系统环境变量**
```bash
# Windows
set > env_backup.txt
```

---

## 📋 五、完整备份检查清单

重装前，确保已完成以下操作：

- [ ] **代码备份**
  - [ ] 已推送到 GitHub / 已创建压缩包 / 已同步到云盘
  
- [ ] **对话历史备份**
  - [ ] 已复制 `ebb5dd7d.txt` 到安全位置
  
- [ ] **依赖记录**
  - [ ] 已运行 `pip freeze > requirements_full.txt`
  
- [ ] **Python 版本记录**
  - [ ] 已记录当前 Python 版本
  
- [ ] **重要数据备份**
  - [ ] 已备份 `user_data.json`（如果有重要用户数据）
  
- [ ] **文档备份**
  - [ ] 已备份重要的测试文档（如果需要）

---

## 🔄 六、重装后恢复步骤

### **第 1 步：恢复代码**
```bash
# 如果使用 Git
git clone https://github.com/你的用户名/LingMa.git

# 如果使用压缩包
tar -xzf 备份文件.tar.gz -C E:\

# 如果使用云盘
# 等待同步完成
```

### **第 2 步：安装 Python**
- 下载并安装与之前相同版本的 Python
- 下载地址：https://www.python.org/downloads/

### **第 3 步：安装依赖**
```bash
cd E:\LingMa
pip install -r requirements.txt
pip install -r requirements_web.txt
```

### **第 4 步：恢复对话历史**
```bash
# 复制回原位置
copy E:\Backups\ebb5dd7d.txt "C:\Users\wanli\.lingma\cache\projects\LingMa-45f45724\conversation-history\"
```

### **第 5 步：验证安装**
```bash
# 测试桌面版
python doc_converter_gui.py

# 测试 Web 版
streamlit run app.py
```

---

## 💡 七、最佳实践建议

### **1. 定期备份**
- 每次重大修改后备份
- 至少每周备份一次

### **2. 使用 Git（强烈推荐）**
- 学习基本的 Git 命令
- 每次提交写清晰的注释
- 使用分支管理不同功能

### **3. 云端 + 本地双重备份**
- GitHub 作为主备份
- 本地压缩包作为额外保险

### **4. 记录重要决策**
- 在代码中添加注释
- 维护 CHANGELOG.md
- 保存关键的对话历史

### **5. 测试恢复流程**
- 定期尝试从备份恢复
- 确保备份文件可用

---

## 🆘 八、常见问题

### **Q1: 我不记得 GitHub 密码怎么办？**
A: 可以使用 SSH 密钥认证，或者重置密码。

### **Q2: 备份文件太大怎么办？**
A: 
- 排除 `*.docx`、`*.log` 等大文件
- 使用压缩格式（.tar.gz 或 .zip）
- 只备份源代码，不备份测试数据

### **Q3: 重装后 Python 版本不同怎么办？**
A: 
- 尽量安装相同版本
- 如果版本差异不大，通常可以兼容
- 如果有问题，重新安装依赖即可

### **Q4: 对话历史文件找不到怎么办？**
A: 
- 搜索 `.lingma` 文件夹
- 或者让 AI 重新生成项目总结

---

## 📞 九、快速恢复命令汇总

```bash
# Git 方式
git clone https://github.com/你的用户名/LingMa.git
cd LingMa
pip install -r requirements.txt
pip install -r requirements_web.txt

# 压缩包方式
tar -xzf LingMa_20260425.tar.gz -C E:\
cd E:\LingMa
pip install -r requirements.txt
pip install -r requirements_web.txt

# 验证
python doc_converter_gui.py
streamlit run app.py
```

---

**最后提醒：** 现在就行动！不要等到重装后才后悔没有备份。

**推荐立即执行：**
1. ✅ 初始化 Git 仓库
2. ✅ 推送到 GitHub
3. ✅ 备份对话历史

祝你使用愉快！🎉
