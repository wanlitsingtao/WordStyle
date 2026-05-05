@echo off
chcp 65001 >nul
echo ========================================
echo   WordStyle Pro - 完整启动
echo ========================================
echo.

cd /d %~dp0

echo [1/3] 启动后端服务...
start "WordStyle Pro Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe run_dev.py"
echo ✅ 后端服务已启动（新窗口）
echo    访问地址: http://localhost:8000/docs
echo.

echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] 启动前端服务...
start "WordStyle Pro Frontend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m streamlit run app_with_wechat_login.py --server.port=8502"
echo ✅ 前端服务已启动（新窗口）
echo    访问地址: http://localhost:8502
echo.

timeout /t 3 /nobreak >nul

echo.
echo [3/3] 打开浏览器...
start http://localhost:8502
echo ✅ 浏览器已打开
echo.

echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 📱 微信扫码登录页面: http://localhost:8502
echo 📖 API 文档: http://localhost:8000/docs
echo.
echo 提示：
echo - 两个服务分别在独立窗口运行
echo - 关闭窗口即可停止对应服务
echo - 按 F11 可以全屏浏览
echo.
echo 按任意键关闭此窗口...
pause >nul
