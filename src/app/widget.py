"""
DesktopDashboard - Desktop Sticky Note Widget.

A frosted-glass, always-on-top window that displays network information
in an Apple-inspired design.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QEvent, Qt, QThread, Signal, Slot, QTimer, QRect
from PySide6.QtGui import (
    QAction,
    QColor,
    QCursor,
    QFont,
    QFontDatabase,
    QGuiApplication,
    QIcon,
    QPainter,
    QPaintEvent,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .config import Settings, load_settings
from .fetcher import NetworkInfo
from .style import get_stylesheet

# ── Icon paths ─────────────────────────────────────────────────────

_ICONS_DIR = Path(__file__).resolve().parent / "icons"
_ICON_PATH = _ICONS_DIR / "icon.svg"
_COPY_ICON_PATH = _ICONS_DIR / "copy.svg"
_PINNED_ICON_PATH = _ICONS_DIR / "pinned.svg"


# ── Apple-style QSS for menus ──────────────────────────────────────

APPLE_MENU_STYLE = """
QMenu {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 4px 0;
    font-size: 13px;
    font-weight: 400;
}

QMenu::item {
    padding: 6px 20px 6px 36px;
    border-radius: 4px;
    margin: 2px 6px;
    min-width: 120px;
}

QMenu::item:selected {
    background-color: rgba(0, 122, 255, 0.15);
    color: #007AFF;
}

QMenu::item:disabled {
    color: rgba(0, 0, 0, 0.3);
}

QMenu::separator {
    height: 1px;
    background: rgba(0, 0, 0, 0.08);
    margin: 4px 12px;
}

QMenu::right-arrow {
    image: none;
}

QMenu::left-arrow {
    image: none;
}
"""

APPLE_SUBMENU_STYLE = """
QMenu {
    background-color: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px;
    padding: 4px 0;
}

QMenu::item {
    padding: 6px 20px 6px 36px;
    border-radius: 4px;
    margin: 2px 6px;
}

QMenu::item:selected {
    background-color: rgba(0, 122, 255, 0.15);
    color: #007AFF;
}
"""


# ---------------------------------------------------------------------------
# Content Block
# ---------------------------------------------------------------------------


class TextBlock:
    """A block that displays a labeled text value with optional copy button."""

    def __init__(
        self,
        parent: QWidget,
        *,
        title: str,
        data_key: str,
        show: bool = True,
        is_value: bool = True,
    ):
        self.title = title
        self.data_key = data_key
        self.show = show

        # Horizontal row: [Label] [Value] [Copy Button]
        self.widget = QWidget(parent)
        row_layout = QHBoxLayout(self.widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        # Label
        self.label_w = QLabel(title, self.widget)
        self.label_w.setObjectName("label_" + data_key)
        row_layout.addWidget(self.label_w)

        row_layout.addStretch()

        # Value
        self.value_w = QLabel("N/A", self.widget)
        if is_value:
            self.value_w.setObjectName(
                "lan_ip" if data_key == "lan_ip" else "public_ip"
            )
        else:
            self.value_w.setObjectName(data_key)
        self.value_w.setMinimumWidth(80)
        row_layout.addWidget(self.value_w)

        # Copy button
        self.copy_btn = QPushButton(self.widget)
        self.copy_btn.setFixedSize(20, 20)
        self.copy_btn.setFlat(True)
        self.copy_btn.setObjectName("copy_btn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setVisible(False)

        # Load copy icon from SVG
        if _COPY_ICON_PATH.is_file():
            self.copy_btn.setIcon(QIcon(str(_COPY_ICON_PATH)))
            self.copy_btn.setIconSize(self.copy_btn.size())

        row_layout.addWidget(self.copy_btn)

    def update(self, data: NetworkInfo) -> None:
        value = getattr(data, self.data_key, "")
        self.value_w.setText(value or "N/A")

    def set_copy_visible(self, visible: bool) -> None:
        self.copy_btn.setVisible(visible)
        if visible:
            self.value_w.setMinimumWidth(0)
        else:
            self.value_w.setMinimumWidth(80)

    def get_value(self) -> str:
        return self.value_w.text()

    def hide(self) -> None:
        self.widget.hide()

    def show_widget(self) -> None:
        self.widget.show()


# ---------------------------------------------------------------------------
# Network fetch thread
# ---------------------------------------------------------------------------


class FetchThread(QThread):
    """Background thread that fetches network info."""

    finished = Signal(NetworkInfo)

    def __init__(self, public_ip_url: str):
        super().__init__()
        self.public_ip_url = public_ip_url

    def run(self):
        import socket
        import ssl
        import urllib.request

        info = NetworkInfo()

        try:
            info.hostname = socket.gethostname()
        except OSError:
            info.hostname = "N/A"

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect(("10.255.255.255", 1))
            info.lan_ip = s.getsockname()[0]
            s.close()
        except OSError:
            try:
                info.lan_ip = socket.gethostbyname(socket.gethostname())
            except OSError:
                info.lan_ip = "N/A"

        for scheme in ("https://", "http://"):
            target = "https://api.ipify.org".replace("https://", scheme)
            try:
                ctx = ssl.create_default_context()
                req = urllib.request.Request(
                    target, headers={"User-Agent": "DesktopDashboard/0.1"}
                )
                with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                    ip = resp.read().decode("utf-8").strip()
                    if ip and ip != "0.0.0.0":
                        info.public_ip = ip
                        break
            except Exception:
                continue

        if not info.public_ip:
            info.public_ip = "N/A"

        self.finished.emit(info)


# ---------------------------------------------------------------------------
# Toast notification label
# ---------------------------------------------------------------------------


class ToastLabel(QLabel):
    """A brief toast notification that auto-hides after 2 seconds."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setObjectName("toast")
        self.setStyleSheet("""
            QLabel#toast {
                background: rgba(0, 0, 0, 0.75);
                color: #ffffff;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        self.setText("已复制")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adjustSize()

    def show_message(self, message: str) -> None:
        self.setText(message)
        self.adjustSize()
        self.show()

        # Auto-hide after 2 seconds
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.hide)
        timer.start(2000)


# ---------------------------------------------------------------------------
# Main Widget Window
# ---------------------------------------------------------------------------


class StickyNoteWindow(QMainWindow):
    """Apple-styled sticky note widget for the desktop."""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self._network_info = NetworkInfo()
        self._blocks: list[TextBlock] = []
        self._drag_position: Optional[QCursor] = None
        self._is_dragging = False
        self._fetch_thread: Optional[FetchThread] = None
        self._refresh_timer_id: Optional[int] = None
        self._clock_timer_id: Optional[int] = None

        # Settings state
        self._window_mode: str = "topmost"
        self._locked: bool = False

        self._init_window()
        self._init_ui()
        self._init_blocks()
        self._start_clock()
        self._refresh_data()
        self._init_context_menu()

    # ── Window initialization ──────────────────────────────────────

    def _init_window(self) -> None:
        cfg = self.settings
        self.setWindowTitle("DesktopDashboard")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.CustomizeWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        w, h = cfg.display.width, cfg.display.height
        self.resize(w, h)
        self.setFixedSize(w, h)
        self.setWindowOpacity(cfg.display.opacity)
        self.setStyleSheet(get_stylesheet(cfg.appearance.theme))

        primary = QGuiApplication.primaryScreen()
        if primary:
            geo = primary.geometry()
            self.move(
                geo.center().x() - self.width() // 2,
                geo.center().y() - self.height() // 2,
            )

    # ── UI construction ────────────────────────────────────────────

    def _init_ui(self) -> None:
        content = QWidget(self)
        content.setObjectName("content")
        content.setStyleSheet(
            f"""
            QWidget#content {{
                background: {self.settings.appearance.bg_color};
                border-radius: {self.settings.display.corner_radius}px;
            }}
            """
        )
        self.setCentralWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            self.settings.display.padding,
            12,
            self.settings.display.padding,
            12,
        )
        layout.setSpacing(6)

        # Title
        self._title_label = QLabel("NETWORK", content)
        self._title_label.setObjectName("title")
        layout.addWidget(self._title_label)

        # Status dot + timestamp row
        status_row = QWidget(content)
        status_row_layout = QHBoxLayout(status_row)
        status_row_layout.setContentsMargins(0, 0, 0, 0)
        status_row_layout.setSpacing(6)

        self._status_dot = QLabel(status_row)
        self._status_dot.setObjectName("status_dot")
        status_row_layout.addWidget(self._status_dot)

        self._time_label = QLabel(content)
        self._time_label.setObjectName("label_time")
        status_row_layout.addStretch()
        status_row_layout.addWidget(self._time_label)

        layout.addWidget(status_row)

        # Separator
        sep = QFrame(content)
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Content blocks
        self._blocks_container = QWidget(content)
        self._blocks_layout = QVBoxLayout(self._blocks_container)
        self._blocks_layout.setContentsMargins(0, 4, 0, 4)
        self._blocks_layout.setSpacing(8)
        layout.addWidget(self._blocks_container)

        layout.addStretch()

        # Toast notification (overlay)
        self._toast = ToastLabel(content)
        self._toast.hide()

        # Enable mouse tracking for hover detection
        content.setMouseTracking(True)
        content.installEventFilter(self)

    # ── Event filter for hover ─────────────────────────────────────

    def eventFilter(self, obj: QWidget, event) -> bool:
        """Handle mouse enter/leave for copy button visibility."""
        if obj is self.centralWidget():
            if event.type() == QEvent.Type.Enter:
                if self._locked:
                    self._update_copy_buttons_visible(True)
            elif event.type() == QEvent.Type.Leave:
                if self._locked:
                    self._update_copy_buttons_visible(False)
        return super().eventFilter(obj, event)

    def _update_copy_buttons_visible(self, visible: bool) -> None:
        """Update copy button visibility based on lock state and hover."""
        for block in self._blocks:
            block.set_copy_visible(visible and self._locked)

    # ── Content blocks ─────────────────────────────────────────────

    def _init_blocks(self) -> None:
        acfg = self.settings.appearance

        if acfg.show_lan_ip:
            self._blocks.append(TextBlock(
                self._blocks_container,
                title="局域网 IP", data_key="lan_ip",
            ))
        if acfg.show_public_ip:
            self._blocks.append(TextBlock(
                self._blocks_container,
                title="公网 IP", data_key="public_ip",
            ))
        if acfg.show_hostname:
            self._blocks.append(TextBlock(
                self._blocks_container,
                title="主机名", data_key="hostname", is_value=False,
            ))

        for block in self._blocks:
            if block.show:
                self._blocks_layout.addWidget(block.widget)

        # Connect copy buttons
        for block in self._blocks:
            if block.copy_btn:
                block.copy_btn.clicked.connect(
                    lambda checked, b=block: self._copy_ip(b)
                )

    # ── Clock ──────────────────────────────────────────────────────

    def _start_clock(self) -> None:
        """Start the real-time clock timer."""
        self._time_label.setText(time.strftime("%H:%M:%S"))
        self._clock_timer_id = self.startTimer(1000)

    # ── Network fetcher ────────────────────────────────────────────

    def _refresh_data(self) -> None:
        if self._fetch_thread and self._fetch_thread.isRunning():
            return

        self._fetch_thread = FetchThread(
            self.settings.refresh.public_ip_url
        )
        self._fetch_thread.finished.connect(self._on_fetch_complete)
        self._fetch_thread.start()

    @Slot(NetworkInfo)
    def _on_fetch_complete(self, info: NetworkInfo) -> None:
        self._network_info = info

        for block in self._blocks:
            block.update(info)

        # Status dot color
        if info.error:
            self._status_dot.setObjectName("status_dot error")
        elif info.lan_ip == "N/A" or info.public_ip == "N/A":
            self._status_dot.setObjectName("status_dot warning")
        else:
            self._status_dot.setObjectName("status_dot")

        self._time_label.setText(time.strftime("%H:%M:%S"))
        self._setup_auto_refresh()

    def _setup_auto_refresh(self) -> None:
        if self._refresh_timer_id is not None:
            self.killTimer(self._refresh_timer_id)
        interval = self.settings.refresh.interval_seconds * 1000
        self._refresh_timer_id = self.startTimer(interval)

    # ── Timer events ───────────────────────────────────────────────

    def timerEvent(self, event) -> None:
        if event.timerId() == self._refresh_timer_id:
            self._refresh_data()
        elif event.timerId() == self._clock_timer_id:
            self._time_label.setText(time.strftime("%H:%M:%S"))
        super().timerEvent(event)

    # ── Display mode ───────────────────────────────────────────────

    def set_window_mode(self, mode: str) -> None:
        if mode == self._window_mode:
            return

        self._window_mode = mode
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.CustomizeWindowHint
        )
        if mode == "topmost":
            flags |= Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.show()

    def get_window_mode(self) -> str:
        return self._window_mode

    # ── Lock / Unlock ──────────────────────────────────────────────

    def set_locked(self, locked: bool) -> None:
        was_locked = self._locked
        self._locked = locked

        if locked != was_locked:
            # Update copy button visibility based on current hover state
            if locked:
                # If currently hovering, show buttons
                pass  # Will be handled by event filter
            else:
                self._update_copy_buttons_visible(False)

        self.update_context_menu()

    def is_locked(self) -> bool:
        return self._locked

    # ── Copy IP to clipboard ──────────────────────────────────────

    def _copy_ip(self, block: TextBlock) -> None:
        value = block.get_value()
        if not value or value == "N/A":
            return

        app = QApplication.instance()
        if app:
            cb = app.clipboard()
            if cb:
                cb.setText(value)

        # Show toast notification
        self._toast.show_message("已复制")

    # ── Drag support ───────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._locked:
            self._drag_position = event.globalPosition().toPoint()
            self._is_dragging = True

    def mouseMoveEvent(self, event) -> None:
        if (
            self._is_dragging
            and not self._locked
            and self._drag_position is not None
        ):
            delta = event.globalPosition().toPoint() - self._drag_position
            self.move(
                self.x() + delta.x(),
                self.y() + delta.y(),
            )
            self._drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._drag_position = None

    # ── Context menu ───────────────────────────────────────────────

    def _init_context_menu(self) -> None:
        self._context_menu = QMenu(self)
        self._context_menu.setStyleSheet(APPLE_MENU_STYLE)
        self.update_context_menu()

    def update_context_menu(self) -> None:
        self._context_menu.clear()

        # 刷新IP
        refresh_action = QAction("  刷新IP", self)
        refresh_action.triggered.connect(self._refresh_data)
        self._context_menu.addAction(refresh_action)

        self._context_menu.addSeparator()

        # 显示方式
        mode_menu = QMenu("  显示方式", self._context_menu)
        mode_menu.setStyleSheet(APPLE_SUBMENU_STYLE)

        self._mode_topmost = QAction("  置顶", self._context_menu)
        self._mode_topmost.setCheckable(True)
        self._mode_normal = QAction("  不置顶", self._context_menu)
        self._mode_normal.setCheckable(True)

        if self._window_mode == "topmost":
            self._mode_topmost.setChecked(True)
        else:
            self._mode_normal.setChecked(True)

        self._mode_topmost.triggered.connect(lambda: self._set_mode("topmost"))
        self._mode_normal.triggered.connect(lambda: self._set_mode("normal"))

        mode_menu.addAction(self._mode_topmost)
        mode_menu.addAction(self._mode_normal)
        self._context_menu.addMenu(mode_menu)

        # 固定
        lock_action = QAction(
            "  固定" if self._locked else "  固定", self._context_menu
        )
        lock_action.setCheckable(True)
        lock_action.setChecked(self._locked)
        lock_action.triggered.connect(self._toggle_lock)
        self._context_menu.addAction(lock_action)

        self._context_menu.addSeparator()

        # 退出
        quit_action = QAction("  退出", self._context_menu)
        quit_action.triggered.connect(QApplication.quit)
        self._context_menu.addAction(quit_action)

    def _set_mode(self, mode: str) -> None:
        self.set_window_mode(mode)
        self.update_context_menu()

    def _toggle_lock(self) -> None:
        self.set_locked(not self._locked)

    def contextMenuEvent(self, event) -> None:
        self._context_menu.exec(event.globalPos())

    # ── Custom paint ───────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        glow_color = QColor(0, 0, 0, 20)
        painter.setBrush(glow_color)
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 18, 18)

        painter.end()

    # ── Close / Quit ───────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()

    def keyPressEvent(self, event) -> None:
        if (
            event.modifiers() == Qt.KeyboardModifier.ControlModifier
            and event.key() == Qt.Key.Key_C
        ):
            QApplication.quit()
        else:
            super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# System Tray
# ---------------------------------------------------------------------------


class SystemTray:
    """Manages a system tray icon for show/hide/quit."""

    def __init__(self, window: StickyNoteWindow):
        self.window = window
        self._tray = QSystemTrayIcon()
        self._build_icon()
        self._build_menu()
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _build_icon(self) -> None:
        if _ICON_PATH.is_file():
            self._tray.setIcon(QIcon(str(_ICON_PATH)))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#007AFF"))
            self._tray.setIcon(QIcon(pixmap))

    def _build_menu(self) -> None:
        menu = QMenu()
        menu.setStyleSheet(APPLE_MENU_STYLE)

        show_action = QAction("  显示", menu)
        show_action.triggered.connect(self.window.showNormal)
        show_action.triggered.connect(self.window.activateWindow)
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("  退出", menu)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.setToolTip("DesktopDashboard")

    @Slot(int)
    def _on_tray_activated(self, reason: int) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.window.isVisible():
                self.window.hide()
            else:
                self.window.showNormal()
                self.window.activateWindow()
