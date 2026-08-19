"""
mervox v1.0 - actualizar_estado.py
Genera estado.json con el resultado de la corrida (usuario, clips generados,
estado final) para que app.py lo muestre en la interfaz web.
"""

import argparse
import glob
import json
import os
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usuario", required=True)
    parser.add_argument("--clips_dir", required=True)
    parser.add_argument("--estado", required=True, choices=["ok", "error"])
    parser.add_argument("--mensaje", default="")
    args = parser.parse_args()

    clips = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(args.clips_dir, "clip_*.mp4"))
    )

    data = {
        "usuario": args.usuario,
        "estado": args.estado,
        "actualizado": datetime.now(timezone.utc).isoformat(),
        "clips": clips,
        "log": args.mensaje,
    }

    with open("estado.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("estado.json actualizado.")


if __name__ == "__main__":
    main()
