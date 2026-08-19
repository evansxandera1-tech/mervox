#!/data/data/com.termux/files/usr/bin/bash
# iniciar_panel.sh - v1.0
# Lanzador del panel de control web de mervox.
export MERVOX_REPO="$(gh api user -q .login)/mervox"
export GH_TOKEN="$(gh auth token)"
cd "$(dirname "$0")"
python panel_control.py
