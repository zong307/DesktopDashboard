@echo off
REM DesktopDashboard - Windows Build Script (PyInstaller)
REM Usage: Activate your environment first, then run this script.
REM Example: conda activate py312
REM          scripts\build.bat

echo ============================================
echo   DesktopDashboard Windows Build
echo ============================================
echo.

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    echo.
    echo Please activate your conda environment first:
    echo   conda activate py312
    echo.
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python found: %PYTHON_VERSION%

REM Check PySide6
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] PySide6 not installed.
    echo.
    echo Please install dependencies:
    echo   pip install PySide6 PySide6-Addons
    echo.
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)
echo [OK] PySide6 installed.

REM Check PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install PyInstaller.
        echo Please install it manually:
        echo   pip install pyinstaller
        echo.
        pause
        exit /b 1
    )
    echo [OK] PyInstaller installed.
)

echo.
echo Building executable...

REM Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "DesktopDashboard.spec" del /q "DesktopDashboard.spec"

python -m PyInstaller ^
    --name DesktopDashboard ^
    --onedir ^
    --windowed ^
    --hidden-import PySide6.QtCore ^
    --hidden-import PySide6.QtGui ^
    --hidden-import PySide6.QtWidgets ^
    --hidden-import PySide6.QtNetwork ^
    --hidden-import yaml ^
    --add-data "config;config" ^
    --add-data "src;src" ^
    src\main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Please check the errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build complete!
echo   Executable: dist\DesktopDashboard\DesktopDashboard.exe
echo ============================================
echo.
pause
