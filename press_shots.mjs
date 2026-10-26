// Press screenshots: node press_shots.mjs (local server on :8765). Run when the design changes, not every refresh.
import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
for (const [path, out, vp] of [['/', 'front-desktop', { width: 1280, height: 860 }], ['/', 'front-phone', { width: 390, height: 844 }], ['/index/', 'record-desktop', { width: 1280, height: 860 }], ['/php2shell/', 'tracker-desktop', { width: 1280, height: 860 }]]) {
  const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: vp.width < 500 ? 2 : 1.5, colorScheme: 'light', reducedMotion: 'reduce' });
  const p = await ctx.newPage(); await p.goto('http://127.0.0.1:8765' + path, { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
  await p.screenshot({ path: `assets/press/${out}.jpg`, type: 'jpeg', quality: 78 }); await ctx.close();
}
await b.close(); console.log('press shots done');
