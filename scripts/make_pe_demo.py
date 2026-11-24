"""Animated demo of the Pricing-Engine app for its project card (zlecenie 593): shots/pricing-engine-demo.svg.

The demo is an illustration made of screenshots of the real app (Pricing-Engine 1.1.0, Dash and Mantine, the
fictional shop Lumo), not a recording. One loop of about 15 s, in the pace of the Data-Generator card:
the page scrolls from the top to the rules, the cursor drags the competitor limit from +5% to +10% and the largest
price step from 10% to 15% (the value next to each slider follows the drag, the headline numbers change after the
release, like the app's updatemode "mouseup"), the page scrolls to the proposals, the cursor shows the lowered
prices and opens the Categories tab, whose bar charts grow in, the page scrolls through both charts and back up.

Input: a folder from Office/scratch/profile-pe-animation/dynamic/capture.mjs: full-page PNGs of the app 960 CSS px
wide at device scale factor 2 in each state and geometry.json (boxes of the sliders, numbers, tabs and charts).
Output: the SVG in the layout of the project's own README demo (a 1000 px page under a 36 px browser bar, classes
m1, m2, ..., CSS animations of transform and opacity only, no script), so build.py's demo_page() places it.

Needs Pillow (not the standard library), unlike build.py.

Usage: python scripts/make_pe_demo.py <capture-folder> [--quality 70] [--res 0.75]
(--res: image px per page px; 0.75 keeps the card near the size of the Data-Generator card.)
"""
from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'shots' / 'pricing-engine-demo.svg'
CSS_W = 960  # CSS px of the app page
W = 1000  # px of the demo page
K = W / CSS_W
BAR = 36  # the demo's own browser bar (build.py drops it)
VIEW = 640  # CSS px of the page in view
EASE = 'cubic-bezier(.65,0,.35,1)'
EASE_OUT = 'cubic-bezier(.22,1,.36,1)'
INK = '#14232a'
CURSOR = 'M0 0V17.2L4.3 13.3L7.2 20.1L10.3 18.8L7.5 12.2H13.2Z'  # arrow, tip at 0,0 (as in the README demo)

# Timeline (seconds). Scroll positions in CSS px of the page.
T = 14.5
Y_TOP, Y_RULES, Y_TABLE, Y_CHARTS = 0, 610, 1130, 1720
SCROLL = [(0, Y_TOP), (0.7, Y_TOP), (1.8, Y_RULES), (6.2, Y_RULES), (7.3, Y_TABLE), (10.6, Y_TABLE),
          (11.8, Y_CHARTS), (13.0, Y_CHARTS), (T, Y_TOP)]
PRESS_ABOVE, RELEASE_ABOVE = 2.35, 3.35
PRESS_STEP, RELEASE_STEP = 4.2, 5.2
LAG = 0.3  # the app recalculates after the release
CLICK_LOWER, CLICK_CATEGORIES = 7.75, 8.95
GROW = [(9.2, 10.0), (11.3, 12.1)]  # the two category charts grow in
FINAL = 5.9  # the point of the loop shown without motion (prefers-reduced-motion): both rules moved, new numbers
DRAGS = {'above': [(0, 5), (PRESS_ABOVE, 5), (RELEASE_ABOVE, 10)],
         'step': [(0, 10), (PRESS_STEP, 10), (RELEASE_STEP, 15)]}


class Motion:
    """CSS keyframes on one timeline. Each track: (seconds, value, easing to the next stop)."""

    def __init__(self, total: float):
        self.total = total
        self.css: list[str] = []
        self.count = 0

    def track(self, prop: str, stops: list, rest) -> str:
        self.count += 1
        name = f'm{self.count}'
        stops = sorted(stops, key=lambda s: s[0])
        if stops[0][0] > 0:
            stops.insert(0, (0, stops[0][1], 'linear'))
        if stops[-1][0] < self.total:
            stops.append((self.total, stops[-1][1], 'linear'))
        frames = ''.join(f'{s / self.total * 100:.3f}%{{{prop}:{value};animation-timing-function:{ease}}}'
                         for s, value, ease in stops)
        self.css.append(f'@keyframes {name}{{{frames}}}.{name}{{{prop}:{rest};'
                        f'animation:{name} {self.total:g}s linear 0s infinite both}}')
        return name


def ease_io(u: float) -> float:
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def path_value(stops: list[tuple[float, float]], t: float) -> float:
    """Value at time t of a path through (time, value) stops, eased between them and held outside."""
    if t <= stops[0][0]:
        return stops[0][1]
    for (t0, v0), (t1, v1) in zip(stops, stops[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * ease_io((t - t0) / (t1 - t0)) if t1 > t0 else v1
    return stops[-1][1]


def tr(x: float, y: float) -> str:
    return f'translate({x:.1f}px,{y:.1f}px)'


def hex_color(css: str) -> str:
    parts = [int(float(p)) for p in css[css.index('(') + 1:css.index(')')].split(',')[:3]]
    return '#{:02x}{:02x}{:02x}'.format(*parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('shots', type=Path)
    ap.add_argument('--quality', type=int, default=70)
    ap.add_argument('--res', type=float, default=0.75, help='image px per page px')
    a = ap.parse_args()
    geo = json.loads((a.shots / 'geometry.json').read_text(encoding='utf-8'))
    base, bold, cats = geo['base'], geo['step-15'], geo['bold-categories']
    images = {name: Image.open(a.shots / f'{name}.png').convert('RGB') for name in geo}
    for name, im in images.items():
        assert im.width == CSS_W * 2, f'{name}: not 960 CSS px at device scale factor 2'

    def image(name: str, x0: float, y0: float, x1: float, y1: float) -> str:
        """Part of a screenshot (CSS px box) as a WebP <image> in page px."""
        crop = images[name].crop((round(x0 * 2), round(y0 * 2), round(x1 * 2), round(y1 * 2)))
        size = (max(1, round((x1 - x0) * K * a.res)), max(1, round((y1 - y0) * K * a.res)))
        buf = io.BytesIO()
        crop.resize(size, Image.LANCZOS).save(buf, 'WEBP', quality=a.quality, method=6)
        data = base64.b64encode(buf.getvalue()).decode()
        return (f'<image x="{x0 * K:.2f}" y="{y0 * K:.2f}" width="{(x1 - x0) * K:.2f}" height="{(y1 - y0) * K:.2f}" '
                f'preserveAspectRatio="none" href="data:image/webp;base64,{data}"/>')

    def switch_on(t: float, fade: float = 0.22) -> list:
        """Opacity: hidden until t, then shown to the end of the loop (the loop starts hidden again)."""
        return [(0, 0, 'linear'), (t, 0, EASE), (t + fade, 1, 'linear')]

    m = Motion(T)
    page: list[str] = []  # in CSS px * K, moved by the scroll
    view: list[str] = []  # fixed in the view: cursor, click rings, scrollbar

    # 1. the page: base rules down to the numbers, below them the proposals after the new rules
    split = Y_RULES + VIEW + 4
    page.append(image('base', 0, 0, CSS_W, split))
    page.append(image('step-15', 0, split, CSS_W, Y_TABLE + VIEW + 4))
    # the headline numbers after each release
    s = base['stats']
    for name, t in (('above-10', RELEASE_ABOVE + LAG), ('step-15', RELEASE_STEP + LAG)):
        assert geo[name]['stats'] == s, 'the numbers moved'
        page.append(f'<g class="{m.track("opacity", switch_on(t), 1)}">'
                    f'{image(name, s["x"] - 4, s["y"] - 4, s["x"] + s["w"] + 4, s["y"] + s["h"] + 4)}</g>')
    # the proposals of the lowered prices, then the Categories tab with its charts
    prop = bold['proposals']
    page.append(f'<g class="{m.track("opacity", switch_on(CLICK_LOWER + 0.2), 0)}">'
                f'{image("bold-lower", 0, prop["y"] - 6, CSS_W, Y_TABLE + VIEW + 4)}</g>')
    tabs = cats['view']
    grow = []
    for (t0, t1), plot in zip(GROW, cats['plots']):
        p = plot['plot']
        x0, x1 = plot['zero'] + 1.5, p['x'] + p['w']
        cls = m.track('transform', [(0, 'scaleX(1)', 'linear'), (t0, 'scaleX(1)', EASE_OUT), (t1, 'scaleX(0)', 'linear')],
                      'scaleX(0)')
        # anchored at the right edge: shrinking to it uncovers the bars from zero outwards, as if they grew
        grow.append(f'<g transform="translate({x1 * K:.2f} {p["y"] * K:.2f})"><rect class="{cls}" '
                    f'x="{-(x1 - x0) * K:.2f}" width="{(x1 - x0) * K:.2f}" height="{p["h"] * K:.2f}" fill="#ffffff"/></g>')
    page.append(f'<g class="{m.track("opacity", switch_on(CLICK_CATEGORIES + 0.15, 0.18), 0)}">'
                f'{image("bold-categories", 0, tabs["y"] - 4, CSS_W, cats["height"])}{"".join(grow)}</g>')

    # 2. the two sliders: a patch over each, then track, bar and thumb as vectors moving with the drag
    times = [round(i / 50, 2) for i in range(int(T * 50) + 1)]
    thumbs = {}
    for rule, stops in DRAGS.items():
        r = base['rules'][rule]
        tx, tw = r['track']['x'], r['track']['w']
        cy = r['thumb']['y'] + r['thumb']['h'] / 2
        radius = r['thumb']['w'] / 2
        bar_x, end = r['bar']['x'], tx + tw + radius
        line_h = r['bar']['h']

        def x_of(v: float, r=r, tx=tx, tw=tw) -> float:
            return tx + (v - r['min']) / (r['max'] - r['min']) * tw

        page.append(f'<rect x="{(bar_x - 8) * K:.2f}" y="{(cy - radius - 4) * K:.2f}" '
                    f'width="{(end - bar_x + 16) * K:.2f}" height="{(2 * radius + 8) * K:.2f}" fill="#ffffff"/>')
        bar = f'y="{(cy - line_h / 2) * K:.2f}" height="{line_h * K:.2f}" rx="{line_h * K / 2:.2f}"'
        full = end - bar_x
        page.append(f'<rect x="{bar_x * K:.2f}" width="{full * K:.2f}" {bar} '
                    f'fill="{hex_color(r["track_style"]["background"])}"/>')
        moving = [t for t in times if stops[1][0] <= t <= stops[2][0]]
        keys = sorted({0.0, T, *[t for t, _ in stops], *moving})
        rest_x = x_of(stops[0][1])
        final_x = x_of(stops[-1][1])  # rest = the final point (both rules moved)
        fill = m.track('transform', [(t, f'scaleX({(x_of(path_value(stops, t)) + radius - bar_x) / full:.4f})', 'linear')
                                     for t in keys], f'scaleX({(final_x + radius - bar_x) / full:.4f})')
        page.append(f'<g transform="translate({bar_x * K:.2f} 0)"><rect class="{fill}" width="{full * K:.2f}" {bar} '
                    f'fill="{hex_color(r["bar_style"]["background"])}"/></g>')
        move = m.track('transform', [(t, tr((x_of(path_value(stops, t)) - rest_x) * K, 0), 'linear') for t in keys],
                       tr((final_x - rest_x) * K, 0))
        ts = r['thumb_style']
        ring = ts['border_width']
        page.append(f'<g class="{move}"><circle cx="{rest_x * K:.2f}" cy="{cy * K:.2f}" r="{(radius - ring / 2) * K:.2f}" '
                    f'fill="{hex_color(ts["background"])}" stroke="{hex_color(ts["border"])}" '
                    f'stroke-width="{ring * K:.2f}"/></g>')
        # the value next to the label follows the drag: one screenshot crop per whole value, the first is the page's
        lo, hi = stops[0][1], stops[-1][1]
        name = {'above': lambda v: f'above-{v}', 'step': lambda v: f'step-{v}'}[rule]
        widest = max(geo[name(v)]['rules'][rule]['value']['w'] for v in range(lo + 1, hi + 1))
        vb = r['value']
        right = vb['x'] + vb['w']
        for v in range(lo + 1, hi + 1):
            assert geo[name(v)]['rules'][rule]['value_text'].strip('+%') == str(v)
            on = [round(path_value(stops, t) + 1e-9) == v for t in times]
            track = [(0, int(on[0]), 'linear')]
            for i in range(1, len(times)):
                if on[i] != on[i - 1]:
                    track += [(times[i] - 0.001, int(on[i - 1]), 'linear'), (times[i], int(on[i]), 'linear')]
            page.append(f'<g class="{m.track("opacity", track, int(v == hi))}">'
                        f'{image(name(v), right - widest - 6, vb["y"] - 3, right + 3, vb["y"] + vb["h"] + 3)}</g>')
        thumbs[rule] = lambda v, x_of=x_of, cy=cy: (x_of(v), cy)

    # 3. the scroll: the page glides between the views, a scrollbar thumb follows
    scroll_stops = [(t, y, EASE if i + 1 < len(SCROLL) and SCROLL[i + 1][1] != y else 'linear')
                    for i, (t, y) in enumerate(SCROLL)]
    scroll = m.track('transform', [(t, tr(0, -y * K), e) for t, y, e in scroll_stops], tr(0, -Y_RULES * K))
    height = cats['height']
    thumb_h = VIEW * VIEW / height
    room = VIEW - thumb_h - 6

    def thumb_y(y: float) -> float:
        return y / (height - VIEW) * room

    bar = m.track('transform', [(t, tr(0, thumb_y(y) * K), e) for t, y, e in scroll_stops], tr(0, thumb_y(Y_RULES) * K))
    view.append(f'<rect class="{bar}" x="{(CSS_W - 7) * K:.2f}" y="{3 * K:.2f}" width="{4 * K:.2f}" '
                f'height="{thumb_h * K:.2f}" rx="{2 * K:.2f}" fill="{INK}" opacity="0.28"/>')

    # 4. the cursor (view coordinates): rest, drag one rule, drag the other, "lower", "Categories", rest
    def at_view(xy: tuple[float, float], y_scroll: float) -> tuple[float, float]:
        return xy[0], xy[1] - y_scroll

    def centre(b: dict, y_scroll: float) -> tuple[float, float]:
        return b['x'] + b['w'] / 2, b['y'] + b['h'] / 2 - y_scroll

    rest = (720, 400)
    grab1 = at_view(thumbs['above'](5), Y_RULES)
    grab2 = at_view(thumbs['step'](10), Y_RULES)
    lower = centre(base['show_segments']['lower'], Y_TABLE)
    categories = centre(base['view_segments']['Categories'], Y_TABLE)
    path = [(0, rest, 'linear'), (1.6, rest, EASE), (PRESS_ABOVE - 0.12, grab1, 'linear')]
    path += [(t, at_view(thumbs['above'](path_value(DRAGS['above'], t)), Y_RULES), 'linear')
             for t in times if PRESS_ABOVE <= t <= RELEASE_ABOVE]
    path += [(3.55, at_view(thumbs['above'](10), Y_RULES), EASE), (PRESS_STEP - 0.12, grab2, 'linear')]
    path += [(t, at_view(thumbs['step'](path_value(DRAGS['step'], t)), Y_RULES), 'linear')
             for t in times if PRESS_STEP <= t <= RELEASE_STEP]
    path += [(7.05, at_view(thumbs['step'](15), Y_RULES), EASE), (CLICK_LOWER - 0.1, lower, 'linear'),
             (8.35, lower, EASE), (CLICK_CATEGORIES - 0.1, categories, 'linear'),
             (12.4, categories, EASE), (13.6, rest, 'linear')]
    cursor_move = m.track('transform', [(t, tr(x * K, y * K), e) for t, (x, y), e in path], tr(rest[0] * K, rest[1] * K))
    cursor_show = m.track('opacity', [(0, 1, 'linear')], 0)
    press = [(0, 'scale(1)', 'linear')]
    for down, up in ((PRESS_ABOVE, RELEASE_ABOVE), (PRESS_STEP, RELEASE_STEP), (CLICK_LOWER, CLICK_LOWER + 0.12),
                     (CLICK_CATEGORIES, CLICK_CATEGORIES + 0.12)):
        press += [(down - 0.08, 'scale(1)', EASE_OUT), (down, 'scale(.88)', 'linear'), (up, 'scale(.88)', EASE_OUT),
                  (up + 0.18, 'scale(1)', 'linear')]
    cursor_press = m.track('transform', press, 'scale(1)')
    for t0, (x, y) in ((PRESS_ABOVE, grab1), (PRESS_STEP, grab2), (CLICK_LOWER, lower),
                       (CLICK_CATEGORIES, categories)):
        ring = m.track('transform', [(t0, 'scale(.2)', EASE_OUT), (t0 + 0.5, 'scale(1)', 'linear'),
                                     (t0 + 0.51, 'scale(.2)', 'linear')], 'scale(1)')
        fade = m.track('opacity', [(t0 - 0.01, 0, 'linear'), (t0, 0.45, EASE_OUT), (t0 + 0.5, 0, 'linear')], 0)
        view.append(f'<g transform="translate({x * K:.1f} {y * K:.1f})"><g class="{fade}"><circle class="{ring}" r="18" '
                    f'fill="{hex_color(base["rules"]["above"]["bar_style"]["background"])}" fill-opacity="0.35"/></g></g>')
    view.append(f'<g class="{cursor_show}"><g class="{cursor_move}"><g class="{cursor_press}">'
                f'<path d="{CURSOR}" transform="scale(1.15)" fill="{INK}" stroke="#ffffff" stroke-width="1.3" '
                f'stroke-linejoin="round" filter="url(#shadow)"/></g></g></g>')

    first, last = base['stat_values'], bold['stat_values']
    alt = (f'Pricing Engine app, illustrated: the competitor limit is dragged from +5% to +10% and the largest price '
           f'step from 10% to 15%, yearly gross profit moves from {first[0]} to {last[0]} PLN, then the lowered '
           f'prices and the profit change per category.')
    vh = VIEW * K
    H = BAR + vh
    css = ''.join(m.css) + '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" '
           f'role="img" aria-label="{alt}"><title>{alt}</title><defs><style>{css}</style>'
           f'<clipPath id="frame"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1:.1f}" rx="10"/></clipPath>'
           f'<clipPath id="view"><rect x="0" y="{BAR}" width="{W}" height="{vh:.1f}"/></clipPath>'
           f'<filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="1.2" '
           f'stdDeviation="1.4" flood-color="#000" flood-opacity="0.35"/></filter></defs>'
           f'<g clip-path="url(#frame)"><rect width="{W}" height="{H:.1f}" fill="#ffffff"/>'
           f'<g clip-path="url(#view)"><g transform="translate(0 {BAR})"><g class="{scroll}">{"".join(page)}</g>'
           f'{"".join(view)}</g></g>'
           f'<rect width="{W}" height="{BAR}" fill="#f6f8fa"/>'
           f'<line x1="0" y1="{BAR - 0.5}" x2="{W}" y2="{BAR - 0.5}" stroke="#d0d7de"/></g>'
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1:.1f}" rx="10" fill="none" stroke="#d0d7de"/></svg>')
    OUT.write_text(svg, encoding='utf-8', newline='\n')
    print(f'{OUT.name}: {OUT.stat().st_size / 1024:.0f} KB, loop {T:g} s, {m.count} animated classes, '
          f'final {FINAL / T:.4f}')


if __name__ == '__main__':
    main()
