"""Static profile graphics: banner, agents terminal, stack modules, career graph.

Every graphic comes in a dark and a light version, the large ones also in a narrow version for phones
(README.md picks them with <picture>). Texts follow insighteo.pl (src/i18n/content.ts, EN), shortened.
Rules from insighteo.pl: no employer or client names, no figures for results, no "—" or "–".

Usage: python scripts/build.py
"""
from __future__ import annotations

import random

from icons import ICONS
from svgkit import ROOT, Svg, esc, width, wrap

THEMES = ('dark', 'light')
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
            op = 0.95 if head else (k + 1) / n * p['rain_opacity']
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
    halo = svg.text_glow(10 if theme == 'dark' else 4)
    nx = cx - width(NAME, 'sans-600', name_size) / 2
    start, step = t_end + 0.35, 0.085
    tag, n_end, xs = typed(svg, nx, ys[1], NAME, 'sans-600', name_size, p['ink'], start, step,
                           extra=f' filter="url(#{halo})" letter-spacing="0"')
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
            + svg.text(pxl + 32 + tw + 12, py, '·', 'mono-400', pill_size, p['muted'])
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
    halo = svg.text_glow(6 if theme == 'dark' else 2)
    ty += lh * 1.25
    deliver = 'deliver: from a conversation about the problem to a deployed tool'
    lines = wrap(deliver, 'mono-400', size, w - pad * 2 - cw * 2)
    g = [svg.arrow(tx, ty, size, p['bright'])]
    for k, line in enumerate(lines):
        g.append(svg.text(tx + cw * 2, ty + k * lh, line, 'mono-600', size, p['bright'], extra=f' filter="url(#{halo})"'))
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


# ---- README ------------------------------------------------------------------------------------------------------

def picture(name: str, alt: str) -> str:
    """Theme and width variants. GitHub sets prefers-color-scheme from the GitHub theme; narrow = phones.
    Order matters: if a combined query ever fails, the next source is still a sensible fallback."""
    return (f'<picture>\n'
            f'  <source media="(prefers-color-scheme: light) and (max-width: 600px)" srcset="assets/{name}-light-narrow.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
            f'  <source media="(max-width: 600px)" srcset="assets/{name}-dark-narrow.svg">\n'
            f'  <img src="assets/{name}-dark.svg" width="100%" alt="{esc(alt)}">\n'
            f'</picture>')


def readme() -> str:
    alts = {n: fn('dark', False).title for n, fn in (('banner', banner), ('agents', agents), ('stack', stack),
                                                       ('career', career))}
    activity_alt = ('Live GitHub activity of Tomasz over the past year: a weekly signal line and a daily heatmap, '
                    'redrawn every day by GitHub Actions.')
    return (
        '<!-- Generated by scripts/build.py. Edit the script, not this file. -->\n'
        f'{picture("banner", alts["banner"])}\n\n'
        f'{picture("agents", alts["agents"])}\n\n'
        f'{picture("stack", alts["stack"])}\n\n'
        f'{picture("career", alts["career"])}\n\n'
        f'{picture("activity", activity_alt)}\n'
    )


def main() -> None:
    (ROOT / 'README.md').write_text(readme(), encoding='utf-8')
    for theme in THEMES:
        for narrow in (False, True):
            suffix = f'{theme}{"-narrow" if narrow else ""}'
            for name, fn in (('banner', banner), ('agents', agents), ('stack', stack), ('career', career)):
                path = fn(theme, narrow).save(f'{name}-{suffix}.svg')
                print(f'{path.name:32} {path.stat().st_size / 1024:6.1f} KB')


if __name__ == '__main__':
    main()
