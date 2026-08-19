"""
Script de PRUEBA v6 — sigue sin tocar story_engine-5_1.py.

Ya confirmamos que /api/v3/talk/topics devuelve el LISTADO COMPLETO
de topics de Mumsnet (con su id y slug cada uno) — esto es mejor
noticia todavía de lo esperado: ni siquiera hace falta la ruta de
Discover, capaz "Creepy Threads" existe directamente como un TOPIC
de Talk (como AIBU), solo que no lo habíamos visto en la home.

Este script:
1) Pagina /api/v3/talk/topics hasta traer TODOS los topics (puede
   haber cientos).
2) Filtra y muestra solo los que su nombre o slug contengan alguna
   palabra relacionada a espeluznante/paranormal/misterio.
3) Guarda todo en un archivo de log, como la vez pasada.
"""
import json
import requests

ARCHIVO_LOG = "resultado_topics_mumsnet.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

BASE = "https://www.mumsnet.com/api/v3"

PALABRAS_CLAVE = [
    "spooky", "paranormal", "creepy", "unexplained", "ghost", "haunt",
    "scary", "mystery", "woo", "supernatural",
]


def escribir(lineas_log, texto):
    print(texto)
    lineas_log.append(texto)


def traer_todos_los_topics(lineas_log):
    """Pagina el índice de topics hasta agotarlo. Devuelve la lista completa."""
    todos = []
    pagina = 1
    while True:
        url = f"{BASE}/talk/topics?page={pagina}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
        except requests.exceptions.RequestException as e:
            escribir(lineas_log, f"Página {pagina}: ERROR DE CONEXIÓN: {e}")
            break

        if resp.status_code != 200:
            escribir(lineas_log, f"Página {pagina}: status {resp.status_code} — freno acá.")
            break

        try:
            data = resp.json()
        except ValueError:
            escribir(lineas_log, f"Página {pagina}: no vino JSON válido — freno acá.")
            break

        lote = data.get("data", [])
        escribir(lineas_log, f"Página {pagina}: {len(lote)} topics recibidos.")

        if not lote:
            break

        todos.extend(lote)
        pagina += 1

        if pagina > 30:  # tope de seguridad, no debería hacer falta
            escribir(lineas_log, "Freno de seguridad: más de 30 páginas, corto igual.")
            break

    return todos


if __name__ == "__main__":
    lineas_log = []

    escribir(lineas_log, "Trayendo TODOS los topics de Mumsnet (con paginación)...\n")
    todos = traer_todos_los_topics(lineas_log)
    escribir(lineas_log, f"\nTOTAL de topics traídos: {len(todos)}\n")

    escribir(lineas_log, "=" * 70)
    escribir(lineas_log, "TOPICS QUE MATCHEAN PALABRAS CLAVE ESPELUZNANTE/PARANORMAL:")
    escribir(lineas_log, "=" * 70)

    encontrados = []
    for t in todos:
        nombre = (t.get("name") or "").lower()
        slug = (t.get("slug") or "").lower()
        for palabra in PALABRAS_CLAVE:
            if palabra in nombre or palabra in slug:
                encontrados.append(t)
                break

    if not encontrados:
        escribir(lineas_log, "Ninguno matcheó. Puede que esté bajo otro nombre.")
    else:
        for t in encontrados:
            escribir(lineas_log, f"\n  id: {t.get('id')}")
            escribir(lineas_log, f"  name: {t.get('name')}")
            escribir(lineas_log, f"  slug: {t.get('slug')}")
            escribir(lineas_log, f"  link: {t.get('link')}")
            escribir(lineas_log, f"  can_view_threads: {t.get('can_view_threads')}")

    # Guardamos también el listado COMPLETO de nombres+slugs+ids (sin
    # todos los demás campos) por si el filtro de palabras no encontró
    # nada y hay que revisar a mano cómo se llama la sección.
    escribir(lineas_log, "\n" + "=" * 70)
    escribir(lineas_log, "LISTADO COMPLETO (solo id / name / slug) — por si el filtro falló:")
    escribir(lineas_log, "=" * 70)
    for t in todos:
        escribir(lineas_log, f"  {t.get('id')}\t{t.get('name')}\t{t.get('slug')}")

    with open(ARCHIVO_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_log))

    print(f"\nListo. Guardado en: {ARCHIVO_LOG}")
    print("Copialo a Download y subilo acá:")
    print(f"  cp ~/{ARCHIVO_LOG} /sdcard/Download/")
