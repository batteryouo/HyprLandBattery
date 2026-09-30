# SDDM login screen

Customizations on top of the AUR package `sddm-astronaut-theme`. Unlike the
rest of `dotfiles/`, **nothing here is symlinked by `install.sh`** — SDDM reads
from system directories, so these files are copies kept for backup and have to
be installed manually.

A `sddm-astronaut-theme` package upgrade overwrites the QML files, so this
directory is also what you re-apply from after `pacman -Syu`.

## Install

```sh
sudo pacman -S --needed sddm
yay -S sddm-astronaut-theme

cd dotfiles/sddm
sudo cp etc/sddm.conf.d/*.conf                  /etc/sddm.conf.d/
sudo cp faces/battery.face.icon                 /usr/share/sddm/faces/
sudo cp themes/sddm-astronaut-theme/Main.qml    /usr/share/sddm/themes/sddm-astronaut-theme/
sudo cp themes/sddm-astronaut-theme/Components/*.qml \
                                                /usr/share/sddm/themes/sddm-astronaut-theme/Components/
sudo cp themes/sddm-astronaut-theme/Themes/battery.conf \
                                                /usr/share/sddm/themes/sddm-astronaut-theme/Themes/
sudo sed -i 's|^ConfigFile=.*|ConfigFile=Themes/battery.conf|' \
  /usr/share/sddm/themes/sddm-astronaut-theme/metadata.desktop
```

Preview without logging out:

```sh
QML_XHR_ALLOW_FILE_READ=1 sddm-greeter-qt6 \
  --test-mode --theme /usr/share/sddm/themes/sddm-astronaut-theme/
```

The environment variable is only needed for this manual preview. The real
greeter picks it up from `GreeterEnvironment` in `etc/sddm.conf.d/virtualkbd.conf`.

To restore the stock theme: `sudo pacman -S sddm-astronaut-theme --overwrite '*'`.

## What was changed

`Themes/battery.conf` is a new theme variant (copied from the bundled
`astronaut.conf`) using Catppuccin Mocha colors, JetBrainsMono Nerd Font, the
`CuteAru.png` wallpaper, and a left-aligned login form.

QML changes on top of the stock theme:

- **`Components/Avatar.qml`** (new) — user picture above the login fields. It
  reads SDDM's `userModel`, so the picture follows whatever username is typed
  or picked from the dropdown, and falls back to the last-logged-in user.
- **`Components/StatusInfo.qml`** (new) — battery percentage and network state
  in the top-right corner. The greeter has no session, so there is no upower or
  NetworkManager to ask; it reads sysfs directly, which is why
  `QML_XHR_ALLOW_FILE_READ=1` is needed. Both the battery (`BAT0`) and the
  interface name (`wlp0s20f3`) are hardcoded to this laptop.
- **`Components/Clock.qml`** — gained a `baseSize` property so the corner clock
  can be scaled independently of the global font size.
- **`Components/LoginForm.qml`** — clock hidden (it is rendered standalone from
  `Main.qml` instead), avatar added, input field made shorter.
- **`Components/Input.qml`** — exposes `typedUsername` so the avatar can track
  what is being typed.
- **`Main.qml`** — narrower login form, clock moved to the bottom-right corner
  at half size, status info anchored top-right.

## Regenerating the avatar

`faces/battery.face.icon` is a PNG despite the extension, cropped from the
wallpaper. The round shape is baked into the alpha channel because Qt6
`MultiEffect` mask rendering drew nothing at all in this greeter build.

```sh
magick dotfiles/.config/hypr/images/CuteAru.png \
  -crop 1040x1040+1048+704 +repage -resize 512x512 \
  \( -size 512x512 xc:none -fill white -draw "circle 256,256 256,0" \) \
  -alpha set -compose DstIn -composite \
  png:dotfiles/sddm/faces/battery.face.icon
```

SDDM looks the file up as `<username>.face.icon`, so it needs renaming for a
different account. Users without such a file get SDDM's built-in silhouette,
which is square.
