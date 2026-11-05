/* Envio único (DEV-07): evita mandar o mesmo formulário duas vezes enquanto o
 * primeiro envio ainda espera a resposta (clique duplo, Enter repetido, clique
 * de novo com o servidor lento).
 *
 * Só age em <form data-envio-unico>. O primeiro envio segue normalmente; os
 * seguintes, até a próxima página chegar, são cancelados. O botão NÃO recebe o
 * atributo disabled: o navegador deixaria de enviar o name/value do botão
 * clicado (em P07, acao=previa ou acao=registrar).
 *
 * Sem JavaScript, o formulário funciona como antes. As garantias continuam no
 * backend (transação, bloqueio da linha e restrições do banco); este arquivo
 * só evita a segunda requisição e a mensagem de erro que ela mostraria.
 *
 * Um envio com erro de validação volta como uma página nova, então o
 * formulário corrigido pode ser enviado de novo. Ao voltar para a página pelo
 * histórico do navegador (cache de voltar/avançar), a trava é liberada.
 */

(function () {
  "use strict";

  function liberar(formulario) {
    delete formulario.dataset.enviando;
    formulario.removeAttribute("aria-busy");
  }

  document.addEventListener("submit", function (evento) {
    var formulario = evento.target;
    if (!(formulario instanceof HTMLFormElement) || !formulario.hasAttribute("data-envio-unico")) {
      return;
    }
    if (evento.defaultPrevented) {
      return;
    }
    if (formulario.dataset.enviando) {
      evento.preventDefault();
      return;
    }
    formulario.dataset.enviando = "1";
    formulario.setAttribute("aria-busy", "true");
  });

  window.addEventListener("pageshow", function (evento) {
    if (evento.persisted) {
      document.querySelectorAll("form[data-enviando]").forEach(liberar);
    }
  });
})();
