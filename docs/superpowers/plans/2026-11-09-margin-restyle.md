# Margin Restyle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle shahbazac.com in the Margin direction: EB Garamond, warm paper, one red accent, tiled home page with FIX Parser as a wide feature tile, a quiet footer theme switch on every page, edged screenshots.

**Architecture:** Nearly everything is CSS in `css/site.css`, plus small markup changes in the home page, the cards include and the layouts. A stdlib Python script, `tests/check_site.py`, checks the built `_site` (fonts, third-party loads, token contrast in both themes, print colours, feature tile, theme switch on every page, old-post cleanup) and serves as the failing test for each task. Visual checks run in the browser pane against the Jekyll dev server.

**Tech Stack:** Jekyll (GitHub Pages gem set) run in Docker, plain CSS, Liquid, Python 3 stdlib for checks, fontTools for font subsetting, headless Chrome for the share image.

**Spec:** `docs/superpowers/specs/2026-11-09-margin-design.md` (read it first). The visual reference is the Margin direction in `docs/design/home-directions.html`; open it in a browser and copy its proportions.

## Global Constraints

- Colour tokens exactly as in the spec. Light: `--bg #f7f5ef`, `--text #1c1b19`, `--muted #6b665d`, `--accent #a3201a`, `--line #dcd7cc`. Dark: `--bg #1c1a17`, `--text #e8e4da`, `--muted #a59f93`, `--accent #e26a5c`, `--line #3a3631`.
- Screenshot edge: light is a 1px `#d3cdc0` border plus a `0 1px 2px rgba(60,45,25,.10), 0 6px 16px -10px rgba(60,45,25,.40)` shadow. Dark is a 1px `#776f64` border with no shadow. Radius 2px at most. No hover lift.
- The FIX Parser line, verbatim: `A standard tool for much of Wall Street. From the largest banks to the smallest trading firms.`
- No usage numbers and no firm names anywhere on the site or in the repo.
- No third-party requests except Google Analytics in production builds. Fonts are self-hosted.
- Dark is set in two places that must match: `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {…} }` and `:root[data-theme="dark"] {…}`.
- Printing always uses the light tokens.
- WCAG AA: text tokens at least 4.5:1 against their background, the dark screenshot edge at least 3:1, visible focus, and the switch keeps `aria-pressed`.
- Don't edit `_pages/resume.html` or its generator, and don't touch `/skills/`.
- Keep the `seo.html` and `analytics.html` includes, `llms.txt` and `/resume.md` unchanged.
- Commit on branch `site/margin-design` only. No push and no merge until Shahbaz asks; when he does, use `git merge --no-ff`. No `Co-Authored-By` or "Generated with" lines in commits.

## Review Focus

1. **Theme chosen against the system.** Choosing Dark on a light-mode machine, or Light on a dark one, must flip every token, including `--shot-edge`, `--code-bg` and `--hl-*`. Task 1's `check_tokens` compares the media-query block with the `[data-theme="dark"]` block.
2. **Printing the resume while dark is active.** It should print dark text on white with no footer. Task 1's `check_print` checks the `@media print` tokens, and Task 6 prints a PDF from dark mode.
3. **Phone width (375px).** No horizontal scroll on home, resume or the 2017 post. The FIX Parser tile stacks, and long URLs and code wrap or scroll inside their box. Task 4 and Task 8 check `scrollWidth`.
4. **The font fails or is slow to load.** Text should render in Georgia straight away and swap later. Task 1's `check_fonts` requires `font-display: swap` and the fallback stack.
5. **Old posts with inline fixed widths, tables and code.** They should stay readable in Garamond on both themes. Task 6 checks the 2015 exchange post and the 2017 JavaScript post visually.

## Commands used throughout

Build (dev build, no analytics), run from the repo root:

```bash
docker run --rm -v "$PWD":/srv/site -w /srv/site -e BUNDLE_PATH=/srv/site/vendor/bundle ruby:3.3 bundle exec jekyll build
```

Check:

```bash
python3 -I tests/check_site.py _site
```

To look at pages, run the `jekyll` config in `.claude/launch.json` with `preview_start`; it serves on port 4000. Docker must be running.

---

### Task 0: Commit the design record

**Files:**
- Already modified: `_config.yml` (exclude `docs`), `docs/design/home-directions.html`, `docs/superpowers/specs/2026-11-09-margin-design.md`, this plan.

- [ ] **Step 1: Add `tests` and `tools` to `exclude` in `_config.yml`**, after `'docs'`.
- [ ] **Step 2: Commit**

```bash
git add _config.yml docs/
git commit -m "Margin design: the four directions mockup, design doc and plan"
```

### Task 1: Site check script (the failing tests)

**Files:**
- Create: `tests/check_site.py`

**Interfaces:**
- Produces: `python3 -I tests/check_site.py <site_dir>` prints one `PASS name` or `FAIL name: reason` line per check, and exits 1 if any check failed. Each check is a function `check_<name>(site: Path) -> list[str]` that returns its failure reasons. Stdlib only (`re`, `pathlib`, `html.parser` or regex).
- Later tasks rely on these token names in `css/site.css`: `--bg --surface --text --muted --accent --accent-soft --line --code-bg --shot-edge --shot-shadow --serif --sans --mono --hl-comment --hl-keyword --hl-string --hl-number --hl-function --hl-class --hl-operator`.

- [ ] **Step 1: Write the checks** in `tests/check_site.py`:

| Check | Fails when |
|---|---|
| `check_fonts` | `_site/css/site.css` lacks an `@font-face` for each of `/fonts/eb-garamond/eb-garamond-400.woff2`, `eb-garamond-400-italic.woff2` and `eb-garamond-500.woff2`; any of those files is missing from `_site`; any `@font-face` lacks `font-display: swap`; or `--serif` doesn't start with `"EB Garamond"` and contain `Georgia`. |
| `check_no_third_party` | any built `.html` has a `<link href>`, `<script src>`, `<img src>` or `<iframe src>` starting `http:`, `https:` or `//`, other than `https://www.googletagmanager.com/`. Links in `<a href>` are fine. Also fails if `site.css` has `url(http` or `url(//`. |
| `check_tokens` | Parse custom properties from the first `:root {` block (light), the `:root:not([data-theme="light"])` block inside the dark media query, and the `:root[data-theme="dark"]` block. Fails if the two dark blocks differ in any property; if the five spec tokens don't equal the Global Constraints values; if, in either theme, `--text`, `--muted` or `--accent` is under 4.5:1 against `--bg`, or any `--hl-*` or `--muted` is under 4.5:1 against `--code-bg`; or if the dark `--shot-edge` is under 3:1 against the dark `--bg`. The light edge is a soft border helped by its shadow and has no ratio requirement. Use the WCAG relative-luminance formula. |
| `check_print` | `site.css` has no `@media print` block that sets `--bg`, `--text`, `--muted`, `--accent` and `--line` to the light values, and hides `.site-footer`. |
| `check_home` | `_site/index.html` doesn't have exactly one element whose class list contains `feature`; that element doesn't contain both `FIX Parser` and the exact FIX line from Global Constraints; or the FIX line appears anywhere else on the page. |
| `check_theme_switch` | any of `index.html`, `resume.html`, `privacy.html`, `404.html` or every post page under `_site/20*/` lacks three `data-theme-choice` buttons (`auto`, `light`, `dark`), or lacks the pre-paint `localStorage.getItem("theme")` script. |
| `check_old_posts` | any built post contains `style="color`; any built page contains `maxcdn.bootstrapcdn.com`; or the 2017 JavaScript post has no `class="fix-tag"`. |
| `check_retired_styles` | `site.css` still contains `--ink`, `translateY(`, `border-radius: 99px`, `text-transform: uppercase` or `border-top: 8px` (template look and black strip, per the anti-goals). |

- [ ] **Step 2: Build and run the checks.**
  Expected: `check_fonts`, `check_tokens`, `check_print`, `check_home`, `check_old_posts` and `check_retired_styles` FAIL. `check_theme_switch` and `check_no_third_party` (apart from maxcdn) PASS.
- [ ] **Step 3: Commit** `tests/check_site.py` with message `Site checks for the Margin restyle`.

### Task 2: Self-hosted EB Garamond

**Files:**
- Create: `tools/subset-fonts.sh`, `fonts/eb-garamond/eb-garamond-400.woff2`, `fonts/eb-garamond/eb-garamond-400-italic.woff2`, `fonts/eb-garamond/eb-garamond-500.woff2`, `fonts/eb-garamond/OFL.txt`
- Modify: `css/site.css` (top of file), `_layouts/default.html` (head)

**Interfaces:**
- Produces: the font family name `"EB Garamond"` at weights 400 and 500 (normal) and 400 (italic), and `--serif: "EB Garamond", Garamond, "Iowan Old Style", Georgia, serif`.

- [ ] **Step 1: Write `tools/subset-fonts.sh`.** It downloads `EBGaramond[wght].ttf`, `EBGaramond-Italic[wght].ttf` and `OFL.txt` from `https://github.com/google/fonts/raw/main/ofl/ebgaramond/` into a temp directory. It pins static instances with `python3 -m fontTools.varLib.instancer` (roman at `wght=400` and `wght=500`, italic at `wght=400`). Then it subsets each with `python3 -m fontTools.subset --flavor=woff2` using:
  - unicodes `U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2190-2193,U+2212,U+2215,U+FEFF,U+FFFD`
  - layout features `kern,liga,clig,calt,locl,onum,lnum,pnum,tnum,smcp,c2sc,frac,mark,mkmk`

  These features keep old-style figures and real small caps; the Fontsource builds drop both. Run the script. Each output is about 31 to 34 KB.
- [ ] **Step 2: Confirm the features survived:**

```bash
python3 -I -c "from fontTools.ttLib import TTFont; t=TTFont('fonts/eb-garamond/eb-garamond-400.woff2'); print(sorted({r.FeatureTag for r in t['GSUB'].table.FeatureList.FeatureRecord}))"
```

  Expected: the list includes `onum` and `smcp`.
- [ ] **Step 3: Add the three `@font-face` rules** (each with `font-display: swap`) at the top of `site.css`, and set `--serif` to the stack above.
- [ ] **Step 4: Preload the regular weight.** In `_layouts/default.html`, before the stylesheet, add `<link rel="preload" href="/fonts/eb-garamond/eb-garamond-400.woff2" as="font" type="font/woff2" crossorigin>`.
- [ ] **Step 5: Build and check.** Expected: `check_fonts` PASS.
- [ ] **Step 6: Commit** with message `Self-hosted EB Garamond with old-style figures and small caps`.

### Task 3: Tokens, base type, header and footer

**Files:**
- Modify: `css/site.css` (the token blocks, base, `.site-header`, `.site-footer`, `.theme-toggle`, and a new `@media print`)

**Interfaces:**
- Consumes: `--serif` from Task 2.
- Produces: every token listed in Task 1. `--sans` and `--serif` are both the EB Garamond stack, kept as aliases because the resume's inline styles use them. `--accent-soft` is a pale tint of the accent (light about `#f1e4df`, dark about `#2e221f`). `--surface` equals `--bg`.

- [ ] **Step 1: Rewrite the three token blocks** with the spec values.
  - Add `--code-bg` (light about `#efece4`, dark about `#25221e`).
  - Add `--shot-edge` and `--shot-shadow` with the Global Constraints values.
  - Retune the `--hl-*` colours so each reaches 4.5:1 on `--code-bg` in its theme. They should be muted inks that suit paper, with the keyword colour near the accent red.
  - Delete `--ink`.
- [ ] **Step 2: Base rules.**
  - Body: `font: 1.28rem/1.5 var(--serif)` with `font-variant-numeric: oldstyle-nums`. Remove the 8px top border.
  - Headings: weight 400 or 500, never 600 or 700.
  - Links: `--accent`.
  - Focus outlines: `--accent`.
  - `.wrap` max-width: 66rem.
- [ ] **Step 3: Header.** The site name is EB Garamond at weight 400. Nav links are muted small caps (`font-variant-caps: all-small-caps; letter-spacing: .07em`) and turn accent on hover. Keep the hairline under the header.
- [ ] **Step 4: Footer.**
  - Plain paper, with a `--line` hairline on top of `.wrap` and no background.
  - Muted, italic copyright.
  - Social links in muted small caps; hide the `.social svg` icons site-wide (builder's call: the mockup is text-only).
  - Switch buttons: muted small caps, no borders or padding box, the pressed one in `--accent`, and normal hover to `--text`.
  - Remove the hard-coded `#c8c8c8`, `#9a9a9a`, `#fff` and `#555`.
- [ ] **Step 5: Print block.** Add `@media print` that sets the five light tokens plus `--code-bg`, `--hl-*` and the light `--shot-*` values on `:root` and `:root[data-theme="dark"]`. Hide `.site-header`, `.site-footer` and `.skip`. Use a white `body` background.
- [ ] **Step 6: Build and check.** Expected: `check_tokens`, `check_print` and `check_retired_styles` PASS. If `check_retired_styles` still finds `translateY(` or the pill radius, those go in Task 4.
- [ ] **Step 7: Commit** with message `Margin colours, type, header and footer`.

### Task 4: Home page tiles with the FIX Parser feature

**Files:**
- Modify: `_includes/cards.html`, `index.html`, `_data/apps.yml` (FIX Parser entry), `css/site.css` (the home sections)

**Interfaces:**
- Consumes: the tokens from Task 3.
- Produces:
  - `{% include cards.html items=… feature=true %}` puts the class `feature` on the first item only.
  - An optional `note` field on an item renders as `<p class="app-claim">` only on a feature item.
  - Existing class names stay: `.apps`, `.app`, `.app-shot`, `.app-body`, `.app-meta`, `.app-tag`, `.app-since`, `.app-url`.

- [ ] **Step 1: Add `note`.** Add `note:` to the FIX Parser entry in `apps.yml` with the exact FIX line. Update the file's header comment to say `note` is shown only on the wide first tile.
- [ ] **Step 2: Update `cards.html`.**
  - Add `feature` to the first `<li>` class when `include.feature` is true.
  - Render `app.note` as `<p class="app-claim">` after the description, only on that item.
  - Drop the `→` after the URL.
- [ ] **Step 3: Update `index.html`.**
  - Pass `feature=true` for apps only.
  - Add `<p class="tagline">{{ site.tagline }}</p>` under the `<h1>`.
  - In each writing row, put the excerpt div first and the `<time>` second, so the date sits in the right-hand margin column.
- [ ] **Step 4: Home CSS, copying the Margin mockup's proportions.**
  - Hero:
    - text column 34rem
    - h1 weight 400 at `clamp(2.6rem, 6vw, 3.7rem)`
    - italic muted tagline
    - social links in accent small caps
  - Section h2: italic, weight 400, about 2.1rem, no underline rule.
  - `.apps` grid:
    - three equal columns, gap about `2.75rem 2.25rem`
    - each card is no box: no border, background or radius, and no transform or shadow on hover; hover turns the h3 accent
    - `.app-shot` uses `--shot-edge` and `--shot-shadow` with a 2px radius
    - `.app-tag` is accent small caps
    - `.app-since` is muted lowercase
    - `.app-url` is muted italic in the body face
  - `.app.feature`:
    - spans the full row, as an inner three-column grid
    - shot across columns 1–2, text in column 3
    - h3 about 2rem
    - `.app-claim` italic
  - At 56rem and below: two columns, and the feature stacks. At 36rem and below: one column.
  - Writing rows: grid `minmax(0, 34rem) minmax(0, 15rem)`, column gap 3.5rem, muted date. At 40rem and below, a single column with the date under the excerpt. No row rules.
- [ ] **Step 5: Build and check.** Expected: `check_home` and `check_retired_styles` PASS.
- [ ] **Step 6: Look at it.**
  - Start the `jekyll` preview and open `/`.
  - Screenshot it in light and in dark (set `document.documentElement.dataset.theme`), and compare against `docs/design/home-directions.html#margin`.
  - At 375px wide, run `document.documentElement.scrollWidth === innerWidth`. Expected: `true`.
- [ ] **Step 7: Commit** with message `Home page in Margin: tiles, FIX Parser feature tile, writing dates in the margin`.

### Task 5: Posts, privacy, 404 and code

**Files:**
- Modify: `css/site.css` (post pages, `.page`, `pre`/`code`, highlight rules, `.post-nav`)

**Interfaces:**
- Consumes: the tokens from Task 3.

- [ ] **Step 1: Post page.**
  - `.post` and `.page` measure: 34rem of text, with the wrap padding outside it.
  - `.post-date`: muted small caps (replace the uppercase).
  - h1 weight 400.
  - `.post-body`: same face and size as the body.
- [ ] **Step 2: Blocks.**
  - Blockquotes: italic, no left bar, indented 1.5rem.
  - Tables: body face, hairline `--line` rules on rows only, `display: block; overflow-x: auto` kept.
  - `pre`: `--code-bg`, 2px radius.
  - Inline `code`: `--code-bg`.
  - Code font size: `.8em`, since Garamond's x-height is small next to the mono stack.
- [ ] **Step 3: `.post-nav`.** Hairline on top, links in accent, titles in italic.
- [ ] **Step 4: Build, check and look.**
  - Expected: all checks except `check_old_posts` PASS.
  - Open one post with code (`/2015/01/05/financial-exchange.html`), `/privacy` and `/404.html`, in both themes. Code tokens should be readable and nothing should overflow at 375px.
- [ ] **Step 5: Commit** with message `Posts, privacy and 404 pages in Margin`.

### Task 6: Resume overrides and old-post cleanup

**Files:**
- Modify: `css/site.css` (resume overrides and the `fix-*` classes), `_posts/2017-05-15-trading-tools-in-javascript.md`, `_posts/2015-01-30-composingcontracts.md`

**Interfaces:**
- Produces: the classes `fix-tag` (colour `--accent`), `fix-sep` (colour `--muted`) and `fix-val` (colour `--text`).

- [ ] **Step 1: Resume overrides.** The resume's inline `<style>` sits in the body after `site.css`, so use selectors one class stronger (`.page .resume …`):
  - h1 and h2 at weight 400.
  - h2 with no bottom border; italic, like the home section headings.
  - `.entry-head h3` at weight 500.
  - `details.more > ul` with radius 0.
  - The resume measure may stay at 46rem; tables of dates need the room.
- [ ] **Step 2: Clean up the 2017 post.**
  - Replace `style="color: #993300;"` with `class="fix-tag"`, `style="color: #999999;"` with `class="fix-sep"` and `style="color: #000000;"` with `class="fix-val"` (a scripted `sed`, counts 87, 250 and 4).
  - Point its Font Awesome `<link>` at `/css/font-awesome.css`. That's version 4.0.3, which has `.fa-warning`.
  - Make the same link change in the composing-contracts post.
  - Don't change any words.
- [ ] **Step 3: Build and check.** Expected: every check PASSes.
- [ ] **Step 4: Look at it.**
  - Open `/resume` in light and dark, at desktop width and at 375px.
  - Open the 2017 post and check that the FIX tag numbers read in the accent in both themes and the warning icons show.
  - Print `/resume` from dark mode to confirm the Review Focus 2 case. Run headless Chrome `--print-to-pdf` on the dev URL after setting `localStorage.theme = "dark"` (or run `window.print()` in the pane with dark set) and look at the PDF: dark text on white, no footer.
- [ ] **Step 5: Commit** with message `Resume and old posts in Margin colours; Font Awesome served locally`.

### Task 7: Share image

**Files:**
- Create: `docs/design/og-image.html`
- Modify: `img/og-default.png`

- [ ] **Step 1: Write `docs/design/og-image.html`.** It's a 1200×630 page:
  - background `#f7f5ef`
  - "Shahbaz Chaudhary" in EB Garamond 400, about 104px
  - the tagline in italic `#6b665d`
  - `shahbazac.com` in `#a3201a` small caps
  - a `#dcd7cc` hairline
  - fonts loaded from `../../fonts/eb-garamond/`

  Use generous left alignment, with no boxes, as in the hero.
- [ ] **Step 2: Render it:**

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=1 --window-size=1200,630 --screenshot="$PWD/img/og-default.png" "file://$PWD/docs/design/og-image.html"
```

  Expected: `file img/og-default.png` reports `1200 x 630`. Open the PNG and confirm Garamond rendered (not Georgia) and the figures are old-style.
- [ ] **Step 3: Commit** with message `Share image redrawn in Margin colours`.

### Task 8: Whole-site pass

- [ ] **Step 1: Run the build and every check.** Expected: all PASS.
- [ ] **Step 2: Theme switch round trip.** On `/` and `/resume`:
  1. Click Dark, reload: the page stays dark and Dark is pressed.
  2. Click Light: everything flips, with `--shot-edge` at `rgb(211, 205, 192)`.
  3. Click Auto: `localStorage.theme` is gone.
- [ ] **Step 3: Overflow at 375px.** Run `scrollWidth === innerWidth` on `/`, `/resume`, `/privacy` and both old posts. Expected: `true` on each.
- [ ] **Step 4: Screenshots for Shahbaz:** home in light and in dark, the FIX Parser tile close up in dark, and the resume in dark.
- [ ] **Step 5: Final commit if anything changed.** Then report. Don't merge or push.
