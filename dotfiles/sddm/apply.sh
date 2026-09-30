#!/usr/bin/env bash
#
# apply.sh — Install this repo's SDDM customizations over the
# sddm-astronaut-theme package.
#
# Usage:
#   ./apply.sh                    Re-apply the theme files
#   ./apply.sh --avatar PICTURE   Also set the login avatar from an image
#   ./apply.sh --user NAME        Install the avatar for another account
#
# Re-runs itself through sudo, since everything lands in /usr/share and /etc.
# Safe to re-run, which is the point: a sddm-astronaut-theme upgrade puts the
# stock QML back, and this restores it.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_DIR="/usr/share/sddm/themes/sddm-astronaut-theme"
FACES_DIR="/usr/share/sddm/faces"
AVATAR_SIZE=512

log() { printf '==> %s\n' "$1"; }
die() { printf 'error: %s\n' "$1" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage:
  ./apply.sh                    Re-apply the theme files
  ./apply.sh --avatar PICTURE   Also set the login avatar from an image
  ./apply.sh --user NAME        Install the avatar for another account
EOF
}

avatar=""
# Under sudo, $USER is root, so the invoking account is the one to install for.
target_user="${SUDO_USER:-$USER}"

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --avatar)
        [ "$#" -ge 2 ] || die "--avatar needs an image path"
        avatar="$2"
        shift 2
        ;;
      --user)
        [ "$#" -ge 2 ] || die "--user needs an account name"
        target_user="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        usage >&2
        die "unknown argument: $1"
        ;;
    esac
  done
}

# Resolve the avatar path before sudo changes the working directory context,
# so a relative path still means what the caller typed.
resolve_avatar() {
  [ -n "$avatar" ] || return 0
  [ -f "$avatar" ] || die "avatar image not found: $avatar"
  avatar="$(cd "$(dirname "$avatar")" && pwd)/$(basename "$avatar")"
}

elevate() {
  [ "$(id -u)" -ne 0 ] || return 0
  command -v sudo >/dev/null 2>&1 || die "this needs root and sudo is not installed"
  log "Re-running with sudo..."
  exec sudo -- "${BASH_SOURCE[0]}" "$@"
}

install_theme() {
  [ -d "$THEME_DIR" ] || die "$THEME_DIR not found; install it with: yay -S sddm-astronaut-theme"

  log "Installing SDDM configuration..."
  install -d /etc/sddm.conf.d
  install -m 644 "$SRC_DIR"/etc/sddm.conf.d/*.conf /etc/sddm.conf.d/

  log "Installing theme files..."
  install -m 644 "$SRC_DIR/themes/sddm-astronaut-theme/Main.qml" "$THEME_DIR/"
  install -m 644 "$SRC_DIR"/themes/sddm-astronaut-theme/Components/*.qml "$THEME_DIR/Components/"
  install -m 644 "$SRC_DIR/themes/sddm-astronaut-theme/Themes/battery.conf" "$THEME_DIR/Themes/"

  log "Selecting the battery.conf variant..."
  sed -i 's|^ConfigFile=.*|ConfigFile=Themes/battery.conf|' "$THEME_DIR/metadata.desktop"
}

install_avatar() {
  [ -n "$avatar" ] || return 0
  command -v magick >/dev/null 2>&1 || die "magick not found; install it with: sudo pacman -S imagemagick"
  id "$target_user" >/dev/null 2>&1 || die "no such user: $target_user"

  local half=$((AVATAR_SIZE / 2))
  local dest="$FACES_DIR/$target_user.face.icon"

  # The round shape is baked into the alpha channel rather than masked in QML,
  # because Qt6 MultiEffect mask rendering draws nothing in this greeter.
  log "Building a round avatar for '$target_user' from $avatar..."
  install -d "$FACES_DIR"
  magick "$avatar" \
    -resize "${AVATAR_SIZE}x${AVATAR_SIZE}^" -gravity center \
    -extent "${AVATAR_SIZE}x${AVATAR_SIZE}" \
    \( -size "${AVATAR_SIZE}x${AVATAR_SIZE}" xc:none \
       -fill white -draw "circle $half,$half $half,0" \) \
    -alpha set -compose DstIn -composite \
    "png:$dest"
  chmod 644 "$dest"
  log "Installed $dest"
}

main() {
  parse_args "$@"
  resolve_avatar
  elevate "$@"
  install_theme
  install_avatar
  log "Done. Preview without logging out:"
  log "  QML_XHR_ALLOW_FILE_READ=1 sddm-greeter-qt6 --test-mode --theme $THEME_DIR/"
}

main "$@"
