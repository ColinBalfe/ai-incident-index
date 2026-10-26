#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Naver, Seznam; Bing feeds DuckDuckGo and ChatGPT search) which pages changed.
Run after the push has deployed. Submits the front page, the live tracker, the incident index and pages for incidents disclosed
in the last 48 hours (data/fresh_urls.json, written by build_pages.py). The key file 9a423bc0bf936048cfebe22836aec515.txt at the site root proves ownership."""
import json, os, urllib.request
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
KEY = '9a423bc0bf936048cfebe22836aec515'
site = json.load(open('data/meta.json'))['site_url']
urls = [site, site + 'php2shell/', site + 'i/']
try: urls += [u for u in json.load(open('data/fresh_urls.json')) if u not in urls]
except (OSError, ValueError): pass
body = json.dumps({"host": site.split('/')[2], "key": KEY, "keyLocation": site + KEY + '.txt', "urlList": urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=20) as r: print('indexnow', r.status, len(urls), 'urls')
except Exception as e:
    print('indexnow failed:', e)
