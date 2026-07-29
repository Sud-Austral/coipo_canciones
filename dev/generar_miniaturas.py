#!/usr/bin/env python3
"""
generar_miniaturas.py — crea Miniaturas/ para la grilla de la portada.

    python dev/generar_miniaturas.py

Las imágenes de Imagenes/ son PNG de 1536x864 y ~2,5 MB cada una: servir las 22
en la portada son ~53 MB. Esto genera versiones WebP de 640px de ancho (unos
40-60 KB), suficientes para tarjetas de ~370px incluso en pantallas retina.
El reproductor sigue usando las imágenes grandes (van a pantalla completa).
"""
import os

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHO = 640
CALIDAD = 82
# imagen de fondo del hero: se sirve a ancho completo, necesita más resolución
HERO_ORIGEN = 'El Fuego Se Apaga en Invierno.png'
HERO_SALIDA = '_hero.webp'
HERO_ANCHO = 1400


def main():
    os.chdir(RAIZ)
    destino = 'Miniaturas'
    os.makedirs(destino, exist_ok=True)

    total_orig = total_min = 0
    archivos = sorted(f for f in os.listdir('Imagenes') if f.lower().endswith('.png'))
    for nombre in archivos:
        origen = os.path.join('Imagenes', nombre)
        salida = os.path.join(destino, os.path.splitext(nombre)[0] + '.webp')
        with Image.open(origen) as im:
            im = im.convert('RGB')
            alto = round(im.height * ANCHO / im.width)
            im.resize((ANCHO, alto), Image.LANCZOS).save(salida, 'WEBP', quality=CALIDAD, method=6)
        o, m = os.path.getsize(origen), os.path.getsize(salida)
        total_orig += o
        total_min += m
        print('%-42s %5.1f MB -> %4.0f KB' % (nombre, o/1048576, m/1024))

    print('\n%d miniaturas · %.1f MB -> %.2f MB (%.0f%% menos)'
          % (len(archivos), total_orig/1048576, total_min/1048576,
             100 * (1 - total_min/total_orig)))

    origen_hero = os.path.join('Imagenes', HERO_ORIGEN)
    if os.path.exists(origen_hero):
        salida = os.path.join(destino, HERO_SALIDA)
        with Image.open(origen_hero) as im:
            im = im.convert('RGB')
            alto = round(im.height * HERO_ANCHO / im.width)
            im.resize((HERO_ANCHO, alto), Image.LANCZOS).save(salida, 'WEBP', quality=86, method=6)
        print('hero %dpx: %.0f KB' % (HERO_ANCHO, os.path.getsize(salida)/1024))


if __name__ == '__main__':
    main()
