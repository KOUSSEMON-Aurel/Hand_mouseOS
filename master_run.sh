#!/bin/bash
# Hand Mouse OS - Flet GUI Launcher

echo "🛡️ Setting up uinput permissions..."
sudo modprobe uinput 2>/dev/null || echo "⚠️ uinput module already loaded"
sudo chmod 666 /dev/uinput 2>/dev/null || echo "⚠️ Could not set uinput permissions (already set or need sudo)"

echo "🚀 Starting Hand Mouse OS (Flet Edition)..."
cd "$(dirname "$0")"
PYTHONPATH=. ./venv/bin/python main.py
