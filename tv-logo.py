# Troca o conteúdo da TV da recepção pela marca da clínica.
#
# Na foto original a TV está tocando um clipe. Este script desenha uma tela de
# sinalização digital com a logo oficial e a encaixa na TV com transformação de
# perspectiva (a TV está de lado na foto, então não dá para simplesmente colar
# um retângulo). O resultado vira `foto-06-tv.jpg`, que é o que `tratar-fotos.py`
# consome — a foto original nunca é alterada.

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
ORIG = r"C:\Users\henri\OneDrive\Área de Trabalho\Diamond lux\originais"
FONTE = os.path.join(ORIG, "foto-06.jpg")
SAIDA = os.path.join(ORIG, "foto-06-tv.jpg")

# cantos da tela na foto original, em sentido horário a partir do alto-esquerdo
TELA = [(2894, 1846), (3622, 1810), (3624, 2286), (2896, 2296)]

TW, TH = 1920, 1080          # resolução da arte da tela


def arte_da_tela():
    """Sinalização: fundo grafite com brilho suave e a logo oficial centralizada."""
    yy = np.linspace(0, 1, TH)[:, None]
    fundo = np.zeros((TH, TW, 3), np.float32)
    for c, (a, b) in enumerate(zip((12, 16, 22), (26, 32, 42))):   # --dark -> mais claro
        fundo[..., c] = a + (b - a) * yy

    xx = np.linspace(0, 1, TW)[None, :]
    brilho = np.exp(-(((xx - 0.5) / 0.42) ** 2 + ((yy - 0.46) / 0.44) ** 2))
    fundo += brilho[..., None] * np.array([16, 18, 24], np.float32)

    tela = Image.fromarray(np.clip(fundo, 0, 255).astype(np.uint8))

    logo = Image.open(os.path.join(BASE, "img", "logo-lockup.png")).convert("RGBA")
    h = round(TH * 0.60)
    logo = logo.resize((round(logo.width * h / logo.height), h), Image.LANCZOS)
    tela.paste(logo, ((TW - logo.width) // 2, (TH - logo.height) // 2), logo)

    # leve reflexo diagonal — sem isso a tela parece um adesivo, não um monitor
    reflexo = Image.new("L", (TW, TH), 0)
    ImageDraw.Draw(reflexo).polygon(
        [(0, TH), (TW * 0.42, 0), (TW * 0.60, 0), (0, TH * 0.62)], fill=26)
    reflexo = reflexo.filter(ImageFilter.GaussianBlur(70))
    return Image.composite(Image.new("RGB", (TW, TH), (255, 255, 255)), tela, reflexo)


def coeffs(origem, destino):
    """Coeficientes de perspectiva no formato do PIL (mapeia destino -> origem)."""
    m = []
    for (ox, oy), (dx, dy) in zip(origem, destino):
        m.append([dx, dy, 1, 0, 0, 0, -ox * dx, -ox * dy])
        m.append([0, 0, 0, dx, dy, 1, -oy * dx, -oy * dy])
    return np.linalg.solve(np.array(m, float), np.array(origem, float).reshape(8))


foto = Image.open(FONTE).convert("RGB")
W, H = foto.size

tela = arte_da_tela()
cf = coeffs([(0, 0), (TW, 0), (TW, TH), (0, TH)], TELA)

encaixada = tela.transform((W, H), Image.PERSPECTIVE, cf, Image.BICUBIC)

mascara = Image.new("L", (W, H), 0)
ImageDraw.Draw(mascara).polygon(TELA, fill=255)
mascara = mascara.filter(ImageFilter.GaussianBlur(2))   # borda sem serrilhado

foto.paste(encaixada, (0, 0), mascara)
foto.save(SAIDA, "JPEG", quality=94, subsampling=0)
print(f"TV trocada -> {os.path.basename(SAIDA)}  ({os.path.getsize(SAIDA)//1024//1024} MB)")
