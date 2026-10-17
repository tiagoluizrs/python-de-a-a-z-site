# Site Python de A a Z

Site estático (HTML, CSS e JavaScript puros), sem framework no navegador.

## Ver no computador
Abra `index.html` no navegador, ou rode um servidor na pasta `site`:

    python -m http.server 8000

e abra http://localhost:8000.

## Estrutura
- `index.html`: Home, escrita à mão. O SEO do `<head>` (entre `<!-- seo:start -->` e `<!-- seo:end -->`) é gerado pelo `build.py`.
- `livro-1.html` a `livro-5.html`, `flask.html`, `django.html`, `drf.html`, `outras.html`: **geradas** pelo `build.py`. Não edite à mão.
- `data/volumes.json` e `data/books.json`: textos, sumários, preços e fichas. É aqui que se muda o conteúdo.
- `css/style.css` (base e Home) e `css/pages.css` (páginas internas): fontes dos estilos.
- `js/main.js`: rolagem suave, efeitos de rolagem, revelar ao rolar, contadores, inclinação da capa. `js/lenis.min.js`: Lenis 1.3.4 (MIT).
- `css/site.min.css` e `js/app.min.js`: **minificados**, são os arquivos que as páginas carregam.
- `assets/img` (WebP e imagens de compartilhamento `og-*.jpg`), `assets/fonts` (Bricolage Grotesque e DM Sans, hospedadas aqui).
- `sitemap.xml` e `robots.txt`: gerados.
- `tools/make_og.py`: gera as imagens de compartilhamento 1200 x 630 (precisa do Pillow).

## Atualizar o site
1. Edite `data/*.json`, `css/*.css`, `js/main.js` ou `index.html`.
2. Rode `python build.py` (precisa de Python e Node/npx; o esbuild é baixado pelo npx na primeira vez). Ele regenera as páginas, o SEO, o sitemap, o robots e os arquivos minificados.
3. Se mudou capas ou textos de compartilhamento: `python tools/make_og.py`.

## SEO (em todas as páginas)
Título e descrição únicos, `canonical`, Open Graph e Twitter Card com imagem 1200 x 630, `robots`, dados estruturados JSON-LD (WebSite, Person e lista de livros na Home; Book e BreadcrumbList nas internas), um único `h1` por página, `alt` nas imagens, `lang="pt-BR"`, sitemap e robots.
O endereço público está em `SITE_URL` no topo do `build.py` (hoje `https://pythondeaaz.com.br`). Se o domínio mudar, altere e rode o build.

## Efeitos e cuidados
- Leque de capas com paralaxe, trilha que se preenche ao rolar, números que contam, itens que aparecem ao rolar, capa que inclina com o mouse.
- `prefers-reduced-motion`: sem rolagem suave e sem animações, tudo visível.
- Celular: o leque fica parado; rolagem suave só com mouse/trackpad. Sem JavaScript o conteúdo continua visível.

## Pendências
- Links da loja e da amostra (`href="#"` com `data-todo`): colocar quando as lojas estiverem no ar.
- "Contato" abre o e-mail e "Termos" é a página `termos.html` (gerada pelo `build.py`; o texto está na função `termos_page`).
- Avaliações: seções prontas e ocultas com `hidden` (remova o atributo quando houver avaliações reais).
- Dados estruturados de preço dos volumes: confirmar quando as lojas estiverem no ar.

## Publicar (GitHub Pages)
Use um repositório **público e separado**, só com o conteúdo desta pasta (o repositório do livro é privado). Settings > Pages > Deploy from a branch (`main`, raiz) e, em Custom domain, `pythondeaaz.com.br`. DNS no registro.br: quatro registros A (`@`) 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153; quatro AAAA (`@`) 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153; e um CNAME `www` apontando para `tiagoluizrs.github.io`. Depois marque "Enforce HTTPS".
