"""
Script de PRUEBA v5 (con log a archivo) — sigue sin tocar story_engine-5_1.py.

Igual que la v5 anterior: prueba un montón de combinaciones de URL
para dar con la forma correcta de la categoría "spooky-paranormal"
en la API interna de Mumsnet. La diferencia es que ADEMÁS de
imprimir todo en pantalla, guarda una copia completa en un archivo
de texto (resultado_api_mumsnet.txt) en la misma carpeta, para que
sea más fácil compartirlo (subir el archivo en vez de tipear/sacar
captura de la terminal).

Uso: python probar_api_mumsnet_v5.py
El archivo queda en: ~/resultado_api_mumsnet.txt
"""
import json
import requests

ARCHIVO_LOG = "resultado_api_mumsnet.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

BASE = "https://www.mumsnet.com/api/v3"

candidatos = []

slugs_spooky = ["spooky-paranormal", "spooky_paranormal", "spooky", "paranormal"]
familias = ["subjects", "categories"]

for familia in familias:
    for slug in slugs_spooky:
        candidatos.append((
            f"{familia}/{slug}/threads",
            f"{BASE}/discover/{familia}/{slug}/threads",
        ))
    for slug in slugs_spooky:
        candidatos.append((
            f"{familia}/{slug} (sin /threads)",
            f"{BASE}/discover/{familia}/{slug}",
        ))

candidatos += [
    ("discover (base)", f"{BASE}/discover"),
    ("discover/subjects (índice)", f"{BASE}/discover/subjects"),
    ("discover/categories (índice)", f"{BASE}/discover/categories"),
    ("talk/topics (índice)", f"{BASE}/talk/topics"),
    ("feeds/trending", f"{BASE}/feeds/trending"),
]

candidatos.append((
    "CONTROL: AIBU por ID 2724 (ya confirmado que funciona)",
    f"{BASE}/talk/topics/2724/threads",
))


def probar(nombre, url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        es_json = False
        preview = ""
        tiene_datos = False
        try:
            data = resp.json()
            es_json = True
            texto = json.dumps(data, ensure_ascii=False)
            preview = texto[:300]
            if isinstance(data, dict) and data.get("data"):
                tiene_datos = True
            elif isinstance(data, list) and len(data) > 0:
                tiene_datos = True
            elif isinstance(data, dict) and len(data) > 1:
                tiene_datos = True
        except ValueError:
            preview = resp.text[:150]
        return {
            "nombre": nombre,
            "url": url,
            "status": resp.status_code,
            "es_json": es_json,
            "tiene_datos": tiene_datos,
            "preview": preview,
        }
    except requests.exceptions.RequestException as e:
        return {
            "nombre": nombre,
            "url": url,
            "status": None,
            "es_json": False,
            "tiene_datos": False,
            "preview": f"ERROR DE CONEXIÓN: {e}",
        }


def escribir(lineas_log, texto):
    """Imprime en pantalla Y guarda la línea en la lista para el archivo."""
    print(texto)
    lineas_log.append(texto)


if __name__ == "__main__":
    lineas_log = []
    resultados = []

    escribir(lineas_log, f"Probando {len(candidatos)} combinaciones...\n")

    for nombre, url in candidatos:
        r = probar(nombre, url)
        resultados.append(r)
        marca = "OK" if r["status"] == 200 else str(r["status"])
        escribir(lineas_log, f"[{marca:>5}] {nombre}  ->  {url}")

    escribir(lineas_log, "\n" + "=" * 70)
    escribir(lineas_log, "RESUMEN — solo las que dieron status 200:")
    escribir(lineas_log, "=" * 70)

    exitosas = [r for r in resultados if r["status"] == 200]
    if not exitosas:
        escribir(lineas_log, "Ninguna dio 200.")
    for r in exitosas:
        escribir(lineas_log, f"\n>>> {r['nombre']}")
        escribir(lineas_log, f"    URL: {r['url']}")
        escribir(lineas_log, f"    ¿Tiene datos reales?: {'SI' if r['tiene_datos'] else 'no (vacío o estructura rara)'}")
        escribir(lineas_log, f"    Preview: {r['preview']}")

    # Detalle completo (JSON entero) de cada endpoint que dio 200,
    # al final del archivo, para no perder nada.
    escribir(lineas_log, "\n" + "=" * 70)
    escribir(lineas_log, "DETALLE COMPLETO de cada respuesta 200 (JSON entero):")
    escribir(lineas_log, "=" * 70)
    for r in exitosas:
        escribir(lineas_log, f"\n----- {r['nombre']} -----")
        escribir(lineas_log, f"URL: {r['url']}")
        try:
            resp = requests.get(r["url"], headers=HEADERS, timeout=12)
            data = resp.json()
            escribir(lineas_log, json.dumps(data, indent=2, ensure_ascii=False)[:5000])
        except Exception as e:
            escribir(lineas_log, f"(no se pudo re-consultar para el detalle: {e})")

    with open(ARCHIVO_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_log))

    print("\n" + "=" * 70)
    print(f"Listo. Todo quedó guardado en: {ARCHIVO_LOG}")
    print("Subilo acá (como archivo, no como captura) para que lo revise.")
    print("=" * 70)
