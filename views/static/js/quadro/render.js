// Desenha as colunas e os cartões do Kanban a partir do estado (contexto.colunas).
// Sempre que o estado muda, tudo é redesenhado: é simples e evita tela dessincronizada.
import { ligarMenu } from '../ui/menu.js';
import { clonarTemplate } from '../ui/modal.js';
import { statusDoPrazo } from '../utils/prazo.js';
import { plural } from '../utils/texto.js';
import { criarFimDasColunas, excluirColuna, ligarAdicionarCartao, renomearColuna } from './colunas.js';
import { abrirModalCartao } from './modal-cartao.js';

function criarCartao(contexto, cartao) {
  const elemento = clonarTemplate('tpl-cartao');
  const prazo = statusDoPrazo(cartao.prazo);
  const temDescricao = Boolean(cartao.descricao && cartao.descricao.trim());

  elemento.dataset.cartaoId = cartao.id;
  elemento.draggable = !contexto.ehCelular();
  elemento.querySelector('.cartao__titulo').textContent = cartao.titulo;

  if (cartao.cor_etiqueta) {
    const etiqueta = elemento.querySelector('.cartao__etiqueta');
    etiqueta.dataset.cor = cartao.cor_etiqueta;
    etiqueta.hidden = false;
  }
  if (prazo) {
    const selo = elemento.querySelector('.prazo');
    selo.dataset.status = prazo.status;
    selo.querySelector('.prazo__texto').textContent = prazo.texto;
    selo.hidden = false;
  }
  elemento.querySelector('.cartao__tem-descricao').hidden = !temDescricao;
  elemento.querySelector('.cartao__indicadores').hidden = !prazo && !temDescricao;

  // Leitor de tela ouve tudo que o cartão mostra (a cor nunca é a única informação).
  const partes = [cartao.titulo];
  if (cartao.cor_etiqueta) partes.push(`etiqueta ${cartao.cor_etiqueta}`);
  if (prazo) partes.push(prazo.descricao);
  if (temDescricao) partes.push('tem descrição');
  elemento.setAttribute('aria-label', `${partes.join(', ')}. Enter para abrir`);

  elemento.addEventListener('click', () => abrirModalCartao(contexto, cartao.id));
  elemento.addEventListener('keydown', (evento) => {
    if (evento.key === 'Enter' || evento.key === ' ') {
      evento.preventDefault();
      abrirModalCartao(contexto, cartao.id);
    }
  });
  return elemento;
}

function criarColuna(contexto, coluna) {
  const secao = clonarTemplate('tpl-coluna');
  const quantidade = plural(coluna.cartoes.length, 'cartão', 'cartões');
  secao.dataset.colunaId = coluna.id;
  secao.setAttribute('aria-label', `Coluna ${coluna.titulo}, ${quantidade}`);

  const botaoTitulo = secao.querySelector('.coluna__titulo-botao');
  botaoTitulo.textContent = coluna.titulo;
  botaoTitulo.addEventListener('click', () => renomearColuna(contexto, coluna, botaoTitulo));

  const contagem = secao.querySelector('.coluna__contagem');
  contagem.textContent = coluna.cartoes.length;
  contagem.setAttribute('aria-label', quantidade);

  const botaoMenu = secao.querySelector('.botao-menu');
  botaoMenu.setAttribute('aria-label', `Opções da coluna ${coluna.titulo}`);
  ligarMenu(botaoMenu, secao.querySelector('.menu'));
  secao.querySelector('[data-acao="renomear"]').addEventListener('click', () => renomearColuna(contexto, coluna, botaoTitulo));
  secao.querySelector('[data-acao="excluir"]').addEventListener('click', () => excluirColuna(contexto, coluna));

  const lista = secao.querySelector('.coluna__cartoes');
  if (coluna.cartoes.length > 0) {
    lista.replaceChildren(...coluna.cartoes.map((cartao) => criarCartao(contexto, cartao)));
  }

  ligarAdicionarCartao(contexto, coluna, secao);
  return secao;
}

/** Redesenha a fila de colunas e, se pedido, foca um elemento (contexto.ui.focarDepois). */
export function renderizarColunas(contexto, container) {
  container.replaceChildren(
    ...contexto.colunas.map((coluna) => criarColuna(contexto, coluna)),
    criarFimDasColunas(contexto),
  );

  if (contexto.ui.focarDepois) {
    const alvo = container.querySelector(contexto.ui.focarDepois);
    contexto.ui.focarDepois = null;
    alvo?.focus();
    alvo?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }
}
