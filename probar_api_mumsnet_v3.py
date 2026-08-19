"""
Script de PRUEBA v3 — sigue sin tocar story_engine-5_1.py.

Ya confirmamos que AIBU funciona con /api/v3/talk/topics/2724/threads
(200 OK, JSON con historias completas). Ahora necesitamos el ID
numérico de la categoría "spooky-paranormal" (Discover), porque el
slug solo no funcionó (404).

Este script:
1) Prueba /api/v3/discover/subjects (sin ID) y /api/v3/discover/categories
   (sin ID), por si devuelven el listado completo con IDs.
2) Descarga el HTML crudo de la página real
   mumsnet.com/discover/spooky-paranormal y busca ahí cualquier
   número que esté pegado a la palabra "subject" o "category" o al
   slug "spooky-paranormal", que es como encontramos el 2724 de AIBU.
"""
import json
import re
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

HEADERS_HTML = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html",
    "Accept-Language": "en-GB,en;q=0.9",
}


def probar_json(nombre, url):
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
            print("Respuesta (primeros 3000 caracteres):")
            print(texto[:3000])
        except ValueError:
            print("No es JSON. Primeros 300 caracteres:")
            print(resp.text[:300])
    except requests.exceptions.RequestException as e:
        print(f"FALLÓ: {e}")


def buscar_id_en_html():
    print(f"\n{'=' * 70}")
    print("BUSCANDO ID NUMÉRICO EN EL HTML DE discover/spooky-paranormal")
    print("=" * 70)
    url = "https://www.mumsnet.com/discover/spooky-paranormal"
    try:
        resp = requests.get(url, headers=HEADERS_HTML, timeout=15)
        html = resp.text
        print(f"Status: {resp.status_code} — HTML de {len(html)} caracteres descargado.")

        # Busca cosas tipo "subject":{"id":1234  o  subject-id="1234"  o
        # cualquier bloque JSON que tenga "spooky-paranormal" cerca de un id.
        patrones = [
            r'"slug"\s*:\s*"spooky-paranormal"[^}]{0,200}',
            r'spooky-paranormal[^"]{0,10}"[^}]{0,300}"id"\s*:\s*(\d+)',
            r'"id"\s*:\s*(\d+)[^}]{0,300}"slug"\s*:\s*"spooky-paranormal"',
            r'subject[_-]?id["\']?\s*[:=]\s*["\']?(\d+)',
        ]
        encontro_algo = False
        for pat in patrones:
            matches = re.findall(pat, html, re.IGNORECASE)
            if matches:
                encontro_algo = True
                print(f"\nPatrón {pat!r} encontró:")
                for m in matches[:5]:
                    print(f"  -> {m}")

        if not encontro_algo:
            print("\nNo se encontró ningún ID pegado al slug en el HTML.")
            print("Buscando cualquier '__NEXT_DATA__' o bloque JSON grande como pista...")
            idx = html.find("__NEXT_DATA__")
            if idx != -1:
                fragmento = html[idx:idx + 500]
                print(f"Encontré __NEXT_DATA__, fragmento:\n{fragmento}")
            else:
                print("Tampoco hay __NEXT_DATA__. No hay pista fácil en el HTML.")

    except requests.exceptions.RequestException as e:
        print(f"FALLÓ: {e}")


if __name__ == "__main__":
    probar_json("Discover subjects (listado, sin ID)",
                "https://www.mumsnet.com/api/v3/discover/subjects")
    probar_json("Discover categories (listado, sin ID)",
                "https://www.mumsnet.com/api/v3/discover/categories")

    buscar_id_en_html()

    print("\n" + "=" * 70)
    print("LISTO. Pegame toda esta salida.")
    print("=" * 70)
