@echo off
REM 自动化测试运行脚本 - Windows版本

echo.
echo ========================================
echo   WordStyle 自动化测试启动器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查测试依赖...
pip list | findstr pytest >nul
if errorlevel 1 (
    echo [提示] 正在安装测试依赖...
    pip install -r requirements-test.txt
) else (
    echo [OK] 测试依赖已安装
)

echo.
echo [2/4] 检查应用状态...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [警告] 后端服务未运行
    echo.
    choice /C YN /M "是否启动后端服务"
    if errorlevel 2 goto skip_backend
    if errorlevel 1 (
        echo [提示] 请在新终端窗口运行: cd backend ^&^& uvicorn app.main:app --reload
        pause
    )
) else (
    echo [OK] 后端服务正常运行
)

:skip_backend
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo [警告] 前端服务未运行
    echo.
    choice /C YN /M "是否启动前端服务"
    if errorlevel 2 goto skip_frontend
    if errorlevel 1 (
        echo [提示] 请在新终端窗口运行: streamlit run app.py
        pause
    )
) else (
    echo [OK] 前端服务正常运行
)

:skip_frontend
echo.
echo [3/4] 选择测试类型:
echo.
echo   1. 快速Demo测试（推荐首次使用）
echo   2. API接口测试
echo   3. UI自动化测试
echo   4. 性能测试
echo   5. 完整测试套件
echo   6. 生成HTML报告
echo.
set /p test_type="请输入选项(1-6): "

echo.
echo [4/4] 执行测试...
echo.

if "%test_type%"=="1" (
    python tests\demo_quick_test.py
) else if "%test_type%"=="2" (
    pytest tests\test_api.py -v -s
) else if "%test_type%"=="3" (
    pytest tests\test_ui.py -v -s
) else if "%test_type%"=="4" (
    pytest tests\test_performance.py -v -s -m "not slow"
) else if "%test_type%"=="5" (
    pytest tests\ -v -m "not slow"
) else if "%test_type%"=="6" (
    pytest tests\ -v --html=test_report.html --self-contained-html
    echo.
    echo [完成] HTML报告已生成: test_report.html
    start test_report.html
) else (
    echo [错误] 无效选项
)

echo.
echo ========================================
echo   测试完成
echo ========================================
echo.
pause
