#!/bin/sh
# Make the page-rendering scripts (prerender.mjs, shot.mjs, make_*.mjs) find Playwright.
# They import 'playwright' as an ES module, which only looks in ./node_modules, not in the
# global install. Link the machine's preinstalled Playwright there instead of installing
# another copy (a second version would not find the preinstalled browser).
# Safe to run every time; does nothing if Playwright is already importable.
cd "$(dirname "$0")" || exit 1
if node --input-type=module -e "await import('playwright')" >/dev/null 2>&1; then
  echo "playwright: ok"
  exit 0
fi
G="$(npm root -g 2>/dev/null)"
if [ -d "$G/playwright" ]; then
  mkdir -p node_modules
  ln -sfn "$G/playwright" node_modules/playwright
  [ -d "$G/playwright-core" ] && ln -sfn "$G/playwright-core" node_modules/playwright-core
else
  # No global copy on this machine: fall back to the version in package.json.
  npm install --no-save --no-audit --no-fund playwright >/dev/null 2>&1
fi
if node --input-type=module -e "await import('playwright')" >/dev/null 2>&1; then
  echo "playwright: linked"
else
  echo "playwright: NOT FOUND - prerender.mjs and shot.mjs will fail; do not publish" >&2
  exit 1
fi
