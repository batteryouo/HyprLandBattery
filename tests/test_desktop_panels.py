import base64
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "dotfiles/.config/eww/scripts"
sys.path.insert(0, str(SCRIPTS))
import panels
import wifi
import wifi_prompt

class WifiTests(unittest.TestCase):
  def test_nmcli_escaped_fields(self):
    self.assertEqual(wifi.fields(r"*:Office\: East\\West:80:WPA2"),
      ["*", "Office: East\\West", "80", "WPA2"])

  def test_active_ap_wins_and_saved_networks_sort_first(self):
    rows = wifi.network_rows(
      "*:Home:AA\\:01:30:WPA2\n:Home:AA\\:02:95:WPA2\n"
      ":Guest:BB\\:01:90:--\n:Work:CC\\:01:50:WPA2\n",
      "wlan0", {"Home": "home-uuid", "Work": "work-uuid"})
    self.assertEqual([row["ssid"] for row in rows], ["Home", "Work", "Guest"])
    self.assertEqual(rows[0]["signal"], 30)
    self.assertTrue(rows[0]["active"])
    self.assertEqual(rows[2]["action"], "Set up")

  def test_network_names_never_become_shell_commands(self):
    ssid = "O'Brien $(touch /tmp/not-executed)"
    rows = wifi.network_rows(f":{ssid}:AA\\:BB:70:WPA2", "wlan0", {})
    self.assertEqual(rows[0]["ssid"], ssid)
    token = rows[0]["token"]
    self.assertRegex(token, r"^[A-Za-z0-9_=-]+$")
    self.assertEqual(json.loads(base64.urlsafe_b64decode(token)),
      ["wlan0", "AA:BB", "", ssid, "WPA2"])

  def test_saved_profile_uses_ssid_instead_of_profile_name(self):
    with patch.object(wifi, "nmcli", side_effect=[
        "wifi-uuid:802-11-wireless\nvpn-uuid:vpn", r"Office\: East"]) as command:
      self.assertEqual(wifi.saved_networks(), {"Office: East": "wifi-uuid"})
      self.assertEqual(command.call_count, 2)

  def test_radio_off_does_not_query_or_scan_access_points(self):
    with patch.object(wifi, "nmcli", side_effect=[
        "wlan0:wifi:disconnected", "disabled"]) as command:
      result = wifi.status()
      self.assertFalse(result["enabled"])
      self.assertEqual(result["networks"], [])
      self.assertEqual(command.call_count, 2)

  def test_status_never_forces_a_scan(self):
    with patch.object(wifi, "nmcli", side_effect=[
        "wlan0:wifi:connected", "enabled", "*:Home:AA\\:BB:75:WPA2", ""]) as command:
      result = wifi.status()
      self.assertTrue(result["connected"])
      self.assertIn("--rescan", command.call_args_list[2].args)
      self.assertIn("no", command.call_args_list[2].args)

  def test_unavailable_service_is_a_renderable_state(self):
    with patch.object(wifi, "nmcli", side_effect=RuntimeError("service unavailable")):
      result = wifi.status()
      self.assertFalse(result["available"])
      self.assertEqual(result["networks"], [])
      self.assertIn("unavailable", result["title"])

  def test_failed_connection_clears_busy_and_reports_failure(self):
    with tempfile.TemporaryDirectory() as runtime, \
        patch.dict(os.environ, {"XDG_RUNTIME_DIR": runtime}), \
        patch.object(wifi, "update") as update, patch.object(wifi, "eww"), \
        patch.object(wifi, "nmcli", side_effect=RuntimeError("connection failed")) as command:
      wifi.action("connect", wifi.token("wlan0", "AA:BB", "saved-uuid", security="WPA2"))
      self.assertEqual(command.call_args.args, ("--wait", "25", "connection", "up",
        "uuid", "saved-uuid", "ifname", "wlan0", "ap", "AA:BB"))
      self.assertIn(unittest.mock.call(wifi_busy=False), update.call_args_list)
      self.assertTrue(any("failed" in call.kwargs.get("wifi_notice", "")
        for call in update.call_args_list))

  def test_new_network_opens_setup_for_that_ssid_without_a_shell(self):
    ssid = "-Office's $(not-a-command)"
    with tempfile.TemporaryDirectory() as runtime, \
        patch.dict(os.environ, {"XDG_RUNTIME_DIR": runtime}), \
        patch.object(wifi, "update"), patch.object(wifi, "eww"), \
        patch.object(wifi, "control") as control, patch.object(wifi.subprocess, "Popen") as launch:
      wifi.action("connect", wifi.token("wlan0", "AA:BB", "", ssid, "WPA2"))
      control.assert_called_once_with("close", "wifi-panel")
      self.assertEqual(launch.call_args.args[0],
        [sys.executable, str(SCRIPTS / "wifi_prompt.py"), unittest.mock.ANY])
      self.assertNotIn("shell", launch.call_args.kwargs)

  def test_password_is_sent_over_stdin_instead_of_shell(self):
    with patch.object(wifi_prompt.subprocess, "run") as command:
      command.return_value.returncode = 0
      wifi_prompt.connect("wlan0", "AA:BB", "Office", "secret $(command)")
      self.assertEqual(command.call_args.kwargs["input"], "secret $(command)\n")
      self.assertNotIn("secret $(command)", command.call_args.args[0])
      self.assertNotIn("shell", command.call_args.kwargs)

  def test_open_network_connects_without_a_password_dialog(self):
    with tempfile.TemporaryDirectory() as runtime, \
        patch.dict(os.environ, {"XDG_RUNTIME_DIR": runtime}), \
        patch.object(wifi, "update"), patch.object(wifi, "eww"), \
        patch.object(wifi, "nmcli", return_value="") as command, \
        patch.object(wifi.subprocess, "Popen") as launch:
      wifi.action("connect", wifi.token("wlan0", "AA:BB", "", "Guest", "--"))
      self.assertIn(unittest.mock.call("--wait", "25", "device", "wifi", "connect",
        "Guest", "ifname", "wlan0", "bssid", "AA:BB", timeout=28),
        command.call_args_list)
      launch.assert_not_called()

class PanelTests(unittest.TestCase):
  def test_empty_ipc_response_is_not_treated_as_success(self):
    with patch.object(panels, "eww", return_value=""):
      with self.assertRaisesRegex(RuntimeError, "empty response"):
        panels.active_windows()

  def test_switch_closes_previous_panel_before_opening_next(self):
    with tempfile.TemporaryDirectory() as runtime, \
        patch.dict(os.environ, {"XDG_RUNTIME_DIR": runtime}), \
        patch.object(panels, "active_windows", return_value={"wifi-panel"}), \
        patch.object(panels, "focused_screen", return_value="0"), \
        patch.object(panels, "eww", return_value="false") as command:
      panels.control("toggle", "calendar-panel")
      calls = command.call_args_list
      self.assertLess(calls.index(unittest.mock.call("close", "wifi-panel")),
        calls.index(unittest.mock.call("open", "calendar-panel", "--screen", "0")))

  def test_toggle_open_panel_only_closes_it(self):
    with tempfile.TemporaryDirectory() as runtime, \
        patch.dict(os.environ, {"XDG_RUNTIME_DIR": runtime}), \
        patch.object(panels, "active_windows", return_value={"wifi-panel"}), \
        patch.object(panels, "eww") as command:
      panels.control("toggle", "wifi-panel")
      self.assertIn(unittest.mock.call("update", "wifi_open=false"), command.call_args_list)
      self.assertIn(unittest.mock.call("close", "wifi-panel"), command.call_args_list)
      self.assertFalse(any(call.args[0] == "open" for call in command.call_args_list))

if __name__ == "__main__":
  unittest.main()
