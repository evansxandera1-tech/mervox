"""
Transcribir mis videos — Interfaz web
=============================================================
Versión: 1.9

v1.9: dos cambios pedidos:
  - Las transcripciones ahora se guardan directo en la carpeta
    Download del celular (~/storage/downloads/transcripciones_mis_canales),
    para poder verlas y abrirlas desde la app de Archivos de Android
    sin tener que copiarlas a mano. Si Termux todavía no tiene
    permiso de almacenamiento (no se corrió termux-setup-storage),
    usa como respaldo la carpeta de siempre junto al script.
  - Se agregó en la misma página un listado de "Archivos ya
    transcritos": nombre, tamaño y fecha de cada .txt guardado, para
    ver todo (barras de progreso, historial de canales, y ahora
    también los archivos generados) sin salir de la interfaz web.

v1.8: dos cambios pedidos:
  - Forzar por link directo ahora SIEMPRE sobrescribe, sin importar
    el modelo. Antes, si transcribías con "small" y luego forzabas
    ese mismo video con "tiny", quedaban dos archivos (uno por
    modelo). Ahora, al forzar, se borran las transcripciones
    anteriores de ese video (cualquier modelo) antes de generar la
    nueva, así que solo queda una por video.
  - Historial de canales: cada canal (o link de video forzado) que
    se usa para iniciar una transcripción queda guardado en
    historial_canales.json, junto al script. En la página aparecen
    como botones debajo del campo de texto para elegirlos con un
    toque, sin tener que volver a buscar o pegar el link.

v1.7: cambio de lógica en qué videos se descargan.
  - Antes: pedía "los N videos más recientes del canal" cada vez,
    sin importar si ya estaban descargados. Si ya tenías 2
    transcritos y pedías 3, volvía a mirar desde el video más nuevo
    y esos 2 quedaban salteados (por existir el archivo), pero
    siempre contando desde el video 1 del canal.
  - Ahora: recorre los videos del canal del más nuevo al más viejo,
    saltea los que YA tengan una transcripción guardada (sin
    importar con qué modelo se hizo) y recién ahí cuenta los N
    pedidos a partir del primero que todavía no está descargado.
  - El chequeo de "ya existe" dejó de depender del modelo: antes
    comparaba el archivo exacto canal+id+modelo.txt; ahora, para
    decidir si un video se saltea, busca cualquier archivo de ese
    canal+id sin importar el modelo. Si ya lo transcribiste en
    "small", no lo vuelve a bajar aunque ahora pidas "tiny".
  - Para forzar la re-transcripción de un video puntual con otro
    modelo, hay que pegar el LINK DIRECTO de ese video (no el canal
    ni el @usuario). En ese caso el script ignora el chequeo de "ya
    existe" y lo procesa siempre con el modelo elegido.

v1.6: se agregaron barras de progreso individuales para cada acción
dentro de un mismo video (Descargando audio, Convirtiendo audio,
Transcribiendo), en vez de solo mostrar el texto en el log. Además,
durante la pausa aleatoria entre videos ahora se muestra una cuenta
regresiva en vivo ("Próxima descarga en Xs") indicando cuándo va a
empezar a descargarse el siguiente video.

v1.5: se agregó filtro explícito para descartar Shorts de la lista de
videos. Aunque se pide la pestaña "/videos" del canal (que en teoría
ya excluye Shorts), se suma una verificación extra por duración
(<=60s se considera Short) y por URL (que no contenga "/shorts/"),
por si YouTube devuelve resultados mixtos.

v1.4: se agregó barra de progreso con tiempo estimado restante. La
interfaz ahora muestra "Video X de Y" y una estimación en minutos de
cuánto falta, calculada con el tiempo promedio que tardó cada video
ya procesado (se ajusta sola a medida que avanza).

v1.3: se reemplazó "scrapetube" por "yt-dlp" para listar los videos
del canal. scrapetube tiene un bug conocido (sin resolver al momento)
por un cambio de YouTube en la estructura interna de sus páginas, que
hacía que siempre devolviera 0 videos. yt-dlp está más mantenido y ya
era una dependencia del script (se usa para descargar el audio), así
que ahora también se usa para listar los videos del canal.

v1.2: se reemplazó la librería Python "openai-whisper" (que depende
de numba/llvmlite, muy inestable para instalar en Termux) por el
binario whisper.cpp, que ya compilaste en ~/whisper.cpp. La app ya
no hace "import whisper": ahora convierte el audio a .wav (16kHz
mono) con ffmpeg y llama a whisper-cli por consola. Requiere tener
descargados los modelos ggml correspondientes a "tiny" y "small"
(ver instrucciones más abajo).

v1.1: se agregó selector de modelo Whisper ("tiny" o "small") en la
misma interfaz web, para poder elegir por corrida cuál usar (tiny es
más rápido, small es más preciso con ruido de fondo/intros fuertes).

Interfaz web simple (Flask, corre en Termux igual que Story Engine)
para pegar el link o @usuario de uno de tus canales y transcribir sus
videos más recientes, sin tener que editar el código cada vez.

Reutiliza la misma lógica de transcribir_mis_videos_v2-3.py (filtro
automático de videos de solo música, pausas al azar entre descargas),
pero ahora manejada desde un formulario web en vez de una lista fija
de canales en el código.

Requisitos en Termux:
    pkg install ffmpeg
    pip install yt-dlp flask --break-system-packages

    Además, whisper.cpp ya compilado en ~/whisper.cpp (build/bin/whisper-cli)
    con los modelos descargados:
        cd ~/whisper.cpp
        sh ./models/download-ggml-model.sh tiny
        sh ./models/download-ggml-model.sh small

Uso: python transcribir_web_v1-9.py
     (abre solo en el navegador del celular, http://127.0.0.1:<puerto>)
"""

import glob
import json
import os
import random
import re
import socket
import subprocess
import threading
import time

import yt_dlp
from flask import Flask, jsonify, redirect, render_template_string, request

CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

_RUTA_DOWNLOADS = os.path.expanduser("~/storage/downloads")
if os.path.isdir(_RUTA_DOWNLOADS):
    CARPETA_SALIDA = os.path.join(_RUTA_DOWNLOADS, "transcripciones_mis_canales")
else:
    # Respaldo: Termux todavía no tiene permiso de almacenamiento
    # (falta correr termux-setup-storage). Se guarda junto al script
    # como antes, para no perder nada mientras tanto.
    CARPETA_SALIDA = os.path.join(CARPETA_SCRIPT, "transcripciones_mis_canales")
os.makedirs(CARPETA_SALIDA, exist_ok=True)

MODELOS_DISPONIBLES = ["tiny", "small"]
MODELO_POR_DEFECTO = "tiny"
PALABRAS_MINIMAS_TEXTO = 30
PAUSA_ENTRE_VIDEOS_MIN = 15
PAUSA_ENTRE_VIDEOS_MAX = 60

HISTORIAL_ARCHIVO = os.path.join(CARPETA_SCRIPT, "historial_canales.json")
HISTORIAL_MAXIMO = 15


def _cargar_historial():
    if not os.path.exists(HISTORIAL_ARCHIVO):
        return []
    try:
        with open(HISTORIAL_ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _guardar_en_historial(entrada):
    """Guarda el canal (o link forzado) al principio del historial,
    sin duplicados, para que la próxima vez se pueda elegir con un
    toque en vez de volver a pegarlo."""
    entrada = entrada.strip()
    historial = [h for h in _cargar_historial() if h != entrada]
    historial.insert(0, entrada)
    historial = historial[:HISTORIAL_MAXIMO]
    try:
        with open(HISTORIAL_ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"⚠️  No se pudo guardar el historial: {e}")

# --- whisper.cpp (reemplaza a la librería Python "whisper") ---
WHISPER_CPP_DIR = os.path.expanduser("~/whisper.cpp")
WHISPER_CPP_BIN = os.path.join(WHISPER_CPP_DIR, "build", "bin", "whisper-cli")
WHISPER_CPP_MODELOS_DIR = os.path.join(WHISPER_CPP_DIR, "models")


def _ruta_modelo_ggml(nombre_modelo):
    return os.path.join(WHISPER_CPP_MODELOS_DIR, f"ggml-{nombre_modelo}.bin")


def _video_ya_transcrito(nombre_canal, video_id):
    """True si ya existe una transcripción de este video para este
    canal, sin importar con qué modelo (tiny/small) se haya hecho."""
    patron = os.path.join(CARPETA_SALIDA, f"{nombre_canal}__{video_id}__*.txt")
    return len(glob.glob(patron)) > 0


def _es_link_de_video(entrada):
    """True si el usuario pegó el link directo a UN video puntual
    (no un canal ni un @usuario). Se usa para forzar la
    re-transcripción de ese video con otro modelo."""
    return bool(re.search(r"(watch\?v=|youtu\.be/|/shorts/)", entrada.strip()))

ESTADO = {
    "corriendo": False,
    "canal": None,
    "log": [],
    "terminado": False,
    "video_actual": 0,
    "total_videos": 0,
    "tiempos_videos": [],
    "etapa": None,
    "etapa_pct": None,
    "pausa_restante_seg": None,
}
CANDADO = threading.Lock()


def log(msg):
    print(msg)
    with CANDADO:
        ESTADO["log"].append(msg)


def _actualizar_etapa(etapa, pct=None):
    """Actualiza la acción actual (descarga/conversión/transcripción)
    y su porcentaje de avance (None = indeterminado, se muestra
    animación en vez de un %)."""
    with CANDADO:
        ESTADO["etapa"] = etapa
        ESTADO["etapa_pct"] = pct


def cargar_modelo(nombre_modelo):
    """Ya no carga nada en memoria (whisper.cpp lo hace por proceso).
    Solo valida que el binario y el modelo ggml existan antes de arrancar,
    para avisar temprano si falta algo."""
    if not os.path.exists(WHISPER_CPP_BIN):
        raise FileNotFoundError(
            f"No se encontró whisper-cli en {WHISPER_CPP_BIN}. "
            "Compilá whisper.cpp primero (ver instrucciones al inicio del archivo)."
        )
    ruta_modelo = _ruta_modelo_ggml(nombre_modelo)
    if not os.path.exists(ruta_modelo):
        raise FileNotFoundError(
            f"No se encontró el modelo '{nombre_modelo}' en {ruta_modelo}. "
            f"Descargalo con: cd {WHISPER_CPP_DIR} && sh ./models/download-ggml-model.sh {nombre_modelo}"
        )
    return ruta_modelo


def descargar_audio(video_url, nombre_salida, progreso_cb=None):
    def _hook(d):
        if not progreso_cb or d.get("status") != "downloading":
            return
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        descargado = d.get("downloaded_bytes")
        if total and descargado:
            progreso_cb(min(100, int(descargado / total * 100)))

    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": nombre_salida,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [_hook] if progreso_cb else [],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def obtener_videos_canal(url_canal, max_videos, nombre_canal):
    """Lista los videos más recientes de un canal usando yt-dlp que
    TODAVÍA NO tengan una transcripción guardada. Recorre del más
    nuevo al más viejo, saltea Shorts y los que ya estén transcritos
    (con cualquier modelo), y devuelve los primeros `max_videos` que
    encuentre sin descargar. También devuelve cuántos se saltearon
    por ya estar transcritos, para informarlo en el log."""
    url_videos = url_canal.rstrip("/")
    if not url_videos.endswith("/videos"):
        url_videos += "/videos"

    ydl_opts = {
        "extract_flat": True,
        # buffer grande: además de descartar Shorts, ahora también
        # se saltean los que ya están transcritos, así que puede
        # hacer falta mirar bastante más atrás que max_videos.
        "playlistend": max(max_videos * 8, 30),
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_videos, download=False)

    entradas = (info or {}).get("entries") or []
    videos = []
    saltados_ya_transcritos = 0
    for entrada in entradas:
        if len(videos) >= max_videos:
            break

        url_entrada = entrada.get("url") or entrada.get("webpage_url") or ""
        if "/shorts/" in url_entrada:
            continue

        duracion = entrada.get("duration")
        if duracion is not None and duracion <= 60:
            continue

        video_id = entrada.get("id")
        if _video_ya_transcrito(nombre_canal, video_id):
            saltados_ya_transcritos += 1
            continue

        titulo = entrada.get("title") or video_id
        videos.append({
            "videoId": video_id,
            "title": {"runs": [{"text": titulo}]},
            "duration": duracion,  # se usa para estimar el % de avance al convertir el audio
        })
    return videos, saltados_ya_transcritos


def obtener_info_video_individual(url_video):
    """Trae los datos de UN solo video a partir de su link directo,
    para el modo 'forzar re-transcripción con otro modelo'."""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_video, download=False)

    video_id = info.get("id")
    titulo = info.get("title") or video_id
    duracion = info.get("duration")
    nombre_canal = (
        info.get("uploader_id") or info.get("channel_id")
        or info.get("uploader") or info.get("channel") or "canal"
    )
    nombre_canal = str(nombre_canal).lstrip("@")

    video = {
        "videoId": video_id,
        "title": {"runs": [{"text": titulo}]},
        "duration": duracion,
    }
    return video, nombre_canal


def _parsear_out_time(valor):
    """Convierte 'HH:MM:SS.microsegundos' (formato de ffmpeg -progress)
    a segundos totales (float)."""
    try:
        h, m, s = valor.strip().split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        return None


def _convertir_a_wav(ruta_entrada, ruta_wav, duracion_total_seg=None, progreso_cb=None):
    """Convierte el audio descargado (m4a) a wav 16kHz mono, formato
    que whisper.cpp necesita. Si se conoce la duración del video y se
    pasa un progreso_cb, reporta el % de avance real leyendo la
    salida de '-progress pipe:1' de ffmpeg."""
    comando = [
        "ffmpeg", "-y", "-i", ruta_entrada,
        "-ar", "16000", "-ac", "1",
        "-progress", "pipe:1", "-nostats",
        ruta_wav,
    ]
    if not progreso_cb or not duracion_total_seg:
        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    for linea in proceso.stdout:
        linea = linea.strip()
        if linea.startswith("out_time="):
            segundos = _parsear_out_time(linea.split("=", 1)[1])
            if segundos is not None:
                pct = min(100, int(segundos / duracion_total_seg * 100))
                progreso_cb(pct)
    proceso.wait()
    if proceso.returncode != 0:
        raise subprocess.CalledProcessError(proceso.returncode, comando)


def _transcribir_con_whisper_cpp(ruta_modelo_ggml, ruta_wav, ruta_salida_sin_extension, progreso_cb=None):
    """Llama a whisper-cli y devuelve el texto transcrito leyendo el
    .txt que el propio binario genera con -otxt. Con -pp (print
    progress), whisper.cpp imprime líneas tipo 'progress = 42%' por
    stderr, que se leen en vivo para reportar el avance real."""
    comando = [
        WHISPER_CPP_BIN,
        "-m", ruta_modelo_ggml,
        "-f", ruta_wav,
        "-l", "es",
        "-otxt",
        "-of", ruta_salida_sin_extension,
        "-np",
        "-pp",
    ]
    if not progreso_cb:
        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        proceso = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        patron_pct = re.compile(r"progress\s*=\s*(\d+)")
        for linea in proceso.stderr:
            coincidencia = patron_pct.search(linea)
            if coincidencia:
                progreso_cb(min(100, int(coincidencia.group(1))))
        proceso.wait()
        if proceso.returncode != 0:
            raise subprocess.CalledProcessError(proceso.returncode, comando)

    ruta_txt_generado = ruta_salida_sin_extension + ".txt"
    with open(ruta_txt_generado, "r", encoding="utf-8") as f:
        texto = f.read().strip()
    os.remove(ruta_txt_generado)
    return texto


def procesar_video(ruta_modelo_ggml, nombre_modelo, video, nombre_canal, forzar=False):
    video_id = video["videoId"]
    titulo = video.get("title", {}).get("runs", [{}])[0].get("text", video_id)
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    temp_audio = os.path.join(CARPETA_SCRIPT, f"temp_{video_id}.m4a")
    temp_wav = os.path.join(CARPETA_SCRIPT, f"temp_{video_id}.wav")
    temp_salida_sin_ext = os.path.join(CARPETA_SCRIPT, f"temp_{video_id}_out")
    txt_salida = os.path.join(CARPETA_SALIDA, f"{nombre_canal}__{video_id}__{nombre_modelo}.txt")

    log(f"  → {titulo}")

    if os.path.exists(txt_salida) and not forzar:
        log("    ⏭️  Ya transcrito antes. Saltando.")
        return
    if forzar:
        anteriores = glob.glob(os.path.join(CARPETA_SALIDA, f"{nombre_canal}__{video_id}__*.txt"))
        for anterior in anteriores:
            os.remove(anterior)
        log(f"    🔁 Forzando transcripción con modelo '{nombre_modelo}' (se sobrescribe cualquier versión anterior).")

    duracion_video = video.get("duration")

    try:
        log("    Descargando audio...")
        _actualizar_etapa("Descargando audio", 0)
        descargar_audio(video_url, temp_audio, progreso_cb=lambda pct: _actualizar_etapa("Descargando audio", pct))

        log("    Convirtiendo audio...")
        _actualizar_etapa("Convirtiendo audio", 0)
        _convertir_a_wav(
            temp_audio, temp_wav, duracion_video,
            progreso_cb=lambda pct: _actualizar_etapa("Convirtiendo audio", pct),
        )

        log("    Transcribiendo...")
        _actualizar_etapa("Transcribiendo", 0)
        texto = _transcribir_con_whisper_cpp(
            ruta_modelo_ggml, temp_wav, temp_salida_sin_ext,
            progreso_cb=lambda pct: _actualizar_etapa("Transcribiendo", pct),
        )
        n_palabras = len(texto.split())

        if n_palabras < PALABRAS_MINIMAS_TEXTO:
            log(f"    ⏭️  Descartado: solo {n_palabras} palabras (probablemente solo música).")
            return

        with open(txt_salida, "w", encoding="utf-8") as f:
            f.write(f"CANAL: {nombre_canal}\nTÍTULO: {titulo}\nURL: {video_url}\nMODELO: {nombre_modelo}\n{'=' * 60}\n\n")
            f.write(texto)

        log(f"    ✅ Guardado ({n_palabras} palabras).")

    except Exception as e:
        log(f"    ❌ Error: {type(e).__name__}: {e}")

    finally:
        _actualizar_etapa(None, None)
        for temp_file in (temp_audio, temp_wav):
            if os.path.exists(temp_file):
                os.remove(temp_file)


def _extraer_nombre_canal(entrada):
    """Acepta tanto un link completo como solo el @usuario, y devuelve
    (url_completa, nombre_para_archivos)."""
    entrada = entrada.strip()
    if entrada.startswith("http"):
        url = entrada
    elif entrada.startswith("@"):
        url = f"https://youtube.com/{entrada}"
    else:
        url = f"https://youtube.com/@{entrada}"
    nombre = url.rstrip("/").split("@")[-1]
    return url, nombre


def procesar_canal_en_hilo(entrada_canal, max_videos, nombre_modelo):
    with CANDADO:
        ESTADO["corriendo"] = True
        ESTADO["terminado"] = False
        ESTADO["log"] = []
        ESTADO["canal"] = entrada_canal
        ESTADO["video_actual"] = 0
        ESTADO["total_videos"] = 0
        ESTADO["tiempos_videos"] = []
        ESTADO["etapa"] = None
        ESTADO["etapa_pct"] = None
        ESTADO["pausa_restante_seg"] = None

    try:
        ruta_modelo_ggml = cargar_modelo(nombre_modelo)

        if _es_link_de_video(entrada_canal):
            log(f"=== Video individual — forzando transcripción (modelo: {nombre_modelo}) ===")
            video, nombre_canal = obtener_info_video_individual(entrada_canal.strip())
            videos = [video]
            forzar = True
            with CANDADO:
                ESTADO["total_videos"] = 1
        else:
            url, nombre_canal = _extraer_nombre_canal(entrada_canal)
            log(f"=== Canal: {nombre_canal} (modelo: {nombre_modelo}) ===")

            log("Buscando videos nuevos del canal (no descargados todavía)...")
            videos, saltados = obtener_videos_canal(url, max_videos, nombre_canal)
            if saltados:
                log(f"  {saltados} video(s) ya estaban transcritos antes (con cualquier modelo), se saltearon.")
            log(f"Nuevos a procesar: {len(videos)}")
            forzar = False

            with CANDADO:
                ESTADO["total_videos"] = len(videos)

        for i, video in enumerate(videos, 1):
            if i > 1:
                pausa = random.uniform(PAUSA_ENTRE_VIDEOS_MIN, PAUSA_ENTRE_VIDEOS_MAX)
                log(f"(pausa de {pausa:.0f}s antes de descargar el próximo video...)")
                fin_pausa = time.time() + pausa
                while True:
                    restante = fin_pausa - time.time()
                    if restante <= 0:
                        break
                    with CANDADO:
                        ESTADO["pausa_restante_seg"] = restante
                    time.sleep(min(1, restante))
                with CANDADO:
                    ESTADO["pausa_restante_seg"] = None
            log(f"[{i}/{len(videos)}]")
            with CANDADO:
                ESTADO["video_actual"] = i
            inicio_video = time.time()
            procesar_video(ruta_modelo_ggml, nombre_modelo, video, nombre_canal, forzar=forzar)
            with CANDADO:
                ESTADO["tiempos_videos"].append(time.time() - inicio_video)

        log("=== Listo ===")

    except Exception as e:
        log(f"❌ Error general: {type(e).__name__}: {e}")

    finally:
        with CANDADO:
            ESTADO["corriendo"] = False
            ESTADO["terminado"] = True


PAGINA = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Transcribir mis videos</title>
<style>
body { font-family: sans-serif; max-width: 480px; margin: 20px auto; padding: 0 12px; }
input, button { font-size: 16px; padding: 10px; width: 100%; box-sizing: border-box; margin-bottom: 10px; }
button { background: #333; color: white; border: none; border-radius: 6px; }
button:disabled { background: #999; }
#log { background: #111; color: #0f0; padding: 10px; font-family: monospace; font-size: 13px;
       white-space: pre-wrap; height: 300px; overflow-y: auto; border-radius: 6px; }
#progreso_contenedor { display: none; margin-bottom: 10px; }
#progreso_barra_fondo { background: #ddd; border-radius: 6px; height: 18px; overflow: hidden; }
#progreso_barra { background: #333; height: 100%; width: 0%; transition: width 0.4s; }
#progreso_texto { font-size: 13px; color: #555; margin-top: 4px; }

#etapa_contenedor { display: none; margin-bottom: 10px; }
#etapa_barra_fondo { background: #e6e6e6; border-radius: 6px; height: 14px; overflow: hidden; }
#etapa_barra { background: #2b8a3e; height: 100%; width: 0%; transition: width 0.3s; }
#etapa_barra.indeterminado {
    width: 40% !important;
    animation: mover_indeterminado 1.2s infinite linear;
}
@keyframes mover_indeterminado {
    0% { margin-left: -40%; }
    100% { margin-left: 100%; }
}
#etapa_texto { font-size: 13px; color: #555; margin-top: 4px; }

#pausa_texto { display: none; font-size: 13px; color: #b45309; margin-bottom: 10px; text-align: center; }

#historial_contenedor { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
#historial_titulo { width: 100%; font-size: 12px; color: #777; }
.chip {
    width: auto; background: #eee; color: #333; border: 1px solid #ccc;
    border-radius: 999px; padding: 5px 12px; font-size: 12px; margin-bottom: 0;
    max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.chip:active { background: #ddd; }

#archivos_seccion { margin-top: 16px; }
#archivos_titulo { font-size: 14px; color: #333; margin-bottom: 6px; font-weight: bold; }
#archivos_lista { max-height: 220px; overflow-y: auto; border: 1px solid #ddd; border-radius: 6px; }
.archivo_item {
    padding: 8px 10px; border-bottom: 1px solid #eee; font-size: 13px;
    display: flex; justify-content: space-between; gap: 8px;
}
.archivo_item:last-child { border-bottom: none; }
.archivo_nombre { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.archivo_meta { color: #888; font-size: 12px; white-space: nowrap; }
</style>
</head>
<body>
<h2>Transcribir mis videos</h2>
<p>Pegá el link o @usuario del canal (solo tus propios canales). Para forzar la re-transcripción de un video puntual con otro modelo, pegá el link directo de ESE video.</p>
<input id="canal" placeholder="https://youtube.com/@MiCanal, @MiCanal, o el link de un video puntual">
<div id="historial_contenedor"></div>
<input id="max_videos" type="number" value="2" min="1" placeholder="Cantidad de videos">
<select id="modelo">
    <option value="tiny">tiny (rápido)</option>
    <option value="small">small (más preciso, más lento)</option>
</select>
<button id="btn" onclick="iniciar()">Transcribir</button>
<div id="progreso_contenedor">
    <div id="progreso_barra_fondo"><div id="progreso_barra"></div></div>
    <div id="progreso_texto"></div>
</div>
<div id="etapa_contenedor">
    <div id="etapa_barra_fondo"><div id="etapa_barra"></div></div>
    <div id="etapa_texto"></div>
</div>
<div id="pausa_texto"></div>
<div id="log"></div>

<div id="archivos_seccion">
    <div id="archivos_titulo">📁 Archivos ya transcritos</div>
    <div id="archivos_lista"></div>
</div>

<script>
function iniciar() {
    const canal = document.getElementById('canal').value.trim();
    const max_videos = document.getElementById('max_videos').value || 2;
    const modelo = document.getElementById('modelo').value;
    if (!canal) { alert('Pegá un canal primero.'); return; }
    document.getElementById('btn').disabled = true;
    fetch('/iniciar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({canal: canal, max_videos: max_videos, modelo: modelo})
    }).then(() => cargarHistorial());
    actualizar();
}

function cargarHistorial() {
    fetch('/historial').then(r => r.json()).then(lista => {
        const cont = document.getElementById('historial_contenedor');
        cont.innerHTML = '';
        if (!lista.length) return;
        const titulo = document.createElement('div');
        titulo.id = 'historial_titulo';
        titulo.textContent = 'Usados antes (tocá para elegir):';
        cont.appendChild(titulo);
        lista.forEach(item => {
            const chip = document.createElement('button');
            chip.type = 'button';
            chip.className = 'chip';
            chip.textContent = item;
            chip.onclick = () => { document.getElementById('canal').value = item; };
            cont.appendChild(chip);
        });
    });
}
function cargarArchivos() {
    fetch('/archivos').then(r => r.json()).then(lista => {
        const cont = document.getElementById('archivos_lista');
        cont.innerHTML = '';
        if (!lista.length) {
            cont.innerHTML = '<div class="archivo_item"><span class="archivo_nombre">Todavía no hay archivos.</span></div>';
            return;
        }
        lista.forEach(a => {
            const item = document.createElement('div');
            item.className = 'archivo_item';
            item.innerHTML = `<span class="archivo_nombre">${a.nombre}</span><span class="archivo_meta">${a.tamano_kb} KB · ${a.fecha}</span>`;
            cont.appendChild(item);
        });
    });
}
window.addEventListener('DOMContentLoaded', cargarHistorial);
window.addEventListener('DOMContentLoaded', cargarArchivos);

function formatearTiempo(segundos) {
    if (segundos == null) return '';
    segundos = Math.round(segundos);
    const m = Math.floor(segundos / 60);
    const s = segundos % 60;
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

function actualizar() {
    fetch('/estado').then(r => r.json()).then(data => {
        document.getElementById('log').textContent = data.log.join('\\n');
        document.getElementById('log').scrollTop = 999999;

        const contenedor = document.getElementById('progreso_contenedor');
        if (data.total_videos > 0) {
            contenedor.style.display = 'block';
            const pct = Math.round((data.video_actual / data.total_videos) * 100);
            document.getElementById('progreso_barra').style.width = pct + '%';
            let texto = `Video ${data.video_actual} de ${data.total_videos} (${pct}%)`;
            if (data.tiempo_restante_seg != null) {
                texto += ` — tiempo restante estimado: ${formatearTiempo(data.tiempo_restante_seg)}`;
            }
            document.getElementById('progreso_texto').textContent = texto;
        } else {
            contenedor.style.display = 'none';
        }

        const etapaContenedor = document.getElementById('etapa_contenedor');
        const etapaBarra = document.getElementById('etapa_barra');
        if (data.etapa) {
            etapaContenedor.style.display = 'block';
            if (data.etapa_pct == null) {
                etapaBarra.classList.add('indeterminado');
                etapaBarra.style.width = '';
                document.getElementById('etapa_texto').textContent = data.etapa + '...';
            } else {
                etapaBarra.classList.remove('indeterminado');
                etapaBarra.style.width = data.etapa_pct + '%';
                document.getElementById('etapa_texto').textContent = `${data.etapa} — ${data.etapa_pct}%`;
            }
        } else {
            etapaContenedor.style.display = 'none';
        }

        const pausaTexto = document.getElementById('pausa_texto');
        if (data.pausa_restante_seg != null) {
            pausaTexto.style.display = 'block';
            pausaTexto.textContent = `⏳ Próxima descarga en ${formatearTiempo(data.pausa_restante_seg)}`;
        } else {
            pausaTexto.style.display = 'none';
        }

        if (data.corriendo) {
            const intervalo = (data.pausa_restante_seg != null) ? 1000 : 2000;
            setTimeout(actualizar, intervalo);
        } else {
            document.getElementById('btn').disabled = false;
            cargarArchivos();
        }
    });
}
</script>
</body>
</html>
"""

app = Flask(__name__)


@app.route("/")
def _raiz():
    return render_template_string(PAGINA)


@app.route("/iniciar", methods=["POST"])
def _iniciar():
    with CANDADO:
        if ESTADO["corriendo"]:
            return jsonify({"error": "Ya hay una transcripción en curso"}), 409
    datos = request.get_json(force=True)
    canal = datos.get("canal", "").strip()
    max_videos = int(datos.get("max_videos", 2))
    nombre_modelo = datos.get("modelo", MODELO_POR_DEFECTO)
    if nombre_modelo not in MODELOS_DISPONIBLES:
        nombre_modelo = MODELO_POR_DEFECTO
    if not canal:
        return jsonify({"error": "Falta el canal"}), 400
    _guardar_en_historial(canal)
    threading.Thread(target=procesar_canal_en_hilo, args=(canal, max_videos, nombre_modelo), daemon=True).start()
    return jsonify({"ok": True})


@app.route("/historial")
def _historial():
    return jsonify(_cargar_historial())


@app.route("/archivos")
def _archivos():
    """Lista los .txt ya generados (nombre, tamaño, fecha), para
    mostrarlos en la misma página sin salir de la interfaz web."""
    archivos = []
    try:
        for nombre in os.listdir(CARPETA_SALIDA):
            if not nombre.endswith(".txt"):
                continue
            ruta = os.path.join(CARPETA_SALIDA, nombre)
            archivos.append({
                "nombre": nombre,
                "tamano_kb": round(os.path.getsize(ruta) / 1024, 1),
                "mtime": os.path.getmtime(ruta),
            })
        archivos.sort(key=lambda a: a["mtime"], reverse=True)
        for a in archivos:
            a["fecha"] = time.strftime("%d/%m %H:%M", time.localtime(a.pop("mtime")))
    except Exception as e:
        log(f"⚠️  No se pudo listar archivos: {e}")
    return jsonify(archivos)


@app.route("/estado")
def _estado():
    with CANDADO:
        tiempos = list(ESTADO["tiempos_videos"])
        video_actual = ESTADO["video_actual"]
        total_videos = ESTADO["total_videos"]
        respuesta = {
            "corriendo": ESTADO["corriendo"],
            "log": list(ESTADO["log"]),
            "video_actual": video_actual,
            "total_videos": total_videos,
            "tiempo_restante_seg": None,
            "etapa": ESTADO["etapa"],
            "etapa_pct": ESTADO["etapa_pct"],
            "pausa_restante_seg": ESTADO["pausa_restante_seg"],
        }
    if tiempos and total_videos:
        promedio = sum(tiempos) / len(tiempos)
        videos_restantes = max(total_videos - video_actual, 0)
        respuesta["tiempo_restante_seg"] = promedio * videos_restantes
    return jsonify(respuesta)


def _obtener_ip_lan():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _abrir_navegador(puerto):
    time.sleep(1.5)
    try:
        subprocess.run(["termux-open-url", f"http://127.0.0.1:{puerto}"], check=True)
    except Exception:
        pass


if __name__ == "__main__":
    puerto = random.randint(6000, 6999)
    ip_lan = _obtener_ip_lan()
    print(f"\n*** Transcribir mis videos — Interfaz web v1.9 ***")
    print(f"Guardando transcripciones en: {CARPETA_SALIDA}")
    print(f"Accedé desde este celular: http://127.0.0.1:{puerto}")
    print(f"Accedé desde otro dispositivo en la misma red: http://{ip_lan}:{puerto}")
    print("Presioná Ctrl+C para apagar.\n")

    threading.Thread(target=_abrir_navegador, args=(puerto,), daemon=True).start()
    app.run(host="0.0.0.0", port=puerto, debug=False, threaded=True)
