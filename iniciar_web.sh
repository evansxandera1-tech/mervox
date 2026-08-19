#!/usr/bin/env bash
# mervox v1.0 - iniciar_web.sh
# Lanzador de la interfaz web local para revisar estado/logs.

cd "$(dirname "$0")"
pip install -q flask
python3 app.py
