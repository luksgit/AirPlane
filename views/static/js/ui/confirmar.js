// Modal "Tem certeza?" reutilizado em todas as exclusões e no "Descartar alterações?".
import { definirCarregando } from './botao.js';
import { abrirModal, clonarTemplate } from './modal.js';
import { toast } from './toast.js';

/**
 * Pergunta ao usuário e devolve uma Promise<boolean> (true = confirmou).
 * Se `acao` for passada, ela roda com o botão em "Excluindo…" antes de fechar;
 * se a ação falhar, o modal fecha, um toast de erro aparece e o resultado é false.
 * O foco começa no "Cancelar", para uma tecla Enter distraída não apagar nada.
 */
export function confirmar({ titulo = 'Tem certeza?', texto, botao = 'Excluir', textoCarregando = 'Excluindo…', acao } = {}) {
  return new Promise((resolver) => {
    const sobreposicao = clonarTemplate('tpl-confirmar');
    const botaoCancelar = sobreposicao.querySelector('[data-acao="cancelar"]');
    const botaoConfirmar = sobreposicao.querySelector('[data-acao="confirmar"]');
    let ocupado = false;

    sobreposicao.querySelector('#confirmar-titulo').textContent = titulo;
    sobreposicao.querySelector('#confirmar-texto').textContent = texto;
    botaoConfirmar.textContent = botao;

    const terminar = (resultado) => {
      fechar();
      resolver(resultado);
    };
    const cancelar = () => {
      if (!ocupado) terminar(false);
    };

    botaoCancelar.addEventListener('click', cancelar);
    botaoConfirmar.addEventListener('click', async () => {
      if (!acao) return terminar(true);
      ocupado = true;
      botaoCancelar.disabled = true;
      definirCarregando(botaoConfirmar, true, textoCarregando);
      try {
        await acao();
        terminar(true);
      } catch (erro) {
        terminar(false);
        toast('erro', erro.message);
      }
    });

    const fechar = abrirModal(sobreposicao, { aoPedirFechar: cancelar, focoInicial: botaoCancelar });
  });
}
