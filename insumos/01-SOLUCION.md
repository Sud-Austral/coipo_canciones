# Solucion, leida desde el codigo

Este documento es la parte solida del ejercicio: el codigo ES la solucion. Casi
todo lo que sigue tiene cita. Donde no la tiene, lleva marca.

## Que hace el sistema

Reune 22 canciones originales sobre prevencion de incendios forestales y las
entrega listas para cantar en grupo: cada linea de cada letra tiene registrado
el instante exacto en que empieza, de modo que la letra avanza sola mientras
suena el audio. Se abre en un navegador, sin instalar nada y sin conexion
[README.md].

Alrededor de eso hay una segunda cosa, menos visible y mas interesante: una
herramienta que calcula esos instantes automaticamente a partir del audio y de
la letra en texto plano [sincronizar.py], en vez de que alguien los marque a
mano uno por uno. El metodo esta documentado paso a paso, con sus resultados
medidos y sus fracasos [METODO_SINCRONIZACION_KARAOKE.md:8],
[METODO_SINCRONIZACION_KARAOKE.md:197].

## Como sincroniza, que es lo unico algoritmico del repositorio

El proceso tiene cinco etapas encadenadas, todas dentro de un solo archivo:

1. Separar la voz del acompanamiento [sincronizar.py:73]. Sin esto, la
   deteccion de canto confunde instrumentos con voz.
2. Detectar donde hay canto y donde hay silencio [sincronizar.py:94],
   agrupando en frases con un hueco minimo y un largo minimo, ambos
   parametrizables.
3. Localizar las secciones repetidas por auto-similitud [sincronizar.py:136],
   [sincronizar.py:145]. Es lo que permite resolver los coros: se reconoce que
   un tramo ya sono antes en vez de intentar transcribirlo de nuevo.
4. Anclar con reconocimiento de voz [sincronizar.py:188]. La transcripcion
   corre en un subproceso con un interprete de Python configurable, y el codigo
   explica por que: en entornos con librerias en conflicto el reconocedor no
   carga, y aislarlo evita que un fallo ahi mate la corrida entera
   [sincronizar.py:162].
5. Afinar contra el pulso [sincronizar.py:258] y buscar el ataque exacto de cada
   linea [sincronizar.py:278].

La salida es el formato estandar de karaoke [sincronizar.py:292] mas un archivo
de marcas propio. Hay ademas una revision previa del entorno
[sincronizar.py:443] y un modo que procesa una carpeta completa emparejando
audios con letras por nombre normalizado [sincronizar.py:464],
[sincronizar.py:467].

[INFERIDO] La herramienta esta pensada para funcionar en Windows con Anaconda:
hay un ajuste explicito para un choque entre dos runtimes de OpenMP que aborta
la separacion de voz [sincronizar.py:28]. Ese comentario documenta un problema
real que alguien sufrio.

## Roles: quien ve que

No hay roles. No es una omision de este documento: es un hecho verificable del
repositorio. En toda la evidencia no existe ninguna tabla de base de datos,
ningun endpoint, ninguna variable de entorno y ningun mecanismo de
autenticacion o autorizacion. El material es publico y se sirve como archivos
estaticos.

[INFERIDO] La unica separacion real es de intencion, no de permisos: las
herramientas de autor viven aparte en [dev/construir_karaoke.py],
[dev/construir_portada.py], [dev/corregir_marcas.py],
[dev/generar_miniaturas.py], [dev/medir_desfase.py], y nada de eso hace falta
para consumir la obra.

## De donde salen los datos

[INFERIDO] Las letras se escriben a mano en texto plano, en un formato propio
que el metodo documenta [METODO_SINCRONIZACION_KARAOKE.md:132] y del que hay un
ejemplo en el repositorio [letra_ejemplo.txt].

[INFERIDO] Los audios y las imagenes son insumos externos que alguien produjo
fuera de aqui. Quien los grabo, quien ilustro y con que derechos es
[PENDIENTE], y se cruza con la pregunta de titularidad del documento anterior.

[INFERIDO] Las marcas de tiempo las genera [sincronizar.py] y luego pueden
corregirse a mano: hay una herramienta dedicada a eso [dev/corregir_marcas.py] y
otra que mide el desfase resultante [dev/medir_desfase.py] guardando lo medido
[dev/_desfases.json]. El metodo dedica una seccion entera a la verificacion y
correccion manual [METODO_SINCRONIZACION_KARAOKE.md:230], o sea que el resultado
automatico se revisa, no se da por bueno.

[INFERIDO] Las paginas publicadas son generadas, no escritas: hay plantillas
[dev/plantilla_karaoke.html], [dev/plantilla_portada.html] y guiones que las
rellenan [dev/construir_karaoke.py], [dev/construir_portada.py], y el propio
README marca portada y reproductor como generados [README.md]. Editar a mano
[index.html] o [Cancionero_Karaoke_Pro.html] es trabajo que se pierde en la
siguiente generacion.

[INFERIDO] Las miniaturas tambien se generan, desde las imagenes de escenario
[dev/generar_miniaturas.py].

## Que NO hace

Estas ausencias son afirmables porque el analizador busco la categoria completa,
no porque no las haya visto:

- No existe ninguna base de datos. La evidencia no reporta ninguna tabla ni
  ningun archivo de esquema en las 336 rutas analizadas.
- No existe ningun endpoint ni ningun servidor. No hay ninguna ruta HTTP en toda
  la evidencia. La documentacion lo dice como caracteristica buscada, no como
  carencia: funciona sin servidor [README.md].
- No existe ninguna variable de entorno. El analizador no reporta ninguna.
- No existe ningun archivo de licencia. Ninguna de las 336 rutas es LICENSE, y
  el repositorio es publico. Es el hallazgo [VERIFICAR] del documento anterior.
- No hay pruebas automatizadas. Ninguna ruta esta bajo tests/ ni responde al
  patron de archivo de prueba. Para una herramienta con cinco etapas encadenadas
  de procesamiento de senal, es una ausencia con consecuencia: la verificacion
  es manual [METODO_SINCRONIZACION_KARAOKE.md:230].
- No existe ninguna dependencia declarada. No hay requirements.txt ni
  pyproject.toml ni package.json en el arbol, pese a que [sincronizar.py:32]
  importa NumPy y las herramientas de sincronizacion usan reconocimiento de voz
  y separacion de fuentes. Quien clone el repositorio no tiene forma automatica
  de saber que instalar; la instruccion vive en prosa
  [METODO_SINCRONIZACION_KARAOKE.md:116].

## Iteraciones

[INFERIDO] Hubo al menos cuatro versiones del reproductor
[Cancionero_Karaoke.html], [Cancionero_Karaoke_Integrado.html],
[Cancionero_Karaoke_Pro.html], [karaoke_cortafuego.html], y el nombre del
tercero mas la instruccion del README senalan cual es la vigente.

[INFERIDO] Hubo al menos dos versiones del formato de marcas: hay un archivo que
lo declara en su nombre [marcas_v2_script.json].

[INFERIDO] El metodo de sincronizacion se reescribio: la seccion de callejones
sin salida [METODO_SINCRONIZACION_KARAOKE.md:197] es el registro de lo que se
probo y no funciono. Es documentacion poco comun y de mucho valor.

[VERIFICAR] El repositorio conserva 2,7 GB de WAV intermedios contra la regla de
su propio [.gitignore:2], y un compilado de Python contra [.gitignore:9]. Ver
[00-PROBLEMA.md] y el manifiesto.

## Lo que este borrador no pudo describir

- La obra en si. El PDF con las 22 letras
  [Cancionero_de_Prevencion_de_Incendios.pdf] no es texto que el analizador lea:
  no puede decir de que trata cada cancion, a que edad apunta ni que mensaje
  preventivo lleva. Todo el contenido, que es el producto, queda fuera de este
  documento.
- Los audios y las imagenes. Misma razon: son binarios.
- Que hace exactamente el reproductor. Los cuatro HTML son generados y grandes;
  el analizador no reporta su logica. Lo que se sabe de atajos de teclado, modo
  escenario y ajuste de desfase en vivo sale del [README.md] escrito por una
  persona, no del codigo.
- El orden dramaturgico del espectaculo. Existe un archivo que lo declara, pero
  su nombre lleva espacios y no se pudo citar con el formato de este documento.
  Esta en la raiz del repositorio.
- Que aporta [INSUMO/ui_ux.md]. Es el unico insumo previo del repositorio y el
  analizador no reporta su contenido.
