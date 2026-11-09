# Margin: a Tufte-inspired redesign of shahbazac.com

Date: 2026-11-09. Status: draft for Shahbaz's review.

## Why

The current site (`css/site.css`, Oct 2026) works but reads as a template: a near-white
background, a system sans with serif headings, rounded 1px cards that lift on hover,
uppercase pill tags, grey body text and a safe blue link colour. Someone told Shahbaz it
looks like AI-made design. An earlier version (warm cream background, serif) looked too
much like Anthropic's own style.

Shahbaz wants more personality while staying elegant. His reference is Edward Tufte:
quiet, typographic, specific choices rather than boxes and effects.

## The four directions explored

All four were built as one mockup from the site's real content:
`docs/design/home-directions.html` (open it in a browser; the bar at the bottom switches
direction and light/dark). Shahbaz liked all four and chose **Margin**. The other three
are recorded here in case the site's direction is revisited.

| Direction | Idea | Paper (light / dark) | Accent | Type |
|---|---|---|---|---|
| **Margin** (chosen) | Tufte's restraint: all serif, one red, no boxes or shadows on text | `#f7f5ef` / `#1c1a17` | red `#a3201a` / `#e26a5c` | EB Garamond throughout |
| Ink | A fixed left column with name, intro and a section index; work tiled beside it | blue-grey `#e7ebee` / `#10161d` | ink blue `#1f4f8f` / `#8db4ea` | Source Serif 4 headings, IBM Plex Sans body, IBM Plex Mono for meta |
| Green | Deep green masthead band over sage paper; screenshots lead | sage `#e8ebe3` / `#121814`, band `#1e4636` | green `#1f5f46`, brass `#85651a` for tags | Alegreya and Alegreya Sans |
| Swiss | Very large condensed name, strict 12-column grid, section counts | cool grey `#e5e6e3` / `#151615` | signal red `#c0221a` / `#ff5b45` | Archivo (condensed widths), DM Mono |

Shared decisions that came out of the exploration:

- **Tiles, not lists**, for apps and open source projects (Shahbaz's preference). Writing
  stays a list.
- **FIX Parser leads** the Apps grid as a wide tile. It is the longest-running and most
  used project, and seven apps in a plain three-column grid would leave one tile alone.

## Goals

1. Restyle the whole site in the Margin direction: home page, post pages, the resume page,
   the privacy page and the 404 page.
2. Make FIX Parser's standing visible on the home page in one plain line, without numbers.
3. Keep a light/dark switch available but quiet.
4. Give screenshots a clear edge in both themes.

## Non-goals

- No new content sections, no changes to `_data/*.yml` ordering, no new pages.
- No Tufte-style sidenotes inside posts. The posts are plain Markdown; retrofitting them is
  separate work.
- The Skill Tracer app at `/skills/` is a separate project and keeps its own styling.

## Anti-goals (failure even if it technically works)

- **Gimmicks.** No paper textures, notebook rules, grid backgrounds, ledger lines or other
  props. Personality comes from type, colour and layout only.
- **The Anthropic look.** No beige paper combined with a coral or orange accent.
- **The template look.** No rounded cards with shadows on hover, no pill tags, no
  translate-on-hover, no uppercase tracked sans labels.
- **Numbers.** No usage figures: they go stale (Shahbaz removed the Skill Tracer count for
  that reason, commit 6155a7f) and they tell competitors too much.

## The design (decided)

### Colour

Light and dark tokens, as in the mockup:

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#f7f5ef` | `#1c1a17` | page |
| `--text` | `#1c1b19` | `#e8e4da` | body |
| `--muted` | `#6b665d` | `#a59f93` | secondary text, dates, URLs |
| `--accent` | `#a3201a` | `#e26a5c` | tags, social links, link hover, active theme choice |
| `--line` | `#dcd7cc` | `#3a3631` | hairlines, screenshot border |

The black top strip and black footer of the current site go away. The footer is plain
paper above a hairline, as in the mockup.

Dark mode: Shahbaz isn't fond of it but accepts the site needs one. It stays warm charcoal
with the lighter red, and gets one tuning pass after he has seen it on real pages.

### Type

- One family for everything: **EB Garamond**, the face Shahbaz saw and approved in the
  mockup. Self-hosted as WOFF2 (latin subset; regular, italic, medium) with
  `font-display: swap`, so the site still loads no third-party resources. Fallback stack:
  `Garamond, "Iowan Old Style", Georgia, serif`. Old-style figures throughout.
- Code stays in the existing monospace stack.
- Body around 1.28rem on the home page and in posts (Garamond runs small).
- Headings are regular or medium weight, never bold; section headings are italic.
- Tags, social links and the theme switch are small caps (the font's own if the subset
  keeps them, otherwise the browser's) with slight letter-spacing, in the accent red.

### Home page

Layout matches the Margin mockup, with tiles:

- **Introduction:** name, italic tagline, the existing lede, social links in red small
  caps. Text column about 34rem wide.
- **Apps:** a three-column tile grid. Each tile: screenshot, then tag and "since" year on
  one line, title, description, the URL in muted italic. **FIX Parser** spans the full
  row: screenshot across two columns, text in the third, larger title.
- **FIX Parser's standing:** the wide tile carries one extra line under its description,
  in italic, approved by Shahbaz:

  > A standard tool for much of Wall Street. From the largest banks to the smallest trading firms.

  No usage numbers appear anywhere on the site or in this repo: Shahbaz doesn't want to
  hand traffic figures to competitors. Firm names are never published.
- **Reference:** Skill Tracer, with its screenshot (added on master in commit eac469c), as
  an ordinary tile the same size as the app tiles, even though it is alone in its section.
- **Open source:** three text tiles (no screenshots), one per project.
- **Writing:** one row per post: title and excerpt in the text column, date in the margin
  column.
- Tablet: two columns, and the wide tiles stack. Phone: one column.

### Screenshots

Screenshots need a visible edge in both themes, because several of them are dark UIs that
sit on light paper, and light UIs that sit on dark paper:

- Light: 1px border a step darker than `--line` (about `#d3cdc0`) plus a soft, low shadow (about `0 1px 2px` and
  `0 6px 16px -10px`, warm and transparent).
- Dark: shadows don't read on charcoal, so use a lighter 1px border (about `#776f64`, roughly 3:1 against the paper so it holds up next to dark screenshots) with
  no shadow.
- Square corners or a 2px radius at most. No hover lift. Hover changes the title colour
  only.

### Light/dark switch

The footer switch from commit eac469c (Auto / Light / Dark, saved in `localStorage`,
applied before first paint) stays as it is in behaviour. Restyle it to match: muted small
caps text buttons, the active choice in the accent red, no borders. It sits in the footer
only, and the footer comes from `_layouts/default.html`, so every page that uses it gets
the switch: home, posts, resume, privacy and 404.

### Inner pages

- Header: site name in EB Garamond on the left, nav (Apps, Open source, Writing, Resume)
  in small caps on the right. A hairline under it.
- Posts: date in small caps above the title; body in EB Garamond with a 34rem measure;
  blockquotes italic with no bar; tables in the body face with hairlines; code blocks on a
  slightly darker paper (`--code-bg`), with the existing highlight colours retuned so they
  read on paper.
- Resume, privacy and 404 pages take the same type and colours.

### The resume page *(builder's call)*

`_pages/resume.html` is generated by `tools/build.py` in `~/Dropbox/resume`, outside this
repo, and carries its own inline `<style>` that uses `--sans`, `--serif` and
`--accent-soft`. The restyle does not edit the generated file or the generator. Instead
`site.css` keeps those three token names as aliases of the new tokens (`--sans` and
`--serif` both pointing at the EB Garamond stack, `--accent-soft` at a pale tint of the
red), and adds resume overrides with selectors strong enough to win over the inline block.
Updating the generator later is a separate change in that other repo.

The resume page shows the footer switch like every other page, but its existing print
rules hide the footer. Printing always uses the light colours, whatever theme is showing on
screen, so a resume printed from dark mode doesn't come out as pale text on white paper.
`site.css` sets the light tokens inside `@media print`, so this covers every page.

### Old posts *(builder's call)*

Two kinds of leftovers in the 2015 and 2017 posts would break the constraints below, so
the restyle fixes them in the post files, leaving the words unchanged:

- Hard-coded text colours in inline spans (for example `#993300` and `#999999` in
  `2017-05-15-trading-tools-in-javascript.md`) fail AA contrast in one theme or the other.
  Replace them with a small set of classes whose colours come from the theme tokens.
- Font Awesome loaded from `maxcdn.bootstrapcdn.com` points at the copy already in
  `/css/font-awesome.css` and `/fonts/`.

### Share image

`img/og-default.png` is redrawn in the Margin colours and type (it was last redrawn in
commit 3b26daf for the current theme).

## Constraints

- Jekyll on GitHub Pages; no build step beyond Jekyll, no frameworks, no third-party
  requests (fonts self-hosted).
- Keep the existing data files and includes (`_data/*.yml`, `_includes/cards.html`), the
  SEO include, `llms.txt`, `/resume.md` and the analytics include working unchanged.
- Accessibility: WCAG AA contrast for text in both themes; visible focus states; the theme
  switch keeps its `aria-pressed` state.
- `docs/` holds design notes and is excluded from the Jekyll build.

## Left to the builder

- Exact type scale, spacing and breakpoints, within the mockup's proportions.
- Whether `cards.html` gains a `feature` option or the home page marks the first app and
  the Reference section as wide some other way.
- How the FIX Parser sentence is stored (for example an optional field in `apps.yml`
  shown only on wide tiles).
- Font subsetting tool and which weights are actually needed.
- Retuned highlight colours, and the exact dark-mode screenshot border.
