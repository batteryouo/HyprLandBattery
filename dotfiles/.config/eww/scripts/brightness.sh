#!/usr/bin/env bash
# Current screen brightness as an integer percentage.
set -euo pipefail

cur="$(brightnessctl get)"
max="$(brightnessctl max)"
echo $(( 100 * cur / max ))
