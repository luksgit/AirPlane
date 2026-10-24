// Comportamento comum dos modais: foco preso dentro do diálogo (Tab),
// Esc e clique fora pedem para fechar, e o foco volta para onde estava.

const FOCAVEIS = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

/**
 * Coloca a `sobreposicao` (fundo escuro + diálogo) na página.
 * - aoPedirFechar: chamado no Esc e no clique fora (quem abriu decide se fecha).
 * - focoInicial: elemento que recebe o foco ao abrir.
 * Devolve a função fechar().
 */
export function abrirModal(sobreposicao, { aoPedirFechar, focoInicial } = {}) {
  const focoAnterior = document.activeElement;
  const dialogo = sobreposicao.firstElementChild;

  sobreposicao.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape') {
      evento.stopPropagation();
      aoPedirFechar?.();
    } else if (evento.key === 'Tab') {
      prenderFoco(evento, dialogo);
    }
  });
  sobreposicao.addEventListener('mousedown', (evento) => {
    if (evento.target === sobreposicao) aoPedirFechar?.();
  });

  document.body.append(sobreposicao);
  (focoInicial || dialogo.querySelector(FOCAVEIS))?.focus();

  return function fechar() {
    sobreposicao.remove();
    if (focoAnterior?.isConnected) focoAnterior.focus();
  };
}

/** Tab no último elemento volta para o primeiro (e Shift+Tab no primeiro vai para o último). */
function prenderFoco(evento, dialogo) {
  const focaveis = [...dialogo.querySelectorAll(FOCAVEIS)].filter((el) => el.offsetParent !== null);
  if (focaveis.length === 0) return;
  const primeiro = focaveis[0];
  const ultimo = focaveis[focaveis.length - 1];
  if (evento.shiftKey && document.activeElement === primeiro) {
    evento.preventDefault();
    ultimo.focus();
  } else if (!evento.shiftKey && document.activeElement === ultimo) {
    evento.preventDefault();
    primeiro.focus();
  }
}

/** Clona o conteúdo de um <template> da página pelo id. */
export function clonarTemplate(id) {
  return document.getElementById(id).content.firstElementChild.cloneNode(true);
}
