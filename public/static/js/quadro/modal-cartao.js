// Modal de detalhe do cartão: título, "Mover para", descrição, prazo, etiqueta e exclusão.
import { api } from '../api.js';
import { definirCarregando } from '../ui/botao.js';
import { confirmar } from '../ui/confirmar.js';
import { limparErro, mostrarErro, mostrarErros } from '../ui/formulario.js';
import { abrirModal, clonarTemplate } from '../ui/modal.js';
import { toast } from '../ui/toast.js';
import { encontrarCartao, removerCartao, salvarCartao } from '../utils/kanban.js';
import { textoExcluirCartao } from '../utils/mensagens.js';
import { validarTituloCartao } from '../utils/validacoes.js';

const ETIQUETAS = [
  ['', 'Sem etiqueta'],
  ['verde', 'Etiqueta verde'],
  ['amarelo', 'Etiqueta amarela'],
  ['laranja', 'Etiqueta laranja'],
  ['vermelho', 'Etiqueta vermelha'],
  ['roxo', 'Etiqueta roxa'],
  ['azul', 'Etiqueta azul'],
];

/** Grupo de botões de etiqueta (role="radio"); setas do teclado trocam a escolha. */
function criarEtiquetas(grupo, corInicial) {
  let escolhida = corInicial;
  const botoes = ETIQUETAS.map(([cor, nome]) => {
    const botao = clonarTemplate('tpl-etiqueta');
    botao.dataset.cor = cor;
    botao.setAttribute('aria-label', nome);
    botao.title = nome;
    return botao;
  });

  const escolher = (cor, focar = false) => {
    escolhida = cor;
    botoes.forEach((botao) => {
      const marcado = botao.dataset.cor === cor;
      botao.setAttribute('aria-checked', String(marcado));
      botao.tabIndex = marcado ? 0 : -1;
      if (marcado && focar) botao.focus();
    });
  };

  botoes.forEach((botao, indice) => {
    botao.addEventListener('click', () => escolher(botao.dataset.cor));
    botao.addEventListener('keydown', (evento) => {
      const passo = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[evento.key];
      if (!passo) return;
      evento.preventDefault();
      escolher(botoes[(indice + passo + botoes.length) % botoes.length].dataset.cor, true);
    });
  });

  grupo.replaceChildren(...botoes);
  escolher(corInicial);
  return () => escolhida;
}

export function abrirModalCartao(contexto, cartaoId) {
  const achado = encontrarCartao(contexto.colunas, cartaoId);
  if (!achado) return;
  const { coluna, cartao } = achado;

  const sobreposicao = clonarTemplate('tpl-modal-cartao');
  const formulario = sobreposicao.querySelector('form');
  const { titulo, coluna: selectColuna, descricao, prazo } = formulario.elements;
  const contador = formulario.querySelector('.modal-cartao__contador');
  const botaoRemoverPrazo = formulario.querySelector('[data-acao="remover-prazo"]');
  const botaoSalvar = formulario.querySelector('[type="submit"]');
  const botaoExcluir = formulario.querySelector('[data-acao="excluir"]');

  // Preenche com os dados atuais do cartão.
  titulo.value = cartao.titulo;
  formulario.querySelector('[data-campo="nome-coluna"]').textContent = coluna.titulo;
  selectColuna.append(...contexto.colunas.map((c) => new Option(c.titulo, String(c.id))));
  selectColuna.value = String(coluna.id);
  descricao.value = cartao.descricao || '';
  prazo.value = cartao.prazo || '';
  const corEscolhida = criarEtiquetas(formulario.querySelector('.etiquetas'), cartao.cor_etiqueta || '');

  const atualizarContador = () => {
    contador.textContent = `${descricao.value.length}/2000`;
  };
  const atualizarRemoverPrazo = () => {
    botaoRemoverPrazo.disabled = !prazo.value;
  };
  atualizarContador();
  atualizarRemoverPrazo();

  const lerValores = () => ({
    titulo: titulo.value,
    colunaId: selectColuna.value,
    descricao: descricao.value,
    prazo: prazo.value,
    cor: corEscolhida(),
  });
  const original = lerValores();
  const temAlteracoes = () => JSON.stringify(lerValores()) !== JSON.stringify(original);

  titulo.addEventListener('input', () => limparErro(titulo));
  descricao.addEventListener('input', atualizarContador);
  prazo.addEventListener('input', atualizarRemoverPrazo);
  botaoRemoverPrazo.addEventListener('click', () => {
    prazo.value = '';
    atualizarRemoverPrazo();
    prazo.focus();
  });

  let ocupado = false;

  const fecharDeVez = () => {
    fechar();
    // O quadro foi redesenhado: o foco vai para o cartão novo na tela (se ele ainda existir).
    document.querySelector(`[data-cartao-id="${cartaoId}"]`)?.focus();
  };

  const pedirFechar = async () => {
    if (ocupado) return;
    if (!temAlteracoes()) return fecharDeVez();
    const descartar = await confirmar({
      titulo: 'Descartar alterações?',
      texto: 'As alterações feitas neste cartão ainda não foram salvas e serão perdidas.',
      botao: 'Descartar',
    });
    if (descartar) fecharDeVez();
  };
  formulario.querySelectorAll('[data-acao="fechar"]').forEach((botao) => botao.addEventListener('click', pedirFechar));

  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    if (ocupado) return;
    const erro = validarTituloCartao(titulo.value);
    if (erro) {
      mostrarErro(titulo, erro);
      titulo.focus();
      return;
    }

    ocupado = true;
    definirCarregando(botaoSalvar, true, 'Salvando…');
    try {
      const salvo = await api.put(`/api/cartoes/${cartaoId}`, {
        titulo: titulo.value.trim(),
        descricao: descricao.value,
        prazo: prazo.value || null,
        cor_etiqueta: corEscolhida() || null,
        coluna_id: Number(selectColuna.value),
      });
      contexto.colunas = salvarCartao(contexto.colunas, salvo);
      contexto.renderizar();
      fecharDeVez();
      toast('sucesso', 'Cartão salvo');
    } catch (falha) {
      ocupado = false;
      definirCarregando(botaoSalvar, false);
      if (!mostrarErros(formulario, falha.campos || {})) toast('erro', falha.message);
    }
  });

  botaoExcluir.addEventListener('click', async () => {
    if (ocupado) return;
    const excluiu = await confirmar({
      texto: textoExcluirCartao(titulo.value.trim() || cartao.titulo),
      acao: () => api.delete(`/api/cartoes/${cartaoId}`),
    });
    if (!excluiu) return;
    contexto.colunas = removerCartao(contexto.colunas, cartaoId);
    contexto.renderizar();
    fechar();
    toast('sucesso', 'Cartão excluído');
  });

  const fechar = abrirModal(sobreposicao, { aoPedirFechar: pedirFechar, focoInicial: titulo });
}
