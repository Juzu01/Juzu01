"""Wariant fine: gęsta siatka 80x44, drobna czcionka, 36 klatek, długa rampa.

Geometria jak w base (popiersie: czaszka, pysk, uszy, oczy, nos, pierś), ale
gładsze bryły i dwubarwne elementy: kremowe policzki/broda, kremowy spód pyska,
kremowe wnętrze uszu i kremowy śliniak na piersi — od tyłu lis jest cały rudy.
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascii_fox import sphere, cone, xform

PARAMS = dict(
    cols=80, rows=44, frames=36, dur=7.2,
    char_w=5.6, line_h=10.0, font_px=8.5,          # rozmiar w SVG
    cam=(0, 0.75, 5.6), target=(0, -0.20, 0), fov=36, aspect=0.56, tilt=-0.10,
    light=(-0.55, 0.45, 0.80), ambient=0.20, diffuse=0.52, fill=0.30,
    ramp=".-:;~=+*xo#&%@", gamma=0.6, split=0.5,
)

def band(r1, r2, h, seg, a0, a1):
    """Wycinek pobocznicy stożka wzdłuż +y między kątami a0..a1 (0 = +x, pi/2 = +z), bez denek."""
    v, tris = [], []
    for i in range(seg + 1):
        a = a0 + (a1 - a0) * i / seg
        v.append([math.cos(a) * r1, 0, math.sin(a) * r1]); v.append([math.cos(a) * r2, h, math.sin(a) * r2])
    for i in range(seg):
        b0, t0, b1, t1 = i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 3
        tris += [[b0, t0, t1], [b0, t1, b1]]
    return v, tris

def split(verts, tris, pred):
    """Dzieli trójkąty wg predykatu na środku ciężkości: (pasujące, reszta)."""
    yes, no = [], []
    for t in tris:
        c = [sum(verts[i][k] for i in t) / 3 for k in range(3)]
        (yes if pred(c) else no).append(t)
    return yes, no

def ear(w, d, h):
    """Klin ucha: płaska ściana przednia (-w..w, 0, d) → wierzchołek (0, h, -0.02), tył zbiega do (0, 0, -d)."""
    verts = [[-w, 0, d], [w, 0, d], [0, 0, -d], [0, h, -0.02]]
    tris = [[0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1]]
    return verts, tris

def inner_ear(ev, k, off):
    """Kremowy trójkąt wnętrza: ściana przednia ucha zmniejszona k razy wokół środka i wysunięta o off w +z."""
    f = [ev[0], ev[1], ev[3]]
    c = [sum(p[i] for p in f) / 3 for i in range(3)]
    return [[c[0] + (p[0] - c[0]) * k, c[1] + (p[1] - c[1]) * k, c[2] + (p[2] - c[2]) * k + off] for p in f]

def fox():
    O, W, K = "o", "w", "k"
    objs = []
    # czaszka: góra ruda, dolny przód (policzki, broda) kremowy
    hv, ht = sphere(1.0, 28, 16, scale=(1.18, 0.98, 1.02))
    def cheek(c):
        x, y, z = c
        return z > -0.05 - 0.6 * max(0.0, -y - 0.4) and y < -0.40 + 0.5 * abs(x) / 1.18
    wt, ot = split(hv, ht, cheek)
    objs.append((hv, ot, 1.0, O)); objs.append((hv, wt, 1.0, W))
    # pysk: góra ruda, spód kremowy (po obrocie rx=98° lokalne +z to świat -y)
    for a0, a1, pal in ((math.pi, 2 * math.pi, O), (0.0, math.pi, W)):
        mz = band(0.50, 0.14, 1.00, 10, a0, a1)
        objs.append((xform(mz[0], rx=math.radians(98), t=(0, -0.12, 0.62)), mz[1], 1.0, pal))
    objs.append((*sphere(0.16, 12, 6, scale=(1.2, 0.9, 1), t=(0, -0.27, 1.60)), 1.0, K))        # nos
    for side in (-1, 1):
        ev, et = ear(0.56, 0.22, 1.30)
        objs.append((xform(ev, rz=-side * math.radians(18), t=(side * 0.60, 0.36, -0.10)), et, 1.0, O))
        iv = inner_ear(ev, 0.58, 0.04)
        objs.append((xform(iv, rz=-side * math.radians(18), t=(side * 0.60, 0.36, -0.10)), [[0, 1, 2]], 1.0, W))
        objs.append((*sphere(0.13, 12, 6, scale=(1.35, 0.85, 1.0), t=(side * 0.46, 0.20, 0.86)), 1.0, K))   # oczy
    # pierś: rudy stożek + kremowy śliniak z przodu
    neck = cone(1.38, 0.80, 2.00, 28)
    objs.append((xform(neck[0], t=(0, -2.30, -0.38)), neck[1], 1.0, O))
    bib = band(1.38 * 1.02, 0.80 * 1.02, 2.00, 14, math.pi / 2 - 1.25, math.pi / 2 + 1.25)
    objs.append((xform(bib[0], t=(0, -2.30, -0.38)), bib[1], 1.0, W))
    return objs
