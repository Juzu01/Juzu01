"""Wariant minimal/bold: krótka rampa, dwa tony, duże płaskie plamy, ostre krawędzie.

Głowa + jasna plama policzków + długi spiczasty pysk + duże uszy; pierś
skrócona do szerokiej szyi, która wchodzi wysoko pod czaszkę (zasłania jej
ciemny spód z każdego kąta) i jest ucięta dołem kadru.
Trzy poziomy: '+' ciemny ton (tylko krawędź w cieniu), '#' i '@' jasny ton —
próg tonu (split) pokrywa się z granicą '+'/'#' rampy, żeby pasma znaków i
kolorów nie nakładały się. Światło niemal od kamery + mocny fill = cel-shading,
dzięki czemu pysk jest jasny z obu stron (120° i 240°). Kremowe części mają
shade > 1 (jaśniejsze futro), więc pysk/policzki/pierś są litymi plamami '@'.
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascii_fox import sphere, cone, xform

PARAMS = dict(
    cols=60, rows=34, frames=32, dur=6.4,
    char_w=7.6, line_h=13.8, font_px=11.5,         # rozmiar w SVG (60*7.6 = 456 px)
    cam=(0, 0.30, 6.5), target=(0, 0.12, 0), fov=34, aspect=0.5, tilt=-0.10,
    light=(-0.25, 0.35, 1.0), ambient=0.22, diffuse=0.45, fill=0.45,
    ramp=" +#@", gamma=0.5, split=0.25,             # 0.5**(1/0.5) = granica '+'/'#'
)

CREAM = 1.45   # mnożnik jasności kremowego futra

def fox():
    O, W, K = "o", "w", "k"
    objs = []
    objs.append((*sphere(1.0, 16, 9, scale=(1.12, 1.0, 1.0)), 1.0, O))                        # czaszka
    objs.append((*sphere(1.0, 12, 6, scale=(0.72, 0.42, 0.40), t=(0, -0.30, 0.72)), CREAM, W))  # jasne policzki
    mz = cone(0.56, 0.14, 1.30, 10)
    objs.append((xform(mz[0], rx=math.radians(96), t=(0, -0.15, 0.50)), mz[1], CREAM, W))       # pysk
    objs.append((*sphere(0.14, 8, 4, scale=(1.15, 1, 1), t=(0, -0.28, 1.80)), 1.0, K))          # nos
    for side in (-1, 1):
        ear = cone(0.45, 0.0, 1.55, 6)
        objs.append((xform(ear[0], rz=-side * math.radians(22), t=(side * 0.75, 0.35, -0.10)), ear[1], 1.0, O))
        objs.append((*sphere(0.19, 8, 4, t=(side * 0.44, 0.22, 0.80)), 1.0, K))                 # oczy (wtopione)
    neck = cone(0.95, 0.72, 1.45, 12)
    objs.append((xform(neck[0], t=(0, -2.00, 0.0)), neck[1], CREAM, W))                         # szyja/pierś: góra pod czaszką, dół ucięty kadrem
    return objs
