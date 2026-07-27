# Contexto del proyecto — Cancionero de Prevención de Incendios

> Documento generado automáticamente a partir del contenido de la carpeta.
> Creado 25-07-2026 · Actualizado 25-07-2026 (incorpora la línea de sincronización karaoke).
> Sirve como punto de partida para futuras sesiones de trabajo.

## 1. Qué es este proyecto

Colección de **22 canciones originales** para educación y sensibilización en **prevención de incendios forestales** en Chile, dirigida a establecimientos educacionales y comunidades. Cada canción tiene letra propia, un estilo musical distinto, un mensaje preventivo específico y un público objetivo definido.

El proyecto existe hoy en dos líneas de trabajo paralelas:

**A. El cancionero como obra y como espectáculo**

| Capa | Archivo / carpeta | Estado |
|---|---|---|
| Obra literaria (registro de propiedad intelectual) | `Cancionero_de_Prevencion_de_Incendios.pdf` | 49 págs., **falta completar autor y RUN** |
| Audio producido (aparentemente con SUNO) | `Audios/` — 22 MP3 | Completo |
| Arte visual por canción | `Imagenes/` — 22 PNG (1536×864) | Completo |
| Reproductor karaoke de presentación | `Cancionero_Karaoke.html` | Funcional, 1 archivo autocontenido |
| Guion de espectáculo | `Orden Cancionero.txt` | 6 actos, orden dramatúrgico distinto al del PDF |

**B. La sincronización automática letra–audio** (ver §6)

| Pieza | Archivo | Estado |
|---|---|---|
| Método documentado | `METODO_SINCRONIZACION_KARAOKE.md` | Completo, con caso real medido |
| Herramienta | `sincronizar.py` | Funcional (CPU, requiere instalación pesada) |
| App de verificación y corrección | `karaoke_cortafuego.html` | Funcional |
| Formato de letra de referencia | `letra_ejemplo.txt` | Canción 1, 58 líneas / 9 secciones |
| Salida de ejemplo | `marcas_v2_script.json` | 58 marcas, canción 1 |

Duración total del repertorio: **83 min 46 s**.

## 2. Inventario de canciones

Numeración según el PDF y el HTML (el orden de espectáculo es otro, ver §4).

| # | Título | Estilo | Mensaje | Público |
|---|---|---|---|---|
| 1 | El Fuego se Apaga en Invierno | Cumbia | La prevención se realiza todo el año | General / comunidades |
| 2 | No Juegues con Fuego | Pop urbano | Conductas de riesgo juvenil y aviso al 130 | Enseñanza media |
| 3 | La Patrulla del Bosque | Rock infantil | Niños como guardianes que enseñan en casa | Enseñanza básica |
| 4 | Limpia tu Terreno | Ranchera norteña | Manejo del combustible en torno a la vivienda | Comunidades |
| 5 | Llama al 130 | Rock and roll | Detección temprana y aviso | General |
| 6 | La Ruta de Escape | Merengue | Plan familiar de evacuación | Familias |
| 7 | Chao Chao Colilla | Funk disco | Causas evitables: colillas, vidrios, fogatas | General |
| 8 | Mi Casa Preparada | Axé | Vivienda resistente en interfaz urbano-forestal | Comunidades de interfaz |
| 9 | El Brigadista | Rock de estadio | Homenaje al personal de extinción | General |
| 10 | Todos Somos Prevención | Gospel pop | Himno de cierre, tarea colectiva | Cierre de eventos |
| 11 | Alerta Roja | Salsa | Conducta en días críticos (calor, viento, sequedad) | General |
| 12 | Chispa Traicionera | Ska | Faenas que producen chispas (soldadura, esmeril) | Trabajadores |
| 13 | Parque Querido | Andino (saya) | Turismo responsable en áreas protegidas | Visitantes |
| 14 | Cuenta Conmigo, Vecino | Vallenato | Red comunitaria para evacuar a personas mayores | Comunidades |
| 15 | Mi Mascota También | Bachata | Incluir mascotas en el plan de evacuación | Familias |
| 16 | Fuente Oficial | Electro pop | Canales oficiales, no viralizar rumores | General |
| 17 | Los Fósforos No Se Tocan | Pop infantil | Fósforos y encendedores son de adultos | Párvulos |
| 18 | Humito Gris | Reggae infantil | Reconocer el humo y avisar a un adulto | Párvulos |
| 19 | De la Mano | Marcha infantil | Conducta en evacuación, valor del simulacro | Párvulos |
| 20 | Señor Fuego | Rock humorístico con personajes | Factores que favorecen y detienen al fuego | General |
| 21 | El Ranking del Descuido | Rock humorístico tipo ranking TV | Los cinco descuidos más frecuentes | General |
| 22 | Déjame Llegar a Viejo | Balada tierna con humor | Valor del bosque y su tiempo de crecimiento | Todas las edades |

Estructura de letras: bloques marcados con etiquetas tipo `[Intro]`, `[Verso 1]`, `[Coro]`, `[Puente]`, `[Outro]` (8 a 13 secciones por canción).

## 3. Archivos y su relación

### `Cancionero_de_Prevencion_de_Incendios.pdf`
Obra literaria en 49 páginas: portada, índice de las 22 obras, nota introductoria y las letras completas con encabezado de estilo/mensaje/público. Generado con ReportLab el 19-07-2026.

**Pendiente:** portada y metadatos contienen los marcadores `[NOMBRE COMPLETO DEL AUTOR]` y `[RUN DEL AUTOR]` sin reemplazar. El campo `/Author` del PDF también dice `[Nombre completo del autor]`. Hay que completarlos antes de cualquier trámite de registro.

### `Audios/` — 22 MP3
Nombres coincidentes con los títulos (con tres variantes menores: `El Señor Fuego.mp3`, `De la mano.mp3`, `Déjame llegar a viejo.mp3`). Todas las canciones tienen su audio. Ninguna huérfana.

### `Imagenes/` — 22 PNG
Todas 1536×864 (16:9), una por canción. La de la canción 20 se llama `Entrevista al Señor Fuego.png` — es la única cuyo nombre no calza literalmente con el título, lo que **impide el emparejamiento automático en el reproductor** (ver §5).

### `Cancionero_Karaoke.html`
Reproductor de karaoke autocontenido (78 KB, sin dependencias externas). Funciona abriéndolo en el navegador, sin servidor ni internet. Contiene:

- Las 22 letras embebidas en un array `SONGS` (`n`, `title`, `style`, `dur`, `lyrics`).
- 22 temas visuales (`THEMES`): gradiente de fondo + efecto de partículas por canción (`rain`, `note`, `leaf`, `confetti`, `sparkle`, `beam`, `rise`, `snow`, `firefly`, `heart`, `cloud`, `pixel`).
- **Carga de medios por drag & drop** o selector de archivos. Los MP3, imágenes y videos se emparejan con cada canción por número inicial en el nombre (`01 …`) o por coincidencia del título normalizado. Los archivos nunca se suben: se usan como `blob:` locales.
- **Modo ensayo** ("Continuar sin archivos"): cronómetro interno que avanza la letra sin audio.
- **Modo sincronización**: se marca con `Enter` el tiempo de cada línea; los tiempos se guardan en `localStorage` bajo la clave `cancionero_times` y se exportan/importan como JSON.
- **Ajuste de offset** de letra ±10 s en pasos de 0,5 s.
- Atajos: `Espacio` play/pausa, `Ctrl+→` siguiente, `Ctrl+←` anterior, `Enter` marcar línea en sincronización, `Esc` cancelar sincronización, botón de pantalla completa.

### `Orden Cancionero.txt`
Guion de espectáculo en vivo: 6 actos con justificación dramatúrgica de cada transición (energía, público objetivo, arco emocional).

### Archivos de la línea de sincronización
Ver §6 para el detalle del método. Son cinco piezas que funcionan juntas: `METODO_SINCRONIZACION_KARAOKE.md` (el método), `sincronizar.py` (la herramienta), `karaoke_cortafuego.html` (verificación y corrección manual), `letra_ejemplo.txt` (formato de entrada) y `marcas_v2_script.json` (salida de ejemplo).

## 4. Dos ordenamientos distintos

El orden del PDF/HTML **no es** el orden del espectáculo. Equivalencias:

| Acto | Posición en show | Canción | # en PDF/HTML |
|---|---|---|---|
| 1 — La apertura | 1 | El Fuego se Apaga en Invierno | 1 |
| | 2 | Señor Fuego | 20 |
| | 3 | Limpia tu Terreno | 4 |
| 2 — Preparar casa y barrio | 4 | Mi Casa Preparada | 8 |
| | 5 | Cuenta Conmigo, Vecino | 14 |
| | 6 | La Ruta de Escape | 6 |
| | 7 | Mi Mascota También | 15 |
| 3 — Evitar las causas | 8 | No Juegues con Fuego | 2 |
| | 9 | Chao Chao Colilla | 7 |
| | 10 | Chispa Traicionera | 12 |
| | 11 | Alerta Roja | 11 |
| | 12 | Parque Querido | 13 |
| 4 — Detectar y responder | 13 | Llama al 130 | 5 |
| | 14 | Fuente Oficial | 16 |
| | 15 | El Ranking del Descuido | 21 |
| 5 — Bloque de los pequeños | 16 | La Patrulla del Bosque | 3 |
| | 17 | Los Fósforos No Se Tocan | 17 |
| | 18 | Humito Gris | 18 |
| | 19 | De la Mano | 19 |
| 6 — Cierre emocional | 20 | El Brigadista | 9 |
| | 21 | Déjame Llegar a Viejo | 22 |
| | 22 | Todos Somos Prevención | 10 |

## 5. Puntos pendientes detectados

1. **Autoría sin completar en el PDF** — placeholders `[NOMBRE COMPLETO DEL AUTOR]` y `[RUN DEL AUTOR]` en portada y metadatos.
2. **Duraciones desajustadas en el HTML** — el campo `dur` de 8 canciones no coincide con el MP3 real. Esto descuadra el avance automático de la letra en modo ensayo y la barra de progreso:

   | # | Canción | `dur` en HTML | MP3 real | Diferencia |
   |---|---|---|---|---|
   | 10 | Todos Somos Prevención | 271 | 314 | +43 s |
   | 13 | Parque Querido | 237 | 300 | +63 s |
   | 14 | Cuenta Conmigo, Vecino | 262 | 344 | +82 s |
   | 15 | Mi Mascota También | 252 | 215 | −37 s |
   | 18 | Humito Gris | 164 | 178 | +14 s |
   | 20 | Señor Fuego | 217 | 254 | +37 s |
   | 21 | El Ranking del Descuido | 224 | 252 | +28 s |
   | 11 | Alerta Roja | 210 | 215 | +5 s |

3. **`Entrevista al Señor Fuego.png` no se empareja solo** — al arrastrarla al reproductor no se asigna a la canción 20. Se resuelve renombrándola `Señor Fuego.png` o anteponiendo el número (`20 Señor Fuego.png`).
4. **Sin tiempos de karaoke en el reproductor de presentación** — ninguna canción trae el array `times` en `Cancionero_Karaoke.html`; la letra avanza por interpolación proporcional. Ya existen marcas reales para la canción 1 (`marcas_v2_script.json`), pero en el formato de Cortafuego: falta el puente entre ambos formatos (ver §6).
5. **21 canciones sin sincronizar** — el método está probado sobre una sola.
6. **Renombrado por número recomendado** — prefijar audios e imágenes con `01`–`22` haría la carga al reproductor inmediata y a prueba de tildes.

## 6. Línea de sincronización karaoke

Trabajo desarrollado en paralelo al cancionero: dado un audio y su letra, obtener el tiempo exacto de entrada de cada línea. Documentado en detalle en `METODO_SINCRONIZACION_KARAOKE.md`.

### La idea

No se trata como problema de transcripción. La letra ya se conoce; lo desconocido son los tiempos, y esos salen de dos señales que no requieren entender ninguna palabra: **energía de la voz aislada** (cuándo se canta) y **auto-similitud espectral** (dónde se repite un tramo musical). Un coro que aparece tres veces se mide una vez y se localiza las otras dos comparando espectrogramas.

Cinco pasos: separación de voz con Demucs (`htdemucs`) → detección de actividad vocal por RMS → localización de secciones repetidas por auto-similitud → anclaje opcional con faster-whisper (`base`) y consenso entre pasadas → afinado con grilla de pulso y retroceso al ataque.

### Resultado medido sobre la canción 1

| Enfoque | Líneas resueltas de 58 |
|---|---|
| Sólo reconocimiento de voz sobre la mezcla | 30 |
| Con separación de voz y consenso | 34 |
| **Método completo** | **58** |

El Coro 2 era un hueco de 45 s sin un solo dato de reconocimiento de voz; la auto-similitud lo resolvió con 0,93 de calce. Tempo medido: 96,2 BPM.

### Uso

```bash
pip install faster-whisper demucs
pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio   # + ffmpeg en el sistema

python3 sincronizar.py cancion.mp3 letra.txt            # completo
python3 sincronizar.py cancion.mp3 letra.txt --rapido    # sin reconocimiento de voz
```

Entrada: una línea cantada por línea de archivo, secciones entre corchetes. **Nombrar bien las secciones importa**: dos bloques `[Coro]` con igual número de líneas se tratan como repeticiones. Salidas: `marcas.json` (para Cortafuego) y `.lrc` (estándar de karaoke).

Instalación >1 GB por PyTorch. Corre en CPU local: varios minutos por canción en equipos modestos. Conviene probar con `--rapido` sobre una canción corta.

### `karaoke_cortafuego.html` — app de verificación

Cuatro pestañas: **Sincronizar** (marcar con barra espaciadora), **Ajustar** (corrección fila por fila, `▶` reproduce desde 1 s antes de cada marca), **Karaoke** (proyección, pantalla completa) y **Exportar** (`.json` / `.lrc`). Trae la canción 1 embebida como demo. **No persiste nada al cerrarse** — hay que descargar el `.json` corregido.

Tabla de diagnóstico rápido:

| Síntoma | Causa probable | Corrección |
|---|---|---|
| Tramo entero corrido parejo | Ancla de sección desplazada | *Correr todo ±0,20 s* |
| Una línea suelta desfasada | Ruido en esa entrada | `±0,1` en esa fila |
| Línea congelada | Marca faltante o tardía | Marcar a mano con barra espaciadora |
| Bloque comprimido | Deriva del patrón transferido | Re-marcar la primera línea del bloque |

### Regla del método

Ninguna salida automática se da por buena sin escucharla completa. Que las 58 líneas tengan un número no significa que las 58 estén bien.

### Callejones sin salida ya documentados

No repetir: Whisper `small` sobre música (entra en bucle degenerado; `base` es mejor), Demucs `mdx_extra_q` (requiere `diffq`), `clip_timestamps` de faster-whisper (devuelve tiempos relativos al recorte), `dynaudnorm` sobre voz aislada (amplifica artefactos), transferir patrones sin re-anclar después (deriva acumulada), filtro de consenso demasiado estricto (elimina coros completos).

### Estado actual

Sólo la canción 1 está sincronizada (`marcas_v2_script.json`, 58 marcas, 175,96 s). Faltan las otras 21. El método sugiere organizar en `canciones/<nombre>/` con `audio.mp3` + `letra.txt` y las salidas dentro de cada subcarpeta; hoy la carpeta está plana.

### Dos reproductores, dos propósitos

`Cancionero_Karaoke.html` es el de **presentación**: las 22 canciones, temas visuales, fondos, para el show. `karaoke_cortafuego.html` es el de **producción**: una canción a la vez, para marcar y corregir tiempos. Ambos exportan/importan tiempos en JSON, pero **con formatos distintos** — Cortafuego usa `{v, titulo, duracion, marcas[], origen}` y el reproductor de presentación usa un objeto indexado por número de canción (`{1: [...], 2: [...]}`). Hay que convertir entre ambos para que las marcas producidas con el método lleguen al show.

## 7. Convenciones útiles

- Idioma: español de Chile, registro cercano y coloquial; el 130 (CONAF) es el número de emergencia recurrente.
- Etiquetas de sección entre corchetes dentro de las letras; el reproductor las usa para dividir bloques.
- Paleta del reproductor: verde bosque, naranja `#F59E0B`, crema `#F7F3E8`.
- Imágenes en 16:9 pensadas como fondo de escenario/proyección.
