"""
Script de PRUEBA aislado — no toca story_engine-5_1.py para nada.
Solo sirve para confirmar si la API interna de Mumsnet (la que
robots.txt permite a Googlebot) responde con JSON real cuando la
llamamos nosotros, y con qué forma exacta viene ese JSON.

Cómo usarlo en Termux:
    pip install requests
    python probar_api_mumsnet.py

Va a probar 3 endpoints (AIBU, Discover "spooky-paranormal", y
categorías) con dos User-Agent distintos cada uno: uno normal de
navegador, y uno que se identifica como Googlebot (ya que
robots.txt solo abre la puerta explícitamente para ese caso).
"""
import json
import requests

ENDPOINTS = {
    "AIBU (talk/topics)": "https://www.mumsnet.com/api/v3/talk/topics/am_i_being_unreasonable/threads",
    "Discover - spooky/paranormal": "https://www.mumsnet.com/api/v3/discover/subjects/spooky-paranormal/threads",
}

USER_AGENTS = {
    "navegador normal": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Googlebot": (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    ),
}


def probar(nombre_endpoint, url):
    print(f"\n{'=' * 70}")
    print(f"ENDPOINT: {nombre_endpoint}")
    print(f"URL: {url}")
    print("=" * 70)

    for nombre_ua, ua in USER_AGENTS.items():
        print(f"\n--- Probando con User-Agent: {nombre_ua} ---")
        headers = {
            "User-Agent": ua,
            "Accept": "application/json",
            "Accept-Language": "en-GB,en;q=0.9",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"Status: {resp.status_code}")
            print(f"Content-Type: {resp.headers.get('Content-Type', '(no viene)')}")

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    texto = json.dumps(data, indent=2, ensure_ascii=False)
                    print("¡Es JSON! Primeros 1500 caracteres de la respuesta:")
                    print(texto[:1500])
                    if len(texto) > 1500:
                        print(f"... (respuesta completa: {len(texto)} caracteres)")
                except ValueError:
                    print("No es JSON válido. Primeros 500 caracteres crudos:")
                    print(resp.text[:500])
            else:
                print("Primeros 500 caracteres de la respuesta (probablemente error):")
                print(resp.text[:500])

        except requests.exceptions.RequestException as e:
            print(f"FALLÓ LA CONEXIÓN: {e}")


if __name__ == "__main__":
    print("Probando la API interna de Mumsnet...\n")
    for nombre, url in ENDPOINTS.items():
        probar(nombre, url)

    print("\n" + "=" * 70)
    print("LISTO. Copiame toda la salida de arriba (o la parte que diga")
    print("'¡Es JSON!' con su contenido) y con eso armo la integración real")
    print("en story_engine-5_1.py, con los nombres de campo correctos.")
    print("=" * 70)
