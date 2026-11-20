# Cripto em Dia

Site estático sobre imposto de renda de criptomoedas no Brasil.

- `conteudo/paginas/` — guias e páginas fixas (Markdown com cabeçalho `---`)
- `conteudo/boletim/` — boletins diários, nome `AAAA-MM-DD-slug.md`
- `templates/` — home, calculadora e página da planilha
- `assets/` — CSS e JS (cotações CoinGecko e calculadora)
- `site.json` — URL base, preço, link do checkout Kiwify, ID do anúncio A-ADS
- `python build.py` gera o site em `docs/` (GitHub Pages: branch `main`, pasta `/docs`)

Rotina automática: ver `AUTOMACAO.md`.
