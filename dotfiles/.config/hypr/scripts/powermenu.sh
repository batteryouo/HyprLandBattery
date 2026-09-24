#!/usr/bin/env bash
# Power menu shared by the Super+M keybinding and the Waybar power button.
set -euo pipefail

choice=$(printf 'Lock\nLogout\nSuspend\nReboot\nShutdown' | wofi --dmenu --prompt 'Power')

case "$choice" in
  Lock) hyprlock ;;
  Logout) hyprctl dispatch exit ;;
  Suspend) systemctl suspend ;;
  Reboot) systemctl reboot ;;
  Shutdown) systemctl poweroff ;;
esac
