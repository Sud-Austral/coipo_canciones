# coipo_canciones — guía para agentes

## Qué es
Cancionero de 22 canciones originales sobre prevención de incendios forestales (Chile), con karaoke sincronizado línea por línea.
Es una **obra con herramientas**, no un sistema de información: sitio estático (HTML autocontenido) más una herramienta Python
de sincronización. Sin backend, base de datos, API, variables de entorno ni autenticación (VERIFICADO en `insumos/01-SOLUCION.md`
y en el código de `dev/` y `sincronizar.py`). Destinatarios y quién lo encargó: ver `insumos/00-PROBLEMA.md`; lo no deducible
está como pendiente de confirmar por el equipo.

## Estructura
- `index.html`, `Cancionero_Karaoke_Pro.html`: **generados, no editar a mano**.
- `dev/plantilla_karaoke.html`, `dev/plantilla_portada.html`: aquí se edita la interfaz.
- `dev/construir_karaoke.py`, `construir_portada.py`, `generar_miniaturas.py`, `medir_desfase.py`, `corregir_marcas.py`.
- `sincronizar.py`: genera marcas desde audio + letra (separación de voz, detección de canto, ASR, afinado).
- `Audios/` (22 MP3), `Imagenes/` (22 PNG), `Miniaturas/` (WebP), `Letras/` (22), `Marcas/` (`.json` y `.lrc` por canción).
- `Cancionero_Karaoke.html` es la **fuente de letras/títulos** (array `SONGS`) que lee `construir_karaoke.py`.
- `METODO_SINCRONIZACION_KARAOKE.md`, `contexto.md`, `INSUMO/ui_ux.md`: documentación y referencia de diseño.

## Comandos (desde la raíz)
```bash
python dev/construir_karaoke.py      # regenera Cancionero_Karaoke_Pro.html
python dev/generar_miniaturas.py     # requiere Pillow
python dev/construir_portada.py      # después del anterior
python sincronizar.py --carpeta-audio Audios --carpeta-letras Letras   # requiere ffmpeg, demucs, faster-whisper, torch
python dev/medir_desfase.py ; python dev/corregir_marcas.py --shift <s>
```
No hay pruebas automáticas ni linter. No ejecuté estos comandos al escribir este archivo: no lo comprobé.

## Convenciones y trampas
- Medios emparejados por nombre normalizado (sin tildes/mayúsculas) entre `Audios`, `Imagenes`, `Marcas` y `Letras`; mantener
  el prefijo numérico `NN_` en `Marcas/`.
- Tras cambiar marcas, letras o medios: reconstruir reproductor, y luego la portada.
- `sincronizar.py` fija `KMP_DUPLICATE_LIB_OK` por un choque de OpenMP en Windows/Anaconda.
- `.sync_tmp/` (WAV intermedios, ~2,7 GB) y `__pycache__/` figuran en `.gitignore` pero **están versionados** (VERIFICADO con
  `git ls-files`): no los edites ni agregues más; retirarlos del índice lo decide una persona.
- `.claude/scheduled_tasks.lock` también está versionado: no lo toques.
- `.github/workflows/readme.yml` llama al generador `Sud-Austral/coipo_aireadme`; no modificarlo.
- Marcas `[PENDIENTE]`/`[VERIFICAR]` en `insumos/`: no las resuelvas tú. Autoría/RUN del PDF: pendiente según `contexto.md`.
- Ante humo o fuego, el número de CONAF que usa la obra es el 130.
