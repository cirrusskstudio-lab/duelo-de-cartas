# Genera los iconos de Android (heredados, redondos y adaptativos) y la pantalla de arranque a partir de un PNG cuadrado.
# Uso: python3 scripts/gen_icons.py icono.png   → escribe native/res/
import sys, os
from PIL import Image, ImageDraw
src = Image.open(sys.argv[1]).convert('RGBA'); OUT = 'native/res'
D = {'mdpi':1, 'hdpi':1.5, 'xhdpi':2, 'xxhdpi':3, 'xxxhdpi':4}
def scaled(px): return src.resize((px, px), Image.NEAREST if px % src.width == 0 or src.width % px == 0 else Image.LANCZOS)
def rounded(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    o = Image.new('RGBA', im.size, (0, 0, 0, 0)); o.paste(im, (0, 0), m); return o
def circle(im):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).ellipse([0, 0, im.width - 1, im.height - 1], fill=255)
    o = Image.new('RGBA', im.size, (0, 0, 0, 0)); o.paste(im, (0, 0), m); return o
for d, k in D.items():
    p = f'{OUT}/mipmap-{d}'; os.makedirs(p, exist_ok=True)
    n = round(48 * k); art = scaled(n)
    rounded(art, round(n * .18)).save(f'{p}/ic_launcher.png')
    circle(art).save(f'{p}/ic_launcher_round.png')
    c = round(108 * k); a = round(76 * k)           # adaptativo: capa de 108 dp con el dibujo a 76 dp (cubre la zona visible de 72 dp)
    fg = Image.new('RGBA', (c, c), (0, 0, 0, 0)); fg.paste(scaled(a), ((c - a) // 2, (c - a) // 2)); fg.save(f'{p}/ic_launcher_foreground.png')
# color de fondo del icono adaptativo = color del borde del dibujo
px = src.convert('RGB'); w, h = px.size
edge = [px.getpixel((x, y)) for x in range(0, w, 8) for y in (2, h - 3)] + [px.getpixel((x, y)) for y in range(0, h, 8) for x in (2, w - 3)]
r, g, b = (sorted(c[i] for c in edge)[len(edge) // 2] for i in range(3))
os.makedirs(f'{OUT}/values', exist_ok=True); os.makedirs(f'{OUT}/drawable', exist_ok=True)
open(f'{OUT}/values/ic_launcher_background.xml', 'w').write(f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#{r:02X}{g:02X}{b:02X}</color>\n</resources>\n')
open(f'{OUT}/drawable/splash.xml', 'w').write('<?xml version="1.0" encoding="utf-8"?>\n<!-- Pantalla de arranque: fondo liso del juego (el logo animado lo muestra el juego) -->\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">\n    <solid android:color="#000000" />\n</shape>\n')
print('iconos generados; fondo adaptativo', f'#{r:02X}{g:02X}{b:02X}')
