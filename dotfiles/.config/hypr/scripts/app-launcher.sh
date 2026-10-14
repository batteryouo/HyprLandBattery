#!/usr/bin/env bash
set -euo pipefail

runtime_dir="${XDG_RUNTIME_DIR:?}"
pid_file="$runtime_dir/hyprlandbattery-app-launcher.pid"
lock_file="$runtime_dir/hyprlandbattery-app-launcher.lock"
closed_at_file="$runtime_dir/hyprlandbattery-app-launcher-closed-at"

set_click_bind() {
    hyprctl eval "_G.appLauncherClickBind:set_enabled($1)" > /dev/null
}

launcher_running() {
    [[ -r "$pid_file" ]] || return 1
    read -r rofi_pid opened_at < "$pid_file" || return 1
    [[ "${rofi_pid:-}" =~ ^[0-9]+$ && -r "/proc/$rofi_pid/cmdline" ]] || return 1
    command_line=$(tr '\0' ' ' < "/proc/$rofi_pid/cmdline")
    [[ "$command_line" == *"rofi -show drun"* ]]
}

close_launcher() {
    if launcher_running; then
        date +%s%3N > "$closed_at_file"
        kill "$rofi_pid" 2>/dev/null || true
    fi
}

if [[ "${1:-}" == close ]]; then
    close_launcher
    exit 0
fi

if [[ "${1:-}" == click ]]; then
    if ! launcher_running; then
        set_click_bind false || true
        exit 0
    fi
    [[ "${opened_at:-}" =~ ^[0-9]+$ ]] || exit 0
    (( $(date +%s%3N) - opened_at >= 300 )) || exit 0
    cursor=$(hyprctl cursorpos -j) || exit 0
    layers=$(hyprctl layers -j) || exit 0
    if python3 -c '
import json, sys
cursor = json.loads(sys.argv[2])
surfaces = [layer for monitor in json.load(sys.stdin).values()
  for level in monitor.get("levels", {}).values() for layer in level
  if layer.get("namespace") == "rofi" and layer.get("pid") == int(sys.argv[1])]
if not surfaces:
  sys.exit(1)
inside = any(layer["x"] <= cursor["x"] < layer["x"] + layer["w"]
  and layer["y"] <= cursor["y"] < layer["y"] + layer["h"] for layer in surfaces)
sys.exit(1 if inside else 0)
' "$rofi_pid" "$cursor" <<< "$layers"; then
        close_launcher
    fi
    exit 0
fi

exec 9> "$lock_file"
if ! flock -n 9; then
    close_launcher
    exit 0
fi

if [[ -r "$closed_at_file" ]]; then
    read -r closed_at < "$closed_at_file" || true
    if [[ "${closed_at:-}" =~ ^[0-9]+$ ]] && (( $(date +%s%3N) - closed_at < 400 )); then
        exit 0
    fi
fi

trap 'set_click_bind false || true; rm -f "$pid_file"' EXIT
rofi -show drun -theme "$HOME/.config/rofi/themes/app-launcher.rasi" &
rofi_pid=$!
printf '%s %s\n' "$rofi_pid" "$(date +%s%3N)" > "$pid_file"
set_click_bind true || true
wait "$rofi_pid" || true
