"""Checks on the built site (_site) for the Margin design.

Usage: python3 -I tests/check_site.py _site
Prints PASS or FAIL per check and exits 1 if any check failed.
"""
import re
import sys
from pathlib import Path

FIX_LINE = ("A standard tool for much of Wall Street. "
            "From the largest banks to the smallest trading firms.")
LIGHT = {"--bg": "#f7f5ef", "--text": "#1c1b19", "--muted": "#6b665d",
         "--accent": "#a3201a", "--line": "#dcd7cc"}
DARK = {"--bg": "#1c1a17", "--text": "#e8e4da", "--muted": "#a59f93",
        "--accent": "#e26a5c", "--line": "#3a3631"}
FONTS = ["eb-garamond-400.woff2", "eb-garamond-400-italic.woff2", "eb-garamond-500.woff2"]
ALLOWED_EXTERNAL = ("https://www.googletagmanager.com/",)
FIRST_PARTY = ("https://shahbazac.com/",)


# ---------- helpers ----------

def css(site):
    return (site / "css" / "site.css").read_text(encoding="utf-8")


def block_after(text, start):
    """Text between the brace that opens at or after `start` and its matching close."""
    i = text.index("{", start)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j]
    raise ValueError("unbalanced braces")


def find_block(text, pattern):
    m = re.search(pattern, text, re.M)
    return block_after(text, m.start()) if m else None


def props(block):
    return {k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block or "")}


def theme_blocks(text):
    light = find_block(text, r"^:root\s*\{")
    media = find_block(text, r"^@media \(prefers-color-scheme: dark\)\s*\{")
    dark_media = find_block(media, r':root:not\(\[data-theme="light"\]\)\s*\{') if media else None
    dark_attr = find_block(text, r'^:root\[data-theme="dark"\]\s*\{')
    return props(light), props(dark_media), props(dark_attr)


def luminance(hexcolor):
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    chans = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    chans = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in chans]
    return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def is_hex(v):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}", v or ""))


def html_pages(site):
    return [p for p in site.rglob("*.html") if "skills" not in p.relative_to(site).parts]


def post_pages(site):
    return sorted(site.glob("20*/**/*.html"))


# ---------- checks ----------

def check_fonts(site):
    text, errs = css(site), []
    faces = re.findall(r"@font-face\s*\{([^}]*)\}", text)
    for f in FONTS:
        if not any(f"/fonts/eb-garamond/{f}" in face for face in faces):
            errs.append(f"no @font-face for {f}")
        if not (site / "fonts" / "eb-garamond" / f).exists():
            errs.append(f"missing file fonts/eb-garamond/{f}")
    if not faces or any("font-display: swap" not in face for face in faces):
        errs.append("every @font-face needs font-display: swap")
    # The font ships 400 and 500 only: any other weight is faked by the browser.
    bad = sorted(set(w for w in re.findall(r"font-weight:\s*(\w+)", text) if w not in ("400", "500")))
    if bad:
        errs.append(f"font-weight other than 400/500: {bad}")
    if not re.search(r"(?m)^h4, h5, h6\s*\{[^}]*font-weight:\s*500", text):
        errs.append("h4-h6 need font-weight 500 (browser default 700 is synthesised)")
    serif = props(find_block(text, r"^:root\s*\{")).get("--serif", "")
    if not serif.startswith('"EB Garamond"') or "Georgia" not in serif:
        errs.append(f"--serif should start with \"EB Garamond\" and fall back to Georgia, got {serif!r}")
    return errs


def check_no_third_party(site):
    errs = []
    # Only tags that make the browser fetch something; canonical and alternate links don't.
    tag = re.compile(r"<(link|script|img|iframe)\b[^>]*>", re.I)
    url = re.compile(r'\b(?:href|src)="((?:https?:)?//[^"]+)"', re.I)
    for p in html_pages(site):
        for m in tag.finditer(p.read_text(encoding="utf-8", errors="replace")):
            t = m.group(0)
            if m.group(1).lower() == "link" and not re.search(r'rel="(?:stylesheet|preload|icon|apple-touch-icon|modulepreload)"', t):
                continue
            u = url.search(t)
            if u and not u.group(1).startswith(ALLOWED_EXTERNAL + FIRST_PARTY):
                errs.append(f"{p.relative_to(site)} loads {u.group(1)}")
    if re.search(r"url\(\s*['\"]?(?:https?:)?//", css(site)):
        errs.append("site.css loads a remote url()")
    return errs


def check_tokens(site):
    light, dark_media, dark_attr = theme_blocks(css(site))
    errs = []
    if not dark_media or not dark_attr:
        return ["missing a dark token block"]
    if dark_media != dark_attr:
        diff = sorted(set(dark_media.items()) ^ set(dark_attr.items()))
        errs.append(f"the two dark blocks differ: {diff[:6]}")
    for name, want, got in [("light", LIGHT, light), ("dark", DARK, dark_attr)]:
        for k, v in want.items():
            if got.get(k, "").lower() != v:
                errs.append(f"{name} {k} should be {v}, got {got.get(k)}")
    for name, toks in [("light", light), ("dark", {**light, **dark_attr})]:
        for k in ("--text", "--muted", "--accent"):
            if is_hex(toks.get(k)) and contrast(toks[k], toks["--bg"]) < 4.5:
                errs.append(f"{name} {k} is {contrast(toks[k], toks['--bg']):.2f}:1 on --bg")
        code_bg = toks.get("--code-bg")
        if not is_hex(code_bg):
            errs.append(f"{name} --code-bg missing")
            continue
        for k in [k for k in toks if k.startswith("--hl-")] + ["--muted"]:
            if is_hex(toks[k]) and contrast(toks[k], code_bg) < 4.5:
                errs.append(f"{name} {k} is {contrast(toks[k], code_bg):.2f}:1 on --code-bg")
    edge = dark_attr.get("--shot-edge")
    if not is_hex(edge) or contrast(edge, dark_attr["--bg"]) < 3:
        errs.append(f"dark --shot-edge {edge} needs 3:1 on --bg")
    return errs


def check_print(site):
    text = css(site)
    block = find_block(text, r"^@media print\s*\{")
    if block is None:
        return ["no @media print block"]
    errs = []
    got = props(block)
    for k, v in LIGHT.items():
        if got.get(k, "").lower() != v:
            errs.append(f"print {k} should be {v}, got {got.get(k)}")
    if not re.search(r"\.site-footer[^{]*\{[^}]*display:\s*none", block):
        errs.append("print should hide .site-footer")
    return errs


def check_home(site):
    page = (site / "index.html").read_text(encoding="utf-8")
    feats = list(re.finditer(r'class="[^"]*\bfeature\b[^"]*"', page))
    if len(feats) != 1:
        return [f"expected exactly one feature element, found {len(feats)}"]
    errs = []
    tile = page[feats[0].start():page.find("</li>", feats[0].start())]
    if "FIX Parser" not in tile:
        errs.append("the feature tile isn't FIX Parser")
    if FIX_LINE not in tile:
        errs.append("the feature tile lacks the FIX Parser line")
    if page.count(FIX_LINE) != 1:
        errs.append(f"the FIX Parser line appears {page.count(FIX_LINE)} times")
    return errs


def check_theme_switch(site):
    errs = []
    pages = [site / n for n in ("index.html", "resume.html", "privacy.html", "404.html")] + post_pages(site)
    for p in pages:
        if not p.exists():
            errs.append(f"missing page {p.relative_to(site)}")
            continue
        t = p.read_text(encoding="utf-8")
        choices = re.findall(r'data-theme-choice="(\w+)"', t)
        if sorted(choices) != ["auto", "dark", "light"]:
            errs.append(f"{p.relative_to(site)} switch buttons: {choices}")
        if 'localStorage.getItem("theme")' not in t:
            errs.append(f"{p.relative_to(site)} lacks the pre-paint theme script")
    return errs


def check_old_posts(site):
    errs = []
    for p in post_pages(site):
        if 'style="color' in p.read_text(encoding="utf-8"):
            errs.append(f"{p.relative_to(site)} has inline colours")
    for p in html_pages(site):
        if "maxcdn.bootstrapcdn.com" in p.read_text(encoding="utf-8", errors="replace"):
            errs.append(f"{p.relative_to(site)} loads from maxcdn")
    js = list(site.glob("2017/**/trading-tools-in-javascript.html"))
    if not js or 'class="fix-tag"' not in js[0].read_text(encoding="utf-8"):
        errs.append("the 2017 JavaScript post has no fix-tag spans")
    return errs


def check_retired_styles(site):
    text = css(site)
    retired = ["--ink", "translateY(", "border-radius: 99px", "text-transform: uppercase", "border-top: 8px"]
    return [f"site.css still has {r!r}" for r in retired if r in text]


CHECKS = [check_fonts, check_no_third_party, check_tokens, check_print,
          check_home, check_theme_switch, check_old_posts, check_retired_styles]


def main(argv):
    site = Path(argv[1] if len(argv) > 1 else "_site")
    failed = 0
    for check in CHECKS:
        name = check.__name__.removeprefix("check_")
        try:
            errs = check(site)
        except Exception as e:  # a crash is a failure, not a pass
            errs = [f"{type(e).__name__}: {e}"]
        if errs:
            failed += 1
            print(f"FAIL {name}: " + "; ".join(errs[:5]) + (f" (+{len(errs) - 5} more)" if len(errs) > 5 else ""))
        else:
            print(f"PASS {name}")
    print(f"{len(CHECKS) - failed}/{len(CHECKS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
