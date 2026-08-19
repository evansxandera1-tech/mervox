"""
mervox v1.0 - segmentar.py
Transcribe el video grabado con faster-whisper y usa Gemini para detectar
los mejores momentos (ganchos narrativos), forzando clips de 60 a 62 segundos
que empiezan y terminan en pausas naturales.
"""

import argparse
import glob
import json
import logging
import os
import sys

from faster_whisper import WhisperModel
import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [segmentar] %(levelname)s: %(message)s",
)
log = logging.getLogger("segmentar")

DURACION_MIN = 60
DURACION_MAX = 62

PROMPT_SISTEMA = """Sos un editor experto en encontrar los mejores momentos de un video para \
convertirlos en clips virales verticales. Te paso una transcripcion con timestamps.

Reglas estrictas:
- Cada clip debe durar entre {dmin} y {dmax} segundos exactos.
- Debe empezar y terminar en una pausa natural del habla (fin de oracion), nunca a mitad de frase.
- Prioriza: ganchos narrativos, preguntas polemicas, momentos emocionales, revelaciones, \
frases citables, humor.
- Devolve SOLO un JSON valido, sin texto adicional, con esta forma exacta:

{{"clips": [{{"inicio": 123.4, "fin": 185.6, "titulo": "string corto", "gancho": "frase de apertura"}}]}}

Transcripcion:
{transcripcion}
"""


def transcribir(ruta_video: str):
    log.info("Transcribiendo %s con faster-whisper...", ruta_video)
    modelo = WhisperModel("base", device="cpu", compute_type="int8")
    segmentos, _ = modelo.transcribe(ruta_video, word_timestamps=True)

    lineas = []
    for seg in segmentos:
        lineas.append(f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text.strip()}")
    return "\n".join(lineas)


def pedir_momentos_a_gemini(transcripcion: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.error("Falta GEMINI_API_KEY en el entorno.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel("gemini-2.5-flash")

    prompt = PROMPT_SISTEMA.format(
        dmin=DURACION_MIN, dmax=DURACION_MAX, transcripcion=transcripcion
    )

    log.info("Pidiendo a Gemini los mejores momentos...")
    respuesta = modelo.generate_content(prompt)
    texto = respuesta.text.strip()

    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.startswith("json"):
            texto = texto[4:]

    try:
        data = json.loads(texto)
    except json.JSONDecodeError:
        log.error("Gemini no devolvio JSON valido: %s", texto[:500])
        sys.exit(1)

    return data.get("clips", [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="Carpeta con el video grabado")
    parser.add_argument("--output", required=True, help="Archivo JSON de salida")
    args = parser.parse_args()

    candidatos = glob.glob(os.path.join(args.input_dir, "**", "*.mp4"), recursive=True)
    if not candidatos:
        log.error("No se encontro ningun .mp4 en %s", args.input_dir)
        sys.exit(1)

    ruta_video = max(candidatos, key=os.path.getsize)
    log.info("Video fuente: %s", ruta_video)

    transcripcion = transcribir(ruta_video)
    clips = pedir_momentos_a_gemini(transcripcion)

    log.info("Momentos detectados: %d", len(clips))

    resultado = {"video_fuente": ruta_video, "clips": clips}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    log.info("Guardado en %s", args.output)


if __name__ == "__main__":
    main()
