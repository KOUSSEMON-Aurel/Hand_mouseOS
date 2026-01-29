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
PYTHONPATH=. ./venv/bin/python main.py
