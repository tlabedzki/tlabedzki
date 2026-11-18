"""App screenshot for a project card: a tall strip of the page, scrolled through inside the card (build.py, projects).

Input: a full-page PNG of the app at a 960 CSS px wide viewport and device scale factor 2 (Data-Generator: headless
Chrome after "Generate data" with the Medium preset, zlecenie 364). Output: shots/<name>.webp, cut at --bottom
(CSS px) and scaled to --width px. build.py embeds the file as a data URI, so keep it small (about 120 KB).

Needs Pillow (not the standard library), unlike build.py, which only reads the finished file.

Usage: python scripts/make_shot.py <full-page.png> <name> [--bottom 3480] [--width 1000] [--quality 72]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CSS_WIDTH = 960


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('name')
    ap.add_argument('--bottom', type=int, default=3480, help='last CSS px of the page to keep')
    ap.add_argument('--width', type=int, default=1000)
    ap.add_argument('--quality', type=int, default=72)
    a = ap.parse_args()
    im = Image.open(a.source).convert('RGB')
    scale = im.width / CSS_WIDTH
    im = im.crop((0, 0, im.width, round(a.bottom * scale)))
    im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
    out = ROOT / 'shots' / f'{a.name}.webp'
    out.parent.mkdir(exist_ok=True)
    im.save(out, quality=a.quality, method=6)  # EXIF and other metadata are not copied
    print(f'{out.name}: {im.width}x{im.height}, {out.stat().st_size / 1024:.0f} KB')


if __name__ == '__main__':
    main()
