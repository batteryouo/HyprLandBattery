#!/usr/bin/env python3
import base64
import json
import os
import subprocess
import sys
import threading

import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

CSS = b"""
window { background: #1e1e2e; color: #cdd6f4; }
.root { padding: 24px; }
.icon { color: #89b4fa; font: 30px 'JetBrainsMono Nerd Font'; margin-right: 14px; }
.title { color: #cdd6f4; font: bold 18px 'JetBrainsMono Nerd Font'; }
.subtitle, .hint { color: #a6adc8; font: 11px 'JetBrainsMono Nerd Font'; }
.network { background: #313244; border-radius: 10px; padding: 12px; margin: 18px 0 12px; }
.network-name { color: #a6e3a1; font: bold 13px 'JetBrainsMono Nerd Font'; }
entry { background: #313244; color: #cdd6f4; border: 1px solid #45475a;
  border-radius: 8px; padding: 10px; font: 12px 'JetBrainsMono Nerd Font'; }
entry:focus { border-color: #89b4fa; }
checkbutton { color: #bac2de; font: 11px 'JetBrainsMono Nerd Font'; margin-top: 8px; }
.error { color: #f38ba8; font: 10px 'JetBrainsMono Nerd Font'; margin-top: 8px; }
button { background: #313244; color: #cdd6f4; border-radius: 8px; padding: 8px 16px;
  font: 11px 'JetBrainsMono Nerd Font'; margin-top: 16px; }
button:hover { background: #45475a; }
.connect { background: #89b4fa; color: #1e1e2e; font-weight: bold; margin-left: 8px; }
.connect:hover { background: #b4befe; }
"""

def decode_token(value):
  device, bssid, _uuid, ssid, security = json.loads(base64.urlsafe_b64decode(value))
  return device, bssid, ssid, security

def connect(device, bssid, ssid, password):
  args = ["nmcli", "--colors", "no", "--wait", "30"]
  if password is not None:
    args.append("--ask")
  args.extend(["device", "wifi", "connect", ssid, "ifname", device, "bssid", bssid])
  result = subprocess.run(args, input=None if password is None else password + "\n",
    text=True, capture_output=True, timeout=35,
    env={**os.environ, "LC_ALL": "C"})
  if result.returncode:
    raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Connection failed.")

class WifiPrompt(Gtk.Window):
  def __init__(self, device, bssid, ssid, secured):
    super().__init__(title="Wi-Fi authentication")
    self.device, self.bssid, self.ssid, self.secured = device, bssid, ssid, secured
    self.set_default_size(430, 300 if secured else 230)
    self.set_resizable(False)
    self.set_position(Gtk.WindowPosition.CENTER)
    self.set_border_width(1)
    self.connect("key-press-event", self.on_key)

    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    root.get_style_context().add_class("root")
    self.add(root)
    heading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    root.pack_start(heading, False, False, 0)
    icon = Gtk.Label(label="󰤨")
    icon.get_style_context().add_class("icon")
    heading.pack_start(icon, False, False, 0)
    copy = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    heading.pack_start(copy, True, True, 0)
    title = Gtk.Label(label="Join Wi-Fi network", xalign=0)
    title.get_style_context().add_class("title")
    copy.pack_start(title, False, False, 0)
    subtitle = Gtk.Label(label="Enter the network password to continue.", xalign=0)
    subtitle.get_style_context().add_class("subtitle")
    copy.pack_start(subtitle, False, False, 0)

    network = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    network.get_style_context().add_class("network")
    network.pack_start(Gtk.Label(label="󰤨  "), False, False, 0)
    name = Gtk.Label(label=ssid, xalign=0, ellipsize=3)
    name.get_style_context().add_class("network-name")
    network.pack_start(name, True, True, 0)
    root.pack_start(network, False, False, 0)

    self.password = Gtk.Entry()
    self.password.set_placeholder_text("Password")
    self.password.set_visibility(False)
    self.password.set_activates_default(True)
    self.password.set_no_show_all(not secured)
    root.pack_start(self.password, False, False, 0)
    show = Gtk.CheckButton(label="Show password")
    show.set_no_show_all(not secured)
    show.connect("toggled", lambda button: self.password.set_visibility(button.get_active()))
    root.pack_start(show, False, False, 0)
    self.error = Gtk.Label(xalign=0)
    self.error.get_style_context().add_class("error")
    root.pack_start(self.error, False, False, 0)

    actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    actions.set_halign(Gtk.Align.END)
    root.pack_end(actions, False, False, 0)
    cancel = Gtk.Button(label="Cancel")
    cancel.connect("clicked", lambda _button: self.close())
    actions.pack_start(cancel, False, False, 0)
    self.submit = Gtk.Button(label="Connect")
    self.submit.get_style_context().add_class("connect")
    self.submit.connect("clicked", self.on_submit)
    self.submit.set_can_default(True)
    self.set_default(self.submit)
    actions.pack_start(self.submit, False, False, 0)

  def on_key(self, _window, event):
    if event.keyval == 65307:
      self.close()

  def on_submit(self, _button):
    password = self.password.get_text() if self.secured else None
    if self.secured and not password:
      self.error.set_text("Enter the network password.")
      self.password.grab_focus()
      return
    self.error.set_text("Connecting…")
    self.submit.set_sensitive(False)
    threading.Thread(target=self.run_connection, args=(password,), daemon=True).start()

  def run_connection(self, password):
    try:
      connect(self.device, self.bssid, self.ssid, password)
      GLib.idle_add(self.close)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
      GLib.idle_add(self.connection_failed, str(error))

  def connection_failed(self, message):
    self.error.set_text(message.splitlines()[-1][:80])
    self.submit.set_sensitive(True)
    self.password.grab_focus()
    return False

def main():
  if len(sys.argv) != 2:
    raise SystemExit("Usage: wifi_prompt.py TOKEN")
  device, bssid, ssid, security = decode_token(sys.argv[1])
  provider = Gtk.CssProvider()
  provider.load_from_data(CSS)
  Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
  window = WifiPrompt(device, bssid, ssid, bool(security and security != "--"))
  window.connect("destroy", Gtk.main_quit)
  window.show_all()
  if window.secured:
    window.password.grab_focus()
  Gtk.main()

if __name__ == "__main__":
  main()
