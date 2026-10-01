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
│   │   ├── environment.lua   # Cursor/GTK/Qt theme env vars
│   │   ├── appearance.lua    # Gaps, borders, rounding, shadows, blur
│   │   ├── animations.lua    # Bezier curves and spring animations
│   │   ├── layouts.lua       # dwindle / master / scrolling layout options
│   │   ├── input.lua         # Keyboard, mouse, touchpad, gestures
│   │   ├── keybindings.lua   # Keybindings
│   │   └── rules.lua         # Window rules
│   ├── hyprlock.conf         # Lock screen appearance
│   ├── hyprpaper.conf        # Wallpaper configuration
│   └── images/CuteAru.png    # Wallpaper image
├── rofi/                     # App launcher / dmenu (config.rasi + Catppuccin Mocha theme)
├── waybar/                   # Top status bar (config.jsonc + style.css)
├── swaync/                    # Notification daemon + control center (Catppuccin Mocha theme)
├── fastfetch/                # System info readout (config.jsonc + logo/)
├── gtk-3.0/settings.ini      # GTK3 app theme (Thunar, Mousepad, pavucontrol, ...)
└── gtk-4.0/settings.ini      # GTK4 app theme

dotfiles/sddm/                # SDDM login screen theme (installed manually)
```

## Features

- **Theme**: Catppuccin Mocha color scheme throughout, with a blue-green gradient
  on active window borders and a floating, rounded-pill Waybar. GTK3/GTK4 apps
  (Thunar, Mousepad, pavucontrol, ...) and Qt apps (the polkit agent) follow
  the same theme via `gtk-3.0`/`gtk-4.0` settings and `QT_QPA_PLATFORMTHEME`.
- **Waybar modules**: workspaces, active window title, clock, volume, network,
  battery, system tray, a notification center button (left-click toggles the
  swaync panel, right-click toggles Do Not Disturb), and a power button (opens
  the same power menu as `Super + M`).
- **Startup apps**: `kitty`, `nm-applet`, `waybar`, `hyprpaper`, `swaync`, the
  polkit-kde authentication agent, `hyprpm reload`, and `cliphist` watchers for
  both text and image clipboard history. The `hyprswitch` daemon is also
  started, with any stale instance killed first and its output logged to
  `$XDG_RUNTIME_DIR/hyprswitch-init.log`.

### Keybindings

| Keys | Action |
| --- | --- |
| `Ctrl + Alt + T` | Open terminal |
| `Super + C` | Close focused window |
| `Alt + Tab` / `Alt + Shift + Tab` | Switch windows (hyprswitch, forward/reverse) |
| `Super + M` | Power menu (Lock / Logout / Suspend / Reboot / Shutdown via rofi) |
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
`swaync`, `fastfetch`, `rofi`, `kitty`, `thunar`, `grim`, `slurp`,
`wl-clipboard`, `cliphist`, `wireplumber`, `brightnessctl`, `playerctl`, `pavucontrol`,
`network-manager-applet`, `polkit-kde-agent`,
`ttf-jetbrains-mono-nerd`, `mousepad`, `loupe`, `mpv`, and `evince`.

`papirus-icon-theme` is also expected (used for folder/app icons).

The following do not come from `pacman` and are installed from the AUR:
`sddm-astronaut-theme` (login screen), `catppuccin-cursors-mocha` (cursor
theme), `catppuccin-gtk-theme-mocha` (GTK3/GTK4 theme), and
`papirus-folders-catppuccin-git` (recolors Papirus's folder icons).

## Installation

Full setup on a fresh Arch machine:

```sh
# 1. Packages
sudo pacman -S --needed hyprland hyprpaper hyprlock hyprswitch uwsm sddm \
  waybar swaync fastfetch rofi kitty thunar grim slurp wl-clipboard cliphist \
  wireplumber brightnessctl playerctl pavucontrol network-manager-applet \
  polkit-kde-agent ttf-jetbrains-mono-nerd mousepad loupe mpv evince \
  papirus-icon-theme

# 2. Dotfiles — symlinks hypr, waybar, swaync, fastfetch, rofi, gtk-3.0 and
#    gtk-4.0 into ~/.config
git clone <this-repo-url>
cd HyprLandBattery
./install.sh

# 3. Login screen (see dotfiles/sddm/README.md for details)
yay -S sddm-astronaut-theme
dotfiles/sddm/apply.sh --avatar ~/Pictures/whatever.png

# 3b. Cursor + GTK theme (AUR)
yay -S catppuccin-cursors-mocha catppuccin-gtk-theme-mocha papirus-folders-catppuccin-git
papirus-folders -C cat-mocha-blue --theme Papirus-Dark

# 4. Start the display manager on boot, then reboot
sudo systemctl enable sddm
```

`install.sh` handles step 2: it checks for missing packages via `pacman` and
symlinks `dotfiles/.config/{hypr,waybar,swaync,fastfetch,rofi,gtk-3.0,gtk-4.0}`
into `~/.config/`, backing up any existing directory first (as
`<name>.backup-<timestamp>`). Run `./install.sh --check` to check packages
without touching `~/.config`.

`papirus-folders` (step 3b) is a one-time imperative command, not a config
file, so it isn't run by `install.sh` — it recolors Papirus's folder icons on
disk to match the Mocha/blue theme. Re-run it if you ever reinstall
`papirus-icon-theme`.

Step 3 is `dotfiles/sddm/apply.sh`, which needs root and so re-runs itself
through sudo. Pass `--avatar` whenever you want a different login picture; the
argument is optional, and without it SDDM shows its own silhouette. The script
also installs a pacman hook that re-applies the theme after a
`sddm-astronaut-theme` upgrade, so upgrades need no follow-up.

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
- `dotfiles/.config/hypr/config/environment.lua` sets the cursor theme to
  `catppuccin-mocha-blue-cursors` (from the AUR `catppuccin-cursors-mocha`
  package). It's a starting template — swap the accent in both `XCURSOR_THEME`
  and `HYPRCURSOR_THEME` (e.g. to `catppuccin-mocha-mauve-cursors`) to change
  it later without starting from scratch.
- GTK/Qt theming covers classic GTK3 apps (Thunar, Mousepad, pavucontrol) and
  Qt apps (the polkit agent, via `QT_QPA_PLATFORMTHEME=gtk3`) fully. GTK4 apps
  built on libadwaita (e.g. Loupe) mostly ignore `gtk-theme-name` by design —
  they'll follow `gtk-application-prefer-dark-theme` for light/dark mode, but
  keep Adwaita's own accent color regardless of `gtk-4.0/settings.ini`.
