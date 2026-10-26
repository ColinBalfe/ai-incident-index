#!/usr/bin/env python3
"""Freeze this edition: copy the prerendered front page to archive/<YYYY-MM-DD-HHMM>/ with the scripts removed, so it shows
exactly what readers saw at this refresh and never redraws from live data. Also writes archive/index.html (every edition).
Run after prerender.mjs. The front page's edition line links here, and the changelog says what changed."""
import json, os, re, html
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
meta = json.load(open('data/meta.json', encoding='utf-8'))
path = meta.get('edition_path') or ('archive/' + meta['as_of'][:16].replace('T', '-').replace(':', '') + '/')
src = open('index.html', encoding='utf-8').read()
src = re.sub(r'<script[^>]*src="/assets/(app|vendor/[^"]+)\.js[^"]*"[^>]*></script>', '', src)
src = src.replace('<link rel="canonical" href="' + meta['site_url'] + '">', '<link rel="canonical" href="' + meta['site_url'] + path + '"><meta name="robots" content="noindex">', 1)
banner = ('<div style="background:#0A111E;color:#F4F3EF;font:600 14px/1.4 Arial,sans-serif;padding:10px 16px;text-align:center">'
          'Frozen copy: Warning Shots edition No. %d, as published %s. Nothing on this page updates. '
          '<a href="/" style="color:#FF5B3E">The live page</a> · <a href="/index/#changelog" style="color:#FF5B3E">What changed</a> · <a href="/archive/" style="color:#FF5B3E">All editions</a></div>') % (meta.get('edition', 0), html.escape(meta.get('as_of_label', '')))
src = re.sub(r'(<body[^>]*>)', r'\1' + banner.replace('\\', '\\\\'), src, count=1)
os.makedirs(path, exist_ok=True)
open(os.path.join(path, 'index.html'), 'w', encoding='utf-8').write(src)
eds = sorted([d for d in os.listdir('archive') if os.path.isdir(os.path.join('archive', d))], reverse=True)
rows = ''.join(f'<li><a href="/archive/{d}/">{d[:10]} {d[11:13]}:{d[13:15]} ET</a></li>' for d in eds)
open('archive/index.html', 'w', encoding='utf-8').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Every edition | Warning Shots</title><meta name="robots" content="noindex"><style>body{font:16px/1.5 Arial,sans-serif;max-width:640px;margin:40px auto;padding:0 16px;background:#F4F3EF;color:#0A111E}a{color:#0A111E}</style></head><body><h1>Every edition</h1><p>Frozen copies of the Warning Shots front page as published at each refresh, from Oct 26, 2026. <a href="/">The live page</a> · <a href="/index/#changelog">The changelog</a></p><ul>' + rows + '</ul></body></html>')
print('snapshot', path, 'edition', meta.get('edition'), '|', len(eds), 'editions archived')
