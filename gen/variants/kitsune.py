"""Wariant kitsune: stylizowany lis — wielka głowa, długi szpiczasty pysk, wysokie uszy, wąska szyja."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascii_fox import sphere, cone, xform

PARAMS = dict(
    cols=70, rows=38, frames=36, dur=7.2,
    char_w=7.2, line_h=13.0, font_px=11.0,          # rozmiar w SVG
    cam=(0, 0.55, 6.6), target=(0, 0.0, 0), fov=34, aspect=0.5, tilt=-0.10,
    light=(-0.3, 0.6, 0.85), ambient=0.26, diffuse=0.56, fill=0.26,
    ramp=" .:-=+*#%@", gamma=0.65, split=0.5,
)

def fox():
    O, W, K = "o", "w", "k"
    objs = []
    HC = (0, 0.15, -0.28)                                                                        # środek czaszki
    objs.append((*sphere(1.0, 18, 10, scale=(1.05, 1.0, 1.0), t=HC), 1.0, O))                  # czaszka
    # pysk: biały stożek + węższy pomarańczowy grzbiet (ten sam stożek, zwężony w x i podniesiony)
    mz = cone(0.36, 0.05, 1.15, 12)
    mzv = xform(mz[0], rx=math.radians(102), t=(0, -0.05, 0.38))
    objs.append((mzv, mz[1], 1.0, W))
    top = xform([[x * 0.5, y, z] for x, y, z in mz[0]], rx=math.radians(102), t=(0, 0.05, 0.38))
    objs.append((top, mz[1], 1.0, O))
    tip = mzv[-1]
    objs.append((*sphere(0.16, 8, 4, scale=(1.3, 0.9, 1), t=(tip[0], tip[1] + 0.03, tip[2] + 0.02)), 1.0, K))   # nos
    SK = (1.05, 1.0, 1.0)                                                                       # skala czaszki
    def on_skull(x, y, depth):
        """Punkt na powierzchni czaszki w (x, y) i środek kuli wtopionej `depth` wzdłuż normalnej."""
        rx, ry = x / SK[0], (y - HC[1]) / SK[1]
        rz = math.sqrt(max(0.0, 1 - rx * rx - ry * ry))
        n = [rx / SK[0], ry / SK[1], rz / SK[2]]; l = math.hypot(*n); n = [c / l for c in n]
        P = (x, y, HC[2] + rz * SK[2])
        return [P[i] - depth * n[i] for i in range(3)]
    for side in (-1, 1):
        ear = cone(0.55, 0.0, 1.10, 4)
        objs.append((xform(ear[0], ry=math.radians(45), rz=-side * math.radians(20), t=(side * 0.55, 0.70, HC[2] - 0.05)), ear[1], 1.0, O))
        # kremowe wnętrze ucha: płaski trójkąt tuż przed przednią ścianą ostrosłupa (z przodu widoczny, z boku linia)
        fz = lambda y: 0.389 * (1 - y / 1.10) + 0.04
        inner = [[-0.27, 0.16, fz(0.16)], [0.27, 0.16, fz(0.16)], [0.0, 0.86, fz(0.86)]]
        objs.append((xform(inner, rz=-side * math.radians(20), t=(side * 0.55, 0.70, HC[2] - 0.05)), [[0, 1, 2]], 1.0, W))
        # oko: duża kula (R=0.5) wtopiona w czaszkę tak, że wystaje tylko płaska czapeczka ~0.5 x 0.2
        eye = sphere(0.50, 12, 6, scale=(1.0, 0.40, 1.0))
        objs.append((xform(eye[0], rz=side * math.radians(25), t=on_skull(side * 0.44, 0.36, 0.42)), eye[1], 1.0, K))
        objs.append((*sphere(0.55, 12, 6, scale=(1.0, 0.75, 0.7), t=(side * 0.45, -0.20, 0.22)), 1.0, W))     # białe policzki
    neck = cone(0.45, 0.40, 0.5, 10)
    objs.append((xform(neck[0], t=(0, -1.30, -0.15)), neck[1], 1.0, W))                         # szyja
    ch = cone(1.05, 0.50, 1.0, 12)
    objs.append((xform(ch[0], t=(0, -2.30, -0.10)), ch[1], 1.0, O))                             # pierś
    objs.append((xform([[x * 0.6, y, z] for x, y, z in ch[0]], t=(0, -2.30, 0.02)), ch[1], 1.0, W))   # biały śliniak
    return objs
