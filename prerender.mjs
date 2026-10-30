// Prerender the first screen into index.html: node prerender.mjs [url] [file]
// The page draws the lead, the incident timeline and the level, Latest stories and the scoreboard from data/*.json in the browser. Baking that
// markup into index.html at build time means the headline is in the first paint instead of waiting for d3, app.js and the
// data bundle; the script then redraws the same markup and nothing moves. Run after build_site.py, before make_og.mjs.
import { chromium } from 'playwright';
import fs from 'fs';
const url = process.argv[2] || 'http://127.0.0.1:8765/index.html';
const file = process.argv[3] || new URL('./index.html', import.meta.url).pathname;
const IDS = ['wall-lead', 'itl-fig', 'itl-level', 'itl-live', 'latest-body', 'rail', 'wall', 'edition', 'tb-updated']; // the lead, the timeline (its chart as a same-size placeholder) with the level, Latest stories, the scoreboard and the deeper sections
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
// A phone-width context: the Wire board shows its short form (12 stories) below 760px, so the phone's first paint is final; wider screens extend the board when the script runs.
const page = await (await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, reducedMotion: 'reduce', colorScheme: 'light' })).newPage();
const errs = []; page.on('pageerror', (e) => errs.push(e.message));
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.__ready === true, null, { timeout: 20000 });
await page.waitForTimeout(400);
const source = fs.readFileSync(file, 'utf8');
const out = await page.evaluate(([src, ids]) => {
  const doc = new DOMParser().parseFromString(src, 'text/html');
  const done = [];
  for (const id of ids) {
    const live = document.getElementById(id), tgt = doc.getElementById(id);
    if (!live || !tgt) continue;
    // copy attributes that the script sets (hidden, class, style, href, title) and the rendered children
    for (const a of ['hidden', 'class', 'style', 'href', 'title']) { if (live.hasAttribute(a)) tgt.setAttribute(a, live.getAttribute(a)); else tgt.removeAttribute(a); }
    tgt.innerHTML = live.innerHTML;
    done.push(id);
  }
  // the Seismograph is drawn (and replayed) by the script; bake only a same-size placeholder so nothing jumps
  doc.querySelectorAll('.seis').forEach((n) => { const ph = doc.createElement('div'); ph.className = 'seis-ph'; ph.innerHTML = '<a href="/index/#all">Every AI incident on the record, scored and sourced →</a>'; n.replaceWith(ph); }); // without the script, a way to the same records
  // the ticker's measured animation is reapplied by the script; keep it still until then
  const run = doc.getElementById('ticker-run'); if (run) { run.classList.remove('go'); run.removeAttribute('style'); }
  doc.documentElement.setAttribute('data-prerendered', '1');
  return { html: '<!doctype html>\n' + doc.documentElement.outerHTML + '\n', done };
}, [source, IDS]);
await browser.close();
if (errs.length) { console.error('page errors:', errs); process.exit(1); }
if (out.done.length < IDS.length - 3) { console.error('prerender: only filled', out.done.join(', ')); process.exit(1); }
fs.writeFileSync(file, out.html);
console.log('prerendered', out.done.length, 'blocks into', file.split('/').pop(), '(' + Math.round(out.html.length / 1024) + ' KB)');
