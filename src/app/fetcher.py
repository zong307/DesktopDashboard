"""
DesktopDashboard - Network information fetcher.

Retrieves LAN IP, public IP, and hostname using standard library modules.
"""

from __future__ import annotations

import socket
import ssl
import threading
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class NetworkInfo:
    """Container for network-related information."""

    lan_ip: str = ""
    public_ip: str = ""
    hostname: str = ""
    error: str = ""


# ---------------------------------------------------------------------------
# LAN IP detection
# ---------------------------------------------------------------------------


def get_lan_ip() -> str:
    """Detect the primary LAN (IPv4) IP address.

    Uses a UDP socket trick: connecting to a public address without
    actually sending data reveals the local interface IP.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        pass

    # Fallback: try to get IP from hostname
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "N/A"


# ---------------------------------------------------------------------------
# Public IP detection
# ---------------------------------------------------------------------------


def get_public_ip(url: str = "https://api.ipify.org") -> str:
    """Fetch the public (WAN) IP address from a remote API.

    Falls back to http if https fails, then to "N/A".
    """
    for scheme in ("https://", "http://"):
        target = url.replace("https://", scheme).replace("http://", scheme)
        if not target.startswith(("http://", "https://")):
            target = scheme + target
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(target, headers={"User-Agent": "DesktopDashboard/0.1"})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                ip = resp.read().decode("utf-8").strip()
                if ip and ip != "0.0.0.0":
                    return ip
        except Exception:
            continue
    return "N/A"


# ---------------------------------------------------------------------------
# Hostname
# ---------------------------------------------------------------------------


def get_hostname() -> str:
    """Return the local machine hostname."""
    try:
        return socket.gethostname()
    except OSError:
        return "N/A"


# ---------------------------------------------------------------------------
# Async fetcher with callback
# ---------------------------------------------------------------------------


def fetch_all(
    *,
    on_done: Optional[Callable[[NetworkInfo], None]] = None,
    lan_ip_url: str = "",
    public_ip_url: str = "https://api.ipify.org",
) -> NetworkInfo:
    """Fetch all network info synchronously and return the result.

    Also accepts a callback for async-style handling.
    """
    info = NetworkInfo()

    # Hostname and LAN IP — very fast
    info.hostname = get_hostname()
    info.lan_ip = get_lan_ip()

    # Public IP — may be slow, run in background thread
    def _fetch_public():
        info.public_ip = get_public_ip(public_ip_url)
        if on_done:
            threading.Thread(target=on_done, args=(info,), daemon=True).start()

    threading.Thread(target=_fetch_public, daemon=True).start()

    return info


def fetch_all_async(
    *,
    on_done: Callable[[NetworkInfo], None],
    public_ip_url: str = "https://api.ipify.org",
) -> None:
    """Fetch network info asynchronously, calling *on_done* when ready."""
    info = fetch_all(on_done=on_done, public_ip_url=public_ip_url)
    # If public IP is already available (fast), call immediately
    # Otherwise wait for the background thread
    if info.public_ip and info.public_ip != "N/A":
        on_done(info)
