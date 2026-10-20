#!/usr/bin/env python3
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

CONFIG = Path(__file__).resolve().parents[1]
PANELS = ("calendar-panel", "wifi-panel", "quicksettings")

def eww(*args):
  result = subprocess.run(["eww", "--config", str(CONFIG), *args],
    text=True, capture_output=True, timeout=4)
  if result.returncode:
    raise RuntimeError(result.stderr.strip() or "EWW did not respond.")
  return result.stdout.strip()

def update(**values):
  return eww("update", *(f"{key}={json.dumps(value, ensure_ascii=False)}"
    if not isinstance(value, str) else f"{key}={value}" for key, value in values.items()))

def active_windows():
  if eww("ping") != "pong":
    raise RuntimeError("EWW returned an empty response. Restart the EWW daemon.")
  return {line.split(":", 1)[0] for line in eww("active-windows").splitlines()}

def focused_screen():
  try:
    result = subprocess.run(["hyprctl", "monitors", "-j"],
      text=True, capture_output=True, timeout=2, check=True)
    # EWW 0.5 matches GDK model names, not Hyprland connector names.
    return str(next(index for index, monitor in enumerate(json.loads(result.stdout))
      if monitor["focused"]))
  except (OSError, ValueError, KeyError, StopIteration, subprocess.SubprocessError):
    return "0"

def close(name, active):
  if name == "wifi-panel":
    update(wifi_open=False)
  elif name == "calendar-panel":
    update(calendar_open=False)
  if name in active:
    eww("close", name)

def open_panel(name, screen):
  eww("open", name, "--screen", screen)
  if name == "wifi-panel":
    update(wifi_open=True)
  elif name == "calendar-panel":
    update(calendar_open=True)

def control(action, name):
  runtime = Path(os.environ["XDG_RUNTIME_DIR"])
  with (runtime / "hyprlandbattery-panels.lock").open("w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
      active = active_windows()
    except RuntimeError:
      subprocess.run(["eww", "--config", str(CONFIG), "daemon"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4, check=True)
      active = active_windows()
    if action == "close":
      close(name, active)
      return
    if name in active and action == "toggle":
      close(name, active)
      return
    for panel in PANELS:
      close(panel, active)
    if name == "wifi-panel" and eww("get", "wifi_busy") != "true":
      update(wifi_notice="")
    open_panel(name, focused_screen())

def main():
  if len(sys.argv) != 3 or sys.argv[1] not in ("toggle", "close", "today") \
      or sys.argv[2] not in PANELS:
    raise SystemExit("Usage: panels.py {toggle|close|today} PANEL")
  try:
    control(sys.argv[1], sys.argv[2])
  except (OSError, RuntimeError, subprocess.SubprocessError) as error:
    print(f"Panel operation failed: {error}", file=sys.stderr)
    subprocess.run(["notify-send", "Desktop panel unavailable",
      "The panel did not respond. Check the EWW log."], check=False)
    raise SystemExit(1)

if __name__ == "__main__":
  main()
