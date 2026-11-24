#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd "$(dirname "$0")/.."
exec python -m s_alpha.fusion_ui "$@"
