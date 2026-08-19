"""
mervox v1.1 - segmentar.py
Transcribe el video grabado con faster-whisper y usa Gemini para detectar
los mejores momentos (ganchos narrativos), forzando clips de 60 a 62 segundos
que empiezan y terminan en pausas naturales.

Cambios v1.1:
- Reintentos con backoff ante fallos de Gemini (rate limit / error transitorio)
- Modelo de respaldo si el principal falla luego de agotar reintentos
- Prompt mas estricto: puntaje de viralidad, razon, maximo de clips, gancho en primeros 3s
- Validacion de clips devueltos (duracion real, limites del video, sin solapamiento)
- Transcripcion guardada en archivo aparte para no perder el trabajo de Whisper si Gemini falla
- Timeout explicito en la llamada a Gemini
"""

import argparse
import glob
import json
import logging
import os
import subprocess
import sys
import time

from faster_whisper import WhisperModel
import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [segmentar] %(levelname)s: %(message)s",
)
log = logging.getLogger("segmentar")

DURACION_MIN = 60
DURACION_MAX = 62
MAX_CLIPS = 5
PUNTAJE_MINIMO = 7
MODELO_PRINCIPAL = "gemini-2.5-flash"
MODELO_RESPALDO = "gemini-2.5-flash-lite"
MAX_REINTENTOS = 3
ESPERA_BASE_SEGUNDOS = 10
TIMEOUT_SEGUNDOS = 120

PROMPT_SISTEMA = """Sos un editor experto en encontrar los mejores momentos de un video para \
convertirlos en clips virales verticales. Te paso una transcripcion con timestamps.

Reglas estrictas:
- Cada clip debe durar entre {dmin} y {dmax} segundos exactos.
- Debe empezar y terminar en una pausa natural del habla (fin de oracion), nunca a mitad de frase.
- El gancho debe estar en los primeros 3 segundos del clip, no despues.
- Descarta saludos, presentaciones, silencios, o contenido repetido.
- Maximo {max_clips} clips por video: elegi SOLO los mejores, no completes el numero si no hay \
suficiente calidad.
- Para cada clip asigna un puntaje de viralidad del 1 al 10. Solo incluí clips con puntaje \
{puntaje_min} o mas.
- Justifica en una frase corta por que ese momento funciona.
- Prioriza: ganchos narrativos, preguntas polemicas, momentos emocionales, revelaciones, \
frases citables, humor.
- Devolve SOLO un JSON valido, sin texto adicional, con esta forma exacta:

{{"clips": [{{"inicio": 123.4, "fin": 185.6, "titulo": "string corto", "gancho": "frase de apertura", \
"puntaje": 8, "razon": "string corto"}}]}}

Transcripcion:
{transcripcion}
"""


def obtener_duracion_video(ruta_video: str) -> float:
    try:
        resultado = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", ruta_video,
            ],
            capture_output=True, text=True, timeout=30, check=True,
        )
        return float(resultado.stdout.strip())
    except Exception as e:
        log.warning("No se pudo obtener duracion del video con ffprobe: %s", e)
        return None


def transcribir(ruta_video: str, ruta_transcripcion: str):
    log.info("Transcribiendo %s con faster-whisper...", ruta_video)
    modelo = WhisperModel("base", device="cpu", compute_type="int8")
    segmentos, _ = modelo.transcribe(ruta_video, word_timestamps=True)

    lineas = []
    for seg in segmentos:
        lineas.append(f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text.strip()}")
    transcripcion = "\n".join(lineas)

    try:
        with open(ruta_transcripcion, "w", encoding="utf-8") as f:
            f.write(transcripcion)
        log.info("Transcripcion guardada en %s", ruta_transcripcion)
    except Exception as e:
        log.warning("No se pudo guardar la transcripcion en disco: %s", e)

    return transcripcion


def _llamar_gemini(nombre_modelo: str, prompt: str):
    modelo = genai.GenerativeModel(nombre_modelo)
    respuesta = modelo.generate_content(
        prompt,
        request_options={"timeout": TIMEOUT_SEGUNDOS},
    )
    texto = respuesta.text.strip()

    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.startswith("json"):
            texto = texto[4:]

    return json.loads(texto)


def pedir_momentos_a_gemini(transcripcion: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.error("Falta GEMINI_API_KEY en el entorno.")
        sys.exit(1)

    genai.configure(api_key=api_key)

    prompt = PROMPT_SISTEMA.format(
        dmin=DURACION_MIN,
        dmax=DURACION_MAX,
        max_clips=MAX_CLIPS,
        puntaje_min=PUNTAJE_MINIMO,
        transcripcion=transcripcion,
    )

    modelos_a_probar = [MODELO_PRINCIPAL, MODELO_RESPALDO]
    ultimo_error = None

    for nombre_modelo in modelos_a_probar:
        for intento in range(1, MAX_REINTENTOS + 1):
            try:
                log.info(
                    "Pidiendo a Gemini (%s) los mejores momentos [intento %d/%d]...",
                    nombre_modelo, intento, MAX_REINTENTOS,
                )
                data = _llamar_gemini(nombre_modelo, prompt)
                return data.get("clips", [])
            except json.JSONDecodeError as e:
                ultimo_error = e
                log.warning("Gemini (%s) no devolvio JSON valido: %s", nombre_modelo, e)
            except Exception as e:
                ultimo_error = e
                log.warning(
                    "Fallo llamada a Gemini (%s) intento %d/%d: %s",
                    nombre_modelo, intento, MAX_REINTENTOS, e,
                )

            if intento < MAX_REINTENTOS:
                espera = ESPERA_BASE_SEGUNDOS * (2 ** (intento - 1))
                log.info("Esperando %ds antes de reintentar...", espera)
                time.sleep(espera)

        log.warning("Modelo %s agoto reintentos, probando siguiente modelo si hay.", nombre_modelo)

    log.error("Gemini fallo en todos los modelos y reintentos. Ultimo error: %s", ultimo_error)
    sys.exit(1)


def validar_clips(clips: list, duracion_video: float) -> list:
    validos = []
    ocupados = []

    for i, clip in enumerate(clips):
        inicio = clip.get("inicio")
        fin = clip.get("fin")
        puntaje = clip.get("puntaje", 0)

        if inicio is None or fin is None:
            log.warning("Clip %d descartado: falta inicio/fin.", i)
            continue

        duracion = fin - inicio
        if not (DURACION_MIN - 1 <= duracion <= DURACION_MAX + 1):
            log.warning(
                "Clip %d descartado: duracion %.1fs fuera de rango (%d-%d).",
                i, duracion, DURACION_MIN, DURACION_MAX,
            )
            continue

        if inicio < 0 or (duracion_video is not None and fin > duracion_video):
            log.warning(
                "Clip %d descartado: fuera de los limites del video (0-%.1fs).",
                i, duracion_video if duracion_video else -1,
            )
            continue

        if puntaje < PUNTAJE_MINIMO:
            log.warning("Clip %d descartado: puntaje %s menor al minimo (%d).", i, puntaje, PUNTAJE_MINIMO)
            continue

        solapado = any(not (fin <= o_inicio or inicio >= o_fin) for o_inicio, o_fin in ocupados)
        if solapado:
            log.warning("Clip %d descartado: se solapa con otro clip ya elegido.", i)
            continue

        ocupados.append((inicio, fin))
        validos.append(clip)

    return validos[:MAX_CLIPS]


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

    duracion_video = obtener_duracion_video(ruta_video)
    ruta_transcripcion = os.path.splitext(args.output)[0] + "_transcripcion.txt"

    transcripcion = transcribir(ruta_video, ruta_transcripcion)
    clips_crudos = pedir_momentos_a_gemini(transcripcion)
    log.info("Momentos devueltos por Gemini: %d", len(clips_crudos))

    clips = validar_clips(clips_crudos, duracion_video)
    log.info("Clips validos tras filtrado: %d", len(clips))

    resultado = {"video_fuente": ruta_video, "clips": clips}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    log.info("Guardado en %s", args.output)


if __name__ == "__main__":
    main()
