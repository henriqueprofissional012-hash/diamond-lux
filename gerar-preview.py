# Empacota o site em um único HTML autocontido, para o link de preview.
#
# CSS, JS e todas as imagens entram embutidos; a única requisição externa que
# sobra é o Google Fonts. O arquivo sai sem doctype/html/head/body porque o
# host do preview já fornece esse invólucro.
#
#   python gerar-preview.py [saída]
#
# A saída padrão fica FORA da pasta do site, para o arquivo de 3 MB nunca ser
# publicado junto no Cloudflare Pages.

import base64
import mimetypes
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(BASE), "diamond-lux-preview.html")

html = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
css = open(os.path.join(BASE, "styles.css"), encoding="utf-8").read()
js = open(os.path.join(BASE, "script.js"), encoding="utf-8").read()


def data_uri(rel):
    caminho = os.path.join(BASE, *rel.split("/"))
    mime = mimetypes.guess_type(caminho)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(open(caminho, 'rb').read()).decode()}"


usadas = sorted(set(re.findall(r'src="(img/[^"]+)"', html)))
for rel in usadas:
    html = html.replace(f'src="{rel}"', f'src="{data_uri(rel)}"')

fontes = re.search(r'<link href="https://fonts\.googleapis[^>]+>', html).group(0)
corpo = html.split("<body>", 1)[1].rsplit("</body>", 1)[0]
corpo = corpo.replace('<script src="script.js" defer></script>', "")

partes = [
    "<title>Clínica Diamond Lux</title>",
    "<script>document.documentElement.classList.add('js')</script>",
    '<link rel="preconnect" href="https://fonts.googleapis.com"/>',
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>',
    fontes,
    "<style>\n" + css + "\n</style>",
    corpo.strip(),
    "<script>\n" + js + "\n</script>",
]

with open(SAIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(partes))

print(f"{len(usadas)} imagens embutidas -> {SAIDA}")
print(f"tamanho: {os.path.getsize(SAIDA) / 1024 / 1024:.1f} MB")
