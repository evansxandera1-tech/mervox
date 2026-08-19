"""
subir_drive.py - v1.0
Sube todos los clips de clips_finales/ a una carpeta "mervox" en Google Drive,
usando una cuenta de servicio (service_account.json).
"""
import os
import glob
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(
    filename="mervox.log",
    level=logging.INFO,
    format="%(asctime)s [subir_drive] %(levelname)s: %(message)s"
)
log = logging.getLogger("subir_drive")

SCOPES = ["https://www.googleapis.com/auth/drive"]
CARPETA_DESTINO = "mervox"

def conectar():
    ruta_cred = os.environ.get("GDRIVE_CREDENTIALS_PATH", "service_account.json")
    creds = service_account.Credentials.from_service_account_file(ruta_cred, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def obtener_o_crear_carpeta(servicio, nombre):
    query = f"name='{nombre}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    resultados = servicio.files().list(q=query, fields="files(id, name)").execute()
    archivos = resultados.get("files", [])
    if archivos:
        return archivos[0]["id"]
    metadata = {"name": nombre, "mimeType": "application/vnd.google-apps.folder"}
    carpeta = servicio.files().create(body=metadata, fields="id").execute()
    log.info(f"Carpeta '{nombre}' creada en Drive")
    return carpeta["id"]

def subir_archivo(servicio, ruta, carpeta_id):
    nombre = os.path.basename(ruta)
    metadata = {"name": nombre, "parents": [carpeta_id]}
    media = MediaFileUpload(ruta, resumable=True)
    servicio.files().create(body=metadata, media_body=media, fields="id").execute()
    log.info(f"Subido: {nombre}")

def main():
    servicio = conectar()
    carpeta_id = obtener_o_crear_carpeta(servicio, CARPETA_DESTINO)

    clips = sorted(glob.glob("clips_finales/*.mp4"))
    if not clips:
        log.warning("No hay clips para subir")
        print("No hay clips en clips_finales/")
        return

    for clip in clips:
        subir_archivo(servicio, clip, carpeta_id)

    print(f"OK: {len(clips)} clips subidos a Drive/{CARPETA_DESTINO}")

if __name__ == "__main__":
    main()
