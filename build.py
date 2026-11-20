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
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def data_br(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def parse(path: Path):
    raw = path.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        for line in fm.strip().splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    html = markdown.markdown(body, extensions=["tables", "toc", "sane_lists"])
    return meta, html


def rel(depth: int) -> str:
    return "../" * depth if depth else "./"


def ad_slot(depth: int) -> str:
    unit = CFG.get("aads_unit_id", "").strip()
    if not unit:
        return ""
    return (f'<div class="ad"><span class="ad-label">Publicidade</span>'
            f'<iframe data-aa="{escape(unit)}" src="https://ad.a-ads.com/{escape(unit)}?size=728x90" '
            f'style="width:728px;height:90px;border:0;padding:0;overflow:hidden;background-color:transparent;" '
            f'title="Publicidade"></iframe></div>')


def cta_planilha(depth: int) -> str:
    return (f'<aside class="cta"><div><strong>Planilha Cripto em Dia</strong>'
            f'<p>Lance suas compras e vendas e ela calcula custo médio, isenção de R$ 35 mil, IR e DARF do mês, '
            f'imposto do exterior e o que lançar em Bens e Direitos.</p></div>'
            f'<a class="btn" href="{rel(depth)}planilha/">Conhecer a planilha</a></aside>')


def page(title, description, body, path_out: str, depth: int, canonical: str, extra_head="", kind="website"):
    r = rel(depth)
    nav = (f'<a href="{r}">Início</a><a href="{r}calculadora-ir-cripto/">Calculadora</a>'
           f'<a href="{r}guias/">Guias</a><a href="{r}boletim/">Boletim</a>'
           f'<a href="{r}planilha/" class="nav-cta">Planilha</a>')
    full_title = title if title.startswith(CFG["name"]) else f"{title} | {CFG['name']}"
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="pt_BR">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%230f3d2e'/><text x='16' y='22' font-size='16' text-anchor='middle' fill='%23f4c95d' font-family='Arial' font-weight='700'>R$</text></svg>">
<link rel="stylesheet" href="{r}assets/style.css">
{extra_head}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{r}"><span class="logo-mark">R$</span> Cripto em Dia</a>
<nav>{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">
<p><strong>Cripto em Dia</strong> — imposto de renda de criptomoedas explicado sem juridiquês.</p>
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
        meta, html = parse(p)
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$", p.name)
        d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        slug = f"{m.group(1)}-{m.group(2)}"
        posts.append({"d": d, "slug": slug, "title": meta.get("title", slug),
                      "description": meta.get("description", ""), "html": html})
    for i, post in enumerate(posts):
        canon = f"{BASE}/boletim/{post['slug']}/"
        ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": post["title"],
              "datePublished": post["d"].isoformat(), "inLanguage": "pt-BR",
              "publisher": {"@type": "Organization", "name": CFG["name"]}}
        nav = ""
        if i + 1 < len(posts):
            nav += f'<a href="../{posts[i+1]["slug"]}/">← Boletim anterior</a>'
        if i > 0:
            nav += f'<a href="../{posts[i-1]["slug"]}/">Próximo boletim →</a>'
        body = (f'<article class="prose"><p class="kicker">Boletim · {data_br(post["d"])}</p>'
                f'<h1>{escape(post["title"])}</h1>{post["html"]}</article>'
                f'<div class="post-nav">{nav}</div>{cta_planilha(2)}{ad_slot(2)}')
        page(post["title"], post["description"], body, f"boletim/{post['slug']}/index.html", 2, canon,
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>', "article")
        urls.append((canon, post["d"].isoformat()))
    items = "".join(
        f'<li><a href="{p["slug"]}/"><span class="date">{p["d"].strftime("%d/%m/%Y")}</span>'
        f'<strong>{escape(p["title"])}</strong><span>{escape(p["description"])}</span></a></li>' for p in posts)
    page("Boletim diário", "Boletim diário do Cripto em Dia: o que mudou nas regras e no mercado de criptomoedas e o que isso muda no seu imposto.",
         f'<section class="prose"><h1>Boletim diário</h1><p>Um resumo curto, todos os dias, do que mudou nas regras e no mercado e do que isso muda para quem declara cripto.</p></section><ul class="list">{items}</ul>',
         "boletim/index.html", 1, f"{BASE}/boletim/")
    urls.append((f"{BASE}/boletim/", posts[0]["d"].isoformat() if posts else date.today().isoformat()))
    rss_items = "".join(
        f"<item><title>{escape(p['title'])}</title><link>{BASE}/boletim/{p['slug']}/</link>"
        f"<guid>{BASE}/boletim/{p['slug']}/</guid><pubDate>{p['d'].strftime('%a, %d %b %Y 09:00:00 -0300')}</pubDate>"
        f"<description>{escape(p['description'])}</description></item>" for p in posts[:30])
    (OUT / "boletim" / "feed.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Cripto em Dia — Boletim</title>'
        f"<link>{BASE}/boletim/</link><description>Boletim diário sobre imposto e regras de cripto no Brasil</description>"
        f"<language>pt-br</language>{rss_items}</channel></rss>", encoding="utf-8")

    # ---------------- páginas fixas
    guias = []
    for p in sorted((ROOT / "conteudo" / "paginas").glob("*.md")):
        meta, html = parse(p)
        slug = meta["slug"]
        depth = slug.count("/") + 1
        updated = meta.get("updated", date.today().isoformat())
        is_guide = slug.startswith("guias/")
        top = ""
        if is_guide:
            guias.append((meta.get("order", "9"), slug, meta["title"], meta.get("description", "")))
            top = f'<p class="kicker">Guia · atualizado em {data_br(date.fromisoformat(updated))}</p>'
        extra = cta_planilha(depth) + ad_slot(depth) if is_guide else ""
        ld = ""
        if is_guide:
            ld = ('<script type="application/ld+json">' + json.dumps({
                "@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
                "dateModified": updated, "inLanguage": "pt-BR",
                "publisher": {"@type": "Organization", "name": CFG["name"]}}, ensure_ascii=False) + "</script>")
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
    buy = (f'<a class="btn btn-big" href="{escape(kiwify)}" rel="nofollow">Comprar por R$ {CFG["preco"]} (Pix ou cartão)</a>'
           if kiwify else '<span class="btn btn-big btn-off">Disponível em breve</span>')
    page("Calculadora de IR de criptomoedas", "Calcule em segundos se suas vendas de cripto no mês são isentas, quanto de IR pagar e até quando vence o DARF.",
         tpl("calculadora.html") + cta_planilha(1) + ad_slot(1), "calculadora-ir-cripto/index.html", 1,
         f"{BASE}/calculadora-ir-cripto/")
    urls.append((f"{BASE}/calculadora-ir-cripto/", date.today().isoformat()))
    page("Planilha de IR para criptomoedas", "Planilha para controlar compras e vendas de cripto e calcular custo médio, isenção, IR mensal, DARF, exterior (Lei 14.754) e Bens e Direitos.",
         tpl("planilha.html").replace("{{BOTAO}}", buy).replace("{{PRECO}}", CFG["preco"]),
         "planilha/index.html", 1, f"{BASE}/planilha/")
    urls.append((f"{BASE}/planilha/", date.today().isoformat()))

    latest = "".join(
        f'<li><a href="boletim/{p["slug"]}/"><span class="date">{p["d"].strftime("%d/%m/%Y")}</span>'
        f'<strong>{escape(p["title"])}</strong></a></li>' for p in posts[:5])
    glist_home = "".join(f'<li><a href="{s}/"><strong>{escape(t)}</strong><span>{escape(d)}</span></a></li>'
                         for _, s, t, d in guias)
    home = (tpl("home.html").replace("{{BOLETINS}}", latest).replace("{{GUIAS}}", glist_home)
            .replace("{{CALC}}", tpl("calculadora.html")).replace("{{CTA}}", cta_planilha(0)).replace("{{AD}}", ad_slot(0)))
    ld_site = ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "WebSite", "name": CFG["name"], "url": BASE + "/",
        "inLanguage": "pt-BR"}, ensure_ascii=False) + "</script>")
    page("Cripto em Dia — Imposto de renda de criptomoedas sem susto",
         "Calculadora de IR de cripto, cotações em reais, guias sobre isenção de R$ 35 mil, DeCripto e corretoras estrangeiras, e boletim diário.",
         home, "index.html", 0, f"{BASE}/", ld_site)
    urls.append((f"{BASE}/", date.today().isoformat()))

    page("Página não encontrada", "Página não encontrada.",
         f'<section class="prose"><h1>Página não encontrada</h1><p>Volte para o <a href="{BASE}/">início</a>.</p></section>',
         "404.html", 0, f"{BASE}/404.html", f'<base href="{BASE}/">')

    sm = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print(f"ok: {len(urls)} URLs, {len(posts)} boletins")


if __name__ == "__main__":
    main()
