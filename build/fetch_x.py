"""Pull the exact text of each X post in research/x_posts.json so the homepage can show it as it looks on X.

Uses X's public embed data (the same source X's own embedded posts use). Writes research/x_cache.json,
keyed by entry id. A post that can't be fetched keeps its last cached copy; a post never fetched is
shown from our own fields only. Run from the repo root: python3 build/fetch_x.py
"""
import html, json, re, sys, urllib.request

SRC, OUT = 'research/x_posts.json', 'research/x_cache.json'


def token(tid):
    # same derivation X's embed client uses
    x = (int(tid) / 1e15) * 3.141592653589793
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    ip, fp = int(x), x - int(x)
    s = ''
    while ip:
        s = digits[ip % 36] + s; ip //= 36
    s = (s or '0') + '.'
    for _ in range(12):
        fp *= 36; d = int(fp); s += digits[d]; fp -= d
    return re.sub(r'(0+|\.)', '', s)


def clean(t):
    text = t.get('text', '')
    a, b = (t.get('display_text_range') or [0, len(text)])[:2]
    ents = t.get('entities') or {}
    for u in ents.get('urls', []) or []:
        text = text.replace(u.get('url', ''), u.get('display_url') or u.get('expanded_url') or '')
    for m in ents.get('media', []) or []:
        text = text.replace(m.get('url', ''), '')
    # trim to the visible range (drops trailing media links and leading reply handles)
    vis = t.get('text', '')[a:b]
    if vis and vis != t.get('text', ''):
        lead = t.get('text', '')[:a]
        text = text[len(lead):] if text.startswith(lead) else text
    text = html.unescape(re.sub(r'\s*https://t\.co/\S+\s*$', '', text)).strip()
    u = t.get('user') or {}
    out = {
        'name': u.get('name', ''), 'handle': u.get('screen_name', ''),
        'avatar': (u.get('profile_image_url_https') or '').replace('_normal.', '_bigger.'),
        'verified': bool(u.get('is_blue_verified') or u.get('verified')),
        'created_at': t.get('created_at', ''), 'text': text, 'id': t.get('id_str', ''),
        'photos': [m.get('media_url_https') for m in (t.get('mediaDetails') or []) if m.get('type') == 'photo'][:1],
        'photo_alts': [(m.get('ext_alt_text') or '').strip() for m in (t.get('mediaDetails') or []) if m.get('type') == 'photo'][:1],  # the author's own alt text, when given
    }
    vids = [m for m in (t.get('mediaDetails') or []) if m.get('type') in ('video', 'animated_gif')]
    if vids:  # a clip: keep only the poster frame and length; the clip itself plays in X's own embedded player
        v = vids[0]
        out['video'] = {'poster': v.get('media_url_https', ''), 'ms': (v.get('video_info') or {}).get('duration_millis') or 0, 'gif': v.get('type') == 'animated_gif'}
    return out


def fetch(tid):
    url = f'https://cdn.syndication.twimg.com/tweet-result?id={tid}&lang=en&token={token(tid)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (WarningShots refresh)'})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    if d.get('__typename') == 'TweetTombstone' or not d.get('text'):
        raise ValueError('unavailable')
    out = clean(d)
    if d.get('note_tweet'):
        out['truncated'] = True  # a long post: X's embed data carries only the start
    if d.get('quoted_tweet'):
        out['quoted'] = clean(d['quoted_tweet'])
    return out


def main():
    posts = json.load(open(SRC, encoding='utf-8'))
    try:
        cache = json.load(open(OUT, encoding='utf-8'))
    except (OSError, ValueError):
        cache = {}
    ok = bad = 0
    for p in posts:
        m = re.search(r'(?:x|twitter)\.com/[^/]+/status/(\d+)', p.get('url', ''))
        if not m:
            continue
        try:
            cache[p['id']] = fetch(m.group(1)); ok += 1
        except Exception as e:  # keep the last good copy
            bad += 1; print(f'  could not fetch {p["id"]}: {e}', file=sys.stderr)
    json.dump(cache, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'x posts: {ok} fetched, {bad} failed, {len(cache)} cached')
    return 1 if bad and not ok else 0


if __name__ == '__main__':
    sys.exit(main())
