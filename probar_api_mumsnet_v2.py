"""
Script de PRUEBA v2 — sigue sin tocar story_engine-5_1.py.

Descubrimos que la página real de AIBU trae escondido en su HTML un
"meta-topic-id: 2724" — o sea que la API probablemente espera el ID
numérico interno de cada topic, no el nombre que se ve en la URL
(am_i_being_unreasonable). Probamos varias combinaciones para dar con
la que responda con datos reales.
"""
import json
import requests

# Cada tupla es: (nombre para mostrar, URL a probar)
ENDPOINTS = [
    ("AIBU por ID numérico (2724)",
     "https://www.mumsnet.com/api/v3/talk/topics/2724/threads"),

    ("AIBU por slug (por si acaso)",
     "https://www.mumsnet.com/api/v3/talk/topics/am_i_being_unreasonable/threads"),

    ("Discover spooky-paranormal por slug",
     "https://www.mumsnet.com/api/v3/discover/subjects/spooky-paranormal/threads"),

    ("AIBU con page=1 (por si pide paginado)",
     "https://www.mumsnet.com/api/v3/talk/topics/2724/threads?page=1"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}


def probar(nombre, url):
    print(f"\n{'=' * 70}")
    print(f"PROBANDO: {nombre}")
    print(f"URL: {url}")
    print("=" * 70)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            texto = json.dumps(data, indent=2, ensure_ascii=False)
            print("Respuesta (primeros 2000 caracteres):")
            print(texto[:2000])
            if len(texto) > 2000:
                print(f"... (respuesta completa: {len(texto)} caracteres)")
        except ValueError:
            print("No es JSON. Primeros 300 caracteres crudos:")
            print(resp.text[:300])
    except requests.exceptions.RequestException as e:
        print(f"FALLÓ LA CONEXIÓN: {e}")


if __name__ == "__main__":
    for nombre, url in ENDPOINTS:
        probar(nombre, url)

    print("\n" + "=" * 70)
    print("LISTO. Pegame toda esta salida. Si alguna da status 200 con")
    print("datos reales, con eso armo la integración final.")
    print("=" * 70)
