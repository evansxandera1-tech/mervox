#!/data/data/com.termux/files/usr/bin/bash
# Copia siempre el transcribir_web_v*.py MÁS RECIENTE de Downloads
# (por fecha de descarga, sin importar el número de versión del
# nombre) a ~/transcribir_web_actual.py, y lo corre.

CARPETA_DESCARGAS="$HOME/storage/downloads"
DESTINO="$HOME/transcribir_web_actual.py"

ULTIMO=$(ls -t "$CARPETA_DESCARGAS"/transcribir_web_v*.py 2>/dev/null | head -n 1)

if [ -z "$ULTIMO" ]; then
    echo "No se encontró ningún transcribir_web_v*.py en Downloads."
    exit 1
fi

cp "$ULTIMO" "$DESTINO"
echo "Usando: $(basename "$ULTIMO")"
python "$DESTINO"
