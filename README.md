# Cancionero de Prevención de Incendios

22 canciones originales para educación y sensibilización en **prevención de incendios
forestales** en Chile, con karaoke sincronizado línea por línea. Dirigido a establecimientos
educacionales y comunidades.

## Para usarlo

Abre **`index.html`** (portada) o directamente **`Cancionero_Karaoke_Pro.html`** (reproductor).
Funciona en el navegador sin instalar nada, sin internet y sin servidor.

- **Modo escenario** (solo imagen y letra, controles que se ocultan): botón en la barra,
  `Shift+E`, o `Cancionero_Karaoke_Pro.html?modo=escenario`
- **Abrir una canción concreta**: `Cancionero_Karaoke_Pro.html?cancion=7`
- **Si la letra va corrida** respecto del audio de tu equipo: `[` y `]` la ajustan en vivo
  (±0,1 s) y el ajuste queda guardado por canción.

| Atajo | Acción |
|---|---|
| `Espacio` | Reproducir / pausar |
| `←` `→` | ∓5 segundos |
| `Ctrl` + `←` `→` | Canción anterior / siguiente |
| `[` `]` | Desfase de la letra ∓0,1 s |
| `Shift`+`E` | Modo escenario |
| `Shift`+`F` | Pantalla completa |
| `Esc` | Cerrar lista / ajustes |

## Qué hay en el repositorio

| Ruta | Qué es |
|---|---|
| `index.html` | Portada del sitio *(generada)* |
| `Cancionero_Karaoke_Pro.html` | Reproductor de karaoke *(generado)* |
| `Audios/` | 22 MP3 |
| `Imagenes/` | 22 PNG 1536×864 (fondo de escenario) |
| `Miniaturas/` | WebP 640px para la grilla de la portada *(generadas)* |
| `Letras/` | 22 letras en el formato de `sincronizar.py` |
| `Marcas/` | Tiempos por línea (`.json`) y karaoke estándar (`.lrc`) |
| `Cancionero_de_Prevencion_de_Incendios.pdf` | Obra literaria: las 22 letras |
| `Orden Cancionero.txt` | Orden dramatúrgico para un espectáculo en vivo |
| `METODO_SINCRONIZACION_KARAOKE.md` | El método de sincronización, documentado |
| `sincronizar.py` | Herramienta que genera las marcas desde audio + letra |
| `dev/` | Plantillas y scripts de construcción |

**Los HTML de la raíz son generados: no editarlos a mano.** La UI del reproductor se edita en
`dev/plantilla_karaoke.html` y la portada en `dev/plantilla_portada.html`.

## Regenerar

```bash
python dev/construir_karaoke.py      # reproductor (letras + marcas + medios)
python dev/generar_miniaturas.py     # miniaturas WebP (requiere Pillow)
python dev/construir_portada.py      # portada (lee el reproductor ya construido)
```

## Sincronizar una canción nueva

```bash
# entorno: ffmpeg en el PATH, y  pip install demucs faster-whisper torch torchaudio
python sincronizar.py --carpeta-audio Audios --carpeta-letras Letras
```

Procesa la carpeta completa con barra de progreso, salta lo ya hecho (`--forzar` para rehacer) y
avisa si una canción quedó bajo 90% de validación. Detalle del método y los callejones sin salida
ya descartados: `METODO_SINCRONIZACION_KARAOKE.md`.

Herramientas de ajuste:

```bash
python dev/medir_desfase.py                    # mide el sesgo marcas-vs-canto (sin oído)
python dev/corregir_marcas.py --shift -0.4     # lo corrige permanentemente
```

## Emergencia forestal

Ante humo o fuego en el bosque, el número de CONAF es el **130**.
