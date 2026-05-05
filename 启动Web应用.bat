@echo off
chcp 65001 >nul
echo ========================================
echo   Word文档转换工具 - Web版
echo ========================================
echo.

cd /d E:\LingMa\WordStyle

REM 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 虚拟环境不存在，请先运行“修复环境.bat”
    pause
    exit /b 1
)

echo [检查] 验证依赖包...
.venv\Scripts\python.exe -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [警告] streamlit未安装，正在安装依赖...
    .venv\Scripts\python.exe -m pip install -r requirements_web.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo 正在启动Web应用...
echo.
echo 浏览器将自动打开 http://localhost:8501
echo 按 Ctrl+C 可以停止服务
echo.
echo ========================================
echo.

.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true

if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请检查错误信息
    pause
)
