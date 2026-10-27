# Warning Shots: the master lockup

Set Oct 27, 2026 by Colin. This is the master; every masthead, card and file follows it.

**Files** (in `assets/brand/`): `brand-sheet.png` (Colin's master sheet: primary on navy, primary on paper, icon), `warning-shots-icon.svg` and `-icon-1024.png` (the icon: W and colon on a navy square, no frame; also the site favicon and app icons), `warning-shots-lockup-dark.png` (on navy), `-light.png` (on paper), each also `-transparent.png`, and `-notag` versions without the tagline. Rendered at 2x from the live CSS; re-render if the lockup changes.

**The lockup**
- **Mark:** the serif W with a colon, top dot red, bottom dot in the ink colour. The W stands about 1.75 times the height of the wordmark's capitals, and its foot sits on the same baseline as the capitals.
- **Wordmark:** WARNING SHOTS in Playfair Display Bold (700), all capitals, letter-spacing 0.16em. It sits close to the colon, about a third of a capital's width away.
- **Tagline:** "See what’s coming." then a small red dot, then "Know what it means." Playfair Display Italic (400), letter-spacing 0.045em, about 55% of the wordmark's size, centred under it. Both phrases in the same full ink colour, never greyed.

**Colours**
- Navy `#0A111E`, paper/ink `#F4F3EF`.
- Red `#FF3300` on dark; `#E02B00` on light.

**Rules**
- The tagline never outweighs the wordmark.
- The red appears only in the top dot of the colon and the tagline's dot.
- Small sizes (sticky nav, inner-page headers) use the mark plus wordmark without the tagline, same font and spacing.
- Never redraw the mark or set the wordmark in another typeface.
- No AI-generated variants of the logo.

**Where it lives in code**
- **Homepage masthead:** `index.template.html`, in `.logo`, `.wordmark` and `.mh-tag`.
- **Inner pages:** `assets/dispatch.css`, in `.logo .wm`.
- **Share cards:** `make_og.mjs` and `make_help_cards.mjs`, in the footer wordmark.
