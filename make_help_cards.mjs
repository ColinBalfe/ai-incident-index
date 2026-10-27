// Share images for the help pages (1200x630): node make_help_cards.mjs. Text-only template cards, no photos of real people or incidents.
import { chromium } from 'playwright';
import fs from 'fs';
const sets = [['help', 'What to do', JSON.parse(fs.readFileSync('research/help.json', 'utf8'))], ['learn', 'Know what it means', JSON.parse(fs.readFileSync('research/learn.json', 'utf8'))], ...(fs.existsSync('data/forecast_cards.json') ? [['forecast', 'Warning Shots forecast', JSON.parse(fs.readFileSync('data/forecast_cards.json', 'utf8'))]] : [])];
for (const [d] of sets) fs.mkdirSync('assets/' + d, { recursive: true });
const mark = fs.readFileSync('assets/mark.svg', 'utf8');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
const pg = await b.newPage({ viewport: { width: 1200, height: 630 } });
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
for (const [dir, lab, pages] of sets) for (const p of pages) {
  const html = `<html><head><style>@font-face{font-family:P;src:url(file://${process.cwd()}/assets/fonts/playfair-display-latin-900-normal.woff2)}@font-face{font-family:P7;src:url(file://${process.cwd()}/assets/fonts/playfair-display-latin-700-normal.woff2)}
  body{margin:0;width:1200px;height:630px;background:#0A111E;color:#F4F3EF;font-family:Arial,Helvetica,sans-serif;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:56px 64px;border-top:14px solid #C0391B}
  .k{font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#FF5B3E;font-size:24px}
  h1{font-family:P,Georgia,serif;font-weight:900;font-size:78px;line-height:1.04;margin:18px 0 0}
  .f{display:flex;align-items:center;gap:18px;font-size:24px;color:#C9D3DE} .f svg{width:64px;height:64px}</style></head>
  <body><div><div class="k">${lab} · ${esc(p.kicker)}</div><h1>${esc(p.h1)}</h1></div><div class="f">${mark}<span><b style="color:#fff;letter-spacing:.16em;font-family:P7,Georgia,serif;font-weight:700">WARNING SHOTS</b> · Every fact sourced · warningshots.ai</span></div></body></html>`;
  await pg.setContent(html, { waitUntil: 'networkidle' });
  await pg.screenshot({ path: `assets/${dir}/${p.slug}.png` });
}
await b.close(); console.log('cards done');
