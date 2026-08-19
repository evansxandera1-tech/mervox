# mervox v1.0

Bot que graba lives de TikTok, genera clips virales verticales con
subtitulos karaoke y los sube a Google Drive.

## Disparo
Se dispara con `/grabar usuario_tiktok` desde el bot de Telegram, que
llama al repository_dispatch de este repo (evento `grabar`).

## Secrets necesarios en GitHub
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- GEMINI_API_KEY
- GDRIVE_CREDENTIALS_JSON (contenido completo del service account)
- TIKTOK_SESSIONID_SS

## Panel de control (Termux)

Abrir http://localhost:8098 en el navegador del celular.
