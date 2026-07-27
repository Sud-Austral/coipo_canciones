# Sincronización automática de letra y audio para karaoke

Método, herramienta y notas de operación.
Documento de referencia para carpeta de trabajo en Claude Cowork.

---

## 1. Qué resuelve

Dado un archivo de audio y la letra de la canción en texto, produce los tiempos
exactos en que entra cada línea. Salida en dos formatos:

- `marcas.json` — para revisar y corregir en la app Cortafuego
- `cancion.lrc` — formato estándar de karaoke (VLC, foobar2000, Winamp)

No sirve para: separar sílabas dentro de una línea (karaoke palabra por palabra),
ni para canciones sin letra conocida previamente.

---

## 2. La idea central

> **No preguntar *qué* se canta. Preguntar *cuándo* se canta y *dónde se repite la música*.**

El error natural es tratar esto como un problema de reconocimiento de voz: transcribir
la canción y calzar la transcripción con la letra. Ese camino funciona a medias y se
derrumba justo donde el arreglo musical se pone denso.

La letra ya se conoce. Lo único desconocido son los tiempos. Y los tiempos se pueden
obtener de dos señales que no requieren entender ni una palabra:

1. **Energía de la voz aislada** — dice cuándo hay alguien cantando
2. **Auto-similitud espectral** — dice dónde se repite un tramo musical

Un coro que se repite tres veces con la misma letra sólo necesita medirse **una vez**.
Las otras dos se localizan comparando espectrogramas y se les copia el patrón interno.

---

## 3. El método, en orden de importancia real

### Paso 1 — Separar la voz del acompañamiento

Herramienta: **Demucs** (modelo `htdemucs`).

Divide la pista en voz e instrumental. Todo lo que viene después funciona mejor sobre
una pista de voz limpia. Es el paso más lento pero el más habilitante.

```bash
python3 -m demucs -n htdemucs --two-stems=vocals -d cpu --segment 7 -j 1 -o sep cancion.mp3
```

`--segment 7` limita el uso de memoria. En un núcleo de CPU, una canción de tres
minutos toma alrededor de un minuto.

### Paso 2 — Detectar actividad vocal

Envolvente de energía RMS sobre la pista de voz, en ventanas de 40 ms cada 10 ms,
convertida a decibeles y suavizada. Umbral adaptativo situado al 30% entre el piso
(percentil 20) y el techo (percentil 97) de la señal.

Después se limpia: se cierran huecos menores a 0,28 s (respiraciones dentro de una
misma frase) y se descartan segmentos menores a 0,22 s (destellos, artefactos de la
separación).

Resultado: la lista de frases cantadas, con inicio y fin. **Esta señal funciona incluso
donde el reconocimiento de voz falla por completo.**

### Paso 3 — Localizar las secciones repetidas

Se calcula un espectrograma reducido a 40 bandas logarítmicas entre 60 Hz y 6 kHz,
normalizando cada trama. Se toma como plantilla un tramo ya medido y se desliza sobre
toda la canción calculando el producto punto.

Se usa la **mezcla completa**, no la voz aislada: el arreglo instrumental también se
repite y aporta señal.

Los picos de similitud marcan dónde vuelve a aparecer esa sección. Con el inicio
localizado, se transfiere el patrón de tiempos internos del tramo original.

Un calce sobre 0,85 es confiable. Bajo 0,6 no sirve.

### Paso 4 — Anclar con reconocimiento de voz

Herramienta: **faster-whisper**, modelo `base`, con marcas de tiempo por palabra.

Se transcribe varias veces (voz aislada y mezcla, con y sin sesgo de vocabulario) y
cada transcripción se alinea contra la letra real mediante **Needleman-Wunsch en banda
diagonal**, con similitud de cadenas como puntaje de calce. Sólo se conservan los
tiempos confirmados por **dos o más pasadas dentro de ±0,6 s**.

La concordancia entre pasadas independientes es la mejor señal disponible de que un
dato es real y no una alucinación del modelo.

> **Este paso es el más lento y el menos decisivo.** Es prescindible: con `--rapido`
> se omite entero y la estructura musical hace el trabajo.

### Paso 5 — Afinar

**Grilla de pulso.** Se detecta el tempo por autocorrelación del flujo espectral
(energía que aparece de golpe, o sea la percusión). Se busca la fase que maximiza la
energía sobre los pulsos. Se arma una grilla con pulsos y contratiempos, porque en
cumbia la voz suele entrar a contratiempo.

Cada marca se cuadra a la grilla **sólo si la corrección es menor a 0,12 s**. Forzar
todo a la grilla mueve marcas correctas a posiciones equivocadas.

**Retroceso al ataque.** El umbral de energía marca la entrada cuando el sonido *ya
subió*, no cuando empezó a subir. Se retrocede hasta el último punto bajo el 15% del
pico local, con tope de 0,40 s.

---

## 4. Uso

### Instalación

```bash
pip install faster-whisper demucs
pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
# ffmpeg debe estar disponible en el sistema
```

### Ejecución

```bash
python3 sincronizar.py cancion.mp3 letra.txt
python3 sincronizar.py cancion.mp3 letra.txt --rapido      # sin reconocimiento de voz
python3 sincronizar.py cancion.mp3 letra.txt --salida otro_nombre.json
```

### Formato de `letra.txt`

Texto plano, una línea de la canción por línea del archivo. Las secciones van entre
corchetes y no se sincronizan, sólo agrupan:

```text
[Intro]
primera línea cantada
segunda línea cantada
[Verso 1]
...
[Coro]
...
```

**Las secciones importan.** El método agrupa por nombre de sección para detectar
repeticiones: dos bloques llamados `[Coro]` con la misma cantidad de líneas se tratan
como repeticiones entre sí. Nombrarlas bien mejora el resultado directamente.

Las líneas de respuesta del coro cuentan como líneas propias y se marcan por separado.

---

## 5. Ejemplo trabajado

**Canción:** *El Fuego se Apaga en Invierno* — cumbia institucional sobre prevención
de incendios forestales. Duración 2:56 (176 s), 58 líneas en 9 secciones, con tres
apariciones del coro y tres versos de igual métrica.

### Resultados por etapa

| Enfoque | Líneas resueltas | Observación |
|---|---|---|
| Sólo reconocimiento de voz sobre la mezcla | 30 / 58 | Coro 2 y outro en blanco |
| Con separación de voz y consenso | 34 / 58 | Ganó el outro, siguió sin el Coro 2 |
| **Método completo** | **58 / 58** | 100% sobre canto detectado |

### Localización por auto-similitud

Plantilla: Coro 1, tramo 42,9–58,8 s.

| Tramo | Similitud | Detectado en | Reconocimiento de voz decía | Diferencia |
|---|---|---|---|---|
| Coro 2 | 0,93 | 82,75 s | *nada* | — |
| Coro final | 0,89 | 142,56 s | 142,3 s | 0,26 s |
| Verso 3 | 0,81 | 122,88 s | 122,6 s | 0,28 s |
| Verso 2 | 0,81 | 63,07 s | 62,5 s | 0,57 s |

El Coro 2 era un hueco de 45 segundos donde el reconocimiento de voz no entregó un
solo dato utilizable. La auto-similitud lo resolvió con 93% de calce.

Las tres coincidencias con el reconocimiento de voz —métodos completamente
independientes, diferencias bajo 0,6 s— son la validación cruzada del método.

### Otros datos medidos

- Tempo: **96,2 BPM** (periodo 0,624 s), típico de cumbia
- Ritmo de canto: 0,37 s por palabra
- Patrón interno del coro: 0 / 2,58 / 4,98 / 7,62 / 9,96 / 12,24 / 14,64 / 17,04 s
- Patrón interno del verso: 0 / 2,24 / 4,74 / 7,42 / 10,44 / 12,88 / 14,94 / 17,40 s
- 35 frases vocales detectadas para 58 líneas: varias líneas se cantan seguidas sin
  pausa audible entre ellas

---

## 6. Callejones sin salida documentados

Errores reales cometidos durante el desarrollo. No repetirlos.

**Modelo `small` de Whisper sobre música.** Entra en bucle degenerado y repite una
sílaba durante toda la canción. El modelo `base` da resultados claramente mejores
sobre audio con acompañamiento. Más grande no es mejor acá.

**Modelo `mdx_extra_q` de Demucs.** Requiere el paquete `diffq`, que no viene por
defecto. Usar `htdemucs` directamente.

**Parámetro `clip_timestamps` de faster-whisper.** Devuelve tiempos relativos al
recorte, no absolutos. Si se necesita procesar por tramos, cortar el audio con ffmpeg
en archivos reales y sumar el desfase a mano.

**Normalización `dynaudnorm` sobre la voz aislada.** Amplifica los artefactos de la
separación en los pasajes silenciosos y empeora la transcripción. Usar la voz cruda.

**Transferir patrones sin ajuste posterior.** Copiar el patrón del Coro 1 a los demás
coros sin pegar después a las entradas de voz detectadas produce deriva acumulada:
en la prueba, el Verso 3 terminó montado sobre el Coro final y el outro comprimido en
0,4 segundos.

**Filtro de consenso demasiado estricto.** Exigir concordancia de dos pasadas y además
monotonía estricta eliminó los dos coros centrales completos. Conviene aplicar el
filtro de consenso y la limpieza de monotonía como etapas separadas, conservando lo
que se pueda de cada una.

**Confiar en la precisión aparente.** Que las 58 líneas tengan un número no significa
que las 58 estén bien. Siempre queda verificación por oído.

---

## 7. Verificación y corrección manual

Ninguna salida automática se da por buena sin escucharla. La app **Cortafuego**
(`karaoke_cortafuego.html`) existe para eso:

1. Abrir la app, cargar el audio
2. Pestaña **Exportar → Abrir proyecto .json**, cargar `marcas.json`
3. Pestaña **Karaoke**, reproducir y escuchar completo

Qué observar y cómo corregir:

| Síntoma | Causa probable | Corrección |
|---|---|---|
| Un tramo entero va corrido parejo | Ancla de sección desplazada | *Correr todo ±0,20 s* |
| Una línea suelta desfasada | Ruido en esa entrada | `±0,1` en esa fila, en *Ajustar* |
| La línea se queda congelada | Marca faltante o muy tardía | Marcar a mano con barra espaciadora |
| Todo el bloque comprimido | Deriva del patrón transferido | Re-marcar la primera línea del bloque |

En *Ajustar*, el botón `▶` de cada fila reproduce desde un segundo antes de su marca,
que es la forma más rápida de auditar una entrada puntual.

Guardar el `.json` corregido al terminar: la app no persiste nada al cerrarse.

---

## 8. Notas para Claude Cowork

Cowork puede ejecutar este método directamente: tiene entorno propio donde instala
paquetes y corre scripts, sobre las carpetas que se le autoricen explícitamente.

### Organización sugerida de la carpeta

```text
karaoke/
├── METODO_SINCRONIZACION_KARAOKE.md   ← este documento
├── sincronizar.py                      ← la herramienta
├── karaoke_cortafuego.html             ← app de verificación
├── letra_ejemplo.txt                   ← formato de referencia
└── canciones/
    └── <nombre_cancion>/
        ├── audio.mp3
        ├── letra.txt
        └── (salidas: marcas.json, marcas.lrc)
```

### Instrucciones de carpeta sugeridas

> Esta carpeta sincroniza letras con audio para karaoke. El método está en
> `METODO_SINCRONIZACION_KARAOKE.md` y la herramienta es `sincronizar.py`.
> Para cada canción nueva: crear subcarpeta en `canciones/`, dejar el audio y la
> letra en el formato del ejemplo, ejecutar el script y reportar el porcentaje de
> validación. Si baja del 90%, revisar qué sección falló antes de entregar.
> Nunca dar por buena una sincronización sin advertir que requiere verificación
> por oído.

### Advertencias operativas

**Instalación pesada.** PyTorch más Demucs superan el gigabyte. La primera ejecución
descarga además el modelo de separación (unos 50 MB) y el de reconocimiento.

**Corre en el procesador local.** La separación de voz usa la CPU de la máquina, no la
nube. En equipos modestos son varios minutos por canción. Conviene empezar con
`--rapido` sobre una canción corta para verificar que el entorno quedó bien.

**Cowork está en fase de investigación.** Si se corta la conexión a mitad de tarea, la
máquina local sigue corriendo pero el hilo de razonamiento se pierde. No depender de
esto para algo con plazo encima.

---

## 9. Extensiones posibles

Ideas no implementadas, en orden de relación esfuerzo/beneficio:

**Karaoke palabra por palabra.** Con las marcas de línea ya fijas, repartir las
palabras dentro de cada línea proporcionalmente a sus sílabas da un resultado
aceptable sin análisis adicional.

**Detección automática de secciones.** Actualmente las secciones se leen de los
corchetes del archivo de letra. Podrían inferirse de la auto-similitud, construyendo
la matriz completa en vez de comparar contra plantillas puntuales.

**Uso de GPU.** Con GPU disponible, el modelo `large` de Whisper sobre voz aislada
probablemente resolvería los tramos densos sin necesidad del paso de auto-similitud.
Habría que verificar si conviene: la auto-similitud es más rápida y más robusta.

**Generación de video.** Con el `.lrc` y la pista instrumental que Demucs ya produce
como subproducto (`no_vocals.wav`), se puede armar un video de karaoke completo con
ffmpeg.

---

*Documento generado a partir del desarrollo y depuración del método sobre un caso
real. Las cifras del ejemplo son medidas, no estimadas.*
