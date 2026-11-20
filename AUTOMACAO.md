# Rotina automática: Notícias (2 edições por dia)

Horários: 8h31 (edição da **Manhã**) e 18h31 (edição da **Noite**), fuso America/Sao_Paulo. Descubra a edição pela hora atual em São Paulo: antes das 14h = Manhã; depois = Noite.

1. **Pesquise** (WebSearch, modo "extended" para notícias de hoje) o que aconteceu desde a edição anterior:
   - mercado: Bitcoin, Ethereum e as principais altcoins (preço em US$ e em R$, variação), ETFs, índice de medo e ganância;
   - notícias relevantes de criptomoedas em geral: regulação (Brasil e exterior), grandes empresas e corretoras, hacks e golpes, lançamentos, stablecoins, adoção;
   - Brasil: Receita Federal, DeCripto, Banco Central, CVM, projetos de lei, corretoras brasileiras.
   Prefira fontes oficiais e veículos reconhecidos. Confirme números em pelo menos duas fontes quando possível.
2. **Escreva UMA edição** em `conteudo/boletim/AAAA-MM-DD-manha-slug.md` ou `AAAA-MM-DD-noite-slug.md` (não crie se já existir uma da mesma edição hoje):
   - cabeçalho `---` com `title:` (até 70 caracteres, descritivo, sem sensacionalismo), `description:` (até 160) e `edicao: Manhã` ou `edicao: Noite`;
   - estrutura: **Mercado em um minuto** (1 parágrafo com números e link `../../mercado/`); **O que movimentou** (3 a 5 tópicos em lista, cada um com 1–3 frases); **E o seu imposto?** (1 parágrafo ligando o tema a uma regra de IR e linkando o guia relevante em `../../guias/<slug>/`);
   - 250–450 palavras, português do Brasil, texto próprio (paráfrase; no máximo uma citação curta, menos de 15 palavras, por fonte);
   - termine com "Fontes:" (links das fontes usadas) e "*Boletim informativo, não é consultoria tributária nem recomendação de investimento.*";
   - nunca recomende compra/venda, nunca faça previsão de preço, não invente fatos nem números. Se uma fonte faz previsão, não a reproduza como se fosse fato.
3. Se uma notícia mudar uma regra de um guia em `conteudo/paginas/`, atualize o guia e o `updated:`. Se mudar um parâmetro do App/Planilha vendidos (isenção de R$ 35 mil, alíquotas, DARF 4600, limite da DeCripto, regra do exterior), registre em `PENDENCIAS.md` e destaque no resumo final.
4. Rode `python build.py` (deve terminar com "ok"), faça commit "Notícias AAAA-MM-DD manhã|noite" e `git -c push.negotiate=true push origin main`.
