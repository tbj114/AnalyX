@echo off
chcp 65001 >nul
echo ========================================
echo   AnalyX - 快速启动脚本 (Windows)
echo ========================================
echo.

echo 1. 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python 版本: %PYTHON_VERSION%
echo.

echo 2. 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo ✅ 依赖包安装完成
echo.

echo 3. 启动 AnalyX...
echo.
python src\main.py

pause
