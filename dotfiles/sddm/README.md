# SDDM login screen

Customizations on top of the AUR package `sddm-astronaut-theme`. Unlike the
rest of `dotfiles/`, **nothing here is symlinked by `install.sh`** — SDDM reads
from system directories, so `apply.sh` copies these files into place instead.

## Install

```sh
yay -S sddm-astronaut-theme
dotfiles/sddm/apply.sh
```

`apply.sh` re-runs itself through sudo and is safe to repeat: it installs the
`/etc/sddm.conf.d` snippets and the theme files, then points the theme's
`metadata.desktop` at `Themes/battery.conf`. Re-run it after editing anything
in this directory.

## Surviving upgrades

An upgrade of `sddm-astronaut-theme` only reverts the files the package owns
and this repo modifies — `Main.qml`, `Components/{Clock,Input,LoginForm}.qml`
and the `ConfigFile` line in `metadata.desktop`. Files added here
(`Avatar.qml`, `StatusInfo.qml`, `Themes/battery.conf`) and the avatar belong
to no package, so pacman leaves them alone.

`apply.sh` installs a pacman hook that restores those files automatically, so
an upgrade needs no follow-up. The hook runs as root and therefore must not
execute anything out of a checkout the user can write to: `apply.sh` keeps a
root-owned copy of itself and the theme files in
`/usr/local/share/hyprlandbattery/sddm`, refreshed on every run, and the hook
executes that copy instead of this one.

To undo the automation: `sudo rm /etc/pacman.d/hooks/95-sddm-astronaut-theme-overlay.hook`.

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

To set or change yours:

```sh
dotfiles/sddm/apply.sh --avatar ~/Pictures/whatever.png
```

That center-crops the image to a square, bakes a round alpha channel into it
and installs it as `<username>.face.icon`. Add `--user NAME` for a different
account. The greeter runs as the `sddm` user and cannot read into a 700 home
directory, which is why the picture has to live in `/usr/share/sddm/faces`
rather than somewhere like `~/.face.icon`.

`faces/example.face.icon` is only a neutral placeholder. The real avatar is a
personal picture that is deliberately not tracked here, so swapping it out
never dirties the repo.

The round shape is baked into the alpha channel because Qt6 `MultiEffect` mask
rendering drew nothing at all in this greeter build, so `Avatar.qml` displays
the file as-is with no masking.
