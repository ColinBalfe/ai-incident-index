// PNG copies of every chart (assets/charts/<id>.svg -> <id>.png, 2400x1350) for sharing and press. Needs the local server.
// node make_charts.mjs http://127.0.0.1:8765
import { chromium } from 'playwright';
import fs from 'fs';
const base = process.argv[2] || 'http://127.0.0.1:8765';
const b = await chromium.launch({ executablePath: fs.existsSync('/opt/pw-browsers/chromium-1243/chrome-linux64/chrome') ? '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' : undefined });
const p = await b.newPage({ viewport: { width: 1200, height: 1350 }, deviceScaleFactor: 2 });
let n = 0;
for (const f of fs.readdirSync('assets/charts').filter((f) => f.endsWith('.svg'))) {
  const png = 'assets/charts/' + f.replace(/\.svg$/, '.png');
  if (fs.existsSync(png) && fs.statSync(png).mtimeMs >= fs.statSync('assets/charts/' + f).mtimeMs) continue;
  const svg = fs.readFileSync('assets/charts/' + f, 'utf8');
  const [, vw, vh] = /viewBox="0 0 (\d+) (\d+)"/.exec(svg) || [0, 1200, 675];
  await p.setViewportSize({ width: +vw, height: +vh });
  await p.goto(base + '/robots.txt').catch(() => {});
  await p.setContent(`<!doctype html><html><head><base href="${base}/"><style>
@font-face{font-family:Archivo;src:url(/assets/fonts/archivo-latin-standard-normal.woff2);font-weight:400 900}
@font-face{font-family:Playfair;src:url(/assets/fonts/playfair-display-latin-700-normal.woff2);font-weight:700}
@font-face{font-family:Playfair;src:url(/assets/fonts/playfair-display-latin-900-normal.woff2);font-weight:900}
html,body{margin:0}svg{display:block;width:${vw}px;height:${vh}px}</style></head><body>${svg}</body></html>`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: png, clip: { x: 0, y: 0, width: +vw, height: +vh } });
  n++;
}
await b.close();
console.log(`charts: ${n} png written`);
