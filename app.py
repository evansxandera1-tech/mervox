"""
mervox v1.0 - app.py
Interfaz web simple para ver el estado y log de la ultima corrida del pipeline.
Lee estado.json (generado por el workflow) y lo muestra en una pagina simple.
"""

import json
import logging
import os

from flask import Flask, render_template_string

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [app] %(levelname)s: %(message)s",
)
log = logging.getLogger("app")

app = Flask(__name__)

RUTA_ESTADO = os.path.join(os.path.dirname(__file__), "estado.json")

PLANTILLA = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>mervox - estado</title>
  <style>
    body { font-family: monospace; background: #111; color: #eee; padding: 20px; }
    h1 { color: #ff9500; }
    .clip { background: #222; padding: 10px; margin: 6px 0; border-radius: 6px; }
    .log { white-space: pre-wrap; background: #000; padding: 10px; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>mervox - estado</h1>
  {% if estado %}
    <p><b>Usuario:</b> {{ estado.get("usuario", "-") }}</p>
    <p><b>Estado:</b> {{ estado.get("estado", "-") }}</p>
    <p><b>Ultima actualizacion:</b> {{ estado.get("actualizado", "-") }}</p>
    <h3>Clips generados:</h3>
    {% for clip in estado.get("clips", []) %}
      <div class="clip">{{ clip }}</div>
    {% endfor %}
    <h3>Log:</h3>
    <div class="log">{{ estado.get("log", "sin datos") }}</div>
  {% else %}
    <p>Todavia no hay ninguna corrida registrada.</p>
  {% endif %}
</body>
</html>
"""


@app.route("/")
def index():
    estado = None
    if os.path.exists(RUTA_ESTADO):
        with open(RUTA_ESTADO, "r", encoding="utf-8") as f:
            estado = json.load(f)
    return render_template_string(PLANTILLA, estado=estado)


if __name__ == "__main__":
    log.info("Iniciando interfaz web de mervox en puerto 5000...")
    app.run(host="0.0.0.0", port=5000)
