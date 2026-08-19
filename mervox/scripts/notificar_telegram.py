"""
notificar_telegram.py - v1.0
Envia un mensaje de texto al chat de Telegram configurado por variables de entorno.
Uso: python notificar_telegram.py "mensaje a enviar"
"""
import os
import sys
import logging
import requests

logging.basicConfig(
    filename="mervox.log",
    level=logging.INFO,
    format="%(asctime)s [notificar_telegram] %(levelname)s: %(message)s"
)
log = logging.getLogger("notificar_telegram")

def enviar(mensaje: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.error("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el entorno.")
        print("ERROR: faltan variables de entorno de Telegram", file=sys.stderr)
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": chat_id, "text": mensaje}, timeout=20)
        resp.raise_for_status()
        log.info(f"Mensaje enviado: {mensaje[:80]}")
        return True
    except Exception as e:
        log.error(f"No se pudo enviar el mensaje: {e}")
        print(f"ERROR enviando a Telegram: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python notificar_telegram.py \"mensaje\"")
        sys.exit(1)
    ok = enviar(sys.argv[1])
    sys.exit(0 if ok else 1)
