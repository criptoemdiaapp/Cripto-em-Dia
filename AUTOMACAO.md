# Rotina automática diária

1. Pesquise (WebSearch) notícias das últimas 24–48 h sobre: tributação de cripto no Brasil, Receita Federal e criptoativos, DeCripto, Banco Central e regulação de criptoativos, projetos de lei sobre cripto, e o movimento do mercado (BTC/ETH em reais). Prefira fontes oficiais (gov.br, Receita, BCB, Planalto, Câmara, Senado) e veículos reconhecidos.
2. Escreva UM boletim em `conteudo/boletim/AAAA-MM-DD-slug.md` (data de hoje, fuso America/Sao_Paulo):
   - cabeçalho `---` com `title:` (até 70 caracteres) e `description:` (até 160);
   - 150–350 palavras, português do Brasil, texto próprio (paráfrase; no máximo uma citação curta, com menos de 15 palavras, por fonte);
   - foco: o que mudou e o que isso muda para quem declara cripto; ligue para o guia relevante em `../../guias/<slug>/`;
   - termine com uma linha "Fontes:" com links e com "*Boletim informativo, não é consultoria tributária.*";
   - não faça recomendação de compra/venda nem previsão de preço; não invente fatos; se não houver novidade relevante, faça um boletim prático (dúvida comum, prazo que se aproxima) com base nos guias.
3. Se uma notícia mudar uma regra descrita num guia em `conteudo/paginas/`, atualize o guia e o campo `updated:`. Se mudar algum parâmetro da planilha, registre em `PENDENCIAS.md`.
4. Rode `python build.py`, confira que terminou com "ok", faça commit ("Boletim AAAA-MM-DD") e push para `main`.
