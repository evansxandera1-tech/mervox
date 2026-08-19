#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# lanzar_ultima_version.sh
# -----------------------------------------------------------------
# Busca en todo el almacenamiento del celular (accesible desde
# Termux) todas las copias de un script Python con un nombre dado,
# lee la variable VERSION = "X.Y" que cada copia declara dentro del
# archivo, y ejecuta automáticamente la copia con el número de
# versión más alto — sin importar en qué carpeta esté guardada
# ni qué fecha de modificación tenga.
#
# Uso:
#   ./lanzar_ultima_version.sh                -> usa NOMBRE_SCRIPT de abajo
#   ./lanzar_ultima_version.sh otro_nombre.py  -> busca ese nombre en su lugar
# =====================================================================

set -euo pipefail

# --- Configuración -----------------------------------------------
NOMBRE_SCRIPT="${1:-transcribir_web_v3-2.py}"

# Carpetas donde se va a buscar. Se puede ampliar esta lista si
# guardas descargas en otras rutas.
CARPETAS_BUSQUEDA=(
  "/sdcard"
  "/storage/emulated/0"
  "$HOME"
)
# -------------------------------------------------------------------

echo "Buscando todas las copias de: $NOMBRE_SCRIPT"
echo "-------------------------------------------------------------"

# 1) Encontrar todas las rutas que coincidan con el nombre, sin duplicar
mapfile -t CANDIDATOS < <(
  for carpeta in "${CARPETAS_BUSQUEDA[@]}"; do
    [ -d "$carpeta" ] || continue
    find "$carpeta" -type f -iname "$NOMBRE_SCRIPT" 2>/dev/null
  done | sort -u
)

if [ "${#CANDIDATOS[@]}" -eq 0 ]; then
  echo "No se encontró ningún archivo llamado '$NOMBRE_SCRIPT' en el celular."
  exit 1
fi

# 2) Para cada candidato, extraer su VERSION (si no la tiene, queda como 0)
MEJOR_ARCHIVO=""
MEJOR_VERSION="0"

for archivo in "${CANDIDATOS[@]}"; do
  version_encontrada=$(grep -oE 'VERSION[[:space:]]*=[[:space:]]*["'"'"']([0-9]+(\.[0-9]+)*)' "$archivo" 2>/dev/null \
    | head -1 \
    | grep -oE '[0-9]+(\.[0-9]+)*' || true)

  version_encontrada="${version_encontrada:-0}"
  echo "  - $archivo   (VERSION detectada: $version_encontrada)"

  # Comparación numérica de versiones tipo "3.2" vs "3.10" usando sort -V
  mayor=$(printf '%s\n%s\n' "$MEJOR_VERSION" "$version_encontrada" | sort -V | tail -1)
  if [ "$mayor" = "$version_encontrada" ] && [ "$version_encontrada" != "$MEJOR_VERSION" ]; then
    MEJOR_VERSION="$version_encontrada"
    MEJOR_ARCHIVO="$archivo"
  elif [ -z "$MEJOR_ARCHIVO" ]; then
    MEJOR_ARCHIVO="$archivo"
  fi
done

echo "-------------------------------------------------------------"
echo "Versión más reciente encontrada: $MEJOR_VERSION"
echo "Ejecutando: $MEJOR_ARCHIVO"
echo "-------------------------------------------------------------"

exec python "$MEJOR_ARCHIVO"
