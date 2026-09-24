# HyprLandBattery

Personal Hyprland desktop configuration for Arch Linux, written using Hyprland's
[Lua configuration API](https://wiki.hyprland.org/Configuring/Lua/) (`hl.config`,
`hl.bind`, etc.) instead of the traditional `hyprland.conf` syntax.

## Structure

```
dotfiles/.config/
├── hypr/
│   ├── hyprland.lua          # Entry point; requires all modules below
│   ├── config/
│   │   ├── options.lua       # Shared variables: terminal, file manager, launcher, mod key
│   │   ├── monitors.lua      # Monitor auto-detection (preferred resolution, auto position/scale)
│   │   ├── startup.lua       # Autostart programs
│   │   ├── environment.lua   # Cursor size env vars
│   │   ├── appearance.lua    # Gaps, borders, rounding, shadows, blur
│   │   ├── animations.lua    # Bezier curves and spring animations
│   │   ├── layouts.lua       # dwindle / master / scrolling layout options
│   │   ├── input.lua         # Keyboard, mouse, touchpad, gestures
│   │   ├── keybindings.lua   # Keybindings
│   │   └── rules.lua         # Window rules
│   ├── plugins/
│   │   └── hyprbars.lua      # Window title bar plugin (close/maximize/float buttons)
│   ├── hyprpaper.conf        # Wallpaper configuration
│   └── images/CuteAru.png    # Wallpaper image
├── waybar/                   # Top status bar (config.jsonc + style.css)
└── mako/config                # Notification daemon config
```

## Features

- **Theme**: Catppuccin Mocha color scheme throughout, with a blue-green gradient
  on active window borders and a floating, rounded-pill Waybar.
- **Waybar modules**: workspaces, active window title, clock, volume, network,
  battery, and system tray.
- **Startup apps**: `kitty`, `nm-applet`, `waybar`, `hyprpaper`, `mako`, the
  polkit-kde authentication agent, `hyprpm reload`, and `cliphist` watchers for
  both text and image clipboard history. The `hyprswitch` daemon is also
  started, with any stale instance killed first and its output logged to
  `$XDG_RUNTIME_DIR/hyprswitch-init.log`.

### Keybindings

| Keys | Action |
| --- | --- |
| `Ctrl + Alt + T` | Open terminal |
| `Alt + F4` | Close focused window |
| `Alt + Tab` / `Alt + Shift + Tab` | Switch windows (hyprswitch, forward/reverse) |
| `Super + M` | Power menu (Lock / Logout / Suspend / Reboot / Shutdown via wofi) |
| `Super + L` | Lock screen (hyprlock) |
| `Super + E` | Open file manager |
| `Super + V` | Toggle floating |
| `Super + R` | Open app launcher |
| `Super + P` | Pseudo-tile window |
| `Super + J` | Toggle split |
| `F11` | Toggle fullscreen |
| `Alt + F10` | Toggle maximize |
| `Print` / `Super + Shift + S` | Screenshot a selected region (saved + copied to clipboard) |
| `Super + Print` | Screenshot the full output |
| `Super + Shift + V` | Open clipboard history |
| `Super + arrow keys` | Move focus |
| `Super + Shift + arrow keys` | Move window |
| `Super + 0-9` | Switch workspace |
| `Super + Shift + 0-9` | Move window to workspace |
| `` Super + ` `` | Toggle special workspace "magic" |
| `` Super + Shift + ` `` | Move window to special workspace "magic" |
| `Super + mouse wheel` | Switch to adjacent workspace |
| `Ctrl + Alt + Left/Right` | Switch to adjacent workspace |
| `Super + mouse drag / resize` | Drag or resize window with mouse |
| Volume / brightness / media keys | Handled via `wpctl`, `brightnessctl`, `playerctl` |

## Prerequisites

This setup targets Arch Linux. The following packages are expected:

`hyprland`, `hyprpaper`, `hyprlock`, `hyprswitch`, `waybar`, `mako`, `wofi`,
`kitty`, `thunar`, `grim`, `slurp`, `wl-clipboard`, `cliphist`, `wireplumber`,
`brightnessctl`, `playerctl`, `pavucontrol`, `network-manager-applet`,
`polkit-kde-agent`, and the `ttf-jetbrains-mono-nerd` font.

The `hyprbars` plugin is installed separately through `hyprpm` (see below), not
through `pacman`.

## Installation

```sh
git clone <this-repo-url>
cd HyprLandBattery
./install.sh
```

`install.sh` will:

1. Check for missing required packages (via `pacman`) and print the install
   command for any that are missing.
2. Symlink `dotfiles/.config/hypr`, `dotfiles/.config/waybar`, and
   `dotfiles/.config/mako` into `~/.config/`, backing up any existing
   directory first (as `<name>.backup-<timestamp>`).

Run `./install.sh --check` to only check for missing packages without
touching `~/.config`.

After installing, enable the `hyprbars` plugin:

```sh
hyprpm add https://github.com/hyprwm/hyprland-plugins
hyprpm enable hyprbars
```

## Notes

- There is no `hyprlock.conf` in this repo, so `hyprlock` uses its built-in
  default appearance. Add one under `dotfiles/.config/hypr/` if you want to
  customize the lock screen.
- `dotfiles/.config/hypr/config/input.lua` includes a per-device override for
  a device named `epic-mouse-v1` — this is a placeholder from the Hyprland
  example config and has no effect unless you rename it to match an actual
  device from `hyprctl devices`.
