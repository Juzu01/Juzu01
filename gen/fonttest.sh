#!/usr/bin/env bash
# Renderuje ascii SVG z wymuszonymi różnymi czcionkami i składa jeden PNG do porównania.
# użycie: gen/fonttest.sh <variant> <katalog_wyjściowy>
set -e
V=$1; OUT=$2; mkdir -p "$OUT"
cd "$(dirname "$0")/.."
python3 gen/ascii_fox.py --variant "$V" --out "$OUT/ascii.svg" >/dev/null
i=0; html='<html><body style="margin:0;background:#0d1117;padding:8px;display:flex;flex-wrap:wrap;gap:8px">'
for f in "DejaVu Sans Mono" "Liberation Mono" "FreeMono" "Adwaita Mono" "Noto Sans Mono" "sans-serif"; do
  i=$((i+1))
  sed "s/font-family:[^;]*;/font-family:'$f';/" "$OUT/ascii.svg" > "$OUT/f$i.svg"
  html="$html<div><div style=\"color:#888;font:11px sans-serif\">$f</div><img src=\"f$i.svg\"></div>"
done
echo "$html</body></html>" > "$OUT/fonts.html"
timeout 90 firefox --headless --profile "$OUT/../ffprof" --window-size=1700,1000 --screenshot "$OUT/fonts.png" "file://$OUT/fonts.html" >/dev/null 2>&1 || true
echo "$OUT/fonts.png"
