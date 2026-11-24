#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd "$(dirname "$0")/.."
command -v pkg >/dev/null || { echo "Run inside Termux"; exit 1; }
pkg install -y python git
python -m s_alpha.doctor
python -m unittest discover -s tests -v
echo "Checks passed. Start with: bash scripts/start-termux.sh"
