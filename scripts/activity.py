"""Live part of the profile: GitHub activity over the past year, redrawn daily by GitHub Actions.

Reads the public contribution calendar through the GraphQL API (GITHUB_TOKEN in Actions is enough) and draws
it in the insighteo.pl style: a weekly signal line and a daily heatmap, dark and light, wide and narrow.
No figures on the graphic (rule from insighteo.pl): only the shape of the activity and month names.

Usage:
  python scripts/activity.py                  # token from GITHUB_TOKEN, or from `gh auth token` locally
  python scripts/activity.py --data file.json # offline, from a saved GraphQL response
Env: PROFILE_LOGIN (default tlabedzki).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import subprocess
import sys
import urllib.request

from svgkit import Svg

LOGIN = os.environ.get('PROFILE_LOGIN', 'tlabedzki')
QUERY = '''query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
weeks{contributionDays{contributionCount date}}}}}}'''
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def token() -> str:
    tok = os.environ.get('GITHUB_TOKEN')
    if tok:
        return tok
    return subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, check=True).stdout.strip()


def fetch() -> dict:
    body = json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', data=body, headers={
        'Authorization': f'bearer {token()}', 'Content-Type': 'application/json', 'User-Agent': 'profile-activity'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if 'errors' in data:
        raise SystemExit(f'GraphQL error: {data["errors"]}')
    return data


def weeks_from(data: dict) -> list[list[tuple[dt.date, int]]]:
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    return [[(dt.date.fromisoformat(d['date']), d['contributionCount']) for d in w['contributionDays']] for w in weeks]


def smooth(points: list[tuple[float, float]]) -> str:
    """Catmull-Rom spline through the points as cubic Bezier path data."""
    d = f'M{points[0][0]:.1f} {points[0][1]:.1f}'
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
    return d


def levels(weeks) -> dict[dt.date, int]:
    counts = sorted(c for w in weeks for _, c in w if c > 0)
    if not counts:
        return {d: 0 for w in weeks for d, _ in w}
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)]
    out = {}
    for w in weeks:
        for d, c in w:
            out[d] = 0 if c == 0 else 1 + sum(c > t for t in q)
    return out


def draw(weeks, theme: str, narrow: bool) -> Svg:
    W = 440 if narrow else 960
    pad = 20 if narrow else 30
    size = 12.5 if narrow else 14
    x0, inner = 12 + pad, W - 24 - pad * 2
    chart_h = 110 if narrow else 150
    n = len(weeks)
    step = inner / n
    cell = step * 0.78
    top_body = 12 + 40
    head_y = top_body + 26 + size
    chart_top = head_y + (40 if narrow else 30)
    months_y = chart_top + chart_h + 22
    heat_top = months_y + 14
    heat_h = step * 7
    legend_y = heat_top + heat_h + 26
    foot_y = legend_y + (24 if narrow else 0)
    H = foot_y + 34
    svg = Svg(W, H, theme, 'Live GitHub activity of Tomasz over the past year: a weekly signal line and a daily '
                           'heatmap, redrawn every day by GitHub Actions.')
    p = svg.p
    svg.css.append('@keyframes in{from{opacity:0}to{opacity:1}}'
                   '@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}'
                   '@keyframes ping{0%{r:5px;opacity:.8}100%{r:15px;opacity:0}}'
                   '@keyframes scan{0%{transform:translateX(0);opacity:0}8%,85%{opacity:1}100%{transform:translateX(' + f'{inner:.0f}' + 'px);opacity:0}}'
                   '.in{animation:in .5s ease-out both}'
                   '.draw{stroke-dasharray:1;animation:draw 2.6s cubic-bezier(.3,.6,.2,1) .4s both}'
                   '.area{animation:in 1.2s ease-out 1.6s both}'
                   '.ping{opacity:0;animation:ping 1.8s ease-out 2.8s infinite}'
                   '.scan{opacity:0;animation:scan 7s linear 3.2s infinite}')
    top = svg.window(12, 12, W - 24, H - 30, '~/signal $ git activity --live')
    # header
    svg.add(f'<circle class="ping" cx="{x0 + 5}" cy="{head_y - size * 0.35:.1f}" r="5" fill="{p["accent2"]}"/>',
            f'<circle cx="{x0 + 5}" cy="{head_y - size * 0.35:.1f}" r="4.5" fill="{p["accent2"]}"/>',
            svg.text(x0 + 18, head_y, 'live', 'mono-600', size, p['accent2']),
            svg.text(x0 + 18 + 48, head_y, 'contributions over the past year', 'mono-400', size, p['soft']))
    sync = 'synced daily by GitHub Actions'
    if narrow:
        svg.add(svg.text(x0, head_y + size * 1.6, sync, 'mono-400', size * 0.92, p['muted']))
    else:
        svg.add(svg.text(x0 + inner, head_y, sync, 'mono-400', size * 0.92, p['muted'], anchor='end'))
    # grid
    for k in range(4):
        gy = chart_top + chart_h * k / 3
        svg.add(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x0 + inner}" y2="{gy:.1f}" stroke="{p["line_soft"]}" '
                f'stroke-dasharray="3 5"/>')
    # signal line (square root scale, so quiet weeks still show)
    totals = [sum(c for _, c in w) for w in weeks]
    peak = max(totals) or 1
    pts = [(x0 + step * (i + 0.5), chart_top + chart_h - chart_h * 0.92 * math.sqrt(t / peak)) for i, t in enumerate(totals)]
    line = smooth(pts)
    fill = svg.uid('area')
    svg.defs.append(f'<linearGradient id="{fill}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["accent"]}" '
                    f'stop-opacity="0.45"/><stop offset="1" stop-color="{p["accent"]}" stop-opacity="0"/></linearGradient>')
    halo = svg.text_glow(5 if theme == 'dark' else 2)
    base = chart_top + chart_h
    svg.add(f'<path class="area" d="{line}L{pts[-1][0]:.1f} {base:.1f}L{pts[0][0]:.1f} {base:.1f}Z" fill="url(#{fill})"/>',
            f'<path class="draw" pathLength="1" d="{line}" stroke="{p["accent"]}" stroke-width="2.5" '
            f'stroke-linecap="round" filter="url(#{halo})"/>')
    lx, ly = pts[-1]
    svg.add(f'<circle class="ping" cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="{p["accent"]}"/>',
            f'<circle class="in" style="animation-delay:2.8s" cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{p["bright"]}"/>')
    # scan beam across the chart
    beam = svg.uid('beam')
    svg.defs.append(f'<linearGradient id="{beam}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["accent"]}" '
                    f'stop-opacity="0"/><stop offset="1" stop-color="{p["accent"]}" stop-opacity="0.14"/></linearGradient>')
    svg.add(f'<rect class="scan" x="{x0 - 40}" y="{chart_top}" width="40" height="{chart_h}" fill="url(#{beam})"/>')
    # month labels where a month starts
    last = None
    for i, w in enumerate(weeks):
        m = w[0][0].month
        if last is not None and m != last and i < n - 2:
            if not narrow or m % 2 == 1:
                svg.add(svg.text(x0 + step * i, months_y, MONTHS[m - 1], 'mono-400', size * 0.86, p['muted'],
                                 cls='in', style='animation-delay:.6s'))
        last = m
    # heatmap
    lv = levels(weeks)
    ops = [0, 0.28, 0.5, 0.75, 1]
    for i, w in enumerate(weeks):
        cells = []
        for d, _ in w:
            row = (d.weekday() + 1) % 7  # Sunday first, like GitHub
            L = lv[d]
            color, op = (p['line_soft'], 1) if L == 0 else (p['accent'], ops[L])
            cells.append(f'<rect x="{x0 + step * i:.1f}" y="{heat_top + step * row:.1f}" width="{cell:.1f}" '
                         f'height="{cell:.1f}" rx="{max(1, cell * 0.2):.1f}" fill="{color}" opacity="{op}"/>')
        svg.add(f'<g class="in" style="animation-delay:{0.5 + i * 0.03:.2f}s">{"".join(cells)}</g>')
    # legend
    lgx = x0 + inner - (5 * (cell + 4)) - width_of('more', size)
    svg.add(svg.text(lgx - 8, legend_y, 'less', 'mono-400', size * 0.86, p['muted'], anchor='end'))
    for k in range(5):
        color, op = (p['line_soft'], 1) if k == 0 else (p['accent'], ops[k])
        svg.add(f'<rect x="{lgx + k * (cell + 4):.1f}" y="{legend_y - cell + 1:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
                f'rx="{max(1, cell * 0.2):.1f}" fill="{color}" opacity="{op}"/>')
    svg.add(svg.text(lgx + 5 * (cell + 4) + 4, legend_y, 'more', 'mono-400', size * 0.86, p['muted']))
    return svg


def width_of(s: str, size: float) -> float:
    return len(s) * 0.6 * size * 0.86


def main() -> None:
    if '--data' in sys.argv:
        data = json.loads(open(sys.argv[sys.argv.index('--data') + 1], encoding='utf-8').read())
    else:
        data = fetch()
    weeks = weeks_from(data)
    for theme in ('dark', 'light'):
        for narrow in (False, True):
            path = draw(weeks, theme, narrow).save(f'activity-{theme}{"-narrow" if narrow else ""}.svg')
            print(f'{path.name:32} {path.stat().st_size / 1024:6.1f} KB')


if __name__ == '__main__':
    main()
