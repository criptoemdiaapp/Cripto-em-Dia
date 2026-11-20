# Segurança — Cripto em Dia

- Site estático (GitHub Pages), sem servidor, banco de dados, login ou cookies próprios.
- CSP em todas as páginas: scripts só do próprio site; conexões só às APIs públicas de cotação (CoinGecko, Alternative.me).
- Conteúdo em Markdown é sanitizado no build: HTML cru vira texto e links com esquemas inseguros são removidos.
- Dados vindos de APIs são inseridos com `textContent`/DOM, nunca como HTML.
- A rotina automática só pode alterar conteúdo (`checar_mudancas.py`) e trata texto da web como dado, não instrução.
- Produtos pagos (app e planilha) NÃO ficam neste repositório público.
- O app pago bloqueia qualquer conexão de rede (CSP `connect-src 'none'`): os dados do cliente ficam só no navegador dele.

Encontrou um problema de segurança? Avise o responsável pelo e-mail de contato do site.
