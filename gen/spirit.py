#!/usr/bin/env python3
"""spirit.svg: prawdziwy wykres kontrybucji (53 tygodnie) i pikselowy duszek-lis,
który skacze po komórkach, zatrzymuje się na dniach z największą liczbą commitów
i tam unosi się w miejscu. Same prostokąty, ruch dyskretny, zero wygładzania.

    python3 gen/spirit.py [--theme dark|light] [--out spirit.svg] [--offline] [--t SEK]
"""
import argparse, json, math, random, subprocess, sys
from datetime import date, datetime, timedelta

USER = "Juzu01"
BEGIN = ""
TOFF = 0.0                  # podgląd: przesunięcie czasu
CELL, GAP = 11, 2
P = CELL + GAP
PX = 3                      # rozmiar piksela duszka
STEP = 0.11                 # s na komórkę
HOLD = 1.8                  # s postoju
THEMES = {
    "dark":  dict(bg="#0d1117", levels=["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"], text="#8b949e", trail="#ff8a2a"),
    "light": dict(bg="#ffffff", levels=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"], text="#57606a", trail="#ff8a2a"),
}
INK = {"O": "#ff8a2a", "D": "#c9541a", "W": "#ffe7c9", "K": "#1a0c04"}
SPRITE_A = [
    ".O.....O.",
    ".OO...OO.",
    ".OWO.OWO.",
    ".OOOOOOO.",
    "OOOOOOOOO",
    "OOOKOOOKO",
    "OOOWWWOOO",
    "OOOWKWOOO",
    "DOOOOOOOD",
    ".DO.O.OD.",
]
SPRITE_B = SPRITE_A[:-1] + [".D.OO.OD."]
SW, SH = len(SPRITE_A[0]) * PX, len(SPRITE_A) * PX

# ---------- dane --------------------------------------------------------------
def calendar(offline):
    if not offline:
        q = '{ user(login:"%s"){ contributionsCollection{ contributionCalendar{ totalContributions weeks{ contributionDays{ contributionCount date } } } } } }' % USER
        try:
            out = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"], capture_output=True, text=True, timeout=30, check=True).stdout
            cal = json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
            return weeks, cal["totalContributions"]
        except Exception as e:  # noqa: BLE001
            print(f"graphql: {e}", file=sys.stderr)
    rnd = random.Random(3)
    today = date.today(); start = today - timedelta(days=today.weekday() + 1 + 52 * 7)
    weeks, total = [], 0
    for w in range(53):
        days = []
        for d in range(7):
            dt = start + timedelta(days=w * 7 + d)
            if dt > today: break
            c = 0 if rnd.random() < .7 or w < 30 else rnd.choice([1, 2, 3, 5, 9, 14])
            total += c; days.append((dt.isoformat(), c))
        weeks.append(days)
    return weeks, total

def level(c, mx):
    if c <= 0: return 0
    return max(1, min(4, math.ceil(c / max(mx, 1) * 4)))

# ---------- trasa duszka --------------------------------------------------------
def route(weeks, hot):
    """Lista (col, row, flip) w krokach czasowych; postoje = powtórzenia z podskokiem."""
    ncol = len(weeks)
    steps = []
    def walk(cols, phase, stops):
        row = 3
        for i, c in enumerate(cols):
            target = stops.get(c)
            want = target if target is not None else max(0, min(6, round(3 + 2.6 * math.sin(i / 3.1 + phase))))
            row += (want > row) - (want < row)
            steps.append((c, row, 0))
            if target is not None and row == target:
                for k in range(int(HOLD / STEP)):
                    steps.append((c, row, -1 if (k // 3) % 2 else 0))     # unoszenie: co 3 kroki 1 px w górę
    right = sorted(hot[0::2]); left = sorted(hot[1::2])
    walk(range(-3, ncol + 3), 0.0, {c: r for c, r in right})
    walk(range(ncol + 2, -4, -1), 1.7, {c: r for c, r in left})
    return steps

# ---------- svg -----------------------------------------------------------------
def sprite(frame, color=None):
    out = []
    for y, row in enumerate(frame):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch == ".": x += 1; continue
            x0 = x
            while x < len(row) and row[x] == ch: x += 1
            out.append(f'<rect x="{x0 * PX}" y="{y * PX}" width="{(x - x0) * PX}" height="{PX}" fill="{color or INK[ch]}"/>')
    return "".join(out)

def build(out, theme, offline):
    th = THEMES[theme]
    weeks, total = calendar(offline)
    mx = max((c for w in weeks for _, c in w), default=1)
    cells = [(wi, di, c, d) for wi, w in enumerate(weeks) for di, (d, c) in enumerate(w)]
    hot = [(wi, di) for wi, di, c, _ in sorted(cells, key=lambda t: (-t[2], t[3]))[:6] if c > 0]
    steps = route(weeks, hot)
    T = len(steps) * STEP

    GX, GY = 40, 48
    W = GX + len(weeks) * P + 16
    H = GY + 7 * P + 18
    g = [f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>']
    g.append(f'<text x="{GX}" y="16" class="t">{total} contributions in the last year</text>')
    for di, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        g.append(f'<text x="{GX - 6}" y="{GY + di * P + 9}" class="t" text-anchor="end">{lab}</text>')
    seen = set()
    for wi, w in enumerate(weeks):
        for di, (d, c) in enumerate(w):
            g.append(f'<rect x="{GX + wi * P}" y="{GY + di * P}" width="{CELL}" height="{CELL}" rx="2" fill="{th["levels"][level(c, mx)]}"/>')
        m = datetime.fromisoformat(w[0][0]).strftime("%b") if w else ""
        if w and m not in seen and datetime.fromisoformat(w[0][0]).day <= 7 and wi < len(weeks) - 2:
            seen.add(m); g.append(f'<text x="{GX + wi * P}" y="{GY - 8}" class="t">{m}</text>')

    def pos(c, r, bob):
        x = GX + c * P + CELL // 2 - SW // 2
        y = GY + r * P + CELL - SH + 1 + bob * PX
        return f"{x} {y}"
    vals = ";".join(pos(c, r, b) for c, r, b in steps)
    kt = ";".join(f"{i / len(steps):.5f}" for i in range(len(steps)))
    flips, ft, last = [], [], None
    for i in range(len(steps)):
        nxt = steps[min(i + 1, len(steps) - 1)]; prv = steps[i]
        dx = nxt[0] - prv[0]
        f = "1 1" if dx >= 0 else "-1 1"
        if dx == 0: f = last or "1 1"
        if f != last: flips.append(f); ft.append(f"{i / len(steps):.5f}"); last = f
    def mover(k):
        return (f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{vals}" keyTimes="{kt}" '
                f'dur="{T:.2f}s" repeatCount="indefinite" begin="{-((T - k * STEP) if k else 0) - TOFF:.3f}s"/>')
    def flipper():
        return (f'<g transform="translate({SW // 2} 0)"><g><animateTransform attributeName="transform" type="scale" calcMode="discrete" values="{";".join(flips)}" keyTimes="{";".join(ft)}" '
                f'dur="{T:.2f}s" repeatCount="indefinite" {BEGIN}/><g transform="translate({-SW // 2} 0)">')
    # ślad: 3 sylwetki z opóźnieniem
    for k, op in ((3, .10), (2, .18), (1, .30)):
        g.append(f'<g opacity="{op}">{sprite(SPRITE_A, th["trail"])}{mover(k)}</g>')
    # duszek: dwie klatki na zmianę
    g.append(f'<g>{mover(0)}{flipper()}'
             f'<g>{sprite(SPRITE_A)}<animate attributeName="opacity" values="1;0" keyTimes="0;.5" calcMode="discrete" dur=".5s" repeatCount="indefinite"/></g>'
             f'<g>{sprite(SPRITE_B)}<animate attributeName="opacity" values="0;1" keyTimes="0;.5" calcMode="discrete" dur=".5s" repeatCount="indefinite"/></g>'
             f'</g></g></g></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" role="img" aria-label="contribution graph with a pixel fox ghost flying over it">'
           f'<style>.t{{font:11px ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{th["text"]}}}</style>'
           + "".join(g) + "</svg>")
    with open(out, "w") as f: f.write(svg)
    print(f"{out}: {len(svg)//1024} KB, {len(weeks)} weeks, total {total}, loop {T:.1f}s, hot {hot}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="spirit.svg")
    ap.add_argument("--theme", default="dark", choices=THEMES)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--t", type=float, default=None)
    a = ap.parse_args()
    if a.t is not None: BEGIN = f'begin="-{a.t}s"'; TOFF = a.t
    build(a.out, a.theme, a.offline)
