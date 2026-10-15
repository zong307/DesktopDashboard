#!/bin/bash
# DesktopDashboard - Create desktop entry (Linux)
# Run: chmod +x scripts/desktop_entry.sh && ./scripts/desktop_entry.sh

set -e

APP_NAME="DesktopDashboard"
EXEC_PATH="${HOME}/.local/share/DesktopDashboard/DesktopDashboard"
ICON_PATH="/usr/share/icons/hicolor/48x48/apps/DesktopDashboard.png"

DESKTOP_FILE="${HOME}/.local/share/applications/${APP_NAME}.desktop"

mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=DesktopDashboard
Comment=Desktop sticky note widget
Exec=${EXEC_PATH}
Icon=${ICON_PATH}
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=false
EOF

echo "Desktop entry created at: $DESKTOP_FILE"
echo "Add to startup: copy to ~/.config/autostart/"
