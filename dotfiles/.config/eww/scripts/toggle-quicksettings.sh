#!/usr/bin/env bash
# Opens/closes the eww quick-settings panel. Bound to the waybar button and
# Super+N, mirroring powermenu.sh's role as a shared wrapper script.
set -euo pipefail

if eww active-windows | grep -q quicksettings; then
  eww close quicksettings
else
  eww open quicksettings
fi
