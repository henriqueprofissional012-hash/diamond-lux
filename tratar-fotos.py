# Prepara as fotos da Clínica Diamond Lux para o site.
#
# Origem: fotos originais do Perfil da Empresa no Google (24 MP / 12 MP),
# em `Área de Trabalho/Diamond lux/originais`. Como a origem é grande, o
# trabalho aqui é só enquadrar, corrigir a luz com mão leve e reduzir com
# nitidez — nada de upscale.

import os
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

SRC = r"C:\Users\henri\OneDrive\Área de Trabalho\Diamond lux\originais"
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

# origem -> (saída, largura, altura, foco vertical 0..1, foco horizontal 0..1)
# Os tamanhos são ~2,5x o de exibição, para ficar nítido em tela retina.
JOBS = [
    ("foto-06-tv.jpg", "recepcao-wide.jpg", 2400, 1730, 0.14, 0.50),  # hero (TV com a marca)
    ("foto-06-tv.jpg", "recepcao.jpg",       960, 1008, 0.46, 0.50),  # estrutura · Recepção
    ("foto-15.jpg", "sobre-clinica.jpg",    2000, 1042, 0.44, 0.50),  # sobre
    ("foto-03.jpg", "sala-tratamentos.jpg",  960, 1008, 0.50, 0.50),  # estrutura 2 / tec 1
    ("foto-05.jpg", "cantinho-cafe.jpg",     960, 1008, 0.50, 0.50),  # estrutura 3
    ("foto-01.jpg", "entrada.jpg",           960, 1008, 0.34, 0.50),  # estrutura 4
    ("foto-08.jpg", "equipamentos.jpg",      900, 1280, 0.46, 0.50),  # tec 2
    ("foto-25.jpg", "produtos.jpg",          900, 1280, 0.50, 0.50),  # tec 3
]


def cover(im, tw, th, fy=0.5, fx=0.5):
    """Recorte estilo object-fit: cover, feito antes de reduzir para não
    desperdiçar resolução."""
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    cw, ch = round(tw / scale), round(th / scale)      # janela no tamanho original
    left = int(round((sw - cw) * fx))
    top = int(round((sh - ch) * fy))
    im = im.crop((left, top, left + cw, top + ch))
    return im.resize((tw, th), Image.LANCZOS)


def grade(im, lo=0.5, hi=99.6, mix=0.55, lift=0.035):
    """Correção de luz com mão leve: níveis por canal para tirar a dominante e
    recuperar faixa, sombra levemente aberta, realce protegido."""
    a = np.asarray(im, np.float32) / 255.0
    out = np.empty_like(a)
    for c in range(3):
        p_lo, p_hi = np.percentile(a[..., c], (lo, hi))
        out[..., c] = a[..., c] if p_hi - p_lo < 1e-4 else np.clip((a[..., c] - p_lo) / (p_hi - p_lo), 0, 1)
    a = out * mix + a * (1 - mix)

    a = a + lift * (1.0 - a) * np.exp(-((a / 0.30) ** 2))       # abre sombra
    a = a - 0.035 * a * np.exp(-(((1 - a) / 0.18) ** 2))        # segura o estouro
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

    # contraste local suave — dá profundidade sem halo
    return im.filter(ImageFilter.UnsharpMask(radius=30, percent=18, threshold=3))


for src, out, tw, th, fy, fx in JOBS:
    p = os.path.join(SRC, src)
    if not os.path.exists(p):
        print("FALTANDO:", src)
        continue

    im = Image.open(p).convert("RGB")
    w0, h0 = im.size

    im = cover(im, tw, th, fy, fx)
    im = grade(im)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=58, threshold=3))  # nitidez pós-redução
    im = ImageEnhance.Color(im).enhance(1.04)

    dst = os.path.join(DST, out)
    im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"{src}  {w0}x{h0}  ->  {out:22} {tw}x{th}  {os.path.getsize(dst)//1024}KB")
