@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo                    WordStyle - GitHub提交准备工具
echo ================================================================================
echo.
echo 此脚本将帮助您完成以下任务：
echo   1. 清理与程序运行无关的文件
echo   2. 检查.gitignore配置
echo   3. 生成Git提交命令
echo   4. 提供后续步骤指南
echo.
echo ================================================================================
echo.

:menu
echo 请选择要执行的操作：
echo.
echo [1] 预览将要删除的文件（不实际删除）
echo [2] 执行文件清理（会删除约180个文件）
echo [3] 查看数据库对比文档
echo [4] 查看GitHub提交流程
echo [5] 生成Git提交命令
echo [6] 查看所有文档列表
echo [0] 退出
echo.
set /p choice="请输入选项 (0-6): "

if "%choice%"=="1" goto preview
if "%choice%"=="2" goto cleanup
if "%choice%"=="3" goto db_doc
if "%choice%"=="4" goto git_flow
if "%choice%"=="5" goto git_commands
if "%choice%"=="6" goto doc_list
if "%choice%"=="0" goto end
goto menu

:preview
echo.
echo ================================================================================
echo                          预览将要删除的文件
echo ================================================================================
echo.
python cleanup_for_github.py
echo.
echo 提示: 以上只是预览，没有实际删除文件。
echo       如需执行删除，请选择选项 [2]
echo.
pause
goto menu

:cleanup
echo.
echo ================================================================================
echo                            执行文件清理
echo ================================================================================
echo.
echo ⚠️  警告: 此操作将删除约180个文件，释放约50MB空间！
echo.
echo 将被删除的文件类型包括：
echo   - 测试脚本 (test_*.py, analyze_*.py, etc.)
echo   - 修复脚本 (fix_*.py, apply_*.py, etc.)
echo   - 临时文件 (*.log, *.bak, result_*.docx, etc.)
echo   - 文档报告 (*优化*.md, *修复*.md, etc.)
echo   - 截图和图片 (*.png, *.jpg)
echo.
echo 保留的核心文件：
echo   - app.py, doc_converter.py, doc_converter_gui.py
echo   - backend/ 目录
echo   - README.md, QUICK_DEPLOY.md, 等关键文档
echo.
set /p confirm="确认执行清理？(yes/no): "
if /i "%confirm%"=="yes" (
    echo.
    echo 开始清理...
    python cleanup_for_github.py
    echo.
    echo ✅ 清理完成！
    echo.
    echo 下一步：
    echo   1. 检查 .gitignore 配置
    echo   2. 执行 Git 提交（选择选项 [5]）
    echo.
) else (
    echo.
    echo ❌ 已取消操作
    echo.
)
pause
goto menu

:db_doc
echo.
echo ================================================================================
echo                          数据库对比文档
echo ================================================================================
echo.
echo 文档位置: DATABASE_COMPARISON_AND_UPGRADE.md
echo.
echo 主要内容包括：
echo   1. 本地SQLite vs 后端PostgreSQL详细对比
echo   2. 三种升级方案（A/B/C）
echo   3. 技术迁移指南
echo   4. 成本分析
echo.
echo 正在打开文档...
start "" "DATABASE_COMPARISON_AND_UPGRADE.md"
echo.
pause
goto menu

:git_flow
echo.
echo ================================================================================
echo                         GitHub提交流程
echo ================================================================================
echo.
echo 完整流程请查看: GITHUB_SUBMISSION_PLAN.md
echo.
echo 简要步骤：
echo.
echo 第1步: 清理文件
echo   python cleanup_for_github.py
echo.
echo 第2步: 初始化Git（如未初始化）
echo   git init
echo   git add .gitignore
echo   git commit -m "Initial commit with .gitignore"
echo.
echo 第3步: 添加所有文件
echo   git add .
echo.
echo 第4步: 首次提交
echo   git commit -m "feat: Initial release - WordStyle v1.0.0"
echo.
echo 第5步: 创建GitHub仓库
echo   访问 https://github.com/new 创建新仓库
echo.
echo 第6步: 关联远程仓库并推送
echo   git remote add origin https://github.com/YOUR_USERNAME/WordStyle.git
echo   git branch -M main
echo   git push -u origin main
echo.
echo 第7步: 创建版本标签
echo   git tag v1.0.0
echo   git push origin v1.0.0
echo.
pause
goto menu

:git_commands
echo.
echo ================================================================================
echo                         Git提交命令
echo ================================================================================
echo.
echo 复制以下命令到命令行执行：
echo.
echo ----------------------------------------------------------------
echo # 1. 添加所有文件
echo git add .
echo.
echo # 2. 检查状态（确认没有敏感文件）
echo git status
echo.
echo # 3. 首次提交
echo git commit -m "feat: Initial release - WordStyle v1.0.0
echo.
echo - Core document conversion engine
echo - Web UI ^(Streamlit^)
echo - Desktop GUI ^(Tkinter^)
echo - Backend API ^(FastAPI^)
echo - User management system
echo - WeChat login integration
echo - Comment and feedback system
echo - Complete deployment guides"
echo.
echo # 4. 关联远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
echo git remote add origin https://github.com/YOUR_USERNAME/WordStyle.git
echo.
echo # 5. 推送到GitHub
echo git branch -M main
echo git push -u origin main
echo.
echo # 6. 创建版本标签
echo git tag v1.0.0
echo git push origin v1.0.0
echo ----------------------------------------------------------------
echo.
echo 提示: 
echo   - 如果已有远程仓库，跳过第4步
echo   - 推送前务必检查 git status，确保没有敏感文件
echo.
pause
goto menu

:doc_list
echo.
echo ================================================================================
echo                          文档列表
echo ================================================================================
echo.
echo 📚 必读文档（按重要性排序）：
echo.
echo 1. EXECUTION_SUMMARY.md          - 执行摘要（快速参考）⭐
echo 2. GITHUB_SUBMISSION_PLAN.md     - GitHub提交完整方案 ⭐
echo 3. README_GITHUB.md              - GitHub项目主页 ⭐
echo 4. QUICK_DEPLOY.md               - 15分钟快速部署 ⭐
echo 5. DATABASE_COMPARISON_AND_UPGRADE.md - 数据库对比与升级 ⭐
echo.
echo 📖 参考文档：
echo.
echo 6. DEPLOYMENT_GUIDE.md           - 详细部署指南
echo 7. deploy_checklist.md           - 部署检查清单
echo 8. PRODUCTION_SYSTEM_PLAN.md     - 生产级系统规划
echo 9. IMPLEMENTATION_GUIDE.md       - 实施指南
echo 10. BACKEND_COMPLETED.md         - 后端完成说明
echo.
echo 🔧 工具脚本：
echo.
echo 11. cleanup_for_github.py        - 文件清理脚本
echo 12. prepare_github.bat           - 本脚本
echo.
echo 💡 提示: 
echo    使用 start 命令打开文档，例如：
echo    start "" "EXECUTION_SUMMARY.md"
echo.
pause
goto menu

:end
echo.
echo ================================================================================
echo                              再见！
echo ================================================================================
echo.
echo 祝您提交顺利，项目成功！🚀
echo.
echo 如有问题，请查阅相关文档或提交Issue。
echo.
pause
exit
