@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0"
cd /d "%ROOT%"
echo Starting WordStyle Supabase mode...
if not exist "%ROOT%.env" if not exist "%ROOT%.streamlit\secrets.toml" (
	echo [ERROR] No Supabase configuration found.
	pause
	exit /b 1
)
if exist "%ROOT%.venv\Scripts\python.exe" (
	set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
	"%PYTHON_EXE%" -c "import streamlit" >nul 2>&1
	if errorlevel 1 set "PYTHON_EXE="
)
if not defined PYTHON_EXE for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
if not defined PYTHON_EXE (
	echo [ERROR] Python 3 not found.
	pause
	exit /b 1
)
"%PYTHON_EXE%" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
	echo [ERROR] Streamlit is not installed.
	pause
	exit /b 1
)
start "WordStyle Main App" /D "%ROOT%" "%PYTHON_EXE%" -m streamlit run app.py --server.port 8503 --server.headless true
timeout /t 3 /nobreak >nul
start "WordStyle Admin Panel" /D "%ROOT%" "%PYTHON_EXE%" -m streamlit run admin_web.py --server.port 8504 --server.headless true
echo Main: http://localhost:8503
echo Admin: http://localhost:8504
pause
