"""Gera as páginas internas do site a partir de data/volumes.json e data/books.json.

Uso (dentro da pasta site):  python build.py
Cria: livro-1.html ... livro-5.html, flask.html, django.html, drf.html e outras.html.
A Home (index.html) é escrita à mão e não é tocada.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
E = html.escape
# Endereço público do site. Troque quando o domínio definitivo estiver no ar e rode `python build.py` de novo.
SITE_URL = "https://pythondeaaz.com.br"
CONTACT_EMAIL = "tiagoluizrs@gmail.com"
DRF_MAILTO = f"mailto:{CONTACT_EMAIL}?subject=Quero%20saber%20quando%20sair%3A%20Django%20Rest%20Framework%20de%20A%20a%20Z"
VOLUMES = json.loads((ROOT / "data" / "volumes.json").read_text(encoding="utf-8"))
BOOKS = {b["key"]: b for b in json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))}

BIO_SHORT = (
    "Graduado em Análise e Desenvolvimento de Sistemas, pós-graduado em Engenharia de Software e em Desenvolvimento Back-end, "
    "com MBA em Gestão de Projetos pela USP. Professor universitário, atualmente trabalha como Analista de Sistemas. "
    "Especialista em Python, Java e JavaScript."
)
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17L17 7"/><path d="M8 7h9v9"/></svg>'
CHEV = '<svg class="toc__chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'


def trunc(text, n=158):
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


def abs_url(path):
    return SITE_URL.rstrip("/") + "/" + path.lstrip("/")


def page_url(path):
    """URL canônica: a Home é a raiz do domínio, não /index.html."""
    return abs_url("" if path == "index.html" else path)


def ld_script(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


def seo_block(title, desc, path, og_image, ld_items, og_type="website"):
    """Todo o SEO do <head>: canonical, Open Graph, Twitter Card e dados estruturados (JSON-LD)."""
    url = page_url(path)
    image = abs_url(og_image)
    lines = [
        f'<link rel="canonical" href="{url}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="author" content="Tiago Silva">',
        f'<meta property="og:type" content="{og_type}">',
        '<meta property="og:locale" content="pt_BR">',
        '<meta property="og:site_name" content="Python de A a Z">',
        f'<meta property="og:title" content="{E(title)}">',
        f'<meta property="og:description" content="{E(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{E(title)}">',
        f'<meta name="twitter:description" content="{E(desc)}">',
        f'<meta name="twitter:image" content="{image}">',
    ]
    lines += [ld_script(item) for item in ld_items]
    return "\n".join(lines)


def breadcrumb_ld(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": page_url(path)} for i, (name, path) in enumerate(items, 1)
        ],
    }


AUTHOR_LD = {"@type": "Person", "name": "Tiago Silva", "url": "https://www.linkedin.com/in/tiagoluizrs/"}
SERIES_LD = {"@type": "BookSeries", "name": "Python de A a Z"}


GA_TAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-75W0L401ED"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-75W0L401ED');
</script>
"""


# Frases que as pessoas buscam (título e descrição das páginas dos volumes).
SEO_VOL = {
    1: ("Livro de Python para iniciantes (Vol. 1)",
        "Livro de Python do zero, para quem nunca programou: ambiente, tipos, memória, coleções, funções e arquivos, com exercícios e testes. Python 3.15."),
    2: ("Livro de Python avançado (Vol. 2)",
        "Python avançado: closures, decoradores, geradores, modelo de dados, orientação a objetos avançada e o CPython por dentro. Livro com exercícios e gabarito."),
    3: ("Livro de Python profissional (Vol. 3)",
        "Python profissional: estrutura de projetos, testes, tipagem, SOLID, segurança, desempenho, threads, processos e asyncio. Livro com exercícios e medições."),
    4: ("Livro de Python com bancos de dados (Vol. 4)",
        "Python com bancos de dados (PostgreSQL, MySQL, Oracle, SQL Server), APIs, Pandas, Polars, Docker, filas e pipelines, mais 66 perguntas de entrevista."),
    5: ("Padrões de projeto em Python (Vol. 5)",
        "Padrões de projeto em Python (design patterns): a versão clássica, a pythônica, quando não usar e o custo medido. Do Strategy ao Repository."),
}



def layout(title, desc, body, extra_attrs="", og="assets/img/og-home.jpg", path="index.html", ld=None, crumbs_ld=None):
    seo = seo_block(title, desc, path, og, (ld or []) + ([breadcrumb_ld(crumbs_ld)] if crumbs_ld else []))
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
{GA_TAG}<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#16182c">
{seo}
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/bricolage-grotesque-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/dm-sans-500.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/site.min.css">
<script>document.documentElement.classList.add("js");</script>
</head>
<body{extra_attrs}>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="site-header" id="topo">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="Python de A a Z, página inicial">Python <span>de</span> <b>A a Z</b></a>
    <nav class="nav" aria-label="Principal">
      <a href="index.html#colecao">Os livros</a>
      <a href="index.html#trilha">Trilha</a>
      <a href="index.html#autor">O autor</a>
      <a class="btn btn--dark btn--sm" href="index.html#colecao">Ver a coleção</a>
    </nav>
  </div>
</header>
<main id="conteudo">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <span class="logo">Python de A a Z</span>
    <nav aria-label="Rodapé">
      <a href="index.html#colecao">Os livros</a>
      <a href="index.html#autor">O autor</a>
      <a href="{GUIA_PATH}">Python do zero ao avançado</a>
      <a href="outras.html">Outras obras</a>
      <a href="mailto:{CONTACT_EMAIL}">Contato</a>
      <a href="termos.html">Termos</a>
    </nav>
    <span>© 2026 Tiago Silva</span>
  </div>
</footer>
<script src="js/app.min.js" defer></script>
</body>
</html>
"""


def crumbs(*items):
    parts = []
    for label, href in items:
        parts.append(f'<a href="{href}">{E(label)}</a>' if href else f"<b>{E(label)}</b>")
    return '<div class="wrap crumbs" aria-label="Você está em"><nav>' + "<span>/</span>".join(parts) + "</nav></div>"


def accordion_row(n, title, right, content):
    return (
        '<details><summary>'
        f'<span class="toc__n">{E(str(n))}</span><span class="toc__t">{E(title)}</span>'
        + (f'<span class="toc__p">{E(right)}</span>' if right else "")
        + f"{CHEV}</summary>{content}</details>"
    )


# ---------------------------------------------------------------- volumes ---
def buy_button(url, label, soon, cls):
    if url:
        return f'<a class="btn {cls}" href="{url}" target="_blank" rel="noopener">{label} {ARROW}</a>'
    return f'<span class="btn {cls} is-soon" aria-disabled="true">{soon}</span>'


def volume_page(v):
    n = v["n"]
    pages = v["pages_miolo"]
    rows = []
    for part in v["parts"]:
        rows.append(f'<div class="toc__part">{E(part["name"])}</div>')
        for c in part["chapters"]:
            rows.append(accordion_row(c["n"], c["title"], f'p. {c["page"]}', f'<div class="toc__d">{E(c["desc"])}</div>'))
    if v["appendices"]:
        rows.append('<div class="toc__part">Apêndices</div>')
        for a in v["appendices"]:
            rows.append(accordion_row(a["letter"], a["title"], f'p. {a["page"]}', f'<div class="toc__d">{E(a["desc"])}</div>'))
    apx = len(v["appendices"])
    count = f'{v["chapters_total"]} capítulos' + (f" e {apx} apêndice" + ("s" if apx > 1 else "") if apx else "")
    paras = "\n".join(f"<p>{E(p)}</p>" for p in v["paras"])
    learn = "\n".join(f"<li>{E(x)}</li>" for x in v["learn"])
    others = "\n".join(
        f'<a class="reveal" data-vol="{o["n"]}" style="--i:{i}" href="livro-{o["n"]}.html">'
        f'<span class="card__cover"><img src="assets/img/capa-{o["n"]}-480.webp" width="480" height="690" alt="" loading="lazy"></span>'
        f'<strong>Volume {o["n"]}: {E(o["topic"])}</strong></a>'
        for i, o in enumerate(x for x in VOLUMES if x["n"] != n)
    )
    body = f"""{crumbs(("Início", "index.html"), ("Os livros", "index.html#colecao"), (f"Volume {n}", None))}
<section class="bookhero" aria-labelledby="titulo">
  <div class="wrap bookhero__grid">
    <div class="bookhero__cover reveal"><img src="assets/img/capa-{n}-960.webp" srcset="assets/img/capa-{n}-480.webp 480w, assets/img/capa-{n}-960.webp 960w" sizes="(max-width: 640px) 80vw, 400px" width="960" height="1380" alt="Capa do Volume {n}: {E(v['topic'])}" fetchpriority="high"></div>
    <div class="bookhero__info">
      <span class="pill reveal">Volume {n} de 5</span>
      <h1 class="display reveal" id="titulo" style="--i:1">Python de A a Z: <span>{E(v['topic'])}</span></h1>
      <p class="by reveal" style="--i:2">por Tiago Silva</p>
      <!-- avaliações (estrelas, nota e contagem) ocultas por enquanto -->
      <p class="lead reveal" style="--i:3">{E(v['lead'])}</p>
      <div class="buybox reveal" style="--i:4">
        <div class="prices">
          <div class="price"><small>Impresso</small><b>R$ {v['price_print']}</b></div>
          <div class="price"><small>E-book</small><b>R$ {v['price_ebook']}</b></div>
        </div>
        <div class="buybox__actions">
          {buy_button(v['links']['print'], 'Comprar impresso na UICLAP', 'Impresso: em breve', 'btn--v')}
          {buy_button(v['links']['ebook'], 'Comprar e-book na Amazon', 'E-book na Amazon: em breve', 'btn--white')}
        </div>
      </div>
      <dl class="ficha reveal" style="--i:5">
        <div><dt>Páginas</dt><dd>{pages}</dd></div>
        <div><dt>Idioma</dt><dd>Português</dd></div>
        <div><dt>Publicação</dt><dd>10/2026</dd></div>
        <div><dt>Versão do Python</dt><dd>3.15</dd></div>
        <div><dt>Formatos</dt><dd>Impresso e e-book (ePub)</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="about" id="sobre">
  <div class="wrap about__grid">
    <div class="about__text">
      <p class="eyebrow reveal">Sobre este livro</p>
      <h2 class="display reveal" style="--i:1">{E(v['headline'])}</h2>
      {paras}
      <div class="card-dark reveal"><h3>Por onde começar</h3><p>{E(v['start'])}</p></div>
      <div class="card-soft reveal"><h3>O que você vai aprender</h3><ul>
{learn}
</ul></div>
    </div>
    <div class="toc-wrap" id="sumario">
      <h2>Sumário</h2>
      <p>{count}. Toque em um item para ver do que ele trata.</p>
      <div class="toc"><div class="toc__scroll" data-lenis-prevent>
{chr(10).join(rows)}
</div></div>
    </div>
  </div>
</section>

<!-- Avaliações: ocultas por enquanto (remova o atributo hidden quando houver avaliações reais) -->
<section class="reviews section" id="avaliacoes" hidden>
  <div class="wrap">
    <p class="eyebrow">Avaliações</p>
    <h2 class="display" style="margin-top:10px;font-size:clamp(32px,5vw,44px)">O que os leitores dizem</h2>
    <div class="reviews__grid"><figure class="review" style="margin:0"><div class="stars" aria-label="5 de 5 estrelas">★★★★★</div><blockquote style="margin:0">Texto da avaliação.</blockquote><figcaption><b>Nome Sobrenome</b></figcaption></figure></div>
  </div>
</section>

<section class="section others">
  <div class="wrap">
    <h2 class="display reveal">Continue a trilha</h2>
    <div class="others__grid">
{others}
    </div>
  </div>
</section>"""
    title = f"{SEO_VOL[n][0]} | Python de A a Z"
    path = f"livro-{n}.html"
    book = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": f"Python de A a Z, Volume {n}: {v['topic']}",
        "url": abs_url(path),
        "image": abs_url(f"assets/img/capa-{n}-960.webp"),
        "description": SEO_VOL[n][1],
        "author": AUTHOR_LD,
        "inLanguage": "pt-BR",
        "bookFormat": "https://schema.org/Paperback",
        "numberOfPages": v["pages_miolo"],
        "datePublished": "2026-10",
        "isPartOf": SERIES_LD,
        "position": n,
        "workExample": [
            {"@type": "Book", "bookFormat": "https://schema.org/Paperback", "inLanguage": "pt-BR"},
            {"@type": "Book", "bookFormat": "https://schema.org/EBook", "inLanguage": "pt-BR"},
        ],
        "offers": [
            {"@type": "Offer", "name": label, "price": v[price].replace(",", "."), "priceCurrency": "BRL", "url": v["links"][fmt],
             "availability": "https://schema.org/InStock"}
            for label, price, fmt in (("Impresso", "price_print", "print"), ("E-book", "price_ebook", "ebook")) if v["links"][fmt]
        ],
    }
    return layout(
        title, SEO_VOL[n][1], body, f' data-vol="{n}"', og=f"assets/img/og-livro-{n}.jpg", path=path, ld=[book],
        crumbs_ld=[("Início", "index.html"), ("Os livros", "index.html#colecao"), (f"Volume {n}", path)],
    )


# ------------------------------------------------- livros da Casa do Código ---
def theme_style(t):
    return f' style="--v-bg:{t["bg"]};--v-tint:{t["tint"]};--v-ink:{t["ink"]};--v-accent:{t["accent"]}"'


def external_page(b):
    t = b["theme"]
    key = b["key"]
    others = [o for k, o in BOOKS.items() if k != key]
    toc_rows = []
    for part in b["toc"]:
        toc_rows.append(f'<div class="toc__part">{E(part["label"])}: {E(part["name"])}</div>')
        for c in part["chapters"]:
            secs = "".join(f"<li>{E(s)}</li>" for s in c["sections"])
            content = f'<div class="toc__d"><ul>{secs}</ul></div>' if secs else ""
            if content:
                toc_rows.append(accordion_row(c["n"], c["title"], "", content))
            else:
                toc_rows.append(
                    f'<div style="display:flex;align-items:center;gap:14px;padding:14px 22px;border-bottom:1px solid rgba(22,24,44,.14)"><span class="toc__n">{E(c["n"])}</span><span class="toc__t">{E(c["title"])}</span></div>'
                )
    paras = "\n".join(f"<p>{E(p)}</p>" for p in b["paragraphs"])
    learn = "\n".join(f"<li>{E(x)}</li>" for x in b["learn"])
    chips = "".join(f'<span class="chip">{E(c)}</span>' for c in b["chips"])
    facts = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in b["facts"])
    audience = f'<div class="card-soft reveal"><h3>Para quem é</h3><p>{E(b["audience"])}</p></div>' if b["audience"] else ""
    prereq = f'<div class="card-soft reveal"><h3>Pré-requisitos</h3><p>{E(b["prereq"])}</p></div>' if b["prereq"] else ""
    if b["soon"]:
        cover = f'<div class="bookhero__cover reveal"><div class="soon-tile"><b>Em<br>breve</b><span>novembro de 2026</span></div></div>'
        pill = '<span class="pill pill--gold reveal">Lançamento · novembro de 2026</span>'
        buy = f"""<div class="buybox reveal" style="--i:4">
        <div><div class="price"><small>Formatos</small><b style="font-size:22px">Impresso e e-book (ePub)</b></div></div>
        <div class="buybox__actions"><a class="btn btn--v" href="{DRF_MAILTO}">Quero saber quando sair</a><a class="btn btn--white" href="#sumario">Ver sumário</a></div>
      </div>"""
        og = "assets/img/capa-1-960.webp"
    else:
        cover = f'<div class="bookhero__cover reveal"><img src="{b["cover"]}" width="341" height="480" alt="Capa do livro {E(b["title"])}" fetchpriority="high" style="aspect-ratio:341/480"></div>'
        pill = '<span class="pill reveal">Casa do Código</span>'
        p = b["prices"]
        buy = f"""<div class="buybox reveal" style="--i:4">
        <div><small style="display:block;font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--v-ink)">Preços na Casa do Código</small>
        <div class="prices" style="margin-top:8px">
          <div class="price"><small>Impresso</small><b style="font-size:28px">R$ {p['print']}</b></div>
          <div class="price"><small>E-book</small><b style="font-size:28px">R$ {p['ebook']}</b></div>
          <div class="price"><small>E-book + impresso</small><b style="font-size:28px">R$ {p['combo']}</b></div>
        </div></div>
        <div class="buybox__actions"><a class="btn btn--v" href="{b['buy']}" target="_blank" rel="noopener">Comprar na Casa do Código {ARROW}</a><a class="btn btn--white" href="#sumario">Ver sumário</a></div>
      </div>
      <p class="note">Quem compra o e-book tem acesso às atualizações futuras do livro.</p>"""
        og = b["cover"]
    toc_link = (
        f'<a class="btn btn--white btn--sm" href="{b["toc_link"]}" target="_blank" rel="noopener">Sumário completo na Casa do Código {ARROW}</a>' if b["toc_link"] else ""
    )
    mini = "".join(
        f'<a class="mini" href="{o["key"]}.html">'
        + (f'<img src="{o["cover"]}" width="341" height="480" alt="" loading="lazy">' if o["cover"] else '<span class="soon" aria-hidden="true">Nov</span>')
        + f'<div><strong>{E(o["title"])}</strong><span>{"Em breve · novembro" if o["soon"] else "Casa do Código"}</span></div></a>'
        for o in others
    )
    body = f"""{crumbs(("Início", "index.html"), ("Outras obras", "outras.html"), (b["title"], None))}
<section class="bookhero" aria-labelledby="titulo">
  <div class="wrap bookhero__grid">
    {cover}
    <div class="bookhero__info">
      {pill}
      <h1 class="display reveal" id="titulo" style="--i:1">{E(b['title'])}</h1>
      <p class="by reveal" style="--i:2">por Tiago Silva · Casa do Código</p>
      <p class="lead reveal" style="--i:3">{E(b['subtitle'])}</p>
      {buy}
      {('<dl class="ficha reveal" style="--i:5">' + facts + '</dl>') if facts else ''}
    </div>
  </div>
</section>

<section class="about" id="sobre">
  <div class="wrap about__grid">
    <div class="about__text">
      <p class="eyebrow reveal">Sobre este livro</p>
      <h2 class="display reveal" style="--i:1">{E(b['headline'])}</h2>
      {paras}
      {audience}
      {prereq}
      <div class="chips reveal">{chips}</div>
      <div class="card-soft reveal"><h3>O que você vai aprender</h3><ul>
{learn}
</ul></div>
    </div>
    <div class="toc-wrap" id="sumario">
      <h2>Sumário</h2>
      <p>Toque em um capítulo para ver as seções.</p>
      <div class="toc"><div class="toc__scroll" data-lenis-prevent>
{chr(10).join(toc_rows)}
</div></div>
      {toc_link}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="authorbox reveal">
      <img src="assets/img/autor-360.webp" width="360" height="360" alt="Tiago Silva" loading="lazy">
      <div><h3>Tiago Silva</h3><p>{E(BIO_SHORT)}</p></div>
      <a class="btn btn--gold btn--sm" href="https://www.linkedin.com/in/tiagoluizrs/" target="_blank" rel="noopener">LinkedIn</a>
    </div>
  </div>
</section>

<section class="wrap" style="padding-bottom:clamp(48px,7vw,88px)">
  <div class="more reveal">
    <div class="more__intro"><small>Do mesmo autor</small><strong>Conheça outras obras</strong><span>Livros sobre frameworks web em Python, pela Casa do Código.</span></div>
    <div class="more__list">{mini}</div>
    <a class="btn btn--chip btn--sm" href="index.html#colecao">Ver a coleção Python de A a Z</a>
  </div>
</section>"""
    desc = trunc(b["subtitle"] + ". " + b["paragraphs"][0], 158)
    path = f"{key}.html"
    isbn = next((val for name, val in b["facts"] if name == "ISBN"), None)
    pages = next((val for name, val in b["facts"] if name == "Páginas"), None)
    pub = next((val for name, val in b["facts"] if name == "Publicação"), None)
    book = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": b["title"],
        "url": abs_url(path),
        "image": abs_url(og if not b["soon"] else "assets/img/og-home.jpg"),
        "description": b["subtitle"],
        "author": AUTHOR_LD,
        "publisher": {"@type": "Organization", "name": "Casa do Código", "url": "https://www.casadocodigo.com.br"},
        "inLanguage": "pt-BR",
        "datePublished": "2026-11" if b["soon"] else (f"{pub[3:]}-{pub[:2]}" if pub else None),
    }
    if isbn:
        book["isbn"] = isbn.replace("-", "")
    if pages:
        book["numberOfPages"] = int(pages)
    if b["prices"] and b["buy"]:
        book["offers"] = [
            {"@type": "Offer", "name": name, "price": b["prices"][k].replace(",", "."), "priceCurrency": "BRL", "url": b["buy"]}
            for name, k in (("Impresso", "print"), ("E-book", "ebook"), ("E-book + impresso", "combo"))
        ]
    book = {k: v for k, v in book.items() if v is not None}
    return layout(
        f"{b['title']} · Tiago Silva", desc, body, theme_style(t), og=f"assets/img/og-{key}.jpg", path=path, ld=[book],
        crumbs_ld=[("Início", "index.html"), ("Outras obras", "outras.html"), (b["title"], path)],
    )


def outras_page():
    cards = []
    for k in ("flask", "django", "drf"):
        b = BOOKS[k]
        chips = "".join(f'<span class="chip">{E(c)}</span>' for c in b["chips"][:6])
        if b["soon"]:
            cards.append(
                f"""<article class="outra outra--soon reveal"{theme_style(b['theme'])}>
  <a class="outra__cover" href="drf.html" aria-hidden="true" tabindex="-1"><div class="soon-tile"><b>Em<br>breve</b><span>novembro de 2026</span></div></a>
  <div><span class="pill pill--gold">Lançamento · novembro de 2026</span>
  <h2 class="display"><a href="drf.html">{E(b['title'])}</a></h2><p class="sub">Casa do Código</p>
  <p class="txt">{E(b['subtitle'])}</p><div class="chips">{chips}</div>
  <p class="note" style="margin-top:16px"><b>Formatos:</b> impresso e e-book (ePub)</p>
  <div class="actions"><a class="btn btn--v" href="drf.html">Ver detalhes e sumário</a><a class="btn btn--chip" href="{DRF_MAILTO}">Quero saber quando sair</a></div></div>
</article>"""
            )
        else:
            p = b["prices"]
            facts = "".join(f"<div><dt>{E(a)}</dt><dd>{E(c)}</dd></div>" for a, c in b["facts"] if a in ("Páginas", "Publicação", "ISBN"))
            prices = f'<div><dt>Impresso</dt><dd>R$ {p["print"]}</dd></div><div><dt>E-book</dt><dd>R$ {p["ebook"]}</dd></div><div><dt>E-book + impresso</dt><dd>R$ {p["combo"]}</dd></div>'
            cards.append(
                f"""<article class="outra reveal"{theme_style(b['theme'])}>
  <a class="outra__cover" href="{k}.html" aria-hidden="true" tabindex="-1"><img src="{b['cover']}" width="341" height="480" alt="" loading="lazy"></a>
  <div><span class="pill">Casa do Código</span>
  <h2 class="display"><a href="{k}.html">{E(b['title'])}</a></h2><p class="sub">{E(b['subtitle'])}</p>
  <p class="txt">{E(b['paragraphs'][0])}</p><div class="chips">{chips}</div>
  <dl class="ficha">{facts}{prices}</dl>
  <div class="actions"><a class="btn btn--v" href="{k}.html">Ver detalhes e sumário</a><a class="btn btn--gold" href="{b['buy']}" target="_blank" rel="noopener">Comprar na Casa do Código {ARROW}</a></div></div>
</article>"""
            )
    body = f"""{crumbs(("Início", "index.html"), ("Outras obras", None))}
<section class="section" style="padding-bottom:24px">
  <div class="wrap">
    <p class="eyebrow reveal" style="color:var(--soft)">Tiago Silva</p>
    <h1 class="display reveal" style="--i:1;margin-top:12px;font-size:clamp(40px,7vw,64px);line-height:.98;letter-spacing:-0.03em">Outras obras do autor</h1>
    <p class="lead reveal" style="--i:2;max-width:620px">Livros sobre frameworks web em Python, publicados pela Casa do Código. Se você já domina os fundamentos da coleção Python de A a Z, estes são o próximo passo na prática.</p>
  </div>
</section>
<section class="wrap outras__list">
{chr(10).join(cards)}
</section>
<section class="section">
  <div class="wrap cta">
    <h2 class="display reveal" style="font-size:clamp(28px,4vw,34px)">Quer começar pelos fundamentos?</h2>
    <a class="btn btn--gold reveal" style="--i:1" href="index.html#colecao">Ver a coleção Python de A a Z</a>
  </div>
</section>"""
    return layout(
        "Outras obras do autor · Python de A a Z",
        "Livros sobre frameworks web em Python, de Tiago Silva, pela Casa do Código: Flask de A a Z, Django de A a Z e Django Rest Framework de A a Z.",
        body, og="assets/img/og-home.jpg", path="outras.html",
        crumbs_ld=[("Início", "index.html"), ("Outras obras", "outras.html")],
    )


def termos_page():
    body = f"""{crumbs(("Início", "index.html"), ("Termos de uso e privacidade", None))}
<section class="section">
  <div class="wrap prose">
    <p class="eyebrow reveal" style="color:var(--soft)">Atualizado em 21 de outubro de 2026</p>
    <h1 class="display reveal" style="--i:1">Termos de uso e privacidade</h1>
    <p class="lead reveal" style="--i:2">Regras simples para usar este site, e o que acontece com os seus dados: nenhum dado pessoal é coletado por aqui.</p>

    <h2>1. Sobre este site</h2>
    <p>Este site divulga a coleção <b>Python de A a Z</b> e outras obras de Tiago Silva. Ele não vende nada diretamente: as compras acontecem em lojas de terceiros, como a UICLAP, a Amazon e a Casa do Código, que têm seus próprios termos, preços e políticas.</p>

    <h2>2. Preços e informações</h2>
    <p>Preços, formatos, número de páginas, sumários e demais informações podem mudar. Procuramos mantê-los corretos, mas vale sempre o que a loja mostrar no momento da compra. Não há garantia de que as informações estejam livres de erros ou atualizadas.</p>

    <h2>3. Direitos autorais</h2>
    <p>Textos, sumários, capas, imagens e demais conteúdos deste site são © 2026 Tiago Silva, todos os direitos reservados. Você pode citar trechos curtos, com crédito e link para o site. A reprodução integral ou o uso comercial exigem autorização por escrito. Os exemplos de código dos livros ficam em um repositório público no GitHub, que traz a licença aplicável no próprio repositório.</p>

    <h2>4. Marcas</h2>
    <p>Python, Django, Flask e os demais nomes citados pertencem aos seus respectivos titulares. A citação não indica vínculo, patrocínio ou aprovação por parte deles.</p>

    <h2>5. Privacidade</h2>
    <p>Este site não tem cadastro, login, formulários nem publicidade, e não pede nenhum dado pessoal para você navegar. As fontes de texto e as imagens são servidas pelo próprio site.</p>
    <p>Para entender quantas pessoas visitam o site e quais páginas interessam mais, usamos o <b>Google Analytics</b>. Ele pode usar cookies e coletar dados de uso de forma agregada, como as páginas visitadas, o tipo de dispositivo, o navegador e a localização aproximada. Esses dados são tratados pelo Google, conforme a política de privacidade dele, e não usamos o Analytics para identificar você. Você pode bloquear os cookies nas configurações do navegador ou usar um bloqueador de rastreamento.</p>
    <p>O site é hospedado no GitHub Pages. O GitHub pode registrar dados técnicos de acesso, como o endereço IP, conforme a política de privacidade dele.</p>
    <p>Se você escrever para o e-mail de contato, usaremos o seu endereço e a sua mensagem apenas para responder. Não compartilhamos esses dados com terceiros. Para pedir acesso, correção ou exclusão (direitos previstos na Lei Geral de Proteção de Dados, a LGPD), escreva para o mesmo e-mail.</p>

    <h2>6. Links externos</h2>
    <p>O site tem links para lojas, redes profissionais e outros endereços. Não controlamos esses sites e não nos responsabilizamos pelo conteúdo nem pelas políticas deles.</p>

    <h2>7. Alterações</h2>
    <p>Estes termos podem ser atualizados. A data da última atualização aparece no topo desta página.</p>

    <h2>8. Contato</h2>
    <p>Dúvidas, pedidos ou sugestões: <a href="mailto:{CONTACT_EMAIL}"><b>{CONTACT_EMAIL}</b></a>.</p>
  </div>
</section>"""
    return layout(
        "Termos de uso e privacidade · Python de A a Z",
        "Termos de uso e privacidade do site Python de A a Z: preços e informações, direitos autorais, o que o site coleta (nenhum dado pessoal) e como falar com o autor.",
        body, og="assets/img/og-home.jpg", path="termos.html",
        crumbs_ld=[("Início", "index.html"), ("Termos de uso e privacidade", "termos.html")],
    )


GUIA_PATH = "livro-python-do-basico-ao-avancado.html"
GUIA_FAQ = [
    ("Qual livro de Python devo ler se nunca programei?",
     "O Volume 1, Fundamentos. Ele parte do zero absoluto e não exige nenhum conhecimento prévio de programação: instala o ambiente, explica variáveis, tipos e memória, e avança por coleções, funções, texto, arquivos, datas e a biblioteca padrão."),
    ("Esta coleção ensina Python do básico ao avançado?",
     "Sim. O Volume 1 cobre a base. O Volume 2 aprofunda a linguagem (decoradores, geradores, modelo de dados, orientação a objetos avançada). O Volume 3 trata de engenharia e concorrência, o Volume 4 de bancos de dados, APIs, análise de dados e produção, e o Volume 5 de padrões de projeto."),
    ("Preciso ler os 5 volumes em ordem?",
     "Não. Cada volume foi escrito para ser lido sozinho, com a lista de pré-requisitos no começo. Quem está começando deve seguir a ordem; quem já programa pode entrar direto no volume de que precisa."),
    ("Qual versão do Python os livros usam?",
     "O Python 3.15, lançado em outubro de 2026. Recursos de versões anteriores trazem o selo da versão em que surgiram, e o Apêndice A do Volume 2 reúne as novidades do Python 3.8 ao 3.15."),
    ("Os livros têm exercícios?",
     "Sim. Todo capítulo traz exercícios com gabarito e testes automatizados. Todo o código, os exercícios e os testes estão em um repositório público no GitHub, organizado por volume e por capítulo."),
    ("Onde comprar?",
     "A versão impressa de cada volume está na UICLAP, com o link na página de cada livro. O e-book na Amazon ainda não foi lançado."),
    ("Quem escreveu a coleção?",
     "Tiago Silva, professor universitário e analista de sistemas, com mais de 10 anos de experiência com Python. A coleção reúne as experiências de mercado, as recomendações e as dores que ele viveu nesses anos."),
]


def guia_page():
    rows = []
    levels = {1: "Iniciante", 2: "Intermediário a avançado", 3: "Avançado", 4: "Avançado, com foco em mercado", 5: "Avançado"}
    for v in VOLUMES:
        n = v["n"]
        rows.append(
            f'<li><a href="livro-{n}.html"><b>Volume {n}: {E(v["topic"])}</b></a> ({levels[n]}). {E(v["short"])}</li>'
        )
    learn = "".join(f"<li>{E(x)}</li>" for x in (
        "Montar um ambiente profissional com ambientes virtuais e o uv",
        "Entender variáveis, tipos, memória, listas, dicionários e conjuntos",
        "Dominar decoradores, geradores, o modelo de dados e a orientação a objetos avançada",
        "Estruturar projetos, escrever testes, usar tipagem estática e aplicar SOLID",
        "Escolher entre threads, multiprocessamento e asyncio com base em medições",
        "Trabalhar com SQL, PostgreSQL, MySQL, SQLAlchemy, Redis e MongoDB",
        "Consumir APIs, validar dados com Pydantic e analisar dados com Pandas e Polars",
        "Levar o código para produção com Docker, filas e pipelines",
        "Aplicar padrões de projeto na versão pythônica, sabendo quando não usar",
    ))
    faq = "".join(f"<h3>{E(q)}</h3>\n    <p>{E(a)}</p>\n    " for q, a in GUIA_FAQ)
    body = f"""{crumbs(("Início", "index.html"), ("Livro de Python do básico ao avançado", None))}
<section class="section">
  <div class="wrap prose">
    <p class="eyebrow reveal" style="color:var(--soft)">Python do zero ao avançado</p>
    <h1 class="display reveal" style="--i:1">Livro de Python do básico ao avançado</h1>
    <p class="lead reveal" style="--i:2">Python de A a Z é uma coleção de 5 volumes para aprender Python do zero ao avançado, em português: do primeiro print() ao código em produção, com exercícios, testes automatizados e todo o código em um repositório público.</p>

    <h2>Python do zero ao avançado em 5 volumes</h2>
    <p>A coleção foi pensada como um caminho. O primeiro volume é um livro de Python para iniciantes. Os seguintes levam você, volume a volume, até o nível profissional: dominar a linguagem, escrever software que outras pessoas conseguem manter, trabalhar com dados e produção, e projetar com padrões de projeto.</p>
    <ul>{"".join(rows)}</ul>

    <h2>Qual volume ler primeiro?</h2>
    <ul>
      <li><b>Nunca programou:</b> comece pelo <a href="livro-1.html">Volume 1</a>. Nenhum conhecimento prévio é necessário.</li>
      <li><b>Já programa em outra linguagem:</b> use o Volume 1 como referência (capítulos 3 a 9) ou vá ao <a href="livro-2.html">Volume 2</a>.</li>
      <li><b>Já escreve scripts em Python e quer entender a linguagem a fundo:</b> <a href="livro-2.html">Volume 2</a>.</li>
      <li><b>Quer escrever Python profissional, com testes, tipagem e concorrência:</b> <a href="livro-3.html">Volume 3</a>.</li>
      <li><b>Quer trabalhar com bancos de dados, APIs, análise de dados e produção:</b> <a href="livro-4.html">Volume 4</a>.</li>
      <li><b>Quer aprender padrões de projeto em Python:</b> <a href="livro-5.html">Volume 5</a>, que pressupõe a base dos volumes anteriores.</li>
    </ul>

    <h2>O que você vai aprender</h2>
    <ul>{learn}</ul>

    <h2>Python e o mercado de trabalho</h2>
    <p>Vagas de Python costumam pedir mais do que sintaxe: uma base sólida, engenharia (testes, segurança e desempenho) e produção (bancos de dados, APIs, Docker e filas). Cada volume cobre uma etapa desse caminho. O Volume 4 reúne ainda 66 perguntas de entrevista técnica, com respostas, de júnior a sênior.</p>

    <h2>Como são os livros</h2>
    <p>São 2.490 páginas no total, escritas com o <b>Python 3.15</b>. Todo capítulo traz exemplos executáveis, as pegadinhas que derrubam quem está começando, exercícios com gabarito e testes automatizados. O código, os exercícios e os testes ficam no <a href="https://github.com/tiagoluizrs/python-de-a-a-z-codigos" target="_blank" rel="noopener">repositório da coleção no GitHub</a>. Cada volume é uma obra de referência: não é preciso lê-lo de capa a capa.</p>

    <h2>Perguntas frequentes</h2>
    {faq}
    <p><a class="btn btn--dark" href="index.html#colecao">Ver os 5 volumes</a> <a class="btn btn--gold" href="https://loja.uiclap.com/titulo/ua213612" target="_blank" rel="noopener">Comprar o Volume 1</a></p>
  </div>
</section>"""
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in GUIA_FAQ],
    }
    return layout(
        "Livro de Python do básico ao avançado | Python de A a Z",
        "Livro de Python do zero ao avançado em 5 volumes: fundamentos, domínio da linguagem, engenharia, dados e produção e padrões de projeto. Veja qual ler primeiro.",
        body, og="assets/img/og-home.jpg", path=GUIA_PATH, ld=[faq_ld],
        crumbs_ld=[("Início", "index.html"), ("Livro de Python do básico ao avançado", GUIA_PATH)],
    )


PAGES = ["index.html", GUIA_PATH] + [f"livro-{n}.html" for n in range(1, 6)] + ["flask.html", "django.html", "drf.html", "outras.html", "termos.html"]


def update_home():
    """Injeta o SEO na Home (index.html é escrita à mão; o bloco entre os marcadores é gerado aqui)."""
    p = ROOT / "index.html"
    text = p.read_text(encoding="utf-8")
    title = "Livro de Python do zero ao avançado | Python de A a Z (5 volumes)"
    m = __import__("re").search(r'<meta name="description" content="([^"]*)">', text)
    desc = html.unescape(m.group(1))
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": abs_url("#site"), "name": "Python de A a Z", "url": abs_url(""), "inLanguage": "pt-BR", "publisher": {"@id": abs_url("#autor")}},
            {"@type": "Person", "@id": abs_url("#autor"), "name": "Tiago Silva", "url": "https://www.linkedin.com/in/tiagoluizrs/", "image": abs_url("assets/img/autor-720.webp"),
             "jobTitle": "Analista de Sistemas e professor universitário", "knowsAbout": ["Python", "Java", "JavaScript", "Engenharia de software"]},
            {"@type": "ItemList", "name": "A coleção Python de A a Z", "itemListElement": [
                {"@type": "ListItem", "position": v["n"], "url": abs_url(f"livro-{v['n']}.html"), "name": f"Volume {v['n']}: {v['topic']}"} for v in VOLUMES]},
        ],
    }
    block = seo_block(title, desc, "index.html", "assets/img/og-home.jpg", [graph])
    new = text[: text.index("<!-- seo:start -->") + len("<!-- seo:start -->")] + "\n" + block + "\n" + text[text.index("<!-- seo:end -->") :]
    p.write_text(new, encoding="utf-8")
    t = __import__("re").search(r"<title>(.*?)</title>", new).group(1)
    assert t == title, "o <title> da Home mudou; ajuste o título em update_home()"


def lastmod(path):
    """Data do último commit do arquivo; se ele foi alterado e ainda não commitado (ou é novo), a data de hoje."""
    import datetime
    import subprocess

    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if dirty:
            return datetime.date.today().isoformat()
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return out or datetime.date.today().isoformat()
    except OSError:
        return datetime.date.today().isoformat()


def write_sitemap_and_robots():
    urls = "\n".join(
        f"  <url><loc>{page_url(p)}</loc><lastmod>{lastmod(p)}</lastmod><changefreq>monthly</changefreq><priority>{'1.0' if p == 'index.html' else '0.9' if p == GUIA_PATH or p.startswith('livro-') else '0.8'}</priority></url>"
        for p in PAGES
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8"
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('sitemap.xml')}\n", encoding="utf-8")


def minify():
    """CSS e JS minificados com esbuild (via npx). Gera css/site.min.css e js/app.min.js."""
    import shutil
    import subprocess

    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        print("AVISO: npx não encontrado; css/site.min.css e js/app.min.js não foram atualizados.")
        return
    css_src = (ROOT / "css" / "style.css").read_text(encoding="utf-8") + "\n" + (ROOT / "css" / "pages.css").read_text(encoding="utf-8")
    tmp_css = ROOT / "css" / "_bundle.tmp.css"
    tmp_css.write_text(css_src, encoding="utf-8")
    subprocess.run([npx, "--yes", "esbuild", str(tmp_css), "--minify", "--legal-comments=none", f"--outfile={ROOT / 'css' / 'site.min.css'}"], check=True, capture_output=True)
    tmp_css.unlink()
    main_min = ROOT / "js" / "_main.tmp.js"
    subprocess.run([npx, "--yes", "esbuild", str(ROOT / "js" / "main.js"), "--minify", "--legal-comments=none", f"--outfile={main_min}"], check=True, capture_output=True)
    lenis = (ROOT / "js" / "lenis.min.js").read_text(encoding="utf-8")
    lenis = lenis.split("//# sourceMappingURL")[0]
    (ROOT / "js" / "app.min.js").write_text("/*! Lenis 1.3.4 (MIT) https://github.com/darkroomengineering/lenis */\n" + lenis + "\n" + main_min.read_text(encoding="utf-8"), encoding="utf-8")
    main_min.unlink()
    print("minificados: css/site.min.css e js/app.min.js")


def main():
    written = []
    for v in VOLUMES:
        name = f"livro-{v['n']}.html"
        (ROOT / name).write_text(volume_page(v), encoding="utf-8")
        written.append(name)
    for k in ("flask", "django", "drf"):
        name = f"{k}.html"
        (ROOT / name).write_text(external_page(BOOKS[k]), encoding="utf-8")
        written.append(name)
    (ROOT / "outras.html").write_text(outras_page(), encoding="utf-8")
    written.append("outras.html")
    (ROOT / "termos.html").write_text(termos_page(), encoding="utf-8")
    written.append("termos.html")
    (ROOT / GUIA_PATH).write_text(guia_page(), encoding="utf-8")
    written.append(GUIA_PATH)
    update_home()
    write_sitemap_and_robots()
    minify()
    print("geradas:", ", ".join(written), "| index.html (SEO), sitemap.xml, robots.txt")


main()
