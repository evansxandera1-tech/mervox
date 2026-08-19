"""
Script de PRUEBA v7 — confirmación final. Sigue sin tocar story_engine-5_1.py.

Encontramos en el listado completo de topics:
  - "The paranormal" (id 16506, slug the_unexplained) -> esto sería
    nuestro "Creepy Threads / Creepy Encounters"
  - "True crime and unsolved mysteries" (id 16646) -> bonus, temática
    parecida, no la pediste pero puede servir a futuro

Confirmamos "AIO" NO existe como topic de Mumsnet (ya buscado en las
7290 entradas, cero resultados) — coincide con lo que ya sabíamos.

Este script prueba ambos IDs con el mismo patrón que ya confirmamos
que funciona para AIBU (/api/v3/talk/topics/{id}/threads), y muestra
cuántas palabras tiene cada historia encontrada (para ver si entran
en el filtro PALABRAS_MIN_HISTORIA=800 que ya usa el script real).
"""
import json
import re
import requests

ARCHIVO_LOG = "resultado_confirmacion_final.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

BASE = "https://www.mumsnet.com/api/v3"

TOPICS_A_PROBAR = [
    ("The paranormal (Creepy Threads)", 16506),
    ("True crime and unsolved mysteries (bonus)", 16646),
]


def escribir(lineas_log, texto):
    print(texto)
    lineas_log.append(texto)


def contar_palabras(html_body):
    texto = re.sub(r"<[^>]+>", " ", html_body or "")
    return len(texto.split())


if __name__ == "__main__":
    lineas_log = []

    for nombre, topic_id in TOPICS_A_PROBAR:
        url = f"{BASE}/talk/topics/{topic_id}/threads"
        escribir(lineas_log, f"\n{'=' * 70}")
        escribir(lineas_log, f"TOPIC: {nombre} (id {topic_id})")
        escribir(lineas_log, f"URL: {url}")
        escribir(lineas_log, "=" * 70)

        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
        except requests.exceptions.RequestException as e:
            escribir(lineas_log, f"ERROR DE CONEXIÓN: {e}")
            continue

        escribir(lineas_log, f"Status: {resp.status_code}")

        if resp.status_code != 200:
            escribir(lineas_log, f"No dio 200. Cuerpo: {resp.text[:300]}")
            continue

        try:
            data = resp.json()
        except ValueError:
            escribir(lineas_log, "No vino JSON válido.")
            continue

        hilos = data.get("data", [])
        escribir(lineas_log, f"Hilos recibidos: {len(hilos)}")

        for h in hilos[:10]:
            subject = h.get("subject", "(sin título)")
            body = h.get("body", "")
            palabras = contar_palabras(body)
            replies = h.get("replies_count", 0)
            escribir(lineas_log, f"\n  - \"{subject}\"")
            escribir(lineas_log, f"    palabras en el cuerpo: {palabras}  |  respuestas: {replies}")

    with open(ARCHIVO_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_log))

    print(f"\n\nListo. Guardado en: {ARCHIVO_LOG}")
    print("Copialo a Download y subilo:")
    print(f"  cp ~/{ARCHIVO_LOG} /sdcard/Download/")
