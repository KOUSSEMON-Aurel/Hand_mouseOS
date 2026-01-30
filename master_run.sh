#!/bin/bash
# Hand Mouse OS - Flet GUI Launcher

echo "🛡️ Checking system permissions..."

# Check if we maintain write access to uinput
if [ -w /dev/uinput ]; then
    echo "✅ uinput permissions OK"
else
    echo "⚠️ Setting up uinput permissions (requires sudo)..."
    sudo modprobe uinput 2>/dev/null
    sudo chmod 666 /dev/uinput 2>/dev/null
fi

echo "🚀 Starting Hand Mouse OS (Flet Edition)..."
cd "$(dirname "$0")"

# Force X11/XCB to avoid Wayland issues with OpenCV/Qt
export QT_QPA_PLATFORM=xcb

# Suppress common library warnings
export GLIB_LOG_LEVEL=4
export G_MESSAGES_DEBUG=none
export NO_AT_BRIDGE=1 # Disable At-Bridge to avoid some Atk errors

# Run main.py and filter out Xlib.xauth warnings
PYTHONPATH=. ./venv/bin/python main.py 2> >(grep -v "Xlib.xauth" >&2)


