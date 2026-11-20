(function () {
  "use strict";
  var brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  var LIMITE = 35000;

  /* ---------------- cotações em reais (CoinGecko, direto do navegador) */
  var tbody = document.getElementById("prices-body");
  if (tbody) {
    var coins = [
      ["bitcoin", "Bitcoin", "BTC"], ["ethereum", "Ethereum", "ETH"], ["solana", "Solana", "SOL"],
      ["ripple", "XRP", "XRP"], ["binancecoin", "BNB", "BNB"], ["tether", "Tether", "USDT"]
    ];
    var url = "https://api.coingecko.com/api/v3/simple/price?vs_currencies=brl&include_24hr_change=true&ids=" +
      coins.map(function (c) { return c[0]; }).join(",");
    var load = function () {
      fetch(url).then(function (r) { return r.json(); }).then(function (d) {
        tbody.innerHTML = coins.map(function (c) {
          var x = d[c[0]];
          if (!x) return "";
          if (typeof x.brl !== "number") return "";
          var ch = typeof x.brl_24h_change === "number" ? x.brl_24h_change : 0;
          var cls = ch >= 0 ? "up" : "down";
          return "<tr><td><strong>" + c[2] + "</strong> <span class='small'>" + c[1] + "</span></td>" +
            "<td class='num'>" + brl.format(x.brl) + "</td>" +
            "<td class='num " + cls + "'>" + (ch >= 0 ? "+" : "") + ch.toFixed(2).replace(".", ",") + "%</td></tr>";
        }).join("");
        var t = document.getElementById("prices-time");
        if (t) t.textContent = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
      }).catch(function () {
        tbody.innerHTML = "<tr><td colspan='3'>Cotações indisponíveis no momento. Tente recarregar a página.</td></tr>";
      });
    };
    load();
    setInterval(load, 120000);
  }


  /* ---------------- página Mercado */
  var mb = document.getElementById("market-body");
  if (mb) {
    var compact = new Intl.NumberFormat("pt-BR", { notation: "compact", maximumFractionDigits: 2 });
    var pct = function (v) { if (typeof v !== "number" || !isFinite(v)) return "–"; return "<span class='" + (v >= 0 ? "up" : "down") + "'>" + (v >= 0 ? "+" : "") + v.toFixed(2).replace(".", ",") + "%</span>"; };
    var price = function (v) { return v >= 1 ? brl.format(v) : "R$ " + v.toLocaleString("pt-BR", { maximumSignificantDigits: 4 }); };
    var loadMk = function () {
      fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=brl&order=market_cap_desc&per_page=20&page=1&price_change_percentage=24h,7d")
        .then(function (r) { return r.json(); }).then(function (d) {
          if (!Array.isArray(d)) throw 0;
          var frag = document.createDocumentFragment();
          d.forEach(function (c) {
            var tr = document.createElement("tr");
            var td = function (content, cls) { var x = document.createElement("td"); if (cls) x.className = cls; if (content instanceof Node) x.appendChild(content); else x.textContent = content; tr.appendChild(x); return x; };
            var pctNode = function (v) { var sp = document.createElement("span"); if (typeof v !== "number" || !isFinite(v)) { sp.textContent = "–"; return sp; } sp.className = v >= 0 ? "up" : "down"; sp.textContent = (v >= 0 ? "+" : "") + v.toFixed(2).replace(".", ",") + "%"; return sp; };
            var num = function (v) { return typeof v === "number" && isFinite(v) ? v : 0; };
            td(String(num(c.market_cap_rank) || "–"));
            var nameCell = document.createElement("span");
            if (typeof c.image === "string" && /^https:\/\/[a-z0-9.-]*coingecko\.com\//i.test(c.image)) {
              var img = document.createElement("img"); img.src = c.image; img.alt = ""; img.loading = "lazy"; img.referrerPolicy = "no-referrer"; nameCell.appendChild(img);
            }
            var strong = document.createElement("strong"); strong.textContent = String(c.name || "").slice(0, 40); nameCell.appendChild(strong);
            var sym = document.createElement("span"); sym.className = "small"; sym.textContent = " " + String(c.symbol || "").toUpperCase().slice(0, 12); nameCell.appendChild(sym);
            td(nameCell);
            td(price(num(c.current_price)), "num");
            td(pctNode(c.price_change_percentage_24h_in_currency), "num");
            td(pctNode(c.price_change_percentage_7d_in_currency), "num");
            td("R$ " + compact.format(num(c.market_cap)), "num");
            td("R$ " + compact.format(num(c.total_volume)), "num");
            frag.appendChild(tr);
          });
          mb.textContent = "";
          mb.appendChild(frag);
          document.getElementById("market-time").textContent = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
        }).catch(function () { mb.innerHTML = "<tr><td colspan='7'>Dados indisponíveis no momento. Tente recarregar em instantes.</td></tr>"; });
      fetch("https://api.coingecko.com/api/v3/global").then(function (r) { return r.json(); }).then(function (g) {
        g = g.data;
        document.getElementById("g-mcap").textContent = "R$ " + compact.format(g.total_market_cap.brl);
        var ch = g.market_cap_change_percentage_24h_usd;
        document.getElementById("g-mcap-ch").innerHTML = pct(ch) + " em 24h";
        document.getElementById("g-dom").textContent = g.market_cap_percentage.btc.toFixed(1).replace(".", ",") + "%";
        document.getElementById("g-n").textContent = g.active_cryptocurrencies.toLocaleString("pt-BR");
      }).catch(function () {});
      fetch("https://api.alternative.me/fng/?limit=1").then(function (r) { return r.json(); }).then(function (f) {
        var x = f.data[0], map = { "Extreme Fear": "Medo extremo", "Fear": "Medo", "Neutral": "Neutro", "Greed": "Ganância", "Extreme Greed": "Ganância extrema" };
        document.getElementById("g-fng").textContent = x.value + "/100";
        document.getElementById("g-fng-l").textContent = map[x.value_classification] || x.value_classification;
      }).catch(function () {});
    };
    loadMk();
    setInterval(loadMk, 120000);
  }

  /* ---------------- calculadora */
  function num(id) {
    var el = document.getElementById(id);
    if (!el) return 0;
    var v = String(el.value).replace(/\s/g, "").replace(/R\$/g, "");
    if (v.indexOf(",") > -1) v = v.replace(/\./g, "").replace(",", ".");
    else if (/^\d{1,3}(\.\d{3})+$/.test(v)) v = v.replace(/\./g, "");
    var n = parseFloat(v);
    return isNaN(n) ? 0 : n;
  }
  function irProgressivo(g) {
    var faixas = [[5e6, 0.15], [10e6, 0.175], [30e6, 0.20], [Infinity, 0.225]];
    var ir = 0, piso = 0;
    for (var i = 0; i < faixas.length && g > piso; i++) {
      var teto = faixas[i][0];
      ir += (Math.min(g, teto) - piso) * faixas[i][1];
      piso = teto;
    }
    return Math.round(ir * 100) / 100;
  }
  function vencimento(mesStr) {
    if (!mesStr) return null;
    var p = mesStr.split("-");
    var y = +p[0], m = +p[1]; // m = 1..12 (mês da venda)
    var d = new Date(y, m + 1, 0); // último dia do mês seguinte
    while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() - 1);
    return d;
  }
  var form = document.getElementById("calc");
  if (form) {
    var mes = document.getElementById("c-mes");
    if (mes && !mes.value) {
      var hoje = new Date();
      mes.value = hoje.getFullYear() + "-" + String(hoje.getMonth() + 1).padStart(2, "0");
    }
    var run = function (ev) {
      if (ev) ev.preventDefault();
      var vendido = num("c-vendido"), custo = num("c-custo"), taxas = num("c-taxas");
      var out = document.getElementById("c-out");
      if (vendido <= 0) {
        out.className = "result";
        out.innerHTML = "Informe o total vendido no mês para ver o resultado.";
        return;
      }
      var ganho = vendido - taxas - custo;
      var venc = vencimento(mes && mes.value);
      var vencTxt = venc ? venc.toLocaleDateString("pt-BR") : "último dia útil do mês seguinte";
      if (vendido <= LIMITE) {
        out.className = "result";
        out.innerHTML = "<strong class='big'>Isento de IR neste mês</strong>" +
          "Você vendeu " + brl.format(vendido) + ", dentro do limite de " + brl.format(LIMITE) + " no mês. " +
          (ganho > 0 ? "O lucro de " + brl.format(ganho) + " vai na declaração anual, em <em>Rendimentos Isentos e Não Tributáveis</em>." :
            "Não houve lucro nas vendas.") +
          "<p class='small'>Atenção: o limite vale para a soma de todas as criptos vendidas no mês, não para o lucro.</p>";
      } else if (ganho <= 0) {
        out.className = "result";
        out.innerHTML = "<strong class='big'>Sem imposto a pagar</strong>" +
          "As vendas passaram de " + brl.format(LIMITE) + ", mas o resultado foi " + brl.format(ganho) + ". Sem lucro, não há IR.";
      } else {
        var ir = irProgressivo(ganho);
        out.className = "result tax";
        out.innerHTML = "<strong class='big'>IR a pagar: " + brl.format(ir) + "</strong>" +
          "Você vendeu " + brl.format(vendido) + " (acima de " + brl.format(LIMITE) + ") com lucro de " + brl.format(ganho) + ". " +
          "Pague o DARF com código <strong>4600</strong> até <strong>" + vencTxt + "</strong>." +
          "<p class='small'>Estimativa: alíquota de 15% até R$ 5 milhões de lucro. Se cair em feriado, o vencimento antecipa. " +
          "Se houver venda com prejuízo e outra com lucro no mesmo mês, confirme com um contador como compensar.</p>";
      }
    };
    form.addEventListener("submit", run);
    form.addEventListener("input", run);

    var ext = document.getElementById("calc-ext");
    if (ext) {
      var runExt = function (ev) {
        if (ev) ev.preventDefault();
        var lucro = num("e-lucro"), prej = num("e-prej");
        var base = Math.max(0, lucro - prej);
        var o = document.getElementById("e-out");
        o.className = base > 0 ? "result tax" : "result";
        o.innerHTML = base > 0 ?
          "<strong class='big'>IR estimado: " + brl.format(base * 0.15) + "</strong>Apurado e pago na declaração anual (Lei 14.754/2023), sem a isenção de R$ 35 mil." :
          "<strong class='big'>Sem imposto</strong>Sem resultado positivo no ano em corretoras estrangeiras.";
      };
      ext.addEventListener("submit", runExt);
      ext.addEventListener("input", runExt);
    }
  }
})();
