"""
DesktopDashboard - Apple-style QSS stylesheet.

Provides a clean, minimal, macOS-inspired visual language using Qt
Style Sheets (QSS).
"""

from __future__ import annotations

LIGHT_THEME = r"""
/* ── Window ───────────────────────────────────────── */
QMainWindow {
    background: transparent;
}

QWidget#content {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 230),
        stop:1 rgba(245, 245, 247, 220)
    );
    border-radius: 16px;
}

/* ── Title label ──────────────────────────────────── */
QLabel#title {
    color: #86868b;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── IP / data labels ─────────────────────────────── */
QLabel#lan_ip,
QLabel#public_ip {
    color: #1d1d1f;
    font-size: 16px;
    font-weight: 600;
}

/* ── Secondary text (label prefix) ────────────────── */
QLabel#label_lan,
QLabel#label_public,
QLabel#label_host,
QLabel#label_time {
    color: #86868b;
    font-size: 11px;
    font-weight: 500;
}

/* ── Separator line ───────────────────────────────── */
QFrame#separator {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 0, 0, 0),
        stop:0.3 rgba(0, 0, 0, 0.06),
        stop:0.7 rgba(0, 0, 0, 0.06),
        stop:1 rgba(0, 0, 0, 0)
    );
    border: none;
    max-height: 1px;
    min-height: 1px;
}

/* ── Status indicator dot ─────────────────────────── */
QLabel#status_dot {
    background: #34C759;
    border-radius: 4px;
    min-width: 8px;
    max-width: 8px;
    min-height: 8px;
    max-height: 8px;
}

QLabel#status_dot.warning {
    background: #FF9500;
}

QLabel#status_dot.error {
    background: #FF3B30;
}

/* ── Tooltip ──────────────────────────────────────── */
QToolTip {
    color: #1d1d1f;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

DARK_THEME = r"""
QMainWindow {
    background: transparent;
}

QWidget#content {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(30, 30, 34, 235),
        stop:1 rgba(25, 25, 28, 225)
    );
    border-radius: 16px;
}

QLabel#title {
    color: #8e8e93;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

QLabel#lan_ip,
QLabel#public_ip {
    color: #f5f5f7;
    font-size: 16px;
    font-weight: 600;
}

QLabel#label_lan,
QLabel#label_public,
QLabel#label_host,
QLabel#label_time {
    color: #8e8e93;
    font-size: 11px;
    font-weight: 500;
}

QFrame#separator {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(255, 255, 255, 0),
        stop:0.3 rgba(255, 255, 255, 0.06),
        stop:0.7 rgba(255, 255, 255, 0.06),
        stop:1 rgba(255, 255, 255, 0)
    );
    border: none;
    max-height: 1px;
    min-height: 1px;
}

QLabel#status_dot {
    background: #30D158;
}

QLabel#status_dot.warning {
    background: #FF9F0A;
}

QLabel#status_dot.error {
    background: #FF453A;
}

QToolTip {
    color: #f5f5f7;
    background: rgba(40, 40, 44, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}
"""


def get_stylesheet(theme: str = "light") -> str:
    """Return the QSS stylesheet string for the given theme."""
    if theme == "dark":
        return DARK_THEME
    return LIGHT_THEME
