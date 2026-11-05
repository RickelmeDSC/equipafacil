/* P07 — estimativa ao vivo das diárias e do total (DEV-07).
 *
 * APENAS INFORMATIVA. O valor que vale é o do backend: a prévia do botão
 * "Calcular resumo" e, no registro, o recálculo dentro da transação. Este
 * arquivo não envia formulário, não grava nada e não decide disponibilidade.
 *
 * A página funciona sem JavaScript: sem este script, a região da estimativa
 * continua escondida e o fluxo prévia → registro é o do servidor.
 *
 * A diária de cada equipamento chega por json_script (diarias_equipamentos),
 * como texto decimal (ex.: "50.00"); nenhuma consulta nova é feita.
 */

(function () {
  "use strict";

  var dados = document.getElementById("diarias-equipamentos");
  var regiao = document.getElementById("previa-ao-vivo");
  var equipamento = document.getElementById("id_equipamento");
  var retirada = document.getElementById("id_data_retirada");
  var prevista = document.getElementById("id_data_devolucao_prevista");

  if (!dados || !regiao || !equipamento || !retirada || !prevista) {
    return;
  }

  var diarias;
  try {
    diarias = JSON.parse(dados.textContent);
  } catch (erro) {
    return;
  }

  var moeda = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

  // Diárias inclusivas: (prevista − retirada) + 1, a mesma regra do backend.
  // As datas são lidas como UTC só para subtrair dias, sem fuso do navegador.
  function quantidadeDeDiarias(inicio, fim) {
    var de = Date.parse(inicio + "T00:00:00Z");
    var ate = Date.parse(fim + "T00:00:00Z");
    if (isNaN(de) || isNaN(ate)) {
      return null;
    }
    var total = Math.round((ate - de) / 86400000) + 1;
    return total >= 1 ? total : null;
  }

  // "2026-11-05" → "05/11/2026". O campo nativo mostra a data no formato do
  // idioma do navegador (em inglês, mês/dia/ano); aqui o período aparece
  // sempre em dia/mês/ano. Só reordena o texto, sem Date e sem fuso.
  function dataBrasileira(iso) {
    var partes = iso.split("-");
    return partes[2] + "/" + partes[1] + "/" + partes[0];
  }

  function atualizar() {
    var diaria = diarias[equipamento.value];
    var total = quantidadeDeDiarias(retirada.value, prevista.value);

    if (!diaria || !total) {
      regiao.hidden = true;
      regiao.textContent = "";
      return;
    }

    // Em centavos, com inteiros: evita o arredondamento de ponto flutuante.
    var centavos = Math.round(parseFloat(diaria) * 100) * total;

    regiao.textContent =
      "Estimativa de " +
      dataBrasileira(retirada.value) +
      " a " +
      dataBrasileira(prevista.value) +
      ": " +
      total +
      (total === 1 ? " diária × " : " diárias × ") +
      moeda.format(parseFloat(diaria)) +
      " = " +
      moeda.format(centavos / 100) +
      ". Use “Calcular resumo” para o valor do servidor.";
    regiao.hidden = false;
  }

  [equipamento, retirada, prevista].forEach(function (campo) {
    campo.addEventListener("change", atualizar);
    campo.addEventListener("input", atualizar);
  });

  atualizar();
})();
