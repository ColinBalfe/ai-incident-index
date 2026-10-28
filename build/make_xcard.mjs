// Renders build/xcard_out/xcard-{navy,white}.html to PNG (1080x1350 at 2x). Needs the local server on :8765 (REFRESH step 3).
import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
for (const t of ['navy', 'white']) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await p.goto(`http://localhost:8765/build/xcard_out/xcard-${t}.html`, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const over = await p.evaluate(() => { const c = document.querySelector('.c'); return c.scrollHeight - c.clientHeight; });
  if (over > 0) console.log(`WARNING ${t}: text overflows by ${over}px; shorten the lead's people line`);
  await p.screenshot({ path: `build/xcard_out/warning-shots-today-${t}.png`, clip: { x: 0, y: 0, width: 1080, height: 1350 } }); await p.close();
}
await b.close(); console.log('xcard rendered');
