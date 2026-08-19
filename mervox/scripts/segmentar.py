"""
segmentar.py - v1.0
Transcribe el video grabado con faster-whisper (timestamps por palabra)
y le pide a Gemini que elija los mejores momentos para clips de 60-62s,
cortando en pausas naturales. Guarda transcripcion.json y momentos.json.
"""
import os
import sys
import json
import glob
import logging
import google.generativeai as genai
from faster_whisper import WhisperModel

logging.basicConfig(
    filename="mervox.log",
    level=logging.INFO,
    format="%(asctime)s [segmentar] %(levelname)s: %(message)s"
)
log = logging.getLogger("segmentar")

def encontrar_video(carpeta="grabacion"):
    candidatos = glob.glob(os.path.join(carpeta, "*.mp4")) + glob.glob(os.path.join(carpeta, "*.flv"))
    if not candidatos:
        log.error(f"No se encontro ningun video en {carpeta}")
        raise FileNotFoundError(f"No hay video en {carpeta}")
    candidatos.sort(key=os.path.getmtime, reverse=True)
    return candidatos[0]

def transcribir(video_path, modelo="small"):
    log.info(f"Transcribiendo {video_path} con modelo {modelo}")
    model = WhisperModel(modelo, device="cpu", compute_type="int8")
    segments, info = model.transcribe(video_path, word_timestamps=True, vad_filter=True)

    palabras = []
    texto_completo = []
    for seg in segments:
        texto_completo.append(seg.text.strip())
        if seg.words:
            for w in seg.words:
                palabras.append({"palabra": w.word.strip(), "inicio": round(w.start, 2), "fin": round(w.end, 2)})

    transcripcion = {
        "idioma_detectado": info.language,
        "texto": " ".join(texto_completo),
        "palabras": palabras
    }
    with open("transcripcion.json", "w", encoding="utf-8") as f:
        json.dump(transcripcion, f, ensure_ascii=False, indent=2)
    log.info(f"Transcripcion guardada: {len(palabras)} palabras")
    return transcripcion

def pedir_momentos_a_gemini(transcripcion):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.error("Falta GEMINI_API_KEY")
        raise RuntimeError("Falta GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    duracion_total = transcripcion["palabras"][-1]["fin"] if transcripcion["palabras"] else 0
    prompt = f"""Sos un editor de clips virales para TikTok/Reels/Shorts.
Te paso la transcripcion completa de un live (duracion total: {duracion_total:.0f} segundos).
Elegi entre 3 y 8 momentos que funcionen como clips independientes.
Reglas estrictas:
- Cada clip debe durar entre 60 y 62 segundos.
- El inicio y el fin de cada clip deben caer en una pausa natural del habla (no cortar una palabra o idea a la mitad).
- No repitas ni superpongas rangos de tiempo.
- Priorizar momentos con carga emocional, humor, revelaciones o picos de interes.

Transcripcion:
{transcripcion['texto']}

Devolveme SOLO un JSON (sin markdown, sin texto extra) con este formato exacto:
[{{"inicio": 123.4, "fin": 184.9, "titulo": "titulo corto y llamativo"}}]
"""
    log.info("Pidiendo momentos a Gemini")
    resp = model.generate_content(prompt)
    texto = resp.text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
    momentos = json.loads(texto)
    log.info(f"Gemini devolvio {len(momentos)} momentos")
    return momentos

def main():
    video = encontrar_video()
    transcripcion = transcribir(video)
    if not transcripcion["palabras"]:
        log.error("Transcripcion vacia, no se puede continuar")
        sys.exit(1)
    momentos = pedir_momentos_a_gemini(transcripcion)
    with open("momentos.json", "w", encoding="utf-8") as f:
        json.dump({"video": video, "momentos": momentos}, f, ensure_ascii=False, indent=2)
    log.info(f"momentos.json guardado con {len(momentos)} clips")
    print(f"OK: {len(momentos)} momentos detectados")

if __name__ == "__main__":
    main()
