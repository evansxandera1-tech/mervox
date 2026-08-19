"""
Story Engine — archivo único.

Motor de generación de video (voz, subtítulos, música, efectos) reusado a
partir de Gen Estoico V5.5, ahora enfocado en historias de Reddit narradas
(en vez de citas/reflexiones estoicas). Todo el paquete fue fusionado aquí
adentro para evitar problemas al copiar carpetas en Termux. Este es el
ÚNICO archivo que hace falta.
"""

# ============================================================
# ---- módulo original: config.py ----
# ============================================================
import os

# =====================================================================
# CONFIGURACIÓN GLOBAL — carpetas, constantes y versión del programa.
# =====================================================================

# Todas las carpetas se anclan a la ubicación real del paquete (no al
# directorio de trabajo actual del proceso), por la misma razón que estaba
# documentada en el script original: Flask resuelve rutas relativas contra
# el root_path de la app, mientras que os.makedirs las resuelve contra el
# cwd del proceso, y esos dos podían no coincidir según desde dónde se
# lanzara el atajo de Termux. Ahora que todo el código vive en un solo
# archivo, CARPETA_BASE es simplemente la carpeta que contiene a este
# mismo archivo (gen_estoico.py).
CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))

CARPETA_SALIDA = os.path.join(CARPETA_BASE, "salidas_estoico")
CARPETA_VIDEOS = os.path.join(CARPETA_BASE, "videos_estoico")
CARPETA_IMAGENES_SUBIDAS = os.path.join(CARPETA_BASE, "imagenes_estoico")
CARPETA_IMAGENES_STOCK = os.path.join(CARPETA_BASE, "imagenes_stock_estoico")
CARPETA_MUSICA = os.path.join(CARPETA_BASE, "musica_estoico")
CARPETA_FUENTES = os.path.join(CARPETA_BASE, "fuentes_estoico")
CARPETA_LOGS = os.path.join(CARPETA_BASE, "logs_estoico")
CARPETA_PREVIEWS_VOZ = os.path.join(CARPETA_BASE, "previews_voz_estoico")
CARPETA_PRUEBAS_AUDIO_REDDIT = os.path.join(CARPETA_BASE, "pruebas_audio_reddit")

for c in [CARPETA_SALIDA, CARPETA_VIDEOS, CARPETA_IMAGENES_SUBIDAS, CARPETA_IMAGENES_STOCK,
          CARPETA_MUSICA, CARPETA_FUENTES, CARPETA_LOGS, CARPETA_PREVIEWS_VOZ, CARPETA_PRUEBAS_AUDIO_REDDIT]:
    os.makedirs(c, exist_ok=True)

# Todo lo que se copia al celular (audio, video, logs) va dentro de esta
# única subcarpeta de Download, en vez de sueltos directo en Download o en
# Movies. El "0_" la manda arriba de todo, ya que Download ordena alfabéticamente.
NOMBRE_CARPETA_DESCARGAS = "0_Papelera_Scripts"

RESOLUCION_ANCHO, RESOLUCION_ALTO = 1920, 1080
FPS = 24
SEGUNDOS_UN_DIA = 24 * 60 * 60
PREFIJO_LOG = "estoico_log_"

# ============================================================================
# BITÁCORA DE CAMBIOS
# ----------------------------------------------------------------------------
# v1.5 - Se quitó el selector de idioma/voz en inglés (VOCES_INGLES, el
#        desplegable "Voz / Idioma" y el botón "Escuchar" de prueba de
#        voces): ahora el narrador usa siempre la voz de Alex en español
#        (es-PE-AlexNeural, vía edge_tts). Quedan intactos los controles
#        de velocidad y tono, y la traducción automática con DeepL (ahora
#        siempre traduce a español).
# v1.6 - Ajustado para historias largas (mínimo ~20 minutos de video):
#        PALABRAS_MIN/MAX_HISTORIA pasó de 250-900 a 2600-7000 palabras,
#        UPVOTES_MINIMOS_HISTORIA bajó de 200 a 80 (las historias largas
#        con muchos upvotes son más raras), y la búsqueda en Reddit ahora
#        trae hasta 50 posts por subreddit del último mes (antes 15 de la
#        última semana) para tener más candidatos que puedan cumplir el
#        filtro de longitud más exigente. También se subió el límite del
#        guion de 30.000 a 60.000 caracteres (texto + campo de la
#        interfaz + truncado del backend), porque una historia de 7000
#        palabras más lo que agrega Gemini podía superar los 30.000.
# v1.7 - Se sacó el filtro de longitud de historias (PALABRAS_MIN/MAX_HISTORIA
#        pasó de 2600-7000 a 1-100000: prácticamente sin filtro) y se bajó
#        UPVOTES_MINIMOS_HISTORIA de 80 a 0, para que por ahora traiga
#        cualquier historia disponible, chica o grande, sin quedarse sin
#        candidatos. El límite del guion (textarea, contador y truncado
#        del backend) subió de 60.000 a 500.000 caracteres.
# v1.8 - Reddit estaba devolviendo 403 (Blocked) en las 5 consultas del
#        JSON público, para todos los subreddits. Se cambió www.reddit.com
#        por old.reddit.com y se reemplazó el User-Agent genérico
#        ("story-engine/1.0") por uno de navegador real (Chrome en
#        Windows) + headers Accept/Accept-Language, para intentar esquivar
#        el bloqueo automático. Si sigue bloqueando, el siguiente paso es
#        migrar a la API oficial con PRAW (credenciales gratuitas de
#        Reddit), como ya estaba previsto en el plan original.
# v1.9 - Se reemplazó el scraping del JSON público de Reddit (que Reddit
#        terminó bloqueando de nuevo) por la API oficial vía PRAW,
#        autenticada con REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET (app tipo
#        "script" creada en reddit.com/prefs/apps). Hay que completar esas
#        dos constantes al principio del bloque de Reddit para que funcione.
# v2.0 - Reddit eliminó la creación de apps de API por autoservicio
#        (Responsible Builder Policy), así que se sacó PRAW y se volvió al
#        scraping, pero más resistente al bloqueo: el JSON ahora prueba
#        varios dominios (www/old/reddit.com) y rota entre 5 User-Agents de
#        navegadores reales en cada intento; si un subreddit sigue sin traer
#        nada por JSON, se cae automáticamente a un segundo método por RSS
#        (que Reddit bloquea menos). Se agregó una pausa corta entre
#        subreddits para no parecer un bot agresivo.
# v2.1 - Se puso la clave de GEMINI_API_KEY, así que ahora "Traer historia
#        de Reddit" (pantalla principal) entrega el guion ya traducido al
#        español y adaptado. En esa misma pantalla: el cuadro de texto se
#        agrandó (de 66px a 220px de alto), los botones Pegar/Borrar pasaron
#        a ser íconos flotantes arriba a la derecha del cuadro (en vez de
#        una fila debajo), y se agregó un tercer ícono "Copiar todo" al
#        lado. El piloto Reddit (pantalla aparte /reddit/piloto) queda sin
#        tocar y sin usarse: todo el flujo real es desde la pantalla
#        principal.
# v2.2 - Ahora "Traer historia de Reddit" apunta a un video de 28-30
#        minutos: si encuentra una sola historia lo bastante larga, la usa
#        sola; si no, combina 2 o 3 historias entre las más votadas hasta
#        que la suma de palabras entre en ese rango (ajustable en
#        PALABRAS_OBJETIVO_MIN/MAX), y arma un solo guion con Gemini que
#        las une con transiciones cortas entre cada una. Si ninguna
#        combinación entra en rango, usa la historia individual más
#        votada igual, para no quedarse sin nada.
# v2.3 - Se corrigió GEMINI_API_KEY: la clave pegada antes estaba
#        duplicada (el mismo código copiado dos veces seguidas), lo que
#        hacía fallar la llamada a Gemini y el script devolvía la historia
#        sin traducir como respaldo. Ahora tiene la clave correcta, una
#        sola vez.
# v2.4 - Prueba real mostró que Gemini resumía bastante al traducir: 3
#        historias que sumaban ~3900-4400 palabras en inglés terminaron en
#        un guion de ~3260 palabras (~21.8 min, no 28-30). Se subió el
#        rango de selección PALABRAS_OBJETIVO_MIN/MAX de 3600-4400 a
#        4400-5400 para compensar esa reducción, y se le pidió explícito
#        a Gemini en los dos prompts que NO resuma de más (solo lo
#        claramente repetitivo), ya que el largo se elige a propósito.
# v2.5 - Reddit cerró en mayo de 2026 el acceso anónimo a los .json (403 en
#        el 100% de los casos) y empezó a limitar fuerte el RSS también
#        (429), incluso en old.reddit.com. Con las 5 vías bloqueadas el
#        mismo día, solo se rescataba 1 historia corta por corrida. Se
#        agregaron dos vías nuevas, en este orden de intento por
#        subreddit: (1) JSON con sesión logueada (cookies de una cuenta
#        real vía REDDIT_USUARIO/REDDIT_CONTRASENA — el bloqueo de mayo
#        2026 es solo para tráfico anónimo, autenticado sigue andando),
#        (2) JSON anónimo rotando dominio/User-Agent (como antes), (3) RSS
#        (como antes), y (4) para r/AITAH específicamente, un dataset
#        local descargado de antemano (RUTA_DATASET_AITA) con ~270.000
#        historias históricas de ese subreddit, como red de seguridad
#        para que nunca falte candidato aunque Reddit bloquee todo ese
#        día. El dataset no cuenta como "usado" hasta que realmente se
#        elige, igual que las demás vías.
# v2.6 - El login de Reddit se intenta una sola vez por arranque del
#        servidor y queda cacheado en memoria: los intentos siguientes no
#        volvían a escribir nada en el log, lo que hacía parecer que el
#        login nunca se ejecutaba. Ahora cada corrida deja explícito en el
#        log si está usando sesión cacheada o no. En la pantalla principal:
#        se sacó el texto de ejemplo (la cita estoica) que venía
#        precargado en el cuadro de guion, se ocultó la caja de vista
#        previa de video con los controles de arrastre (quedó sin uso real
#        para este flujo, enfocado en audio narrado), y se agregó el botón
#        "🔊 Generar audio y descargar" al lado de "Traer historia de
#        Reddit", que arma el audio del guion actual y deja un enlace de
#        descarga + reproductor, reusando el mismo backend que ya usaba la
#        pantalla de piloto.
# v2.7 - El fallback de sesión cacheada de v2.6 avisaba QUE el login había
#        fallado en un arranque anterior, pero no decía POR QUÉ (el motivo
#        real solo se veía en el log del primer intento, que no siempre se
#        guarda). Ahora el motivo del fallo queda guardado en memoria y se
#        repite en el log de cada corrida siguiente también, para poder
#        diagnosticar sin depender de haber capturado justo el primer
#        intento.
# v2.8 - Un solo 429 (límite de pedidos por minuto) de Gemini hacía caer
#        directo al texto sin traducir, algo fácil de pisar en pruebas
#        seguidas. Ahora generar_guion_reddit() reintenta hasta 4 veces
#        con espera creciente (5s, 10s, 20s...), respetando el header
#        Retry-After si Gemini lo manda, antes de rendirse y devolver el
#        texto original. Sigue sin cortar el pipeline si todos los
#        intentos fallan.
# v2.9 - El 429 persistente de Gemini no era por límite de pedidos: el
#        modelo GEMINI_MODELO ("gemini-2.0-flash") fue retirado por Google
#        el 31 de marzo de 2026, así que ninguna espera lo iba a arreglar.
#        Se cambió a "gemini-2.5-flash" (modelo vigente, tier gratis con
#        más margen). Los reintentos de v2.8 quedan igual, por si en el
#        futuro se vuelve a pisar el límite real de pedidos por minuto.
# v2.10 - Los dos prompts de Gemini (PROMPT_GUION_REDDIT y
#         PROMPT_GUION_REDDIT_MULTIPLE) asumían siempre jerga de Reddit
#         (AITA/YTA/NTA). Se agregaron reglas explícitas para que Gemini
#         también traduzca bien historias de foros británicos tipo
#         Mumsnet/AIBU: conversión de AIBU/YABU/YANBU al mismo formato de
#         pregunta-veredicto que ya se usaba, más jerga de foro (WWYD, LTB,
#         STBXH/STBXW, IMHO, HTH/RTFT), acrónimos de parentesco (DH, DD,
#         DS, DP, DC, PIL, MIL, FIL), qué hacer con nombres de usuario
#         citados, y cuándo aclarar referencias culturales locales (NHS,
#         etc.) sin sobre-explicar. Esto es solo el prompt: el script
#         todavía no trae historias de Mumsnet, sigue usando las mismas
#         fuentes de Reddit (obtener_historia_reddit); estas reglas quedan
#         listas para cuando se agregue esa fuente.
# v2.11 - Se integró Mumsnet/AIBU como fuente adicional de historias
#         (funciones _listar_hilos_mumsnet, _traer_hilo_mumsnet,
#         _candidatos_por_mumsnet), sumándose a los subreddits de siempre
#         dentro de obtener_historia_reddit — no los reemplaza. AVISO
#         IMPORTANTE: a diferencia del scraper de Reddit, que se probó
#         contra el JSON real, este scraper de Mumsnet se armó sin poder
#         confirmar el HTML real de mumsnet.com (no hay acceso a internet
#         desde donde se escribió este código: se dedujo el patrón a
#         partir de una lectura de las páginas convertida a texto, no del
#         HTML crudo). Puede que _listar_hilos_mumsnet o
#         _traer_hilo_mumsnet no encuentren nada la primera vez que
#         corran de verdad en Termux. Si eso pasa: el log va a avisar
#         "Mumsnet: el índice no devolvió ningún hilo" o "no se encontró
#         el inicio del post" — mandar ese log de vuelta para ajustar los
#         patrones con el caso real, el mismo proceso iterativo que ya se
#         usó para el scraper de Reddit (v1.8 a v2.6). Mientras tanto, si
#         esta fuente no aporta nada, el pipeline sigue funcionando igual
#         solo con Reddit (nunca corta el programa).
# v2.12 - Se hizo más robusta la generación de voz con edge_tts: antes solo
#         se reintentaba (hasta 3 veces) cuando edge_tts tiraba un error de
#         conexión explícito. Ahora, además, cada parte de audio generada
#         se valida leyendo su duración con ffprobe DENTRO del mismo bucle
#         de reintento (no recién más adelante en otra función): así se
#         detectan tanto audios vacíos como audios cortados a la mitad por
#         un corte de conexión momentáneo, y ambos casos entran al mismo
#         reintento automático en vez de tumbar el video entero. También se
#         agregó el botón "🔄 Otra historia" en el piloto Reddit para
#         descartar la historia mostrada (sin generar video) y traer una
#         distinta, vía la nueva ruta /reddit/descartar_historia.
# v3.9 - Se agregó auto-actualización de edge-tts: al arrancar el servidor
#        se compara en segundo plano la versión instalada contra la última
#        publicada en PyPI y, si hay una más nueva, se instala sola con pip
#        (sin bloquear el arranque). Esto ataca la causa real del error
#        "NoAudioReceived"/audio vacío que venía dando es-PE-AlexNeural: no
#        es un problema de la voz ni del script, sino de la librería
#        edge-tts desactualizada perdiendo sincronía con cambios del lado
#        de Microsoft. Si después de los 3 reintentos normales la
#        generación de voz sigue fallando, ahora se dispara una
#        actualización forzada única y un reintento extra antes de recién
#        ahí devolver el error.
#        Los botones de audio se separaron en 4 botones independientes, sin
#        mezclar y sin desplegables: "Escuchar ES", "Descargar audio ES",
#        "Escuchar EN" y "Descargar audio EN". Antes "Generar audio" hacía
#        escuchar+descargar juntos en un solo botón para español, y el de
#        inglés generaba el audio pero nunca mostraba el guion adaptado en
#        pantalla (por eso no se veían los caracteres en inglés en ningún
#        cuadro de texto: el backend sí lo generaba y lo mandaba en la
#        respuesta, pero el JS nunca lo escribía en el DOM). Ahora "Escuchar
#        EN" también vuelca ese guion en inglés a un cuadro de texto de
#        solo lectura debajo del botón.
# v4.0 - Se corrigió "Invalid pitch '0Hz'." en el audio en inglés: la
#         constante TONO_NARRADOR_INGLES estaba sin el signo (edge_tts
#         exige +/-), pasó de "0Hz" a "+0Hz" (bug viejo, no introducido en
#         la v3.9). Además, el cuadro de guion en inglés ahora muestra un
#         contador de caracteres arriba, y se agregó un cuadro nuevo debajo
#         con la traducción al español de ese guion en inglés (vía DeepL;
#         si falla la traducción, el cuadro queda vacío sin cortar la
#         generación del audio).
# v4.1 - Se agregó un botón "Escuchar ES (voz alt.)" con VOZ_NARRADOR_ALT =
#        "es-MX-JorgeNeural", para probar si el "audio vacío o dañado" es
#        específico de es-PE-AlexNeural o algo más general. Se confirmó
#        además que el pitch en español (TONO="-10Hz", VELOCIDAD="-10%")
#        ya tenía el signo puesto correctamente: ese no era el problema
#        del lado español (a diferencia del de inglés, corregido en v4.0).
# v4.2 - La prueba de v4.1 confirmó que el "audio vacío o dañado" fallaba
#        con la voz principal Y con la alternativa (y también en inglés):
#        no es un problema de una voz puntual ni de este script, sino del
#        servicio no oficial de Microsoft detrás de edge_tts, que a veces
#        deja de responder con audio real para todo el mundo durante un
#        rato, incluso con la librería ya actualizada (la auto-actualización
#        de la v3.9 no alcanza para esos casos). Para que el pipeline NUNCA
#        se quede sin audio por esto, se agregó gTTS (servicio de Google,
#        independiente del de Microsoft) como motor de emergencia: si
#        edge_tts agota los 3 reintentos normales Y el reintento extra tras
#        la actualización forzada, en vez de tirar el error se genera el
#        audio con gTTS automáticamente (instalándolo solo si hace falta).
#        gTTS no soporta tono (pitch), así que en ese modo el audio queda
#        con tono neutro (se avisa en el log); la velocidad configurada sí
#        se le aplica después, vía ffmpeg. Tampoco da tiempos de palabra
#        reales, así que en ese caso los subtítulos usan tiempos repartidos
#        parejo entre las palabras según la duración real del audio, en vez
#        de los tiempos exactos que da edge_tts.
# v4.3 - Se agregó, al final de la página principal, un probador de voces
#        en español: un desplegable con las ~44 voces neuronales en
#        español que ofrece edge_tts (una femenina y una masculina por
#        cada país/variante), un cuadro de texto de ejemplo precargado con
#        100 caracteres (editable), y un botón "▶️ Reproducir ejemplo" que
#        genera y reproduce un audio corto con la voz elegida. Usa la
#        misma función robusta de generación de audio que ya tiene
#        reintentos y el fallback de gTTS de la v4.2 (no la función de
#        preview vieja, que no tenía ninguna de esas protecciones), así
#        que este probador tampoco se queda sin sonido si edge_tts falla.
# v4.4 - Se corrigió que el fallback de gTTS (agregado en la v4.2) tapaba
#        su propio error real: si gTTS también fallaba, se perdía el
#        motivo (se mostraba de nuevo el viejo error de edge_tts) y no
#        había forma de saber por qué. Ahora se loguea el error de gTTS
#        aparte y se junta con el de edge_tts en un solo mensaje final,
#        para poder ver la causa real de ambos fallos.
# v4.5 - Se agregó más registro de diagnóstico al fallback de gTTS: ahora
#        loguea el tamaño en bytes del audio crudo que devuelve gTTS
#        (antes de ajustarle la velocidad con ffmpeg) y el tamaño del
#        archivo final, y si gTTS devuelve un archivo de 0 bytes lo dice
#        explícitamente en vez de dejar que ffmpeg lo procese a ciegas.
#        Esto es solo para terminar de diagnosticar el reporte de "ninguna
#        voz en español funciona" (donde el log de la v4.4 mostró que
#        ffprobe fallaba sobre el archivo final de gTTS, pero sin decir en
#        qué paso se había generado mal: si en gTTS mismo o en el ajuste
#        de velocidad con ffmpeg de después).
# v4.6 - El "Probador de voces en español" (sección de abajo de la página)
#        narraba el texto tal cual, sin traducir: útil para probar una
#        voz con texto ya en español, pero no servía para pegar un guion
#        de Mumsnet/Reddit sin traducir y escucharlo ya en español. Se
#        agregó: (1) casillero "Traducir con Gemini antes de narrar",
#        que llama a la nueva traducir_texto_gemini() (misma lógica de
#        reintentos ante 429 que generar_guion_reddit, pero para texto
#        libre en vez del formato de "grupo" de historias) antes de
#        generar la voz, y vuelca el texto traducido de vuelta al
#        textarea; y (2) controles propios de velocidad y tono debajo
#        del selector de voz (antes ese probador siempre usaba los
#        valores fijos TONO/VELOCIDAD del narrador principal, sin poder
#        ajustarlos ahí).
# v4.7 - Se sacaron las dos herramientas de prueba de voz que se habían ido
#        acumulando para diagnóstico (v4.1 y v4.6): el botón "Escuchar ES
#        (voz alt.)" con VOZ_NARRADOR_ALT, y toda la sección "Probador de
#        voces en español" (selector con las 44 voces de edge_tts,
#        traducción con Gemini y sus propios sliders). Se sacó también el
#        código que quedaba huérfano al sacar eso: VOZ_NARRADOR_ALT,
#        VOCES_ESPANOL, TEXTO_EJEMPLO_VOZ_ES, traducir_texto_gemini()/
#        PROMPT_TRADUCIR_LIBRE, generar_preview_voz()/TEXTO_PRUEBA_VOZ y
#        la ruta /preview_voz_espanol y /generar_audio_prueba_alt. Los
#        sliders de velocidad y tono que tenía el probador se movieron a
#        la sección AUDIO — ESPAÑOL (junto a "Escuchar ES"/"Descargar
#        audio ES"), que ahora los manda al generar/descargar el audio en
#        español en vez de usar siempre los valores fijos TONO/VELOCIDAD.
# v4.8 - Nueva paleta de colores en toda la interfaz web (pantalla principal
#        y pantalla de piloto Reddit): base violeta-azulado muy oscuro
#        (#150e2b), acento principal magenta eléctrico (#ff2e88, antes
#        coral #ff6b6b), y dos acentos nuevos en esquema tríada: cian
#        (#00e5ff, reemplaza --verdigris) y lima (#d4ff3d, --accent3, aún
#        sin usar en ningún elemento). Modo claro actualizado en la misma
#        línea. Colores vívidos pero con jerarquía: violeta domina,
#        magenta para acciones principales, cian/lima quedan disponibles
#        para diferenciar acciones secundarias más adelante.
# v5.0 - Rediseño estructural de la sección "Guion" en dos recuadros
#        independientes y autosuficientes: "Guion (idioma original)"
#        (el cuadro #texto de siempre) con sus propios botones "Generar
#        audio"/"Descargar audio" (voz Ryan) y un botón nuevo "Traducir";
#        y "Guion traducido (español)" (oculto hasta tocar "Traducir"),
#        con los sliders de velocidad/tono arriba y sus propios botones
#        de audio (voz Alex). Cambios de fondo:
#        - "Traer historia" ya NO traduce: /traer_historia ahora arma el
#          guion con generar_guion_ingles() en vez de generar_guion_reddit(),
#          así que carga tal cual en el idioma original.
#        - Nueva ruta /traducir_guion (POST): traduce a español el texto
#          que mande el frontend, con traducir_texto_deepl() (la
#          traducción con Gemini se había sacado en la v4.7; se usa DeepL
#          porque es la que seguía disponible en el código).
#        - /generar_audio_ingles ahora recibe el guion editable desde el
#          frontend (como ya hacía /generar_audio_prueba) en vez de
#          regenerarlo con generar_guion_ingles(), y acepta
#          velocidad_voz/tono_voz: los sliders pasan a compartirse entre
#          los dos idiomas en vez de usar TONO_NARRADOR_INGLES/
#          VELOCIDAD_NARRADOR_INGLES fijos.
#        - Se sacaron los campos de solo lectura textoIngles/
#          textoInglesEspanol y los bloques "AUDIO — ESPAÑOL"/
#          "AUDIO — INGLÉS": todo vive ahora en los dos recuadros nuevos.
# v5.1 - Se reactivó el filtro de longitud de historias (PALABRAS_MIN_HISTORIA,
#        que desde la v1.7 estaba en 1, o sea sin filtro real). Ahora
#        PALABRAS_MIN_HISTORIA = 800: se descartan las historias de texto
#        corto y solo entran las de texto largo (~6 min de narración en
#        adelante). Sin techo (PALABRAS_MAX_HISTORIA sigue en 100000).
# ============================================================================

# Versión del script. Se sube manualmente (1.0 -> 1.1 -> 1.2 ...) cada vez que se hace
# una mejora o se corrige un error, para que se sepa qué versión está corriendo en Termux
# y en la interfaz web sin tener que preguntar.
# Convención de numeración: al llegar a x.9, la siguiente versión pasa al
# entero siguiente (x.9 -> (x+1).0), no sigue a x.10, x.11, etc.
# Story Engine arranca en 1.0: es un proyecto nuevo a partir de Gen Estoico V5.5,
# no continúa su numeración.
VERSION_SCRIPT = "5.1"

# Velocidad de los efectos de video animados (ceniza y vela). Solo estos dos
# tienen una noción de "velocidad" porque son los únicos con movimiento en
# el tiempo; el resto de los efectos son estáticos. El valor es un
# multiplicador: 1.0 = velocidad original, <1.0 = más lento, >1.0 = más
# rápido.
VELOCIDAD_EFECTO_MIN, VELOCIDAD_EFECTO_MAX = 0.3, 2.5
VELOCIDAD_EFECTO_POR_DEFECTO = 1.0

# ============================================================
# ---- módulo original: texto.py ----
# ============================================================
import re

# ===================== Procesamiento de Texto =====================


def limpiar_texto_para_voz(texto):
    lineas = texto.split("\n")
    lineas_limpias = []
    for linea in lineas:
        l = linea.replace("\u200b", "").strip()
        if not l: continue
        l = re.sub(r"[*#_`~]", "", l)
        l = re.sub(r"[\U0001F000-\U0001FFFF\u2600-\u27BF\u2190-\u21FF\u2B00-\u2BFF\uFE0F\u200D]", "", l)
        if l: lineas_limpias.append(l)
    return re.sub(r"\s+", " ", " ".join(lineas_limpias)).strip()


def dividir_en_bloques(texto_limpio, frases_por_bloque=3):
    frases = re.split(r"(?<=[.!?])\s+", texto_limpio.strip())
    frases = [f.strip() for f in frases if f.strip()]
    bloques, actual, chars_actual = [], [], 0
    LIMITE_CHARS = 220
    for frase in frases:
        if actual and (len(actual) >= frases_por_bloque or chars_actual + len(frase) > LIMITE_CHARS):
            bloques.append(" ".join(actual))
            actual, chars_actual = [], 0
        actual.append(frase)
        chars_actual += len(frase)
    if actual:
        bloques.append(" ".join(actual))
    return bloques

# ============================================================
# ---- módulo original: logs.py ----
# ============================================================
import os
import sys
import time
import signal
import logging
import threading
from datetime import datetime


# =====================================================================
# LOGS: cada video generado tiene su propio archivo de log con hora
# exacta (incluidos milisegundos), que arranca desde el instante en que
# se recibe la orden de generar. Además hay un log general de eventos
# aparte ("..._eventos.txt") que registra cuándo arranca/se cierra el
# servidor, y si el programa se cierra o se actualiza mientras se está
# generando un video, eso también queda anotado ahí y en el log de ese
# video.
# =====================================================================


def _carpeta_logs_real():
    carpeta_download = "/sdcard/Download"
    if os.path.isdir(carpeta_download):
        carpeta = os.path.join(carpeta_download, NOMBRE_CARPETA_DESCARGAS)
        os.makedirs(carpeta, exist_ok=True)
        return carpeta
    return CARPETA_LOGS


def limpiar_logs_antiguos():
    limite = time.time() - SEGUNDOS_UN_DIA
    carpeta = _carpeta_logs_real()
    try:
        for nombre in os.listdir(carpeta):
            if not (nombre.startswith(PREFIJO_LOG) and nombre.endswith(".txt")):
                continue
            ruta = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta) and os.path.getmtime(ruta) < limite:
                try: os.remove(ruta)
                except Exception: pass
    except Exception: pass


FORMATO_LOG = logging.Formatter("%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s", datefmt="%H:%M:%S")


def crear_logger_video():
    limpiar_logs_antiguos()
    marca = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ruta_log = os.path.join(_carpeta_logs_real(), f"{PREFIJO_LOG}{marca}.txt")

    logger = logging.getLogger(f"estoico_{marca}_{id(threading.current_thread())}")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    manejador = logging.FileHandler(ruta_log, encoding="utf-8")
    manejador.setFormatter(FORMATO_LOG)
    logger.addHandler(manejador)
    return logger, ruta_log


def cerrar_logger_video(logger):
    for h in list(logger.handlers):
        try: h.close()
        except Exception: pass
        logger.removeHandler(h)


# ---- Log general de eventos del servidor (arranques, cierres, actualizaciones) ----
# Este log es distinto al de cada video: queda un solo archivo que junta todos los
# eventos del programa aunque el script se reinicie o se actualice.

RUTA_LOG_EVENTOS = os.path.join(_carpeta_logs_real(), "estoico_eventos.txt")
_logger_eventos = logging.getLogger("estoico_eventos")
_logger_eventos.setLevel(logging.DEBUG)
_logger_eventos.propagate = False
if not _logger_eventos.handlers:
    _manejador_eventos = logging.FileHandler(RUTA_LOG_EVENTOS, encoding="utf-8")
    _manejador_eventos.setFormatter(FORMATO_LOG)
    _logger_eventos.addHandler(_manejador_eventos)


def log_evento(mensaje):
    try:
        _logger_eventos.info(mensaje)
        for h in _logger_eventos.handlers:
            h.flush()
    except Exception:
        pass


# Referencia al logger del video que se está generando en este momento (si hay uno),
# para poder anotar en SU log si el proceso se cae o se actualiza a mitad de camino.
LOGGER_VIDEO_ACTIVO = {"logger": None, "ruta": None}


def _registrar_interrupcion(motivo):
    """Si hay un video generándose cuando el proceso recibe una señal de cierre/actualización,
    deja constancia tanto en el log de ese video como en el log general de eventos."""
    logger_activo = LOGGER_VIDEO_ACTIVO.get("logger")
    if logger_activo:
        try:
            logger_activo.error(f"⚠️ El proceso se detuvo/actualizó mientras se generaba el video ({motivo}).")
            for h in logger_activo.handlers:
                h.flush()
        except Exception:
            pass
    log_evento(f"⚠️ Servidor detenido/actualizado ({motivo}). Video en curso: {LOGGER_VIDEO_ACTIVO.get('ruta')}")


def _manejador_senal(numero_senal, frame):
    _registrar_interrupcion(f"señal {numero_senal}")
    sys.exit(0)


try:
    signal.signal(signal.SIGTERM, _manejador_senal)
    signal.signal(signal.SIGINT, _manejador_senal)
except Exception:
    pass

# ============================================================
# ---- módulo original: fuentes.py ----
# ============================================================
import os
import requests


# ===================== Fuentes =====================

FUENTES_DISPONIBLES = {
    "Montserrat": "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-SemiBold.ttf",
    "Playfair Display": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/static/PlayfairDisplay-BoldItalic.ttf",
    "Cormorant Garamond": "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Bold.ttf",
    "EB Garamond": "https://github.com/google/fonts/raw/main/ofl/ebgaramond/static/EBGaramond-Bold.ttf",
    "Lora": "https://github.com/google/fonts/raw/main/ofl/lora/static/Lora-Bold.ttf",
}
# Montserrat SemiBold como nueva fuente por defecto: para historias de Reddit
# en horizontal (1920x1080) se lee mejor una tipografía limpia tipo sans-serif
# que las serif decorativas que traía el proyecto original (esas siguen
# disponibles en el desplegable por si se prefiere ese estilo).
FUENTE_POR_DEFECTO = "Montserrat"


def asegurar_fuente(nombre_fuente):
    url = FUENTES_DISPONIBLES.get(nombre_fuente)
    if not url:
        nombre_fuente = FUENTE_POR_DEFECTO
        url = FUENTES_DISPONIBLES[FUENTE_POR_DEFECTO]

    ruta_destino = os.path.join(CARPETA_FUENTES, url.split("/")[-1])
    if not os.path.exists(ruta_destino) or os.path.getsize(ruta_destino) < 1000:
        try:
            respuesta = requests.get(url, timeout=15)
            respuesta.raise_for_status()
            with open(ruta_destino, "wb") as f: f.write(respuesta.content)
        except Exception:
            if nombre_fuente != FUENTE_POR_DEFECTO: return asegurar_fuente(FUENTE_POR_DEFECTO)
            return None
    return nombre_fuente

# ============================================================
# ---- módulo original: musica.py ----
# ============================================================
import os
import random


# ===================== Música =====================


def seleccionar_musica_fondo(genero):
    if genero == "ninguno": return None
    carpeta = os.path.join(CARPETA_MUSICA, genero)
    if os.path.isdir(carpeta):
        pistas = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith(".mp3")]
        if pistas: return random.choice(pistas)
    return None


for _genero in ["piano", "ambient", "cuerdas"]:
    os.makedirs(os.path.join(CARPETA_MUSICA, _genero), exist_ok=True)

# ============================================================
# ---- módulo original: proyecto.py ----
# ============================================================
import os


# =====================================================================
# CARPETA DE PROYECTO POR VIDEO
# ---------------------------------------------------------------------
# Cada video generado tiene su propia carpeta (estilo carpeta de proyecto
# de edición: voz, imagen, subtítulos y efecto separados), en vez de que
# todos los archivos intermedios queden sueltos y mezclados en una sola
# carpeta general. El video final también queda adentro, en la raíz de la
# carpeta del proyecto.
# =====================================================================


def crear_carpeta_proyecto(nombre_base, marca):
    """Crea (si no existe) la carpeta del proyecto para un video puntual,
    con una subcarpeta por tipo de archivo. Devuelve un diccionario con las
    rutas absolutas de cada subcarpeta más la raíz del proyecto."""
    nombre_proyecto = f"{nombre_base}_{marca}"
    raiz = os.path.join(CARPETA_VIDEOS, nombre_proyecto)
    rutas = {
        "nombre_proyecto": nombre_proyecto,
        "raiz": raiz,
        "voz": os.path.join(raiz, "voz"),
        "imagen": os.path.join(raiz, "imagen"),
        "subtitulos": os.path.join(raiz, "subtitulos"),
        "efecto": os.path.join(raiz, "efecto"),
    }
    for clave, ruta in rutas.items():
        if clave not in ("nombre_proyecto",):
            os.makedirs(ruta, exist_ok=True)
    return rutas

# ============================================================
# ---- módulo original: voz_stock.py ----
# ============================================================
import os
import random
import time
import requests


# ===================== Voz y Stock =====================

VOZ_NARRADOR = "es-PE-AlexNeural"

# Voz para el audio en inglés adaptado (v3.4). Pitch y velocidad quedan
# fijos (no editables desde la interfaz por ahora, a diferencia de la voz
# en español que sí tiene sliders).
VOZ_NARRADOR_INGLES = "en-GB-RyanNeural"
TONO_NARRADOR_INGLES = "+0Hz"
VELOCIDAD_NARRADOR_INGLES = "-10%"


# Pega aquí tu API key gratuita de DeepL (la consigues en https://www.deepl.com/pro-api → plan Free).
# Las keys del plan Free terminan en ":fx"
DEEPL_API_KEY = "c19a9209-13c5-4477-a103-da87cf4f2f39:fx"
DEEPL_URL_FREE = "https://api-free.deepl.com/v2/translate"
DEEPL_IDIOMA_DESTINO = {"es": "ES", "en": "EN-US"}


def traducir_texto_deepl(texto, idioma_destino, logger=None):
    """Traduce el texto al idioma del narrador usando la API gratuita de DeepL.
    Si no hay API key configurada o falla la petición, devuelve el texto original sin traducir."""
    if not DEEPL_API_KEY:
        if logger: logger.warning("DEEPL_API_KEY vacía: se omite la traducción, se usa el texto tal cual.")
        return texto
    destino = DEEPL_IDIOMA_DESTINO.get(idioma_destino)
    if not destino:
        return texto
    try:
        resp = requests.post(
            DEEPL_URL_FREE,
            headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"},
            data={"text": texto, "target_lang": destino},
            timeout=30,
        )
        resp.raise_for_status()
        datos = resp.json()
        return datos["translations"][0]["text"]
    except Exception as e:
        if logger: logger.warning(f"Fallo la traducción con DeepL, se usa el texto original: {e}")
        return texto


TONO = "-10Hz"
VELOCIDAD = "-10%"

# Velocidad y tono de voz ahora se ajustan con una barra deslizante (no con
# opciones predefinidas). El valor por defecto de cada barra coincide con
# TONO/VELOCIDAD de arriba, así que si no se toca nada el resultado es
# idéntico al de siempre. Los límites evitan que edge_tts reciba un valor
# absurdo si algo llega mal formado desde el formulario.
VELOCIDAD_VOZ_MIN, VELOCIDAD_VOZ_MAX = -50, 50
TONO_VOZ_MIN, TONO_VOZ_MAX = -50, 50
VELOCIDAD_VOZ_POR_DEFECTO = -10
TONO_VOZ_POR_DEFECTO = -10


def _formatear_ajuste_voz(valor, sufijo, por_defecto, minimo, maximo):
    """Convierte el número que manda la barra deslizante (ej. -10, 25) al
    formato que espera edge_tts (ej. '-10%', '+25Hz'), recortando a los
    límites permitidos si el valor es inválido o se pasa de rango."""
    try:
        v = int(float(valor))
    except (TypeError, ValueError):
        v = por_defecto
    v = max(minimo, min(maximo, v))
    return f"{v:+d}{sufijo}"


def _lista_claves(var_base, respaldos_fijos):
    claves = []
    for i in range(1, 11):
        var = var_base if i == 1 else f"{var_base}_{i}"
        v = os.environ.get(var)
        if v and v not in claves: claves.append(v)
    for r in respaldos_fijos:
        if r and r not in claves: claves.append(r)
    return claves


PEXELS_API_KEYS = _lista_claves("PEXELS_API_KEY", ["WsXOOtwwqY9m2AzAuhQKdnM8ZLmJFpB5OsMwYleHRUyy7YCKsU230usZ"])
PIXABAY_API_KEYS = _lista_claves("PIXABAY_API_KEY", ["56560067-073dd5296a400da3085818083"])

_claves_pexels_agotadas, _claves_pixabay_agotadas = set(), set()

# Términos de búsqueda para imágenes de fondo de historias tipo Reddit
# (confesiones, relatos personales). Reemplaza a la lista anterior de temática
# estoica (estatuas, ruinas), pensada para citas filosóficas.
TERMINOS_STOCK_FONDO = [
    "city night lights", "empty room window", "person silhouette thinking",
    "urban street rain", "dramatic storm clouds", "phone screen dark",
    "empty apartment", "car night drive", "coffee shop window",
    "text message screen", "hallway door closed", "city skyline dusk",
]


def _buscar_foto_pexels(consulta, evitar=None):
    evitar = evitar or set()
    claves = [k for k in PEXELS_API_KEYS if k not in _claves_pexels_agotadas]
    for clave in claves:
        try:
            res = requests.get("https://api.pexels.com/v1/search", headers={"Authorization": clave}, params={"query": consulta, "orientation": "landscape", "per_page": 10}, timeout=10)
            if res.status_code == 429:
                _claves_pexels_agotadas.add(clave)
                continue
            if res.status_code != 200: return None
            fotos = res.json().get("photos", [])
            cand = [f["src"]["large2x"] for f in fotos if f.get("src", {}).get("large2x") and f["src"]["large2x"] not in evitar]
            if cand: return random.choice(cand)
        except Exception: return None
    return None


def _buscar_foto_pixabay(consulta, evitar=None):
    evitar = evitar or set()
    claves = [k for k in PIXABAY_API_KEYS if k not in _claves_pixabay_agotadas]
    for clave in claves:
        try:
            res = requests.get("https://pixabay.com/api/", params={"key": clave, "q": consulta, "image_type": "photo", "orientation": "horizontal", "per_page": 10}, timeout=10)
            if res.status_code == 429:
                _claves_pixabay_agotadas.add(clave)
                continue
            if res.status_code != 200: return None
            hits = res.json().get("hits", [])
            cand = [h["largeImageURL"] for h in hits if h.get("largeImageURL") and h["largeImageURL"] not in evitar]
            if cand: return random.choice(cand)
        except Exception: return None
    return None


def obtener_imagen_stock(indice, usadas, logger=None):
    terminos = TERMINOS_STOCK_FONDO[:]
    random.shuffle(terminos)
    for termino in terminos:
        url = _buscar_foto_pexels(termino, evitar=usadas) or _buscar_foto_pixabay(termino, evitar=usadas)
        if url:
            ruta_destino = os.path.join(CARPETA_IMAGENES_STOCK, f"stock_{indice}_{int(time.time())}.jpg")
            try:
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                with open(ruta_destino, "wb") as f: f.write(r.content)
                usadas.add(url)
                return ruta_destino
            except Exception: continue
    return None

# ============================================================
# ---- módulo original: audio.py ----
# ============================================================
import os
import re
import asyncio
import subprocess

import edge_tts


# ===================== Auto-actualización de edge-tts =====================
# La causa real detrás del error "NoAudioReceived"/audio vacío-dañado que
# venía dando edge_tts (confirmado contra los issues del repo oficial
# rany2/edge-tts) es que Microsoft cambia seguido detalles internos del
# servicio, y una versión vieja de la librería deja de "calzar" con eso:
# la conexión responde pero sin audio real, y ni siquiera reintentar
# soluciona nada si el paquete sigue desactualizado. Estas dos funciones
# atacan esa causa en vez de solo reintentar a ciegas.
_EDGE_TTS_YA_CHEQUEADO = False


def _version_instalada_edge_tts():
    try:
        import importlib.metadata
        return importlib.metadata.version("edge-tts")
    except Exception:
        return None


def _version_mas_nueva_edge_tts(timeout=6):
    """Consulta la API pública de PyPI (sin necesitar pip) para saber la
    última versión publicada de edge-tts. Devuelve None si no hay red o
    falla la consulta, sin cortar nada más del programa."""
    try:
        resp = requests.get("https://pypi.org/pypi/edge-tts/json", timeout=timeout)
        resp.raise_for_status()
        return resp.json()["info"]["version"]
    except Exception:
        return None


def actualizar_edge_tts_si_hace_falta(logger=None, forzar=False):
    """Compara versión instalada vs. la última de PyPI y, si hay una más
    nueva (o si 'forzar' es True, para el reintento de emergencia), corre
    'pip install --upgrade edge-tts' en un subproceso. No bloquea el
    arranque del servidor si algo falla (sin red, pip roto, etc.): solo
    queda un aviso en el log y el programa sigue con la versión que ya
    tenía instalada."""
    global _EDGE_TTS_YA_CHEQUEADO
    if _EDGE_TTS_YA_CHEQUEADO and not forzar:
        return
    _EDGE_TTS_YA_CHEQUEADO = True
    try:
        instalada = _version_instalada_edge_tts()
        ultima = _version_mas_nueva_edge_tts()
        if not ultima:
            if logger: logger.warning("No se pudo chequear la última versión de edge-tts en PyPI (sin red o falló la consulta); se sigue con la versión instalada.")
            return
        if instalada == ultima and not forzar:
            if logger: logger.info(f"edge-tts ya está en su última versión ({instalada}).")
            return
        if logger: logger.info(f"Actualizando edge-tts ({instalada} -> {ultima})...")
        resultado = subprocess.run(
            ["pip", "install", "--upgrade", "edge-tts", "--break-system-packages"],
            capture_output=True, text=True, timeout=90,
        )
        if resultado.returncode == 0:
            if logger: logger.info(f"edge-tts actualizado correctamente a {ultima}.")
        else:
            if logger: logger.warning(f"Falló la actualización de edge-tts (pip devolvió error): {resultado.stderr.strip()[:300]}")
    except Exception as e:
        if logger: logger.warning(f"No se pudo actualizar edge-tts automáticamente: {e}")


# ===================== Fallback: gTTS (motor de emergencia) =====================
# edge_tts depende de un servicio no oficial de Microsoft que puede dejar de
# responder con audio real para todo el mundo durante un rato (confirmado:
# en la v4.1 falló tanto con la voz principal como con la alternativa y con
# la de inglés). La auto-actualización de arriba ataca la causa de "librería
# desactualizada", pero no sirve cuando el problema está del lado de
# Microsoft y no del lado de este script. Para que el video nunca se quede
# sin audio por esto, si edge_tts agota TODOS sus reintentos (incluido el
# extra tras la actualización forzada) se usa gTTS como último recurso: es
# un servicio de Google, totalmente aparte del de Microsoft.
try:
    from gtts import gTTS
    _GTTS_DISPONIBLE = True
except ImportError:
    _GTTS_DISPONIBLE = False


def _instalar_gtts_si_hace_falta(logger=None):
    """Instala gTTS con pip la primera vez que hace falta (recién cuando
    edge_tts ya falló del todo), igual que la auto-actualización de
    edge-tts de más arriba. No bloquea nada más si falla."""
    global _GTTS_DISPONIBLE, gTTS
    if _GTTS_DISPONIBLE:
        return True
    try:
        if logger: logger.info("gTTS no está instalado; instalando (motor de emergencia, edge_tts agotó todos sus reintentos)...")
        resultado = subprocess.run(
            ["pip", "install", "gTTS", "--break-system-packages"],
            capture_output=True, text=True, timeout=90,
        )
        if resultado.returncode != 0:
            if logger: logger.warning(f"No se pudo instalar gTTS: {resultado.stderr.strip()[:300]}")
            return False
        from gtts import gTTS as _gTTS
        gTTS = _gTTS
        _GTTS_DISPONIBLE = True
        if logger: logger.info("gTTS instalado correctamente.")
        return True
    except Exception as e:
        if logger: logger.warning(f"No se pudo instalar gTTS: {e}")
        return False


def _idioma_gtts_desde_voz(voz):
    """Deduce el código de idioma de gTTS a partir del nombre de voz de
    edge_tts (ej. 'es-PE-AlexNeural' -> 'es', 'en-GB-RyanNeural' -> 'en')."""
    return "en" if voz.lower().startswith("en-") else "es"


def _aplicar_velocidad_ffmpeg(ruta_entrada, ruta_salida, velocidad, logger=None):
    """Aplica el % de velocidad (mismo formato que usa edge_tts, ej. '-10%')
    a un audio ya generado, vía el filtro atempo de ffmpeg. gTTS no tiene
    forma de pedir la velocidad al generar, así que se ajusta después."""
    try:
        pct = float(str(velocidad).replace("%", "").replace("+", ""))
    except Exception:
        pct = 0.0
    factor = max(0.5, min(1.0 + (pct / 100.0), 2.0))
    if abs(factor - 1.0) < 0.001:
        if ruta_entrada != ruta_salida:
            shutil.copyfile(ruta_entrada, ruta_salida)
        return
    cmd = ["ffmpeg", "-y", "-i", ruta_entrada, "-filter:a", f"atempo={factor}", ruta_salida]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        # Antes esto quedaba en silencio (solo se copiaba el crudo sin
        # avisar). Ahora se loguea para saber si el archivo final vacío
        # viene de acá o de gTTS mismo.
        if logger: logger.warning(f"ffmpeg no pudo ajustar la velocidad del audio de gTTS (código {resultado.returncode}): {resultado.stderr.strip()[-300:]}. Se usa el audio de gTTS sin ajustar velocidad.")
        shutil.copyfile(ruta_entrada, ruta_salida)


def _generar_chunk_audio_gtts_fallback(texto, voz, ruta_audio, velocidad, logger=None):
    """Último recurso cuando edge_tts (Microsoft) no devolvió audio ni
    actualizando la librería: genera el audio con gTTS (Google). Tira
    RuntimeError si tampoco esto funciona, para que quien llama sepa que
    de verdad no hay forma de generar audio en este momento."""
    if not _instalar_gtts_si_hace_falta(logger=logger):
        raise RuntimeError("gTTS no está disponible y no se pudo instalar.")
    idioma = _idioma_gtts_desde_voz(voz)
    ruta_cruda = f"{ruta_audio}.gtts_crudo.mp3"
    gTTS(text=texto, lang=idioma).save(ruta_cruda)
    # Se registra el tamaño del archivo crudo de gTTS ANTES de tocarlo con
    # ffmpeg, para poder distinguir en el log si el problema es que gTTS
    # (Google) tampoco devolvió audio real, o si el archivo de gTTS estaba
    # bien y el que lo rompió fue el paso de ajuste de velocidad de acá
    # abajo.
    tamano_crudo = os.path.getsize(ruta_cruda) if os.path.exists(ruta_cruda) else 0
    if logger: logger.info(f"gTTS generó {tamano_crudo} bytes en el archivo crudo (antes de ajustar velocidad).")
    if tamano_crudo == 0:
        if os.path.exists(ruta_cruda):
            os.remove(ruta_cruda)
        raise RuntimeError("gTTS devolvió un archivo vacío (0 bytes): probablemente no hay conexión desde este dispositivo hacia el servicio de Google usado por gTTS, o el pedido fue rechazado.")
    try:
        _aplicar_velocidad_ffmpeg(ruta_cruda, ruta_audio, velocidad, logger=logger)
    finally:
        if os.path.exists(ruta_cruda):
            os.remove(ruta_cruda)
    tamano_final = os.path.getsize(ruta_audio) if os.path.exists(ruta_audio) else 0
    if logger: logger.info(f"Audio final de gTTS (después de ajustar velocidad): {tamano_final} bytes.")
    obtener_duracion_audio(ruta_audio)  # valida que haya quedado audio real
    if logger:
        logger.warning("Audio generado con gTTS (fallback): edge_tts (Microsoft) no respondió tras todos los reintentos. El tono configurado no se aplica en este modo (gTTS no lo soporta); la velocidad sí.")


# ===================== Audio y tiempos =====================


def _dividir_texto_en_partes_audio(texto, n_partes):
    """Divide el texto en n_partes trozos lo mas parejos posible en
    caracteres, cortando siempre al final de una frase completa (nunca a
    mitad de una). Si hay menos frases que n_partes, devuelve una parte
    por frase."""
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    frases = [f.strip() for f in frases if f.strip()]
    if not frases:
        return [texto] if texto.strip() else []
    if len(frases) <= n_partes:
        return frases
    total_chars = sum(len(f) for f in frases)
    objetivo = total_chars / n_partes
    partes, actual, chars_actual = [], [], 0
    for frase in frases:
        if actual and chars_actual >= objetivo and len(partes) < n_partes - 1:
            partes.append(" ".join(actual))
            actual, chars_actual = [], 0
        actual.append(frase)
        chars_actual += len(frase) + 1
    if actual:
        partes.append(" ".join(actual))
    return partes


async def _generar_chunk_audio_y_tiempos_async(texto, voz, ruta_audio, logger=None, tono=TONO, velocidad=VELOCIDAD, intentos=3):
    """Genera un unico chunk de audio con una sola llamada a edge_tts (sin
    trocear). Es la logica 'de siempre'; se usa tanto para textos cortos
    como para cada parte cuando generar_audio_y_tiempos_async trocea el
    texto largo.

    Reintenta automaticamente ante errores de red/conexion (DNS, socket,
    SSL, stream cortado) hasta 'intentos' veces, con espera creciente entre
    cada intento (2s, 4s, 6s...), antes de darse por vencido y propagar el
    error."""
    ultimo_error = None
    submaker = None
    uso_fallback_gtts = False
    for intento in range(1, intentos + 1):
        try:
            communicate = edge_tts.Communicate(texto, voz, pitch=tono, rate=velocidad, boundary="WordBoundary")
            submaker = edge_tts.SubMaker()
            with open(ruta_audio, "wb") as file:
                async for chunk in communicate.stream():
                    tipo = chunk.get("type")
                    if tipo == "audio":
                        file.write(chunk["data"])
                    elif tipo == "WordBoundary":
                        submaker.feed(chunk)
            # edge_tts a veces responde sin tirar ningún error pero deja un
            # audio vacío o cortado a la mitad (por ejemplo si la conexión
            # se corta un instante durante la descarga): sin esta
            # verificación eso pasaba desapercibido acá y recién tronaba
            # más adelante, en otra función, tumbando el video entero.
            # Probar la duración con ffprobe en este mismo punto detecta
            # ambos casos (vacío o corrupto) y los manda al mismo
            # reintento de acá abajo, sea cual sea la causa exacta.
            try:
                obtener_duracion_audio(ruta_audio)
            except Exception:
                raise RuntimeError("edge_tts devolvió un audio vacío o dañado (no se pudo leer su duración), sin tirar error propio.")
            break
        except Exception as e:
            ultimo_error = e
            if logger:
                logger.warning(f"Intento {intento}/{intentos} fallo generando voz ({e}).")
            if intento < intentos:
                await asyncio.sleep(2 * intento)
            else:
                # Los reintentos normales ya se agotaron. Antes de rendirse
                # del todo, se dispara una actualización forzada de
                # edge-tts (por si la causa es librería desactualizada,
                # que es lo más común según los issues del repo oficial) y
                # se prueba UNA vez más. Si esto también falla, recién ahí
                # se propaga el error como antes.
                if logger: logger.warning("Se agotaron los reintentos normales; se intenta actualizar edge-tts y reintentar una vez más antes de rendirse.")
                actualizar_edge_tts_si_hace_falta(logger=logger, forzar=True)
                try:
                    communicate = edge_tts.Communicate(texto, voz, pitch=tono, rate=velocidad, boundary="WordBoundary")
                    submaker = edge_tts.SubMaker()
                    with open(ruta_audio, "wb") as file:
                        async for chunk in communicate.stream():
                            tipo = chunk.get("type")
                            if tipo == "audio":
                                file.write(chunk["data"])
                            elif tipo == "WordBoundary":
                                submaker.feed(chunk)
                    obtener_duracion_audio(ruta_audio)
                    if logger: logger.info("La generación de voz funcionó tras actualizar edge-tts.")
                except Exception:
                    # edge_tts agotó TODAS las chances, incluida la
                    # actualización forzada de la librería: el problema está
                    # del lado del servicio de Microsoft, no de este script.
                    # Último recurso: gTTS (Google), un servicio aparte.
                    try:
                        _generar_chunk_audio_gtts_fallback(texto, voz, ruta_audio, velocidad, logger=logger)
                        submaker = None
                        uso_fallback_gtts = True
                    except Exception as e_gtts:
                        # Antes acá se perdía el motivo real por el que
                        # gTTS fallaba (se tapaba con el error viejo de
                        # edge_tts). Ahora se loguea aparte y se junta en
                        # el mensaje final, para poder diagnosticar cuál de
                        # los dos motores fue el que falló y por qué.
                        if logger: logger.warning(f"El fallback de gTTS también falló ({e_gtts}).")
                        raise RuntimeError(f"edge_tts falló ({ultimo_error}) y el fallback de gTTS también falló ({e_gtts}).")
    palabras_tiempos = []
    if uso_fallback_gtts:
        # gTTS no da tiempos de palabra reales (a diferencia de edge_tts):
        # se reparten las palabras parejo a lo largo de la duración real
        # del audio, para que los subtítulos sigan funcionando de forma
        # aproximada en vez de quedar sin tiempos.
        try:
            duracion_total = obtener_duracion_audio(ruta_audio)
            palabras = texto.split()
            if palabras:
                paso = duracion_total / len(palabras)
                for i, palabra in enumerate(palabras):
                    palabras_tiempos.append({"texto": palabra, "inicio": i * paso, "fin": (i + 1) * paso})
        except Exception:
            pass
    else:
        try:
            if hasattr(submaker, "offset_and_duration"):
                for offset, duration, text in submaker.offset_and_duration:
                    inicio, dur = offset / 10000000.0, duration / 10000000.0
                    palabras_tiempos.append({"texto": text, "inicio": inicio, "fin": inicio + dur})
            elif hasattr(submaker, "cues"):
                for cue in submaker.cues:
                    inicio = cue.start.total_seconds() if hasattr(cue.start, "total_seconds") else cue.start / 10000000.0
                    fin = cue.end.total_seconds() if hasattr(cue.end, "total_seconds") else cue.end / 10000000.0
                    texto_cue = getattr(cue, "content", None) or getattr(cue, "text", "")
                    palabras_tiempos.append({"texto": texto_cue, "inicio": inicio, "fin": fin})
        except Exception:
            pass
    return palabras_tiempos


async def generar_audio_y_tiempos_async(texto, voz, ruta_audio, logger=None, tono=TONO, velocidad=VELOCIDAD):
    """Si el texto supera los 1000 caracteres, SIEMPRE se trocea en 5 partes
    (cortando por frases completas) y se genera el audio de cada parte por
    separado, para reducir la chance de que edge_tts corte el stream a
    mitad de un texto largo. Despues se concatenan los audios parciales con
    ffmpeg y se ajustan los tiempos de palabra de cada parte sumandoles el
    offset acumulado de las partes anteriores."""
    if len(texto) <= 1000:
        return await _generar_chunk_audio_y_tiempos_async(texto, voz, ruta_audio, logger=logger, tono=tono, velocidad=velocidad)

    partes = _dividir_texto_en_partes_audio(texto, 5)
    if logger:
        logger.info(f"Texto de {len(texto)} caracteres: se trocea en {len(partes)} partes para la generación de voz.")

    rutas_parciales = []
    palabras_tiempos = []
    offset_acumulado = 0.0
    ruta_lista = f"{ruta_audio}.concat.txt"
    try:
        for i, parte in enumerate(partes):
            ruta_parcial = f"{ruta_audio}.parte{i}.mp3"
            if logger:
                logger.info(f"Generando parte {i + 1}/{len(partes)} de la voz ({len(parte)} caracteres).")
            tiempos_parte = await _generar_chunk_audio_y_tiempos_async(parte, voz, ruta_parcial, logger=logger, tono=tono, velocidad=velocidad)
            for pt in tiempos_parte:
                palabras_tiempos.append({"texto": pt["texto"], "inicio": pt["inicio"] + offset_acumulado, "fin": pt["fin"] + offset_acumulado})
            rutas_parciales.append(ruta_parcial)
            offset_acumulado += obtener_duracion_audio(ruta_parcial)

        with open(ruta_lista, "w", encoding="utf-8") as f:
            for r in rutas_parciales:
                f.write(f"file '{os.path.abspath(r)}'\n")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", ruta_lista, "-c", "copy", ruta_audio]
        resultado_ffmpeg = subprocess.run(cmd, capture_output=True, text=True)
        if resultado_ffmpeg.returncode != 0:
            raise RuntimeError(f"ffmpeg no pudo unir las {len(partes)} partes de audio: {resultado_ffmpeg.stderr[-500:]}")
    finally:
        for r in rutas_parciales:
            if os.path.exists(r):
                os.remove(r)
        if os.path.exists(ruta_lista):
            os.remove(ruta_lista)

    return palabras_tiempos


def generar_audio_y_tiempos(texto, voz, ruta_audio, logger=None, tono=TONO, velocidad=VELOCIDAD):
    return asyncio.run(generar_audio_y_tiempos_async(texto, voz, ruta_audio, logger=logger, tono=tono, velocidad=velocidad))


def obtener_duracion_audio(ruta_audio):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", ruta_audio], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def calcular_tiempos_de_bloques(bloques, palabras_tiempos, duracion_total_audio):
    resultado = []
    if palabras_tiempos:
        idx = 0
        for bloque in bloques:
            n_palabras = len(bloque.split())
            sub = palabras_tiempos[idx: idx + n_palabras]
            idx += n_palabras
            if sub:
                resultado.append((bloque, sub[0]["inicio"], sub[-1]["fin"], sub))
            else:
                ultimo_fin = resultado[-1][2] if resultado else 0.0
                resultado.append((bloque, ultimo_fin, duracion_total_audio, []))
        return resultado

    total_chars = sum(len(b) for b in bloques) or 1
    t = 0.0
    for bloque in bloques:
        dur = duracion_total_audio * (len(bloque) / total_chars)
        resultado.append((bloque, t, t + dur, []))
        t += dur
    return resultado

# ============================================================
# ---- módulo nuevo: reddit.py ----
# ============================================================
import csv
import json
import html
import itertools
import random as _random_reddit
import xml.etree.ElementTree as ET

# ===================== Extracción de historias de Reddit =====================

# Reddit dejó de permitir crear apps de API por autoservicio (Responsible
# Builder Policy), así que se volvió al scraping, pero más resistente al
# bloqueo que la versión anterior: se prueban varios dominios/user-agents
# rotando en cada intento (JSON), y si eso falla, se cae a un segundo
# método por RSS (que Reddit bloquea menos que el JSON).

# Desde mayo de 2026, Reddit bloquea (403) el JSON público para tráfico
# ANÓNIMO. El tráfico autenticado (una sesión logueada de verdad) sigue
# funcionando, así que primero se intenta loguearse con esta cuenta y usar
# esa sesión para las consultas; si el login falla por cualquier motivo, el
# script sigue igual con JSON anónimo y RSS como antes (nunca se corta el
# programa por esto).
REDDIT_USUARIO = "Born642"
REDDIT_CONTRASENA = "silverhawk"

# Dataset local de respaldo: historias históricas de r/AITAH descargadas de
# antemano (no vía scraping en vivo), para que SIEMPRE haya candidatos
# aunque Reddit bloquee ese día por completo. Se usa solo si las otras vías
# no traen nada para ese subreddit. Formato esperado: CSV con columnas
# "id","title","text" (o "body"/"selftext") y opcionalmente "score"/"ups".
# Si el archivo no existe todavía, esta vía simplemente no aporta nada (no
# rompe el resto del programa) hasta que lo descargues y lo coloques ahí.
RUTA_DATASET_AITA = os.path.join(CARPETA_BASE, "dataset_aita.csv")

# Dominios alternativos para el mismo contenido: si uno está bloqueado en
# ese momento, se prueba el siguiente.
DOMINIOS_REDDIT_JSON = ["www.reddit.com", "old.reddit.com", "reddit.com"]

# User-Agents realistas de navegadores comunes, para rotar en cada pedido
# y no repetir siempre la misma firma (que es lo que termina bloqueando).
USER_AGENTS_ROTACION = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
]

SUBREDDITS_RELATOS = [
    "AITAH", "relationship_advice", "confessions", "TrueOffMyChest",
    "maliciouscompliance",
]

# Filtros de selección: se descartan historias fuera de este rango de
# palabras, con pocos upvotes, o marcadas como NSFW/borradas.
#
# v5.1: se volvió a activar el filtro de longitud (estaba desactivado
# desde la v1.7, con 1-100000, o sea "aceptar cualquier cosa"). Ahora se
# descartan las historias de texto corto y solo entran las de texto
# largo: mínimo 800 palabras (a ~130-140 palabras por minuto de voz, son
# unos 6 minutos de narración). Sin techo superior (PALABRAS_MAX_HISTORIA
# se deja en 100000, no se puso límite de máximo, solo de mínimo). Si 800
# te deja con pocos candidatos o te trae historias más cortas de lo que
# esperás, subí o bajá este número.
PALABRAS_MIN_HISTORIA, PALABRAS_MAX_HISTORIA = 800, 100000
UPVOTES_MINIMOS_HISTORIA = 0

# Objetivo de duración final del video: 28-30 minutos de narración.
# A ~130-140 palabras por minuto de voz, eso ronda las 3640-4200 palabras
# en el GUION FINAL (ya traducido). Pero Gemini suele resumir bastante al
# traducir/adaptar (en una prueba real, 3 historias que sumaban ~3900-4400
# palabras en inglés terminaron en un guion de ~3260 palabras en español,
# un 20-25% menos). Por eso el rango de selección apunta más alto que el
# objetivo final, para compensar esa reducción. Se usa para: (a) preferir
# una sola historia larga que ya caiga en este rango, o (b) si no hay
# ninguna así, combinar 2 o 3 historias más votadas hasta que la suma entre
# en rango. Si después de una tanda de pruebas el guion sigue quedando
# corto o largo, ajustar estos dos números.
PALABRAS_OBJETIVO_MIN, PALABRAS_OBJETIVO_MAX = 4400, 5400

RUTA_HISTORIAS_USADAS = os.path.join(CARPETA_BASE, "reddit_historias_usadas.json")

# ----- Fuente Mumsnet / AIBU (v2.11) -----
# Mumsnet no tiene JSON público como Reddit: se lee el HTML de la página de
# índice de AIBU (ordenada por más reciente) para sacar título+enlace de
# cada hilo, y después se entra a cada hilo para sacar el cuerpo del post.
# A diferencia del scraper de Reddit, este está basado en el patrón de
# texto visible de la página (no en nombres de clases CSS, que no se
# pudieron confirmar de antemano): si Mumsnet cambia su maquetación esto
# puede dejar de traer candidatos. Si eso pasa, revisar el log — avisa
# cuánto encontró en cada paso — y ajustar los patrones de
# _listar_hilos_mumsnet/_traer_hilo_mumsnet.
MUMSNET_ACTIVADO = True
MUMSNET_URL_BASE = "https://www.mumsnet.com/talk/am_i_being_unreasonable"
MUMSNET_PAGINAS_A_REVISAR = 3  # páginas del índice a recorrer por corrida (~50 hilos por página)
MUMSNET_HILOS_A_ABRIR = 20  # de los hilos listados, a cuántos se les va a pedir el cuerpo (evita pegarle a 150 páginas en una sola corrida)

# v3.4: Reddit queda "en pausa" por ahora (código intacto, no se borra
# nada) y Mumsnet pasa a ser la única fuente mientras esto esté en True.
# Se probó el scraper contra Mumsnet real y los patrones matchearon sin
# necesitar ajustes. Para volver a usar Reddit (solo o junto con Mumsnet),
# poner esto en False.
USAR_SOLO_MUMSNET = True


def _cargar_ids_usados():
    if not os.path.exists(RUTA_HISTORIAS_USADAS):
        return set()
    try:
        with open(RUTA_HISTORIAS_USADAS, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def _guardar_id_usado(id_post):
    usados = _cargar_ids_usados()
    usados.add(id_post)
    try:
        with open(RUTA_HISTORIAS_USADAS, "w", encoding="utf-8") as f:
            json.dump(sorted(usados), f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _normalizar_y_filtrar(id_post, subreddit, titulo, cuerpo, upvotes, over_18, url, ids_usados):
    """Aplica los filtros de selección a los datos ya extraídos de un post,
    vengan del JSON o del RSS. Punto único de filtrado para los dos métodos."""
    if not id_post or id_post in ids_usados:
        return None
    if over_18:
        return None
    titulo = (titulo or "").strip()
    cuerpo = (cuerpo or "").strip()
    if not cuerpo or cuerpo in ("[removed]", "[deleted]"):
        return None
    n_palabras = len(cuerpo.split())
    if n_palabras < PALABRAS_MIN_HISTORIA or n_palabras > PALABRAS_MAX_HISTORIA:
        return None
    if upvotes < UPVOTES_MINIMOS_HISTORIA:
        return None
    return {
        "id": id_post,
        "subreddit": subreddit,
        "titulo": titulo,
        "cuerpo": cuerpo,
        "upvotes": upvotes,
        "url": url,
    }


# Sesión logueada cacheada en memoria: se inicia sesión como máximo una vez
# por corrida del programa (no una vez por subreddit), y se reutiliza para
# todos los pedidos de esa corrida. Si el login falla, queda en False para
# no reintentarlo 5 veces seguidas en la misma corrida (una por subreddit).
_SESION_REDDIT = {"sesion": None, "intentado": False, "motivo_fallo": None}


def _iniciar_sesion_reddit(logger=None):
    """Inicia sesión en reddit.com con REDDIT_USUARIO/REDDIT_CONTRASENA
    usando el endpoint clásico de login (el mismo que usa el sitio web, no
    la API OAuth), y devuelve un requests.Session ya logueado. Devuelve
    None si algo falla (credenciales incorrectas, captcha, 2FA activado,
    cambio en el endpoint, etc.) — en ese caso el resto del programa sigue
    con JSON anónimo y RSS como respaldo, sin cortarse.

    Nota: Reddit puede pedir verificación adicional (captcha/2FA) según la
    cuenta; si eso pasa, este login por request simple no va a poder
    completarlo y va a fallar de forma prolija (queda logueado el intento
    como fallido y se sigue sin sesión)."""
    if _SESION_REDDIT["intentado"]:
        if logger:
            if _SESION_REDDIT["sesion"] is not None:
                logger.info("Sesión de Reddit ya intentada antes en este arranque del servidor. ¿Hay sesión activa?: sí")
            else:
                logger.info(
                    "Sesión de Reddit ya intentada antes en este arranque del servidor. "
                    f"¿Hay sesión activa?: no (motivo del fallo: {_SESION_REDDIT['motivo_fallo']}; "
                    "no se reintenta en esta misma corrida del servidor)"
                )
        return _SESION_REDDIT["sesion"]
    _SESION_REDDIT["intentado"] = True

    if not REDDIT_USUARIO or not REDDIT_CONTRASENA:
        return None

    ua = _random_reddit.choice(USER_AGENTS_ROTACION)
    sesion = requests.Session()
    sesion.headers.update({
        "User-Agent": ua,
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })
    try:
        # Paso 1: visitar la portada para conseguir las cookies iniciales
        # (algunas protecciones anti-bot de Reddit revisan que exista una
        # cookie de sesión previa al login, no solo el POST suelto).
        sesion.get("https://www.reddit.com/", timeout=15)

        resp = sesion.post(
            "https://www.reddit.com/api/login",
            data={
                "op": "login",
                "user": REDDIT_USUARIO,
                "passwd": REDDIT_CONTRASENA,
                "api_type": "json",
            },
            headers={"Referer": "https://www.reddit.com/login/"},
            timeout=15,
        )
        resp.raise_for_status()
        cuerpo = resp.json()
        errores = cuerpo.get("json", {}).get("errors", [])
        if errores:
            _SESION_REDDIT["motivo_fallo"] = str(errores)
            if logger:
                logger.warning(f"Login de Reddit ({REDDIT_USUARIO}) rechazado: {errores}")
            return None

        if logger:
            logger.info(f"Sesión de Reddit iniciada correctamente como {REDDIT_USUARIO}.")
        _SESION_REDDIT["sesion"] = sesion
        return sesion
    except Exception as e:
        _SESION_REDDIT["motivo_fallo"] = f"{type(e).__name__}: {e}"
        if logger:
            logger.warning(f"No se pudo iniciar sesión en Reddit ({REDDIT_USUARIO}): {e}")
        return None


def _candidatos_por_json(sub, ids_usados, logger=None, sesion=None):
    """Primer método: JSON de Reddit, probando varios dominios y
    User-Agents rotativos hasta que alguno responda sin bloqueo. Si se pasa
    una sesión logueada, se usa esa (tráfico autenticado, no bloqueado por
    el filtro anónimo de mayo 2026) antes de caer a un pedido anónimo
    suelto con requests.get."""
    candidatos = []
    dominios = list(DOMINIOS_REDDIT_JSON)
    _random_reddit.shuffle(dominios)
    for dominio in dominios:
        ua = _random_reddit.choice(USER_AGENTS_ROTACION)
        pedir = sesion.get if sesion is not None else requests.get
        try:
            resp = pedir(
                f"https://{dominio}/r/{sub}/top.json",
                params={"limit": 50, "t": "month"},
                headers={
                    "User-Agent": ua,
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                },
                timeout=15,
            )
            resp.raise_for_status()
            posts = resp.json().get("data", {}).get("children", [])
            for post in posts:
                datos = post.get("data", {})
                candidato = _normalizar_y_filtrar(
                    datos.get("id"), datos.get("subreddit", sub), datos.get("title"),
                    datos.get("selftext"), datos.get("ups", 0), datos.get("over_18"),
                    f"https://reddit.com{datos.get('permalink', '')}", ids_usados,
                )
                if candidato:
                    candidatos.append(candidato)
            return candidatos  # dominio funcionó: no hace falta probar los otros
        except Exception as e:
            origen = "logueado" if sesion is not None else "anónimo"
            if logger:
                logger.warning(f"JSON ({origen}) de r/{sub} vía {dominio} falló: {e}")
            continue
    return candidatos


def _candidatos_por_dataset(sub, ids_usados, logger=None):
    """Vía de respaldo (v2.5): dataset local descargado de antemano, solo
    para r/AITAH por ahora. No depende de la red ni de que Reddit esté
    bloqueando o no: si el archivo RUTA_DATASET_AITA existe, siempre puede
    aportar candidatos. Acepta encabezados típicos de los datasets públicos
    de AITA (id/title/text o body/selftext, score u ups opcional)."""
    candidatos = []
    if sub.lower() != "aitah" or not os.path.exists(RUTA_DATASET_AITA):
        return candidatos
    try:
        with open(RUTA_DATASET_AITA, "r", encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                id_post = fila.get("id") or fila.get("post_id") or ""
                titulo = fila.get("title") or fila.get("titulo") or ""
                cuerpo = fila.get("text") or fila.get("body") or fila.get("selftext") or ""
                try:
                    upvotes = int(float(fila.get("score") or fila.get("ups") or 0))
                except (TypeError, ValueError):
                    upvotes = 0
                candidato = _normalizar_y_filtrar(
                    id_post, "AITAH", titulo, cuerpo, upvotes, False,
                    f"https://reddit.com/r/AITAH/comments/{id_post}", ids_usados,
                )
                if candidato:
                    candidatos.append(candidato)
    except Exception as e:
        if logger:
            logger.warning(f"No se pudo leer el dataset local de AITA: {e}")
    return candidatos


def _candidatos_por_rss(sub, ids_usados, logger=None):
    """Segundo método (respaldo): feed RSS público, que Reddit bloquea
    menos que el JSON. Solo trae posts de texto (con cuerpo), no de link;
    no incluye la cantidad de upvotes (queda en 0)."""
    candidatos = []
    ua = _random_reddit.choice(USER_AGENTS_ROTACION)
    try:
        resp = requests.get(
            f"https://www.reddit.com/r/{sub}/top/.rss",
            params={"limit": 50, "t": "month"},
            headers={"User-Agent": ua, "Accept": "application/atom+xml, application/xml, text/xml, */*"},
            timeout=15,
        )
        resp.raise_for_status()
    except Exception as e:
        if logger:
            logger.warning(f"RSS de r/{sub} falló: {e}")
        return candidatos

    try:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        raiz = ET.fromstring(resp.content)
        for entrada in raiz.findall("atom:entry", ns):
            id_bruto = entrada.findtext("atom:id", default="", namespaces=ns) or ""
            id_post = id_bruto.split("_")[-1] if "_" in id_bruto else id_bruto
            titulo = entrada.findtext("atom:title", default="", namespaces=ns) or ""
            contenido_bruto = entrada.findtext("atom:content", default="", namespaces=ns) or ""
            link_el = entrada.find("atom:link", ns)
            url = link_el.get("href") if link_el is not None else ""

            # El cuerpo real del post viene envuelto entre estos comentarios
            # HTML; si no están, es un post de link (sin texto) y se descarta.
            m = re.search(r"<!-- SC_OFF -->(.*?)<!-- SC_ON -->", contenido_bruto, re.DOTALL)
            if not m:
                continue
            cuerpo = re.sub(r"<[^>]+>", " ", m.group(1))
            cuerpo = html.unescape(cuerpo)
            cuerpo = re.sub(r"\s+", " ", cuerpo).strip()

            candidato = _normalizar_y_filtrar(id_post, sub, titulo, cuerpo, 0, False, url, ids_usados)
            if candidato:
                candidatos.append(candidato)
    except Exception as e:
        if logger:
            logger.warning(f"No se pudo leer el RSS de r/{sub}: {e}")
    return candidatos


def _texto_plano_html(html_bruto):
    """Convierte HTML crudo a texto plano simple: saca scripts/estilos,
    saca todas las etiquetas, decodifica entidades y colapsa espacios. Es
    una limpieza genérica (no sabe nada de la estructura particular de
    Mumsnet), usada como base para los patrones de _traer_hilo_mumsnet."""
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_bruto, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def _listar_hilos_mumsnet(paginas=MUMSNET_PAGINAS_A_REVISAR, logger=None):
    """Devuelve una lista de (id_hilo, titulo, url_hilo) sacada del índice
    de AIBU, recorriendo las primeras `paginas` páginas (la 1 son los
    hilos más recientes). No trae el cuerpo todavía, solo título+enlace:
    eso se pide aparte por hilo en _traer_hilo_mumsnet(), para no
    descargar 150 páginas completas de golpe."""
    hilos, vistos = [], set()
    ua = _random_reddit.choice(USER_AGENTS_ROTACION)
    for pagina in range(1, paginas + 1):
        url = MUMSNET_URL_BASE if pagina == 1 else f"{MUMSNET_URL_BASE}?page={pagina}"
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": ua, "Accept-Language": "en-GB,en;q=0.9"},
                timeout=15,
            )
            resp.raise_for_status()
        except Exception as e:
            if logger:
                logger.warning(f"Mumsnet: falló la página de índice {pagina}: {e}")
            continue

        # Cada hilo del listado es un enlace con esta forma (confirmado
        # contra el HTML real): Mumsnet usa la URL completa en el href, no
        # una ruta relativa, por eso el prefijo "https://www.mumsnet.com"
        # es opcional en el patrón (se acepta con o sin él, por las dudas).
        # href="https://www.mumsnet.com/talk/am_i_being_unreasonable/<id>-<slug>"
        # y el texto visible del enlace es el título del hilo.
        encontrados_en_pagina = 0
        for m in re.finditer(
            r'href="(?:https?://www\.mumsnet\.com)?(/talk/am_i_being_unreasonable/(\d+)-[a-z0-9-]+)"[^>]*>([^<]{4,300})<',
            resp.text,
        ):
            href, id_hilo, titulo = m.group(1), m.group(2), html.unescape(m.group(3)).strip()
            if id_hilo in vistos or not titulo:
                continue
            vistos.add(id_hilo)
            hilos.append((id_hilo, titulo, f"https://www.mumsnet.com{href}"))
            encontrados_en_pagina += 1
        if logger:
            logger.info(f"Mumsnet: índice página {pagina} — {encontrados_en_pagina} hilos encontrados.")
            if encontrados_en_pagina == 0:
                # Diagnóstico: si no encontró nada, guardamos qué respondió
                # realmente Mumsnet (código de estado + un fragmento del
                # cuerpo) para saber si fue un bloqueo, un captcha, un muro
                # de cookies u otra cosa, en vez de adivinar a ciegas.
                fragmento = re.sub(r"\s+", " ", resp.text[:300]).strip()
                logger.warning(
                    f"Mumsnet: 0 hilos en página {pagina} — status={resp.status_code}, "
                    f"largo_respuesta={len(resp.text)} bytes, primeros 300 caracteres: {fragmento!r}"
                )
                # Si la página SÍ menciona la ruta de los hilos en algún
                # lado (o sea que no es un bloqueo/captcha, sino que el
                # patrón no matchea la maquetación real), mostramos el HTML
                # crudo alrededor del primer enlace real para poder ajustar
                # el patrón con el caso concreto, en vez de a ciegas.
                idx = resp.text.find("/talk/am_i_being_unreasonable/")
                if idx != -1:
                    ventana = resp.text[max(0, idx - 80):idx + 400]
                    logger.warning(f"Mumsnet: HTML alrededor del primer enlace de hilo encontrado: {ventana!r}")
                else:
                    logger.warning("Mumsnet: la respuesta ni siquiera contiene '/talk/am_i_being_unreasonable/' en ningún lado.")
        time.sleep(_random_reddit.uniform(0.5, 1.2))
    return hilos


def _traer_hilo_mumsnet(id_hilo, titulo, url_hilo, logger=None):
    """Entra a un hilo puntual y extrae el cuerpo del post original (no
    los comentarios). Se apoya en un patrón de texto que se comprobó
    manualmente en varios hilos reales: después de la línea
    "<usuario> · <cuándo>" que sigue al conteo de respuestas, viene el
    cuerpo del post, y termina antes de "OP posts" o del primer comentario
    (usuario · fecha) siguiente. Si el patrón no matchea (por un cambio de
    maquetación de Mumsnet), devuelve None sin cortar el resto del
    programa; ese hilo simplemente no aporta candidato."""
    ua = _random_reddit.choice(USER_AGENTS_ROTACION)
    try:
        resp = requests.get(
            url_hilo,
            headers={"User-Agent": ua, "Accept-Language": "en-GB,en;q=0.9"},
            timeout=15,
        )
        resp.raise_for_status()
    except Exception as e:
        if logger:
            logger.warning(f"Mumsnet: falló al abrir el hilo {id_hilo}: {e}")
        return None

    try:
        texto = _texto_plano_html(resp.text)
        # Ancla de inicio: la primera línea "usuario · algo con fecha/hora"
        # (Today/Yesterday/dd de un mes) que aparece después del título.
        idx_titulo = texto.find(titulo[:40]) if len(titulo) >= 40 else texto.find(titulo)
        zona = texto[idx_titulo:] if idx_titulo != -1 else texto
        m_inicio = re.search(r"^[^\n]{2,40}·\s*(Today|Yesterday|\d{1,2}/\d{1,2}/\d{4}|\d+\s+days?\s+ago)[^\n]*$", zona, re.MULTILINE)
        if not m_inicio:
            if logger:
                logger.warning(f"Mumsnet: no se encontró el inicio del post en el hilo {id_hilo} (posible cambio de maquetación).")
            return None
        resto = zona[m_inicio.end():]
        # Ancla de fin: donde termina el post y empieza lo demás (respuestas,
        # "OP posts: See next", o la próxima línea "usuario · fecha").
        m_fin = re.search(r"\n(OP posts|See all|Show quote history)", resto)
        cuerpo = resto[:m_fin.start()] if m_fin else resto[:4000]
        cuerpo = re.sub(r"\n+", " ", cuerpo).strip()
        return cuerpo if len(cuerpo.split()) >= 15 else None
    except Exception as e:
        if logger:
            logger.warning(f"Mumsnet: no se pudo extraer el cuerpo del hilo {id_hilo}: {e}")
        return None


def _candidatos_por_mumsnet(ids_usados, logger=None):
    """Arma candidatos desde AIBU (Mumsnet) con el mismo formato que usa
    Reddit (id/subreddit/titulo/cuerpo/upvotes/url), para que
    _agrupar_para_objetivo y el resto del pipeline no tengan que saber de
    dónde vino cada historia. Los ids se guardan con prefijo "ms_" para no
    pisarse con ids de Reddit en el archivo de historias usadas."""
    candidatos = []
    if not MUMSNET_ACTIVADO:
        return candidatos
    hilos = _listar_hilos_mumsnet(logger=logger)
    if not hilos:
        if logger:
            logger.warning("Mumsnet: el índice no devolvió ningún hilo (posible bloqueo o cambio de maquetación).")
        return candidatos

    for id_hilo, titulo, url_hilo in hilos[:MUMSNET_HILOS_A_ABRIR]:
        id_completo = f"ms_{id_hilo}"
        if id_completo in ids_usados:
            continue
        cuerpo = _traer_hilo_mumsnet(id_hilo, titulo, url_hilo, logger=logger)
        if not cuerpo:
            continue
        candidato = _normalizar_y_filtrar(id_completo, "Mumsnet_AIBU", titulo, cuerpo, 0, False, url_hilo, ids_usados)
        if candidato:
            candidatos.append(candidato)
        time.sleep(_random_reddit.uniform(0.5, 1.2))

    if logger:
        logger.info(f"Mumsnet: {len(candidatos)} candidatos válidos de {len(hilos[:MUMSNET_HILOS_A_ABRIR])} hilos revisados.")
    return candidatos


def _agrupar_para_objetivo(candidatos):
    """A partir de todos los candidatos disponibles (ya filtrados y sin
    usar), arma el grupo de historias para un solo video, apuntando a
    PALABRAS_OBJETIVO_MIN/MAX en total:

    1. Si hay alguna historia individual que ya cae en ese rango sola, se
       usa esa (la de más upvotes entre las que cumplen).
    2. Si no, se prueban combinaciones de 2 y de 3 historias entre las 15
       más votadas, buscando alguna cuya suma de palabras entre en rango;
       se prefiere la de más upvotes sumados y, a igualdad, la que use
       menos historias.
    3. Si ninguna combinación entra en rango, se devuelve igual la historia
       individual más votada (el video sale más corto que el objetivo,
       pero no se queda sin nada).

    Devuelve una lista de 1 a 3 diccionarios de historia."""
    if not candidatos:
        return []

    en_rango = [c for c in candidatos if PALABRAS_OBJETIVO_MIN <= len(c["cuerpo"].split()) <= PALABRAS_OBJETIVO_MAX]
    if en_rango:
        en_rango.sort(key=lambda c: c["upvotes"], reverse=True)
        return [en_rango[0]]

    top_candidatos = sorted(candidatos, key=lambda c: c["upvotes"], reverse=True)[:15]
    mejor_clave, mejor_combo = None, None
    for tam in (2, 3):
        for combo in itertools.combinations(top_candidatos, tam):
            total_palabras = sum(len(c["cuerpo"].split()) for c in combo)
            if PALABRAS_OBJETIVO_MIN <= total_palabras <= PALABRAS_OBJETIVO_MAX:
                total_upvotes = sum(c["upvotes"] for c in combo)
                clave = (-total_upvotes, tam)
                if mejor_clave is None or clave < mejor_clave:
                    mejor_clave, mejor_combo = clave, combo
    if mejor_combo:
        return list(mejor_combo)

    candidatos_ordenados = sorted(candidatos, key=lambda c: c["upvotes"], reverse=True)
    return [candidatos_ordenados[0]]


def obtener_historia_reddit(subreddits=None, logger=None):
    """Trae candidatos de varios subreddits y arma el grupo de 1 a 3
    historias para un solo video, apuntando a 28-30 minutos de narración
    (ver _agrupar_para_objetivo). Primero intenta el JSON público (rotando
    dominio y User-Agent); si eso no trae nada para un subreddit, cae al
    RSS público como respaldo.

    Devuelve una LISTA de 1 a 3 diccionarios con
    id/subreddit/titulo/cuerpo/upvotes/url, o None si no se encontró
    ningún candidato."""
    subreddits = subreddits or SUBREDDITS_RELATOS
    ids_usados = _cargar_ids_usados()
    candidatos = []

    # Reddit "en pausa" por ahora (v3.4): mientras USAR_SOLO_MUMSNET esté en
    # True, Mumsnet es la ÚNICA fuente y este bloque entero de Reddit se
    # salta (no se borra nada, sigue todo funcionando si se apaga el flag).
    if not USAR_SOLO_MUMSNET:
        sesion = _iniciar_sesion_reddit(logger=logger)

        for sub in subreddits:
            encontrados = []
            if sesion is not None:
                encontrados = _candidatos_por_json(sub, ids_usados, logger=logger, sesion=sesion)
            if not encontrados:
                encontrados = _candidatos_por_json(sub, ids_usados, logger=logger)
            if not encontrados:
                encontrados = _candidatos_por_rss(sub, ids_usados, logger=logger)
            if not encontrados:
                encontrados = _candidatos_por_dataset(sub, ids_usados, logger=logger)
            candidatos.extend(encontrados)
            # pequeña pausa entre subreddits para no disparar varios pedidos
            # seguidos y parecer un bot más agresivo de lo necesario
            time.sleep(_random_reddit.uniform(0.8, 1.8))
    elif logger:
        logger.info("Reddit en pausa (USAR_SOLO_MUMSNET=True): se busca solo en Mumsnet.")

    # Fuente Mumsnet/AIBU (v2.11, ahora principal desde v3.4 mientras
    # USAR_SOLO_MUMSNET esté activo).
    try:
        candidatos.extend(_candidatos_por_mumsnet(ids_usados, logger=logger))
    except Exception as e:
        if logger:
            logger.warning(f"Mumsnet: fuente completa falló: {e}")

    if not candidatos:
        return None

    return _agrupar_para_objetivo(candidatos)


# ===================== Guion con Gemini (traducción + transformación) =====================

# Pega aquí tu API key gratuita de Gemini (la consigues en https://aistudio.google.com/apikey).
GEMINI_API_KEY = "AQ.Ab8RN6IJeJNtyFywqBinlFfAmumIsA4GQlqtEStRx11wEBk_uw"
GEMINI_MODELO = "gemini-2.5-flash"

# Tono/personalidad del narrador. Placeholder por ahora: ajustar cuando se
# defina el tono final (serio, canchero, sarcástico, neutro-cercano...).
TONO_NARRADOR_REDDIT = "cercano y natural, como si le contara la historia a un amigo"

PROMPT_GUION_REDDIT = """Traducí y adaptá al español la siguiente historia (puede venir de Reddit o de un foro británico como Mumsnet/AIBU; no la traduzcas palabra por palabra: adaptá modismos y tono para que suene natural, como si un narrador la contara en voz alta).

Reglas de términos y jerga del foro de origen (aplicá solo las que correspondan según lo que aparezca en el texto):
- Veredicto: "AITA"/"AIBU" → convertilo en la pregunta narrativa "¿Estoy siendo injusta/o?". "YTA"/"YABU" → "sí, estás siendo injusta/o". "NTA"/"YANBU" → "no estás siendo injusta/o". Nunca los traduzcas palabra por palabra ni los dejes en inglés.
- Otra jerga de veredicto/foro si aparece: WWYD → "¿qué harían ustedes?"; LTB → "déjalo"/"termina la relación"; STBXH/STBXW → "mi futuro exesposo/a"; IMHO → "en mi humilde opinión" (o se omite si suena forzado); HTH, RTFT y jerga interna similar → se omiten, no aportan a la narración.
- Acrónimos de parentesco: expandilos siempre (DH → mi esposo, DD → mi hija, DS → mi hijo, DP → mi pareja, DC → mi hijo/a, PIL → mis suegros, MIL → mi suegra, FIL → mi suegro).
- Nombres de usuario del foro (si aparecen citados, ej. "Fulanito dice..."): no los traduzcas ni los leas literal si suenan raros en voz alta; reemplazalos por una referencia neutra ("otra persona respondió...", "alguien más comentó...").
- Referencias culturales locales (NHS, marcas, lugares, programas de TV): mantenelas tal cual y agregá una aclaración breve entre paréntesis SOLO si el sentido no es obvio sin ella.
- Conservá el sarcasmo, la ironía o el tono pasivo-agresivo del original si lo tiene; no lo suavices. Si hay humor seco (típico de foros británicos), buscale un equivalente natural en español, no traducción literal que pierda la gracia.

Después:
1. Mantené prácticamente todo el relato: no la resumas de más, achicá solo partes claramente repetitivas si las hay. El largo de esta historia ya se eligió a propósito para la duración del video, así que un guion mucho más corto que el original es un problema.
2. Agregá 2 o 3 comentarios o reacciones breves del narrador insertados durante el relato (por ejemplo "acá se puso interesante", "yo no hubiera aguantado eso").
3. Empezá con un gancho corto de 1-2 frases explicando por qué se eligió esta historia.
4. Cerrá con una reflexión o pregunta corta para el espectador.
5. Puntuá y acentuá el texto con cuidado (comas, puntos, puntos suspensivos, signos de exclamación e interrogación, tildes). La voz sintética que va a leer esto en voz alta solo usa la puntuación para decidir pausas y entonación: si el texto queda sin acentos o con puntuación pobre, se lee plano y sin emoción. Usá los signos donde correspondan para marcar sorpresa, tensión, humor o alivio según el momento del relato.

Tono del narrador: {tono}

Historia original (título: "{titulo}"):
{cuerpo}

Devolvé SOLO el texto final del guion, sin explicaciones ni comillas alrededor. No uses asteriscos, markdown ni emojis."""

PROMPT_GUION_REDDIT_MULTIPLE = """Vas a armar un guion narrado en español para un video que junta varias historias reales (de Reddit y/o de un foro británico como Mumsnet/AIBU), una atrás de la otra, para llegar a unos 28-30 minutos de narración en total.

Reglas de términos y jerga del foro de origen (aplicá solo las que correspondan según lo que aparezca en cada historia):
- Veredicto: "AITA"/"AIBU" → convertilo en la pregunta narrativa "¿Estoy siendo injusta/o?". "YTA"/"YABU" → "sí, estás siendo injusta/o". "NTA"/"YANBU" → "no estás siendo injusta/o". Nunca los traduzcas palabra por palabra ni los dejes en inglés.
- Otra jerga de veredicto/foro si aparece: WWYD → "¿qué harían ustedes?"; LTB → "déjalo"/"termina la relación"; STBXH/STBXW → "mi futuro exesposo/a"; IMHO → "en mi humilde opinión" (o se omite si suena forzado); HTH, RTFT y jerga interna similar → se omiten, no aportan a la narración.
- Acrónimos de parentesco: expandilos siempre (DH → mi esposo, DD → mi hija, DS → mi hijo, DP → mi pareja, DC → mi hijo/a, PIL → mis suegros, MIL → mi suegra, FIL → mi suegro).
- Nombres de usuario del foro (si aparecen citados): no los traduzcas ni los leas literal si suenan raros en voz alta; reemplazalos por una referencia neutra ("otra persona respondió...", "alguien más comentó...").
- Referencias culturales locales (NHS, marcas, lugares, programas de TV): mantenelas tal cual y agregá una aclaración breve entre paréntesis SOLO si el sentido no es obvio sin ella.
- Conservá el sarcasmo, la ironía o el tono pasivo-agresivo del original si lo tiene; no lo suavices. Si hay humor seco (típico de foros británicos), buscale un equivalente natural en español, no traducción literal que pierda la gracia.

Para cada una de las historias numeradas abajo:
1. Traducila y adaptala al español (no palabra por palabra: adaptá modismos y tono para que suene natural).
2. Mantené prácticamente todo el relato: no la resumas de más, achicá solo partes claramente repetitivas si las hay. El largo de cada historia ya se eligió a propósito para llegar a los 28-30 minutos entre todas, así que un guion mucho más corto que el conjunto original es un problema.
3. Agregá 2 o 3 comentarios o reacciones breves del narrador insertados durante el relato.

Reglas para el guion completo:
- Empezá con un gancho corto (2-3 frases) que presente que hoy van varias historias, sin arruinar los finales.
- Entre historia e historia, agregá una transición corta y natural del narrador (por ejemplo "bueno, pasemos a la siguiente..."), variando la frase cada vez para que no se repita.
- Cerrá todo el guion con una sola reflexión o pregunta corta para el espectador, que abarque el conjunto.
- Puntuá y acentuá con mucho cuidado (comas, puntos, puntos suspensivos, exclamaciones, interrogaciones, tildes): la voz sintética que lee esto en voz alta solo usa la puntuación para decidir pausas y entonación.

Tono del narrador: {tono}

Historias:
{historias}

Devolvé SOLO el texto final del guion completo y unificado, sin explicaciones, sin numerar ni titular cada historia, sin comillas alrededor. No uses asteriscos, markdown ni emojis."""

# ----- Guion en inglés adaptado (v3.4) -----
# No traduce (el original ya está en inglés): adapta y transforma para que
# cuente como contenido editado/comentado y no una simple lectura del post
# original, con el mismo criterio de monetización que ya se aplicaba al
# guion en español.
PROMPT_GUION_INGLES = """Adapt the following real story (from Reddit or a British forum like Mumsnet/AIBU) into a narrated script. Do NOT just copy the original text: rework the phrasing, add narrator commentary, and restructure it into a proper spoken narration — this needs to read as transformed, commented content, not a verbatim reading of the original post (important for monetisation).

Rules for forum jargon (apply only what's relevant):
- Keep verdict jargon (AITA/AIBU, YTA/YABU, NTA/YANBU) but phrase it naturally as part of the narration, not as raw acronyms.
- Expand kinship acronyms (DH -> my husband, DD -> my daughter, DS -> my son, DP -> my partner, DC -> my child, PIL -> my in-laws, MIL -> my mother-in-law, FIL -> my father-in-law).
- If forum usernames are quoted, don't read them literally if they sound odd out loud; replace with a neutral reference ("someone else replied...", "another commenter said...").

Then:
1. Keep almost all of the story: don't over-summarise, only trim clearly repetitive parts. The length was chosen on purpose for the video's target duration.
2. Add 2-3 brief narrator reactions/comments woven into the story (e.g. "now that's when it got interesting", "I wouldn't have put up with that").
3. Start with a short 1-2 sentence hook explaining why this story was picked.
4. Close with a short reflection or question for the viewer.
5. Punctuate carefully (commas, full stops, ellipses, exclamation and question marks) since the synthetic voice reading this only uses punctuation to decide pauses and tone.

Narrator tone: {tono}

Original story (title: "{titulo}"):
{cuerpo}

Return ONLY the final script text, no explanations or quotes around it. No asterisks, markdown or emojis."""

PROMPT_GUION_INGLES_MULTIPLE = """You're building one narrated script in English that joins several real stories (from Reddit and/or a British forum like Mumsnet/AIBU) back to back, aiming for about 28-30 minutes of narration total. Do NOT just copy the original texts: rework the phrasing, add narrator commentary, and restructure — this needs to read as transformed, commented content, not a verbatim reading (important for monetisation).

Rules for forum jargon (apply only what's relevant per story):
- Keep verdict jargon (AITA/AIBU, YTA/YABU, NTA/YANBU) but phrase it naturally as part of the narration.
- Expand kinship acronyms (DH -> my husband, DD -> my daughter, DS -> my son, DP -> my partner, DC -> my child, PIL -> my in-laws, MIL -> my mother-in-law, FIL -> my father-in-law).
- If forum usernames are quoted, replace with a neutral reference instead of reading them literally.

For each numbered story below:
1. Rework it into narration (don't just copy the original wording).
2. Keep almost all of the story: don't over-summarise, only trim clearly repetitive parts.
3. Add 2-3 brief narrator reactions/comments woven into the story.

Rules for the whole script:
- Start with a short hook (2-3 sentences) letting viewers know several stories are coming, without spoiling the endings.
- Between stories, add a short natural narrator transition (e.g. "alright, moving on to the next one..."), varying the phrase each time.
- Close the whole script with a single reflection or question for the viewer covering all the stories.
- Punctuate carefully: the synthetic voice reading this only uses punctuation to decide pauses and tone.

Narrator tone: {tono}

Stories:
{historias}

Return ONLY the final unified script text, no explanations, no numbering or titling each story, no quotes around it. No asterisks, markdown or emojis."""


def generar_guion_ingles(grupo, tono=TONO_NARRADOR_REDDIT, logger=None):
    """Igual que generar_guion_reddit pero en inglés y SIN traducir (el
    original ya está en inglés): adapta/transforma el texto para que
    cuente como contenido editado y no una copia del post original."""
    if not GEMINI_API_KEY:
        if logger:
            logger.warning("GEMINI_API_KEY vacía: se usa la historia en inglés sin adaptar.")
        return "\n\n".join(h["cuerpo"] for h in grupo)

    if len(grupo) == 1:
        prompt = PROMPT_GUION_INGLES.format(tono=tono, titulo=grupo[0]["titulo"], cuerpo=grupo[0]["cuerpo"])
    else:
        bloques_historias = "\n\n".join(
            f'Story {i + 1} (title: "{h["titulo"]}"):\n{h["cuerpo"]}' for i, h in enumerate(grupo)
        )
        prompt = PROMPT_GUION_INGLES_MULTIPLE.format(tono=tono, historias=bloques_historias)

    intentos_maximos = 4
    espera = 5
    for intento in range(1, intentos_maximos + 1):
        try:
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODELO}:generateContent",
                params={"key": GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=90,
            )
            if resp.status_code == 429:
                espera_real = espera
                try:
                    espera_real = max(espera, int(float(resp.headers.get("Retry-After", espera))))
                except (TypeError, ValueError):
                    pass
                if logger:
                    logger.warning(
                        f"Gemini devolvió 429 (guion inglés). Intento {intento}/{intentos_maximos}, "
                        f"reintentando en {espera_real}s..."
                    )
                if intento < intentos_maximos:
                    time.sleep(espera_real)
                    espera *= 2
                    continue
                resp.raise_for_status()
            resp.raise_for_status()
            datos = resp.json()
            return datos["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            if intento >= intentos_maximos:
                if logger:
                    logger.warning(f"Fallo la generación del guion en inglés tras {intentos_maximos} intentos, se usa el texto original: {e}")
                return "\n\n".join(h["cuerpo"] for h in grupo)
            if logger:
                logger.warning(f"Fallo al llamar a Gemini para guion inglés (intento {intento}/{intentos_maximos}): {e}")
            time.sleep(espera)
            espera *= 2
    return "\n\n".join(h["cuerpo"] for h in grupo)


def generar_guion_reddit(grupo, tono=TONO_NARRADOR_REDDIT, logger=None):
    """Arma el guion final (traducido + adaptado + con comentarios del
    narrador) a partir de un grupo de 1 a 3 historias crudas de Reddit
    (ver obtener_historia_reddit), usando una sola llamada a la API de
    Gemini. Si son varias historias, las une en un solo guion con
    transiciones entre ellas. Si falla o no hay API key configurada,
    devuelve el texto original sin transformar (con aviso en el log) para
    que el resto del pipeline no se caiga."""
    if not GEMINI_API_KEY:
        if logger:
            logger.warning("GEMINI_API_KEY vacía: se usa la historia sin traducir/transformar.")
        return "\n\n".join(h["cuerpo"] for h in grupo)

    if len(grupo) == 1:
        prompt = PROMPT_GUION_REDDIT.format(tono=tono, titulo=grupo[0]["titulo"], cuerpo=grupo[0]["cuerpo"])
    else:
        bloques_historias = "\n\n".join(
            f'Historia {i + 1} (título: "{h["titulo"]}"):\n{h["cuerpo"]}' for i, h in enumerate(grupo)
        )
        prompt = PROMPT_GUION_REDDIT_MULTIPLE.format(tono=tono, historias=bloques_historias)

    # Gemini free tier devuelve 429 (Too Many Requests) cuando se supera el
    # límite de pedidos por minuto — algo fácil de pisar en pruebas
    # seguidas como las que se venían haciendo. Antes, un solo 429 hacía
    # caer directo al texto sin traducir. Ahora se reintenta unas pocas
    # veces con espera creciente (y respetando el header Retry-After si
    # Gemini lo manda) antes de rendirse.
    intentos_maximos = 4
    espera = 5
    for intento in range(1, intentos_maximos + 1):
        try:
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODELO}:generateContent",
                params={"key": GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=90,
            )
            if resp.status_code == 429:
                espera_real = espera
                try:
                    espera_real = max(espera, int(float(resp.headers.get("Retry-After", espera))))
                except (TypeError, ValueError):
                    pass
                if logger:
                    logger.warning(
                        f"Gemini devolvió 429 (límite de pedidos). Intento {intento}/{intentos_maximos}, "
                        f"reintentando en {espera_real}s..."
                    )
                if intento < intentos_maximos:
                    time.sleep(espera_real)
                    espera *= 2
                    continue
                resp.raise_for_status()
            resp.raise_for_status()
            datos = resp.json()
            return datos["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            if intento >= intentos_maximos:
                if logger:
                    logger.warning(f"Fallo la generación del guion con Gemini tras {intentos_maximos} intentos, se usa el texto original: {e}")
                return "\n\n".join(h["cuerpo"] for h in grupo)
            # Fallo que no sea 429 (ej. de red): igual se reintenta, con la
            # misma espera creciente, por si fue algo pasajero.
            if logger:
                logger.warning(f"Fallo al llamar a Gemini (intento {intento}/{intentos_maximos}): {e}")
            time.sleep(espera)
            espera *= 2
    return "\n\n".join(h["cuerpo"] for h in grupo)

# ============================================================
# ---- módulo original: subtitulos.py ----
# ============================================================

# ===================== Subtítulos ASS Dinámicos y Centrados =====================


def _tiempo_ass(segundos):
    h, m, s = int(segundos // 3600), int((segundos % 3600) // 60), segundos % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


COLORES_SUBTITULO = {
    "blanco": "FFFFFF",
    "amarillo_calido": "D9C27E",
    "gris_claro": "D8D8D8",
    "pergamino": "F4EEDC",
    "oro_viejo": "D4AF37",
    "rojo_carmesi": "8B0000"
}


def _ajustar_texto_a_caja(palabras, tamano_max, ancho_caja_px, alto_max_px, tamano_min=14):
    """Dado un ancho y alto máximos en píxeles, encuentra el mayor tamaño de fuente
    (partiendo de tamano_max) con el que el texto, envuelto en líneas, cabe completo.
    Devuelve (tamano_final, lineas) donde lineas es una lista de listas de palabras."""
    tamano = tamano_max
    lineas = [[palabras[0]]] if palabras else [[]]
    while tamano >= tamano_min:
        ancho_char_aprox = tamano * 0.56  # estimación conservadora para fuentes serif
        alto_linea_aprox = tamano * 1.3
        max_chars_linea = max(1, int(ancho_caja_px / ancho_char_aprox))

        lineas = []
        actual = []
        largo_actual = 0
        for palabra in palabras:
            largo_palabra = len(palabra) + (1 if actual else 0)
            if actual and largo_actual + largo_palabra > max_chars_linea:
                lineas.append(actual)
                actual = [palabra]
                largo_actual = len(palabra)
            else:
                actual.append(palabra)
                largo_actual += largo_palabra
        if actual: lineas.append(actual)

        alto_total = alto_linea_aprox * max(1, len(lineas))
        if alto_total <= alto_max_px:
            return tamano, lineas
        tamano -= 2
    return tamano_min, lineas


def generar_ass_estoico(bloques_con_tiempos, posicion, color, tamano_sub, nombre_fuente, animacion, ruta_ass, opacidad_sub=100, ancho_caja_pct=None, pos_y_pct=None):
    color_hex = COLORES_SUBTITULO.get(color, COLORES_SUBTITULO["blanco"])

    if color in ["blanco", "gris_claro", "pergamino"]:
        color_base = "888888"
    else:
        color_base = "CCCCCC"

    # Opacidad del subtítulo: 100 = totalmente opaco (alpha 00 en ASS), valores
    # menores van subiendo el canal alfa hacia FF (transparente). Se aplica por
    # igual al color principal y al color "atenuado" que se usa antes de que
    # cada palabra se resalte, para que la transparencia sea pareja en todo momento.
    try:
        opacidad_sub = max(10, min(100, int(float(opacidad_sub))))
    except (TypeError, ValueError):
        opacidad_sub = 100
    alpha_hex = f"{int(round((100 - opacidad_sub) / 100 * 255)):02X}"

    primary = f"&H{alpha_hex}{color_hex[4:6]}{color_hex[2:4]}{color_hex[0:2]}&"
    base_bgr = f"&H{alpha_hex}{color_base[4:6]}{color_base[2:4]}{color_base[0:2]}&"

    # Coordenadas ancladas al centro exacto
    x_centro = RESOLUCION_ANCHO // 2
    margen_borde = 40
    try:
        ancho_caja_pct = max(20, min(95, int(float(ancho_caja_pct)))) if ancho_caja_pct is not None else None
    except (TypeError, ValueError):
        ancho_caja_pct = None
    try:
        pos_y_pct = max(5, min(90, int(float(pos_y_pct)))) if pos_y_pct is not None else None
    except (TypeError, ValueError):
        pos_y_pct = None

    ancho_caja = int(RESOLUCION_ANCHO * (ancho_caja_pct / 100)) if ancho_caja_pct else int(RESOLUCION_ANCHO * 0.5)  # ancho de la "caja" (ajustable arrastrando los costados)
    alto_caja_max = int(RESOLUCION_ALTO * 0.65)  # altura máxima permitida para el bloque de texto

    alineacion = 5  # 5 = centro (por defecto, para centro/abajo)
    margen_l, margen_r = 20, 20
    if posicion == "izquierda":
        alineacion = 4  # 4 = medio-izquierda: el texto crece hacia la derecha desde el ancla
        x_centro = margen_borde
        y_centro = int(RESOLUCION_ALTO * (pos_y_pct / 100)) if pos_y_pct is not None else RESOLUCION_ALTO // 2
        margen_l, margen_r = margen_borde, RESOLUCION_ANCHO - ancho_caja - margen_borde
    elif posicion == "derecha":
        alineacion = 6  # 6 = medio-derecha: el texto crece hacia la izquierda desde el ancla
        x_centro = RESOLUCION_ANCHO - margen_borde
        y_centro = int(RESOLUCION_ALTO * (pos_y_pct / 100)) if pos_y_pct is not None else RESOLUCION_ALTO // 2
        margen_l, margen_r = RESOLUCION_ANCHO - ancho_caja - margen_borde, margen_borde
    elif posicion == "centro":
        y_centro = int(RESOLUCION_ALTO * (pos_y_pct / 100)) if pos_y_pct is not None else RESOLUCION_ALTO // 2
        ancho_caja = int(RESOLUCION_ANCHO * (ancho_caja_pct / 100)) if ancho_caja_pct else RESOLUCION_ANCHO - margen_l - margen_r
        margen_l = margen_r = (RESOLUCION_ANCHO - ancho_caja) // 2
    else:  # abajo
        y_centro = int(RESOLUCION_ALTO * (pos_y_pct / 100)) if pos_y_pct is not None else int(RESOLUCION_ALTO * 0.8)
        ancho_caja = int(RESOLUCION_ANCHO * (ancho_caja_pct / 100)) if ancho_caja_pct else RESOLUCION_ANCHO - margen_l - margen_r
        margen_l = margen_r = (RESOLUCION_ANCHO - ancho_caja) // 2

    pos_tag = f"{{\\pos({x_centro},{y_centro})}}"

    encabezado = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {RESOLUCION_ANCHO}\nPlayResY: {RESOLUCION_ALTO}\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        # Alineación dinámica: 5=centro para centro/abajo, 4/6=izquierda/derecha ancladas a caja fija
        f"Style: Default,{nombre_fuente},{tamano_sub},{primary},&H000000FF&,&H{alpha_hex}000000&,&H{alpha_hex}000000&,"
        f"-1,-1,0,0,100,100,1,0,1,3,1,{alineacion},{margen_l},{margen_r},0,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    lineas_dialogo = []
    for bloque, inicio, fin, sub_palabras in bloques_con_tiempos:
        palabras_bloque = [p["texto"] for p in sub_palabras] if sub_palabras else bloque.split()
        tamano_final, lineas_palabras = _ajustar_texto_a_caja(palabras_bloque, tamano_sub, ancho_caja, alto_caja_max)
        fs_tag = f"{{\\fs{tamano_final}}}"
        # Mapa palabra -> número de línea, para insertar \N en el lugar correcto durante el karaoke
        linea_de_palabra = {}
        idx = 0
        for n_linea, grupo in enumerate(lineas_palabras):
            for _ in grupo:
                linea_de_palabra[idx] = n_linea
                idx += 1

        if animacion == "dinamico" and sub_palabras:
            tiempo_actual = inicio
            for i, palabra_info in enumerate(sub_palabras):
                p_inicio = palabra_info["inicio"]
                p_fin = palabra_info["fin"]

                if tiempo_actual < p_inicio:
                    texto_base = "\\N".join(" ".join(g) for g in lineas_palabras)
                    lineas_dialogo.append(
                        f"Dialogue: 0,{_tiempo_ass(tiempo_actual)},{_tiempo_ass(p_inicio)},Default,,0,0,0,,{pos_tag}{fs_tag}{{\\blur2\\c{base_bgr}}}{texto_base}\n"
                    )

                texto_karaoke = ""
                for j, p2 in enumerate(sub_palabras):
                    if j > 0 and linea_de_palabra.get(j) != linea_de_palabra.get(j - 1):
                        texto_karaoke += "\\N"
                    elif j > 0:
                        texto_karaoke += " "
                    if j == i:
                        texto_karaoke += f"{{\\c{primary}\\fscx108\\fscy108}}{p2['texto']}{{\\fscx100\\fscy100\\c{base_bgr}}}"
                    else:
                        texto_karaoke += p2['texto']

                lineas_dialogo.append(
                    f"Dialogue: 0,{_tiempo_ass(p_inicio)},{_tiempo_ass(p_fin)},Default,,0,0,0,,{pos_tag}{fs_tag}{{\\blur2\\c{base_bgr}}}{texto_karaoke}\n"
                )
                tiempo_actual = p_fin

            if tiempo_actual < fin:
                texto_base = "\\N".join(" ".join(g) for g in lineas_palabras)
                lineas_dialogo.append(
                    f"Dialogue: 0,{_tiempo_ass(tiempo_actual)},{_tiempo_ass(fin)},Default,,0,0,0,,{pos_tag}{fs_tag}{{\\blur2\\c{base_bgr}}}{texto_base}\n"
                )
        else:
            texto_ass = "\\N".join(" ".join(g) for g in lineas_palabras)
            lineas_dialogo.append(
                f"Dialogue: 0,{_tiempo_ass(inicio)},{_tiempo_ass(fin)},Default,,0,0,0,,{pos_tag}{fs_tag}{{\\blur2\\fad(400,400)\\c{primary}}}{texto_ass}\n"
            )

    with open(ruta_ass, "w", encoding="utf-8") as f:
        f.write(encabezado)
        f.writelines(lineas_dialogo)

# ============================================================
# ---- módulo original: video.py ----
# ============================================================
import os
import time
import random
import shutil
import subprocess


# ===================== Video =====================


def _construir_zoom_multifase(duracion, fps=None, zoom_max=1.16):
    """Arma un movimiento de camara con varias fases (zoom-in, pan izquierda,
    pan derecha, pan arriba, pan abajo, zoom-out) para el fondo estatico.

    La duracion de cada fase se calcula a partir de la duracion total del
    video (mas video, fases un poco mas largas, hasta un tope), y todo el
    ciclo se repite en loop durante el video completo (mod), asi que un
    video de 30 minutos no se queda quieto despues del primer ciclo.
    Devuelve las expresiones de zoompan (z, x, y) listas para usar."""
    fps = fps or FPS
    d_zoom = max(3.0, min(6.0, duracion * 0.15))
    d_pan = max(3.0, min(6.0, duracion * 0.12))

    b1 = d_zoom
    b2 = b1 + d_pan
    b3 = b2 + d_pan
    b4 = b3 + d_pan
    b5 = b4 + d_pan
    b6 = b5 + d_zoom

    f = lambda s: max(1, round(s * fps))
    b1f, b2f, b3f, b4f, b5f, b6f = f(b1), f(b2), f(b3), f(b4), f(b5), f(b6)
    Z = zoom_max
    m = f"mod(on,{b6f})"

    expr_z = (
        f"if(lt({m},{b1f}),1+{Z - 1:.5f}*({m}/{b1f}),"
        f"if(lt({m},{b5f}),{Z:.5f},"
        f"{Z:.5f}-{Z - 1:.5f}*(({m}-{b5f})/{b6f - b5f})))"
    )
    H = (
        f"if(lt({m},{b1f}),0,"
        f"if(lt({m},{b2f}),-0.7*(({m}-{b1f})/{b2f - b1f}),"
        f"if(lt({m},{b3f}),-0.7+1.4*(({m}-{b2f})/{b3f - b2f}),"
        f"if(lt({m},{b4f}),0.7*(1-(({m}-{b3f})/{b4f - b3f})),0))))"
    )
    V = (
        f"if(lt({m},{b3f}),0,"
        f"if(lt({m},{b4f}),-0.6*(({m}-{b3f})/{b4f - b3f}),"
        f"if(lt({m},{b5f}),-0.6*(1-(({m}-{b4f})/{b5f - b4f})),0)))"
    )
    expr_x = f"(iw*(1-1/zoom))/2*(1+({H}))"
    expr_y = f"(ih*(1-1/zoom))/2*(1+({V}))"
    return expr_z, expr_x, expr_y


def generar_segmento_imagen(ruta_imagen, duracion, ruta_salida, logger=None):
    duracion = max(0.5, duracion)
    frames = max(1, int(duracion * FPS))
    zoom_objetivo = round(random.uniform(1.06, 1.10), 3)
    modo = random.choice(["in", "out"])
    if modo == "in": expr_zoom = f"min(zoom+{zoom_objetivo - 1.0:.5f}/{frames},{zoom_objetivo})"
    else: expr_zoom = f"if(eq(on,1),{zoom_objetivo},max(zoom-{zoom_objetivo - 1.0:.5f}/{frames},1.0))"

    # Optimización: Limitamos a 1536 de ancho (un poco más que 720p) para ahorrar RAM
    filtro = (
        f"scale=1536:-1,"
        f"zoompan=z='{expr_zoom}':d={frames}:s={RESOLUCION_ANCHO}x{RESOLUCION_ALTO}:fps={FPS},"
        f"drawbox=x=0:y=0:w={RESOLUCION_ANCHO}:h={RESOLUCION_ALTO}:color=black@0.38:t=fill,"
        f"format=yuv420p"
    )

    cmd = ["ffmpeg", "-y", "-threads", "4", "-loop", "1", "-i", ruta_imagen, "-t", str(duracion), "-vf", filtro, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", ruta_salida]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def generar_segmento_imagen_estatico(ruta_imagen, duracion, ruta_salida, logger=None):
    """Genera el fondo para el modo 'fondo fijo': una sola imagen que se mantiene durante
    todo el video, con un movimiento de camara de varias fases (zoom-in, pan
    en las 4 direcciones, zoom-out) que se repite en loop durante todo el
    video, con duracion de fases calculada segun la duracion total."""
    duracion = max(0.5, duracion)
    frames = max(1, int(duracion * FPS))
    expr_z, expr_x, expr_y = _construir_zoom_multifase(duracion)

    filtro = (
        f"scale=1536:-1,"
        f"zoompan=z='{expr_z}':x='{expr_x}':y='{expr_y}':d={frames}:s={RESOLUCION_ANCHO}x{RESOLUCION_ALTO}:fps={FPS},"
        f"drawbox=x=0:y=0:w={RESOLUCION_ANCHO}:h={RESOLUCION_ALTO}:color=black@0.38:t=fill,"
        f"format=yuv420p"
    )
    cmd = ["ffmpeg", "-y", "-threads", "4", "-loop", "1", "-i", ruta_imagen, "-t", str(duracion), "-vf", filtro, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", ruta_salida]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def obtener_imagen_predeterminada(logger=None, carpeta_imagenes_stock=None):
    """Si no se sube ni configura nada, se usa siempre esta misma imagen: se
    descarga de Pexels UNA sola vez la primera vez que se usa, y de ahí en
    adelante queda guardada para siempre (no se vuelve a descargar)."""
    carpeta_imagenes_stock = carpeta_imagenes_stock or CARPETA_IMAGENES_STOCK
    ruta = os.path.join(carpeta_imagenes_stock, "_predeterminada.jpg")
    if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
        return ruta
    usadas = set()
    for termino in TERMINOS_STOCK_FONDO:
        url = _buscar_foto_pexels(termino, evitar=usadas) or _buscar_foto_pixabay(termino, evitar=usadas)
        if url:
            try:
                import requests
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                with open(ruta, "wb") as f: f.write(r.content)
                if logger: logger.info("Imagen de fondo predeterminada descargada y guardada para siempre.")
                return ruta
            except Exception:
                continue
    return None


def descargar_varias_imagenes_stock(cantidad, logger=None):
    """Descarga 'cantidad' imágenes distintas de Pexels/Pixabay para repartir
    en partes iguales a lo largo del video (no quedan guardadas para siempre,
    se piden nuevas cada vez que se usa esta opción)."""
    usadas = set()
    imagenes = []
    for i in range(max(1, cantidad)):
        ruta = obtener_imagen_stock(i, usadas, logger=logger)
        if ruta: imagenes.append(ruta)
    return imagenes


def generar_video_multi_imagen_transicion(rutas_imagenes, duracion_total, ruta_salida, logger=None, transicion=0.7):
    """Reparte 'duracion_total' en partes iguales entre las imágenes dadas y
    las une con un desvanecimiento suave (0.5 a 1 seg) entre cada una."""
    rutas_imagenes = [r for r in rutas_imagenes if r and os.path.exists(r)]
    n = len(rutas_imagenes)
    if n == 0: return False
    if n == 1: return generar_segmento_imagen_estatico(rutas_imagenes[0], duracion_total, ruta_salida, logger=logger)

    duracion_parte = duracion_total / n
    transicion = max(0.5, min(transicion, 1.0, duracion_parte / 2))
    carpeta_temp = os.path.dirname(ruta_salida)

    segmentos = []
    for i, img in enumerate(rutas_imagenes):
        ruta_seg = os.path.join(carpeta_temp, f"_multi_{i}_{int(time.time())}.mp4")
        if generar_segmento_imagen_estatico(img, duracion_parte + transicion, ruta_seg, logger=logger):
            segmentos.append(ruta_seg)

    if not segmentos: return False
    if len(segmentos) == 1:
        shutil.copy(segmentos[0], ruta_salida)
        return True

    inputs_cmd = []
    for s in segmentos: inputs_cmd += ["-i", s]
    partes_filtro = []
    etiqueta_previa = "0:v"
    offset_acumulado = duracion_parte
    for i in range(1, len(segmentos)):
        etiqueta_salida = f"v{i}" if i < len(segmentos) - 1 else "vout"
        partes_filtro.append(f"[{etiqueta_previa}][{i}:v]xfade=transition=fade:duration={transicion:.2f}:offset={offset_acumulado:.2f}[{etiqueta_salida}]")
        etiqueta_previa = etiqueta_salida
        offset_acumulado += duracion_parte

    cmd = ["ffmpeg", "-y"] + inputs_cmd + ["-filter_complex", ";".join(partes_filtro), "-map", "[vout]", "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", ruta_salida]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    ok = resultado.returncode == 0
    if not ok and logger:
        logger.error(f"ffmpeg (transición entre varias imágenes) devolvió error:\n{resultado.stderr[-2000:]}")
    for s in segmentos:
        try: os.remove(s)
        except Exception: pass
    return ok


def _normalizar_velocidad_efecto(velocidad_efecto):
    try:
        v = float(velocidad_efecto)
    except (TypeError, ValueError):
        v = VELOCIDAD_EFECTO_POR_DEFECTO
    return max(VELOCIDAD_EFECTO_MIN, min(VELOCIDAD_EFECTO_MAX, v))


def aplicar_efecto_video(ruta_entrada, ruta_salida, efecto, duracion, velocidad_efecto=VELOCIDAD_EFECTO_POR_DEFECTO, logger=None):
    """Aplica un efecto visual liviano sobre el video ya armado (con subtítulos
    quemados). Si el efecto falla por algún motivo, se sigue con el video
    original sin efecto en vez de romper todo el proceso.

    'velocidad_efecto' solo tiene efecto real en los dos únicos efectos con
    movimiento en el tiempo (ceniza y vela); el resto son filtros estáticos
    y lo ignoran."""
    if not efecto or efecto == "ninguno":
        return ruta_entrada

    velocidad = _normalizar_velocidad_efecto(velocidad_efecto)

    filtros_simples = {
        "vineta": "vignette=PI/4",
        "grano_pelicula": "noise=alls=14:allf=t+u",
        # El período del parpadeo (2s por defecto) se divide por la velocidad:
        # con velocidad 2.0 el parpadeo dura la mitad (más rápido), con 0.5 el doble (más lento).
        "vela": f"eq=brightness='0.05*sin(2*PI*t/{max(0.4, 2.0 / velocidad):.4f})':eval=frame",
        "niebla": "geq=lum='lum(X,Y)+35*(Y/H)':cb='cb(X,Y)':cr='cr(X,Y)'",
        "rayo_luz": "geq=lum='lum(X,Y)+25*exp(-((X-0.5*Y-0.2*W)/180)^2)':cb='cb(X,Y)':cr='cr(X,Y)'",
        "pergamino": "colorbalance=rs=0.15:gs=0.05:bs=-0.15,eq=saturation=0.85",
    }

    if efecto in filtros_simples:
        cmd = ["ffmpeg", "-y", "-i", ruta_entrada, "-vf", filtros_simples[efecto],
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", "-c:a", "copy", ruta_salida]
    elif efecto == "ceniza":
        # Rediseño del efecto (2 iteraciones de calibración con ffmpeg real):
        #
        # 1) La primera versión usaba blend=screen directo sobre YUV, lo que
        #    mezcla también la crominancia y termina TIÑENDO toda la pantalla
        #    de violeta parejo (comprobado con ffmpeg real: un blend "screen"
        #    de gris sobre negro puro en YUV da como resultado color, no
        #    gris). Se corrige generando las partículas como una capa blanca
        #    con canal alfa (alphamerge) y componiéndolas con 'overlay'
        #    (compositing por alpha), que no tiene ese problema.
        # 2) El umbral de ruido original (pensado para 'alls', 0-255) estaba
        #    mal calibrado para 'c0s' (que en la práctica nunca pasa de
        #    ~150): con esos valores no aparecía ninguna partícula. Se
        #    recalibraron los umbrales contra el rango real del filtro.
        #    Además, generar el ruido a baja resolución y escalarlo hacia
        #    arriba (en vez de a resolución completa) agrupa el ruido en
        #    motas redondeadas y dispersas en vez de una alfombra de
        #    estática fina — así se ve a partículas de ceniza cayendo, no a
        #    ruido de TV.
        #
        # Dos capas de profundidad: partículas lejanas (chicas, dispersas,
        # lentas) y cercanas (más grandes, un poco más densas y rápidas).
        # 'velocidad' escala la caída de ambas por igual.
        capa_blanco_lejos = f"color=c=white:s={RESOLUCION_ANCHO}x{RESOLUCION_ALTO}:d={duracion}"
        capa_alfa_lejos = (
            f"color=c=black:s=240x135:d={duracion},"
            f"noise=c0s=100:c0f=t,lutyuv=y='if(gt(val,138),255,0)',"
            f"scale={RESOLUCION_ANCHO}x{RESOLUCION_ALTO},gblur=sigma=1.5,"
            f"scroll=vertical={0.012 * velocidad:.5f},format=gray"
        )
        capa_blanco_cerca = f"color=c=white:s={RESOLUCION_ANCHO}x{RESOLUCION_ALTO}:d={duracion}"
        capa_alfa_cerca = (
            f"color=c=black:s=320x180:d={duracion},"
            f"noise=c0s=100:c0f=t,lutyuv=y='if(gt(val,133),255,0)',"
            f"scale={RESOLUCION_ANCHO}x{RESOLUCION_ALTO},gblur=sigma=0.9,"
            f"scroll=vertical={0.030 * velocidad:.5f},format=gray"
        )
        cmd = ["ffmpeg", "-y", "-i", ruta_entrada,
               "-f", "lavfi", "-i", capa_blanco_lejos,
               "-f", "lavfi", "-i", capa_alfa_lejos,
               "-f", "lavfi", "-i", capa_blanco_cerca,
               "-f", "lavfi", "-i", capa_alfa_cerca,
               "-filter_complex",
               "[1:v][2:v]alphamerge,colorchannelmixer=aa=0.55[lejos];"
               "[3:v][4:v]alphamerge,colorchannelmixer=aa=0.7[cerca];"
               "[0:v][lejos]overlay=format=auto[tmp];"
               "[tmp][cerca]overlay=format=auto[vout]",
               "-map", "[vout]", "-map", "0:a?",
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", "-c:a", "copy", ruta_salida]
    else:
        return ruta_entrada

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        if logger:
            logger.error(f"ffmpeg (efecto de video '{efecto}') devolvió error, se sigue sin efecto:\n{resultado.stderr[-2000:]}")
        return ruta_entrada
    return ruta_salida


def concatenar_segmentos(rutas_segmentos, ruta_salida, logger=None):
    ruta_lista = ruta_salida + "_lista.txt"
    with open(ruta_lista, "w", encoding="utf-8") as f:
        for ruta in rutas_segmentos: f.write(f"file '{os.path.abspath(ruta)}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", ruta_lista, "-c", "copy", ruta_salida]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def quemar_subtitulos(ruta_video_in, ruta_ass, carpeta_fuentes_abs, ruta_video_out, logger=None):
    cmd = ["ffmpeg", "-y", "-threads", "4", "-i", ruta_video_in, "-vf", f"ass={ruta_ass}:fontsdir={carpeta_fuentes_abs}", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", "-c:a", "copy", ruta_video_out]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def mezclar_audio_final(ruta_video_sin_audio, ruta_voz, ruta_musica, volumen_musica, ruta_salida, logger=None):
    if ruta_musica:
        filtro = f"[1:a]volume=1.0[voz];[2:a]volume={volumen_musica / 100:.2f}[mus];[voz][mus]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        cmd = ["ffmpeg", "-y", "-i", ruta_video_sin_audio, "-i", ruta_voz, "-stream_loop", "-1", "-i", ruta_musica, "-filter_complex", filtro, "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-shortest", ruta_salida]
    else:
        cmd = ["ffmpeg", "-y", "-i", ruta_video_sin_audio, "-i", ruta_voz, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", ruta_salida]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0 and logger:
        logger.error(f"ffmpeg (mezcla final de audio) devolvió error:\n{resultado.stderr[-2000:]}")
    return resultado.returncode == 0

# ============================================================
# ---- módulo original: procesamiento.py ----
# ============================================================
import os
import re
import time
import subprocess
import threading
import traceback
from datetime import datetime


# ===================== Estado global =====================

CANDADO_ESTADO = threading.Lock()
ESTADO = {
    "activo": False, "terminado": False, "fase": "inactivo", "porcentaje": 0,
    "resultado": {"mensaje": None, "video": None},
    # ---- Cronometraje (tiempos por fase y total) ----
    "tiempo_inicio_video": None,   # epoch: cuándo arrancó este video
    "tiempo_fase_inicio": None,    # epoch: cuándo arrancó la fase actual
    "tiempos_fases": {},           # {"nombre fase": segundos_que_tardó, ...}
    "tiempo_total": None,          # segundos que tardó el video completo (una vez terminado)
}


def _cerrar_fase_actual():
    """Calcula cuánto duró la fase que estaba corriendo y lo suma a
    tiempos_fases. Debe llamarse ya con CANDADO_ESTADO tomado. Devuelve el
    instante actual, para reutilizarlo como inicio de la fase siguiente."""
    ahora = time.time()
    fase_actual = ESTADO.get("fase")
    inicio_fase = ESTADO.get("tiempo_fase_inicio")
    if fase_actual and inicio_fase:
        duracion = round(ahora - inicio_fase, 1)
        tiempos = ESTADO.setdefault("tiempos_fases", {})
        tiempos[fase_actual] = round(tiempos.get(fase_actual, 0) + duracion, 1)
    return ahora


def actualizar_fase(fase, porcentaje, logger=None):
    with CANDADO_ESTADO:
        # Si la fase cambió de nombre, se cierra (cronometra) la anterior y
        # arranca el cronómetro de la nueva. Si es la misma fase avisando un
        # % más alto (como hace _ProgresoSuave), el cronómetro sigue corriendo.
        if ESTADO.get("fase") != fase:
            ESTADO["tiempo_fase_inicio"] = _cerrar_fase_actual()
        ESTADO["fase"] = fase
        ESTADO["porcentaje"] = max(0, min(99, porcentaje))
    if logger:
        logger.info(f"Fase: {fase} ({ESTADO['porcentaje']}%)")


class _ProgresoSuave:
    """Durante un paso largo de ffmpeg (que no avisa su propio avance), esto
    va subiendo el porcentaje solo, de a poquito, para que la barra no se
    quede pegada en un número fijo y luego salte de golpe."""
    def __init__(self, fase, inicio, fin, logger=None, duracion_estimada=25):
        self.fase, self.inicio, self.fin = fase, inicio, fin
        self.logger, self.duracion_estimada = logger, duracion_estimada
        self._detener = threading.Event()
        self._hilo = None

    def __enter__(self):
        actualizar_fase(self.fase, self.inicio, logger=self.logger)
        def _tick():
            paso = 0
            pasos_totales = max(1, self.duracion_estimada * 2)
            while not self._detener.is_set() and paso < pasos_totales:
                time.sleep(0.5)
                paso += 1
                pct = self.inicio + int((self.fin - self.inicio) * (paso / pasos_totales))
                actualizar_fase(self.fase, min(pct, self.fin - 1))
        self._hilo = threading.Thread(target=_tick, daemon=True)
        self._hilo.start()
        return self

    def __exit__(self, *a):
        self._detener.set()
        if self._hilo:
            self._hilo.join(timeout=1)
        actualizar_fase(self.fase, self.fin, logger=self.logger)


def generar_nombre_archivo(texto):
    lineas = [l.strip() for l in texto.split("\n") if l.strip()]
    primera = lineas[0][:40] if lineas else "estoico"
    limpio = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]", "", primera).strip().replace(" ", "_")
    return limpio or "estoico"


def procesar_todo(texto_bruto, frases_por_bloque, posicion, color_sub, tamano_sub, fuente_sub,
                   musica_genero, volumen_musica, rutas_imagenes_subidas, animacion,
                   traducir_auto=False, fondo_fijo=False, velocidad_voz=None, tono_voz=None,
                   opacidad_sub=100, cantidad_imagenes_descargar=0, ancho_sub_pct=None, pos_y_pct=None,
                   efecto_video="ninguno", velocidad_efecto=VELOCIDAD_EFECTO_POR_DEFECTO, logger=None, ruta_log=None):
    if logger is None:
        logger, ruta_log = crear_logger_video()
    LOGGER_VIDEO_ACTIVO["logger"], LOGGER_VIDEO_ACTIVO["ruta"] = logger, ruta_log
    logger.info("Arrancó el procesamiento del video en el hilo de trabajo.")
    try:
        if traducir_auto:
            actualizar_fase("traduciendo texto", 4, logger=logger)
            texto_bruto = traducir_texto_deepl(texto_bruto, "es", logger=logger)

        actualizar_fase("preparando texto", 8, logger=logger)
        texto_limpio = limpiar_texto_para_voz(texto_bruto)
        bloques = dividir_en_bloques(texto_limpio, frases_por_bloque=frases_por_bloque)
        if not bloques: raise ValueError("El guion quedó vacío.")

        nombre_base = generar_nombre_archivo(texto_bruto)
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Carpeta de proyecto de este video: todo lo que se genera para este
        # video en particular (voz, imagen, subtítulos, efecto, y el video
        # final) queda adentro, separado por tipo, en vez de mezclado con
        # los archivos de otros videos.
        proyecto = crear_carpeta_proyecto(nombre_base, marca)

        actualizar_fase("generando voz", 18, logger=logger)
        voz = VOZ_NARRADOR
        velocidad_final = _formatear_ajuste_voz(velocidad_voz, "%", VELOCIDAD_VOZ_POR_DEFECTO, VELOCIDAD_VOZ_MIN, VELOCIDAD_VOZ_MAX)
        tono_final = _formatear_ajuste_voz(tono_voz, "Hz", TONO_VOZ_POR_DEFECTO, TONO_VOZ_MIN, TONO_VOZ_MAX)
        ruta_audio = os.path.join(proyecto["voz"], "voz.mp3")
        logger.info(f"Motor de voz: edge_tts | voz={voz} | velocidad={velocidad_final} | tono={tono_final}")
        palabras_tiempos = generar_audio_y_tiempos(texto_limpio, voz, ruta_audio, logger=logger, tono=tono_final, velocidad=velocidad_final)
        duracion_total = obtener_duracion_audio(ruta_audio)

        tiempos_bloques = calcular_tiempos_de_bloques(bloques, palabras_tiempos, duracion_total)

        # Los intermedios "de imagen" (fondo sin subtítulos todavía) viven en
        # la subcarpeta imagen/ del proyecto.
        carpeta_temp = proyecto["imagen"]
        segmentos = []

        if fondo_fijo:
            # Modo "fondo fijo": una o varias imágenes quietas, repartidas en
            # partes iguales según la duración exacta del video, con un
            # desvanecimiento suave entre ellas si hay más de una.
            actualizar_fase("preparando imágenes", 25, logger=logger)
            if rutas_imagenes_subidas:
                imagenes_para_fondo = rutas_imagenes_subidas
            elif cantidad_imagenes_descargar and cantidad_imagenes_descargar > 1:
                imagenes_para_fondo = descargar_varias_imagenes_stock(cantidad_imagenes_descargar, logger=logger)
            else:
                imagenes_para_fondo = [obtener_imagen_predeterminada(logger=logger)]
            imagenes_para_fondo = [p for p in imagenes_para_fondo if p and os.path.exists(p)]

            ruta_seg = os.path.join(carpeta_temp, "seg_fijo.mp4")
            with _ProgresoSuave("generando fondo", 40, 65, logger=logger, duracion_estimada=int(duracion_total / 8)):
                if imagenes_para_fondo:
                    ok = generar_video_multi_imagen_transicion(imagenes_para_fondo, duracion_total, ruta_seg, logger=logger)
                else:
                    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={RESOLUCION_ANCHO}x{RESOLUCION_ALTO}:d={duracion_total}", "-r", str(FPS), ruta_seg]
                    ok = subprocess.run(cmd, capture_output=True, text=True).returncode == 0
            if ok: segmentos.append(ruta_seg)
        else:
            actualizar_fase("preparando imágenes", 25, logger=logger)
            usadas = set()
            rutas_imagenes = []
            for i in range(len(bloques)):
                if rutas_imagenes_subidas:
                    rutas_imagenes.append(rutas_imagenes_subidas[i % len(rutas_imagenes_subidas)])
                else:
                    rutas_imagenes.append(obtener_imagen_stock(i, usadas, logger=logger))

            actualizar_fase("generando fondo", 35, logger=logger)
            for i, (bloque, inicio, fin, sub_palabras) in enumerate(tiempos_bloques):
                duracion_bloque = max(0.5, fin - inicio)
                ruta_seg = os.path.join(carpeta_temp, f"seg_{i}.mp4")
                imagen = rutas_imagenes[i]
                if imagen and os.path.exists(imagen):
                    ok = generar_segmento_imagen(imagen, duracion_bloque, ruta_seg, logger=logger)
                else:
                    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={RESOLUCION_ANCHO}x{RESOLUCION_ALTO}:d={duracion_bloque}", "-r", str(FPS), ruta_seg]
                    ok = subprocess.run(cmd, capture_output=True, text=True).returncode == 0
                if ok: segmentos.append(ruta_seg)
                actualizar_fase("generando fondo", 35 + int(30 * (i + 1) / len(tiempos_bloques)), logger=logger)

        if not segmentos: raise RuntimeError("No se pudo generar el video.")

        with _ProgresoSuave("uniendo escenas", 68, 76, logger=logger, duracion_estimada=int(duracion_total / 15)):
            ruta_video_base = os.path.join(carpeta_temp, "base.mp4")
            concatenar_segmentos(segmentos, ruta_video_base, logger=logger)

        nombre_fuente_ok = asegurar_fuente(fuente_sub) or FUENTE_POR_DEFECTO
        ruta_ass = os.path.join(proyecto["subtitulos"], "subs.ass")

        generar_ass_estoico(tiempos_bloques, posicion, color_sub, tamano_sub, nombre_fuente_ok, animacion, ruta_ass, opacidad_sub=opacidad_sub, ancho_caja_pct=ancho_sub_pct, pos_y_pct=pos_y_pct)

        with _ProgresoSuave("quemando subtítulos", 78, 86, logger=logger, duracion_estimada=int(duracion_total / 10)):
            ruta_video_subs = os.path.join(proyecto["subtitulos"], "con_subs.mp4")
            quemar_subtitulos(ruta_video_base, ruta_ass, os.path.abspath(CARPETA_FUENTES), ruta_video_subs, logger=logger)

        with _ProgresoSuave("aplicando efecto", 86, 90, logger=logger, duracion_estimada=int(duracion_total / 12)):
            ruta_video_efecto = os.path.join(proyecto["efecto"], "con_efecto.mp4")
            ruta_video_lista = aplicar_efecto_video(ruta_video_subs, ruta_video_efecto, efecto_video, duracion_total, velocidad_efecto=velocidad_efecto, logger=logger)

        ruta_musica = seleccionar_musica_fondo(musica_genero)
        nombre_final = f"{nombre_base}_{marca}_estoico.mp4"
        ruta_final = os.path.join(proyecto["raiz"], nombre_final)
        with _ProgresoSuave("mezclando audio", 90, 98, logger=logger, duracion_estimada=int(duracion_total / 15)):
            exito_mezcla = mezclar_audio_final(ruta_video_lista, ruta_audio, ruta_musica, volumen_musica, ruta_final, logger=logger)
        if not exito_mezcla or not os.path.exists(ruta_final) or os.path.getsize(ruta_final) == 0:
            raise RuntimeError(
                "Falló la mezcla final de audio y video (ffmpeg no generó el archivo). "
                "Revisá el log de esta corrida para ver el error exacto de ffmpeg."
            )

        # La ruta que ve el navegador incluye la carpeta del proyecto (ej.
        # "mi_video_20260804_195000/mi_video_20260804_195000_estoico.mp4"),
        # ya que el video final ahora vive adentro de esa carpeta y no
        # suelto en videos_estoico/.
        ruta_relativa_video = f"{proyecto['nombre_proyecto']}/{nombre_final}"

        with CANDADO_ESTADO:
            _cerrar_fase_actual()
            ESTADO["porcentaje"], ESTADO["fase"], ESTADO["terminado"], ESTADO["activo"] = 100, "listo", True, False
            ESTADO["resultado"] = {"mensaje": "Éxito.", "video": ruta_relativa_video}
            if ESTADO.get("tiempo_inicio_video"):
                ESTADO["tiempo_total"] = round(time.time() - ESTADO["tiempo_inicio_video"], 1)
        logger.info(f"✅ Video terminado con éxito: {ruta_relativa_video} (tiempo total: {ESTADO['tiempo_total']}s)")
        logger.info(f"Tiempos por fase: {ESTADO['tiempos_fases']}")
    except Exception as e:
        with CANDADO_ESTADO:
            _cerrar_fase_actual()
            ESTADO["terminado"], ESTADO["activo"], ESTADO["fase"] = True, False, "error"
            ESTADO["resultado"] = {"mensaje": f"Error: {e}", "video": None}
            if ESTADO.get("tiempo_inicio_video"):
                ESTADO["tiempo_total"] = round(time.time() - ESTADO["tiempo_inicio_video"], 1)
        logger.error(f"❌ Falló la generación del video: {e}")
        logger.error(traceback.format_exc())
    finally:
        LOGGER_VIDEO_ACTIVO["logger"], LOGGER_VIDEO_ACTIVO["ruta"] = None, None
        cerrar_logger_video(logger)

# ============================================================
# ---- módulo original: web.py ----
# ============================================================
import os
import time
import threading
import random

from flask import Blueprint, jsonify, request, render_template_string, send_from_directory, make_response, redirect, url_for


reddit_bp = Blueprint("reddit", __name__)

# =====================================================================
# INTERFAZ WEB
# =====================================================================

PLANTILLA = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>V{{ version }} STORY ENGINE</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&display=swap');
    :root {
        --bg:#150e2b; --bg-elev:#1f1640; --surface:#2a1f52; --border:#4a3a7a;
        --text:#f4f0ff; --text-dim:#c9bdea; --text-muted:#9686c0;
        --accent:#ff2e88; --accent-soft:rgba(255,46,136,0.16); --accent-deep:#c4116a;
        --accent2:#00e5ff; --accent3:#d4ff3d;
        --verdigris:#00e5ff; --danger:#ff4d4d;
        --radius-s:6px; --radius-m:11px;
        --sombra: 0 4px 14px rgba(0,0,0,0.35);
    }
    body.light {
        --bg:#fff5fb; --bg-elev:#ffffff; --surface:#ffe8f5; --border:#ffc3e3;
        --text:#2c1b3d; --text-dim:#5d4874; --text-muted:#93819c;
        --accent:#ff2e88; --accent-soft:rgba(255,46,136,0.14); --accent-deep:#c4116a;
        --accent2:#0091a8; --accent3:#a8c400;
        --verdigris:#0091a8; --danger:#e2405a;
        --sombra: 0 4px 12px rgba(120,60,40,0.10);
    }
    * { box-sizing:border-box; }
    body { background:var(--bg); color:var(--text); font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin:0; padding:10px; transition: background 0.2s, color 0.2s; }
    .container { max-width: 900px; margin:0 auto; }
    .fuente-sello { font-family:'Cinzel', Georgia, 'Times New Roman', serif; }

    .header-bar { display:flex; justify-content:space-between; align-items:center; gap:8px; background:var(--bg-elev); border:1px solid var(--border); border-radius:var(--radius-m); padding:11px 14px; box-shadow:var(--sombra); margin-bottom:18px; }
    .marca { display:flex; align-items:center; gap:11px; min-width:0; }
    .sello { flex-shrink:0; width:36px; height:36px; border-radius:50%; border:1.5px solid var(--accent); display:flex; align-items:center; justify-content:center; font-size:10.5px; font-weight:700; color:var(--accent); background: radial-gradient(circle at 32% 30%, var(--accent-soft), transparent 72%); letter-spacing:0.2px; }
    .marca-texto { min-width:0; }
    .marca-titulo { display:block; font-size:13.5px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .marca-sub { display:block; font-size:9px; letter-spacing:1.4px; text-transform:uppercase; color:var(--text-muted); margin-top:2px; }

    .btn-icon { background:var(--surface); border:1px solid var(--border); color:var(--text); border-radius:9px; width:34px; height:34px; font-size:15px; cursor:pointer; flex-shrink:0; transition: transform 0.15s, border-color 0.15s; }
    .btn-icon:active { transform:scale(0.92); }

    .seccion { margin-top:22px; }
    .seccion:first-of-type { margin-top:2px; }
    .eyebrow { display:flex; align-items:center; gap:9px; margin-bottom:11px; }
    .eyebrow .num { flex-shrink:0; width:19px; height:19px; border-radius:50%; border:1px solid var(--accent); color:var(--accent); font-size:10px; font-weight:700; display:flex; align-items:center; justify-content:center; }
    .eyebrow .titulo { font-size:10.5px; letter-spacing:1.6px; text-transform:uppercase; color:var(--text-dim); font-weight:600; }
    .eyebrow .linea { flex:1; height:1px; background:var(--border); }

    label { font-size:10.5px; color:var(--text-muted); display:block; margin-top:13px; font-weight:600; text-transform:uppercase; letter-spacing:0.7px; }
    label.libre { text-transform:none; font-weight:400; letter-spacing:0; color:var(--text-dim); font-size:12.5px; }
    textarea, select, input[type="text"], input[type="file"] { width:100%; padding:10px 12px; border-radius:var(--radius-s); background:var(--surface); border:1px solid var(--border); color:var(--text); font-size:13px; box-sizing:border-box; margin-top:6px; transition: border-color 0.15s, box-shadow 0.15s; font-family:inherit; }
    textarea:focus, select:focus, input:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft); }
    textarea { height:220px; resize:vertical; }
    .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    #contadorCaracteres { font-size:10.5px; color:var(--text-muted); margin-top:4px; text-align:right; }

    input[type="range"] { accent-color:var(--accent); width:100%; margin-top:8px; height:3px; }

    .capcut-box { width:100%; max-width:400px; height:225px; background:#111; background-size:cover; background-position:center;
        border:1px solid var(--border); border-radius:var(--radius-m); position:sticky; top:8px; z-index:500; margin:16px auto; overflow:hidden; touch-action:none; user-select:none; box-shadow:var(--sombra); transition: box-shadow 0.2s; }
    .capcut-box.en-vivo { box-shadow:0 0 0 2px var(--accent), var(--sombra); }
    .capcut-box::before, .capcut-box::after { content:''; position:absolute; width:16px; height:16px; border:2px solid var(--accent); opacity:0.75; pointer-events:none; }
    .capcut-box::before { top:7px; left:7px; border-right:none; border-bottom:none; }
    .capcut-box::after { bottom:7px; right:7px; border-left:none; border-top:none; }
    .velo { position:absolute; inset:0; background:rgba(0,0,0,0.38); pointer-events:none; }

    .cajaTexto { position:absolute; padding:0 14px; font-size:14px; line-height:1.4; text-shadow: 0 0 5px rgba(0,0,0,0.8); cursor:ns-resize; }

    .izq { left:25%; top:50%; transform:translate(-50%, -50%); text-align:center; width:45%; }
    .der { left:75%; top:50%; transform:translate(-50%, -50%); text-align:center; width:45%; }
    .centro { left:50%; top:50%; transform:translate(-50%, -50%); text-align:center; width:80%; }
    .abajo { left:50%; top:80%; transform:translate(-50%, -50%); text-align:center; width:80%; }

    .col-blanco { color:#FFFFFF; }
    .col-amarillo_calido { color:#D9C27E; }
    .col-gris_claro { color:#D8D8D8; }
    .col-pergamino { color:#F4EEDC; }
    .col-oro_viejo { color:#D4AF37; }
    .col-rojo_carmesi { color:#8B0000; }

    #resizeHandle { position:absolute; width:22px; height:22px; background:var(--accent); color:#161310; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; cursor:nwse-resize; z-index:10; border:1px solid var(--accent-deep); }
    #efectoPreview { position:absolute; inset:0; pointer-events:none; z-index:3; }
    #efectoPreview.fx-vineta { box-shadow: inset 0 0 60px 20px rgba(0,0,0,0.75); }
    #efectoPreview.fx-grano_pelicula {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.35'/%3E%3C/svg%3E");
        animation: fxGranoParpadeo 0.15s steps(2) infinite;
    }
    @keyframes fxGranoParpadeo { 0%{opacity:0.7;} 50%{opacity:1;} 100%{opacity:0.7;} }
    #efectoPreview.fx-vela { background:#000; animation: fxVela 2.4s ease-in-out infinite; }
    @keyframes fxVela { 0%,100%{opacity:0.08;} 50%{opacity:0.22;} 25%{opacity:0.14;} 75%{opacity:0.18;} }
    #efectoPreview.fx-niebla { background: linear-gradient(to top, rgba(255,255,255,0.35), rgba(255,255,255,0) 55%); }
    #efectoPreview.fx-rayo_luz { background: linear-gradient(115deg, rgba(255,244,214,0) 40%, rgba(255,244,214,0.32) 50%, rgba(255,244,214,0) 62%); animation: fxRayo 5s ease-in-out infinite; }
    @keyframes fxRayo { 0%,100%{ opacity:0.5; } 50%{ opacity:1; } }
    #efectoPreview.fx-pergamino { background:#7a5a30; mix-blend-mode:color; opacity:0.28; }
    #efectoPreview.fx-ceniza {
        background-image: radial-gradient(circle, rgba(255,255,255,0.85) 1px, transparent 1.5px);
        background-size: 26px 34px, 40px 52px;
        animation: fxCeniza 6s linear infinite;
        opacity:0.5;
    }
    @keyframes fxCeniza { from{ background-position: 0 0; } to{ background-position: 0 400px; } }
    .handleLateral { position:absolute; top:50%; transform:translateY(-50%); width:22px; height:22px; background:var(--bg-elev); color:var(--accent); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; cursor:ew-resize; z-index:10; border:1px solid var(--accent); }
    .handleVertical { position:absolute; top:-11px; left:50%; transform:translateX(-50%); width:22px; height:22px; background:var(--bg-elev); color:var(--accent); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; cursor:ns-resize; z-index:10; border:1px solid var(--accent); }
    #contador { font-size:11px; color:var(--text-muted); margin-top:6px; }
    #contador div { padding:2px 0; }

    button.principal { display:block; width:auto; min-width:220px; margin:18px auto 4px; padding:13px 26px; border-radius:var(--radius-s); border:1px solid var(--accent-deep); background:linear-gradient(180deg, var(--accent), var(--accent-deep)); color:#161310; font-family:'Cinzel', Georgia, serif; font-weight:700; font-size:12px; letter-spacing:1.6px; text-transform:uppercase; cursor:pointer; box-shadow:0 1px 0 rgba(255,255,255,0.18) inset, 0 4px 12px rgba(0,0,0,0.35); transition: transform 0.15s, box-shadow 0.15s; }
    button.principal:hover { box-shadow:0 1px 0 rgba(255,255,255,0.18) inset, 0 6px 16px rgba(0,0,0,0.3); }
    button.principal:active { transform:translateY(1px); box-shadow:0 1px 0 rgba(255,255,255,0.1) inset; }
    button.principal:disabled { opacity:0.55; cursor:default; }
    video { width:100%; border-radius:var(--radius-m); margin-top:10px; border:1px solid var(--border); box-shadow:var(--sombra); }
    .msg { font-size:13px; margin-top:8px; padding:11px; background:var(--bg-elev); border:1px solid var(--border); border-radius:var(--radius-s); text-align:center; }

    #procesoView { display:none; margin-top:16px; padding:18px 16px; background:var(--bg-elev); border:1px solid var(--border); border-radius:var(--radius-m); box-shadow:var(--sombra); }
    #procesoView h2 { font-family:'Cinzel', Georgia, serif; font-size:12.5px; letter-spacing:1.6px; text-transform:uppercase; margin:0 0 14px 0; text-align:center; color:var(--text-dim); font-weight:600; }
    .paso { margin-bottom:13px; }
    .paso:last-child { margin-bottom:0; }
    .paso-etiqueta { display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px; color:var(--text-muted); }
    .paso.activo .paso-etiqueta { color:var(--accent); font-weight:bold; }
    .paso.hecho .paso-etiqueta { color:var(--verdigris); }
    .paso-track { width:100%; height:6px; border-radius:3px; background:var(--border); overflow:hidden; }
    .paso-fill { height:100%; width:0%; background:var(--text-muted); border-radius:3px; transition: width 0.4s ease; }
    .paso.activo .paso-fill { background:var(--accent); }
    .paso.hecho .paso-fill { background:var(--verdigris); }
    .paso.error .paso-etiqueta, .paso.error .paso-fill { color:var(--danger); background:var(--danger); }

    .accesos { display:flex; flex-direction:column; align-items:stretch; gap:1px; margin:16px auto 0 0; max-width:200px; }
    .acceso { display:flex; align-items:center; gap:8px; background:transparent; border:none; border-bottom:1px solid var(--border); border-radius:0; padding:8px 2px; cursor:pointer; color:var(--text); font-family:inherit; width:100%; text-align:left; opacity:0.72; transition: opacity 0.15s, transform 0.15s; }
    .acceso:active { opacity:1; transform:scale(0.98); }
    .acceso-icono { font-size:13px; flex-shrink:0; }
    .acceso-texto { display:flex; flex-direction:column; min-width:0; flex:1; }
    .acceso-titulo { font-size:9.5px; letter-spacing:1px; text-transform:uppercase; color:var(--text-dim); font-weight:600; }
    .acceso-resumen { font-size:9px; color:var(--text-muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .acceso::after { content:'▾'; margin-left:6px; font-size:9px; color:var(--text-muted); flex-shrink:0; }
    .btn-mini { font-size:10.5px; padding:5px 11px; border-radius:20px; background:var(--surface); border:1px solid var(--border); color:var(--text-dim); cursor:pointer; font-family:inherit; }
    .btn-mini:active { transform:scale(0.94); }
    .btn-flotante { font-size:14px; width:30px; height:30px; padding:0; border-radius:50%; background:var(--bg-elev); border:1px solid var(--border); color:var(--text-dim); cursor:pointer; box-shadow:0 2px 6px rgba(0,0,0,0.35); display:flex; align-items:center; justify-content:center; }
    .btn-flotante:active { transform:scale(0.9); }
    .wrap-textarea { position:relative; }
    .iconos-textarea { position:absolute; top:8px; right:8px; display:flex; gap:5px; }

    .modal-overlay { display:none; position:fixed; inset:0; background:transparent; z-index:1000; align-items:flex-end; justify-content:center; pointer-events:none; }
    .modal-overlay.abierto { display:flex; }
    .modal-hoja { pointer-events:auto; width:100%; max-width:480px; height:auto; max-height:58vh; max-height:58dvh; overflow-y:auto; background:var(--bg-elev); border:1px solid var(--border); border-bottom:none; border-radius:16px 16px 0 0; padding:16px 16px 22px; box-shadow:0 -10px 26px rgba(0,0,0,0.45); animation:entrarPanel 0.2s ease; }
    @keyframes entrarPanel { from{ transform:translateY(24px); opacity:0; } to{ transform:translateY(0); opacity:1; } }
    .modal-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; padding-bottom:12px; border-bottom:1px solid var(--border); }
    .modal-titulo { font-size:12.5px; letter-spacing:1.6px; text-transform:uppercase; color:var(--text); }
</style>
</head>
<body>
<div class="container">
    <div class="header-bar" style="justify-content:flex-start;">
        <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">
            <div class="sello fuente-sello">V{{ version }}</div>
            <button class="btn-icon" id="btnGenerar" type="button" title="Generar video ahora">🎬</button>
            <button class="btn-icon" id="btnTheme" type="button">☀️</button>
        </div>
        <div class="marca-texto">
            <span class="marca-titulo fuente-sello">Story Engine</span>
            <span class="marca-sub">Video · Voz · Palabra</span>
        </div>
    </div>

    <div id="formulario">

    <div class="seccion">
        <div class="eyebrow"><span class="num">I</span><span class="titulo">Guion (idioma original)</span><span class="linea"></span></div>
        <div class="wrap-textarea">
            <textarea id="texto" maxlength="500000" placeholder="Escribí o pegá tu texto acá..."></textarea>
            <div class="iconos-textarea">
                <button type="button" id="btnPegar" class="btn-flotante" title="Pegar">📋</button>
                <button type="button" id="btnCopiar" class="btn-flotante" title="Copiar todo">📄</button>
                <button type="button" id="btnBorrar" class="btn-flotante" title="Borrar">🗑️</button>
            </div>
        </div>
        <div style="display:flex; gap:6px; margin-top:6px; flex-wrap:wrap;">
            <button type="button" id="btnTraerReddit" class="btn-mini">📥 Traer historia</button>
            <button type="button" id="btnOtraHistoria" class="btn-mini" style="display:none;">🔄 Otra historia</button>
        </div>
        <div id="infoHistoriaReddit" style="font-size:10.5px; color:var(--text-muted); margin-top:4px;"></div>

        <div style="margin-top:14px; padding-top:10px; border-top:1px solid var(--border);">
            <span style="font-size:10.5px; color:var(--text-muted);">AUDIO — IDIOMA ORIGINAL · Voz Ryan</span>
            <div style="display:flex; gap:6px; margin-top:8px; flex-wrap:wrap;">
                <button type="button" id="btnGenerarAudioOriginal" class="btn-mini">🔊 Generar audio</button>
                <button type="button" id="btnDescargarAudioOriginal" class="btn-mini">⬇️ Descargar audio</button>
                <button type="button" id="btnTraducir" class="btn-mini">🌐 Traducir</button>
            </div>
            <div id="infoAudioOriginal" style="font-size:10.5px; color:var(--text-muted); margin-top:4px;"></div>
        </div>

        <div id="contadorCaracteres">0 / 500000</div>
        <div id="contador"></div>
    </div>

    <div class="seccion" id="seccionTraducido" style="display:none;">
        <div class="eyebrow"><span class="num">II</span><span class="titulo">Guion traducido (español)</span><span class="linea"></span></div>

        <div class="grid-2" style="margin-top:8px;">
            <div>
                <label style="display:flex; justify-content:space-between;"><span>Velocidad</span></label>
                <div style="display:flex; align-items:center; gap:6px;">
                    <button type="button" onclick="ajustarVozES('velocidad_voz_es', -5)" style="width:36px; height:36px; font-size:18px;">−</button>
                    <input type="number" id="velocidad_voz_es" min="-50" max="50" step="5" value="-10"
                           style="text-align:center; width:100%;" oninput="actualizarValoresVozES()">
                    <button type="button" onclick="ajustarVozES('velocidad_voz_es', 5)" style="width:36px; height:36px; font-size:18px;">+</button>
                    <span style="width:26px;">%</span>
                </div>
            </div>
            <div>
                <label style="display:flex; justify-content:space-between;"><span>Tono</span></label>
                <div style="display:flex; align-items:center; gap:6px;">
                    <button type="button" onclick="ajustarVozES('tono_voz_es', -5)" style="width:36px; height:36px; font-size:18px;">−</button>
                    <input type="number" id="tono_voz_es" min="-50" max="50" step="5" value="-10"
                           style="text-align:center; width:100%;" oninput="actualizarValoresVozES()">
                    <button type="button" onclick="ajustarVozES('tono_voz_es', 5)" style="width:36px; height:36px; font-size:18px;">+</button>
                    <span style="width:30px;">Hz</span>
                </div>
            </div>
        </div>
        <div style="font-size:9.5px; color:var(--text-muted); margin-top:4px;">Se aplican tanto al audio en español como al audio del idioma original.</div>

        <div class="wrap-textarea" style="margin-top:10px;">
            <textarea id="textoTraducido" placeholder="Acá va a aparecer el guion traducido al español después de tocar 'Traducir'..."></textarea>
        </div>
        <div id="contadorTextoTraducido" style="font-size:10.5px; color:var(--text-muted); margin-top:2px;">0 caracteres</div>

        <div style="display:flex; gap:6px; margin-top:8px; flex-wrap:wrap;">
            <button type="button" id="btnGenerarAudioTraducido" class="btn-mini">🔊 Generar audio</button>
            <button type="button" id="btnDescargarAudioTraducido" class="btn-mini">⬇️ Descargar audio</button>
        </div>
        <div id="infoAudioTraducido" style="font-size:10.5px; color:var(--text-muted); margin-top:4px;"></div>
    </div>

    <div class="accesos">
        <button type="button" class="acceso" data-modal="modalEstilo">
            <span class="acceso-icono">🎨</span>
            <span class="acceso-texto">
                <span class="acceso-titulo">Estilo</span>
                <span class="acceso-resumen" id="resumenEstilo">—</span>
            </span>
        </button>
        <button type="button" class="acceso" data-modal="modalVoz">
            <span class="acceso-icono">🎙️</span>
            <span class="acceso-texto">
                <span class="acceso-titulo">Voz</span>
                <span class="acceso-resumen" id="resumenVoz">—</span>
            </span>
        </button>
        <button type="button" class="acceso" data-modal="modalFondo">
            <span class="acceso-icono">🖼️</span>
            <span class="acceso-texto">
                <span class="acceso-titulo">Fondo</span>
                <span class="acceso-resumen" id="resumenFondo">—</span>
            </span>
        </button>
    </div>

    <div class="seccion" style="display:none;">
        <div class="capcut-box" id="preview">
            <div class="velo"></div>
            <div id="efectoPreview"></div>
            <div class="cajaTexto centro col-oro_viejo" id="cajaTexto">
                <span id="resizeHandle">⤢</span>
                <span id="handleIzq" class="handleLateral" style="left:-11px;">↔</span>
                <span id="handleDer" class="handleLateral" style="right:-11px;">↔</span>
                <span id="handleArriba" class="handleVertical">↕</span>
            </div>
        </div>
        <div style="text-align:center; font-size:11px; color:var(--text-muted);">
            Punto dorado o rueda del mouse: agranda/achica letra. Flechas de los costados: ensancha el cuadro.
            Flecha de arriba: sube o baja el cuadro.
        </div>
        <input type="hidden" id="ancho_sub_pct" value="73">
        <input type="hidden" id="pos_y_pct" value="83">
    </div>

    <!-- ===== Modal: Estilo visual ===== -->
    <div class="modal-overlay" id="modalEstilo">
        <div class="modal-hoja">
            <div class="modal-header">
                <span class="modal-titulo fuente-sello">🎨 Estilo visual</span>
                <button type="button" class="btn-icon" data-cerrar="modalEstilo">✕</button>
            </div>
            <div class="grid-2">
                <div>
                    <label>Animación</label>
                    <select id="animacion">
                        <option value="estatico" selected>Estático (bloque)</option>
                        <option value="dinamico">Dinámico (por palabra)</option>
                    </select>
                </div>
                <div>
                    <label>Efecto de video</label>
                    <select id="efecto_video">
                        <option value="ninguno">Ninguno</option>
                        <option value="ceniza">Ceniza/polvo cayendo</option>
                        <option value="grano_pelicula">Grano de película</option>
                        <option value="vela">Luz de vela parpadeante</option>
                        <option value="niebla">Niebla baja</option>
                        <option value="rayo_luz">Rayo de luz con polvo</option>
                        <option value="vineta">Viñeta oscura</option>
                        <option value="pergamino">Tono pergamino/mármol</option>
                    </select>
                </div>
                <div id="contenedorVelocidadEfecto" style="display:none;">
                    <label style="display:flex; justify-content:space-between;">
                        <span>Velocidad del efecto</span>
                        <span id="valorVelocidadEfecto">1.0x</span>
                    </label>
                    <input type="range" id="velocidad_efecto" min="0.3" max="2.5" step="0.1" value="1.0"
                           oninput="document.getElementById('valorVelocidadEfecto').textContent = parseFloat(this.value).toFixed(1) + 'x'">
                    <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Solo cambia "Ceniza" y "Vela" (los demás efectos son fijos, sin movimiento).</div>
                </div>
                <div>
                    <label>Posición</label>
                    <select id="posicion">
                        <option value="centro">Centro (Recomendado)</option>
                        <option value="abajo">Abajo</option>
                        <option value="izquierda">Izquierda</option>
                        <option value="derecha">Derecha</option>
                    </select>
                </div>
            </div>
            <div class="grid-2">
                <div>
                    <label>Color</label>
                    <select id="color_sub">
                        <option value="oro_viejo">Oro Viejo (Recomendado)</option>
                        <option value="blanco">Blanco</option>
                        <option value="pergamino" selected>Pergamino</option>
                        <option value="amarillo_calido">Amarillo</option>
                        <option value="gris_claro">Gris</option>
                        <option value="rojo_carmesi">Carmesí</option>
                    </select>
                </div>
                <div>
                    <label>Fuente</label>
                    <select id="fuente_sub">
                        <option value="Playfair Display">Playfair Display</option>
                        <option value="Cormorant Garamond">Cormorant Garamond</option>
                        <option value="EB Garamond">EB Garamond</option>
                        <option value="Lora">Lora</option>
                    </select>
                </div>
            </div>
            <div style="margin-top:6px;">
                <label style="display:flex; justify-content:space-between;">
                    <span>Opacidad de subtítulos</span>
                    <span id="valorOpacidadSub">100%</span>
                </label>
                <input type="range" id="opacidad_sub" min="20" max="100" step="5" value="100"
                       oninput="aplicarOpacidadSub(this.value)">
            </div>
        </div>
    </div>

    <!-- ===== Modal: Voz ===== -->
    <div class="modal-overlay" id="modalVoz">
        <div class="modal-hoja">
            <div class="modal-header">
                <span class="modal-titulo fuente-sello">🎙️ Voz</span>
                <button type="button" class="btn-icon" data-cerrar="modalVoz">✕</button>
            </div>
            <div id="contenedorControlesEdgeTTS" class="grid-2">
                <div style="margin-top:6px;">
                    <label style="display:flex; justify-content:space-between;">
                        <span>Velocidad de voz</span>
                    </label>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <button type="button" onclick="ajustarVoz('velocidad_voz', -5)" style="width:36px; height:36px; font-size:18px;">−</button>
                        <input type="number" id="velocidad_voz" min="-50" max="50" step="5" value="-10"
                               style="text-align:center; width:100%;" oninput="actualizarValoresVoz()">
                        <button type="button" onclick="ajustarVoz('velocidad_voz', 5)" style="width:36px; height:36px; font-size:18px;">+</button>
                        <span style="width:26px;">%</span>
                    </div>
                </div>
                <div style="margin-top:6px;">
                    <label style="display:flex; justify-content:space-between;">
                        <span>Tono (grave ↔ agudo)</span>
                    </label>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <button type="button" onclick="ajustarVoz('tono_voz', -5)" style="width:36px; height:36px; font-size:18px;">−</button>
                        <input type="number" id="tono_voz" min="-50" max="50" step="5" value="-10"
                               style="text-align:center; width:100%;" oninput="actualizarValoresVoz()">
                        <button type="button" onclick="ajustarVoz('tono_voz', 5)" style="width:36px; height:36px; font-size:18px;">+</button>
                        <span style="width:30px;">Hz</span>
                    </div>
                </div>
            </div>
            <label class="libre" style="display:flex; align-items:center; gap:6px; margin-top:9px;">
                <input type="checkbox" id="traducir_auto" style="width:auto; margin:0;">
                Traducir automático (DeepL)
            </label>
        </div>
    </div>

    <!-- ===== Modal: Fondo y música ===== -->
    <div class="modal-overlay" id="modalFondo">
        <div class="modal-hoja">
            <div class="modal-header">
                <span class="modal-titulo fuente-sello">🖼️ Fondo y música</span>
                <button type="button" class="btn-icon" data-cerrar="modalFondo">✕</button>
            </div>
            <div class="grid-2">
                <div>
                    <label>Música</label>
                    <select id="musica_genero">
                        <option value="piano">Piano melancólico</option>
                        <option value="ambient">Ambient profundo</option>
                        <option value="cuerdas">Cuerdas dramáticas</option>
                        <option value="ninguno">Sin música</option>
                    </select>
                </div>
                <div>
                    <label>Imágenes de fondo (opcional)</label>
                    <input type="file" id="imagenes" accept="image/*" multiple>
                </div>
            </div>
            <label class="libre" style="display:flex; align-items:center; gap:6px; margin-top:9px;">
                <input type="checkbox" id="fondo_fijo" style="width:auto; margin:0;" checked>
                Fondo fijo (sin zoom ni cambios)
            </label>
            <div style="margin-top:9px;">
                <label>Descargar imágenes de Pexels/Pixabay (0 = usar imagen fija predeterminada)</label>
                <input type="number" id="cantidad_imagenes_descargar" min="0" max="20" value="0" style="width:100%;">
                <div style="font-size:10.5px; color:var(--text-muted); margin-top:2px;">
                    Si pones 2 o más, se descargan esa cantidad y se reparten en partes iguales
                    a lo largo del video, con desvanecimiento entre ellas.
                </div>
            </div>
        </div>
    </div>

    <input type="hidden" id="frases_por_bloque" value="3">
    <input type="hidden" id="tamano_sub" value="42">
    <input type="hidden" id="volumen_musica" value="12">
    </div>

    <div id="procesoView">
        <h2>Progreso de generación</h2>
        <div id="tiempoTotal" style="text-align:center; font-size:13px; color:var(--text-dim); margin-bottom:12px;">⏱️ 0s</div>
        <div id="listaPasos"></div>
    </div>
    <div id="resArea"></div>
</div>

<script>
    const RESOLUCION_VIDEO_ANCHO = 1280;
    const btnTheme = document.getElementById('btnTheme');
    function aplicarTema(tema) {
        document.body.classList.toggle('light', tema === 'light');
        btnTheme.textContent = tema === 'light' ? '🌙' : '☀️';
    }
    aplicarTema(localStorage.getItem('tema_estoico') || 'dark');
        function actualizarValoresVoz() {
            let v = parseInt(document.getElementById('velocidad_voz').value, 10);
            let t = parseInt(document.getElementById('tono_voz').value, 10);
            if (isNaN(v)) v = -10;
            if (isNaN(t)) t = -10;
            v = Math.max(-50, Math.min(50, v));
            t = Math.max(-50, Math.min(50, t));
            document.getElementById('velocidad_voz').value = v;
            document.getElementById('tono_voz').value = t;
        }
        function ajustarVoz(id, delta) {
            const campo = document.getElementById(id);
            let val = parseInt(campo.value, 10);
            if (isNaN(val)) val = 0;
            campo.value = Math.max(-50, Math.min(50, val + delta));
            actualizarValoresVoz();
        }
        actualizarValoresVoz();

    btnTheme.addEventListener('click', () => {
        const nuevo = document.body.classList.contains('light') ? 'dark' : 'light';
        localStorage.setItem('tema_estoico', nuevo);
        aplicarTema(nuevo);
    });

    let intervaloPalabraEstoico = null;

    function updatePreview() {
        const caja = document.getElementById('cajaTexto');
        const handle = document.getElementById('resizeHandle');
        
        let cClass = '';
        const pos = document.getElementById('posicion').value;
        if(pos==='izquierda') cClass='izq';
        else if(pos==='derecha') cClass='der';
        else if(pos==='centro') cClass='centro';
        else if(pos==='abajo') cClass='abajo';

        if (!caja.contains(handle)) caja.appendChild(handle);
        caja.className = 'cajaTexto ' + cClass + ' col-' + document.getElementById('color_sub').value;
        caja.style.fontFamily = `'${document.getElementById('fuente_sub').value}', serif`;

        // Animación: "dinámico" muestra el texto palabra por palabra (como
        // saldrá en el video real), "estático" muestra el bloque completo.
        if (intervaloPalabraEstoico) { clearInterval(intervaloPalabraEstoico); intervaloPalabraEstoico = null; }
        const textoGuion = document.getElementById('texto').value.trim();
        const palabras = textoGuion ? textoGuion.split(/\\s+/).filter(Boolean) : ['Así', 'como', 'el', 'sol', 'no', 'espera', 'plegarias...'];
        const animacion = document.getElementById('animacion').value;

        if (animacion === 'dinamico') {
            let idx = 0;
            const pintar = () => {
                const palabra = palabras[idx % palabras.length];
                caja.childNodes[0] ? (caja.childNodes[0].nodeValue = `"${palabra}"`) : caja.prepend(document.createTextNode(`"${palabra}"`));
                idx++;
            };
            if (caja.childNodes[0] && caja.childNodes[0].nodeType === Node.TEXT_NODE) {
                caja.childNodes[0].nodeValue = `"${palabras[0]}"`;
            } else {
                caja.prepend(document.createTextNode(`"${palabras[0]}"`));
            }
            idx = 1;
            intervaloPalabraEstoico = setInterval(pintar, 550);
        } else {
            const texto = palabras.slice(0, 8).join(' ');
            if (caja.childNodes[0] && caja.childNodes[0].nodeType === Node.TEXT_NODE) {
                caja.childNodes[0].nodeValue = `"${texto}..."`;
            } else {
                caja.prepend(document.createTextNode(`"${texto}..."`));
            }
        }
        
        const n = document.getElementById('texto').value.length;
        const minutos = Math.max(0, n / 900); // ~900 caracteres hablados por minuto
        const minutosTxt = minutos < 1 && n > 0 ? '<1 min' : `~${minutos.toFixed(1)} min`;
        document.getElementById('contadorCaracteres').textContent = `${n} / 500000 caracteres (${minutosTxt} de video)`;
    }

    ['posicion', 'color_sub', 'fuente_sub', 'texto', 'animacion'].forEach(id => {
        document.getElementById(id).addEventListener('input', updatePreview);
        document.getElementById(id).addEventListener('change', updatePreview);
    });

    // ---- Accesos rápidos (Estilo / Voz / Fondo) y sus hojas modales ----
    function abrirModal(id) {
        document.getElementById(id).classList.add('abierto');
        document.getElementById('preview').classList.add('en-vivo');
        // Aseguramos que el cuadro quede a la vista (arriba de la hoja) al abrir cualquier panel.
        document.getElementById('preview').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    function cerrarModal(id) {
        document.getElementById(id).classList.remove('abierto');
        if (!document.querySelector('.modal-overlay.abierto')) {
            document.getElementById('preview').classList.remove('en-vivo');
        }
    }

    document.querySelectorAll('.acceso').forEach(btn => {
        btn.addEventListener('click', () => abrirModal(btn.dataset.modal));
    });
    document.querySelectorAll('[data-cerrar]').forEach(btn => {
        btn.addEventListener('click', () => cerrarModal(btn.dataset.cerrar));
    });
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => { if (e.target === overlay) cerrarModal(overlay.id); });
    });

    function actualizarResumenes() {
        const colorTexto = document.getElementById('color_sub').selectedOptions[0].text.split(' (')[0];
        const fuenteTexto = document.getElementById('fuente_sub').value;
        document.getElementById('resumenEstilo').textContent = `${colorTexto} · ${fuenteTexto}`;

        document.getElementById('resumenVoz').textContent = 'Alex (Español)';

        document.getElementById('resumenFondo').textContent = document.getElementById('musica_genero').selectedOptions[0].text;
    }
    ['color_sub', 'fuente_sub', 'musica_genero'].forEach(id => {
        document.getElementById(id).addEventListener('change', actualizarResumenes);
    });
    actualizarResumenes();

    document.getElementById('imagenes').addEventListener('change', (e) => {
        const archivo = e.target.files[0];
        if (!archivo) return;
        const lector = new FileReader();
        lector.onload = (ev) => { document.getElementById('preview').style.backgroundImage = `url(${ev.target.result})`; };
        lector.readAsDataURL(archivo);
    });

    function aplicarTamano(tamanoReal) {
        tamanoReal = Math.max(12, Math.min(100, Math.round(tamanoReal))); // LIMITE ALTO A 100
        document.getElementById('tamano_sub').value = tamanoReal;
        const caja = document.getElementById('preview');
        document.getElementById('cajaTexto').style.fontSize = (tamanoReal * ((caja.offsetWidth || 400) / RESOLUCION_VIDEO_ANCHO)) + 'px';
        return tamanoReal;
    }
    aplicarTamano(34);

    function aplicarOpacidadSub(valor) {
        document.getElementById('valorOpacidadSub').textContent = valor + '%';
        document.getElementById('cajaTexto').style.opacity = (valor / 100);
    }
    aplicarOpacidadSub(document.getElementById('opacidad_sub').value);

    function aplicarEfectoPreview() {
        const el = document.getElementById('efectoPreview');
        el.className = '';
        const efecto = document.getElementById('efecto_video').value;
        if (efecto && efecto !== 'ninguno') el.classList.add('fx-' + efecto);
    }
    document.getElementById('efecto_video').addEventListener('change', aplicarEfectoPreview);
    aplicarEfectoPreview();

    function toggleVelocidadEfecto() {
        const efecto = document.getElementById('efecto_video').value;
        document.getElementById('contenedorVelocidadEfecto').style.display = (efecto === 'ceniza' || efecto === 'vela') ? 'block' : 'none';
    }
    document.getElementById('efecto_video').addEventListener('change', toggleVelocidadEfecto);
    toggleVelocidadEfecto();

    // ---- Pegar / Copiar / Borrar en el cuadro de guion ----
    document.getElementById('btnPegar').addEventListener('click', async () => {
        try {
            const texto = await navigator.clipboard.readText();
            document.getElementById('texto').value = texto;
            updatePreview();
        } catch (e) {
            alert('No se pudo leer el portapapeles automáticamente. Mantené presionado el cuadro de texto y elegí "Pegar".');
        }
    });
    document.getElementById('btnCopiar').addEventListener('click', async () => {
        const btn = document.getElementById('btnCopiar');
        const texto = document.getElementById('texto').value;
        try {
            await navigator.clipboard.writeText(texto);
            const original = btn.textContent;
            btn.textContent = '✅';
            setTimeout(() => { btn.textContent = original; }, 1200);
        } catch (e) {
            alert('No se pudo copiar automáticamente. Mantené presionado el cuadro de texto, seleccioná todo y elegí "Copiar".');
        }
    });
    document.getElementById('btnBorrar').addEventListener('click', () => {
        document.getElementById('texto').value = '';
        updatePreview();
        document.getElementById('texto').focus();
    });

    // ---- Traer historia de Reddit y armar el guion automáticamente ----
    // v5.0: ya no traduce acá: el guion que llega queda tal cual, en su
    // idioma original (inglés). La traducción es una acción aparte, con
    // su propio botón "Traducir" (ver más abajo).
    let idsHistoriaActual = [];
    document.getElementById('btnTraerReddit').addEventListener('click', async () => {
        const btn = document.getElementById('btnTraerReddit');
        const info = document.getElementById('infoHistoriaReddit');
        const btnOtra = document.getElementById('btnOtraHistoria');
        btn.disabled = true;
        btn.textContent = 'Buscando historia...';
        info.textContent = '';
        try {
            const resp = await fetch('/reddit/traer_historia');
            const data = await resp.json();
            if (!resp.ok || data.error) {
                info.style.color = 'var(--danger)';
                info.textContent = '❌ ' + (data.error || 'Error desconocido');
                idsHistoriaActual = [];
                btnOtra.style.display = 'none';
            } else {
                document.getElementById('texto').value = data.guion;
                updatePreview();
                // Guion original nuevo: la traducción anterior queda obsoleta.
                document.getElementById('textoTraducido').value = '';
                document.getElementById('seccionTraducido').style.display = 'none';
                document.getElementById('contadorTextoTraducido').textContent = '0 caracteres';
                info.style.color = 'var(--text-muted)';
                if (data.cantidad > 1) {
                    info.textContent = `${data.cantidad} historias combinadas (r/${data.subreddit}) — ${data.upvotes} upvotes totales`;
                } else {
                    info.textContent = `r/${data.subreddit} — ${data.titulo} (${data.upvotes} upvotes)`;
                }
                idsHistoriaActual = data.ids || [];
                btnOtra.style.display = idsHistoriaActual.length ? 'inline-block' : 'none';
            }
        } catch (e) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ ' + e;
        }
        btn.disabled = false;
        btn.textContent = '📥 Traer historia';
    });

    // ---- Descartar la historia actual (sin generar video) y traer otra ----
    document.getElementById('btnOtraHistoria').addEventListener('click', async () => {
        const btnOtra = document.getElementById('btnOtraHistoria');
        const info = document.getElementById('infoHistoriaReddit');
        if (!idsHistoriaActual.length) return;
        btnOtra.disabled = true;
        btnOtra.textContent = 'Descartando...';
        try {
            const form = new FormData();
            form.append('ids', JSON.stringify(idsHistoriaActual));
            const resp = await fetch('/reddit/descartar_historia', { method: 'POST', body: form });
            const data = await resp.json();
            if (!resp.ok || data.error) {
                info.style.color = 'var(--danger)';
                info.textContent = '❌ ' + (data.error || 'No se pudo descartar');
                btnOtra.disabled = false;
                btnOtra.textContent = '🔄 Otra historia';
                return;
            }
        } catch (e) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ ' + e;
            btnOtra.disabled = false;
            btnOtra.textContent = '🔄 Otra historia';
            return;
        }
        idsHistoriaActual = [];
        btnOtra.disabled = false;
        btnOtra.textContent = '🔄 Otra historia';
        btnOtra.style.display = 'none';
        document.getElementById('btnTraerReddit').click();
    });

    // ---- Audio del idioma original (voz Ryan), Traducir, y audio del
    // guion traducido en español (voz Alex). v5.0: los dos bloques de
    // guion son autosuficientes, cada uno con su propio texto editable
    // y sus propios botones de audio. Los sliders de velocidad/tono se
    // comparten entre los dos idiomas (confirmado por el usuario).

    function _descargarArchivo(url, nombreArchivo) {
        const a = document.createElement('a');
        a.href = url;
        a.download = nombreArchivo;
        document.body.appendChild(a);
        a.click();
        a.remove();
    }

    function actualizarValoresVozES() {
        let v = parseInt(document.getElementById('velocidad_voz_es').value, 10);
        let t = parseInt(document.getElementById('tono_voz_es').value, 10);
        if (isNaN(v)) v = -10;
        if (isNaN(t)) t = -10;
        v = Math.max(-50, Math.min(50, v));
        t = Math.max(-50, Math.min(50, t));
        document.getElementById('velocidad_voz_es').value = v;
        document.getElementById('tono_voz_es').value = t;
    }
    function ajustarVozES(id, delta) {
        const el = document.getElementById(id);
        let v = parseInt(el.value, 10);
        if (isNaN(v)) v = -10;
        el.value = Math.max(-50, Math.min(50, v + delta));
        actualizarValoresVozES();
    }

    async function _generarAudioOriginal() {
        const texto = document.getElementById('texto').value.trim();
        if (!texto) throw new Error('Escribí o traé un guion primero.');
        const form = new FormData();
        form.append('guion', texto);
        form.append('velocidad_voz', document.getElementById('velocidad_voz_es').value);
        form.append('tono_voz', document.getElementById('tono_voz_es').value);
        const resp = await fetch('/reddit/generar_audio_ingles', { method: 'POST', body: form });
        const data = await resp.json();
        if (!resp.ok || data.error) throw new Error(data.error || 'Error desconocido');
        return data;
    }

    async function _generarAudioTraducido() {
        const texto = document.getElementById('textoTraducido').value.trim();
        if (!texto) throw new Error('Todavía no hay guion traducido. Tocá "Traducir" primero.');
        const form = new FormData();
        form.append('guion', texto);
        form.append('velocidad_voz', document.getElementById('velocidad_voz_es').value);
        form.append('tono_voz', document.getElementById('tono_voz_es').value);
        const resp = await fetch('/reddit/generar_audio_prueba', { method: 'POST', body: form });
        const data = await resp.json();
        if (!resp.ok || data.error) throw new Error(data.error || 'Error desconocido');
        return data;
    }

    document.getElementById('btnGenerarAudioOriginal').addEventListener('click', async () => {
        const btn = document.getElementById('btnGenerarAudioOriginal');
        const info = document.getElementById('infoAudioOriginal');
        btn.disabled = true;
        btn.textContent = 'Generando...';
        info.style.color = 'var(--text-muted)';
        info.innerHTML = 'Esto puede tardar unos segundos...';
        try {
            const data = await _generarAudioOriginal();
            const url = '/reddit/audio_prueba/' + data.archivo;
            info.style.color = 'var(--text-muted)';
            info.innerHTML = `✅ Listo (${data.duracion}s)<br><audio controls autoplay src="${url}" style="width:100%; margin-top:6px;"></audio>`;
        } catch (e) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ ' + e.message;
        }
        btn.disabled = false;
        btn.textContent = '🔊 Generar audio';
    });

    document.getElementById('btnDescargarAudioOriginal').addEventListener('click', async () => {
        const btn = document.getElementById('btnDescargarAudioOriginal');
        const info = document.getElementById('infoAudioOriginal');
        btn.disabled = true;
        btn.textContent = 'Generando...';
        info.style.color = 'var(--text-muted)';
        info.innerHTML = 'Esto puede tardar unos segundos...';
        try {
            const data = await _generarAudioOriginal();
            _descargarArchivo('/reddit/audio_prueba/' + data.archivo, data.archivo);
            info.style.color = 'var(--text-muted)';
            info.textContent = `✅ Descargado (${data.duracion}s)`;
        } catch (e) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ ' + e.message;
        }
        btn.disabled = false;
        btn.textContent = '⬇️ Descargar audio';
    });

    document.getElementById('btnTraducir').addEventListener('click', async () => {
        const btn = document.getElementById('btnTraducir');
        const info = document.getElementById('infoAudioOriginal');
        const texto = document.getElementById('texto').value.trim();
        if (!texto) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ Escribí o traé un guion primero.';
            return;
        }
        btn.disabled = true;
        btn.textContent = 'Traduciendo...';
        try {
            const form = new FormData();
            form.append('guion', texto);
            const resp = await fetch('/reddit/traducir_guion', { method: 'POST', body: form });
            const data = await resp.json();
            if (!resp.ok || data.error) throw new Error(data.error || 'Error desconocido');
            document.getElementById('textoTraducido').value = data.guion_traducido || '';
            document.getElementById('contadorTextoTraducido').textContent = (data.guion_traducido || '').length + ' caracteres';
            document.getElementById('seccionTraducido').style.display = 'block';
            document.getElementById('seccionTraducido').scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (e) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ ' + e.message;
        }
        btn.disabled = false;
        btn.textContent = '🌐 Traducir';
    });

    document.getElementById('textoTraducido').addEventListener('input', () => {
        document.getElementById('contadorTextoTraducido').textContent = document.getElementById('textoTraducido').value.length + ' caracteres';
    });

    document.getElementById('btnGenerarAudioTraducido').addEventListener('click', async () => {
        const btn = document.getElementById('btnGenerarAudioTraducido');
        const info = document.getElementById('infoAudioTraducido');
        btn.disabled = true;
        btn.textContent = 'Generando...';
        info.style.color = 'var(--text-muted)';
        info.innerHTML = 'Esto puede tardar unos segundos...';
        try {
            const data = await _generarAudioTraducido();
            const url = '/reddit/audio_prueba/' + data.archivo;
            info.style.color = 'var(--text-muted)';
            info.innerHTML = `✅ Listo (${data.duracion}s)<br><audio controls autoplay src="${url}" style="width:100%; margin-top:6px;"></audio>`;
        } catch (e) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ ' + e.message;
        }
        btn.disabled = false;
        btn.textContent = '🔊 Generar audio';
    });

    document.getElementById('btnDescargarAudioTraducido').addEventListener('click', async () => {
        const btn = document.getElementById('btnDescargarAudioTraducido');
        const info = document.getElementById('infoAudioTraducido');
        btn.disabled = true;
        btn.textContent = 'Generando...';
        info.style.color = 'var(--text-muted)';
        info.innerHTML = 'Esto puede tardar unos segundos...';
        try {
            const data = await _generarAudioTraducido();
            _descargarArchivo('/reddit/audio_prueba/' + data.archivo, data.archivo);
            info.style.color = 'var(--text-muted)';
            info.textContent = `✅ Descargado (${data.duracion}s)`;
        } catch (e) {
            info.style.color = 'var(--danger)';
            info.textContent = '❌ ' + e.message;
        }
        btn.disabled = false;
        btn.textContent = '⬇️ Descargar audio';
    });

    function aplicarAncho(pct) {
        pct = Math.max(20, Math.min(95, Math.round(pct)));
        document.getElementById('ancho_sub_pct').value = pct;
        document.getElementById('cajaTexto').style.width = pct + '%';
        return pct;
    }
    function aplicarPosY(pct) {
        pct = Math.max(5, Math.min(90, Math.round(pct)));
        document.getElementById('pos_y_pct').value = pct;
        document.getElementById('cajaTexto').style.top = pct + '%';
        return pct;
    }

    (function () {
        const handle = document.getElementById('resizeHandle');
        let arrastrando = false, startY = 0, tamanoInicial = 34;

        handle.addEventListener('mousedown', (e) => { e.stopPropagation(); arrastrando = true; startY = e.clientY; tamanoInicial = parseInt(document.getElementById('tamano_sub').value, 10); });
        handle.addEventListener('touchstart', (e) => { e.stopPropagation(); arrastrando = true; startY = e.touches[0].clientY; tamanoInicial = parseInt(document.getElementById('tamano_sub').value, 10); }, { passive: true });
        
        window.addEventListener('mousemove', (e) => { if (arrastrando) aplicarTamano(tamanoInicial + (startY - e.clientY) / 4); });
        window.addEventListener('touchmove', (e) => { if (arrastrando) aplicarTamano(tamanoInicial + (startY - e.touches[0].clientY) / 4); }, { passive: true });
        
        window.addEventListener('mouseup', () => arrastrando = false);
        window.addEventListener('touchend', () => arrastrando = false);

        document.getElementById('cajaTexto').addEventListener('wheel', (e) => {
            e.preventDefault();
            aplicarTamano(parseInt(document.getElementById('tamano_sub').value, 10) + (e.deltaY < 0 ? 1 : -1));
        }, { passive: false });

        // ---- Tiradores de los costados: ensanchan o achican el cuadro ----
        let arrastrandoAncho = false, startXAncho = 0, anchoInicial = 50, ladoAncho = 1;
        function iniciarAncho(clientX, lado) {
            arrastrandoAncho = true; startXAncho = clientX; ladoAncho = lado;
            anchoInicial = parseInt(document.getElementById('ancho_sub_pct').value, 10);
        }
        document.getElementById('handleDer').addEventListener('mousedown', (e) => { e.stopPropagation(); iniciarAncho(e.clientX, 1); });
        document.getElementById('handleDer').addEventListener('touchstart', (e) => { e.stopPropagation(); iniciarAncho(e.touches[0].clientX, 1); }, { passive: true });
        document.getElementById('handleIzq').addEventListener('mousedown', (e) => { e.stopPropagation(); iniciarAncho(e.clientX, -1); });
        document.getElementById('handleIzq').addEventListener('touchstart', (e) => { e.stopPropagation(); iniciarAncho(e.touches[0].clientX, -1); }, { passive: true });

        function moverAncho(clientX) {
            if (!arrastrandoAncho) return;
            const anchoPreview = document.getElementById('preview').offsetWidth || 400;
            const deltaPct = ((clientX - startXAncho) / anchoPreview) * 100 * ladoAncho * 2;
            aplicarAncho(anchoInicial + deltaPct);
        }
        window.addEventListener('mousemove', (e) => moverAncho(e.clientX));
        window.addEventListener('touchmove', (e) => moverAncho(e.touches[0].clientX), { passive: true });
        window.addEventListener('mouseup', () => arrastrandoAncho = false);
        window.addEventListener('touchend', () => arrastrandoAncho = false);

        // ---- Tirador de arriba: sube o baja el cuadro en la pantalla ----
        let arrastrandoPosY = false, startYPos = 0, posYInicial = 50;
        function iniciarPosY(clientY) {
            arrastrandoPosY = true; startYPos = clientY;
            posYInicial = parseInt(document.getElementById('pos_y_pct').value, 10);
        }
        document.getElementById('handleArriba').addEventListener('mousedown', (e) => { e.stopPropagation(); iniciarPosY(e.clientY); });
        document.getElementById('handleArriba').addEventListener('touchstart', (e) => { e.stopPropagation(); iniciarPosY(e.touches[0].clientY); }, { passive: true });

        function moverPosY(clientY) {
            if (!arrastrandoPosY) return;
            const altoPreview = document.getElementById('preview').offsetHeight || 700;
            const deltaPct = ((clientY - startYPos) / altoPreview) * 100;
            aplicarPosY(posYInicial + deltaPct);
        }
        window.addEventListener('mousemove', (e) => moverPosY(e.clientY));
        window.addEventListener('touchmove', (e) => moverPosY(e.touches[0].clientY), { passive: true });
        window.addEventListener('mouseup', () => arrastrandoPosY = false);
        window.addEventListener('touchend', () => arrastrandoPosY = false);
    })();

    // Etapas del proceso, en el mismo orden y con los mismos rangos de % que reporta el backend.
    const PASOS_BASE = [
        { fase: 'preparando texto',      label: '📝 Preparando texto',      ini: 0,  fin: 8   },
        { fase: 'generando voz',         label: '🎙️ Generando voz',         ini: 8,  fin: 18  },
        { fase: 'preparando imágenes',   label: '🖼️ Preparando imágenes',   ini: 18, fin: 25  },
        { fase: 'generando fondo',       label: '🎞️ Generando fondo',       ini: 25, fin: 65  },
        { fase: 'uniendo escenas',       label: '🔗 Uniendo escenas',       ini: 65, fin: 68  },
        { fase: 'quemando subtítulos',   label: '💬 Quemando subtítulos',   ini: 68, fin: 78  },
        { fase: 'mezclando audio',       label: '🎚️ Mezclando audio',       ini: 78, fin: 90  },
        { fase: 'listo',                 label: '✅ Finalizando',           ini: 90, fin: 100 },
    ];
    const PASO_TRADUCCION = { fase: 'traduciendo texto', label: '🌐 Traduciendo texto', ini: 0, fin: 4 };
    let PASOS = PASOS_BASE;

    function construirPasos() {
        const cont = document.getElementById('listaPasos');
        cont.innerHTML = PASOS.map((p, i) => `
            <div class="paso" id="paso_${i}">
                <div class="paso-etiqueta"><span>${p.label}</span><span><span id="pasoTiempo_${i}" style="color:var(--text-dim); margin-right:6px;"></span><span id="pasoPct_${i}">0%</span></span></div>
                <div class="paso-track"><div class="paso-fill" id="pasoFill_${i}"></div></div>
            </div>
        `).join('');
    }

    // Da formato legible a una duración en segundos: "12.3s" o "1m 05s".
    function formatoTiempo(seg) {
        if (seg === undefined || seg === null) return '';
        seg = Math.max(0, seg);
        if (seg < 60) return `${seg.toFixed(seg < 10 ? 1 : 0)}s`;
        const min = Math.floor(seg / 60);
        const resto = Math.round(seg % 60);
        return `${min}m ${resto.toString().padStart(2, '0')}s`;
    }

    function actualizarPasos(porcentaje, huboError, tiemposFases, faseActual, faseTranscurrido) {
        tiemposFases = tiemposFases || {};
        PASOS.forEach((p, i) => {
            const el = document.getElementById(`paso_${i}`);
            const fill = document.getElementById(`pasoFill_${i}`);
            const pct = document.getElementById(`pasoPct_${i}`);
            const tiempoEl = document.getElementById(`pasoTiempo_${i}`);
            let relleno;
            if (porcentaje >= p.fin) relleno = 100;
            else if (porcentaje <= p.ini) relleno = 0;
            else relleno = Math.round((porcentaje - p.ini) / (p.fin - p.ini) * 100);

            fill.style.width = relleno + '%';
            pct.textContent = relleno + '%';

            // Tiempo: si esta fase ya terminó, muestra cuánto tardó (dato
            // final del backend). Si es la fase que está corriendo ahora
            // mismo, muestra el cronómetro en vivo.
            if (tiemposFases[p.fase] !== undefined) {
                tiempoEl.textContent = formatoTiempo(tiemposFases[p.fase]);
            } else if (p.fase === faseActual && relleno > 0 && relleno < 100) {
                tiempoEl.textContent = formatoTiempo(faseTranscurrido);
            } else {
                tiempoEl.textContent = '';
            }

            el.classList.remove('activo', 'hecho', 'error');
            if (huboError && porcentaje < p.fin) { el.classList.add('error'); }
            else if (relleno >= 100) el.classList.add('hecho');
            else if (relleno > 0) el.classList.add('activo');
        });
    }

    function mostrarSoloProgreso() {
        document.getElementById('formulario').style.display = 'none';
        document.getElementById('procesoView').style.display = 'block';
    }
    function mostrarFormulario() {
        document.getElementById('formulario').style.display = 'block';
        document.getElementById('procesoView').style.display = 'none';
    }

    function mostrarResultado(resultado, tiempoTotal) {
        const res = document.getElementById('resArea');
        const lineaTiempo = tiempoTotal !== undefined && tiempoTotal !== null
            ? `<div class="msg" style="color:var(--text-dim); font-size:12px;">⏱️ Tiempo total: ${formatoTiempo(tiempoTotal)}</div>` : '';
        if (resultado.video) {
            res.innerHTML = `<video controls src="/reddit/videos/${resultado.video}" style="border: 2px solid var(--accent);"></video><div class="msg" style="color:var(--accent);">✅ Video guardado con éxito.</div>${lineaTiempo}<button class="principal" id="btnOtro" type="button">🎬 Generar otro video</button>`;
        } else {
            res.innerHTML = `<div class="msg" style="color:var(--danger)">❌ ${resultado.mensaje}</div>${lineaTiempo}<button class="principal" id="btnOtro" type="button">🎬 Intentar de nuevo</button>`;
        }
        document.getElementById('btnOtro').addEventListener('click', () => {
            res.innerHTML = '';
            mostrarFormulario();
        });
    }

    function actualizarTiempoTotal(segundos) {
        document.getElementById('tiempoTotal').textContent = `⏱️ ${formatoTiempo(segundos)}`;
    }

    function iniciarSondeo() {
        const intervalo = setInterval(async () => {
            const p = await (await fetch('/reddit/progreso')).json();
            const huboError = p.fase === 'error';
            actualizarPasos(p.porcentaje, huboError, p.tiempos_fases, p.fase, p.fase_transcurrido);
            if (p.tiempo_transcurrido !== undefined) actualizarTiempoTotal(p.tiempo_transcurrido);
            if (p.terminado) {
                clearInterval(intervalo);
                actualizarPasos(100, huboError, p.tiempos_fases, null, null);
                mostrarResultado(p.resultado, p.tiempo_total);
            }
        }, 1500);
    }

    async function generarVideo() {
        const form = new FormData();
        ['texto', 'frases_por_bloque', 'posicion', 'color_sub', 'tamano_sub', 'opacidad_sub', 'ancho_sub_pct', 'pos_y_pct', 'fuente_sub', 'velocidad_voz', 'tono_voz', 'musica_genero', 'volumen_musica', 'animacion', 'efecto_video', 'velocidad_efecto'].forEach(id => form.append(id, document.getElementById(id).value));
        form.append('traducir_auto', document.getElementById('traducir_auto').checked ? '1' : '0');
        form.append('fondo_fijo', document.getElementById('fondo_fijo').checked ? '1' : '0');
        form.append('cantidad_imagenes_descargar', document.getElementById('cantidad_imagenes_descargar').value);
        const archivos = document.getElementById('imagenes').files;
        for (let i = 0; i < archivos.length; i++) form.append('imagenes', archivos[i]);

        document.getElementById('resArea').innerHTML = '';
        const traducirActivo = document.getElementById('traducir_auto').checked;
        PASOS = traducirActivo ? [PASO_TRADUCCION, ...PASOS_BASE] : PASOS_BASE;
        construirPasos();
        actualizarPasos(0, false);
        mostrarSoloProgreso();

        const resp = await fetch('/reddit/iniciar', { method: 'POST', body: form });
        const data = await resp.json();
        if (data.error) {
            mostrarFormulario();
            document.getElementById('resArea').innerHTML = `<div class="msg" style="color:var(--danger)">${data.error}</div>`;
            return;
        }
        iniciarSondeo();
    }
    document.getElementById('btnGenerar').addEventListener('click', generarVideo);
    updatePreview();

    (async function comprobarEstadoAlCargar() {
        try {
            const p = await (await fetch('/reddit/progreso')).json();
            if (p.activo) {
                // Se está generando un video: la página se recargó (por ejemplo, por una
                // actualización) mientras tanto. Esto no detiene el proceso en el servidor;
                // simplemente volvemos a mostrar el progreso donde iba.
                PASOS = (p.fase === 'traduciendo texto') ? [PASO_TRADUCCION, ...PASOS_BASE] : PASOS_BASE;
                construirPasos();
                actualizarPasos(p.porcentaje, false, p.tiempos_fases, p.fase, p.fase_transcurrido);
                if (p.tiempo_transcurrido !== undefined) actualizarTiempoTotal(p.tiempo_transcurrido);
                mostrarSoloProgreso();
                iniciarSondeo();
            } else if (p.terminado && p.resultado && (p.resultado.video || p.resultado.mensaje)) {
                // El video terminó (con éxito o con error) mientras la página estaba recargando.
                PASOS = PASOS_BASE;
                construirPasos();
                actualizarPasos(100, p.fase === 'error', p.tiempos_fases, null, null);
                mostrarSoloProgreso();
                mostrarResultado(p.resultado, p.tiempo_total);
            }
        } catch (e) {}
    })();
</script>
</body>
</html>
"""

# =====================================================================
# INTERFAZ DEL PILOTO REDDIT (versión mínima, solo para probar por ahora)
# =====================================================================
# Página aparte y simple: por ahora el objetivo es nada más traer una
# historia + armar el guion con Gemini, y después poder escuchar el audio
# generado con edge_tts como prueba — sin tocar todavía imágenes, efectos,
# subtítulos ni música. Cuando el piloto esté afinado, esto se puede ir
# uniendo al flujo completo de /reddit/generar_automatico.
PLANTILLA_PILOTO = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Piloto Reddit — prueba</title>
<style>
    body { background:#150e2b; color:#f4f0ff; font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; margin:0; padding:16px; max-width:640px; margin:0 auto; }
    h1 { font-size:16px; letter-spacing:1px; text-transform:uppercase; color:#ff2e88; margin-bottom:4px; }
    p.sub { font-size:12px; color:#9686c0; margin-top:0; margin-bottom:20px; }
    button.paso { display:block; width:100%; padding:14px; margin-bottom:14px; border-radius:10px; border:1px solid #ff2e88; background:linear-gradient(180deg,#ff2e88,#c4116a); color:#150e2b; font-weight:700; font-size:13px; letter-spacing:0.5px; cursor:pointer; }
    button.paso:disabled { opacity:0.4; cursor:not-allowed; }
    .info { font-size:12px; color:#9686c0; margin-bottom:6px; }
    .info b { color:#f4f0ff; }
    textarea { width:100%; min-height:220px; box-sizing:border-box; background:#1f1640; color:#f4f0ff; border:1px solid #4a3a7a; border-radius:8px; padding:10px; font-size:13px; margin-bottom:14px; }
    #estadoAudio { font-size:12px; color:#00e5ff; margin-bottom:10px; }
    audio { width:100%; margin-bottom:10px; }
    .msg-error { color:#ff4d4d; font-size:12px; margin-bottom:10px; }
</style>
</head>
<body>
    <h1>Piloto Reddit</h1>
    <p class="sub">Paso 1: traer una historia y armar el guion. Paso 2: escuchar el audio de prueba (todavía sin video).</p>

    <button class="paso" id="btnTraer" type="button">1️⃣ Traer historia y generar guion</button>
    <div id="infoHistoria"></div>
    <textarea id="guion" placeholder="Acá va a aparecer el guion generado. También lo podés editar a mano antes de generar el audio de prueba." disabled></textarea>

    <button class="paso" id="btnAudio" type="button" disabled>2️⃣ Generar audio de prueba</button>
    <div id="estadoAudio"></div>
    <div id="resAudio"></div>

<script>
    const btnTraer = document.getElementById('btnTraer');
    const btnAudio = document.getElementById('btnAudio');
    const infoHistoria = document.getElementById('infoHistoria');
    const guionArea = document.getElementById('guion');
    const estadoAudio = document.getElementById('estadoAudio');
    const resAudio = document.getElementById('resAudio');

    btnTraer.addEventListener('click', async () => {
        btnTraer.disabled = true;
        btnTraer.textContent = 'Buscando historia...';
        infoHistoria.innerHTML = '';
        resAudio.innerHTML = '';
        estadoAudio.textContent = '';
        try {
            const resp = await fetch('/reddit/traer_historia');
            const data = await resp.json();
            if (!resp.ok || data.error) {
                infoHistoria.innerHTML = `<div class="msg-error">❌ ${data.error || 'Error desconocido'}</div>`;
            } else {
                infoHistoria.innerHTML = `<div class="info"><b>r/${data.subreddit}</b> — ${data.titulo} (${data.upvotes} upvotes)</div>`;
                guionArea.value = data.guion;
                guionArea.disabled = false;
                btnAudio.disabled = false;
            }
        } catch (e) {
            infoHistoria.innerHTML = `<div class="msg-error">❌ ${e}</div>`;
        }
        btnTraer.disabled = false;
        btnTraer.textContent = '1️⃣ Traer historia y generar guion';
    });

    btnAudio.addEventListener('click', async () => {
        btnAudio.disabled = true;
        btnAudio.textContent = 'Generando audio...';
        resAudio.innerHTML = '';
        estadoAudio.textContent = 'Esto puede tardar unos segundos...';
        try {
            const form = new FormData();
            form.append('guion', guionArea.value);
            const resp = await fetch('/reddit/generar_audio_prueba', { method: 'POST', body: form });
            const data = await resp.json();
            if (!resp.ok || data.error) {
                estadoAudio.innerHTML = `<div class="msg-error">❌ ${data.error || 'Error desconocido'}</div>`;
            } else {
                estadoAudio.textContent = `✅ Listo (${data.duracion}s)`;
                resAudio.innerHTML = `<audio controls src="/reddit/audio_prueba/${data.archivo}"></audio>`;
            }
        } catch (e) {
            estadoAudio.innerHTML = `<div class="msg-error">❌ ${e}</div>`;
        }
        btnAudio.disabled = false;
        btnAudio.textContent = '2️⃣ Generar audio de prueba';
    });
</script>
</body>
</html>
"""
@reddit_bp.route("/")
def inicio():
    # Autoagrega un ?v=<numero random> a la URL si no lo tiene todavía, para
    # que cada visita se vea como una URL "distinta" y el navegador nunca
    # reutilice una versión vieja guardada en caché (esto es aparte del
    # header Cache-Control de abajo, que ya evita el cacheo del lado del
    # navegador; el ?v= random cubre también proxies/DNS intermedios y
    # evita tener que escribirlo a mano cada vez).
    if "v" not in request.args:
        v = random.randint(1000, 9999)
        return redirect(url_for("reddit.inicio", v=v))
    res = make_response(render_template_string(
        PLANTILLA, version=VERSION_SCRIPT,
    ))
    res.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return res

@reddit_bp.route("/piloto")
def piloto():
    res = make_response(PLANTILLA_PILOTO)
    res.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return res

@reddit_bp.route("/iniciar", methods=["POST"])
def iniciar():
    logger, ruta_log = crear_logger_video()
    logger.info("Solicitud de generación recibida (clic en 'Generar video').")

    texto = request.form.get("texto", "").strip()[:500000]
    if not texto:
        logger.error("Texto vacío: se cancela antes de empezar.")
        cerrar_logger_video(logger)
        return jsonify({"error": "Texto vacío"}), 400
    try:
        frases_por_bloque = int(request.form.get("frases_por_bloque", 3))
    except (TypeError, ValueError):
        frases_por_bloque = 3
    frases_por_bloque = max(1, min(10, frases_por_bloque))

    posicion = request.form.get("posicion", "centro")
    color_sub = request.form.get("color_sub", "oro_viejo")

    # APLICACIÓN DE AUMENTO DE LÍMITE A 100
    try:
        tamano_sub = int(float(request.form.get("tamano_sub", 42)))
    except (TypeError, ValueError):
        tamano_sub = 42
    tamano_sub = max(12, min(100, tamano_sub))

    try:
        opacidad_sub = int(float(request.form.get("opacidad_sub", 100)))
    except (TypeError, ValueError):
        opacidad_sub = 100
    opacidad_sub = max(20, min(100, opacidad_sub))

    fuente_sub = request.form.get("fuente_sub", FUENTE_POR_DEFECTO)
    # velocidad_voz y tono_voz llegan como números (de las barras deslizantes);
    # se recortan a los límites válidos recién al usarlos en _formatear_ajuste_voz.
    velocidad_voz = request.form.get("velocidad_voz", VELOCIDAD_VOZ_POR_DEFECTO)
    tono_voz = request.form.get("tono_voz", TONO_VOZ_POR_DEFECTO)
    musica_genero = request.form.get("musica_genero", "piano")
    try:
        volumen_musica = int(request.form.get("volumen_musica", 12))
    except (TypeError, ValueError):
        volumen_musica = 12
    volumen_musica = max(0, min(100, volumen_musica))
    animacion = request.form.get("animacion", "estatico")
    traducir_auto = request.form.get("traducir_auto", "0") == "1"
    fondo_fijo = request.form.get("fondo_fijo", "0") == "1"
    try:
        cantidad_imagenes_descargar = int(request.form.get("cantidad_imagenes_descargar", 0))
    except (TypeError, ValueError):
        cantidad_imagenes_descargar = 0
    cantidad_imagenes_descargar = max(0, min(20, cantidad_imagenes_descargar))
    try:
        ancho_sub_pct = int(float(request.form.get("ancho_sub_pct", 73)))
    except (TypeError, ValueError):
        ancho_sub_pct = 73
    ancho_sub_pct = max(20, min(95, ancho_sub_pct))
    try:
        pos_y_pct = int(float(request.form.get("pos_y_pct", 83)))
    except (TypeError, ValueError):
        pos_y_pct = 83
    pos_y_pct = max(5, min(90, pos_y_pct))
    efecto_video = request.form.get("efecto_video", "ninguno")
    if efecto_video not in {"ninguno", "ceniza", "grano_pelicula", "vela", "niebla", "rayo_luz", "vineta", "pergamino"}:
        efecto_video = "ninguno"
    # Velocidad de los efectos "ceniza" y "vela" (el resto la ignora). Se
    # valida acá con un valor por defecto razonable; el recorte final a los
    # límites permitidos ocurre en aplicar_efecto_video.
    try:
        velocidad_efecto = float(request.form.get("velocidad_efecto", VELOCIDAD_EFECTO_POR_DEFECTO))
    except (TypeError, ValueError):
        velocidad_efecto = VELOCIDAD_EFECTO_POR_DEFECTO

    rutas_imagenes_subidas = []
    for archivo in request.files.getlist("imagenes"):
        if archivo and archivo.filename:
            ruta = os.path.join(CARPETA_IMAGENES_SUBIDAS, f"{int(time.time())}_{archivo.filename}")
            archivo.save(ruta)
            rutas_imagenes_subidas.append(ruta)

    with CANDADO_ESTADO:
        if ESTADO["activo"]:
            logger.error("Ya había un video generándose: se rechaza esta nueva solicitud.")
            cerrar_logger_video(logger)
            return jsonify({"error": "Ya hay un video generándose"}), 409
        ahora = time.time()
        ESTADO["activo"], ESTADO["terminado"], ESTADO["fase"], ESTADO["porcentaje"] = True, False, "preparando", 0
        ESTADO["tiempo_inicio_video"], ESTADO["tiempo_fase_inicio"] = ahora, ahora
        ESTADO["tiempos_fases"], ESTADO["tiempo_total"] = {}, None

    logger.info(
        f"Parámetros: frases_por_bloque={frases_por_bloque}, posicion={posicion}, "
        f"color_sub={color_sub}, tamano_sub={tamano_sub}, opacidad_sub={opacidad_sub}, fuente_sub={fuente_sub}, musica_genero={musica_genero}, "
        f"volumen_musica={volumen_musica}, animacion={animacion}, traducir_auto={traducir_auto}, "
        f"fondo_fijo={fondo_fijo}, imagenes_subidas={len(rutas_imagenes_subidas)}, largo_texto={len(texto)}, "
        f"efecto_video={efecto_video}, velocidad_efecto={velocidad_efecto}"
    )

    threading.Thread(
        target=procesar_todo,
        args=(texto, frases_por_bloque, posicion, color_sub, tamano_sub, fuente_sub, musica_genero, volumen_musica, rutas_imagenes_subidas, animacion, traducir_auto, fondo_fijo, velocidad_voz, tono_voz),
        kwargs={"opacidad_sub": opacidad_sub, "cantidad_imagenes_descargar": cantidad_imagenes_descargar, "ancho_sub_pct": ancho_sub_pct, "pos_y_pct": pos_y_pct, "efecto_video": efecto_video, "velocidad_efecto": velocidad_efecto, "logger": logger, "ruta_log": ruta_log},
        daemon=True,
    ).start()
    return jsonify({"ok": True})

@reddit_bp.route("/descartar_historia", methods=["POST"])
def descartar_historia():
    """Marca como usados los IDs de la historia (o grupo de historias) que
    se está mostrando en el piloto, SIN generar video, para que el próximo
    'Traer historia de Reddit' devuelva una distinta. Es el mismo mecanismo
    que ya usa /reddit/generar_automatico, solo que disparado a mano."""
    try:
        ids = json.loads(request.form.get("ids", "[]"))
    except Exception:
        ids = []
    if not ids:
        return jsonify({"error": "No se recibieron IDs para descartar"}), 400
    for id_post in ids:
        _guardar_id_usado(id_post)
    return jsonify({"ok": True, "descartados": len(ids)})


@reddit_bp.route("/traer_historia")
def traer_historia():
    """Trae de Reddit el grupo de 1 a 3 historias (según cuánto haga falta
    para llegar a los 28-30 minutos objetivo) y arma un solo guion
    adaptado, EN SU IDIOMA ORIGINAL (inglés, sin traducir), pero NO genera
    el video todavía. Sirve para revisar en pantalla que el guion está
    bien antes de gastar tiempo de render.

    v5.0: antes devolvía el guion ya traducido al español con
    generar_guion_reddit(); ahora la traducción es una acción aparte
    (ver /traducir_guion), así que acá se usa generar_guion_ingles() para
    devolver el guion tal cual, en inglés."""
    global _ULTIMO_GRUPO_HISTORIAS
    logger, ruta_log = crear_logger_video()
    try:
        grupo = obtener_historia_reddit(logger=logger)
        if not grupo:
            logger.warning("No se encontró ninguna historia nueva que cumpla los filtros.")
            return jsonify({"error": "No se encontró ninguna historia nueva que cumpla los filtros"}), 404

        # Se guarda el grupo crudo (sin adaptar) en memoria del servidor
        # por si algún flujo futuro lo necesita reusar (v3.4).
        _ULTIMO_GRUPO_HISTORIAS = grupo

        guion = generar_guion_ingles(grupo, logger=logger)
        subreddits_unicos = sorted(set(h["subreddit"] for h in grupo))
        upvotes_total = sum(h["upvotes"] for h in grupo)
        palabras_total = sum(len(h["cuerpo"].split()) for h in grupo)
        logger.info(
            f"Historia(s) traída(s): {len(grupo)} — "
            + "; ".join(f"r/{h['subreddit']} — {h['titulo']}" for h in grupo)
        )
        return jsonify({
            "ok": True,
            "cantidad": len(grupo),
            "ids": [h["id"] for h in grupo],
            "subreddit": ", ".join(subreddits_unicos),
            "titulo": grupo[0]["titulo"] if len(grupo) == 1 else f"{len(grupo)} historias combinadas",
            "titulos": [h["titulo"] for h in grupo],
            "upvotes": upvotes_total,
            "palabras_originales": palabras_total,
            "url": grupo[0]["url"] if len(grupo) == 1 else None,
            "guion": guion,
        })
    finally:
        cerrar_logger_video(logger)


# Última historia (cruda, sin adaptar) traída con /traer_historia. Server
# local de un solo usuario (Termux), así que una variable simple alcanza,
# sin necesidad de sesiones por usuario.
_ULTIMO_GRUPO_HISTORIAS = []


@reddit_bp.route("/traducir_guion", methods=["POST"])
def traducir_guion():
    """v5.0: traduce al español el guion que esté en el cuadro 'Guion
    (idioma original)' (tal cual lo mande el frontend, editado o no).
    Usa la misma traducción por DeepL que ya existía en el proyecto;
    la que se anunciaba como Gemini se había sacado en la v4.7 junto con
    el resto del probador de voces, así que se usa DeepL, que es la
    traducción que sigue disponible en el código."""
    guion = request.form.get("guion", "").strip()
    if not guion:
        return jsonify({"error": "No hay guion para traducir"}), 400

    logger, ruta_log = crear_logger_video()
    try:
        guion_traducido = traducir_texto_deepl(guion, "es", logger=logger)
        return jsonify({"ok": True, "guion_traducido": guion_traducido})
    except Exception as e:
        logger.error(f"Fallo la traducción del guion: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cerrar_logger_video(logger)


@reddit_bp.route("/generar_audio_ingles", methods=["POST"])
def generar_audio_ingles():
    """Genera el audio del guion en su idioma original (voz británica
    VOZ_NARRADOR_INGLES), a partir del texto que mande el frontend —igual
    que /generar_audio_prueba pero con la voz en inglés.

    v5.0: antes regeneraba el guion desde cero con generar_guion_ingles()
    y usaba velocidad/tono fijos (TONO_NARRADOR_INGLES/
    VELOCIDAD_NARRADOR_INGLES). Ahora usa el texto tal cual esté en el
    cuadro "Guion (idioma original)" (editado a mano o no) y acepta
    velocidad_voz/tono_voz desde el frontend, compartiendo los mismos
    sliders que el audio en español."""
    guion = request.form.get("guion", "").strip()
    velocidad_voz = request.form.get("velocidad_voz", VELOCIDAD_VOZ_POR_DEFECTO)
    tono_voz = request.form.get("tono_voz", TONO_VOZ_POR_DEFECTO)
    if not guion:
        return jsonify({"error": "Escribí o traé un guion primero."}), 400

    logger, ruta_log = crear_logger_video()
    try:
        texto_limpio = limpiar_texto_para_voz(guion)
        if not texto_limpio:
            logger.warning("El guion en inglés quedó vacío después de limpiarlo para voz.")
            return jsonify({"error": "El guion quedó vacío después de limpiarlo"}), 400

        velocidad_final = _formatear_ajuste_voz(velocidad_voz, "%", VELOCIDAD_VOZ_POR_DEFECTO, VELOCIDAD_VOZ_MIN, VELOCIDAD_VOZ_MAX)
        tono_final = _formatear_ajuste_voz(tono_voz, "Hz", TONO_VOZ_POR_DEFECTO, TONO_VOZ_MIN, TONO_VOZ_MAX)

        nombre_archivo = f"audio_ingles_{int(time.time()*1000)}.mp3"
        ruta_audio = os.path.join(CARPETA_PRUEBAS_AUDIO_REDDIT, nombre_archivo)
        logger.info(f"Generando audio en inglés con voz={VOZ_NARRADOR_INGLES} | velocidad={velocidad_final} | tono={tono_final}")
        generar_audio_y_tiempos(
            texto_limpio, VOZ_NARRADOR_INGLES, ruta_audio, logger=logger,
            tono=tono_final, velocidad=velocidad_final,
        )
        duracion = obtener_duracion_audio(ruta_audio)
        logger.info(f"Audio en inglés generado: {nombre_archivo} ({duracion:.1f}s)")

        return jsonify({
            "ok": True,
            "archivo": nombre_archivo,
            "duracion": round(duracion, 1),
        })
    except Exception as e:
        logger.error(f"Fallo la generación del audio en inglés: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cerrar_logger_video(logger)


@reddit_bp.route("/generar_audio_prueba", methods=["POST"])
def generar_audio_prueba():
    """Prueba suelta: toma el guion (texto plano, tal cual quedó en el
    textarea del piloto, ya sea generado por Gemini o editado a mano) y
    genera SOLO el audio con la misma voz que se usaría en el video real
    (VOZ_NARRADOR), sin tocar imágenes, subtítulos ni música. Sirve
    para escuchar cómo queda la narración antes de meterse con el resto
    del pipeline.

    v4.7: acepta velocidad_voz/tono_voz desde el frontend (antes siempre
    usaba los valores fijos TONO/VELOCIDAD), para poder ajustarlos desde
    los controles que quedaron junto a los botones "Escuchar ES"/
    "Descargar audio ES"."""
    guion = request.form.get("guion", "").strip()
    velocidad_voz = request.form.get("velocidad_voz", VELOCIDAD_VOZ_POR_DEFECTO)
    tono_voz = request.form.get("tono_voz", TONO_VOZ_POR_DEFECTO)
    if not guion:
        return jsonify({"error": "No hay guion para generar el audio"}), 400

    logger, ruta_log = crear_logger_video()
    try:
        texto_limpio = limpiar_texto_para_voz(guion)
        if not texto_limpio:
            logger.warning("El guion quedó vacío después de limpiarlo para voz.")
            return jsonify({"error": "El guion quedó vacío después de limpiarlo"}), 400

        velocidad_final = _formatear_ajuste_voz(velocidad_voz, "%", VELOCIDAD_VOZ_POR_DEFECTO, VELOCIDAD_VOZ_MIN, VELOCIDAD_VOZ_MAX)
        tono_final = _formatear_ajuste_voz(tono_voz, "Hz", TONO_VOZ_POR_DEFECTO, TONO_VOZ_MIN, TONO_VOZ_MAX)

        nombre_archivo = f"prueba_audio_{int(time.time()*1000)}.mp3"
        ruta_audio = os.path.join(CARPETA_PRUEBAS_AUDIO_REDDIT, nombre_archivo)
        logger.info(f"Generando audio de prueba con voz={VOZ_NARRADOR} | velocidad={velocidad_final} | tono={tono_final}")
        generar_audio_y_tiempos(texto_limpio, VOZ_NARRADOR, ruta_audio, logger=logger, tono=tono_final, velocidad=velocidad_final)
        duracion = obtener_duracion_audio(ruta_audio)
        logger.info(f"Audio de prueba generado: {nombre_archivo} ({duracion:.1f}s)")

        # Los audios de prueba en español son descartables: se borran los
        # anteriores para no ir acumulando archivos sueltos en cada
        # intento. Los de inglés (prefijo audio_ingles_) se respetan, para
        # no borrar la descarga en inglés al probar el audio en español.
        try:
            for nombre in os.listdir(CARPETA_PRUEBAS_AUDIO_REDDIT):
                if nombre != nombre_archivo and not nombre.startswith("audio_ingles_"):
                    try: os.remove(os.path.join(CARPETA_PRUEBAS_AUDIO_REDDIT, nombre))
                    except Exception: pass
        except Exception:
            pass

        return jsonify({"ok": True, "archivo": nombre_archivo, "duracion": round(duracion, 1)})
    except Exception as e:
        logger.error(f"Fallo la generación del audio de prueba: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cerrar_logger_video(logger)


@reddit_bp.route("/audio_prueba/<path:archivo>")
def servir_audio_prueba(archivo):
    base_real = os.path.realpath(CARPETA_PRUEBAS_AUDIO_REDDIT)
    ruta_real = os.path.realpath(os.path.join(CARPETA_PRUEBAS_AUDIO_REDDIT, archivo))
    if not (ruta_real == base_real or ruta_real.startswith(base_real + os.sep)):
        return "No encontrado", 404
    return send_from_directory(os.path.dirname(ruta_real), os.path.basename(ruta_real))


@reddit_bp.route("/generar_automatico", methods=["POST"])
def generar_automatico():
    """Etapa 3 del piloto: todo en uno, disparado con un solo click.
    Trae el grupo de 1 a 3 historias (según haga falta para llegar a los
    28-30 minutos objetivo), arma el guion, y lo manda al mismo pipeline
    de generación de video que ya usa /reddit/iniciar, con valores por
    defecto razonables (los mismos que la interfaz manual)."""
    logger, ruta_log = crear_logger_video()
    logger.info("Solicitud de generación automática recibida (piloto Reddit).")

    grupo = obtener_historia_reddit(logger=logger)
    if not grupo:
        logger.warning("No se encontró ninguna historia nueva que cumpla los filtros.")
        cerrar_logger_video(logger)
        return jsonify({"error": "No se encontró ninguna historia nueva que cumpla los filtros"}), 404

    guion = generar_guion_reddit(grupo, logger=logger)
    titulo_resumen = grupo[0]["titulo"] if len(grupo) == 1 else f"{len(grupo)} historias combinadas"
    subreddits_unicos = sorted(set(h["subreddit"] for h in grupo))
    logger.info(
        f"Historia(s) elegida(s): {len(grupo)} — "
        + "; ".join(f"r/{h['subreddit']} — {h['titulo']} ({h['upvotes']} upvotes)" for h in grupo)
    )

    with CANDADO_ESTADO:
        if ESTADO["activo"]:
            logger.error("Ya había un video generándose: se rechaza esta nueva solicitud.")
            cerrar_logger_video(logger)
            return jsonify({"error": "Ya hay un video generándose"}), 409
        ahora = time.time()
        ESTADO["activo"], ESTADO["terminado"], ESTADO["fase"], ESTADO["porcentaje"] = True, False, "preparando", 0
        ESTADO["tiempo_inicio_video"], ESTADO["tiempo_fase_inicio"] = ahora, ahora
        ESTADO["tiempos_fases"], ESTADO["tiempo_total"] = {}, None

    # Recién acá se marca cada historia del grupo como usada: si algo falla
    # antes de este punto, las historias quedan disponibles para reintentar.
    for h in grupo:
        _guardar_id_usado(h["id"])

    threading.Thread(
        target=procesar_todo,
        args=(guion, 3, "centro", "oro_viejo", 42, FUENTE_POR_DEFECTO, "piano", 12, [], "estatico", False, False, VELOCIDAD_VOZ_POR_DEFECTO, TONO_VOZ_POR_DEFECTO),
        kwargs={"opacidad_sub": 100, "cantidad_imagenes_descargar": 0, "ancho_sub_pct": 73, "pos_y_pct": 83, "efecto_video": "ninguno", "velocidad_efecto": VELOCIDAD_EFECTO_POR_DEFECTO, "logger": logger, "ruta_log": ruta_log},
        daemon=True,
    ).start()
    return jsonify({"ok": True, "titulo": titulo_resumen, "subreddit": ", ".join(subreddits_unicos)})


@reddit_bp.route("/progreso")
def progreso():
    with CANDADO_ESTADO:
        estado_copia = dict(ESTADO)
    # Mientras se está generando, se calcula "en vivo" cuánto lleva corriendo
    # el video completo y la fase actual, para que el navegador pueda
    # mostrar un cronómetro que avanza aunque el backend no haya avisado
    # todavía un cambio de fase (por ejemplo, un paso de ffmpeg largo).
    if estado_copia.get("activo"):
        if estado_copia.get("tiempo_inicio_video"):
            estado_copia["tiempo_transcurrido"] = round(time.time() - estado_copia["tiempo_inicio_video"], 1)
        if estado_copia.get("tiempo_fase_inicio"):
            estado_copia["fase_transcurrido"] = round(time.time() - estado_copia["tiempo_fase_inicio"], 1)
    return jsonify(estado_copia)

@reddit_bp.route("/videos/<path:archivo>")
def servir_video(archivo):
    # 'archivo' ahora puede incluir la subcarpeta del proyecto (ej.
    # "mi_video_20260804_195000/mi_video_20260804_195000_estoico.mp4"), no
    # solo un nombre de archivo suelto. Se resuelve la ruta real y se
    # verifica que siga quedando adentro de CARPETA_VIDEOS, para no permitir
    # que alguien pida algo como "../../otra_carpeta/archivo".
    base_real = os.path.realpath(CARPETA_VIDEOS)
    ruta_real = os.path.realpath(os.path.join(CARPETA_VIDEOS, archivo))
    if not (ruta_real == base_real or ruta_real.startswith(base_real + os.sep)):
        return "No encontrado", 404
    return send_from_directory(os.path.dirname(ruta_real), os.path.basename(ruta_real))

# ============================================================
# ---- arranque (antes gen_estoico-1.py) ----
# ============================================================
import random
import socket
import subprocess
import threading
import time

from flask import Flask, redirect



def _obtener_ip_lan():
    """Obtiene la IP local del celular en la red WiFi (para acceder desde otro dispositivo)."""
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
    try: subprocess.run(["termux-open-url", f"http://127.0.0.1:{puerto}"], check=True)
    except Exception: pass


def main():
    app = Flask(__name__)
    app.register_blueprint(reddit_bp, url_prefix="/reddit")

    @app.route("/")
    def _raiz():
        return redirect("/reddit/")

    puerto = random.randint(6000, 6999)  # puerto al azar en cada arranque (evita choques con un proceso viejo que haya quedado colgado en el puerto anterior)
    ip_lan = _obtener_ip_lan()

    print(f"\033[1;93m*** Story Engine V{VERSION_SCRIPT} ***\033[0m")
    print(f"Accede desde este celular: http://127.0.0.1:{puerto}")
    print(f"Accede desde otro dispositivo en la misma red: http://{ip_lan}:{puerto}")
    print("\nPresiona Ctrl+C para apagar.\n")

    threading.Thread(target=_abrir_navegador, args=(puerto,), daemon=True).start()
    # Chequeo/actualización de edge-tts en segundo plano: no bloquea el
    # arranque del servidor ni la apertura del navegador, y si falla (sin
    # red en ese momento, por ejemplo) simplemente no hace nada.
    threading.Thread(target=actualizar_edge_tts_si_hace_falta, daemon=True).start()

    try:
        app.run(host="0.0.0.0", port=puerto, debug=False, threaded=True)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
