"""Shared building blocks for the profile graphics: palettes, embedded fonts, text measuring, window chrome.

Style: insighteo.pl "command center" (near-black screen, teal accent, terminals, falling glyphs, IBM Plex).
GitHub shows the graphics through <img>: no JS, no external fonts, so fonts are embedded as WOFF2 data URIs
(subsets made by scripts/subset_fonts.py) and all motion is CSS inside the SVG.

Theme rule: every file holds both palettes and picks one with @media (prefers-color-scheme) inside the SVG
(save_themed). In an <img>, Chrome answers that query with the used color-scheme of the <img>, and GitHub sets
color-scheme from the theme it actually paints (also "sync with system" with a dark day theme). A <source media>
in the README would follow the OS instead, and GitHub's own switches (<themed-picture>, #gh-dark-mode-only)
only look at data-color-mode, so they miss that case (zlecenie 319). Without prefers-color-scheme: dark.

Motion rule: the base styles are the final state and animations only lead into it (fill-mode both), so
@media (prefers-reduced-motion: reduce) can switch every animation off and leave the finished picture.

Python standard library only: the daily workflow runs this without installing anything.
"""
from __future__ import annotations

import base64
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / 'fonts'
ASSETS = ROOT / 'assets'
METRICS = json.loads((FONTS / 'metrics.json').read_text(encoding='utf-8'))

# Palette 7a from insighteo.pl (src/styles/global.css) and a light palette for GitHub's light themes.
PALETTES = {
    'dark': {
        'page': '#0d1117',
        'bg': '#000502',
        'panel': '#00100b',
        'bar': '#001a12',
        'line': 'rgba(45,212,191,0.28)',
        'line_soft': 'rgba(45,212,191,0.14)',
        'ink': '#ecfeff',
        'text': '#a7f3d0',
        'soft': '#b5d1ca',
        'muted': '#7fa39b',
        'accent': '#2dd4bf',
        'accent2': '#4ade80',
        'amber': '#fbbf24',
        'pink': '#f472b6',
        'bright': '#ccfbf1',
        'rain': '#2dd4bf',
        'rain_head': '#ccfbf1',
        'rain_opacity': 0.8,
        'rain_head_opacity': 0.95,
        'glow': 0.35,
        'text_glow': True,
        'veil': '#000502',
    },
    # Light: GitHub's own light colors (Primer: canvas, borders, fg default/muted, success) with one teal accent
    # from insighteo.pl, darkened for contrast. No glow and no warm colors: on white a glow blurs the text and
    # amber/pink clash with GitHub (zlecenie 323). Text contrast at least 4.5:1 (WCAG AA) on panel and bg.
    'light': {
        'page': '#ffffff',
        'bg': '#f6f8fa',
        'panel': '#ffffff',
        'bar': '#f6f8fa',
        'line': '#d1d9e0',
        'line_soft': '#e1e6eb',
        'ink': '#1f2328',
        'text': '#1f2328',
        'soft': '#424a53',
        'muted': '#59636e',
        'accent': '#0f766e',
        'accent2': '#1a7f37',
        'amber': '#115e59',
        'pink': '#0f766e',
        'bright': '#0f766e',
        'rain': '#0f766e',
        'rain_head': '#0f766e',
        'rain_opacity': 0.2,
        'rain_head_opacity': 0.4,
        'glow': 0,
        'text_glow': False,
        'veil': '#f6f8fa',
    },
}

FAMILY = {'mono': "'Plex Mono', ui-monospace, 'Cascadia Mono', Consolas, monospace",
          'sans': "'Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"}


def esc(text: str) -> str:
    return escape(text, quote=True)


def width(text: str, face: str, size: float) -> float:
    """Advance width of `text` in px (no kerning, which matches per-glyph placement)."""
    adv = METRICS[face]
    return sum(adv.get(ch, 0.6) for ch in text) * size


def wrap(text: str, face: str, size: float, max_w: float) -> list[str]:
    words, lines, cur = text.split(' '), [], ''
    for w in words:
        test = f'{cur} {w}' if cur else w
        if cur and width(test, face, size) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def _font_face(face: str) -> str:
    family, weight = face.split('-')
    name = 'Plex Mono' if family == 'mono' else 'Plex Sans'
    out = []
    for suffix, rng in (('', 'U+0020-007E,U+00B7,U+2022'), ('-ext', 'U+0104-017C')):
        data = base64.b64encode((FONTS / f'{face}{suffix}.woff2').read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{name}';font-weight:{weight};"
                   f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{rng}}}")
    return ''.join(out)


class Svg:
    """Collects defs, CSS and body markup, then writes one self-contained SVG."""

    def __init__(self, w: float, h: float, theme: str, title: str):
        self.w, self.h, self.theme, self.title = w, h, theme, title
        self.p = PALETTES[theme]
        self.fonts: set[str] = set()
        self.css: list[str] = []
        self.defs: list[str] = []
        self.body: list[str] = []
        self._ids = 0

    def uid(self, prefix: str) -> str:
        """Unique id; the theme letter keeps ids apart when save_themed puts both themes in one file."""
        self._ids += 1
        return f'{prefix}{self.theme[0]}{self._ids}'

    def font(self, face: str) -> str:
        self.fonts.add(face)
        family, weight = face.split('-')
        return f'font-family:{FAMILY[family]};font-weight:{weight}'

    def add(self, *parts: str) -> None:
        self.body.extend(parts)

    def text(self, x: float, y: float, s: str, face: str, size: float, fill: str, *, anchor: str = 'start',
             cls: str = '', style: str = '', extra: str = '') -> str:
        c = f' class="{cls}"' if cls else ''
        st = f';{style}' if style else ''
        a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
        return (f'<text x="{x:.1f}" y="{y:.1f}"{a}{c} style="{self.font(face)};font-size:{size}px{st}"'
                f' fill="{fill}"{extra}>{esc(s)}</text>')

    def render(self) -> str:
        return _render(self, [self])

    def save(self, name: str) -> Path:
        return _write(name, self.render())

    # ---- shared pieces -------------------------------------------------------------------------------------------

    def glow_filter(self, blur: float = 16) -> str:
        fid = self.uid('glow')
        self.defs.append(f'<filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%">'
                         f'<feGaussianBlur stdDeviation="{blur}"/></filter>')
        return fid

    def text_glow(self, blur: float = 6) -> str:
        """Soft halo behind text (like text-shadow on insighteo.pl): the ` filter="..."` attribute to add.
        Empty in palettes without text_glow (light: on white the halo only blurs the text)."""
        if not self.p['text_glow']:
            return ''
        fid = self.uid('halo')
        self.defs.append(f'<filter id="{fid}" x="-10%" y="-40%" width="120%" height="180%">'
                         f'<feGaussianBlur in="SourceGraphic" stdDeviation="{blur}" result="b"/>'
                         f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
        return f' filter="url(#{fid})"'

    def panel(self, x: float, y: float, w: float, h: float, *, rx: float = 14, glow: bool = True) -> None:
        p = self.p
        if glow and p['glow']:
            fid = self.glow_filter(18)
            self.add(f'<rect x="{x + 10}" y="{y + 14}" width="{w - 20}" height="{h - 20}" rx="{rx}" fill="{p["accent"]}" '
                     f'opacity="{p["glow"]}" filter="url(#{fid})"/>')
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{p["panel"]}"/>')

    def panel_border(self, x: float, y: float, w: float, h: float, *, rx: float = 14) -> None:
        self.add(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="{rx}" '
                 f'stroke="{self.p["line"]}"/>')

    def window(self, x: float, y: float, w: float, h: float, title: str, *, bar: float = 40) -> float:
        """Terminal window like on insighteo.pl. Returns the y where the body starts."""
        p = self.p
        self.panel(x, y, w, h)
        clip = self.uid('bar')
        self.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/></clipPath>')
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{bar}" fill="{p["bar"]}" clip-path="url(#{clip})"/>',
                 f'<line x1="{x}" y1="{y + bar}" x2="{x + w}" y2="{y + bar}" stroke="{p["line_soft"]}"/>')
        for i in range(3):
            self.add(f'<circle cx="{x + 22 + i * 16}" cy="{y + bar / 2}" r="5" fill="{p["accent"]}" opacity="0.35"/>')
        self.add(self.text(x + 78, y + bar / 2 + 4.5, title, 'mono-400', 13, p['muted']))
        self.panel_border(x, y, w, h)
        return y + bar

    def check(self, x: float, y: float, s: float, color: str, extra: str = '') -> str:
        """Check mark (the ✓ of the insighteo.pl terminals; Plex subsets have no such glyph). (x, y) = baseline-left."""
        return (f'<path d="M{x:.1f} {y - s * 0.42:.1f}l{s * 0.3:.1f} {s * 0.3:.1f}l{s * 0.52:.1f} {-s * 0.62:.1f}" '
                f'stroke="{color}" stroke-width="{max(1.6, s * 0.13):.1f}" stroke-linecap="round" '
                f'stroke-linejoin="round"{extra}/>')

    def arrow(self, x: float, y: float, s: float, color: str, extra: str = '') -> str:
        m = y - s * 0.32
        return (f'<path d="M{x:.1f} {m:.1f}h{s * 0.78:.1f}M{x + s * 0.48:.1f} {m - s * 0.28:.1f}l{s * 0.3:.1f} '
                f'{s * 0.28:.1f}l{-s * 0.3:.1f} {s * 0.28:.1f}" stroke="{color}" stroke-width="{max(1.6, s * 0.12):.1f}" '
                f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    def spinner(self, x: float, y: float, s: float, color: str, extra: str = '') -> str:
        """Braille spinner ⠿ drawn as 2x3 dots that blink in turn."""
        r, dx, dy = s * 0.075, s * 0.26, s * 0.22
        order = [0, 1, 2, 5, 4, 3]
        dots = []
        for i, (cx, cy) in enumerate([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]):
            k = order.index(i)
            dots.append(f'<circle class="spin" style="animation-delay:{k * 0.12:.2f}s" cx="{x + s * 0.18 + cx * dx:.1f}" '
                        f'cy="{y - s * 0.62 + cy * dy:.1f}" r="{r:.1f}" fill="{color}"/>')
        return f'<g{extra}>{"".join(dots)}</g>'


# ---- writing -----------------------------------------------------------------------------------------------------

# Dark is the default; light only when the <img> (or the OS, where the browser has nothing better) says light.
THEME_SWITCH = ('.theme-light{display:none}'
                '@media (prefers-color-scheme: light){.theme-dark{display:none}.theme-light{display:inline}}')


def _render(head: Svg, parts: list[Svg]) -> str:
    fonts = ''.join(_font_face(f) for f in sorted(set().union(*(s.fonts for s in parts))))
    css = ''.join(dict.fromkeys(c for s in parts for c in s.css))  # shared rules (BASE_CSS) only once
    reduce = '@media (prefers-reduced-motion: reduce){*{animation:none!important}}'
    if len(parts) == 1:
        body = ''.join(head.body)
    else:
        css += THEME_SWITCH
        body = ''.join(f'<g class="theme-{s.theme}">{"".join(s.body)}</g>' for s in parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {head.w:g} {head.h:g}" width="{head.w:g}" '
            f'height="{head.h:g}" role="img" aria-labelledby="title" fill="none">'
            f'<title id="title">{esc(head.title)}</title>'
            f'<style>{fonts}{css}{reduce}</style>'
            f'<defs>{"".join(d for s in parts for d in s.defs)}</defs>'
            f'{body}</svg>\n')


def _write(name: str, text: str) -> Path:
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / name
    path.write_text(text, encoding='utf-8')
    return path


def save_themed(name: str, dark: Svg, light: Svg) -> Path:
    """One file, both themes (see "Theme rule" at the top). Same size and title expected from both."""
    assert (dark.theme, light.theme) == ('dark', 'light') and (dark.w, dark.h) == (light.w, light.h)
    return _write(name, _render(dark, [dark, light]))
