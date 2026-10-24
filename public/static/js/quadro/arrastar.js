// Arrastar e soltar cartões (HTML5 drag and drop). Desligado no celular: lá se usa
// o "Mover para" do modal. O movimento é otimista: a tela muda na hora e, se a API
// falhar, o cartão volta para onde estava.
import { api } from '../api.js';
import { toast } from '../ui/toast.js';
import { encontrarCartao, moverCartao } from '../utils/kanban.js';

async function soltarCartao(contexto, cartaoId, colunaId, posicao) {
  const atual = encontrarCartao(contexto.colunas, cartaoId);
  if (!atual) return;
  if (atual.coluna.id === colunaId && atual.indice === posicao) {
    contexto.renderizar(); // Soltou no mesmo lugar: nada para salvar.
    return;
  }

  const antes = contexto.colunas;
  contexto.colunas = moverCartao(antes, cartaoId, colunaId, posicao);
  contexto.renderizar();
  try {
    await api.put(`/api/cartoes/${cartaoId}/mover`, { coluna_id: colunaId, posicao });
  } catch {
    contexto.colunas = antes;
    contexto.renderizar();
    toast('erro', 'Não foi possível mover o cartão');
  }
}

/** Liga o arrastar e soltar em todas as colunas do container (eventos delegados). */
export function ligarArrastar(contexto, container) {
  let arraste = null; // { cartaoId, elemento, espaco } enquanto um cartão está sendo arrastado

  const marcarColunaAlvo = (coluna) => {
    container.querySelectorAll('.coluna--alvo').forEach((c) => {
      if (c !== coluna) c.classList.remove('coluna--alvo');
    });
    coluna?.classList.add('coluna--alvo');
  };

  const limpar = () => {
    if (!arraste) return;
    arraste.espaco.remove();
    arraste.elemento.hidden = false;
    marcarColunaAlvo(null);
    arraste = null;
  };

  container.addEventListener('dragstart', (evento) => {
    const elemento = evento.target.closest?.('.cartao');
    if (!elemento || contexto.ehCelular()) {
      evento.preventDefault();
      return;
    }
    const espaco = document.createElement('div');
    espaco.className = 'cartao-espaco';
    espaco.style.height = `${elemento.offsetHeight}px`;
    arraste = { cartaoId: Number(elemento.dataset.cartaoId), elemento, espaco };

    evento.dataTransfer.effectAllowed = 'move';
    evento.dataTransfer.setData('text/plain', elemento.dataset.cartaoId);
    elemento.classList.add('cartao--pegando');
    // Depois que o navegador "fotografou" o cartão inclinado, ele some e o espaço tracejado entra no lugar.
    setTimeout(() => {
      elemento.classList.remove('cartao--pegando');
      if (!arraste) return;
      elemento.hidden = true;
      elemento.after(espaco);
    }, 0);
  });

  container.addEventListener('dragover', (evento) => {
    const coluna = evento.target.closest('.coluna');
    if (!arraste || !coluna) return;
    evento.preventDefault();
    evento.dataTransfer.dropEffect = 'move';

    // O espaço entra antes do primeiro cartão cuja metade ainda está abaixo do mouse.
    const lista = coluna.querySelector('.coluna__cartoes');
    const visiveis = [...lista.querySelectorAll('.cartao:not([hidden])')];
    const antesDe = visiveis.find((cartao) => {
      const caixa = cartao.getBoundingClientRect();
      return evento.clientY < caixa.top + caixa.height / 2;
    });
    if (antesDe && arraste.espaco.nextElementSibling !== antesDe) lista.insertBefore(arraste.espaco, antesDe);
    if (!antesDe && lista.lastElementChild !== arraste.espaco) lista.append(arraste.espaco);
    marcarColunaAlvo(coluna);
  });

  container.addEventListener('drop', (evento) => {
    if (!arraste) return;
    evento.preventDefault();
    const lista = arraste.espaco.parentElement;
    const coluna = lista?.closest('.coluna');
    if (!coluna) return limpar();

    // Posição = quantos cartões visíveis ficaram antes do espaço tracejado.
    const posicao = [...lista.querySelectorAll('.cartao:not([hidden]), .cartao-espaco')].indexOf(arraste.espaco);
    const { cartaoId } = arraste;
    limpar();
    soltarCartao(contexto, cartaoId, Number(coluna.dataset.colunaId), posicao);
  });

  container.addEventListener('dragend', limpar);
}
