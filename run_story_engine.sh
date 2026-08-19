#!/data/data/com.termux/files/usr/bin/bash
DESCARGAS="$HOME/storage/downloads"
DESTINO="$HOME/story_engine"
mkdir -p "$DESTINO"

ULTIMO=$(ls -t "$DESCARGAS"/story_engine*.py 2>/dev/null | head -n 1)
if [ -z "$ULTIMO" ]; then
    echo "❌ No se encontró ningún story_engine*.py en Download."
    exit 1
fi

echo "📥 Usando: $(basename "$ULTIMO")"
cp "$ULTIMO" "$DESTINO/story_engine.py"
cd "$DESTINO" || exit 1
python3 story_engine.py
