#!/bin/bash
# DesktopDashboard - macOS / Linux Build Script (PyInstaller)
# Usage: Activate your environment first, then run this script.
# Example: conda activate py312
#          chmod +x scripts/build.sh && ./scripts/build.sh

set -e

echo "============================================"
echo "  DesktopDashboard Build ($(uname -s))"
echo "============================================"
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 not found in PATH."
    echo
    echo "Please activate your conda environment first:"
    echo "  conda activate py312"
    echo
    echo "Then run this script again."
    echo
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "[OK] Python found: $PYTHON_VERSION"

# Check PySide6
python3 -c "import PySide6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo
    echo "[ERROR] PySide6 not installed."
    echo
    echo "Please install dependencies:"
    echo "  pip install PySide6 PySide6-Addons"
    echo
    echo "Then run this script again."
    echo
    exit 1
fi
echo "[OK] PySide6 installed."

# Check PyInstaller
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo
    echo "[WARNING] PyInstaller not found. Installing..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo
        echo "[ERROR] Failed to install PyInstaller."
        echo "Please install it manually:"
        echo "  pip install pyinstaller"
        echo
        exit 1
    fi
    echo "[OK] PyInstaller installed."
fi

echo
echo "Building executable..."

# Clean previous build
rm -rf dist build DesktopDashboard.spec

python3 -m PyInstaller \
    --name DesktopDashboard \
    --onedir \
    --windowed \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtGui \
    --hidden-import PySide6.QtWidgets \
    --hidden-import PySide6.QtNetwork \
    --hidden-import yaml \
    --add-data "config:config" \
    --add-data "src:src" \
    src/main.py

if [ $? -ne 0 ]; then
    echo
    echo "[ERROR] Build failed. Please check the errors above."
    exit 1
fi

echo
echo "============================================"
echo "  Build complete!"
echo "  Executable: dist/DesktopDashboard/DesktopDashboard"
echo "============================================"
