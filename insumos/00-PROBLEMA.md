# Problema, reconstruido desde el codigo

## Advertencia sobre la cadena de inferencia

Este documento se escribio hacia atras, desde lo construido. Es la parte mas
debil del ejercicio: el codigo dice que hace el sistema, no que quiso hacer
nadie ni por que. Cada afirmacion lleva su cita o su marca, y ninguna es un
hecho del negocio hasta que alguien del negocio la confirme.

Este repositorio es ademas un caso poco habitual: **no es un sistema de
informacion, es una obra**. Lo que se versiona son 22 canciones, sus letras,
sus imagenes y un reproductor; el unico programa real es la herramienta que
sincroniza letra y audio [sincronizar.py]. Buena parte de lo que un insumo
suele preguntar —tablas, roles, endpoints— aqui no aplica, y decirlo es mas
util que rellenarlo.

## Que problema se estaba resolviendo

[INFERIDO] Habia que educar en prevencion de incendios forestales y el
material disponible no servia, o no existia. El repositorio contiene una obra
completa de 22 canciones originales [Cancionero_de_Prevencion_de_Incendios.pdf]
con su orden dramaturgico para un espectaculo en vivo, y el propio proyecto
declara estar dirigido a establecimientos educacionales y comunidades
[README.md], [contexto.md]. Luego probablemente habia un problema con llegar a
publico escolar y comunitario con el mensaje de prevencion. Es una hipotesis: el
codigo no dice quien lo pidio.

[INFERIDO] El problema no era solo tener las canciones, sino poder cantarlas en
grupo. Todo el esfuerzo tecnico del repositorio esta puesto en una sola cosa:
saber en que instante exacto empieza cada linea de la letra
[METODO_SINCRONIZACION_KARAOKE.md:8]. Eso solo hace falta si alguien va a
seguir la letra mientras suena la musica. Existe ademas un modo pensado para
proyectar sin controles a la vista [README.md], que es una necesidad de sala,
no de escritorio.

[INFERIDO] Habia que poder usarlo donde no hay internet. El reproductor es un
archivo HTML que se abre directamente y funciona sin instalar nada, sin
servidor y sin conexion [README.md], y todos los audios, imagenes y marcas
viajan dentro del propio repositorio. Se toma esa decision cuando se espera
usar el material en lugares con conectividad mala o nula. Que lugares son, y si
esa fue la razon, es [PENDIENTE].

[INFERIDO] Sincronizar la letra a mano era el cuello de botella. La herramienta
automatiza cinco etapas —separar la voz del acompanamiento [sincronizar.py:73],
detectar donde hay canto [sincronizar.py:94], localizar secciones repetidas
[sincronizar.py:145], anclar con reconocimiento de voz [sincronizar.py:188] y
afinar contra el pulso [sincronizar.py:258]— y el metodo documenta que se
probaron caminos que no funcionaron antes de llegar a este
[METODO_SINCRONIZACION_KARAOKE.md:197]. Nadie construye eso para 22 canciones
si marcarlas a mano fuera comodo. Cuanto tardaba hacerlo a mano es [PENDIENTE].

## Quien sufre el problema

[PENDIENTE] No hay roles en este repositorio. No existe autenticacion, ni
permisos, ni usuarios: no hay ninguna tabla, ningun guard y ningun endpoint en
toda la evidencia. El publico declarado son establecimientos educacionales y
comunidades [README.md], pero eso es una declaracion de intencion escrita en la
documentacion, no una estructura del sistema.

[PENDIENTE] Cuantas personas usan el material, en cuantos establecimientos y
con que frecuencia. El repositorio no lo puede saber: no hay analitica, no hay
registro de uso y no hay servidor que pudiera medirlo.

[INFERIDO] Hay al menos dos publicos distintos y el repositorio los distingue.
Uno consume la obra —abre el reproductor [index.html],
[Cancionero_Karaoke_Pro.html]— y otro la produce: hay una carpeta separada de
herramientas de autor [dev/construir_karaoke.py], [dev/construir_portada.py],
[dev/corregir_marcas.py], [dev/generar_miniaturas.py], [dev/medir_desfase.py]
que el publico final nunca ejecuta.

## Como se resolvia antes

[PENDIENTE] El codigo no lo dice. No hay importadores de planilla, ni migracion
desde un sistema anterior, ni rastro de un formato heredado. La obra parece
haber nacido en este repositorio.

[INFERIDO] Hubo al menos tres intentos de reproductor antes del actual: conviven
cuatro archivos de karaoke [Cancionero_Karaoke.html],
[Cancionero_Karaoke_Integrado.html], [Cancionero_Karaoke_Pro.html] y
[karaoke_cortafuego.html], y solo uno de ellos es el que la documentacion manda
usar [README.md]. Los otros tres son iteraciones. Cuales quedaron obsoletos y
cuales siguen en uso es [PENDIENTE], y es una pregunta con consecuencia
practica: hoy los cuatro se publican igual.

## Que pasa si no se hace nada

[PENDIENTE] Sin excepcion. El codigo no responde esto y no se puede deducir de
que el sistema exista.

## Volumen

[INFERIDO] La obra son 22 canciones y esa cifra si es solida: aparece declarada
[README.md], [contexto.md] y coincide con lo que hay en el arbol —22 letras, 22
audios, 22 imagenes de escenario y 22 archivos de marcas. Es un catalogo
cerrado, no un sistema que crece.

[VERIFICAR] El repositorio pesa 2,9 GB en disco y **2,7 GB de eso son 111
archivos WAV** intermedios del proceso de sincronizacion. 101 de ellos estan
bajo una carpeta que el propio [.gitignore:2] declara ignorada, con el
comentario "temporales del pipeline de sincronizacion (WAV intermedios, pesan
cientos de MB)" [.gitignore:1]. La regla no los saca porque se versionaron
antes de escribirla. El efecto es concreto y medible: este repositorio no pudo
analizarse por descarga y hubo que clonarlo aparte. No es un problema de
negocio, es deuda tecnica con costo real, y se corrige sin perder nada del
historial. El bot lo listara en delete_files.md cuando corra.

[INFERIDO] Del mismo tipo, menor: hay un compilado de Python versionado
`__pycache__/sincronizar.cpython-313.pyc` (visto en git ls-files; el analizador no indexa esa carpeta) que [.gitignore:9] tambien declara
ignorado. Misma causa, mismo remedio.

## Quien decide que esta terminado

[PENDIENTE] Sin excepcion. No hay criterio de aceptacion escrito en ninguna
parte del repositorio.

[VERIFICAR] Hay una pregunta juridica que el codigo plantea y no resuelve: son
22 canciones originales y una obra literaria publicada como PDF
[Cancionero_de_Prevencion_de_Incendios.pdf] en un repositorio **publico**, sin
ningun archivo de licencia en todo el arbol. Quien tiene los derechos de letra,
musica, grabacion e imagenes, y bajo que condiciones puede reutilizarlas un
tercero, no esta declarado. Lo cierra Fiscalia.

## Pendientes, y a quien preguntarle cada uno

| Pregunta | A quien |
|---|---|
| Quien encargo la obra y con que proposito | area que impulso el cancionero |
| En cuantos establecimientos se ha usado y con que resultado | area de educacion ambiental / prevencion |
| Cuanto tardaba sincronizar una cancion a mano | quien hizo el trabajo antes de [sincronizar.py] |
| Cual de los cuatro reproductores es el vigente | autor del repositorio |
| Que se hace con los 2,7 GB de WAV intermedios | autor del repositorio |
| Quien es titular de los derechos de las 22 canciones | Fiscalia |
| Bajo que licencia se publica un repositorio publico sin LICENSE | Fiscalia |

## Verificar, y quien los cierra

| Afirmacion | Quien la cierra |
|---|---|
| Titularidad de derechos de obra musical y literaria | Fiscalia |
| Condiciones de reutilizacion por terceros del material publicado | Fiscalia |
| Que hacer con los WAV versionados contra la regla de [.gitignore:2] | autor del repositorio |
