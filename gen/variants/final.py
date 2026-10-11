"""Wariant finalny: bryła i czystość z „minimal", dłuższy lisi pysk z „kitsune",
poprawki po dwóch rundach sędziów: kamera daleko (uszy nie „pompują"),
jawne progi jasności (lite `@`, bez pasa `#` na szyi), szczęka V z odwróconego
stożka (spiczasty podbródek z przodu), uszy pośredniej wysokości, węższa pierś."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascii_fox import sphere, cone, xform

PARAMS = dict(
    cols=60, rows=34, frames=32, dur=6.4,
    char_w=7.0, line_h=13.8, font_px=11.5,
    cam=(0, 0.6, 12.0), target=(0, 0.0, 0), fov=19, aspect=0.5, tilt=-0.08,
    light=(-0.5, 0.5, 0.75), ambient=0.30, diffuse=0.50, fill=0.35,
    ramp=" +#@", gamma=0.5, split=0.42, thresholds=(0.08, 0.22, 0.42),
)
CREAM = 1.45

def fox():
    O, W, K = "o", "w", "k"
    objs = []
    objs.append((*sphere(1.0, 16, 9, scale=(1.02, 0.92, 0.96), t=(0, 0.12, 0)), 1.0, O))          # czaszka
    jaw = cone(0.0, 1.00, 1.30, 12)                                                                # szczęka V (czubek w dół)
    objs.append((xform(jaw[0], t=(0, -1.12, 0.04)), jaw[1], 1.0, O))
    chin = cone(0.0, 0.58, 0.85, 10)                                                               # kremowy podbródek
    objs.append((xform(chin[0], t=(0, -1.02, 0.42)), chin[1], CREAM, W))
    objs.append((*sphere(1.0, 12, 6, scale=(0.74, 0.34, 0.40), t=(0, -0.20, 0.72)), CREAM, W))     # jasne policzki
    mz = cone(0.42, 0.08, 1.40, 10)
    objs.append((xform(mz[0], rx=math.radians(97), t=(0, -0.05, 0.50)), mz[1], CREAM, W))          # pysk (spód kremowy)
    top = [[x * 0.72, y, z] for x, y, z in mz[0]]
    objs.append((xform(top, rx=math.radians(97), t=(0, 0.10, 0.50)), mz[1], 1.0, O))                # grzbiet pyska rudy
    objs.append((*sphere(0.15, 8, 4, scale=(1.15, 1, 1), t=(0, -0.19, 1.90)), 1.0, K))             # nos
    for side in (-1, 1):
        ear = cone(0.48, 0.0, 1.50, 5)
        objs.append((xform(ear[0], rz=-side * math.radians(16), t=(side * 0.62, 0.45, -0.08)), ear[1], 1.0, O))
        objs.append((*sphere(0.19, 8, 4, t=(side * 0.42, 0.30, 0.82)), 1.0, K))                    # oczy
    neck = cone(0.86, 0.58, 1.70, 12)
    objs.append((xform(neck[0], t=(0, -2.55, 0.0)), neck[1], CREAM, W))                            # szyja/pierś
    return objs
