#!/usr/bin/env bash
# Current output volume as an integer percentage.
set -euo pipefail

wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{printf "%d\n", $2 * 100}'
