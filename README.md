# Clínica Diamond Lux — Home

Implementação da home aprovada pela cliente. HTML + CSS + JS estáticos, sem build —
pronto para publicar no Cloudflare Pages (basta apontar para esta pasta).

```bash
node serve.cjs
```
→ http://localhost:8951

## Arquivos

| Arquivo      | O que é                                                    |
|--------------|------------------------------------------------------------|
| `index.html` | Marcação completa + sprite de ícones SVG (line-art)         |
| `styles.css` | Tokens de design, seções 01–10 e breakpoints                |
| `script.js`  | Menu mobile, link ativo no scroll, reveal ao entrar na tela |
| `img/`       | Fotos tratadas da clínica                                   |
| `serve.js`   | Servidor local de desenvolvimento                           |

## Tokens

| Token      | Valor     | Uso                          |
|------------|-----------|------------------------------|
| `--dark`   | `#0C1016` | header, hero, footer         |
| `--dark-2` | `#10141A` | seção Tecnologia             |
| `--panel`  | `#12161E` | barra de benefícios, CTA     |
| `--gold`   | `#C99A46` | labels, botões, detalhes     |
| `--cream`  | `#F8F7F4` | fundo das seções claras      |
| `--W`      | `1280px`  | largura do container         |
| `--hd`     | `84px`    | altura do header             |

Tipografia: **Playfair Display** (títulos) + **Inter** (texto, menu, botões).

## Logo

A arte oficial (`LOGO.jpg`) é quadrada e empilha CLÍNICA / Diamond / Lux. O header
aprovado usa o lockup horizontal, então `extrair-logo.py` recorta a arte com fundo
transparente e remonta o letreiro — a tipografia continua sendo a da logo oficial.

| Arquivo               | Uso                                   |
|-----------------------|---------------------------------------|
| `logo-mark.png`       | Losango — header, rodapé, hero        |
| `logo-mark-gold.png`  | Losango dourado — CTA final           |
| `logo-wordmark.png`   | CLÍNICA + Diamond Lux (uma linha)     |
| `logo-lockup.png`     | Lockup vertical completo (uso externo)|

## Seções

`index.html` segue a ordem: header, hero, barra de benefícios, sobre, serviços,
estrutura, tecnologia, depoimentos, CTA, formulário e rodapé. O assistente é fixo
e vive fora do `<main>`.

**Estrutura** é um guia numerado do percurso real de quem chega: 01 Entrada,
02 Recepção, 03 Caminho do Café, 04 Sala de Tratamentos. A numeração existe porque
a ordem carrega informação — não é enfeite.

**Serviços** tem 12 cards em duas fileiras de seis: os seis pilares de atendimento
e os seis procedimentos que a clínica realiza (harmonização glútea, subcisão de
celulite, PRP e PRF, toxina botulínica, terapia capilar e limpeza de pele).

**Depoimentos** são as três avaliações reais do perfil do Google, todas 5 estrelas.
Para atualizar, copie o texto do perfil e troque no HTML.

## Formulário

Sem back-end: a validação é no navegador e o envio monta uma mensagem e abre o
WhatsApp da clínica. Os dados **não trafegam nem ficam salvos neste site**.

O CPF tem máscara e conferência dos dígitos verificadores, e o telefone tem máscara
de 10 e 11 dígitos. O consentimento é obrigatório.

> **LGPD** — CPF e data de nascimento são dados pessoais. Hoje eles vão direto do
> navegador da pessoa para o WhatsApp da clínica, sem passar por servidor nosso,
> que é o caminho mais simples e com menos exposição. Se um dia a captação for para
> um CRM ou e-mail, será preciso um endpoint com HTTPS, política de privacidade
> publicada e definição de prazo de retenção.

## Assistente Lux

FAQ local em `script.js`, no mesmo padrão do bot da Casateliê: nenhuma chamada
externa, casamento por expressão regular e chips de atalho. O avatar é o losango
dourado da marca.

As respostas são informativas e nunca clínicas — qualquer pergunta que dependa de
avaliação profissional cai no fallback, que encaminha para o WhatsApp. Ao editar
`RESPOSTAS`, mantenha esse limite.

## Texto

A prosa passou pela skill Humanizer: sem tríades forçadas, sem linguagem de venda
genérica ("última geração", "alta performance") e sem travessão como conector. Os
títulos aprovados pela cliente, os rótulos curtos da barra e os depoimentos do
Google ficaram como estão, porque a própria skill manda preservar títulos e
citações.

Vale também para a publicidade médica: nada de prometer resultado. O texto
descreve o procedimento e a avaliação, não o efeito garantido.

## Hero contínuo

A foto da recepção ocupa os 66% da direita, mas não existe emenda visível: o véu
sobre ela é **100% opaco no `--dark` exato do fundo** nos primeiros 9% e só então
começa a abrir. Como as duas cores são idênticas, a borda simplesmente não existe
(medido: 0 níveis de diferença entre colunas vizinhas). O mesmo vale embaixo, onde
a foto fecha em `--dark` antes de encontrar a barra de benefícios.

Se mexer nesse degradê, mantenha o primeiro trecho em `var(--dark)` sólido —
qualquer valor abaixo de 100% de opacidade traz a faixa prateada de volta.

## Animação de entrada

O estado escondido (`opacity:0`) vive sob `.js .rv`, e a classe `js` é adicionada
por um script inline no `<head>`. Sem JS, nada fica invisível. Há ainda uma rede
de segurança em `script.js`: aba aberta em segundo plano congela o
IntersectionObserver, então o que está na primeira dobra é revelado por tempo.

## Fotos

As fotos são as **originais do Perfil da Empresa no Google** (4284×5712 / 3024×4032),
baixadas em resolução cheia e guardadas em `Área de Trabalho/Diamond lux/originais`.

`tratar-fotos.py` faz o trabalho: enquadra cada uma no formato da seção (recorte
feito no arquivo grande, antes de reduzir, para não desperdiçar resolução),
corrige a luz com mão leve (níveis por canal, sombra aberta, realce protegido,
contraste local) e reduz com nitidez. Saída ~2,5x o tamanho de exibição.

| Saída                  | Origem       | Onde aparece                    |
|------------------------|--------------|---------------------------------|
| `recepcao-wide.jpg`    | `foto-06`    | Hero                            |
| `recepcao.jpg`         | `foto-06`    | Estrutura · Recepção            |
| `sobre-clinica.jpg`    | `foto-15`    | Sobre a clínica                 |
| `sala-tratamentos.jpg` | `foto-03`    | Estrutura · Sala / Tecnologia 1 |
| `cantinho-cafe.jpg`    | `foto-05`    | Estrutura · Caminho do Café     |
| `entrada.jpg`          | `foto-01`    | Estrutura · Entrada             |
| `equipamentos.jpg`     | `foto-08`    | Tecnologia 2                    |
| `produtos.jpg`         | `foto-25`    | Tecnologia 3                    |

Para trocar o enquadramento de alguma, ajuste o foco vertical/horizontal na tabela
`JOBS` do script e rode de novo.

### Como baixar as originais do Google de novo

O Google guarda a foto original e serve miniaturas. Para pegar a versão cheia:

1. Google Maps → perfil da clínica → **Fotos** → abra a foto.
2. Botão direito → **Copiar endereço da imagem**.
3. A URL termina com um sufixo de tamanho, tipo `=w141-h141-k-no`.
4. Troque o sufixo por **`=s0`** — é a original.

Alternativa: `takeout.google.com` → exportar *Perfil da Empresa*.

## A ajustar antes de publicar

- `https://instagram.com/` → perfil real
- `https://maps.google.com/` → link do Google Maps da clínica
