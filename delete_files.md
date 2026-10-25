# Archivos propuestos para borrar

> Generado por `Sud-Austral/coipo_aireadme`. **Nada se borro.**
> Esta es una lista para revisar; la decision es de una persona.


## Cuanto se recupera

El detector encontro **1** candidatos (47 KB), el **0.3%** de los 337 archivos que el analizador recorre en cada corrida.

De ellos, **0** se proponen para borrar (0 KB) y **1** quedan para revisar.

Esto no es solo orden: cada archivo muerto ocupa presupuesto de contexto y empuja la evidencia real contra el corte de 30.000 caracteres que se envia al modelo.

## Revisar antes de decidir

| Archivo | Tamaño | Por que |
| --- | ---: | --- |
| `__pycache__/sincronizar.cpython-313.pyc` | 47 KB | El revisor no se pronuncio sobre este archivo. El detector lo marco como resto de build o entorno. |


## Lo que este analisis no puede ver

La deteccion de huerfanos es estatica. No ve `importlib`, ni imports
dinamicos, ni rutas construidas en cadenas de texto, ni archivos
referenciados desde HTML, ni datos que se leen por ruta en tiempo de
ejecucion.

Por eso hay una seccion **Revisar**: no es una nota al pie, es la mitad del
informe.
