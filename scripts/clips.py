"""
mervox v1.0 - clips.py
Corta cada momento detectado, recorta a vertical 9:16 con seguimiento de rostro,
quema subtitulos estilo karaoke y aplica vineta suave.
"""

import argparse
import json
import logging
import os
import subprocess

import cv2
from faster_whisper import WhisperModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [clips] %(levelname)s: %(message)s",
)
log = logging.getLogger("clips")

ANCHO_SALIDA = 1080
ALTO_SALIDA = 1920


def detectar_centro_rostro(ruta_video: str, inicio: float, fin: float) -> float:
    cap = cv2.VideoCapture(ruta_video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_medio = int(((inicio + fin) / 2) * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_medio)
    ok, frame = cap.read()
    cap.release()

    if not ok:
        return 0.5

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clasificador = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    rostros = clasificador.detectMultiScale(gris, 1.1, 5)

    if len(rostros) == 0:
        return 0.5

    x, y, w, h = max(rostros, key=lambda r: r[2] * r[3])
    ancho_frame = frame.shape[1]
    centro_x = (x + w / 2) / ancho_frame
    return centro_x


def cortar_y_verticalizar(ruta_video, inicio, fin, centro_x, salida_tmp):
    duracion = fin - inicio
    filtro = (
        f"crop=ih*9/16:ih:(iw-ih*9/16)*{centro_x}:0,"
        f"scale={ANCHO_SALIDA}:{ALTO_SALIDA},"
        f"vignette=PI/5"
    )
    cmd = [
        "ffmpeg", "-y", "-ss", str(inicio), "-i", ruta_video,
        "-t", str(duracion), "-vf", filtro,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        salida_tmp,
    ]
    subprocess.run(cmd, check=True)


def generar_ass(ruta_video, inicio, fin, ruta_ass):
    modelo = WhisperModel("base", device="cpu", compute_type="int8")
    segmentos, _ = modelo.transcribe(
        ruta_video, word_timestamps=True, clip_timestamps=[inicio, fin]
    )

    encabezado = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginV
Style: Default,Montserrat ExtraBold,72,&H00FFFFFF,&H0000A5FF,&H00000000,&H00000000,1,3,0,2,180

[Events]
Format: Layer, Start, End, Style, Text
"""

    def t(seg):
        h = int(seg // 3600)
        m = int((seg % 3600) // 60)
        s = seg % 60
        return f"{h:01d}:{m:02d}:{s:05.2f}"

    eventos = []
    for seg in segmentos:
        for palabra in seg.words or []:
            ini_rel = max(0, palabra.start - inicio)
            fin_rel = max(0, palabra.end - inicio)
            texto = palabra.word.strip().upper()
            eventos.append(
                f"Dialogue: 0,{t(ini_rel)},{t(fin_rel)},Default,{{\\c&H0000A5FF&}}{texto}{{\\c&HFFFFFF&}}"
            )

    with open(ruta_ass, "w", encoding="utf-8") as f:
        f.write(encabezado)
        f.write("\n".join(eventos))


def quemar_subtitulos(ruta_video_tmp, ruta_ass, salida_final):
    cmd = [
        "ffmpeg", "-y", "-i", ruta_video_tmp,
        "-vf", f"ass={ruta_ass}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        salida_final,
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--momentos", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.momentos, "r", encoding="utf-8") as f:
        data = json.load(f)

    ruta_video = data["video_fuente"]
    clips = data["clips"]

    for i, clip in enumerate(clips, start=1):
        inicio = float(clip["inicio"])
        fin = float(clip["fin"])
        titulo = clip.get("titulo", f"clip_{i}")
        log.info("Procesando clip %d/%d: %s (%.1fs -> %.1fs)", i, len(clips), titulo, inicio, fin)

        tmp_vertical = os.path.join(args.output_dir, f"tmp_{i}.mp4")
        ruta_ass = os.path.join(args.output_dir, f"sub_{i}.ass")
        salida_final = os.path.join(args.output_dir, f"clip_{i:02d}.mp4")

        centro_x = detectar_centro_rostro(ruta_video, inicio, fin)
        cortar_y_verticalizar(ruta_video, inicio, fin, centro_x, tmp_vertical)
        generar_ass(ruta_video, inicio, fin, ruta_ass)
        quemar_subtitulos(tmp_vertical, ruta_ass, salida_final)

        os.remove(tmp_vertical)
        log.info("Listo: %s", salida_final)

    log.info("Total de clips generados: %d", len(clips))


if __name__ == "__main__":
    main()
