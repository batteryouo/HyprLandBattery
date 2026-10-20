#!/usr/bin/env python3
import base64
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
from panels import control, eww, update

def nmcli(*args, timeout=6):
  result = subprocess.run(["nmcli", "--colors", "no", *args],
    env={**os.environ, "LC_ALL": "C"}, text=True, capture_output=True, timeout=timeout)
  if result.returncode:
    raise RuntimeError(result.stderr.strip() or "NetworkManager is unavailable.")
  return result.stdout.rstrip("\n")

def fields(line):
  values, field, escaped = [], "", False
  for char in line:
    if escaped:
      field += char
      escaped = False
    elif char == "\\":
      escaped = True
    elif char == ":":
      values.append(field)
      field = ""
    else:
      field += char
  values.append(field + ("\\" if escaped else ""))
  return values

def saved_networks():
  saved = {}
  for line in nmcli("-t", "-f", "UUID,TYPE", "connection", "show").splitlines():
    row = fields(line)
    if len(row) != 2:
      continue
    uuid, kind = row
    if kind == "802-11-wireless":
      try:
        ssid = nmcli("-g", "802-11-wireless.ssid", "connection", "show", "uuid", uuid)
      except RuntimeError:
        continue
      saved.setdefault(fields(ssid)[0], uuid)
  return saved

def token(device, bssid, uuid, ssid="", security=""):
  return base64.urlsafe_b64encode(
    json.dumps([device, bssid, uuid, ssid, security]).encode()).decode()

def network_rows(output, device, saved):
  networks = {}
  for line in output.splitlines():
    row = fields(line)
    if len(row) != 5:
      continue
    in_use, ssid, bssid, signal, security = row
    if not ssid or not signal.isdigit():
      continue
    active = in_use == "*"
    uuid = saved.get(ssid, "")
    strength = int(signal)
    kind = "Connected" if active else "Saved" if uuid else "Open" if not security or security == "--" else "Secured"
    network = {
      "ssid": ssid, "signal": strength, "active": active, "saved": bool(uuid),
      "icon": "󰤨" if strength >= 70 else "󰤥" if strength >= 40 else "󰤟",
      "detail": f"{kind}  ·  {strength}%",
      "action": "Connected" if active else "Connect" if uuid else "Set up",
      "token": token(device, bssid, uuid, ssid, security),
    }
    # Keep the connected AP, otherwise the strongest AP for each SSID.
    previous = networks.get(ssid)
    if previous is None or (active, strength) > (previous["active"], previous["signal"]):
      networks[ssid] = network
  return sorted(networks.values(), key=lambda n: (
    not n["active"], not n["saved"], -n["signal"], n["ssid"].casefold()))[:6]

def status():
  state = {"available": False, "enabled": False, "connected": False,
    "title": "Wi-Fi unavailable", "detail": "No wireless adapter found.",
    "networks": [], "empty": "No wireless adapter found."}
  try:
    devices = [fields(line) for line in nmcli("-t", "-f", "DEVICE,TYPE,STATE",
      "device", "status").splitlines()]
    devices = [row for row in devices if len(row) == 3 and row[1] == "wifi"]
    if not devices:
      return state
    device = next((row for row in devices if row[2] == "connected"), devices[0])[0]
    state["available"] = True
    state["enabled"] = nmcli("radio", "wifi") == "enabled"
    if not state["enabled"]:
      state.update(title="Wi-Fi is off", detail="Turn on Wi-Fi to see nearby networks.",
        empty="Wireless networking is turned off.")
      return state
    rows = network_rows(nmcli("-t", "-f", "IN-USE,SSID,BSSID,SIGNAL,SECURITY",
      "device", "wifi", "list", "--rescan", "no", "ifname", device), device, saved_networks())
    connected = next((row for row in rows if row["active"]), None)
    state.update(networks=rows, connected=connected is not None,
      title=connected["ssid"] if connected else "Not connected",
      detail=f"Connected  ·  Signal {connected['signal']}%" if connected else "Choose a saved network to connect.",
      empty="No networks found. Try scanning again.")
  except (OSError, RuntimeError, subprocess.SubprocessError):
    state.update(available=False, title="NetworkManager unavailable",
      detail="Check that the NetworkManager service is running.",
      empty="Unable to read wireless networks.")
  return state

def settings():
  control("close", "wifi-panel")
  subprocess.Popen(["nm-connection-editor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    start_new_session=True)

def action(name, argument=""):
  runtime = Path(os.environ["XDG_RUNTIME_DIR"])
  with (runtime / "hyprlandbattery-wifi.lock").open("w") as lock:
    try:
      fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
      return
    update(wifi_busy=True, wifi_notice="")
    try:
      if name == "scan":
        update(wifi_notice="Scanning for nearby networks…")
        nmcli("--wait", "10", "device", "wifi", "list", "--rescan", "yes", timeout=12)
        update(wifi_notice="Scan complete.")
      elif name == "toggle":
        enabled = nmcli("radio", "wifi") == "enabled"
        nmcli("radio", "wifi", "off" if enabled else "on")
      elif name == "connect":
        device, bssid, uuid, ssid, security = json.loads(base64.urlsafe_b64decode(argument))
        if not uuid:
          if not security or security == "--":
            update(wifi_notice="Connecting…")
            nmcli("--wait", "25", "device", "wifi", "connect", ssid,
              "ifname", device, "bssid", bssid, timeout=28)
            update(wifi_notice="Connected.")
            return
          control("close", "wifi-panel")
          prompt = Path(__file__).with_name("wifi_prompt.py")
          subprocess.Popen([sys.executable, str(prompt), argument], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
          return
        update(wifi_notice="Connecting…")
        nmcli("--wait", "25", "connection", "up", "uuid", uuid,
          "ifname", device, "ap", bssid, timeout=28)
        update(wifi_notice="Connected.")
      elif name == "settings":
        settings()
      else:
        raise ValueError("Unknown Wi-Fi action.")
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError):
      update(wifi_notice="The operation failed. Try again or open Network settings.")
    finally:
      update(wifi_busy=False)
      eww("poll", "wifi_state")

def main():
  if len(sys.argv) == 2 and sys.argv[1] == "status":
    print(json.dumps(status(), ensure_ascii=False))
  elif len(sys.argv) >= 2 and sys.argv[1] in ("scan", "toggle", "connect", "settings"):
    action(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
  else:
    raise SystemExit("Usage: wifi.py {status|scan|toggle|connect TOKEN|settings}")

if __name__ == "__main__":
  main()
