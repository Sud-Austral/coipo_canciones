#!/usr/bin/env python3
"""
medir_desfase.py — mide objetivamente si las marcas van tarde o temprano.

    python dev/medir_desfase.py

No requiere oído humano: compara cada marca contra el inicio real del canto en
la pista de voz aislada que Demucs dejó cacheada en .sync_tmp/, y reporta el
sesgo sistemático (mediana) por canción y global.

Interpretación del resultado:
  sesgo POSITIVO = las marcas van TARDE (la voz entra antes que la marca)
                   -> corregir con:  dev/corregir_marcas.py --shift <sesgo>
  sesgo NEGATIVO = las marcas van TEMPRANO
"""
import json, os, sys

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import sincronizar

VENTANA = 1.2   # s: hasta dónde buscar el inicio de canto alrededor de una marca
HUECO = 1.5     # s: separación mínima con la marca previa para considerarla inicio de frase


def leer_json(ruta):
    for enc in ('utf-8', 'cp1252'):
        try:
            with open(ruta, encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
    raise SystemExit('no se pudo leer ' + ruta)


def medir(nombre):
    """Devuelve (sesgo, n_muestras) para una canción, o (None, 0)."""
    base = nombre[:-5]
    voz = None
    for raiz, _, archivos in os.walk(os.path.join('.sync_tmp', base)):
        if 'vocals.wav' in archivos:
            voz = os.path.join(raiz, 'vocals.wav')
            break
    if not voz:
        return None, 0

    marcas = leer_json(os.path.join('Marcas', nombre))['marcas']
    frases = sincronizar.detectar_frases(voz)
    if not frases:
        return None, 0
    inicios = np.array([f[0] for f in frases])

    deltas = []
    for i, t in enumerate(marcas):
        # solo marcas que abren frase: la anterior quedó lejos
        if i > 0 and t - marcas[i-1] < HUECO:
            continue
        j = int(np.argmin(np.abs(inicios - t)))
        d = inicios[j] - t          # >0 si la voz entra DESPUÉS de la marca
        if abs(d) <= VENTANA:
            deltas.append(d)

    if len(deltas) < 3:
        return None, len(deltas)
    # el sesgo que hay que aplicar es el opuesto: si la voz entra después,
    # la marca está temprano (sesgo negativo)
    return float(np.median(deltas)), len(deltas)


SALIDA = os.path.join('dev', '_desfases.json')


def main():
    os.chdir(RAIZ)
    archivos = sorted(f for f in os.listdir('Marcas') if f.endswith('.json'))
    print('%-34s %8s %8s' % ('canción', 'sesgo', 'muestras'))
    print('-' * 52)
    todos, medidos = [], {}
    for nombre in archivos:
        sesgo, n = medir(nombre)
        if sesgo is None:
            print('%-34s %8s %8d' % (nombre[:34], 'n/d', n))
            continue
        marca = ' <-- revisar' if abs(sesgo) > 0.25 else ''
        print('%-34s %+8.3f %8d%s' % (nombre[:34], sesgo, n, marca))
        todos.append(sesgo)
        medidos[nombre] = {'sesgo': round(sesgo, 3), 'muestras': n}

    if todos:
        a = np.array(todos)
        g = float(np.median(a))
        print('-' * 52)
        print('mediana global: %+.3f s   (media %+.3f, desv %.3f, n=%d canciones)'
              % (g, a.mean(), a.std(), len(a)))
        with open(SALIDA, 'w', encoding='utf-8') as f:
            json.dump({'global': round(g, 3), 'canciones': medidos}, f,
                      ensure_ascii=False, indent=1)
        print('medidas guardadas en %s' % SALIDA)
        print()
        if abs(g) < 0.08:
            print('Las marcas están alineadas con el canto (sesgo < 0,08 s).')
            print('La sensación de atraso se resuelve con la anticipación del')
            print('reproductor, no moviendo las marcas.')
        else:
            signo = 'TARDE' if g < 0 else 'TEMPRANO'
            print('Las marcas van %s %.2f s en promedio.' % (signo, abs(g)))
            print('Corregir cada canción con su propia medida:')
            print('  python dev/corregir_marcas.py --auto')


if __name__ == '__main__':
    main()
