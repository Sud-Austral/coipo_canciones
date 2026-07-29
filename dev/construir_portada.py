#!/usr/bin/env python3
"""
construir_portada.py — genera index.html (portada del sitio) desde el reproductor.

    python dev/construir_portada.py

Toma el array SONGS de Cancionero_Karaoke_Pro.html (títulos, estilos, duración e
imagen ya resueltos) y arma la grilla del repertorio dentro de
dev/plantilla_portada.html, reemplazando el marcador <!--__TARJETAS__-->.
"""
import json, math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MENSAJES = {
    1: 'La prevención se hace todo el año', 2: 'Conductas de riesgo y aviso al 130',
    3: 'Niños guardianes que enseñan en casa', 4: 'Manejo del combustible en la vivienda',
    5: 'Detección temprana y aviso', 6: 'Plan familiar de evacuación',
    7: 'Colillas, vidrios y fogatas', 8: 'Vivienda resistente en la interfaz',
    9: 'Homenaje al personal de extinción', 10: 'Himno de cierre: tarea colectiva',
    11: 'Conducta en días críticos', 12: 'Faenas que producen chispas',
    13: 'Turismo responsable en parques', 14: 'Red vecinal para evacuar a quien lo necesita',
    15: 'Las mascotas también evacúan', 16: 'Informarse por canales oficiales',
    17: 'Los fósforos son de adultos', 18: 'Reconocer el humo y avisar',
    19: 'Conducta en una evacuación', 20: 'Qué favorece y qué detiene al fuego',
    21: 'Los cinco descuidos más frecuentes', 22: 'El bosque y su tiempo de crecimiento',
}


def fmt(ms):
    s = round(ms / 1000)
    return '%d:%02d' % (s // 60, s % 60)


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))


def main():
    os.chdir(RAIZ)
    with open('Cancionero_Karaoke_Pro.html', encoding='utf-8') as f:
        html = f.read()
    i0 = html.index('const SONGS = ') + len('const SONGS = ')
    songs, _ = json.JSONDecoder().raw_decode(html, i0)

    tarjetas = []
    for s in songs:
        # miniatura WebP de 640px (1,7 MB en total contra 53 MB de los PNG);
        # si falta, se cae al PNG original
        mini = 'Miniaturas/' + os.path.splitext(os.path.basename(s['bg']))[0] + '.webp'
        img = mini if os.path.exists(mini) else s['bg']
        tarjetas.append(
            '        <li class="carta">\n'
            '          <a class="carta__link" href="Cancionero_Karaoke_Pro.html?cancion={n}">\n'
            '            <img class="carta__img" src="{img}" alt="" width="640" height="360" loading="lazy" decoding="async">\n'
            '            <span class="carta__num">{n:02d}</span>\n'
            '            <span class="carta__cuerpo">\n'
            '              <span class="carta__titulo">{title}</span>\n'
            '              <span class="carta__meta">{style} · {dur}</span>\n'
            '              <span class="carta__msg">{msg}</span>\n'
            '            </span>\n'
            '          </a>\n'
            '        </li>'.format(
                n=s['n'], img=esc(img), title=esc(s['title']),
                style=esc(s['style']), dur=fmt(s['dur']),
                msg=esc(MENSAJES.get(s['n'], '')),
            ))

    total_min = math.floor(sum(s['dur'] for s in songs) / 60000)
    with open(os.path.join('dev', 'plantilla_portada.html'), encoding='utf-8') as f:
        plantilla = f.read()
    salida = (plantilla
              .replace('<!--__TARJETAS__-->', '\n'.join(tarjetas))
              .replace('__TOTAL_MIN__', str(total_min))
              .replace('__TOTAL_CANCIONES__', str(len(songs))))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(salida)
    print('escrito: index.html (%d canciones, %d min) — %.1f KB'
          % (len(songs), total_min, len(salida) / 1024))


if __name__ == '__main__':
    main()
