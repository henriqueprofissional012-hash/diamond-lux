# Prepara o retrato da Thalita para o site: tira as bordas brancas do
# WhatsApp, corta no formato pedido e ajusta luz de leve.
#
#   python preparar-retrato.py <foto> [fx] [fy] [zoom] [largura] [altura] [destino]
#
#   fx    0 = puxa para a esquerda da foto, 1 = para a direita
#   fy    0 = puxa para o topo, 1 = para a base
#   zoom  1 = maior corte possível; 0.8 = fecha mais no assunto

import sys, os
from PIL import Image, ImageOps, ImageEnhance, ImageChops


def arg(i, conv, padrao):
    return conv(sys.argv[i]) if len(sys.argv) > i else padrao


ORIGEM = arg(1, str, "thalita-original.jpg")
FX = arg(2, float, 0.5)
FY = arg(3, float, 0.42)
ZOOM = arg(4, float, 1.0)
LARGURA = arg(5, int, 1200)
ALTURA = arg(6, int, 1200)
DESTINO = arg(7, str, os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "thalita.jpg"))


def sem_bordas(im):
    """Corta as faixas quase brancas que o WhatsApp deixa em volta."""
    fundo = Image.new("RGB", im.size, (255, 255, 255))
    dif = ImageChops.difference(im.convert("RGB"), fundo).convert("L")
    caixa = dif.point(lambda p: 255 if p > 18 else 0).getbbox()
    return im.crop(caixa) if caixa else im


def enquadra(im):
    """Maior retângulo do formato pedido, reduzido pelo zoom e posicionado por fx/fy."""
    alvo = LARGURA / ALTURA
    l, a = im.size
    nova_l, nova_a = (int(a * alvo), a) if l / a > alvo else (l, int(l / alvo))
    nova_l, nova_a = int(nova_l * ZOOM), int(nova_a * ZOOM)
    x = int((l - nova_l) * FX)
    y = int((a - nova_a) * FY)
    return im.crop((x, y, x + nova_l, y + nova_a)).resize((LARGURA, ALTURA), Image.LANCZOS)


im = ImageOps.exif_transpose(Image.open(ORIGEM)).convert("RGB")
im = enquadra(sem_bordas(im))
im = ImageEnhance.Brightness(im).enhance(1.02)
im = ImageEnhance.Contrast(im).enhance(1.04)
im = ImageEnhance.Sharpness(im).enhance(1.15)

os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
im.save(DESTINO, "JPEG", quality=86, optimize=True, progressive=True)
print(f"{DESTINO}  {im.size[0]}x{im.size[1]}  {os.path.getsize(DESTINO)/1024:.0f} KB")
