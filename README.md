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
│   ├── hyprlock.conf         # Lock screen appearance
│   ├── hyprpaper.conf        # Wallpaper configuration
│   └── images/CuteAru.png    # Wallpaper image
├── waybar/                   # Top status bar (config.jsonc + style.css)
├── mako/config               # Notification daemon config
└── fastfetch/                # System info readout (config.jsonc + logo/)

dotfiles/sddm/                # SDDM login screen theme (installed manually)
```

## Features

- **Theme**: Catppuccin Mocha color scheme throughout, with a blue-green gradient
  on active window borders and a floating, rounded-pill Waybar.
- **Waybar modules**: workspaces, active window title, clock, volume, network,
  battery, system tray, and a power button (opens the same power menu as
  `Super + M`).
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
| `Super + Tab` | Switch to the next empty workspace |
| `Ctrl + Alt + Left/Right` | Switch to adjacent workspace |
| `Super + mouse drag / resize` | Drag or resize window with mouse |
| Volume / brightness / media keys | Handled via `wpctl`, `brightnessctl`, `playerctl` |

## Prerequisites

This setup targets Arch Linux. The following packages are expected:

`hyprland`, `hyprpaper`, `hyprlock`, `hyprswitch`, `uwsm`, `sddm`, `waybar`,
`mako`, `fastfetch`, `wofi`, `kitty`, `thunar`, `grim`, `slurp`,
`wl-clipboard`, `cliphist`, `wireplumber`, `brightnessctl`, `playerctl`, `pavucontrol`,
`network-manager-applet`, `polkit-kde-agent`, and the
`ttf-jetbrains-mono-nerd` font.

Two things do not come from `pacman`: the `hyprbars` plugin (installed through
`hyprpm`) and the `sddm-astronaut-theme` login screen (from the AUR).

## Installation

Full setup on a fresh Arch machine:

```sh
# 1. Packages
sudo pacman -S --needed hyprland hyprpaper hyprlock hyprswitch uwsm sddm \
  waybar mako fastfetch wofi kitty thunar grim slurp wl-clipboard cliphist \
  wireplumber brightnessctl playerctl pavucontrol network-manager-applet \
  polkit-kde-agent ttf-jetbrains-mono-nerd

# 2. Dotfiles — symlinks hypr, waybar, mako and fastfetch into ~/.config
git clone <this-repo-url>
cd HyprLandBattery
./install.sh

# 3. Window title bars
hyprpm add https://github.com/hyprwm/hyprland-plugins
hyprpm enable hyprbars

# 4. Login screen (see dotfiles/sddm/README.md for details)
yay -S sddm-astronaut-theme
cd dotfiles/sddm
sudo cp etc/sddm.conf.d/*.conf /etc/sddm.conf.d/
sudo cp faces/example.face.icon "/usr/share/sddm/faces/$USER.face.icon"
sudo cp themes/sddm-astronaut-theme/Main.qml \
        /usr/share/sddm/themes/sddm-astronaut-theme/
sudo cp themes/sddm-astronaut-theme/Components/*.qml \
        /usr/share/sddm/themes/sddm-astronaut-theme/Components/
sudo cp themes/sddm-astronaut-theme/Themes/battery.conf \
        /usr/share/sddm/themes/sddm-astronaut-theme/Themes/
sudo sed -i 's|^ConfigFile=.*|ConfigFile=Themes/battery.conf|' \
  /usr/share/sddm/themes/sddm-astronaut-theme/metadata.desktop
cd ../..

# 5. Start the display manager on boot, then reboot
sudo systemctl enable sddm
```

`install.sh` only handles step 2: it checks for missing packages via `pacman`
and symlinks `dotfiles/.config/{hypr,waybar,mako,fastfetch}` into `~/.config/`, backing
up any existing directory first (as `<name>.backup-<timestamp>`). Run
`./install.sh --check` to check packages without touching `~/.config`.

## Notes

- `dotfiles/.config/hypr/hyprlock.conf` themes the lock screen (Catppuccin
  Mocha colors, the repo wallpaper, clock, date, and battery percentage). It
  reads battery capacity from `/sys/class/power_supply/BAT0`, so update that
  path if your hardware exposes a different battery name.
- The fastfetch logos under `dotfiles/.config/fastfetch/logo/` are personal
  images and stay untracked; only the ASCII `cat.txt` is committed as an
  example. After cloning, point `logo.source` in `config.jsonc` at `cat.txt`
  or at an image of your own.
- `dotfiles/sddm/` holds the login screen theme (a customized
  `sddm-astronaut-theme`). It is **not** symlinked by `install.sh` because SDDM
  reads from system directories — see `dotfiles/sddm/README.md` for how to
  install it and how to re-apply it after a package upgrade.
- `dotfiles/.config/hypr/config/input.lua` includes a per-device override for
  a device named `epic-mouse-v1` — this is a placeholder from the Hyprland
  example config and has no effect unless you rename it to match an actual
  device from `hyprctl devices`.
