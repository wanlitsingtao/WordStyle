@echo off
chcp 65001 >nul
echo ========================================
echo   Word文档转换工具 - 环境修复脚本
echo ========================================
echo.

cd /d E:\LingMa\WordStyle

echo [步骤 1/5] 检查Python是否可用...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [成功] Python已安装

echo.
echo [步骤 2/5] 删除旧的虚拟环境...
if exist ".venv" (
    echo 正在删除旧的虚拟环境...
    rmdir /s /q .venv
    if errorlevel 1 (
        echo [警告] 删除失败，可能有进程占用
        echo 请关闭所有Python进程后重试
        pause
        exit /b 1
    )
    echo [成功] 旧虚拟环境已删除
) else (
    echo 虚拟环境不存在，跳过此步骤
)

echo.
echo [步骤 3/5] 创建新的虚拟环境...
python -m venv .venv
if errorlevel 1 (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
)
echo [成功] 虚拟环境创建完成

echo.
echo [步骤 4/5] 验证虚拟环境...
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 虚拟环境创建不完整，缺少python.exe
    pause
    exit /b 1
)
if not exist ".venv\Scripts\pip.exe" (
    echo [错误] 虚拟环境创建不完整，缺少pip.exe
    pause
    exit /b 1
)
echo [成功] 虚拟环境验证通过

echo.
echo [步骤 5/5] 安装依赖包...
echo 这可能需要几分钟时间，请耐心等待...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements_web.txt
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    echo 请检查网络连接或手动运行: .venv\Scripts\pip.exe install -r requirements_web.txt
    pause
    exit /b 1
)
echo [成功] 依赖包安装完成

echo.
echo ========================================
echo   环境修复完成！
echo ========================================
echo.
echo 现在您可以：
echo 1. 运行 "启动Web应用.bat" 启动Web版
echo 2. 运行 "启动转换工具.bat" 启动GUI版
echo.
echo 如果仍有问题，请查看上面的错误信息
echo.
pause
