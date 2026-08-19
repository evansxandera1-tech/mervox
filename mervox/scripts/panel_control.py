"""
panel_control.py - v1.0
Interfaz web local (Flask) para ver desde el celular el estado de las
corridas del workflow mervox en GitHub Actions. Requiere GH_TOKEN
en el entorno (personal access token con permiso 'repo').
Uso: python panel_control.py
"""
import os
import logging
import requests
from flask import Flask, render_template_string

logging.basicConfig(
    filename="panel_control.log",
    level=logging.INFO,
    format="%(asctime)s [panel_control] %(levelname)s: %(message)s"
)
log = logging.getLogger("panel_control")

app = Flask(__name__)

REPO = os.environ.get("MERVOX_REPO", "")
GH_TOKEN = os.environ.get("GH_TOKEN", "")

PLANTILLA = """
<html><head><title>mervox - panel</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:sans-serif;background:#111;color:#eee;padding:16px}
.run{border:1px solid #333;border-radius:8px;padding:12px;margin-bottom:10px}
.ok{color:#4caf50}.fail{color:#f44336}.progreso{color:#ffb300}
</style></head><body>
<h2>mervox - corridas recientes</h2>
{% for r in runs %}
  <div class="run">
    <b>#{{ r.run_number }}</b> - {{ r.created_at }}<br>
    Estado: <span class="{{ r.clase }}">{{ r.status }} / {{ r.conclusion }}</span><br>
    <a href="{{ r.html_url }}" target="_blank">Ver en GitHub</a>
  </div>
{% else %}
  <p>No hay corridas todavia.</p>
{% endfor %}
</body></html>
"""

@app.route("/")
def index():
    runs = []
    if REPO and GH_TOKEN:
        try:
            url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=10"
            headers = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json"}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            for r in resp.json().get("workflow_runs", []):
                clase = "progreso"
                if r["status"] == "completed":
                    clase = "ok" if r["conclusion"] == "success" else "fail"
                runs.append({
                    "run_number": r["run_number"],
                    "created_at": r["created_at"],
                    "status": r["status"],
                    "conclusion": r["conclusion"] or "-",
                    "html_url": r["html_url"],
                    "clase": clase
                })
        except Exception as e:
            log.error(f"Error consultando GitHub: {e}")
    return render_template_string(PLANTILLA, runs=runs)

if __name__ == "__main__":
    if not REPO or not GH_TOKEN:
        print("Aviso: definir MERVOX_REPO y GH_TOKEN antes de correr el panel.")
    app.run(host="0.0.0.0", port=8098)
