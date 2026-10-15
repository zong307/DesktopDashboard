"""
DesktopDashboard - Configuration management.

Loads settings from YAML config file with sensible defaults.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# ---------------------------------------------------------------------------
# Default configuration values
# ---------------------------------------------------------------------------

DEFAULTS = {
    "display": {
        "width": 280,
        "height": 180,
        "corner_radius": 16,
        "padding": 20,
        "opacity": 0.85,
        "frosted_glass": True,
        "font_family": "",
        "font_size": 13,
        "font_weight": 500,
    },
    "refresh": {
        "interval_seconds": 60,
        "public_ip_url": "https://api.ipify.org",
    },
    "appearance": {
        "theme": "light",
        "accent_color": "#007AFF",
        "text_color_primary": "#1d1d1f",
        "text_color_secondary": "#86868b",
        "bg_color": "rgba(255, 255, 255, 0.85)",
        "show_lan_ip": True,
        "show_public_ip": True,
        "show_hostname": False,
        "show_timestamp": True,
    },
    "window": {
        "always_on_top": True,
        "draggable": True,
        "show_on_startup": True,
    },
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DisplaySettings:
    width: int = 280
    height: int = 180
    corner_radius: int = 16
    padding: int = 20
    opacity: float = 0.85
    frosted_glass: bool = True
    font_family: str = ""
    font_size: int = 13
    font_weight: int = 500


@dataclass
class RefreshSettings:
    interval_seconds: int = 60
    public_ip_url: str = "https://api.ipify.org"


@dataclass
class AppearanceSettings:
    theme: str = "light"
    accent_color: str = "#007AFF"
    text_color_primary: str = "#1d1d1f"
    text_color_secondary: str = "#86868b"
    bg_color: str = "rgba(255, 255, 255, 0.85)"
    show_lan_ip: bool = True
    show_public_ip: bool = True
    show_hostname: bool = False
    show_timestamp: bool = True


@dataclass
class WindowSettings:
    always_on_top: bool = True
    draggable: bool = True
    show_on_startup: bool = True


@dataclass
class Settings:
    display: DisplaySettings = field(default_factory=DisplaySettings)
    refresh: RefreshSettings = field(default_factory=RefreshSettings)
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)
    window: WindowSettings = field(default_factory=WindowSettings)


# ---------------------------------------------------------------------------
# YAML parser helpers
# ---------------------------------------------------------------------------


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*."""
    result = base.copy()
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _parse_yaml(path: Path) -> dict:
    """Parse a YAML file, returning an empty dict when yaml is unavailable."""
    if yaml is None:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            return data or {}
    except (OSError, yaml.YAMLError):  # type: ignore[name-defined]
        return {}


# ---------------------------------------------------------------------------
# Settings loader
# ---------------------------------------------------------------------------


def _find_config_path() -> Path:
    """Locate the settings.yaml configuration file.

    Search order:
    1. CODEX_CONFIG_PATH environment variable
    2. config/settings.yaml relative to this package
    3. config/settings.yaml relative to the executable / cwd
    """
    env_path = os.environ.get("CODEX_CONFIG_PATH")
    if env_path:
        candidate = Path(env_path)
        if candidate.is_file():
            return candidate

    # Relative to this module's file
    candidate = Path(__file__).resolve().parent.parent.parent / "config" / "settings.yaml"
    if candidate.is_file():
        return candidate

    # Relative to cwd
    candidate = Path.cwd() / "config" / "settings.yaml"
    if candidate.is_file():
        return candidate

    # Relative to executable (PyInstaller)
    if getattr(sys, "frozen", False):
        candidate = Path(sys.executable).parent / "config" / "settings.yaml"
        if candidate.is_file():
            return candidate

    return Path.cwd() / "config" / "settings.yaml"


def load_settings(path: Optional[Path] = None) -> Settings:
    """Load and return a :class:`Settings` instance from the YAML config."""
    config_path = path or _find_config_path()
    raw = _parse_yaml(config_path)
    merged = _deep_merge(DEFAULTS, raw)

    display_raw = merged.get("display", {})
    refresh_raw = merged.get("refresh", {})
    appearance_raw = merged.get("appearance", {})
    window_raw = merged.get("window", {})

    return Settings(
        display=DisplaySettings(**display_raw),
        refresh=RefreshSettings(**refresh_raw),
        appearance=AppearanceSettings(**appearance_raw),
        window=WindowSettings(**window_raw),
    )
