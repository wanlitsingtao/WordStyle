@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   📱 微信收款码配置工具
echo ========================================
echo.
echo 请按照以下步骤操作：
echo.
echo 1. 打开微信 → 收付款 → 二维码收款
echo 2. 点击"保存收款码"到桌面
echo 3. 将收款码图片重命名为: personal_qr_code.png
echo 4. 将该文件复制到本文件夹
echo.
echo ----------------------------------------
echo.

REM 检查是否已存在收款码
if exist "personal_qr_code.png" (
    echo ✅ 检测到已配置的收款码: personal_qr_code.png
    echo.
    choice /C YN /M "是否要替换现有收款码"
    if errorlevel 2 goto :skip_replace
)

:skip_replace
echo.
echo 💡 提示：您也可以直接在网页中上传收款码
echo.
echo    访问: http://localhost:8501
echo    在侧边栏选择充值档位后，点击"生成支付二维码"
echo    如果未检测到收款码，会显示上传按钮
echo.
echo ----------------------------------------
echo.

pause

REM 打开浏览器
start http://localhost:8501

echo.
echo 🚀 已打开应用页面，请在侧边栏测试充值功能
echo.
pause
