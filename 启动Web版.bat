@echo off
chcp 65001 >nul
echo ========================================
echo   启动 Web 版文档转换工具
echo ========================================
echo.

REM 检查是否安装了 streamlit
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements_web.txt
    echo.
)

echo [启动] 正在启动 Streamlit 应用...
echo [提示] 浏览器会自动打开 http://localhost:8501
echo [提示] 按 Ctrl+C 可停止服务
echo.

streamlit run app.py --server.port 8501 --server.headless false

pause
