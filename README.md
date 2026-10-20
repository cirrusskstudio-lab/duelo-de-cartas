# Duelo de Cartas Maker — Sosinas Corp

Juego de cartas: crea tus propias cartas, arma mazos y duela contra la IA o con un amigo por internet.
Empaquetado para Android con Capacitor 8.

| Carpeta / archivo | Qué es |
|---|---|
| `docs/index.html` | El juego completo (un solo archivo) |
| `docs/` | También sirve como página web (GitHub Pages: rama `main`, carpeta `/docs`) |
| `native/java/` | Código Android propio (pantalla completa) |
| `native/res/` | Iconos de la app y pantalla de arranque (`scripts/gen_icons.py native/icon.png` los regenera) |
| `app.config.json` | Versión de la app |
| `scripts/prepare-android.mjs` | Ajusta el proyecto Android que crea Capacitor (cámara para el QR, Android 16, iconos) |
| `.github/workflows/android.yml` | Construye la app en GitHub: APK de prueba y AAB para Google Play |

## Cómo se construye
Cada cambio subido a `main` (o **Actions → Construir app Android → Run workflow**) genera:
- En **Releases**: el **APK de prueba** para descargar e instalar directo desde el celular.
- En la pestaña **Actions**: **DueloDeCartas-APK-prueba** y **DueloDeCartas-AAB-GooglePlay**.

## Antes de publicar en Google Play
- `app.config.json` → sube `versionName` en cada versión nueva.
- Secrets del repositorio para firmar el AAB: `UPLOAD_KEYSTORE_B64`, `UPLOAD_KEYSTORE_PASSWORD`, `UPLOAD_KEY_ALIAS`, `UPLOAD_KEY_PASSWORD`.
