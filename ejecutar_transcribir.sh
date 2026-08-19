#!/data/data/com.termux/files/usr/bin/bash
# Busca la version mas reciente de "transcribir_web" en todo el almacenamiento
# y la ejecuta, sin importar la carpeta donde este guardada.

echo "Buscando versiones de transcribir_web..."

ARCHIVO_MAS_RECIENTE=$(find /storage/emulated/0 /sdcard ~ -iname "transcribir_web_v*.py" 2>/dev/null \
  | sort -t v -k2 -V \
  | tail -n 1)

if [ -z "$ARCHIVO_MAS_RECIENTE" ]; then
    echo "No se encontro ningun archivo transcribir_web_v*.py"
    exit 1
fi

echo "Version mas reciente encontrada:"
echo "$ARCHIVO_MAS_RECIENTE"
echo ""
echo "Iniciando..."
python "$ARCHIVO_MAS_RECIENTE"
