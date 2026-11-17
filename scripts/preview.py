"""Local preview of the profile README, rendered by GitHub's own Markdown API (same sanitizer as the profile).

Writes preview/index.html (GitHub-like profile layout, light or dark from prefers-color-scheme) and serves the repo
on 127.0.0.1 only. Needs the gh CLI (logged in) and github-markdown-css in .cache (npm install github-markdown-css).
Nothing is published: the Markdown API only returns HTML.

Usage: python scripts/preview.py [--serve] [--port 8765]
"""
from __future__ import annotations

import http.server
import json
import subprocess
import sys
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'preview'
CSS = ROOT / '.cache' / 'node_modules' / 'github-markdown-css' / 'github-markdown.css'

PAGE = '''<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preview: tlabedzki</title>
<link rel="stylesheet" href="github-markdown.css">
<style>
  :root { color-scheme: light dark; }
  body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
         background: #ffffff; color: #1f2328; }
  @media (prefers-color-scheme: dark) { body { background: #0d1117; color: #e6edf3; } }
  .top { height: 64px; border-bottom: 1px solid rgba(128,128,128,.25); display: flex; align-items: center; padding: 0 24px;
         font-weight: 600; gap: 12px; background: rgba(128,128,128,.06); }
  .top i { width: 32px; height: 32px; border-radius: 50%; background: rgba(128,128,128,.35); display: inline-block; }
  .layout { max-width: 1280px; margin: 0 auto; padding: 24px 32px; display: grid; grid-template-columns: 296px 1fr; gap: 24px; }
  .side .avatar { width: 296px; height: 296px; border-radius: 50%; background: rgba(128,128,128,.25); }
  .side h1 { font-size: 24px; margin: 16px 0 0; } .side p { margin: 4px 0; opacity: .7; }
  .box { border: 1px solid rgba(128,128,128,.3); border-radius: 6px; padding: 24px; min-width: 0; }
  .box .label { font-size: 12px; font-family: ui-monospace, monospace; opacity: .7; margin-bottom: 16px; }
  .markdown-body { background: transparent; }
  @media (max-width: 767px) {
    .layout { grid-template-columns: 1fr; padding: 16px; }
    .side { display: flex; gap: 16px; align-items: center; }
    .side .avatar { width: 64px; height: 64px; flex: none; } .side h1 { margin: 0; font-size: 20px; }
    .box { padding: 16px; }
  }
</style></head><body>
<div class="top"><i></i> github.com / tlabedzki (local preview)</div>
<div class="layout">
  <aside class="side"><div class="avatar"></div><div><h1>Tomasz Labedzki</h1><p>tlabedzki</p></div></aside>
  <main class="box"><div class="label">tlabedzki / README.md</div>
  <article class="markdown-body">@@BODY@@</article></main>
</div>
<script>
  // GitHub's own script (<themed-picture>) puts the <img> back as a direct child of <picture>; the Markdown API
  // output has it wrapped in a link, so without this the browser ignores the <source> variants.
  for (const pic of document.querySelectorAll('picture')) {
    const img = pic.querySelector('a > img');
    if (img) { const a = img.parentElement; pic.appendChild(img); a.remove(); }
  }
</script></body></html>'''


def render() -> Path:
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    res = subprocess.run(['gh', 'api', 'markdown', '--input', '-'], input=json.dumps({'text': text, 'mode': 'markdown'}),
                         capture_output=True, text=True, encoding='utf-8', check=True)
    html = res.stdout
    # The API keeps relative paths; the page lives in preview/, the graphics in assets/.
    html = html.replace('srcset="assets/', 'srcset="../assets/').replace('src="assets/', 'src="../assets/')
    OUT.mkdir(exist_ok=True)
    (OUT / 'github-markdown.css').write_text(CSS.read_text(encoding='utf-8'), encoding='utf-8')
    (OUT / 'rendered.html').write_text(res.stdout, encoding='utf-8')
    path = OUT / 'index.html'
    path.write_text(PAGE.replace("@@BODY@@", html), encoding='utf-8')
    return path


def main() -> None:
    path = render()
    print(f'written {path}')
    if '--serve' in sys.argv:
        port = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 8765
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
            print(f'serving http://127.0.0.1:{port}/preview/')
            srv.serve_forever()


if __name__ == '__main__':
    main()
