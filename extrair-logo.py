# Extrai a logo oficial (LOGO.jpg) com fundo transparente.
#
# A arte é clara sobre fundo escuro, então o canal alpha vem da luminância —
# recorte limpo, sem halo, que assenta em qualquer fundo escuro do site.
#
# A arte original é quadrada e empilha CLÍNICA / Diamond / Lux. O cabeçalho
# aprovado usa o lockup horizontal (losango à esquerda, CLÍNICA sobre
# "Diamond Lux" em uma linha), então o letreiro é recomposto a partir das
# palavras recortadas da própria logo — a tipografia continua sendo a oficial.

import os
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = r"C:\Users\henri\OneDrive\Área de Trabalho\Diamond lux\LOGO.jpg"
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

SCALE = 4          # 640 -> 2560, para ficar nítido em telas retina
LO, HI = 74, 186   # rampa de luminância -> alpha
GOLD = (201, 154, 70)


def load():
    im = Image.open(SRC).convert("RGB").resize((640 * SCALE, 640 * SCALE), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    lum = a @ [0.299, 0.587, 0.114]
    alpha = np.clip((lum - LO) / (HI - LO), 0, 1) ** 0.85 * 255
    rgb = np.clip(a * 1.10 + 26, 0, 255)     # clareia o traço para o grafite do site
    return rgb, alpha


def rgba(rgb, alpha, box):
    x0, y0, x1, y1 = box
    return Image.fromarray(
        np.dstack([rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]]).astype(np.uint8), "RGBA")


def despeckle(im):
    """Apaga respingos do JPEG por área absoluta.

    O limiar é fixo, não relativo à maior mancha: no lockup a maior é o losango,
    e uma fração dele apagaria o acento do Í junto com o respingo. Nesta escala
    um respingo tem ~80 px e um acento ~480 px, então o corte fica no meio.
    """
    mask = np.asarray(im.getchannel("A")) > 40
    lab, n = ndimage.label(mask, np.ones((3, 3), bool))
    if n <= 1:
        return im
    areas = ndimage.sum_labels(mask, lab, range(1, n + 1))
    a = np.asarray(im).copy()
    a[..., 3] *= np.isin(lab, 1 + np.flatnonzero(areas >= (SCALE * 3.5) ** 2))
    return Image.fromarray(a, "RGBA")


def main_run(im, gap=20 * SCALE):
    """Mantém só o bloco principal de colunas. A logo original tem respingos
    soltos longe da palavra; entre letras a lacuna é pequena, para o respingo
    é enorme — então o maior bloco de tinta é o texto."""
    ink = (np.asarray(im.getchannel("A")) > 40).sum(0)
    on = np.flatnonzero(ink)
    if not len(on):
        return im
    runs, start = [], on[0]
    for a, b in zip(on, on[1:]):
        if b - a > gap:
            runs.append((start, a + 1))
            start = b
    runs.append((start, on[-1] + 1))
    x0, x1 = max(runs, key=lambda r: ink[r[0]:r[1]].sum())
    return im.crop((x0, 0, x1, im.height))


def tight(im, pad=0):
    b = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    return im.crop((max(0, b[0] - pad), max(0, b[1] - pad),
                    min(im.width, b[2] + pad), min(im.height, b[3] + pad)))


def scale_h(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def tint(im, color):
    """Recolore mantendo o alpha — usado na versão dourada do losango."""
    a = np.asarray(im).astype(np.float32)
    lum = (a[..., :3] @ [0.299, 0.587, 0.114]) / 255.0
    out = np.dstack([np.clip(lum[..., None] * np.array(color, np.float32) * 1.18, 0, 255),
                     a[..., 3:]])
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def save(im, name):
    p = os.path.join(DST, name)
    im.save(p)
    print(f"{name:24} {im.width}x{im.height}  {os.path.getsize(p) // 1024}KB")


def bands(alpha, y0, y1, gap=3 * SCALE):
    """Separa as linhas de texto por faixas de linhas vazias."""
    rows = (alpha[y0:y1] > 40).sum(1) > 0
    out, start, empty = [], None, 0
    for i, on in enumerate(rows):
        if on:
            if start is None:
                start = i
            empty = 0
        elif start is not None:
            empty += 1
            if empty >= gap:
                out.append((y0 + start, y0 + i - empty + 1))
                start = None
    if start is not None:
        out.append((y0 + start, y1))
    return out


def split_thin_top(alpha, band):
    """CLÍNICA quase encosta em 'Diamond' — separa as duas no vale de densidade
    logo abaixo do topo da faixa."""
    y0, y1 = band
    d = (alpha[y0:y1] > 40).sum(1)
    h = y1 - y0
    lo, hi = int(h * 0.22), int(h * 0.40)
    cut_at = y0 + lo + int(np.argmin(d[lo:hi]))
    return (y0, cut_at), (cut_at, y1)


rgb, alpha = load()
S = SCALE

# ── losango ────────────────────────────────────────────────────────────────
mark = tight(main_run(despeckle(rgba(rgb, alpha, (0, 90 * S, 640 * S, 312 * S)))))
save(scale_h(mark, 180), "logo-mark.png")
save(tint(scale_h(mark, 180), GOLD), "logo-mark-gold.png")

# ── letreiro horizontal: CLÍNICA em cima, "Diamond Lux" em uma linha ───────
raw = bands(alpha, 315 * S, 508 * S)
if len(raw) != 2:
    raise SystemExit(f"esperava 2 faixas (CLÍNICA+Diamond / Lux), achei {len(raw)}")
b_clinica, b_diamond = split_thin_top(alpha, raw[0])
boxes = [b_clinica, b_diamond, raw[1]]

clinica, diamond, lux = [tight(main_run(despeckle(rgba(rgb, alpha, (0, a, 640 * S, b))))) for a, b in boxes]
assert clinica.height < diamond.height * 0.6, "recorte de CLÍNICA saiu errado"

H = 120                                    # altura de "Diamond" no letreiro final
diamond, lux = scale_h(diamond, H), scale_h(lux, H)
clinica = scale_h(clinica, round(H * 0.30))
space = round(H * 0.34)

row_w = diamond.width + space + lux.width
gap = round(H * 0.34)                      # respiro entre CLÍNICA e a palavra
W, Ht = max(row_w, clinica.width), clinica.height + gap + H

word = Image.new("RGBA", (W, Ht), (0, 0, 0, 0))
word.paste(clinica, (0, 0), clinica)       # CLÍNICA alinhada à esquerda
word.paste(diamond, (0, clinica.height + gap), diamond)
word.paste(lux, (diamond.width + space, clinica.height + gap), lux)
save(word, "logo-wordmark.png")

# ── lockup completo (para OG image / usos externos) ────────────────────────
save(scale_h(tight(despeckle(rgba(rgb, alpha, (0, 90 * S, 640 * S, 508 * S)))), 420), "logo-lockup.png")
