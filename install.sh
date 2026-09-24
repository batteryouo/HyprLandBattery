#!/usr/bin/env bash
#
# install.sh — Symlink this repo's dotfiles into ~/.config.
#
# Usage:
#   ./install.sh            Symlink the config directories
#   ./install.sh --check    Only check for missing packages, don't install
#
# Safe to re-run: existing (non-symlink) configs are backed up with a
# timestamp suffix before the symlink is created.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$REPO_DIR/dotfiles/.config"
TARGET_DIR="$HOME/.config"

# Top-level config directories/files this repo manages under ~/.config.
CONFIGS=(hypr waybar mako)

# Packages expected to be installed on the system (Arch Linux package names).
# hyprbars is a Hyprland plugin managed separately via hyprpm, not pacman.
REQUIRED_PACKAGES=(
    hyprland
    hyprpaper
    hyprlock
    hyprswitch
    waybar
    mako
    wofi
    kitty
    thunar
    grim
    slurp
    wl-clipboard
    cliphist
    wireplumber
    brightnessctl
    playerctl
    pavucontrol
    network-manager-applet
    polkit-kde-agent
    ttf-jetbrains-mono-nerd
)

log()  { printf '==> %s\n' "$1"; }
warn() { printf 'warning: %s\n' "$1" >&2; }

check_packages() {
    if ! command -v pacman >/dev/null 2>&1; then
        warn "pacman not found; skipping dependency check (this repo targets Arch Linux)."
        return
    fi

    local missing=()
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if ! pacman -Qi "$pkg" >/dev/null 2>&1; then
            missing+=("$pkg")
        fi
    done

    if [ "${#missing[@]}" -eq 0 ]; then
        log "All required packages are installed."
    else
        warn "Missing packages: ${missing[*]}"
        warn "Install them with: sudo pacman -S ${missing[*]}"
        warn "(or use an AUR helper such as yay/paru if a package is AUR-only)"
    fi
}

link_config() {
    local name="$1"
    local src="$SOURCE_DIR/$name"
    local dest="$TARGET_DIR/$name"

    if [ ! -e "$src" ]; then
        warn "Source '$src' does not exist, skipping."
        return
    fi

    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
        log "'$dest' is already linked correctly, skipping."
        return
    fi

    if [ -e "$dest" ] || [ -L "$dest" ]; then
        local backup="${dest}.backup-$(date +%Y%m%d%H%M%S)"
        warn "'$dest' already exists, backing up to '$backup'."
        mv "$dest" "$backup"
    fi

    ln -s "$src" "$dest"
    log "Linked '$dest' -> '$src'."
}

main() {
    mkdir -p "$TARGET_DIR"

    log "Checking for required packages..."
    check_packages

    if [ "${1:-}" = "--check" ]; then
        exit 0
    fi

    log "Linking config directories into $TARGET_DIR ..."
    for name in "${CONFIGS[@]}"; do
        link_config "$name"
    done

    log "Done."
    log "Note: the hyprbars plugin is loaded via hyprpm and is not installed by this script."
    log "Enable it with: hyprpm add https://github.com/hyprwm/hyprland-plugins && hyprpm enable hyprbars"
}

main "$@"
