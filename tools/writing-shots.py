"""Makes the 800x500 shots for the Writing tiles on the home page, from each post's own
pictures. Run from the repo root: python3 -I tools/writing-shots.py  (needs Pillow)

"fit" scales the whole picture onto white with a small margin, for diagrams whose ends
carry the point; "crop" fills the tile and keeps the left of the picture.
"""
import io
from pathlib import Path
from PIL import Image, ImageCms

W, H = 800, 500
OUT = Path("img/writing")
SHOTS = [
    # (source picture in the post, output name, how)
    ("assets/financial-exchange/neworder1.png", "financial-exchange", "fit"),
    ("assets/composingcontracts/mappingdiagram.png", "composing-contracts", "crop"),
    ("assets/multicolumn/retina.png", "multicolumn-editors", "crop"),
    ("assets/trading-tools-in-javascript/sequencediagram.png", "trading-tools-in-javascript", "fit"),
]


def fit(im):
    s = min(W * 0.94 / im.width, H * 0.94 / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    tile = Image.new("RGB", (W, H), (255, 255, 255))
    tile.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return tile


def crop(im):
    if im.width / im.height > W / H:
        im = im.crop((0, 0, round(im.height * W / H), im.height))
    else:
        im = im.crop((0, 0, im.width, round(im.width * H / W)))
    return im.resize((W, H), Image.LANCZOS)


def load_srgb(src):
    """Open a picture as sRGB on white. Several sources carry Mac colour profiles
    (Generic RGB, Display); dropping them makes browsers show the raw values as sRGB,
    which looks harsher than the post, so convert through the profile instead."""
    im = Image.open(src)
    icc = im.info.get("icc_profile")
    im = im.convert("RGBA")
    flat = Image.new("RGBA", im.size, (255, 255, 255, 255))
    flat.alpha_composite(im)
    im = flat.convert("RGB")
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                       ImageCms.createProfile("sRGB"))
    return im


OUT.mkdir(parents=True, exist_ok=True)
for src, name, how in SHOTS:
    im = load_srgb(src)
    (fit if how == "fit" else crop)(im).save(OUT / f"{name}.webp", quality=82, method=6)
    print(OUT / f"{name}.webp", (OUT / f"{name}.webp").stat().st_size, "bytes")
