"""Wariant bazowy: popiersie lisa (czaszka, pysk, uszy, oczy, nos, pierś)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascii_fox import sphere, cone, xform

PARAMS = dict(
    cols=60, rows=32, frames=32, dur=6.4,
    char_w=7.2, line_h=13.0, font_px=11.0,          # rozmiar w SVG
    cam=(0, 0.35, 5.6), target=(0, -0.15, 0), fov=34, aspect=0.5, tilt=-0.12,
    light=(-0.6, 0.7, 0.75), ambient=0.18, diffuse=0.62, fill=0.28,
    ramp=" .:-=+*#%@", gamma=0.7, split=0.5,
)

def fox():
    O, W, K = "o", "w", "k"
    objs = []
    objs.append((*sphere(1.0, 16, 9, scale=(1.18, 0.98, 1.02)), 1.0, O))                     # czaszka
    mz = cone(0.46, 0.13, 1.05, 10)
    objs.append((xform(mz[0], rx=math.radians(98), t=(0, -0.18, 0.62)), mz[1], 1.0, W))        # pysk
    objs.append((*sphere(0.15, 8, 4, scale=(1.3, 1, 1), t=(0, -0.30, 1.62)), 1.0, K))          # nos
    for side in (-1, 1):
        ear = cone(0.44, 0.0, 1.35, 4)
        objs.append((xform(ear[0], rz=-side * math.radians(22), t=(side * 0.66, 0.42, -0.08)), ear[1], 1.0, O))
        objs.append((*sphere(0.15, 8, 4, t=(side * 0.44, 0.22, 0.86)), 1.0, K))               # oczy
    neck = cone(1.05, 0.60, 1.10, 12)
    objs.append((xform(neck[0], t=(0, -1.70, -0.12)), neck[1], 1.0, W))                        # pierś
    return objs
