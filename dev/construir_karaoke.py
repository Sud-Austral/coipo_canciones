#!/usr/bin/env python3
"""
construir_karaoke.py — regenera Cancionero_Karaoke_Pro.html desde sus fuentes.

    python dev/construir_karaoke.py

Fuentes (todas en el repo):
  - Cancionero_Karaoke.html      letras, títulos y estilos (array SONGS original)
  - Marcas/NN_*.json             tiempos por línea y duración real de cada canción
  - Audios/*.mp3, Imagenes/*.png medios, emparejados por nombre normalizado
  - dev/plantilla_karaoke.html   la plantilla del reproductor (aquí se edita la UI)

Salida: Cancionero_Karaoke_Pro.html en la raíz (no editarlo a mano).
"""
import json, os, re, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return ' '.join(re.sub(r'[^a-z0-9ñ ]', ' ', s).split())


def buscar(mapa, clave):
    v = mapa.get(clave)
    if v:
        return v
    cand = list(dict.fromkeys(f for k, f in mapa.items() if clave and (clave in k or k in clave)))
    return cand[0] if len(cand) == 1 else None


def leer_json(ruta):
    for enc in ('utf-8', 'cp1252'):
        try:
            with open(ruta, encoding=enc) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
    raise SystemExit('no se pudo leer ' + ruta)


def contar_lineas(lyrics):
    n = 0
    for bloque in lyrics.split('\n\n'):
        for i, linea in enumerate(bloque.split('\n')):
            t = linea.strip()
            if i == 0 and t.startswith('[') and t.endswith(']'):
                continue
            if t:
                n += 1
    return n


# la imagen de la canción 20 no calza con el título por nombre
IMG_ESPECIAL = {20: 'Entrevista al Señor Fuego.png'}

SLUGS = {
    1: 'El_Fuego_se_Apaga_en_Invierno', 2: 'No_Juegues_con_Fuego', 3: 'La_Patrulla_del_Bosque',
    4: 'Limpia_tu_Terreno', 5: 'Llama_al_130', 6: 'La_Ruta_de_Escape', 7: 'Chao_Chao_Colilla',
    8: 'Mi_Casa_Preparada', 9: 'El_Brigadista', 10: 'Todos_Somos_Prevencion', 11: 'Alerta_Roja',
    12: 'Chispa_Traicionera', 13: 'Parque_Querido', 14: 'Cuenta_Conmigo_Vecino',
    15: 'Mi_Mascota_Tambien', 16: 'Fuente_Oficial', 17: 'Los_Fosforos_No_Se_Tocan',
    18: 'Humito_Gris', 19: 'De_la_Mano', 20: 'Senor_Fuego', 21: 'El_Ranking_del_Descuido',
    22: 'Dejame_Llegar_a_Viejo',
}


def main():
    os.chdir(RAIZ)

    with open('Cancionero_Karaoke.html', encoding='utf-8') as f:
        html = f.read()
    i0 = html.index('const SONGS = ') + len('const SONGS = ')
    songs, _ = json.JSONDecoder().raw_decode(html, i0)
    print('letras/estilos: %d canciones' % len(songs))

    audios = {norm(os.path.splitext(f)[0]): f for f in os.listdir('Audios') if f.lower().endswith('.mp3')}
    imagenes = {norm(os.path.splitext(f)[0]): f for f in os.listdir('Imagenes') if f.lower().endswith('.png')}

    problemas = []
    for s in songs:
        clave = norm(s['title'])

        audio = buscar(audios, clave)
        if audio:
            s['file'] = audio
            s['url'] = 'Audios/' + audio
        else:
            problemas.append('sin audio: ' + s['title'])

        img = IMG_ESPECIAL.get(s['n']) or buscar(imagenes, clave)
        if img:
            s['bg'] = 'Imagenes/' + img
            s['bgType'] = 'image'
        else:
            problemas.append('sin imagen: ' + s['title'])

        ruta_marcas = os.path.join('Marcas', '%02d_%s.json' % (s['n'], SLUGS[s['n']]))
        if os.path.exists(ruta_marcas):
            datos = leer_json(ruta_marcas)
            s['dur'] = int(round(datos.get('duracion', s['dur']) * 1000))
            marcas = datos.get('marcas', [])
            esperado = contar_lineas(s['lyrics'])
            if len(marcas) == esperado and esperado > 0:
                s['times'] = marcas
            else:
                s.pop('times', None)
                problemas.append('marcas %d != %d líneas: %s (queda sin karaoke exacto)'
                                 % (len(marcas), esperado, s['title']))
        else:
            s['dur'] = int(round(s['dur'] * 1000))
            s.pop('times', None)
            problemas.append('sin marcas: ' + s['title'])

    con_times = sum(1 for s in songs if s.get('times'))
    print('con karaoke exacto: %d/%d' % (con_times, len(songs)))
    for p in problemas:
        print('  AVISO: ' + p)

    with open(os.path.join('dev', 'plantilla_karaoke.html'), encoding='utf-8') as f:
        plantilla = f.read()
    marcador = '/*__SONGS__*/null'
    if marcador not in plantilla:
        sys.exit('la plantilla no tiene el placeholder ' + marcador)
    salida = plantilla.replace(marcador, json.dumps(songs, ensure_ascii=False))

    destino = 'Cancionero_Karaoke_Pro.html'
    with open(destino, 'w', encoding='utf-8') as f:
        f.write(salida)
    print('escrito: %s (%.1f KB)' % (destino, len(salida) / 1024))


if __name__ == '__main__':
    main()
