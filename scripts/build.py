"""Static profile graphics: banner, agents terminal, stack modules, career graph, projects.

Every graphic is one SVG with a dark and a light version inside (svgkit.save_themed: the SVG follows the theme
GitHub paints), plus a narrow file for phones (README.md picks it with <picture> by width only). Texts follow insighteo.pl (src/i18n/content.ts, EN), shortened.
Rules from insighteo.pl: no employer or client names, no figures for results, no "—" or "–".

Usage: python scripts/build.py
"""
from __future__ import annotations

import base64
import random

from icons import ICONS
from svgkit import ROOT, Svg, esc, save_themed, width, wrap

NAME = 'Tomasz Łabędzki'
ROLE = 'Analytics Engineer · AI Engineer · Data Analyst'
TAGLINE = 'I build tools that turn data into decisions.'

BASE_CSS = (
    '@keyframes in{from{opacity:0}to{opacity:1}}'
    '@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}'
    '@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}'
    '@keyframes spin{0%,100%{opacity:.25}20%{opacity:1}}'
    '@keyframes run{0%,99%{opacity:1}100%{opacity:0}}'
    '.in{animation:in .01s both}'
    '.up{animation:up .6s cubic-bezier(.2,.7,.2,1) both}'
    '.spin{animation:spin .72s linear infinite}'
)


def typed(svg: Svg, x: float, y: float, s: str, face: str, size: float, fill: str, start: float, step: float,
          *, extra: str = '') -> tuple[str, float, list[float]]:
    """Text revealed glyph by glyph. Returns markup, end time and the x after every glyph (for a caret)."""
    out, cx, xs = [], x, []
    for i, ch in enumerate(s):
        if ch != ' ':
            out.append(f'<tspan x="{cx:.1f}" class="in" style="animation-delay:{start + i * step:.2f}s">{esc(ch)}</tspan>')
        cx += width(ch, face, size)
        xs.append(cx)
    tag = (f'<text y="{y:.1f}" style="{svg.font(face)};font-size:{size}px" fill="{fill}"{extra}>'
           f'{"".join(out)}</text>')
    return tag, start + len(s) * step, xs


def caret(svg: Svg, x0: float, y: float, h: float, xs: list[float], start: float, step: float, color: str,
          w: float = 3) -> str:
    """Caret that follows typed text, then blinks. Without motion it rests after the last glyph."""
    name = svg.uid('caret')
    n = len(xs)
    frames = ''.join(f'{(i + 1) / n * 100:.2f}%{{transform:translateX({xs[i] - x0:.1f}px)}}' for i in range(n))
    svg.css.append(f'@keyframes {name}{{0%{{transform:translateX(0)}}{frames}}}'
                   f'.{name}{{transform:translateX({xs[-1] - x0 + 4:.1f}px);'
                   f'animation:{name} {n * step:.2f}s step-end {start:.2f}s backwards,'
                   f'blink 1.1s step-end {start + n * step:.2f}s infinite}}')
    return f'<rect class="{name}" x="{x0 + 2:.1f}" y="{y - h * 0.8:.1f}" width="{w}" height="{h:.1f}" fill="{color}"/>'


def rain(svg: Svg, x: float, y: float, w: float, h: float, *, size: float = 15, gap: float = 22,
         seed: int = 7) -> None:
    """Falling glyphs like the background of insighteo.pl (src/components/Rain.astro), as CSS animation."""
    p = svg.p
    rnd = random.Random(seed)
    glyphs = '0123456789%+-<>=/ABCDEFSKU$#'
    lh = size * 1.25
    clip = svg.uid('rainclip')
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/></clipPath>')
    cols = []
    for i in range(int(w // gap)):
        n = rnd.randint(6, 16)
        cx = x + 8 + i * gap
        y0 = y + rnd.uniform(-n * lh * 0.5, h - n * lh * 0.4)
        name = svg.uid('r')
        dur = rnd.uniform(7, 15)
        a, b = -(y0 - y) - n * lh, h + y - y0
        svg.css.append(f'@keyframes {name}{{from{{transform:translateY({a:.0f}px)}}to{{transform:translateY({b:.0f}px)}}}}'
                       f'.{name}{{animation:{name} {dur:.1f}s linear {-rnd.uniform(0, dur):.1f}s infinite}}')
        spans = []
        for k in range(n):
            head = k == n - 1
            op = p['rain_head_opacity'] if head else (k + 1) / n * p['rain_opacity']
            color = p['rain_head'] if head else p['rain']
            spans.append(f'<tspan x="{cx:.0f}" y="{k * lh:.0f}" fill="{color}" opacity="{op:.2f}">'
                         f'{esc(rnd.choice(glyphs))}</tspan>')
        cols.append(f'<g transform="translate(0 {y0:.0f})"><g class="{name}"><text style="{svg.font("mono-400")};'
                    f'font-size:{size}px">{"".join(spans)}</text></g></g>')
    svg.add(f'<g clip-path="url(#{clip})">{"".join(cols)}</g>')


def hud_corners(svg: Svg, x: float, y: float, w: float, h: float, inset: float = 18, arm: float = 22) -> None:
    c = svg.p['accent']
    pts = [(x + inset, y + inset, 1, 1), (x + w - inset, y + inset, -1, 1),
           (x + inset, y + h - inset, 1, -1), (x + w - inset, y + h - inset, -1, -1)]
    for px, py, sx, sy in pts:
        svg.add(f'<path d="M{px} {py + sy * arm}V{py}H{px + sx * arm}" stroke="{c}" stroke-width="2" opacity="0.7"/>')


# ---- 1. banner ---------------------------------------------------------------------------------------------------

def banner(theme: str, narrow: bool) -> Svg:
    W, H = (440, 440) if narrow else (960, 360)
    svg = Svg(W, H, theme, f'{NAME}: {ROLE}. {TAGLINE}')
    p = svg.p
    svg.css.append(BASE_CSS)
    x, y, w, h = 12, 12, W - 24, H - 30
    svg.panel(x, y, w, h, rx=16)
    svg.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{p["bg"]}"/>')
    rain(svg, x, y, w, h, size=14 if narrow else 15, gap=17 if narrow else 19)
    veil = svg.uid('veil')
    svg.defs.append(f'<radialGradient id="{veil}" cx="50%" cy="50%" r="62%">'
                    f'<stop offset="0" stop-color="{p["veil"]}" stop-opacity="0.95"/>'
                    f'<stop offset="0.45" stop-color="{p["veil"]}" stop-opacity="0.86"/>'
                    f'<stop offset="0.8" stop-color="{p["veil"]}" stop-opacity="0.35"/>'
                    f'<stop offset="1" stop-color="{p["veil"]}" stop-opacity="0"/></radialGradient>')
    svg.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="url(#{veil})"/>')
    # scan beam sweeping down
    beam = svg.uid('beam')
    svg.defs.append(f'<linearGradient id="{beam}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["accent"]}" '
                    f'stop-opacity="0"/><stop offset="0.9" stop-color="{p["accent"]}" stop-opacity="0.05"/>'
                    f'<stop offset="1" stop-color="{p["accent"]}" stop-opacity="0.16"/></linearGradient>')
    clip = svg.uid('bclip')
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/></clipPath>')
    svg.css.append(f'@keyframes sweep{{0%{{transform:translateY(-90px)}}55%,100%{{transform:translateY({H + 10}px)}}}}'
                   f'.beam{{transform:translateY(-90px);animation:sweep 9s cubic-bezier(.5,0,.5,1) 4s infinite}}')
    svg.add(f'<g clip-path="url(#{clip})"><rect class="beam" x="{x}" y="0" width="{w}" height="80" fill="url(#{beam})"/></g>')
    hud_corners(svg, x, y, w, h)
    svg.panel_border(x, y, w, h, rx=16)

    cx = W / 2
    prompt_size, name_size, role_size, tag_size = (13, 42, 13.5, 17) if narrow else (15, 64, 18, 21)
    ys = (100, 182, 226, 266, 334) if narrow else (96, 180, 224, 262, 308)
    # prompt line
    prompt = 'insighteo@command-center:~$ whoami'
    px = cx - width(prompt, 'mono-400', prompt_size) / 2
    tag, t_end, _ = typed(svg, px, ys[0], prompt, 'mono-400', prompt_size, p['accent'], 0.3, 0.03)
    svg.add(tag)
    # name typed glyph by glyph, caret follows
    halo = svg.text_glow(10)
    nx = cx - width(NAME, 'sans-600', name_size) / 2
    start, step = t_end + 0.35, 0.085
    tag, n_end, xs = typed(svg, nx, ys[1], NAME, 'sans-600', name_size, p['ink'], start, step,
                           extra=f'{halo} letter-spacing="0"')
    svg.add(tag, caret(svg, nx, ys[1], name_size * 0.95, xs, start, step, p['accent'], w=4 if not narrow else 3))
    # role and tagline
    svg.add(svg.text(cx, ys[2], ROLE, 'mono-400', role_size, p['accent'], anchor='middle', cls='up',
                     style=f'animation-delay:{n_end + 0.2:.2f}s'))
    lines = wrap(TAGLINE, 'sans-400', tag_size, w - 60)
    for i, line in enumerate(lines):
        svg.add(svg.text(cx, ys[3] + i * tag_size * 1.35, line, 'sans-400', tag_size, p['soft'], anchor='middle',
                         cls='up', style=f'animation-delay:{n_end + 0.45:.2f}s'))
    # status pill
    label = 'open to projects'
    site = 'insighteo.pl'
    pill_size = 13 if narrow else 14
    tw = width(label, 'mono-400', pill_size)
    sw = width(site, 'mono-400', pill_size)
    pw = 34 + tw + 26 + sw + 18
    pxl = cx - pw / 2
    py = ys[4] + (len(lines) - 1) * tag_size * 1.35 * (1 if narrow else 0)
    svg.css.append('@keyframes ping{0%{r:4px;opacity:.8}100%{r:11px;opacity:0}}'
                   '.ping{animation:ping 1.8s ease-out 0s infinite;opacity:0}')
    svg.add(f'<g class="up" style="animation-delay:{n_end + 0.7:.2f}s">'
            f'<rect x="{pxl:.1f}" y="{py - 21}" width="{pw:.1f}" height="32" rx="16" fill="{p["accent2"]}" '
            f'fill-opacity="0.10" stroke="{p["accent2"]}" stroke-opacity="0.45"/>'
            f'<circle class="ping" cx="{pxl + 18:.1f}" cy="{py - 5}" r="4" fill="{p["accent2"]}"/>'
            f'<circle cx="{pxl + 18:.1f}" cy="{py - 5}" r="4" fill="{p["accent2"]}"/>'
            + svg.text(pxl + 32, py, label, 'mono-400', pill_size, p['accent2'])
            # the dot sits midway between the inks of 's' and 'i', not their advance boxes: in Plex Mono 's' ends
            # 0.076 em before its box, 'i' starts 0.106 em into its box and '·' is centred in its own box
            + svg.text(pxl + 32 + tw + 13 + pill_size * (0.106 - 0.076) / 2, py, '·', 'mono-400', pill_size,
                       p['muted'], anchor='middle')
            + svg.text(pxl + 32 + tw + 26, py, site, 'mono-400', pill_size, p['ink'])
            + '</g>')
    return svg


# ---- 2. agents terminal ------------------------------------------------------------------------------------------

AGENTS = [
    ('decisions', 'pricing, purchasing and margin tools'),
    ('pipelines', 'integrations, warehouse and data models'),
    ('ai', 'ML models, LLM integrations and AI agents'),
    ('reports', 'Power BI and automated reporting'),
    ('apps', 'web apps from requirements to deployment'),
]


def agents(theme: str, narrow: bool) -> Svg:
    W = 440 if narrow else 960
    size = 14 if narrow else 16.5
    lh = size * 1.75
    pad = 20 if narrow else 30
    rows = 2 + (len(AGENTS) * (2 if narrow else 1)) + (4 if narrow else 2) + 1
    H = 40 + 26 + rows * lh + 40
    alt = ('Terminal: agents start and report what Tomasz does: ' +
           '; '.join(f'{a}: {d}' for a, d in AGENTS) +
           '. Delivers from a conversation about the problem to a deployed tool. Status: open to projects.')
    svg = Svg(W, H, theme, alt)
    p = svg.p
    svg.css.append(BASE_CSS)
    x, y, w, h = 12, 12, W - 24, H - 30
    top = svg.window(x, y, w, h, 'tomasz@insighteo: ~')
    tx = x + pad
    ty = top + 26 + size
    cw = width('m', 'mono-400', size)
    # command typed
    svg.add(svg.text(tx, ty, '$', 'mono-400', size, p['accent']))
    cmd = 'insighteo agents run --profile tomasz'
    tag, t, _ = typed(svg, tx + cw * 2, ty, cmd, 'mono-400', size, p['ink'], 0.4, 0.03)
    svg.add(tag)
    t += 0.3
    ty += lh
    loaded = wrap('profile loaded: data, automation and AI for business', 'mono-400', size, w - pad * 2 - cw * 2)
    svg.add(f'<g class="in" style="animation-delay:{t:.2f}s">' + svg.check(tx + 1, ty, size, p['accent2'])
            + ''.join(svg.text(tx + cw * 2, ty + k * lh, line, 'mono-400', size, p['accent2'])
                      for k, line in enumerate(loaded)) + '</g>')
    ty += lh * (len(loaded) - 1)
    name_w = max(len(f'agent:{a}') for a, _ in AGENTS) + 2
    for i, (agent, desc) in enumerate(AGENTS):
        t_show = t + 0.45 + i * 0.32
        t_done = t_show + 1.1 + i * 0.12
        ty += lh
        label = f'agent:{agent}'
        g = [svg.spinner(tx, ty, size, p['amber'],
                         extra=f' class="runbox" style="animation:run {t_done - t_show:.2f}s step-end {t_show:.2f}s both;opacity:0"'),
             svg.check(tx + 1, ty, size, p['accent2'], extra=f' class="in" style="animation-delay:{t_done:.2f}s"'),
             svg.text(tx + cw * 2, ty, label, 'mono-600', size, p['amber'])]
        dy = ty
        if narrow:
            dy = ty + lh * 0.92
            ty = dy
            dx = tx + cw * 4
        else:
            dx = tx + cw * (2 + name_w)
        g.append(svg.text(dx, dy, desc, 'mono-400', size, p['text']))
        # status at the right: running, then done
        if not narrow:
            rx = x + w - pad
            g.append(svg.text(rx, ty, 'running', 'mono-400', size * 0.85, p['amber'], anchor='end',
                              style=f'animation:run {t_done - t_show:.2f}s step-end {t_show:.2f}s both;opacity:0'))
            g.append(svg.text(rx, ty, 'done', 'mono-400', size * 0.85, p['accent2'], anchor='end', cls='in',
                              style=f'animation-delay:{t_done:.2f}s'))
        svg.add(f'<g class="up" style="animation-delay:{t_show:.2f}s">{"".join(g)}</g>')
    t_end = t + 0.45 + (len(AGENTS) - 1) * 0.32 + 1.1 + (len(AGENTS) - 1) * 0.12 + 0.35
    # outcome lines
    halo = svg.text_glow(6)
    ty += lh * 1.25
    deliver = 'deliver: from a conversation about the problem to a deployed tool'
    lines = wrap(deliver, 'mono-400', size, w - pad * 2 - cw * 2)
    g = [svg.arrow(tx, ty, size, p['bright'])]
    for k, line in enumerate(lines):
        g.append(svg.text(tx + cw * 2, ty + k * lh, line, 'mono-600', size, p['bright'], extra=halo))
    svg.add(f'<g class="up" style="animation-delay:{t_end:.2f}s">{"".join(g)}</g>')
    ty += lh * len(lines)
    svg.add(f'<g class="up" style="animation-delay:{t_end + 0.3:.2f}s">'
            f'<circle cx="{tx + size * 0.4:.1f}" cy="{ty - size * 0.33:.1f}" r="{size * 0.26:.1f}" fill="{p["accent2"]}"/>'
            + svg.text(tx + cw * 2, ty, 'status: open to projects', 'mono-400', size, p['accent2']) + '</g>')
    ty += lh
    svg.add(f'<g class="in" style="animation-delay:{t_end + 0.6:.2f}s">'
            + svg.text(tx, ty, '$', 'mono-400', size, p['accent'])
            + f'<rect x="{tx + cw * 2:.1f}" y="{ty - size * 0.82:.1f}" width="{cw:.1f}" height="{size * 1.05:.1f}" '
              f'fill="{p["accent"]}" style="animation:blink 1.1s step-end {t_end + 0.6:.2f}s infinite"/></g>')
    return svg


# ---- 3. stack modules --------------------------------------------------------------------------------------------

STACK = [
    ('data', [('Python', 'python'), ('SQL', 'SQL'), ('Airflow', 'apacheairflow'), ('dbt', 'dbt'),
              ('BigQuery', 'googlebigquery'), ('PostgreSQL', 'postgresql'), ('Snowflake', 'snowflake')]),
    ('bi', [('Power BI', 'BI'), ('DAX', 'DAX'), ('pandas', 'pandas'), ('Plotly', 'plotly')]),
    ('ml', [('scikit-learn', 'scikitlearn'), ('PyCaret', 'Py')]),
    ('ai', [('OpenAI API', 'AI'), ('Claude Agent SDK', 'claude')]),
    ('apps', [('React', 'react'), ('TypeScript', 'typescript'), ('FastAPI', 'fastapi'), ('SQLAlchemy', 'sqlalchemy'),
              ('SQLite', 'sqlite'), ('Streamlit', 'streamlit'), ('GitHub Actions', 'githubactions')]),
    ('automation', [('Google Apps Script', 'googleappsscript')]),
]


def icon(svg: Svg, key: str, x: float, y: float, s: float) -> str:
    """Brand icon in the accent colour; tools without a Simple Icons entry get a monogram tile of the same size."""
    p = svg.p
    if key in ICONS:
        k = s / 24
        return f'<path transform="translate({x:.1f} {y:.1f}) scale({k:.3f})" d="{ICONS[key]}" fill="{p["accent"]}"/>'
    fs = s * (0.5 if len(key) <= 2 else 0.4)
    return (f'<rect x="{x + 0.75:.1f}" y="{y + 0.75:.1f}" width="{s - 1.5:.1f}" height="{s - 1.5:.1f}" rx="4" '
            f'stroke="{p["accent"]}" stroke-width="1.5"/>'
            + svg.text(x + s / 2, y + s / 2 + fs * 0.36, key, 'mono-600', fs, p['accent'], anchor='middle'))


def stack(theme: str, narrow: bool) -> Svg:
    W = 440 if narrow else 960
    pad = 20 if narrow else 30
    size = 13.5 if narrow else 15
    chip_h = 32 if narrow else 36
    gap = 8 if narrow else 10
    isz = 16 if narrow else 18
    label_w = 0 if narrow else width('modules/automation', 'mono-600', size) + 24
    cw = width('m', 'mono-400', size)
    x0 = 12
    inner = W - 24 - pad * 2
    # layout
    rows, cy = [], 0.0
    head = 26 + size
    cy = head + size * 1.9
    for group, items in STACK:
        if narrow:
            rows.append(('label', group, cy))
            cy += size * 1.5
        cx = label_w
        line_top = cy
        chips = []
        for name, key in items:
            cwid = 12 + isz + 9 + width(name, 'mono-400', size) + 14
            if cx + cwid > inner and cx > label_w:
                cx = label_w
                cy += chip_h + gap
            chips.append((name, key, cx, cy, cwid))
            cx += cwid + gap
        rows.append(('group', group, line_top, chips))
        cy += chip_h + (gap + 12 if narrow else gap + 8)
    foot = cy + size * 1.2
    H = 12 + 40 + foot + 34
    alt = 'Tech stack: ' + '; '.join(f'{g}: ' + ', '.join(n for n, _ in items) for g, items in STACK) + '.'
    svg = Svg(W, H, theme, alt)
    p = svg.p
    svg.css.append(BASE_CSS)
    svg.css.append('@keyframes pulse{0%{opacity:0}3%{opacity:1}10%,100%{opacity:0}}'
                   '.pulse{opacity:0;animation:pulse 9s linear infinite}')
    top = svg.window(x0, 12, W - 24, H - 30, '~/stack')
    bx = x0 + pad
    by = top
    svg.add(svg.text(bx, by + head, '$', 'mono-400', size, p['accent']))
    tag, t, _ = typed(svg, bx + cw * 2, by + head, 'insighteo modules --list', 'mono-400', size, p['ink'], 0.3, 0.03)
    svg.add(tag)
    t += 0.25
    idx = 0
    for row in rows:
        if row[0] == 'label':
            svg.add(svg.text(bx, by + row[2] + size, f'modules/{row[1]}', 'mono-600', size, p['amber'], cls='up',
                             style=f'animation-delay:{t + idx * 0.07:.2f}s'))
            continue
        _, group, ly, chips = row
        if not narrow:
            svg.add(svg.text(bx, by + ly + chip_h / 2 + size * 0.36, f'modules/{group}', 'mono-600', size, p['amber'],
                             cls='up', style=f'animation-delay:{t + idx * 0.07:.2f}s'))
        for name, key, cx, cy, cwid in chips:
            X, Y = bx + cx, by + cy
            d = t + idx * 0.07
            svg.add(f'<g class="up" style="animation-delay:{d:.2f}s">'
                    f'<rect x="{X:.1f}" y="{Y:.1f}" width="{cwid:.1f}" height="{chip_h}" rx="8" fill="{p["bar"]}" '
                    f'stroke="{p["line"]}"/>'
                    f'<rect class="pulse" style="animation-delay:{3 + idx * 0.11:.2f}s" x="{X:.1f}" y="{Y:.1f}" '
                    f'width="{cwid:.1f}" height="{chip_h}" rx="8" stroke="{p["accent"]}" stroke-width="1.5" '
                    f'fill="{p["accent"]}" fill-opacity="0.08"/>'
                    + icon(svg, key, X + 12, Y + (chip_h - isz) / 2, isz)
                    + svg.text(X + 12 + isz + 9, Y + chip_h / 2 + size * 0.36, name, 'mono-400', size, p['ink'])
                    + '</g>')
            idx += 1
    fy = by + foot
    svg.add(f'<g class="up" style="animation-delay:{t + idx * 0.07 + 0.2:.2f}s">'
            + svg.check(bx + 1, fy, size, p['accent2'])
            + svg.text(bx + cw * 2, fy, 'all modules loaded', 'mono-400', size, p['accent2']) + '</g>')
    return svg


# ---- 4. career graph ---------------------------------------------------------------------------------------------

CAREER = [
    ('2024 - currently', 'Analytics Engineer', True, [
        'data pipelines and an analysis-ready warehouse (Python, SQL, Airflow, dbt)',
        'a pricing algorithm for multiple European markets',
        'profitability monitoring with costs down to product level',
        'language model integrations in company processes',
    ]),
    ('2022 - 2024', 'Data Analyst', False, [
        'Python apps for pricing policy and product data quality',
        'automated supplier orders',
        'algorithms for product bundles and sorting for revenue and margin',
        'integration of competitor pricing data',
    ]),
    ('2018 - 2022', 'Business Analyst', False, [
        'advanced SQL and data pipelines',
        'tools for sales, orders, products and accounting (Google Apps Script)',
        'ERP rollout: process analysis, data migration, testing',
    ]),
    ('2016 - 2018', 'Stock Optimization Manager, then Sales & Business Analysis Manager', False, [
        'sales forecasts and seasonal purchase planning',
        'stock turnover and clearance strategies',
        'leading a small analytics team and setting KPIs',
    ]),
]
EDUCATION = ('2024 - 2026', 'Postgraduate studies in Data Science (Advanced Data Analytics), '
                            'Wroclaw University of Economics and Business')
INTRO = '# over 10 years where business meets data, in e-commerce'


def career(theme: str, narrow: bool) -> Svg:
    W = 440 if narrow else 960
    pad = 20 if narrow else 30
    size = 13 if narrow else 15
    lh = size * 1.7
    gx = 12 + pad + 6
    tx = gx + (26 if narrow else 30)
    bx_off = 22
    text_w = W - 24 - pad - (tx - 12)
    # rows: (kind, payload)
    rows = [('intro', INTRO)]
    for i, (years, role, head, added) in enumerate(CAREER):
        if i:
            rows.append(('gap', None))
        rows.append(('commit', (years, role, head)))
        for a in added:
            for k, line in enumerate(wrap(a, 'mono-400', size, text_w - 2 * width('m', 'mono-400', size))):
                rows.append(('add', (line, k > 0)))
        if i == 0:
            rows.append(('fork', None))
            rows.append(('edu', EDUCATION))
            rows.append(('merge', None))
    # expand edu / commit wrapping
    flat = []
    for kind, val in rows:
        if kind == 'commit':
            years, role, head = val
            lead = years + '  '
            first_w = text_w - width(lead, 'mono-600', size)
            lines = wrap(role, 'mono-600', size, first_w if not narrow else text_w)
            if narrow:
                flat.append(('commit', (years, head, None)))
                flat += [('role', l) for l in lines]
            else:
                flat.append(('commit', (years, head, lines[0])))
                flat += [('role', l) for l in lines[1:]]
        elif kind == 'edu':
            years, txt = val
            flat.append(('edu', years))
            flat += [('edutext', l) for l in wrap(txt, 'mono-400', size, text_w - bx_off)]
        elif kind == 'intro':
            flat += [('intro', l) for l in wrap(val, 'mono-400', size, W - 24 - pad * 2)]
            flat.append(('gap', None))
        else:
            flat.append((kind, val))
    H = (12 + 40 + 24 + len(flat) * lh + 30 - sum(k == 'gap' for k, _ in flat) * lh * 0.6
         - sum(k in ('fork', 'merge') for k, _ in flat) * lh * 0.55)
    alt = ('Career graph as git log: over 10 years where business meets data, in e-commerce. ' +
           ' '.join(f'{y}: {r} ({"; ".join(a)}).' for y, r, _, a in CAREER) + f' Education {EDUCATION[0]}: {EDUCATION[1]}.')
    svg = Svg(W, H, theme, alt)
    p = svg.p
    svg.css.append(BASE_CSS)
    top = svg.window(12, 12, W - 24, H - 30, '~/career $ git log --graph')
    y = top + 24 + size
    y_first = y_last = None
    branch = []
    nodes = []
    for i, (kind, val) in enumerate(flat):
        d = 0.3 + i * 0.07
        st = f'animation-delay:{d:.2f}s'
        if kind == 'intro':
            svg.add(svg.text(12 + pad, y, val, 'mono-400', size, p['muted'], cls='up', style=st))
        elif kind == 'commit':
            years, head, role = val
            nodes.append((gx, y - size * 0.33, head, d))
            y_first = y_first or y
            y_last = y
            parts = [svg.text(tx, y, years, 'mono-600', size, p['amber'])]
            xx = tx + width(years + '  ', 'mono-600', size)
            if role:
                parts.append(svg.text(xx, y, role, 'mono-600', size, p['ink']))
            svg.add(f'<g class="up" style="{st}">{"".join(parts)}</g>')
        elif kind == 'role':
            svg.add(svg.text(tx, y, val, 'mono-600', size, p['ink'], cls='up', style=st))
        elif kind == 'add':
            line, cont = val
            prefix = '  ' if cont else '+ '
            svg.add(svg.text(tx, y, prefix + line, 'mono-400', size, p['text'], cls='up', style=st,
                             extra=' xml:space="preserve"'))
        elif kind == 'fork':
            branch.append(y - lh * 0.65)
        elif kind == 'edu':
            nodes.append((gx + bx_off, y - size * 0.33, False, d))
            svg.add(svg.text(tx + bx_off, y, val, 'mono-600', size, p['amber'], cls='up', style=st))
        elif kind == 'edutext':
            svg.add(svg.text(tx + bx_off, y, val, 'mono-400', size, p['ink'], cls='up', style=st))
        elif kind == 'merge':
            branch.append(y - lh * 0.4)
        y += {'fork': lh * 0.45, 'merge': lh * 0.45, 'gap': lh * 0.4}.get(kind, lh)
    # graph lines
    a, b = branch
    svg.css.append('@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}'
                   '.draw{stroke-dasharray:1;animation:draw 2.4s ease-out .3s both}')
    y0 = y_first - size * 0.33
    y1 = y_last - size * 0.33 + lh * 1.2
    svg.add(f'<path class="draw" pathLength="1" d="M{gx} {y0:.1f}V{y1:.1f}" stroke="{p["accent"]}" stroke-width="2" '
            f'stroke-opacity="0.7"/>')
    svg.add(f'<path class="draw" pathLength="1" d="M{gx} {a:.1f}c0 10 {bx_off} 8 {bx_off} 20V{b - 20:.1f}c0 12 '
            f'{-bx_off} 10 {-bx_off} 20" stroke="{p["pink"]}" stroke-width="2" stroke-opacity="0.75"/>')
    svg.css.append('@keyframes halo{0%{r:6px;opacity:.7}100%{r:16px;opacity:0}}'
                   '.halo{opacity:0;animation:halo 2s ease-out 1s infinite}')
    for nx, ny, head, d in nodes:
        c = p['pink'] if nx != gx else p['accent']
        if head:
            svg.add(f'<circle class="halo" cx="{nx}" cy="{ny:.1f}" r="6" fill="{p["pink"]}"/>')
        svg.add(f'<g class="up" style="animation-delay:{d:.2f}s"><circle cx="{nx}" cy="{ny:.1f}" r="6" fill="{p["panel"]}" '
                f'stroke="{p["pink"] if head else c}" stroke-width="2.5"/>'
                f'<circle cx="{nx}" cy="{ny:.1f}" r="2.5" fill="{p["pink"] if head else c}"/></g>')
    return svg


# ---- 5. projects -------------------------------------------------------------------------------------------------

# Published portfolio projects (zlecenie 344, decyzja «3a»; bigger card with the app and a button: zlecenie 364).
# One card per project (assets/project-<slug>.svg), each followed in README.md by a clickable "View project" button:
# a link inside an SVG does not work on GitHub and a linked <picture> breaks (see svgkit notes), so the button is a
# plain linked <img>. A new project = one more entry here, a shot made by scripts/make_shot.py and build.py.
# shot: shots/<file>, a strip of the app page 960 CSS px wide; stops: CSS px of the page where the scroll pauses,
# rest: the stop shown without motion (prefers-reduced-motion).
PROJECTS = [
    {
        'name': 'Data-Generator',
        'slug': 'data-generator',
        'desc': 'A fully fictional Polish online shop in 15 linked tables, from orders, reviews and the prices of '
                'five competitors to web sessions, returns and A/B tests. Truth columns, down to the true churn date, '
                'let you check your analysis, and 75 realism criteria pass.',
        # analyses the data is good for (zlecenie 373): one line under the description, as in the repo README
        'uses': ['sales forecasting', 'cohorts and churn', 'market basket', 'campaign ROAS', 'cancellations',
                 'ratings', 'price index', 'A/B tests'],
        'stack': [('Python', 'python'), ('pandas', 'pandas'), ('NumPy', 'numpy'), ('Dash', None),
                  ('Plotly', 'plotly')],
        'url': 'https://github.com/tlabedzki/Data-Generator',
        'run': 'python -m ui.app',
        'serve': 'Dash is running on http://127.0.0.1:8050/',
        'host': '127.0.0.1:8050',
        'shot': 'data-generator.webp',
        'stops': [0, 470, 1460, 2330, 2870],
        'rest': 2330,
        'shot_alt': 'its web app (Dash) scrolls from the parameters through the data preview to the charts',
    },
    {
        'name': 'Pricing-Engine',
        'slug': 'pricing-engine',
        'desc': 'A new price for every product of Lumo, the shop from Data-Generator, from elasticity estimated on '
                "price history and discounts, five competitors' prices and margin rules. Each price has a "
                'one-sentence reason, and the true elasticity checks the result.',
        'uses_label': 'Methods:',  # zlecenie 586: what the engine does, where Data-Generator lists what to practise
        'uses': ['price elasticity', 'empirical Bayes', 'price index', 'margin rules', 'profit scenarios'],
        'stack': [('Python', 'python'), ('pandas', 'pandas'), ('DuckDB', None), ('SciPy', None),
                  ('Dash', None), ('Plotly', 'plotly')],
        'url': 'https://github.com/tlabedzki/Pricing-Engine',
        'run': 'python -m ui.app',
        'serve': 'Dash is running on http://127.0.0.1:8050/',
        'host': '127.0.0.1:8050',
        # v1.1.0 (Dash and Mantine, the Data-Generator look; zlecenie 589): shot at 960 CSS px like Data-Generator
        'shot': 'pricing-engine.webp',
        'stops': [0, 490, 1010],
        'rest': 1010,
        'shot_alt': 'its web app (Dash) scrolls from the pricing rules to the yearly result and the proposals '
                    'with their reasons',
    },
]
SHOT_VIEW = 600  # CSS px of the app page visible in the browser frame (at 960 CSS px wide)
BUTTON = 'view-project'


def webp_size(data: bytes) -> tuple[int, int]:
    """Width and height of a WebP (VP8, VP8L or VP8X) without Pillow: build.py stays on the standard library."""
    kind = data[12:16]
    if kind == b'VP8X':
        return 1 + int.from_bytes(data[24:27], 'little'), 1 + int.from_bytes(data[27:30], 'little')
    if kind == b'VP8L':
        b = int.from_bytes(data[21:25], 'little')
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    return int.from_bytes(data[26:28], 'little') & 0x3FFF, int.from_bytes(data[28:30], 'little') & 0x3FFF


def scroll_keyframes(stops: list[float], hold: float = 1.9, glide: float = 1.15,
                     back: float = 1.4) -> tuple[list[tuple[float, float]], float]:
    """Keyframe stops (percent, CSS px) for a page that pauses at each stop, glides on and finally scrolls back up."""
    total = len(stops) * hold + (len(stops) - 1) * glide + back
    frames, t = [], 0.0
    for i, s in enumerate(stops):
        frames.append((t / total * 100, s))
        t += hold
        frames.append((t / total * 100, s))
        t += glide if i < len(stops) - 1 else 0
    frames.append((100.0, stops[0]))
    return frames, total


def browser(svg: Svg, proj: dict, x: float, y: float, w: float, delay: float, narrow: bool) -> float:
    """Browser frame with the app inside, scrolled through by CSS. Returns the bottom y."""
    p = svg.p
    data = (ROOT / 'shots' / proj['shot']).read_bytes()
    iw, ih = webp_size(data)
    bar = 26 if narrow else 30
    vh = w * SHOT_VIEW / 960
    k = w / 960  # CSS px of the page -> px in the card
    img_h = w * ih / iw
    shot_id = f'shot-{proj["slug"]}'  # same in both themes, so _render keeps one copy of the image
    svg.defs.append(f'<image id="{shot_id}" width="{w:.1f}" height="{img_h:.1f}" preserveAspectRatio="none" '
                    f'href="data:image/webp;base64,{base64.b64encode(data).decode()}"/>')
    clip = svg.uid('view')
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y + bar}" width="{w}" height="{vh:.1f}"/></clipPath>')
    frame = svg.uid('frame')
    svg.defs.append(f'<clipPath id="{frame}"><rect x="{x}" y="{y}" width="{w}" height="{bar + vh:.1f}" rx="10"/></clipPath>')
    # scroll: the page and the scrollbar thumb move on the same keyframes
    frames, total = scroll_keyframes(proj['stops'])
    max_stop = ih / iw * 960 - SHOT_VIEW
    thumb_h = vh * SHOT_VIEW / (ih / iw * 960)
    page, thumb = svg.uid('page'), svg.uid('thumb')
    ease = 'animation-timing-function:cubic-bezier(.65,0,.35,1)'
    kf_page = ''.join(f'{pc:.2f}%{{transform:translateY({-s * k:.1f}px);{ease}}}' for pc, s in frames)
    kf_thumb = ''.join(f'{pc:.2f}%{{transform:translateY({s / max_stop * (vh - thumb_h - 6):.1f}px);{ease}}}'
                       for pc, s in frames)
    start = delay + 1.6
    svg.css.append(f'@keyframes {page}{{{kf_page}}}@keyframes {thumb}{{{kf_thumb}}}'
                   f'.{page}{{transform:translateY({-proj["rest"] * k:.1f}px);'
                   f'animation:{page} {total:.2f}s {start:.2f}s infinite both}}'
                   f'.{thumb}{{transform:translateY({proj["rest"] / max_stop * (vh - thumb_h - 6):.1f}px);'
                   f'animation:{thumb} {total:.2f}s {start:.2f}s infinite both}}')
    glow = ''
    if p['glow']:
        fid = svg.glow_filter(14)
        glow = (f'<rect x="{x + 8}" y="{y + 12}" width="{w - 16}" height="{bar + vh - 16:.1f}" rx="10" '
                f'fill="{p["accent"]}" opacity="{p["glow"] * 0.8:.2f}" filter="url(#{fid})"/>')
    dots = ''.join(f'<circle cx="{x + 14 + i * 13}" cy="{y + bar / 2:.1f}" r="4" fill="{p["muted"]}" opacity="0.5"/>'
                   for i in range(3))
    fs = 11 if narrow else 12
    host_w = width(proj['host'], 'mono-400', fs) + 28
    pill_x = x + 62
    pill = (f'<rect x="{pill_x:.1f}" y="{y + bar / 2 - 9:.1f}" width="{host_w:.1f}" height="18" rx="9" fill="{p["bg"]}" '
            f'stroke="{p["line_soft"]}"/>'
            f'<circle cx="{pill_x + 10:.1f}" cy="{y + bar / 2:.1f}" r="2.5" fill="{p["accent2"]}"/>'
            + svg.text(pill_x + 18, y + bar / 2 + fs * 0.36, proj['host'], 'mono-400', fs, p['muted']))
    track_x = x + w - 7
    svg.add(f'<g class="up" style="animation-delay:{delay:.2f}s">{glow}'
            f'<g clip-path="url(#{frame})">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{bar + vh:.1f}" fill="#ffffff"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{bar}" fill="{p["bar"]}"/>'
            f'<line x1="{x}" y1="{y + bar}" x2="{x + w}" y2="{y + bar}" stroke="{p["line_soft"]}"/>'
            f'{dots}{pill}'
            f'<g clip-path="url(#{clip})"><g class="{page}"><use href="#{shot_id}" x="{x}" y="{y + bar}"/></g>'
            f'<rect class="{thumb}" x="{track_x:.1f}" y="{y + bar + 3:.1f}" width="4" height="{thumb_h:.1f}" rx="2" '
            f'fill="#14232a" opacity="0.28"/></g></g>'
            f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{bar + vh - 1:.1f}" rx="10" '
            f'stroke="{p["accent"] if p["glow"] else p["line"]}" stroke-opacity="{0.55 if p["glow"] else 1}"/></g>')
    return y + bar + vh


def chips(svg: Svg, items: list[tuple[str, str | None]], x: float, y: float, max_w: float, size: float,
          delay: float) -> float:
    """Stack chips like the stack card, wrapped to max_w. Returns the bottom y."""
    p = svg.p
    ch, gap, isz = size * 2.15, 8, size * 1.1
    cx, cy, out = x, y, []
    for i, (name, key) in enumerate(items):
        cw = 11 + (isz + 7 if key else 0) + width(name, 'mono-400', size) + 12
        if cx + cw > x + max_w and cx > x:
            cx, cy = x, cy + ch + gap
        g = (f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="7" fill="{p["bar"]}" '
             f'stroke="{p["line"]}"/>')
        tx = cx + 11
        if key:
            g += icon(svg, key, tx, cy + (ch - isz) / 2, isz)
            tx += isz + 7
        g += svg.text(tx, cy + ch / 2 + size * 0.36, name, 'mono-400', size, p['ink'])
        out.append(f'<g class="up" style="animation-delay:{delay + i * 0.07:.2f}s">{g}</g>')
        cx += cw + gap
    svg.add(*out)
    return cy + ch


def project_card(proj: dict, index: int, theme: str, narrow: bool) -> Svg:
    W = 440 if narrow else 960
    pad = 20 if narrow else 30
    size = 13 if narrow else 15
    lh = size * 1.75
    name_size = 25 if narrow else 30
    inner = W - 24 - pad * 2
    bw = inner if narrow else 520  # browser width
    # desktop: text on the left, browser on the right (user's choice, zlecenie 364); phone: one column
    col_x = 0  # text column, relative to the left padding
    col_w = inner if narrow else inner - bw - 40
    b_x = 0 if narrow else inner - bw
    cw = width('m', 'mono-400', size)
    lines = wrap(proj['desc'], 'mono-400', size, col_w)
    uses_label = proj.get('uses_label', 'Practise:')
    # wrap only between analyses: a no-break space inside each (e.g. "A/B tests") keeps it on one line
    nb = [u.replace(' ', '\u00a0') for u in proj.get('uses', [])]
    uses = [line.replace('\u00a0', ' ')
            for line in wrap(f'{uses_label} {", ".join(nb)}', 'mono-400', size, col_w)] if nb else []
    bar = 26 if narrow else 30
    b_h = bar + bw * SHOT_VIEW / 960
    # layout (y relative to the window body)
    head = 26 + size  # prompt baseline
    serve = head + lh
    top = serve + lh * 0.9  # content starts here
    if narrow:
        name_y = top + name_size * 0.9
        b_y = name_y + 18
        desc_y = b_y + b_h + 22 + size
    else:
        name_y = top + name_size * 0.95
        b_y = top + 4
        desc_y = name_y + 22 + size
    uses_y = desc_y + len(lines) * lh + size * 0.6  # first baseline of the analyses line, half a line below
    chips_y = (uses_y + (len(uses) - 1) * lh if uses else desc_y + (len(lines) - 1) * lh) + size + 18
    chip_rows_h = size * 2.15 * 2 + 8  # room for two rows of chips (measured again below)
    body_h = max(b_y + b_h, chips_y + chip_rows_h) + (24 if narrow else 30)
    H = 12 + 40 + body_h + 18
    total = len(PROJECTS)
    uses_alt = f'{uses_label} {", ".join(proj["uses"])}. ' if uses else ''
    alt = (f'Project {index + 1} of {total}: {proj["name"]}. {proj["desc"]} {uses_alt}'
           f'Stack: {", ".join(n for n, _ in proj["stack"])}. Animated preview: {proj["shot_alt"]}. '
           f'Link below the card: View project.')
    svg = Svg(W, H, theme, alt)
    p = svg.p
    svg.css.append(BASE_CSS)
    x0 = 12
    by = svg.window(x0, 12, W - 24, H - 30, ('' if narrow else 'tomasz@insighteo: ') + f'~/projects/{proj["name"]}')
    count = f'{index + 1:02d} / {total:02d}'  # position in the list: the card is one of a series
    svg.add(svg.text(x0 + W - 24 - 18, 12 + 20 + 4.5, count, 'mono-400', 13, p['muted'], anchor='end'))
    bx = x0 + pad
    svg.add(svg.text(bx, by + head, '$', 'mono-400', size, p['accent']))
    tag, t, _ = typed(svg, bx + cw * 2, by + head, proj['run'], 'mono-400', size, p['ink'], 0.4, 0.04)
    svg.add(tag)
    t += 0.3
    svg.add(svg.text(bx + cw * 2, by + serve, proj['serve'], 'mono-400', size * 0.92, p['muted'], cls='up',
                     style=f'animation-delay:{t:.2f}s'))
    halo = svg.text_glow(6)
    svg.add(svg.text(bx + col_x, by + name_y, proj['name'], 'sans-600', name_size, p['bright'], cls='up',
                     style=f'animation-delay:{t + 0.2:.2f}s', extra=halo))
    browser(svg, proj, bx + b_x, by + b_y, bw, t + 0.35, narrow)
    d = t + 0.6
    svg.add(f'<g class="up" style="animation-delay:{d:.2f}s">'
            + ''.join(svg.text(bx + col_x, by + desc_y + i * lh, line, 'mono-400', size, p['text'])
                      for i, line in enumerate(lines)) + '</g>')
    if uses:
        # the label in the accent colour, the analyses in the description's colour
        first = uses[0][len(uses_label):]
        lx = bx + col_x + width(uses_label, 'mono-400', size)
        svg.add(f'<g class="up" style="animation-delay:{d + 0.1:.2f}s">'
                + svg.text(bx + col_x, by + uses_y, uses_label, 'mono-400', size, p['accent'])
                + svg.text(lx, by + uses_y, first, 'mono-400', size, p['text'], style='white-space:pre')
                + ''.join(svg.text(bx + col_x, by + uses_y + i * lh, line, 'mono-400', size, p['text'])
                          for i, line in enumerate(uses) if i) + '</g>')
    end = chips(svg, proj['stack'], bx + col_x, by + chips_y, col_w, size * 0.92, d + 0.2)
    assert end - by <= chips_y + chip_rows_h + 0.1, 'stack chips need more than two rows'
    return svg


def view_button(theme: str) -> Svg:
    """The "View project" button under every card, as a linked <img> in README.md. Left margin = the card's (12 px)."""
    W, H = 216, 56
    svg = Svg(W, H, theme, 'View project')
    p = svg.p
    x, y, w, h = 12, 6, W - 18, H - 12
    fill, ink = (p['accent'], p['bg']) if theme == 'dark' else (p['accent'], '#ffffff')
    size = 17
    label = 'View project'
    tw = width(label, 'sans-600', size)
    tx = x + (w - tw - 28) / 2
    clip = svg.uid('btn')
    shine = svg.uid('shine')
    svg.defs.append(f'<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath>'
                    f'<linearGradient id="{shine}" x1="0" y1="0" x2="1" y2="0">'
                    f'<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
                    f'<stop offset="0.5" stop-color="#ffffff" stop-opacity="{0.45 if theme == "dark" else 0.3}"/>'
                    f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>')
    svg.css.append('@keyframes sweep{0%,62%{transform:translateX(-90px)}100%{transform:translateX(260px)}}'
                   '.sweep{transform:translateX(-90px);animation:sweep 4.2s ease-in-out 1.2s infinite}'
                   '@keyframes nudge{0%,70%,100%{transform:none}80%{transform:translateX(4px)}90%{transform:none}}'
                   '.nudge{animation:nudge 4.2s ease-in-out 1.2s infinite}')
    glow = ''
    if p['glow']:
        fid = svg.glow_filter(8)
        glow = (f'<rect x="{x + 6}" y="{y + 8}" width="{w - 12}" height="{h - 10}" rx="10" fill="{fill}" '
                f'opacity="0.45" filter="url(#{fid})"/>')
    svg.add(glow,
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}"/>',
            f'<g clip-path="url(#{clip})"><g class="sweep"><rect x="{x}" y="{y}" width="70" height="{h}" '
            f'fill="url(#{shine})" transform="skewX(-20)"/></g></g>',
            svg.text(tx, y + h / 2 + size * 0.35, label, 'sans-600', size, ink),
            f'<g class="nudge">{svg.arrow(tx + tw + 12, y + h / 2 + size * 0.32, size, ink)}</g>')
    return svg


# ---- README ------------------------------------------------------------------------------------------------------

def picture(name: str, alt: str) -> str:
    """Width variants only (narrow = phones). The theme is picked inside each SVG, never here: a <source> with
    prefers-color-scheme follows the OS, not the GitHub theme (zlecenie 319, see svgkit)."""
    return (f'<picture>\n'
            f'  <source media="(max-width: 600px)" srcset="assets/{name}-narrow.svg">\n'
            f'  <img src="assets/{name}.svg" width="100%" alt="{esc(alt)}">\n'
            f'</picture>')


def button(proj: dict) -> str:
    """Clickable "View project" under a card: a linked <img>, not a <picture> (that one breaks when linked)."""
    return (f'<p><a href="{proj["url"]}"><img src="assets/{BUTTON}.svg" width="216" height="56" '
            f'alt="View project: {esc(proj["name"])} on GitHub"></a></p>')


def readme() -> str:
    alts = {n: fn('dark', False).title for n, fn in (('banner', banner), ('agents', agents), ('stack', stack),
                                                       ('career', career))}
    cards = ''.join(f'{picture("project-" + proj["slug"], project_card(proj, i, "dark", False).title)}\n\n'
                    f'{button(proj)}\n\n' for i, proj in enumerate(PROJECTS))
    activity_alt = ('Live GitHub activity of Tomasz over the past year: a weekly signal line and a daily heatmap, '
                    'redrawn every day by GitHub Actions.')
    return (
        '<!-- Generated by scripts/build.py. Edit the script, not this file. -->\n'
        f'{picture("banner", alts["banner"])}\n\n'
        f'{picture("agents", alts["agents"])}\n\n'
        f'{picture("stack", alts["stack"])}\n\n'
        f'{picture("career", alts["career"])}\n\n'
        f'{cards}'
        f'{picture("activity", activity_alt)}\n'
    )


def main() -> None:
    (ROOT / 'README.md').write_text(readme(), encoding='utf-8')
    out = [save_themed(f'{BUTTON}.svg', view_button('dark'), view_button('light'))]
    for narrow in (False, True):
        sfx = '-narrow' if narrow else ''
        for name, fn in (('banner', banner), ('agents', agents), ('stack', stack), ('career', career)):
            out.append(save_themed(f'{name}{sfx}.svg', fn('dark', narrow), fn('light', narrow)))
        for i, proj in enumerate(PROJECTS):
            out.append(save_themed(f'project-{proj["slug"]}{sfx}.svg', project_card(proj, i, 'dark', narrow),
                                   project_card(proj, i, 'light', narrow)))
    for path in out:
        print(f'{path.name:32} {path.stat().st_size / 1024:6.1f} KB')


if __name__ == '__main__':
    main()
