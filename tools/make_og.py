"""Gera as imagens de compartilhamento (Open Graph, 1200 x 630) em assets/img/og-*.jpg.

Uso (precisa do Pillow):  python tools/make_og.py
As fontes (DM Sans e Bricolage Grotesque, licença OFL) estão em tools/fonts.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
W, H = 1200, 630
VOLUMES = json.loads((ROOT / "data" / "volumes.json").read_text(encoding="utf-8"))
COLORS = {
    1: ("#f2a47a", "#2a1f4d", "#b8321f"),
    2: ("#8fd0e0", "#16224a", "#c2410c"),
    3: ("#cfe8c4", "#17382a", "#b45309"),
    4: ("#f3e1a0", "#3a2c08", "#9a3412"),
    5: ("#ec9a82", "#3a1608", "#b8321f"),
}


def font(name, size, weight):
    f = ImageFont.truetype(str(ROOT / "tools" / "fonts" / name), size)
    f.set_variation_by_axes([96, weight, 100] if name.startswith("Bricolage") else [14, weight])
    return f


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def cover(n, height, angle=0):
    im = Image.open(IMG / f"capa-{n}-960.webp").convert("RGBA")
    im = im.resize((round(height * im.width / im.height), height), Image.LANCZOS)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *im.size), radius=18, fill=255)
    im.putalpha(mask)
    shadow = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 120), (40, 52), mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    shadow.alpha_composite(im, (40, 40))
    return shadow.rotate(angle, resample=Image.BICUBIC, expand=True)


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + ([line] if line else [])


def save(img, name):
    img.convert("RGB").save(IMG / name, "JPEG", quality=88, optimize=True, progressive=True)
    print("gerado", name)


# Home: fundo escuro com o leque de capas
home = Image.new("RGBA", (W, H), rgb("#16182c"))
d = ImageDraw.Draw(home)
d.text((70, 92), "A BÍBLIA DO PROGRAMADOR PYTHON", font=font("DMSans.ttf", 24, 700), fill=rgb("#cfd0e0"))
d.text((66, 128), "Python", font=font("Bricolage.ttf", 150, 800), fill=(255, 255, 255))
d.text((70, 300), "de", font=font("Bricolage.ttf", 64, 500), fill=(255, 255, 255))
d.text((148, 300), "A a Z", font=font("Bricolage.ttf", 64, 800), fill=rgb("#ffd86b"))
d.rounded_rectangle((70, 420, 440, 474), radius=27, fill=rgb("#ffd86b"))
d.text((96, 435), "5 VOLUMES · POR TIAGO SILVA", font=font("DMSans.ttf", 21, 700), fill=rgb("#16182c"))
for n, (x, y, ang, hh) in zip(range(1, 6), [(610, 150, 12, 330), (690, 105, 6, 350), (780, 80, 0, 380), (880, 105, -6, 350), (960, 150, -12, 330)]):
    c = cover(n, hh, ang)
    home.alpha_composite(c, (x, y))
save(home, "og-home.jpg")

# Volumes: fundo na cor do livro, título à esquerda e capa à direita
for v in VOLUMES:
    n = v["n"]
    bg, ink, accent = COLORS[n]
    im = Image.new("RGBA", (W, H), rgb(bg))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 80, 70 + 230, 80 + 56), radius=28, fill=rgb(ink))
    d.text((92, 93), f"VOLUME {n} DE 5", font=font("DMSans.ttf", 22, 700), fill=(255, 255, 255))
    d.text((66, 160), "Python", font=font("Bricolage.ttf", 118, 800), fill=rgb(ink))
    d.text((70, 290), "de", font=font("Bricolage.ttf", 54, 500), fill=rgb(ink))
    d.text((134, 290), "A a Z", font=font("Bricolage.ttf", 54, 800), fill=rgb(accent))
    f = font("Bricolage.ttf", 46, 800)
    y = 392
    for line in wrap(d, v["topic"], f, 560):
        d.text((70, y), line, font=f, fill=rgb(ink))
        y += 56
    d.text((70, 560), "por Tiago Silva", font=font("DMSans.ttf", 24, 700), fill=rgb(ink))
    im.alpha_composite(cover(n, 520, 5), (700, 34))
    save(im, f"og-livro-{n}.jpg")

# Livros da Casa do Código
books = {b["key"]: b for b in json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))}
for key, b in books.items():
    t = b["theme"]
    im = Image.new("RGBA", (W, H), rgb(t["bg"]))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 80, 70 + 250, 80 + 56), radius=28, fill=rgb(t["ink"]))
    d.text((92, 93), "CASA DO CÓDIGO" if not b["soon"] else "EM BREVE · NOV/2026", font=font("DMSans.ttf", 22, 700), fill=(255, 255, 255))
    f = font("Bricolage.ttf", 76, 800)
    y = 180
    for line in wrap(d, b["title"], f, 600):
        d.text((66, y), line, font=f, fill=rgb(t["ink"]))
        y += 86
    f2 = font("DMSans.ttf", 28, 500)
    for line in wrap(d, b["subtitle"], f2, 580)[:3]:
        d.text((70, y + 20), line, font=f2, fill=rgb(t["ink"]))
        y += 38
    d.text((70, 560), "por Tiago Silva", font=font("DMSans.ttf", 24, 700), fill=rgb(t["ink"]))
    if b["cover"]:
        cv = Image.open(ROOT / b["cover"]).convert("RGBA")
        cv = cv.resize((round(460 * cv.width / cv.height), 460), Image.LANCZOS)
        mask = Image.new("L", cv.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *cv.size), radius=8, fill=255)
        cv.putalpha(mask)
        sh = Image.new("RGBA", (cv.width + 80, cv.height + 80), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 120), (40, 52), mask)
        sh = sh.filter(ImageFilter.GaussianBlur(16))
        sh.alpha_composite(cv, (40, 40))
        im.alpha_composite(sh.rotate(4, resample=Image.BICUBIC, expand=True), (760, 70))
    else:
        d.rounded_rectangle((830, 90, 830 + 330, 90 + 470), radius=10, fill=rgb(t["accent"]))
        d.text((870, 250), "Em", font=font("Bricolage.ttf", 90, 800), fill=rgb("#ffd86b"))
        d.text((870, 340), "breve", font=font("Bricolage.ttf", 90, 800), fill=rgb("#ffd86b"))
    save(im, f"og-{key}.jpg")
