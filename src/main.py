"""
DesktopDashboard - Entry point.

Usage:
    python src/main.py
"""

from __future__ import annotations

import signal
import sys
from pathlib import Path

# Ensure the project root is on the Python path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from src.app.config import load_settings
from src.app.widget import StickyNoteWindow, SystemTray


def main() -> None:
    # High DPI support
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("DesktopDashboard")
    app.setApplicationVersion("0.1.0")
    app.setStyle("Fusion")

    # Ctrl+C handler for console
    signal.signal(signal.SIGINT, lambda *a: QApplication.quit())

    # Load configuration
    settings = load_settings()

    # Create and show widget
    window = StickyNoteWindow(settings)
    window.show()

    # System tray
    tray = SystemTray(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
