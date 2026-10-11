#!/usr/bin/env python3
"""Obracający się lis w ASCII: siatka 3D → rasteryzator z z-buforem → znaki.

Wariant (plik w gen/variants/<nazwa>.py) dostarcza `fox()` (lista obiektów
(verts, tris, shade, paleta)) i `PARAMS` (rozdzielczość, rampa, światło...).

    python3 gen/ascii_fox.py --variant base --sheet /tmp/sheet.png   # podgląd 4 kątów (PNG)
    python3 gen/ascii_fox.py --variant base --out ascii-dark.svg     # animowany SVG
"""
import argparse, importlib.util, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- bryły -----------------------------------------------------------
def sphere(r=1.0, lon=12, lat=7, scale=(1, 1, 1), t=(0, 0, 0)):
    v, tris = [], []
    for i in range(lat + 1):
        th = math.pi * i / lat
        for j in range(lon):
            ph = 2 * math.pi * j / lon
            v.append([r * math.sin(th) * math.cos(ph) * scale[0] + t[0],
                      r * math.cos(th) * scale[1] + t[1],
                      r * math.sin(th) * math.sin(ph) * scale[2] + t[2]])
    for i in range(lat):
        for j in range(lon):
            a, b = i * lon + j, i * lon + (j + 1) % lon
            tris += [[a, b, b + lon], [a, b + lon, a + lon]]
    return v, tris

def cone(r1, r2, h, seg=8):
    """Stożek/walec wzdłuż +y, podstawa w (0,0,0)."""
    v, tris = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        v.append([math.cos(a) * r1, 0, math.sin(a) * r1]); v.append([math.cos(a) * r2, h, math.sin(a) * r2])
    bot = len(v); v.append([0, 0, 0]); top = len(v); v.append([0, h, 0])
    for i in range(seg):
        j = (i + 1) % seg
        b0, t0, b1, t1 = i * 2, i * 2 + 1, j * 2, j * 2 + 1
        tris += [[b0, t0, t1], [b0, t1, b1], [b0, b1, bot], [t1, t0, top]]
    return v, tris

def box(w, h, d, t=(0, 0, 0)):
    """Prostopadłościan wyśrodkowany w t."""
    v = [[(i & 1) * w - w / 2 + t[0], ((i >> 1) & 1) * h - h / 2 + t[1], ((i >> 2) & 1) * d - d / 2 + t[2]] for i in range(8)]
    quads = [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]]
    tris = []
    for a, b, c, d2 in quads: tris += [[a, b, c], [a, c, d2]]
    return v, tris

def xform(v, rx=0, ry=0, rz=0, t=(0, 0, 0), s=1.0):
    if isinstance(s, (int, float)): s = (s, s, s)
    cx, sx = math.cos(rx), math.sin(rx); cy, sy = math.cos(ry), math.sin(ry); cz, sz = math.cos(rz), math.sin(rz)
    out = []
    for x, y, z in v:
        x, y, z = x * s[0], y * s[1], z * s[2]
        y, z = y * cx - z * sx, y * sx + z * cx
        x, z = x * cy + z * sy, -x * sy + z * cy
        x, y = x * cz - y * sz, x * sz + y * cz
        out.append([x + t[0], y + t[1], z + t[2]])
    return out

# ---------- rasteryzator -------------------------------------------------------
def _norm(a):
    l = math.hypot(*a) or 1
    return [a[0] / l, a[1] / l, a[2] / l]
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

def render(objs, P, ry):
    """Zwraca (lum, pal): jasność 0..1 (-1 = tło) i paleta na komórkę."""
    cols, rows = P["cols"], P["rows"]
    cam_pos, target = P["cam"], P["target"]
    fwd = _norm(_sub(target, cam_pos)); right = _norm(_cross(fwd, [0, 1, 0])); up = _cross(right, fwd)
    f = 1 / math.tan(math.radians(P["fov"]) / 2)
    sx, sy = rows * f / P["aspect"] / 2, rows * f / 2
    light = _norm(P["light"]); amb, kd, kf = P["ambient"], P["diffuse"], P["fill"]
    z = [math.inf] * (cols * rows); lum = [-1.0] * (cols * rows); pal = [None] * (cols * rows)
    for verts, tris, shade, pid in objs:
        w = xform(verts, rx=P["tilt"], ry=ry)
        proj = []
        for p in w:
            d = _sub(p, cam_pos); dz = _dot(d, fwd)
            proj.append(None if dz < 0.05 else (cols / 2 + _dot(d, right) / dz * sx, rows / 2 - _dot(d, up) / dz * sy, dz))
        for a, b, c in tris:
            pa, pb, pc = proj[a], proj[b], proj[c]
            if None in (pa, pb, pc): continue
            n = _norm(_cross(_sub(w[b], w[a]), _sub(w[c], w[a])))
            if _dot(n, _sub(cam_pos, w[a])) < 0: n = [-n[0], -n[1], -n[2]]
            view = _norm(_sub(cam_pos, w[a]))
            L = min(1.0, amb + kd * max(0.0, _dot(n, light)) + kf * max(0.0, _dot(n, view))) * shade
            x0, x1 = max(0, int(min(pa[0], pb[0], pc[0]))), min(cols - 1, int(max(pa[0], pb[0], pc[0])) + 1)
            y0, y1 = max(0, int(min(pa[1], pb[1], pc[1]))), min(rows - 1, int(max(pa[1], pb[1], pc[1])) + 1)
            area = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pc[0] - pa[0]) * (pb[1] - pa[1])
            if abs(area) < 1e-9: continue
            for yy in range(y0, y1 + 1):
                py = yy + 0.5
                for xx in range(x0, x1 + 1):
                    px = xx + 0.5
                    w0 = ((pb[0] - px) * (pc[1] - py) - (pc[0] - px) * (pb[1] - py)) / area
                    w1 = ((pc[0] - px) * (pa[1] - py) - (pa[0] - px) * (pc[1] - py)) / area
                    w2 = 1 - w0 - w1
                    if w0 < 0 or w1 < 0 or w2 < 0: continue
                    depth = w0 * pa[2] + w1 * pb[2] + w2 * pc[2]
                    i = yy * cols + xx
                    if depth < z[i]: z[i] = depth; lum[i] = L; pal[i] = pid
    return lum, pal

def to_chars(lum, pal, P):
    """Siatka [(znak, klucz_koloru)] — klucz = paleta + '1'/'2' (ciemny/jasny), ' ' dla tła."""
    cols, rows, ramp, gamma, split = P["cols"], P["rows"], P["ramp"], P["gamma"], P["split"]
    thr = P.get("thresholds")          # opcjonalnie: jawne progi jasności dla kolejnych znaków rampy (poza spacją)
    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            L = lum[y * cols + x]
            if L < 0: row.append((" ", None)); continue
            if thr: k = sum(1 for t in thr if L >= t)
            else: k = int(min(1, max(0, L)) ** gamma * (len(ramp) - 1) + 0.5)
            row.append((ramp[min(k, len(ramp) - 1)], pal[y * cols + x] + ("1" if L < split else "2")))
        grid.append(row)
    return grid

def frames(variant, n=None):
    objs = variant.fox(); P = variant.PARAMS
    n = n or P["frames"]
    return [to_chars(*render(objs, P, 2 * math.pi * i / n), P) for i in range(n)]

def load_variant(name):
    path = name if name.endswith(".py") else os.path.join(HERE, "variants", name + ".py")
    spec = importlib.util.spec_from_file_location("variant", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

# ---------- wyjście -------------------------------------------------------------
THEMES = {
    "dark":  {"bg": "#0d1117", "o1": "#b5581a", "o2": "#ff8a2a", "w1": "#9a8c78", "w2": "#f1e4cb", "k1": "#1a0c04", "k2": "#1a0c04"},
    "light": {"bg": "#ffffff", "o1": "#a8440c", "o2": "#f0761a", "w1": "#7d6648", "w2": "#c49a62", "k1": "#1a0c04", "k2": "#1a0c04"},
}

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_svg(variant, out, theme="dark"):
    P = variant.PARAMS; th = THEMES[theme]
    fr = frames(variant)
    cols, rows, n = P["cols"], P["rows"], len(fr)
    CW, LH, FS = P["char_w"], P["line_h"], P["font_px"]
    PAD = 12
    W, H = int(cols * CW + 2 * PAD), int(rows * LH + 2 * PAD)
    dur = P["dur"]
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="rotating ascii fox">',
         f'<style>text{{font-family:ui-monospace,"Cascadia Mono","JetBrains Mono","SF Mono",Menlo,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace;font-size:{FS}px;white-space:pre}}</style>',
         f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>']
    for fi, grid in enumerate(fr):
        t0, t1 = fi / n, (fi + 1) / n
        g.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{t0:.5f};{t1:.5f};1" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>')
        for yi, row in enumerate(grid):
            if all(c == " " for c, _ in row): continue
            runs, cur, buf = [], None, []
            for ch, key in row:
                if key != cur and buf: runs.append((cur, "".join(buf))); buf = []
                cur = key; buf.append(ch)
            if buf: runs.append((cur, "".join(buf)))
            parts = "".join(f'<tspan fill="{th[key]}">{esc(txt)}</tspan>' if key else f'<tspan fill="none">{esc(txt)}</tspan>' for key, txt in runs)
            # textLength + preserve: każda linia ma dokładnie cols*CW szerokości niezależnie od czcionki
            g.append(f'<text x="{PAD}" y="{PAD + (yi + 0.8) * LH:.1f}" xml:space="preserve" textLength="{cols * CW:.1f}" lengthAdjust="spacingAndGlyphs">{parts}</text>')
        g.append("</g>")
    g.append("</svg>")
    svg = "\n".join(g)
    with open(out, "w") as f: f.write(svg)
    print(f"{out}: {len(svg)//1024} KB, {n} frames {cols}x{rows}, {W}x{H}px")

def contact_sheet(variant, out, angles=(0, 60, 120, 180, 240, 300), scale=2):
    """PNG z kilkoma kątami obok siebie (DejaVu Sans Mono), do oceny wzrokiem."""
    from PIL import Image, ImageDraw, ImageFont
    P = variant.PARAMS; objs = variant.fox(); th = THEMES["dark"]
    fnt = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 8 * scale) if os.path.exists("/usr/share/fonts/TTF/DejaVuSansMono.ttf") else ImageFont.load_default()
    cw, lh = fnt.getbbox("M")[2], int(8 * scale * 1.25)
    cols, rows = P["cols"], P["rows"]
    W = len(angles) * (cols * cw + 10) + 10; H = rows * lh + 20
    im = Image.new("RGB", (W, H), th["bg"]); d = ImageDraw.Draw(im)
    for ai, ang in enumerate(angles):
        grid = to_chars(*render(objs, P, math.radians(ang)), P)
        ox = 10 + ai * (cols * cw + 10)
        for yi, row in enumerate(grid):
            for xi, (ch, key) in enumerate(row):
                if ch != " ": d.text((ox + xi * cw, 10 + yi * lh), ch, font=fnt, fill=th[key])
    im.save(out); print(f"{out}: {W}x{H}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="base")
    ap.add_argument("--out"); ap.add_argument("--sheet"); ap.add_argument("--theme", default="dark")
    ap.add_argument("--text", action="store_true", help="wypisz klatkę 0 jako tekst")
    a = ap.parse_args()
    v = load_variant(a.variant)
    if a.text:
        for row in frames(v, 1)[0]: print("".join(c for c, _ in row))
    if a.sheet: contact_sheet(v, a.sheet)
    if a.out: build_svg(v, a.out, a.theme)
