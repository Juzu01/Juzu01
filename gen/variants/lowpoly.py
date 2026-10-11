"""Wariant low-poly: mało segmentów, twarde fasety, mocny kontrast.

Duże trójkątne uszy (ostrosłup 3-ścienny z jasnym wnętrzem), spiczasty pysk
(ostrosłup 4-ścienny, krawędzią do góry), zwarta pierś.  Styl karty Pokémon.
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascii_fox import sphere, cone, xform

PARAMS = dict(
    cols=64, rows=34, frames=32, dur=6.4,
    char_w=7.2, line_h=13.0, font_px=11.0,          # rozmiar w SVG
    cam=(0, 0.50, 5.8), target=(0, 0.10, 0), fov=36, aspect=0.5, tilt=-0.10,
    light=(-0.72, 0.58, 0.42), ambient=0.30, diffuse=0.65, fill=0.10,
    ramp=" .:+*#%@", gamma=0.8, split=0.32,
)

def _inner_face(verts, a, b, c, shrink=0.62, lift=0.05):
    """Trójkąt wpisany w ścianę (a,b,c), odsunięty wzdłuż normalnej (wnętrze ucha)."""
    pa, pb, pc = verts[a], verts[b], verts[c]
    cx = [(pa[i] + pb[i] + pc[i]) / 3 for i in range(3)]
    u = [pb[i] - pa[i] for i in range(3)]; v = [pc[i] - pa[i] for i in range(3)]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    l = math.hypot(*n) or 1; n = [k / l for k in n]
    if n[2] < 0: n = [-k for k in n]                      # na zewnątrz = +z (przód)
    out = [[cx[i] + (p[i] - cx[i]) * shrink + n[i] * lift for i in range(3)] for p in (pa, pb, pc)]
    return out, [[0, 1, 2]]

def fox():
    O, W, K = "o", "w", "k"
    objs = []
    # czaszka: 8 x 5 — ośmiokąt z góry, pięć pasów
    objs.append((*sphere(1.0, 8, 5, scale=(1.05, 1.00, 1.02)), 1.0, O))
    # żuchwa/policzki: kremowa maska dolnej części twarzy (spłaszczona kula wystająca z czaszki)
    objs.append((*sphere(0.92, 8, 5, scale=(1.02, 0.66, 1.0), t=(0, -0.42, 0.22)), 1.0, W))
    # pysk: ostrosłup 4-ścienny (kwadrat w przekroju, płaski grzbiet na górze), kremowy
    mz = cone(0.52, 0.06, 0.92, 4)
    mv = xform(mz[0], ry=math.pi / 4)                       # kwadrat w przekroju: płaski grzbiet
    objs.append((xform(mv, rx=math.radians(100), t=(0, -0.12, 0.60)), mz[1], 1.0, W))
    # nos: ośmiościan
    objs.append((*sphere(0.12, 4, 2, scale=(1.3, 0.9, 1.0), t=(0, -0.30, 1.48)), 1.0, K))
    # uszy: ostrosłup 3-ścienny płaską ścianą do przodu + jasny trójkąt wnętrza
    for side in (-1, 1):
        ear = cone(0.50, 0.0, 1.35, 3)
        ev = xform(ear[0], ry=math.pi / 2)                  # ściana (1,2,apex) patrzy w +z
        ev = xform(ev, rz=-side * math.radians(15), t=(side * 0.64, 0.46, -0.10))
        objs.append((ev, ear[1], 1.0, O))
        # ściana przednia: wierzchołki podstawy 2 i 4 (po ry) i apex (idx 7)
        iv, it = _inner_face(ev, 2, 4, 7, shrink=0.56)
        objs.append((iv, it, 0.55, W))
        # oczy: ośmiościan rozciągnięty w migdał, lekko skośny
        eye = sphere(0.14, 4, 2, scale=(1.3, 0.6, 0.5))
        objs.append((xform(eye[0], rz=side * math.radians(18), t=(side * 0.46, 0.26, 0.94)), eye[1], 1.0, K))
    # szyja: krótki walec łączący głowę z piersią
    nk = cone(0.64, 0.64, 0.60, 8)
    objs.append((xform(nk[0], t=(0, -1.20, -0.08)), nk[1], 1.0, O))
    # pierś: krótki, szeroki ścięty stożek (nieco przygaszony, żeby nie bił twarzy)
    neck = cone(0.95, 0.68, 0.70, 8)
    objs.append((xform(neck[0], t=(0, -1.85, -0.05)), neck[1], 0.85, W))
    return objs
