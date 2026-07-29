#!/usr/bin/env python3
"""
corregir_marcas.py — aplica un corrimiento permanente a las marcas de karaoke.

    python dev/corregir_marcas.py --shift -0.4              # todas las canciones
    python dev/corregir_marcas.py --shift 0.25 --cancion 7  # solo la canción 7

Úsalo cuando, tras calibrar de oído con [ y ] en el reproductor, confirmes un
sesgo constante: el valor de --shift es el mismo desfase que te acomodó en el
player (positivo = las marcas estaban atrasadas y se adelantan... es decir, se
RESTA al tiempo; el signo coincide con el del ajuste del reproductor).

Reescribe Marcas/NN_*.json y regenera el .lrc desde la letra correspondiente.
Después de correrlo: python dev/construir_karaoke.py  (y poner el desfase del
reproductor de vuelta en 0).
"""
import argparse, json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import sincronizar  # leer_letra y a_lrc del propio pipeline


def leer_json(ruta):
    for enc in ('utf-8', 'cp1252'):
        try:
            with open(ruta, encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
    raise SystemExit('no se pudo leer ' + ruta)


def main():
    ap = argparse.ArgumentParser(description='Corrimiento permanente de Marcas/*.json y .lrc')
    ap.add_argument('--shift', type=float,
                    help='segundos; el mismo signo del desfase que te acomodó en el reproductor')
    ap.add_argument('--auto', action='store_true',
                    help='usa dev/_desfases.json (de medir_desfase.py): cada canción con su medida')
    ap.add_argument('--cancion', type=int, help='número 1-22; sin esto, aplica a todas')
    ap.add_argument('--min', type=float, default=0.0, dest='minimo',
                    help='con --auto: ignora sesgos menores a este valor (evita perseguir ruido)')
    a = ap.parse_args()

    if not a.auto and a.shift is None:
        sys.exit('pasa --shift S o --auto')

    os.chdir(RAIZ)
    medidas = None
    if a.auto:
        ruta_med = os.path.join('dev', '_desfases.json')
        if not os.path.exists(ruta_med):
            sys.exit('falta %s: corre primero python dev/medir_desfase.py' % ruta_med)
        medidas = leer_json(ruta_med)

    archivos = sorted(f for f in os.listdir('Marcas') if f.endswith('.json'))
    if a.cancion:
        archivos = [f for f in archivos if f.startswith('%02d_' % a.cancion)]
        if not archivos:
            sys.exit('no hay marcas para la canción %d' % a.cancion)

    for nombre in archivos:
        if medidas:
            # sesgo medido: negativo = marca tarde; el shift equivalente es su opuesto
            info = medidas['canciones'].get(nombre)
            sesgo = info['sesgo'] if info else medidas['global']
            if abs(sesgo) < a.minimo:
                print('%-34s sin cambios (sesgo %+.3f < %.2f)' % (nombre[:34], sesgo, a.minimo))
                continue
            shift = -sesgo
            if not info:
                print('  (%s sin medida propia: se usa la mediana global)' % nombre)
        else:
            shift = a.shift
        # el reproductor SUMA el desfase al tiempo del audio; corregirlo en las
        # marcas equivale a RESTARLO de cada marca
        delta = -shift

        ruta = os.path.join('Marcas', nombre)
        datos = leer_json(ruta)
        dur = datos.get('duracion', 0)
        marcas = [round(max(0.0, t + delta), 2) for t in datos['marcas']]
        # preservar monotonicidad tras el clamp en 0
        for i in range(1, len(marcas)):
            if marcas[i] < marcas[i-1] + 0.05:
                marcas[i] = round(marcas[i-1] + 0.05, 2)
        if dur:
            marcas = [min(t, round(dur - 0.5, 2)) for t in marcas]
        datos['marcas'] = marcas
        datos['origen'] = datos.get('origen', '') + ' +shift(%.2f)' % shift
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)

        letra = os.path.join('Letras', nombre[:-5] + '.txt')
        if os.path.exists(letra):
            lineas, _ = sincronizar.leer_letra(letra)
            if len(lineas) == len(marcas):
                lrc = os.path.join('Marcas', nombre[:-5] + '.lrc')
                with open(lrc, 'w', encoding='utf-8') as f:
                    f.write(sincronizar.a_lrc(marcas, lineas, datos.get('titulo', ''), dur or marcas[-1] + 4))
        print('%-34s %d marcas %+.2f s' % (nombre[:34], len(marcas), delta))

    print('\nlisto. Ahora: python dev/construir_karaoke.py  (y desfase del reproductor a 0)')


if __name__ == '__main__':
    main()
