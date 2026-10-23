// Renders a 1200x630 share card for every dispatch (incidents, cases, milestones) from the page's own data.
// node make_cards.mjs [url] — writes cards/<kind>-<id>.jpg and cards/manifest.json; re-renders only changed records.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
const url = process.argv[2] || 'http://127.0.0.1:8765/index.html';
const here = path.dirname(new URL(import.meta.url).pathname);
const outDir = path.join(here, 'cards'); fs.mkdirSync(outDir, { recursive: true });
const manifestPath = path.join(outDir, 'manifest.json');
const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, 'utf8')) : {};
const hash = (o) => crypto.createHash('sha1').update(JSON.stringify(o)).digest('hex').slice(0, 12);
const data = (f) => JSON.parse(fs.readFileSync(path.join(here, 'data', f + '.json'), 'utf8'));
const meta = data('meta');
const records = { i: Object.fromEntries(data('incidents').map((r) => [r.id, r])), c: Object.fromEntries(data('fixes').map((f) => [f.incident_id, f])), m: Object.fromEntries(data('capabilities').map((c) => [c.id, c])), n: Object.fromEntries(data('news').filter((n) => n.siren).map((n) => [n.id, n])) };
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
const page = await (await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1, reducedMotion: 'reduce' })).newPage();
await page.goto(url, { waitUntil: 'networkidle' }); await page.waitForFunction(() => window.__ready, null, { timeout: 15000 }); await page.waitForTimeout(300);
const ids = await page.evaluate(() => window.WS.ids());
let made = 0, kept = 0;
for (const kind of ['i', 'c', 'm', 'n']) {
  for (const id of ids[kind]) {
    const rec = records[kind][id]; const key = kind + '-' + id; const h = hash({ rec, v: 2 });
    const file = path.join(outDir, key + '.jpg');
    if (manifest[key] === h && fs.existsSync(file)) { kept++; continue; }
    const dataUrl = await page.evaluate(async ([k, i]) => window.WS.card(k, i, 1200, 630), [kind, id]);
    if (!dataUrl) { console.log('skip', key); continue; }
    fs.writeFileSync(file, Buffer.from(dataUrl.split(',')[1], 'base64'));
    manifest[key] = h; made++;
  }
}
// drop cards for records that no longer exist
for (const key of Object.keys(manifest)) { const [kind, ...rest] = key.split('-'); const id = rest.join('-'); if (!records[kind] || !records[kind][id]) { delete manifest[key]; try { fs.unlinkSync(path.join(outDir, key + '.jpg')); } catch (e) {} } }
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 0));
await browser.close();
console.log('cards: rendered', made, 'unchanged', kept, 'as of', meta.as_of);
