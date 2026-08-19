"""
mervox v1.0 - notificar_telegram.py
Envia un mensaje de texto al chat configurado, usado en distintos
puntos del pipeline para avisar el progreso.
"""

import os
import sys

import requests


def main():
    if len(sys.argv) < 2:
        print("Uso: python notificar_telegram.py '<mensaje>'")
        sys.exit(1)

    mensaje = sys.argv[1]
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el entorno.")
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": f"[mervox] {mensaje}"})
    resp.raise_for_status()
    print("Notificacion enviada.")


if __name__ == "__main__":
    main()
