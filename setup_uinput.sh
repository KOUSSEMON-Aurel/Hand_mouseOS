#!/bin/bash
echo "🔧 Configuring UInput permissions for Wayland..."

# 1. Load module if not loaded
if ! lsmod | grep -q uinput; then
    echo "bi loading uinput module..."
    sudo modprobe uinput
    echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf
fi

# 2. Create udev rule for current user
USER_NAME=$(whoami)
echo "👤 Granting access to user: $USER_NAME"

echo "KERNEL==\"uinput\", MODE=\"0660\", GROUP=\"uinput\", OPTIONS+=\"static_node=uinput\"" | sudo tee /etc/udev/rules.d/99-uinput.rules
echo "KERNEL==\"uinput\", SUBSYSTEM==\"misc\", OPTIONS+=\"static_node=uinput\", TAG+=\"uaccess\"" | sudo tee -a /etc/udev/rules.d/99-uinput.rules

# 3. Create group if needed and add user
if ! getent group uinput > /dev/null; then
    sudo groupadd uinput
fi
sudo usermod -aG uinput $USER_NAME
sudo usermod -aG input $USER_NAME

# 4. Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "✅ Configuration done!"
echo "⚠️  You may need to LOGOUT/LOGIN for group changes to take effect."
echo "👉 Try running the app now. If it fails, restart your session."
