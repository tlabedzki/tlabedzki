"""Subset IBM Plex fonts for embedding in the SVG graphics (dev tool, run once).

GitHub shows the graphics through <img>, which cannot load external fonts, so every SVG embeds small WOFF2 subsets
as data URIs. This script cuts the @fontsource files down to printable ASCII (plus Polish letters in a separate
"ext" face) and writes advance widths to fonts/metrics.json, so the generators can measure text without fontTools.

Needs: pip install fonttools brotli. Source: the @fontsource packages in ../Insighteo-Website/node_modules.
Usage: python scripts/subset_fonts.py [path-to-@fontsource]
"""
import json
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / 'Insighteo-Website' / 'node_modules' / '@fontsource'
OUT = ROOT / 'fonts'

ASCII = ''.join(chr(c) for c in range(0x20, 0x7F)) + '·•'
POLISH = 'ĄąĆćĘęŁłŃńŚśŹźŻż'

FACES = {
    'mono-400': ('ibm-plex-mono', 400),
    'mono-600': ('ibm-plex-mono', 600),
    'sans-400': ('ibm-plex-sans', 400),
    'sans-600': ('ibm-plex-sans', 600),
}


def cut(src: Path, dst: Path, text: str) -> dict:
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['kern', 'liga']
    opts.name_IDs = []
    opts.notdef_outline = False
    font = subset.load_font(str(src), opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    subset.save_font(font, str(dst), opts)
    t = TTFont(str(src))
    upem = t['head'].unitsPerEm
    cmap = t.getBestCmap()
    hmtx = t['hmtx']
    return {ch: round(hmtx[cmap[ord(ch)]][0] / upem, 4) for ch in text if ord(ch) in cmap}


def main() -> None:
    metrics = {}
    for key, (pkg, weight) in FACES.items():
        files = SRC / pkg / 'files'
        adv = cut(files / f'{pkg}-latin-{weight}-normal.woff2', OUT / f'{key}.woff2', ASCII)
        adv |= cut(files / f'{pkg}-latin-ext-{weight}-normal.woff2', OUT / f'{key}-ext.woff2', POLISH)
        metrics[key] = adv
        print(key, (OUT / f'{key}.woff2').stat().st_size, (OUT / f'{key}-ext.woff2').stat().st_size)
    (OUT / 'metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=0), encoding='utf-8')


if __name__ == '__main__':
    main()
