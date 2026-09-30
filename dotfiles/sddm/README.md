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
sudo cp faces/example.face.icon                 "/usr/share/sddm/faces/$USER.face.icon"
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
  NetworkManager to ask; it reads sysfs and procfs directly, which is why
  `QML_XHR_ALLOW_FILE_READ=1` is needed. Nothing is tied to this machine: the
  network state comes from the default route in `/proc/net/route` (whose
  interface name also picks the Wi-Fi or Ethernet icon), and the battery is
  found by probing the usual `/sys/class/power_supply` names, since
  `XMLHttpRequest` cannot list a directory. The battery line hides itself when
  no battery is found, so a desktop shows only the network state.
- **`Components/Clock.qml`** — gained a `baseSize` property so the corner clock
  can be scaled independently of the global font size.
- **`Components/LoginForm.qml`** — clock hidden (it is rendered standalone from
  `Main.qml` instead), avatar added, input field made shorter.
- **`Components/Input.qml`** — exposes `typedUsername` so the avatar can track
  what is being typed.
- **`Main.qml`** — narrower login form, clock moved to the bottom-right corner
  at half size, status info anchored top-right.

## Avatar

SDDM looks up `/usr/share/sddm/faces/<username>.face.icon`, which is a plain
PNG despite the extension. A user without one gets SDDM's built-in silhouette.

`faces/example.face.icon` is only a neutral placeholder — the real avatar is a
personal picture that is deliberately not tracked here, so it survives being
swapped out without dirtying the repo. To use your own, crop a square, bake a
round alpha channel into it, and install it under your username:

```sh
magick <picture> \
  -resize 512x512^ -gravity center -extent 512x512 \
  \( -size 512x512 xc:none -fill white -draw "circle 256,256 256,0" \) \
  -alpha set -compose DstIn -composite \
  png:/tmp/face.png
sudo cp /tmp/face.png "/usr/share/sddm/faces/$USER.face.icon"
```

The round shape has to be baked into the alpha channel because Qt6
`MultiEffect` mask rendering drew nothing at all in this greeter build, so
`Avatar.qml` displays the file as-is with no masking.

To crop a specific region instead of the center, replace the resize/extent
pair with `-crop <w>x<h>+<x>+<y> +repage -resize 512x512`.
