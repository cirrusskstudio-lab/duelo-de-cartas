# Duelo de Cartas Maker (Sosinas Corp) — notas para seguir trabajando

- **El juego es un solo archivo: `docs/index.html`.** Es la versión maestra: se edita aquí y se sube a `main`.
- Cada push a `main` dispara `.github/workflows/android.yml`: genera el APK de prueba (Release `prueba-N`) y el AAB para Google Play (artefacto en Actions). Para cambios que no tocan el juego, usa `[skip ci]` en el mensaje del commit.
- App ID: `com.sosinascorp.duelodecartas` (no cambiarlo: Google Play lo fija para siempre). Versión visible en `app.config.json`.
- Íconos: `native/icon.png` → `python3 scripts/gen_icons.py native/icon.png` regenera `native/res/`.
- El script principal del juego va en `<script type="text/plain" id="appMainScript">` y se ejecuta después de cargar IndexedDB.
- Pruebas (Playwright, Python) en `pruebas/` (ejecútalas desde esa carpeta: algunas importan otras). Abren `file:///home/claude/duelo-de-cartas/docs/index.html`; los de red (`*_net.py`) conectan dos navegadores con `net_helpers.py`. El juego trae además 123 pruebas internas en el Campo de Pruebas (`test_sandbox_auto.py`).
- Multijugador: WebRTC con intercambio manual de códigos/QR; ambos jugadores deben tener la misma versión.
- Mazos de ejemplo importables (Creador → «Importar copia de seguridad» → Aceptar = fusionar) en `mazos/`.
