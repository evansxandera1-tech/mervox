"""
clips.py - v1.0
Corta cada momento elegido, lo recorta a vertical 9:16 centrando en el rostro
detectado, quema subtitulos estilo karaoke (palabra activa resaltada) y
aplica una vineta. Guarda los clips finales en clips_finales/.
"""
import os
import json
import logging
import subprocess
import cv2

logging.basicConfig(
    filename="mervox.log",
    level=logging.INFO,
    format="%(asctime)s [clips] %(levelname)s: %(message)s"
)
log = logging.getLogger("clips")

ANCHO_OUT, ALTO_OUT = 1080, 1920

def detectar_centro_rostro(video_path, tiempo_muestra):
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, tiempo_muestra * 1000)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return 0.5
    alto, ancho = frame.shape[:2]
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostros = cascade.detectMultiScale(gris, 1.1, 5)
    if len(rostros) == 0:
        return 0.5
    x, y, w, h = max(rostros, key=lambda r: r[2] * r[3])
    centro_x = (x + w / 2) / ancho
    return max(0.0, min(1.0, centro_x))

def segundos_a_ass(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generar_ass_karaoke(palabras, inicio_clip, fin_clip, ruta_ass):
    lineas = []
    lineas.append("[Script Info]")
    lineas.append(f"PlayResX: {ANCHO_OUT}")
    lineas.append(f"PlayResY: {ALTO_OUT}")
    lineas.append("ScriptType: v4.00+")
    lineas.append("")
    lineas.append("[V4+ Styles]")
    lineas.append("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding")
    lineas.append("Style: Default,Arial Black,72,&H00FFFFFF,&H0000D7FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,60,220,1")
    lineas.append("")
    lineas.append("[Events]")
    lineas.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")

    palabras_clip = [p for p in palabras if p["inicio"] >= inicio_clip and p["fin"] <= fin_clip]
    bloque = []
    for p in palabras_clip:
        bloque.append(p)
        if len(bloque) == 6 or p is palabras_clip[-1]:
            t_ini = bloque[0]["inicio"]
            t_fin = bloque[-1]["fin"]
            texto_k = ""
            for palabra in bloque:
                dur_cs = max(1, int((palabra["fin"] - palabra["inicio"]) * 100))
                texto_k += f"{{\\k{dur_cs}}}{palabra['palabra']} "
            ini_rel = t_ini - inicio_clip
            fin_rel = t_fin - inicio_clip
            lineas.append(f"Dialogue: 0,{segundos_a_ass(ini_rel)},{segundos_a_ass(fin_rel)},Default,,0,0,0,,{texto_k.strip()}")
            bloque = []

    with open(ruta_ass, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

def cortar_clip(video_path, inicio, fin, centro_x_rel, ruta_ass, salida):
    duracion = fin - inicio
    alto_src_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
                     "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path]
    out = subprocess.run(alto_src_cmd, capture_output=True, text=True).stdout.strip()
    ancho_src, alto_src = map(int, out.split(","))

    ancho_crop = int(alto_src * ANCHO_OUT / ALTO_OUT)
    ancho_crop = min(ancho_crop, ancho_src)
    x_centro_px = int(centro_x_rel * ancho_src)
    x_off = max(0, min(ancho_src - ancho_crop, x_centro_px - ancho_crop // 2))

    ass_escapado = ruta_ass.replace(":", "\\:")
    filtro = (
        f"crop={ancho_crop}:{alto_src}:{x_off}:0,"
        f"scale={ANCHO_OUT}:{ALTO_OUT},"
        f"vignette=PI/5,"
        f"subtitles='{ass_escapado}'"
    )

    cmd = [
        "ffmpeg", "-y", "-ss", str(inicio), "-i", video_path, "-t", str(duracion),
        "-vf", filtro, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", salida
    ]
    log.info(f"Cortando clip {salida} ({inicio:.1f}s - {fin:.1f}s)")
    subprocess.run(cmd, check=True)

def main():
    with open("momentos.json", encoding="utf-8") as f:
        data = json.load(f)
    with open("transcripcion.json", encoding="utf-8") as f:
        transcripcion = json.load(f)

    video = data["video"]
    momentos = data["momentos"]
    os.makedirs("clips_finales", exist_ok=True)

    for i, m in enumerate(momentos, start=1):
        inicio, fin = float(m["inicio"]), float(m["fin"])
        tiempo_muestra = inicio + (fin - inicio) / 2
        centro_x = detectar_centro_rostro(video, tiempo_muestra)

        ruta_ass = f"clip_{i}.ass"
        generar_ass_karaoke(transcripcion["palabras"], inicio, fin, ruta_ass)

        salida = f"clips_finales/clip_{i}.mp4"
        cortar_clip(video, inicio, fin, centro_x, ruta_ass, salida)
        log.info(f"Clip {i} listo: {salida} - titulo: {m.get('titulo', '')}")

    print(f"OK: {len(momentos)} clips generados en clips_finales/")

if __name__ == "__main__":
    main()
