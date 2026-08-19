"""
Transcribir mis videos — Interfaz web
=============================================================
Versión: 4.3

v4.3: fix en _extraer_nombre_canal (usada por las tres pestañas:
  transcribir, descargar gameplay y contar). El link de "Compartir
  canal" de YouTube trae un ?si=... de tracking pegado al final; al
  agregarle '/videos' sin sacar antes esa query, la URL quedaba
  rota y yt-dlp tiraba 404. Ahora se descarta la query antes de
  armar la URL final. De paso, también tolera texto extra pegado
  alrededor del link o el @usuario (ej. el nombre del canal).

v4.2: dos mejoras a la pestaña "Descargar gameplay":
  1) FIX "authcheck": listar canales de gameplay AJENOS (no el dueño
     de ~/cookies.txt) fallaba con "Playlists that require
     authentication may not extract correctly...". Se agregó
     extractor_args youtubetab:skip=authcheck a la función que lista
     esos canales, así yt-dlp no exige que las cookies coincidan con
     el canal para poder listarlo.
  2) BOTÓN "Contar videos": tercer botón en la pestaña, separado de
     los de descarga. No baja nada — solo recorre el canal y
     devuelve cuántos videos recientes son verticales y cuántos
     horizontales, para saber qué hay antes de pedir una descarga.
     Reutiliza el mismo log/estado/polling que ya tenía la pestaña.

v4.1: dos mejoras a la pestaña "Descargar gameplay":
  1) CONTEO POR ORIENTACIÓN: al buscar videos de un canal, ahora se
     informa cuántos de los revisados son verticales y cuántos
     horizontales (dentro del lote reciente que se llega a escanear,
     no de todo el historial del canal — sería demasiado pedir la
     resolución de cada video que subió alguna vez).
  2) BOTÓN "Descargar horizontales": se agregó un segundo botón al
     lado del de verticales. Internamente es la misma lógica de
     descarga, solo cambia el filtro de orientación. Los dos tipos
     se guardan en la misma carpeta del canal (para no duplicar
     estructura), diferenciados por su propio nombre de archivo.

v4.0: se agregó una segunda pestaña "🎮 Descargar gameplay" en la
  misma interfaz (mismo servidor, mismo puerto, un clic para
  cambiar de pestaña sin recargar la página). No descarga audio ni
  transcribe: baja el VIDEO completo (720p, formato vertical 9:16
  únicamente) de un canal, uno por uno.
  - Filtro de orientación: antes de descargar cada video se
    consulta su resolución real; si es horizontal (ancho > alto) se
    saltea solo, sin bajarlo, aunque esté entre los más recientes
    del canal.
  - Carpeta por canal, para dar crédito: cada canal descargado
    genera su propia carpeta dentro de
    ~/storage/downloads/gameplay_descargado/<nombre_canal>/, así
    que si mezclás varios canales (ej. uno de Minecraft Parkour y
    otro de Subway Surfers) cada uno queda organizado aparte con su
    nombre.
  - Reutiliza la infraestructura ya existente: historial de canales
    (uno separado, propio de esta pestaña), barra de progreso, log
    en vivo, pausas aleatorias entre descargas y los reintentos
    automáticos ante fallas transitorias de yt-dlp.
  - Por ahora NO combina ni recorta nada (eso queda pendiente para
    más adelante); solo descarga los videos verticales tal cual,
    listos para usarlos después.

v3.2: se subió el timeout de las llamadas a Gemini (mejora de guion)
  de 60 a 240 segundos. Con guiones largos (videos de 30-45+ minutos,
  varios miles de palabras), 60 segundos no siempre alcanzaba y la
  API cortaba con ReadTimeout, guardando el texto crudo de whisper.cpp
  sin la mejora. Con más margen, se reduce ese fallo sin afectar los
  guiones cortos (que igual responden mucho antes del límite).

v3.1: el historial de canales usados (historial_canales.json) ahora
  se guarda en una carpeta FIJA dentro de Download
  (~/storage/downloads/transcribir_web_datos/), separada de la
  carpeta donde esté el script. Antes se guardaba junto al archivo
  .py, así que al mover o reemplazar el script por una versión
  nueva en otra carpeta, el historial "desaparecía" (no se borraba,
  pero el script ya no lo encontraba). Ahora, sin importar dónde se
  guarde cada versión nueva del .py, siempre lee y escribe ese mismo
  archivo fijo. También se quitó el límite de 15 canales: de acá en
  más se guardan todos, para siempre. Si ya tenías un historial
  viejo guardado junto al script, se migra automáticamente la
  primera vez que corras esta versión.

v3.0: dos mejoras grandes.
  1) DESCARGAS ROBUSTAS: las tres llamadas a yt-dlp ahora reintentan
     solas ante fallas transitorias (conexión reseteada, "Requested
     format is not available" puntual, etc.), con una pausa creciente
     entre intento e intento (backoff). Además se agregó ritmo de
     descarga (sleep_interval / sleep_interval_requests) para que el
     script se comporte menos como tráfico automatizado desde el
     arranque, en vez de solo reaccionar después de que YouTube ya
     empezó a bloquear. Nada de esto es infalible (YouTube cambia sus
     reglas seguido), pero baja bastante la tasa de fallos que se veía
     en el log.
  2) MEJORA DE GUION CON GEMINI: después de transcribir con
     whisper.cpp, si hay una GEMINI_API_KEY configurada, el texto se
     manda a la API de Gemini en dos pasadas: la primera corrige
     errores de transcripción, parafrasea (cambia palabras y
     estructura de oraciones) y agrega puntuación pensada para que una
     voz sintética la lea bien (comas, puntos, oraciones cortas); la
     segunda pasada relee ese resultado y lo pule (repeticiones,
     puntuación rara, que no se aleje del sentido original). El .txt
     final guardado es la versión mejorada por Gemini, lista para
     pasar a un generador de voz; el texto crudo de whisper.cpp queda
     guardado aparte (mismo nombre + "__original.txt") por si hace
     falta comparar. Si no hay GEMINI_API_KEY configurada, este paso
     se saltea solo y se guarda el texto de whisper.cpp tal cual,
     como antes.
     Requiere: la librería "requests" (probablemente ya instalada, es
     dependencia de yt-dlp) y la variable de entorno GEMINI_API_KEY
     seteada en Termux, por ejemplo agregando a ~/.bashrc:
         export GEMINI_API_KEY="tu_clave_aca"
     Se puede elegir otro modelo con la variable opcional
     GEMINI_MODELO (por defecto usa "gemini-3.6-flash").

v2.7: la versión del script ahora se ve también en la interfaz web
  (al lado del título "Transcribir mis videos"), no solo en el
  banner de la terminal al arrancar. Se agregó una constante
  VERSION al principio del archivo que alimenta a los dos lugares,
  para no tener que actualizarla en varios sitios.

v2.6: causa real del "Requested format is not available" encontrada:
  YouTube exige resolver un desafío de JavaScript ("n challenge")
  antes de entregar formatos de audio/video reales; sin eso, solo
  devuelve miniaturas (sb0-sb3). Se agregó "js_runtimes": {"node": {}}
  y "remote_components": {"ejs:github"} a las tres llamadas de
  yt-dlp para que use Node.js a resolver ese desafío. Requiere tener
  Node.js instalado en Termux: pkg install nodejs

v2.5: dos cambios para el error "Requested format is not available"
  que seguía apareciendo en algunos videos incluso con cookies:
  1) Se agregó "tv" como primer player_client (antes de "android" y
     "web") — es el que menos está sufriendo el nuevo sistema de
     streaming forzado por YouTube ("SABR") que rompe formatos en
     otros clientes sin un token especial (PO token).
  2) El formato pedido para el audio pasó de "m4a/bestaudio/best" a
     simplemente "bestaudio/best", para no descartar formatos
     válidos solo por no ser m4a.

v2.4: dos cambios.
  1) Se agregó "web" como segundo player_client (además de
     "android") en las tres llamadas de yt-dlp, porque con solo
     "android" algunos videos no ofrecían el formato de audio
     pedido ("Requested format is not available").
  2) Todo lo que el script imprime en pantalla (progreso, errores,
     etc.) ahora también se guarda en un log de texto en
     Descargas del celular: ~/storage/downloads/transcribir_web.log
     (se puede abrir con cualquier editor de texto o explorador de
     archivos, sin depender de sacar captura de pantalla).

v2.3: se agregó "cookiefile" (apuntando a ~/cookies.txt) a todas
  las llamadas de yt-dlp, para pasar el chequeo "Sign in to confirm
  you're not a bot" en los casos donde player_client=android por sí
  solo no alcanzó. Requiere exportar las cookies de una cuenta de
  YouTube logueada (extensión "Get cookies.txt" o similar) y
  copiarlas a ~/cookies.txt en Termux antes de correr el script.

v2.2: se agregó "player_client=android" a todas las llamadas de
  yt-dlp para esquivar el error "Sign in to confirm you're not a
  bot" que YouTube empieza a mostrar después de varias descargas
  seguidas desde la misma sesión/IP. Si esto no alcanza, el
  siguiente paso es pasar cookies de una cuenta logueada con
  --cookies-from-browser o un archivo cookies.txt.

v2.1: se corrigió una carrera de tiempos que hacía que la página
  dejara de consultar el estado para siempre. Al tocar "Transcribir",
  la página pedía el estado al mismo instante que arrancaba el
  proceso; a veces ese primer pedido llegaba una fracción de segundo
  antes de que el hilo llegara a marcar "corriendo=true", la página
  leía "no está corriendo" y cortaba el polling, aunque atrás
  siguiera transcribiendo bien. Ahora "corriendo=true" se marca
  apenas llega el pedido de iniciar (antes de arrancar el hilo), y la
  página además espera la respuesta de ese pedido antes de empezar a
  consultar el estado.

v2.0: se corrigieron dos problemas reportados con la v1.9.
  - La página no se actualizaba sola al abrirla o refrescarla: el
    log, la barra de progreso, etc. solo se cargaban al tocar
    "Transcribir". Si refrescabas el navegador (o lo volvías a
    abrir), se veía todo vacío aunque hubiera un proceso corriendo
    o recién terminado. Ahora la página consulta el estado apenas
    carga, sin esperar a que toques el botón.
  - Los archivos "desaparecían" de la lista porque en la v1.9 se
    cambió la carpeta de salida a Download, pero las transcripciones
    viejas habían quedado guardadas en la carpeta anterior (junto al
    script). No se había borrado nada, solo la interfaz miraba en
    otro lado. Ahora, al arrancar, el script migra automáticamente
    los .txt que encuentra en la carpeta vieja hacia la carpeta
    nueva en Download, así todo lo anterior vuelve a aparecer.

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

Uso: python transcribir_web_v3-0.py
     (abre solo en el navegador del celular, http://127.0.0.1:<puerto>)
"""

import glob
import json
import os
import random
import re
import socket
import subprocess
import sys
import threading
import time

import requests
import yt_dlp
from flask import Flask, jsonify, redirect, render_template_string, request

CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
VERSION = "4.3"  # se actualiza a mano en cada versión nueva del script

# --- Log a archivo, además de la pantalla -----------------------------
# Todo lo que el script imprime con print() (progreso, errores, etc.)
# se ve solo en la pantalla de Termux y se pierde al cerrar o hacer
# scroll. Esta clase "Tee" duplica esa salida también a un archivo en
# la carpeta de Descargas del celular, para poder revisarla después
# sin depender de sacar captura de pantalla.
RUTA_LOG = os.path.expanduser("~/storage/downloads/transcribir_web.log")


class _Tee:
    def __init__(self, *destinos):
        self.destinos = destinos

    def write(self, texto):
        for destino in self.destinos:
            destino.write(texto)
            destino.flush()

    def flush(self):
        for destino in self.destinos:
            destino.flush()


try:
    os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)
    _archivo_log = open(RUTA_LOG, "a", encoding="utf-8", buffering=1)
    _archivo_log.write(
        f"\n\n===== Nueva ejecución: {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n"
    )
    sys.stdout = _Tee(sys.stdout, _archivo_log)
    sys.stderr = _Tee(sys.stderr, _archivo_log)
except OSError:
    # Si por algún motivo no se puede escribir en Descargas (falta el
    # permiso de storage, por ejemplo), el script sigue andando igual,
    # solo que sin guardar el log a archivo.
    pass

_RUTA_DOWNLOADS = os.path.expanduser("~/storage/downloads")
if os.path.isdir(_RUTA_DOWNLOADS):
    CARPETA_SALIDA = os.path.join(_RUTA_DOWNLOADS, "transcripciones_mis_canales")
else:
    # Respaldo: Termux todavía no tiene permiso de almacenamiento
    # (falta correr termux-setup-storage). Se guarda junto al script
    # como antes, para no perder nada mientras tanto.
    CARPETA_SALIDA = os.path.join(CARPETA_SCRIPT, "transcripciones_mis_canales")
os.makedirs(CARPETA_SALIDA, exist_ok=True)


def _migrar_archivos_antiguos():
    """Si esta carpeta de salida es nueva (por ejemplo, porque se
    actualizó a una versión que ahora guarda en Download) y hay
    transcripciones de versiones anteriores guardadas junto al
    script, las mueve acá para que no 'desaparezcan' de la lista."""
    carpeta_antigua = os.path.join(CARPETA_SCRIPT, "transcripciones_mis_canales")
    if os.path.abspath(carpeta_antigua) == os.path.abspath(CARPETA_SALIDA):
        return
    if not os.path.isdir(carpeta_antigua):
        return
    movidos = 0
    for nombre in os.listdir(carpeta_antigua):
        if not nombre.endswith(".txt"):
            continue
        origen = os.path.join(carpeta_antigua, nombre)
        destino = os.path.join(CARPETA_SALIDA, nombre)
        if os.path.exists(destino):
            continue
        try:
            os.rename(origen, destino)
            movidos += 1
        except Exception:
            pass
    if movidos:
        print(f"📦 Se migraron {movidos} transcripción(es) de {carpeta_antigua} a {CARPETA_SALIDA}")


_migrar_archivos_antiguos()

MODELOS_DISPONIBLES = ["tiny", "small"]
MODELO_POR_DEFECTO = "tiny"
PALABRAS_MINIMAS_TEXTO = 30
PAUSA_ENTRE_VIDEOS_MIN = 15
PAUSA_ENTRE_VIDEOS_MAX = 60

# --- Descargas robustas (v3.0) ------------------------------------
# Reintentos propios del script ante fallas transitorias de yt-dlp
# (conexión reseteada, formato momentáneamente no disponible, etc.),
# además de los reintentos internos de yt-dlp por fragmento.
REINTENTOS_YTDLP = 4
ESPERA_ENTRE_REINTENTOS_SEG = 8  # crece con cada intento (backoff)

# --- Gemini: mejora de guion (v3.0) --------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODELO = os.environ.get("GEMINI_MODELO", "gemini-3.6-flash").strip()
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODELO}:generateContent"
)
GEMINI_TIMEOUT_SEG = 240  # 4 min: cubre guiones largos (videos de 30-45+ min), evita ReadTimeout en textos de miles de palabras

GEMINI_PROMPT_GENERAR = """Sos un editor de guiones en español. Te paso la transcripción cruda de un video, hecha por un modelo de reconocimiento de voz, que puede tener palabras mal reconocidas.

Tu tarea:
1. Corregí los errores de transcripción (palabras que claramente están mal reconocidas por el audio).
2. Reescribí el guion cambiando palabras (sinónimos) y la estructura de las oraciones, manteniendo EXACTAMENTE la misma historia, los mismos hechos y el mismo sentido. No inventes ni agregues información nueva.
3. Puntuá el texto pensando en que lo va a leer una voz sintética: usá comas para pausas cortas, puntos entre ideas, y evitá oraciones de más de 20 palabras.
4. Devolvé SOLO el guion final, sin comentarios, sin explicaciones, sin encabezados.

Transcripción original:
{texto}"""

GEMINI_PROMPT_REVISAR = """Sos un editor revisando un guion que vos mismo reescribiste. Releélo con ojo crítico y fijate si quedó algo raro: frases repetidas, puntuación que no ayuda a una lectura natural en voz alta, o algo que se haya alejado del sentido original. Corregí lo que haga falta.

Devolvé SOLO la versión final pulida del guion, sin comentarios ni explicaciones.

Guion a revisar:
{texto}"""

# El historial vive en una carpeta FIJA (Download), separada de
# CARPETA_SCRIPT, para que sobreviva sin importar dónde se guarde o
# reemplace el archivo .py en cada nueva versión del script. Si en
# algún momento no existe Download (falta termux-setup-storage), se
# usa la carpeta del script solo como respaldo temporal.
_RUTA_DATOS_FIJA = os.path.join(_RUTA_DOWNLOADS, "transcribir_web_datos")
if os.path.isdir(_RUTA_DOWNLOADS):
    os.makedirs(_RUTA_DATOS_FIJA, exist_ok=True)
    HISTORIAL_ARCHIVO = os.path.join(_RUTA_DATOS_FIJA, "historial_canales.json")
else:
    HISTORIAL_ARCHIVO = os.path.join(CARPETA_SCRIPT, "historial_canales.json")

# Sin límite: se guardan todos los canales usados, para siempre.


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
    toque en vez de volver a pegarlo. No hay límite de cantidad: todo
    lo usado queda guardado para siempre."""
    entrada = entrada.strip()
    historial = [h for h in _cargar_historial() if h != entrada]
    historial.insert(0, entrada)
    try:
        with open(HISTORIAL_ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"⚠️  No se pudo guardar el historial: {e}")


def _migrar_historial_antiguo():
    """Si en una versión anterior el historial quedó guardado junto
    al script (ruta vieja) y todavía no existe en la carpeta fija
    nueva, lo copia para no perder los canales ya guardados."""
    ruta_vieja = os.path.join(CARPETA_SCRIPT, "historial_canales.json")
    if os.path.abspath(ruta_vieja) == os.path.abspath(HISTORIAL_ARCHIVO):
        return
    if os.path.exists(HISTORIAL_ARCHIVO) or not os.path.exists(ruta_vieja):
        return
    try:
        with open(ruta_vieja, "r", encoding="utf-8") as f:
            historial_viejo = json.load(f)
        with open(HISTORIAL_ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(historial_viejo, f, ensure_ascii=False, indent=2)
        print(f"📦 Se migró el historial de canales de {ruta_vieja} a {HISTORIAL_ARCHIVO}")
    except Exception:
        pass


_migrar_historial_antiguo()

# --- Descargar gameplay (v4.0) --------------------------------------
if os.path.isdir(_RUTA_DOWNLOADS):
    CARPETA_GAMEPLAY = os.path.join(_RUTA_DOWNLOADS, "gameplay_descargado")
else:
    CARPETA_GAMEPLAY = os.path.join(CARPETA_SCRIPT, "gameplay_descargado")
os.makedirs(CARPETA_GAMEPLAY, exist_ok=True)

CALIDAD_MAXIMA_GAMEPLAY = 720  # alto máximo en píxeles

HISTORIAL_GAMEPLAY_ARCHIVO = os.path.join(_RUTA_DATOS_FIJA if os.path.isdir(_RUTA_DOWNLOADS) else CARPETA_SCRIPT, "historial_canales_gameplay.json")


def _cargar_historial_gameplay():
    if not os.path.exists(HISTORIAL_GAMEPLAY_ARCHIVO):
        return []
    try:
        with open(HISTORIAL_GAMEPLAY_ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _guardar_en_historial_gameplay(entrada):
    entrada = entrada.strip()
    historial = [h for h in _cargar_historial_gameplay() if h != entrada]
    historial.insert(0, entrada)
    try:
        with open(HISTORIAL_GAMEPLAY_ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"⚠️  No se pudo guardar el historial de gameplay: {e}")


def _sanear_nombre_archivo(texto, largo_maximo=80):
    """Saca caracteres problemáticos para nombre de archivo/carpeta
    (barras, dos puntos, etc.) y recorta si es muy largo."""
    texto = re.sub(r'[\\/:*?"<>|]+', "", texto).strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto[:largo_maximo] if texto else "sin_titulo"


def _video_ya_descargado_gameplay(carpeta_canal, video_id):
    patron = os.path.join(carpeta_canal, f"{video_id}__*")
    return len(glob.glob(patron)) > 0


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

# --- Estado propio de la pestaña "Descargar gameplay" (v4.0) --------
# Separado del ESTADO de transcripción para que cada pestaña tenga su
# propio log/progreso independiente.
ESTADO_GAMEPLAY = {
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
CANDADO_GAMEPLAY = threading.Lock()


def log_gp(msg):
    print(msg)
    with CANDADO_GAMEPLAY:
        ESTADO_GAMEPLAY["log"].append(msg)


def _actualizar_etapa_gp(etapa, pct=None):
    with CANDADO_GAMEPLAY:
        ESTADO_GAMEPLAY["etapa"] = etapa
        ESTADO_GAMEPLAY["etapa_pct"] = pct


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


def _con_reintentos(func, descripcion):
    """Ejecuta func() reintentando ante fallas transitorias (conexión
    reseteada, formato momentáneamente no disponible, etc.), con una
    espera creciente entre intento e intento. Relanza el último error
    si se agotan los reintentos."""
    ultimo_error = None
    for intento in range(1, REINTENTOS_YTDLP + 1):
        try:
            return func()
        except Exception as e:
            ultimo_error = e
            if intento < REINTENTOS_YTDLP:
                espera = ESPERA_ENTRE_REINTENTOS_SEG * intento
                log(f"    ⚠️  {descripcion} falló (intento {intento}/{REINTENTOS_YTDLP}): "
                    f"{type(e).__name__}: {e}. Reintentando en {espera}s...")
                time.sleep(espera)
            else:
                log(f"    ❌ {descripcion} falló definitivamente tras {REINTENTOS_YTDLP} intentos.")
    raise ultimo_error


def descargar_audio(video_url, nombre_salida, progreso_cb=None):
    def _hook(d):
        if not progreso_cb or d.get("status") != "downloading":
            return
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        descargado = d.get("downloaded_bytes")
        if total and descargado:
            progreso_cb(min(100, int(descargado / total * 100)))

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": nombre_salida,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [_hook] if progreso_cb else [],
        # Usar el cliente "android" de YouTube en vez del "web" para
        # esquivar el chequeo de "Sign in to confirm you're not a bot"
        # que empieza a aparecer después de varias descargas seguidas.
        "extractor_args": {"youtube": {"player_client": ["tv", "android", "web"]}},
        # Cookies de una cuenta de YouTube logueada, exportadas con
        # una extensión tipo "Get cookies.txt" y copiadas a
        # ~/cookies.txt en Termux. Sin esto, el chequeo de bot puede
        # seguir apareciendo aunque se use player_client=android.
        "cookiefile": os.path.expanduser("~/cookies.txt"),
        # YouTube exige resolver un desafío de JavaScript ("n
        # challenge") antes de entregar formatos de audio/video de
        # verdad; sin esto solo devuelve miniaturas (sb0-sb3) y
        # falla con "Requested format is not available". Node ya
        # tiene que estar instalado en Termux (pkg install nodejs).
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
        # --- Descargas robustas (v3.0) ---
        # Reintentos internos de yt-dlp ante cortes de red durante
        # la descarga de un fragmento puntual (además del reintento
        # de la llamada completa que hace _con_reintentos más abajo).
        "retries": 5,
        "fragment_retries": 5,
        "retry_sleep_functions": {"http": lambda n: min(4 * (n + 1), 20)},
        # Ritmo de descarga: pequeñas pausas para no parecer tráfico
        # automatizado desde el arranque (anticiparse al bloqueo, en
        # vez de solo reaccionar cuando ya empezó).
        "sleep_interval_requests": 2,
        "sleep_interval": 1,
        "max_sleep_interval": 5,
    }

    def _descargar():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

    _con_reintentos(_descargar, "Descarga de audio")


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
        "extractor_args": {"youtube": {"player_client": ["tv", "android", "web"]}},
        "cookiefile": os.path.expanduser("~/cookies.txt"),
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
        "retries": 5,
        "sleep_interval_requests": 1,
    }

    def _listar():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url_videos, download=False)

    info = _con_reintentos(_listar, "Listado de videos del canal")

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


def _obtener_orientacion_video(video_id):
    """Consulta la resolución real de un video puntual (sin
    descargarlo) para saber si es vertical (alto > ancho) u
    horizontal. Devuelve (es_vertical, ancho, alto); si no se puede
    determinar, devuelve (None, None, None) y el llamador decide qué
    hacer (por las dudas, se saltea)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["tv", "android", "web"]}},
        "cookiefile": os.path.expanduser("~/cookies.txt"),
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
        "retries": 3,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        ancho, alto = info.get("width"), info.get("height")
        if not ancho or not alto:
            return None, None, None
        return alto > ancho, ancho, alto
    except Exception:
        return None, None, None


def obtener_videos_canal_por_orientacion(url_canal, max_videos, nombre_canal, carpeta_canal, orientacion):
    """Como obtener_videos_canal, pero para la pestaña de gameplay:
    filtra por orientación ("vertical" u "horizontal"), saltea
    Shorts y los que ya estén descargados. De paso, cuenta cuántos
    videos de cada orientación encontró entre TODOS los revisados
    (no solo los que matchean el filtro pedido), para poder
    informarlo en el log. Como hay que consultar la resolución real
    de cada candidato (un pedido extra por video), es más lento que
    listar para transcripción."""
    url_videos = url_canal.rstrip("/")
    if not url_videos.endswith("/videos"):
        url_videos += "/videos"

    ydl_opts = {
        "extract_flat": True,
        "playlistend": max(max_videos * 8, 30),
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {"player_client": ["tv", "android", "web"]},
            # Sin esto, yt-dlp rechaza listar canales AJENOS (no el
            # dueño de ~/cookies.txt) con "Playlists that require
            # authentication may not extract correctly...". Es
            # esperable: las cookies son de tu cuenta, no de la del
            # canal de gameplay. skip=authcheck le dice a yt-dlp que
            # igual intente listar sin ese chequeo extra.
            "youtubetab": {"skip": ["authcheck"]},
        },
        "cookiefile": os.path.expanduser("~/cookies.txt"),
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
        "retries": 5,
        "sleep_interval_requests": 1,
    }

    def _listar():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url_videos, download=False)

    info = _con_reintentos(_listar, "Listado de videos del canal (gameplay)")

    entradas = (info or {}).get("entries") or []
    quiere_vertical = orientacion == "vertical"
    videos = []
    contador_vertical = 0
    contador_horizontal = 0
    saltados_ya_descargados = 0
    for entrada in entradas:
        url_entrada = entrada.get("url") or entrada.get("webpage_url") or ""
        if "/shorts/" in url_entrada:
            continue

        duracion = entrada.get("duration")
        if duracion is not None and duracion <= 60:
            continue

        video_id = entrada.get("id")
        es_vertical, ancho, alto = _obtener_orientacion_video(video_id)
        if es_vertical is None:
            continue  # no se pudo determinar la resolución; no cuenta en ningún lado
        if es_vertical:
            contador_vertical += 1
        else:
            contador_horizontal += 1

        if len(videos) >= max_videos:
            continue  # ya se juntaron suficientes, pero se sigue contando el resto del lote

        coincide = es_vertical if quiere_vertical else not es_vertical
        if not coincide:
            continue

        if _video_ya_descargado_gameplay(carpeta_canal, video_id):
            saltados_ya_descargados += 1
            continue

        titulo = entrada.get("title") or video_id
        videos.append({
            "videoId": video_id,
            "titulo": titulo,
            "duration": duracion,
        })
    return videos, contador_vertical, contador_horizontal, saltados_ya_descargados


def contar_videos_canal(url_canal, limite=60):
    """Recorre el canal y cuenta cuántos videos recientes son
    verticales y cuántos horizontales, SIN descargar nada y sin
    filtrar por ya descargados: es solo un conteo informativo, para
    saber qué hay antes de elegir cuántos pedir con los botones de
    descarga. 'limite' es cuántos videos del canal se revisan (no
    todo el historial, sería demasiado pedir la resolución de cada
    uno)."""
    url_videos = url_canal.rstrip("/")
    if not url_videos.endswith("/videos"):
        url_videos += "/videos"

    ydl_opts = {
        "extract_flat": True,
        "playlistend": limite,
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {"player_client": ["tv", "android", "web"]},
            "youtubetab": {"skip": ["authcheck"]},
        },
        "cookiefile": os.path.expanduser("~/cookies.txt"),
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
        "retries": 5,
        "sleep_interval_requests": 1,
    }

    def _listar():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url_videos, download=False)

    info = _con_reintentos(_listar, "Listado de videos del canal (conteo)")

    entradas = (info or {}).get("entries") or []
    contador_vertical = 0
    contador_horizontal = 0
    revisados = 0
    for entrada in entradas:
        url_entrada = entrada.get("url") or entrada.get("webpage_url") or ""
        if "/shorts/" in url_entrada:
            continue
        duracion = entrada.get("duration")
        if duracion is not None and duracion <= 60:
            continue
        video_id = entrada.get("id")
        es_vertical, ancho, alto = _obtener_orientacion_video(video_id)
        if es_vertical is None:
            continue
        revisados += 1
        if es_vertical:
            contador_vertical += 1
        else:
            contador_horizontal += 1
    return contador_vertical, contador_horizontal, revisados


def descargar_video_gameplay(video_url, nombre_salida, progreso_cb=None):
    """Baja el video COMPLETO (no solo audio), limitado a
    CALIDAD_MAXIMA_GAMEPLAY de alto, en mp4. Sirve tanto para
    vertical como horizontal: el filtro de orientación ya se aplicó
    antes, al elegir qué videos entran en la lista."""
    def _hook(d):
        if not progreso_cb or d.get("status") != "downloading":
            return
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        descargado = d.get("downloaded_bytes")
        if total and descargado:
            progreso_cb(min(100, int(descargado / total * 100)))

    formato = f"bestvideo[height<={CALIDAD_MAXIMA_GAMEPLAY}]+bestaudio/best[height<={CALIDAD_MAXIMA_GAMEPLAY}]/best"
    ydl_opts = {
        "format": formato,
        "merge_output_format": "mp4",
        "outtmpl": nombre_salida,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [_hook] if progreso_cb else [],
        "extractor_args": {"youtube": {"player_client": ["tv", "android", "web"]}},
        "cookiefile": os.path.expanduser("~/cookies.txt"),
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
        "retries": 5,
        "fragment_retries": 5,
        "retry_sleep_functions": {"http": lambda n: min(4 * (n + 1), 20)},
        "sleep_interval_requests": 2,
        "sleep_interval": 1,
        "max_sleep_interval": 5,
    }

    def _descargar():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

    _con_reintentos(_descargar, "Descarga de video (gameplay)")


def procesar_video_gameplay(video, nombre_canal, carpeta_canal, orientacion):
    video_id = video["videoId"]
    titulo = video["titulo"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    nombre_archivo = f"{video_id}__{orientacion}__{_sanear_nombre_archivo(titulo)}.mp4"
    ruta_salida = os.path.join(carpeta_canal, nombre_archivo)

    log_gp(f"  → {titulo}")

    try:
        log_gp(f"    Descargando video (720p, {orientacion})...")
        _actualizar_etapa_gp("Descargando video", 0)
        descargar_video_gameplay(
            video_url, ruta_salida,
            progreso_cb=lambda pct: _actualizar_etapa_gp("Descargando video", pct),
        )
        tamano_mb = round(os.path.getsize(ruta_salida) / (1024 * 1024), 1) if os.path.exists(ruta_salida) else 0
        log_gp(f"    ✅ Guardado en {nombre_canal}/ ({tamano_mb} MB).")
    except Exception as e:
        log_gp(f"    ❌ Error: {type(e).__name__}: {e}")
    finally:
        _actualizar_etapa_gp(None, None)


def procesar_canal_gameplay_en_hilo(entrada_canal, max_videos, orientacion):
    with CANDADO_GAMEPLAY:
        ESTADO_GAMEPLAY["corriendo"] = True
        ESTADO_GAMEPLAY["terminado"] = False
        ESTADO_GAMEPLAY["log"] = []
        ESTADO_GAMEPLAY["canal"] = entrada_canal
        ESTADO_GAMEPLAY["video_actual"] = 0
        ESTADO_GAMEPLAY["total_videos"] = 0
        ESTADO_GAMEPLAY["tiempos_videos"] = []
        ESTADO_GAMEPLAY["etapa"] = None
        ESTADO_GAMEPLAY["etapa_pct"] = None
        ESTADO_GAMEPLAY["pausa_restante_seg"] = None

    try:
        url, nombre_canal = _extraer_nombre_canal(entrada_canal)
        carpeta_canal = os.path.join(CARPETA_GAMEPLAY, nombre_canal)
        os.makedirs(carpeta_canal, exist_ok=True)

        log_gp(f"=== Canal: {nombre_canal} (gameplay, {orientacion}, 720p) ===")
        log_gp("Buscando videos nuevos del canal...")
        videos, contador_vertical, contador_horizontal, saltados_ya_descargados = obtener_videos_canal_por_orientacion(
            url, max_videos, nombre_canal, carpeta_canal, orientacion
        )
        log_gp(f"  Entre los revisados: {contador_vertical} vertical(es), {contador_horizontal} horizontal(es).")
        if saltados_ya_descargados:
            log_gp(f"  {saltados_ya_descargados} video(s) ya estaban descargados antes, se saltearon.")
        log_gp(f"Nuevos a descargar ({orientacion}): {len(videos)}")

        with CANDADO_GAMEPLAY:
            ESTADO_GAMEPLAY["total_videos"] = len(videos)

        for i, video in enumerate(videos, 1):
            if i > 1:
                pausa = random.uniform(PAUSA_ENTRE_VIDEOS_MIN, PAUSA_ENTRE_VIDEOS_MAX)
                log_gp(f"(pausa de {pausa:.0f}s antes de descargar el próximo video...)")
                fin_pausa = time.time() + pausa
                while True:
                    restante = fin_pausa - time.time()
                    if restante <= 0:
                        break
                    with CANDADO_GAMEPLAY:
                        ESTADO_GAMEPLAY["pausa_restante_seg"] = restante
                    time.sleep(min(1, restante))
                with CANDADO_GAMEPLAY:
                    ESTADO_GAMEPLAY["pausa_restante_seg"] = None
            log_gp(f"[{i}/{len(videos)}]")
            with CANDADO_GAMEPLAY:
                ESTADO_GAMEPLAY["video_actual"] = i
            inicio_video = time.time()
            procesar_video_gameplay(video, nombre_canal, carpeta_canal, orientacion)
            with CANDADO_GAMEPLAY:
                ESTADO_GAMEPLAY["tiempos_videos"].append(time.time() - inicio_video)

        log_gp("=== Listo ===")

    except Exception as e:
        log_gp(f"❌ Error general: {type(e).__name__}: {e}")

    finally:
        with CANDADO_GAMEPLAY:
            ESTADO_GAMEPLAY["corriendo"] = False
            ESTADO_GAMEPLAY["terminado"] = True


def procesar_conteo_gameplay_en_hilo(entrada_canal):
    """Como procesar_canal_gameplay_en_hilo, pero solo cuenta (no
    descarga nada). Reutiliza el mismo ESTADO_GAMEPLAY/log/polling
    que ya tiene la pestaña, para no duplicar infraestructura."""
    with CANDADO_GAMEPLAY:
        ESTADO_GAMEPLAY["corriendo"] = True
        ESTADO_GAMEPLAY["terminado"] = False
        ESTADO_GAMEPLAY["log"] = []
        ESTADO_GAMEPLAY["canal"] = entrada_canal
        ESTADO_GAMEPLAY["video_actual"] = 0
        ESTADO_GAMEPLAY["total_videos"] = 0
        ESTADO_GAMEPLAY["tiempos_videos"] = []
        ESTADO_GAMEPLAY["etapa"] = None
        ESTADO_GAMEPLAY["etapa_pct"] = None
        ESTADO_GAMEPLAY["pausa_restante_seg"] = None

    try:
        url, nombre_canal = _extraer_nombre_canal(entrada_canal)
        log_gp(f"=== Canal: {nombre_canal} (solo conteo) ===")
        log_gp("Revisando videos del canal (esto no descarga nada)...")
        contador_vertical, contador_horizontal, revisados = contar_videos_canal(url)
        log_gp(f"  Entre los revisados: {contador_vertical} vertical(es), {contador_horizontal} horizontal(es).")
        log_gp("=== Listo ===")

    except Exception as e:
        log_gp(f"❌ Error general: {type(e).__name__}: {e}")

    finally:
        with CANDADO_GAMEPLAY:
            ESTADO_GAMEPLAY["corriendo"] = False
            ESTADO_GAMEPLAY["terminado"] = True


def obtener_info_video_individual(url_video):
    """Trae los datos de UN solo video a partir de su link directo,
    para el modo 'forzar re-transcripción con otro modelo'."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["tv", "android", "web"]}},
        "cookiefile": os.path.expanduser("~/cookies.txt"),
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
        "retries": 5,
    }

    def _info():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url_video, download=False)

    info = _con_reintentos(_info, "Obtener info del video")

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


def _llamar_gemini(prompt):
    """Llama a la API de Gemini (REST, generateContent) con un solo
    prompt de texto y devuelve la respuesta como string. Lanza una
    excepción si falla la llamada o si la respuesta viene vacía
    (por ejemplo, si el modelo la bloqueó por seguridad)."""
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(GEMINI_URL, headers=headers, json=body, timeout=GEMINI_TIMEOUT_SEG)
    resp.raise_for_status()
    data = resp.json()
    candidatos = data.get("candidates") or []
    if not candidatos:
        raise ValueError(f"Gemini no devolvió candidatos: {data}")
    partes = candidatos[0].get("content", {}).get("parts") or []
    texto = "".join(p.get("text", "") for p in partes).strip()
    if not texto:
        raise ValueError(f"Gemini devolvió una respuesta vacía: {data}")
    return texto


def mejorar_guion_con_gemini(texto_original):
    """Flujo de 2 pasadas (v3.0): 1) corrige errores de transcripción,
    parafrasea y puntúa para lectura en voz alta; 2) relee y pule ese
    resultado. Si algo falla en cualquiera de las dos pasadas (sin
    API key, sin conexión, error de la API), devuelve el texto
    original de whisper.cpp sin cortar el proceso."""
    if not GEMINI_API_KEY:
        log("    ℹ️  Sin GEMINI_API_KEY configurada: se guarda el texto de whisper.cpp tal cual.")
        return texto_original, False

    try:
        _actualizar_etapa("Mejorando guion con Gemini (1/2)", None)
        borrador = _llamar_gemini(GEMINI_PROMPT_GENERAR.format(texto=texto_original))

        _actualizar_etapa("Mejorando guion con Gemini (2/2)", None)
        final = _llamar_gemini(GEMINI_PROMPT_REVISAR.format(texto=borrador))

        return final, True
    except Exception as e:
        log(f"    ⚠️  Falló la mejora con Gemini ({type(e).__name__}: {e}). "
            "Se guarda el texto de whisper.cpp tal cual.")
        return texto_original, False


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

        log("    Mejorando guion con Gemini (corrección + parafraseo + puntuación)...")
        texto_final, mejorado_con_gemini = mejorar_guion_con_gemini(texto)

        with open(txt_salida, "w", encoding="utf-8") as f:
            f.write(f"CANAL: {nombre_canal}\nTÍTULO: {titulo}\nURL: {video_url}\nMODELO: {nombre_modelo}\n{'=' * 60}\n\n")
            f.write(texto_final)

        if mejorado_con_gemini:
            # Se guarda también el texto crudo de whisper.cpp aparte,
            # por si hace falta comparar contra lo que armó Gemini.
            ruta_original = txt_salida.replace(".txt", "__original.txt")
            with open(ruta_original, "w", encoding="utf-8") as f:
                f.write(f"CANAL: {nombre_canal}\nTÍTULO: {titulo}\nURL: {video_url}\nMODELO: {nombre_modelo}\n{'=' * 60}\n\n")
                f.write(texto)
            log(f"    ✅ Guardado ({n_palabras} palabras originales) — guion mejorado con Gemini.")
        else:
            log(f"    ✅ Guardado ({n_palabras} palabras).")

    except Exception as e:
        log(f"    ❌ Error: {type(e).__name__}: {e}")

    finally:
        _actualizar_etapa(None, None)
        for temp_file in (temp_audio, temp_wav):
            if os.path.exists(temp_file):
                os.remove(temp_file)


def _extraer_nombre_canal(entrada):
    """Acepta link completo (incluyendo el de 'Compartir canal', que
    trae un ?si=... de tracking pegado al final), solo el @usuario,
    o cualquiera de los dos con texto extra pegado alrededor (ej. el
    nombre del canal). Devuelve (url_base_sin_query,
    nombre_para_archivos). La query (?si=...) se descarta: si no se
    quita antes de agregar '/videos' más adelante, queda pegada
    DENTRO de la query string y la URL final es inválida (404)."""
    entrada = entrada.strip()

    m = re.search(r"https?://\S+", entrada)
    if m:
        url = m.group(0)
    else:
        m = re.search(r"@[\w.\-]+", entrada)
        if m:
            url = f"https://youtube.com/{m.group(0)}"
        else:
            token = entrada.split()[0] if entrada.split() else entrada
            url = f"https://youtube.com/@{token}"

    url = url.split("?")[0].rstrip("/")  # se descarta el ?si=... y similares
    nombre = url.split("@")[-1] if "@" in url else url.split("/")[-1]
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
.archivo_canal { color: #555; font-size: 12px; white-space: nowrap; }

#tabs { display: flex; gap: 6px; margin-bottom: 14px; }
.tab_btn {
    flex: 1; padding: 10px; font-size: 14px; text-align: center; cursor: pointer;
    background: #eee; color: #333; border: 1px solid #ccc; border-radius: 6px; width: auto;
}
.tab_btn.activa { background: #333; color: white; border-color: #333; }
#conteo_orientacion_gp { font-size: 13px; color: #555; margin: -4px 0 10px; min-height: 16px; }
</style>
</head>
<body>
<div id="tabs">
    <button type="button" class="tab_btn activa" id="tab_btn_transcribir" onclick="mostrarTab('transcribir')">🎙️ Transcribir</button>
    <button type="button" class="tab_btn" id="tab_btn_gameplay" onclick="mostrarTab('gameplay')">🎮 Descargar gameplay</button>
</div>

<div id="tab_transcribir">
<h2>Transcribir mis videos <small style="font-weight:normal;color:#888;">v{{ version }}</small></h2>
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
</div>

<div id="tab_gameplay" style="display:none">
<h2>Descargar gameplay <small style="font-weight:normal;color:#888;">v{{ version }}</small></h2>
<p>Pegá el link o @usuario del canal. Baja los videos VERTICALES (9:16) más recientes, en 720p, uno por uno, guardados en su propia carpeta (nombre del canal) para dar crédito.</p>
<input id="canal_gp" placeholder="https://youtube.com/@CanalDeGameplay o @CanalDeGameplay">
<div id="historial_contenedor_gp"></div>
<input id="max_videos_gp" type="number" value="2" min="1" placeholder="Cantidad de videos">
<div id="conteo_orientacion_gp"></div>
<button id="btn_gp_v" onclick="iniciarGameplay('vertical')">Descargar verticales</button>
<button id="btn_gp_h" onclick="iniciarGameplay('horizontal')">Descargar horizontales</button>
<button id="btn_gp_c" onclick="iniciarConteoGameplay()">Contar videos</button>
<div id="progreso_contenedor_gp">
    <div id="progreso_barra_fondo_gp"><div id="progreso_barra_gp"></div></div>
    <div id="progreso_texto_gp"></div>
</div>
<div id="etapa_contenedor_gp">
    <div id="etapa_barra_fondo_gp"><div id="etapa_barra_gp"></div></div>
    <div id="etapa_texto_gp"></div>
</div>
<div id="pausa_texto_gp"></div>
<div id="log_gp"></div>

<div id="archivos_seccion_gp">
    <div id="archivos_titulo">📁 Videos ya descargados</div>
    <div id="archivos_lista_gp"></div>
</div>
</div>

<script>
function mostrarTab(nombre) {
    document.getElementById('tab_transcribir').style.display = (nombre === 'transcribir') ? 'block' : 'none';
    document.getElementById('tab_gameplay').style.display = (nombre === 'gameplay') ? 'block' : 'none';
    document.getElementById('tab_btn_transcribir').classList.toggle('activa', nombre === 'transcribir');
    document.getElementById('tab_btn_gameplay').classList.toggle('activa', nombre === 'gameplay');
}

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
    }).then(() => {
        // Recién acá, con la respuesta del POST ya recibida (y por lo
        // tanto "corriendo=true" ya garantizado del lado del backend),
        // arranca el polling. Antes se llamaba a actualizar() en
        // paralelo al fetch, sin esperarlo, lo que podía ganarle la
        // carrera y cortar el polling para siempre.
        cargarHistorial();
        actualizar();
    });
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
window.addEventListener('DOMContentLoaded', actualizar);

function iniciarGameplay(orientacion) {
    const canal = document.getElementById('canal_gp').value.trim();
    const max_videos = document.getElementById('max_videos_gp').value || 2;
    if (!canal) { alert('Pegá un canal primero.'); return; }
    document.getElementById('btn_gp_v').disabled = true;
    document.getElementById('btn_gp_h').disabled = true;
    document.getElementById('btn_gp_c').disabled = true;
    document.getElementById('conteo_orientacion_gp').textContent = '';
    fetch('/iniciar_gameplay', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({canal: canal, max_videos: max_videos, orientacion: orientacion})
    }).then(() => {
        cargarHistorialGameplay();
        actualizarGameplay();
    });
}

function iniciarConteoGameplay() {
    const canal = document.getElementById('canal_gp').value.trim();
    if (!canal) { alert('Pegá un canal primero.'); return; }
    document.getElementById('btn_gp_v').disabled = true;
    document.getElementById('btn_gp_h').disabled = true;
    document.getElementById('btn_gp_c').disabled = true;
    document.getElementById('conteo_orientacion_gp').textContent = '';
    fetch('/contar_gameplay', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({canal: canal})
    }).then(() => {
        cargarHistorialGameplay();
        actualizarGameplay();
    });
}

function cargarHistorialGameplay() {
    fetch('/historial_gameplay').then(r => r.json()).then(lista => {
        const cont = document.getElementById('historial_contenedor_gp');
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
            chip.onclick = () => { document.getElementById('canal_gp').value = item; };
            cont.appendChild(chip);
        });
    });
}

function cargarArchivosGameplay() {
    fetch('/archivos_gameplay').then(r => r.json()).then(lista => {
        const cont = document.getElementById('archivos_lista_gp');
        cont.innerHTML = '';
        if (!lista.length) {
            cont.innerHTML = '<div class="archivo_item"><span class="archivo_nombre">Todavía no hay videos.</span></div>';
            return;
        }
        lista.forEach(a => {
            const item = document.createElement('div');
            item.className = 'archivo_item';
            item.innerHTML = `<span class="archivo_nombre">${a.nombre}</span><span class="archivo_canal">${a.canal}</span><span class="archivo_meta">${a.tamano_mb} MB · ${a.fecha}</span>`;
            cont.appendChild(item);
        });
    });
}

window.addEventListener('DOMContentLoaded', cargarHistorialGameplay);
window.addEventListener('DOMContentLoaded', cargarArchivosGameplay);
window.addEventListener('DOMContentLoaded', actualizarGameplay);

function actualizarGameplay() {
    fetch('/estado_gameplay').then(r => r.json()).then(data => {
        document.getElementById('log_gp').textContent = data.log.join('\\n');
        document.getElementById('log_gp').scrollTop = 999999;

        const lineaConteo = data.log.find(l => l.includes('Entre los revisados:'));
        document.getElementById('conteo_orientacion_gp').textContent = lineaConteo ? lineaConteo.trim() : '';

        const contenedor = document.getElementById('progreso_contenedor_gp');
        if (data.total_videos > 0) {
            contenedor.style.display = 'block';
            const pct = Math.round((data.video_actual / data.total_videos) * 100);
            document.getElementById('progreso_barra_gp').style.width = pct + '%';
            let texto = `Video ${data.video_actual} de ${data.total_videos} (${pct}%)`;
            if (data.tiempo_restante_seg != null) {
                texto += ` — tiempo restante estimado: ${formatearTiempo(data.tiempo_restante_seg)}`;
            }
            document.getElementById('progreso_texto_gp').textContent = texto;
        } else {
            contenedor.style.display = 'none';
        }

        const etapaContenedor = document.getElementById('etapa_contenedor_gp');
        const etapaBarra = document.getElementById('etapa_barra_gp');
        if (data.etapa) {
            etapaContenedor.style.display = 'block';
            if (data.etapa_pct == null) {
                etapaBarra.classList.add('indeterminado');
                etapaBarra.style.width = '';
                document.getElementById('etapa_texto_gp').textContent = data.etapa + '...';
            } else {
                etapaBarra.classList.remove('indeterminado');
                etapaBarra.style.width = data.etapa_pct + '%';
                document.getElementById('etapa_texto_gp').textContent = `${data.etapa} — ${data.etapa_pct}%`;
            }
        } else {
            etapaContenedor.style.display = 'none';
        }

        const pausaTexto = document.getElementById('pausa_texto_gp');
        if (data.pausa_restante_seg != null) {
            pausaTexto.style.display = 'block';
            pausaTexto.textContent = `⏳ Próxima descarga en ${formatearTiempo(data.pausa_restante_seg)}`;
        } else {
            pausaTexto.style.display = 'none';
        }

        if (data.corriendo) {
            const intervalo = (data.pausa_restante_seg != null) ? 1000 : 2000;
            setTimeout(actualizarGameplay, intervalo);
        } else {
            document.getElementById('btn_gp_v').disabled = false;
            document.getElementById('btn_gp_h').disabled = false;
            document.getElementById('btn_gp_c').disabled = false;
            cargarArchivosGameplay();
        }
    });
}

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
    return render_template_string(PAGINA, version=VERSION)


@app.route("/iniciar", methods=["POST"])
def _iniciar():
    with CANDADO:
        if ESTADO["corriendo"]:
            return jsonify({"error": "Ya hay una transcripción en curso"}), 409
        # Se marca "corriendo" ACÁ, antes de arrancar el hilo, para que
        # cuando la página reciba la respuesta de este POST el estado
        # ya diga "corriendo=true" con seguridad. Si se marcara recién
        # dentro del hilo, existía una carrera: la página podía
        # consultar /estado una fracción de segundo antes de que el
        # hilo llegara a esa línea, ver "corriendo=false" y dejar de
        # consultar para siempre (aunque atrás siguiera transcribiendo).
        ESTADO["corriendo"] = True
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
            # Los .txt de respaldo con el texto crudo de whisper.cpp
            # (guardados junto al guion mejorado por Gemini) no se
            # listan acá, para no duplicar cada video en la lista.
            if nombre.endswith("__original.txt"):
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


@app.route("/iniciar_gameplay", methods=["POST"])
def _iniciar_gameplay():
    with CANDADO_GAMEPLAY:
        if ESTADO_GAMEPLAY["corriendo"]:
            return jsonify({"error": "Ya hay una descarga de gameplay en curso"}), 409
        ESTADO_GAMEPLAY["corriendo"] = True
    datos = request.get_json(force=True)
    canal = datos.get("canal", "").strip()
    max_videos = int(datos.get("max_videos", 2))
    orientacion = datos.get("orientacion", "vertical")
    if orientacion not in ("vertical", "horizontal"):
        orientacion = "vertical"
    if not canal:
        return jsonify({"error": "Falta el canal"}), 400
    _guardar_en_historial_gameplay(canal)
    threading.Thread(target=procesar_canal_gameplay_en_hilo, args=(canal, max_videos, orientacion), daemon=True).start()
    return jsonify({"ok": True})


@app.route("/contar_gameplay", methods=["POST"])
def _contar_gameplay():
    with CANDADO_GAMEPLAY:
        if ESTADO_GAMEPLAY["corriendo"]:
            return jsonify({"error": "Ya hay una descarga o conteo de gameplay en curso"}), 409
        ESTADO_GAMEPLAY["corriendo"] = True
    datos = request.get_json(force=True)
    canal = datos.get("canal", "").strip()
    if not canal:
        return jsonify({"error": "Falta el canal"}), 400
    _guardar_en_historial_gameplay(canal)
    threading.Thread(target=procesar_conteo_gameplay_en_hilo, args=(canal,), daemon=True).start()
    return jsonify({"ok": True})


@app.route("/historial_gameplay")
def _historial_gameplay():
    return jsonify(_cargar_historial_gameplay())


@app.route("/archivos_gameplay")
def _archivos_gameplay():
    """Lista los .mp4 ya descargados (nombre, canal, tamaño, fecha),
    recorriendo todas las carpetas de canal dentro de CARPETA_GAMEPLAY."""
    archivos = []
    try:
        for nombre_canal in os.listdir(CARPETA_GAMEPLAY):
            carpeta_canal = os.path.join(CARPETA_GAMEPLAY, nombre_canal)
            if not os.path.isdir(carpeta_canal):
                continue
            for nombre in os.listdir(carpeta_canal):
                if not nombre.endswith(".mp4"):
                    continue
                ruta = os.path.join(carpeta_canal, nombre)
                archivos.append({
                    "nombre": nombre,
                    "canal": nombre_canal,
                    "tamano_mb": round(os.path.getsize(ruta) / (1024 * 1024), 1),
                    "mtime": os.path.getmtime(ruta),
                })
        archivos.sort(key=lambda a: a["mtime"], reverse=True)
        for a in archivos:
            a["fecha"] = time.strftime("%d/%m %H:%M", time.localtime(a.pop("mtime")))
    except Exception as e:
        log_gp(f"⚠️  No se pudo listar archivos de gameplay: {e}")
    return jsonify(archivos)


@app.route("/estado_gameplay")
def _estado_gameplay():
    with CANDADO_GAMEPLAY:
        tiempos = list(ESTADO_GAMEPLAY["tiempos_videos"])
        video_actual = ESTADO_GAMEPLAY["video_actual"]
        total_videos = ESTADO_GAMEPLAY["total_videos"]
        respuesta = {
            "corriendo": ESTADO_GAMEPLAY["corriendo"],
            "log": list(ESTADO_GAMEPLAY["log"]),
            "video_actual": video_actual,
            "total_videos": total_videos,
            "tiempo_restante_seg": None,
            "etapa": ESTADO_GAMEPLAY["etapa"],
            "etapa_pct": ESTADO_GAMEPLAY["etapa_pct"],
            "pausa_restante_seg": ESTADO_GAMEPLAY["pausa_restante_seg"],
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
    print(f"\n*** Transcribir mis videos — Interfaz web v{VERSION} ***")
    print(f"Guardando transcripciones en: {CARPETA_SALIDA}")
    print(f"Guardando gameplay descargado en: {CARPETA_GAMEPLAY}")
    print(f"Accedé desde este celular: http://127.0.0.1:{puerto}")
    print(f"Accedé desde otro dispositivo en la misma red: http://{ip_lan}:{puerto}")
    print("Presioná Ctrl+C para apagar.\n")

    threading.Thread(target=_abrir_navegador, args=(puerto,), daemon=True).start()
    app.run(host="0.0.0.0", port=puerto, debug=False, threaded=True)
