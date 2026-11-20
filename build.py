#!/usr/bin/env python3
"""Gera o site estático Cripto em Dia em ./docs (GitHub Pages: branch main, pasta /docs).

Conteúdo:
  conteudo/paginas/*.md   -> páginas fixas (guias, sobre, aviso legal...)
  conteudo/boletim/*.md   -> boletins diários (nome do arquivo: AAAA-MM-DD-slug.md)
Configuração: site.json
"""
import json
import re
import shutil
from datetime import date, datetime
from html import escape
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
CFG = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data: https://*.coingecko.com; "
       "connect-src https://api.coingecko.com https://api.alternative.me; "
       "frame-src https://ad.a-ads.com https://*.a-ads.com; "
       "form-action 'self'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def data_br(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


SAFE_URL = re.compile(r"^(https://|http://|\.\./|\./|#|[a-z0-9][a-z0-9\-/]*/?$)", re.I)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[a-z0-9\-]*[a-z0-9])?(?:/[a-z0-9]+(?:[a-z0-9\-]*[a-z0-9])?)*$")


class BuildError(Exception):
    pass


def _safe_attr(match):
    attr, url = match.group(1), match.group(2)
    if not SAFE_URL.match(url.strip()):
        return f'{attr}="#"'
    return match.group(0)


def sanitize_html(html: str) -> str:
    """Defesa extra: links e imagens só com URLs seguras; links externos com rel=noopener."""
    html = re.sub(r'(href|src)="([^"]*)"', _safe_attr, html)
    html = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener noreferrer"', html)
    return html


def parse(path: Path):
    raw = path.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) < 3:
            raise BuildError(f"{path.name}: cabeçalho '---' sem fechamento")
        _, fm, body = parts
        for line in fm.strip().splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    # HTML cru não é permitido no conteúdo: '<' vira entidade antes do Markdown
    body = body.replace("<", "&lt;")
    html = markdown.markdown(body, extensions=["tables", "sane_lists"])
    return meta, sanitize_html(html)


def ld_json(obj) -> str:
    txt = json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'<script type="application/ld+json">{txt}</script>'


_email = str(CFG.get("contato_email", "")).strip()
if _email and not re.match(r"^[^@\s<>\"']+@[^@\s<>\"']+\.[a-z]{2,}$", _email, re.I):
    raise BuildError("site.json: contato_email inválido")
CONTATO_HTML = (f'pelo e-mail <a href="mailto:{escape(_email)}">{escape(_email)}</a>' if _email
                else "pelo e-mail de suporte que aparece no seu recibo de compra")


def rel(depth: int) -> str:
    return "../" * depth if depth else "./"


def ad_slot(depth: int) -> str:
    unit = str(CFG.get("aads_unit_id", "")).strip()
    if not unit:
        return ""
    if not unit.isdigit():
        raise BuildError("site.json: aads_unit_id deve conter só números")
    return (f'<div class="ad"><span class="ad-label">Publicidade</span>'
            f'<iframe data-aa="{escape(unit)}" src="https://ad.a-ads.com/{escape(unit)}?size=728x90" '
            f'style="width:728px;height:90px;border:0;padding:0;overflow:hidden;background-color:transparent;" '
            f'referrerpolicy="strict-origin-when-cross-origin" loading="lazy" '
            f'sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox allow-same-origin" '
            f'title="Publicidade"></iframe></div>')


def cta_planilha(depth: int) -> str:
    return (f'<aside class="cta"><div><strong>App + Planilha Cripto em Dia</strong>'
            f'<p>Lance suas compras e vendas e veja na hora: custo médio, isenção de R$ 35 mil, IR e DARF do mês, '
            f'imposto do exterior e o que lançar em Bens e Direitos.</p></div>'
            f'<a class="btn" href="{rel(depth)}planilha/">Conhecer o pacote</a></aside>')


def page(title, description, body, path_out: str, depth: int, canonical: str, extra_head="", kind="website", noindex=False):
    r = rel(depth)
    nav = (f'<a href="{r}">Início</a><a href="{r}calculadora-ir-cripto/">Calculadora</a>'
           f'<a href="{r}mercado/">Mercado</a><a href="{r}boletim/">Notícias</a><a href="{r}guias/">Guias</a>'
           f'<a href="{r}planilha/" class="nav-cta">Planilha</a>')
    full_title = title if title.startswith(CFG["name"]) else f"{title} | {CFG['name']}"
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
{'<meta name="robots" content="noindex">' if noindex else ''}
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="pt_BR">
<link rel="icon" type="image/png" sizes="48x48" href="{r}assets/img/favicon-48.png">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<meta property="og:image" content="{BASE}/assets/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b1d3f">
<link rel="stylesheet" href="{r}assets/style.css">
{extra_head}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{r}"><img src="{r}assets/img/logo.png" alt="Cripto em Dia" width="144" height="52"></a>
<nav>{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">
<p><strong>Cripto em Dia</strong> — notícias de criptomoedas e imposto de renda, explicados sem juridiquês.</p>
<p class="small">Conteúdo informativo, não é consultoria tributária, contábil ou de investimentos. Regras podem mudar: confira sempre a fonte oficial e, em caso de dúvida, fale com um contador.</p>
<p class="small"><a href="{r}sobre/">Sobre</a> · <a href="{r}aviso-legal/">Aviso legal</a> · <a href="{r}privacidade/">Privacidade</a> · <a href="{r}boletim/feed.xml">RSS</a></p>
</div></footer>
<script src="{r}assets/app.js" defer></script>
</body>
</html>
"""
    dest = OUT / path_out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")
    urls = []

    # ---------------- boletins
    posts = []
    for p in sorted((ROOT / "conteudo" / "boletim").glob("*.md"), reverse=True):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9\-]*)\.md$", p.name)
        if not m:
            raise BuildError(f"conteudo/boletim/{p.name}: nome fora do padrão AAAA-MM-DD-slug.md (só letras minúsculas, números e hífens)")
        meta, html = parse(p)
        d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        if meta.get("edicao", "") not in ("", "Manhã", "Noite"):
            raise BuildError(f"{p.name}: edicao deve ser Manhã ou Noite")
        slug = f"{m.group(1)}-{m.group(2)}"
        posts.append({"d": d, "slug": slug, "title": meta.get("title", slug), "ed": meta.get("edicao", ""),
                      "description": meta.get("description", ""), "html": html})
    _rank = {"": 0, "Manhã": 1, "Noite": 2}
    posts.sort(key=lambda p: (p["d"], _rank.get(p["ed"], 0)), reverse=True)
    for i, post in enumerate(posts):
        canon = f"{BASE}/boletim/{post['slug']}/"
        ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": post["title"],
              "datePublished": post["d"].isoformat(), "inLanguage": "pt-BR",
              "publisher": {"@type": "Organization", "name": CFG["name"]}}
        nav = ""
        if i + 1 < len(posts):
            nav += f'<a href="../{posts[i+1]["slug"]}/">← Edição anterior</a>'
        if i > 0:
            nav += f'<a href="../{posts[i-1]["slug"]}/">Próxima edição →</a>'
        ed = f' · edição da {post["ed"].lower()}' if post["ed"] else ""
        body = (f'<article class="prose"><p class="kicker">Notícias · {data_br(post["d"])}{ed}</p>'
                f'<h1>{escape(post["title"])}</h1>{post["html"]}</article>'
                f'<div class="post-nav">{nav}</div>{cta_planilha(2)}{ad_slot(2)}')
        page(post["title"], post["description"], body, f"boletim/{post['slug']}/index.html", 2, canon,
             ld_json(ld), "article")
        urls.append((canon, post["d"].isoformat()))
    items = "".join(
        f'<li><a href="{p["slug"]}/"><span class="date">{p["d"].strftime("%d/%m/%Y")}{(" · " + p["ed"]) if p["ed"] else ""}</span>'
        f'<strong>{escape(p["title"])}</strong><span>{escape(p["description"])}</span></a></li>' for p in posts)
    page("Notícias de criptomoedas", "Notícias de Bitcoin, Ethereum e criptomoedas em geral, duas vezes por dia, com o que muda no seu imposto de renda.",
         f'<section class="prose"><h1>Notícias de criptomoedas</h1><p>Duas edições por dia, de manhã e à noite: o mercado em um minuto, as principais notícias de Bitcoin, Ethereum e outras criptomoedas, e o que muda para quem declara cripto. Para preços ao vivo, veja a página <a href="../mercado/">Mercado</a>.</p></section><ul class="list">{items}</ul>',
         "boletim/index.html", 1, f"{BASE}/boletim/")
    urls.append((f"{BASE}/boletim/", posts[0]["d"].isoformat() if posts else date.today().isoformat()))
    rss_items = "".join(
        f"<item><title>{escape(p['title'])}</title><link>{BASE}/boletim/{p['slug']}/</link>"
        f"<guid>{BASE}/boletim/{p['slug']}/</guid><pubDate>{p['d'].strftime('%a, %d %b %Y') + (' 19:00:00 -0300' if p['ed'] == 'Noite' else ' 09:00:00 -0300')}</pubDate>"
        f"<description>{escape(p['description'])}</description></item>" for p in posts[:30])
    (OUT / "boletim" / "feed.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Cripto em Dia — Notícias</title>'
        f"<link>{BASE}/boletim/</link><description>Notícias de criptomoedas duas vezes por dia, com o que muda no seu imposto de renda</description>"
        f"<language>pt-br</language>{rss_items}</channel></rss>", encoding="utf-8")

    # ---------------- páginas fixas
    guias = []
    for p in sorted((ROOT / "conteudo" / "paginas").glob("*.md")):
        meta, html = parse(p)
        slug = meta.get("slug", "")
        if not SLUG_RE.match(slug):
            raise BuildError(f"{p.name}: slug inválido '{slug}'")
        depth = slug.count("/") + 1
        updated = meta.get("updated", date.today().isoformat())
        is_guide = slug.startswith("guias/")
        top = ""
        if is_guide:
            guias.append((int(meta.get("order", "99")), slug, meta["title"], meta.get("description", "")))
            top = f'<p class="kicker">Guia · atualizado em {data_br(date.fromisoformat(updated))}</p>'
        extra = cta_planilha(depth) + ad_slot(depth) if is_guide else ""
        ld = ""
        if is_guide:
            ld = ld_json({
                "@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
                "dateModified": updated, "inLanguage": "pt-BR",
                "publisher": {"@type": "Organization", "name": CFG["name"]}})
        html = html.replace("{{CONTATO}}", CONTATO_HTML)
        body = f'<article class="prose">{top}<h1>{escape(meta["title"])}</h1>{html}</article>{extra}'
        page(meta["title"], meta.get("description", ""), body, f"{slug}/index.html", depth, f"{BASE}/{slug}/", ld)
        urls.append((f"{BASE}/{slug}/", updated))
    guias.sort()
    glist = "".join(f'<li><a href="{s.split("/",1)[1]}/"><strong>{escape(t)}</strong><span>{escape(d)}</span></a></li>'
                    for _, s, t, d in guias)
    page("Guias de imposto de renda de cripto", "Guias práticos sobre imposto de renda de criptomoedas no Brasil: isenção de R$ 35 mil, DeCripto, corretoras estrangeiras e declaração.",
         f'<section class="prose"><h1>Guias</h1><p>O essencial sobre imposto de cripto no Brasil, com a fonte de cada regra.</p></section><ul class="list">{glist}</ul>',
         "guias/index.html", 1, f"{BASE}/guias/")
    urls.append((f"{BASE}/guias/", date.today().isoformat()))

    # ---------------- calculadora, planilha, home (templates HTML)
    def tpl(name):
        return (ROOT / "templates" / name).read_text(encoding="utf-8")

    kiwify = CFG.get("kiwify_checkout_url", "").strip()
    if kiwify and not re.match(r"^https://([a-z0-9-]+\.)*kiwify\.(com\.br|app|com)/", kiwify):
        raise BuildError("site.json: kiwify_checkout_url precisa ser um link https da Kiwify")
    buy = (f'<a class="btn btn-big" href="{escape(kiwify)}" rel="nofollow noopener">Comprar por R$ {CFG["preco"]} (Pix ou cartão)</a>'
           if kiwify else '<span class="btn btn-big btn-off">Disponível em breve</span>')
    page("Mercado de criptomoedas hoje: preços em reais", "Preços ao vivo em reais das 20 maiores criptomoedas, variação em 24h e 7 dias, valor de mercado total, participação do Bitcoin e índice de medo e ganância.",
         tpl("mercado.html") + ad_slot(1), "mercado/index.html", 1, f"{BASE}/mercado/")
    urls.append((f"{BASE}/mercado/", date.today().isoformat()))
    page("Calculadora de IR de criptomoedas", "Calcule em segundos se suas vendas de cripto no mês são isentas, quanto de IR pagar e até quando vence o DARF.",
         tpl("calculadora.html") + cta_planilha(1) + ad_slot(1), "calculadora-ir-cripto/index.html", 1,
         f"{BASE}/calculadora-ir-cripto/")
    urls.append((f"{BASE}/calculadora-ir-cripto/", date.today().isoformat()))
    page("App e planilha de IR para criptomoedas", "App e planilha para controlar compras e vendas de cripto e calcular custo médio, isenção, IR mensal, DARF, exterior (Lei 14.754) e Bens e Direitos.",
         tpl("planilha.html").replace("{{BOTAO}}", buy).replace("{{PRECO}}", CFG["preco"]),
         "planilha/index.html", 1, f"{BASE}/planilha/")
    urls.append((f"{BASE}/planilha/", date.today().isoformat()))

    latest = "".join(
        f'<li><a href="boletim/{p["slug"]}/"><span class="date">{p["d"].strftime("%d/%m/%Y")}{(" · " + p["ed"]) if p["ed"] else ""}</span>'
        f'<strong>{escape(p["title"])}</strong></a></li>' for p in posts[:6])
    glist_home = "".join(f'<li><a href="{s}/"><strong>{escape(t)}</strong><span>{escape(d)}</span></a></li>'
                         for _, s, t, d in guias)
    home = (tpl("home.html").replace("{{BOLETINS}}", latest).replace("{{GUIAS}}", glist_home)
            .replace("{{CALC}}", tpl("calculadora.html")).replace("{{CTA}}", cta_planilha(0)).replace("{{AD}}", ad_slot(0)))
    ld_site = ld_json({
        "@context": "https://schema.org", "@type": "WebSite", "name": CFG["name"], "url": BASE + "/",
        "inLanguage": "pt-BR"})
    page("Cripto em Dia — Imposto de renda de criptomoedas sem susto",
         "Notícias de criptomoedas duas vezes por dia, preços ao vivo em reais, calculadora de IR de cripto e guias sobre isenção de R$ 35 mil, DeCripto e corretoras estrangeiras.",
         home, "index.html", 0, f"{BASE}/", ld_site)
    urls.append((f"{BASE}/", date.today().isoformat()))

    page("Página não encontrada", "Página não encontrada.",
         f'<section class="prose"><h1>Página não encontrada</h1><p>Volte para o <a href="{BASE}/">início</a>.</p></section>',
         "404.html", 0, f"{BASE}/404.html", f'<base href="{BASE}/">', noindex=True)

    sm = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    broken = []
    for f in OUT.rglob("*.html"):
        if f.name == "404.html":
            continue
        for href in re.findall(r'(?:href|src)="([^"#?]+)', f.read_text(encoding="utf-8")):
            if href.startswith(("http://", "https://", "data:", "mailto:")):
                continue
            t = (f.parent / href).resolve()
            if t.is_dir():
                t = t / "index.html"
            if not t.exists():
                broken.append(f"{f.relative_to(OUT)} -> {href}")
    if broken:
        raise BuildError("links internos quebrados:\n  " + "\n  ".join(broken))
    print(f"ok: {len(urls)} URLs, {len(posts)} boletins")


if __name__ == "__main__":
    import sys
    try:
        main()
    except BuildError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
