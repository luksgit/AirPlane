// Tela "Meus planos de voo" (Hangar): lista, cria, renomeia e exclui quadros.
import { api } from './api.js';
import { iniciarCabecalho } from './header.js';
import { abrirModalTitulo } from './quadros/modal-titulo.js';
import { confirmar } from './ui/confirmar.js';
import { mostrarEstado } from './ui/estados.js';
import { ligarMenu } from './ui/menu.js';
import { clonarTemplate } from './ui/modal.js';
import { toast, toastNaProximaPagina } from './ui/toast.js';
import { resumoDoQuadro, textoExcluirQuadro } from './utils/mensagens.js';

const lista = document.getElementById('hangar-lista');
const botaoCriarNoFim = lista.querySelector('.quadro-novo');
const estados = {
  carregando: document.getElementById('hangar-carregando'),
  lista,
  vazio: document.getElementById('hangar-vazio'),
  erro: document.getElementById('hangar-erro'),
};

let quadros = [];

function criarCard(quadro) {
  const card = clonarTemplate('tpl-quadro');
  const resumo = resumoDoQuadro(quadro.total_colunas, quadro.total_cartoes);
  const link = card.querySelector('.quadro-card__link');
  link.href = `/quadros/${quadro.id}`;
  link.setAttribute('aria-label', `${quadro.titulo}, ${resumo}`);
  card.querySelector('.quadro-card__titulo').textContent = quadro.titulo;
  card.querySelector('.quadro-card__resumo').textContent = resumo;

  const botaoMenu = card.querySelector('.botao-menu');
  botaoMenu.setAttribute('aria-label', `Opções do quadro ${quadro.titulo}`);
  ligarMenu(botaoMenu, card.querySelector('.menu'));
  card.querySelector('[data-acao="renomear"]').addEventListener('click', () => renomear(quadro));
  card.querySelector('[data-acao="excluir"]').addEventListener('click', () => excluir(quadro));
  return card;
}

function renderizar() {
  lista.replaceChildren(...quadros.map(criarCard), botaoCriarNoFim);
  mostrarEstado(estados, quadros.length > 0 ? 'lista' : 'vazio');
}

async function carregar() {
  mostrarEstado(estados, 'carregando');
  try {
    quadros = await api.get('/api/quadros');
    renderizar();
  } catch {
    mostrarEstado(estados, 'erro');
  }
}

function novoQuadro() {
  abrirModalTitulo({
    tituloModal: 'Novo plano de voo',
    textoBotao: 'Criar quadro',
    textoCarregando: 'Criando…',
    salvar: async (titulo) => {
      const quadro = await api.post('/api/quadros', { titulo });
      toastNaProximaPagina('sucesso', 'Quadro criado');
      window.location.assign(`/quadros/${quadro.id}`);
    },
  });
}

function renomear(quadro) {
  abrirModalTitulo({
    tituloModal: 'Renomear quadro',
    valorInicial: quadro.titulo,
    textoBotao: 'Salvar',
    textoCarregando: 'Salvando…',
    salvar: async (titulo) => {
      const atualizado = await api.put(`/api/quadros/${quadro.id}`, { titulo });
      quadro.titulo = atualizado.titulo;
      renderizar();
      toast('sucesso', 'Quadro renomeado');
    },
  });
}

async function excluir(quadro) {
  const excluiu = await confirmar({
    texto: textoExcluirQuadro(quadro.titulo, quadro.total_colunas, quadro.total_cartoes),
    acao: () => api.delete(`/api/quadros/${quadro.id}`),
  });
  if (!excluiu) return;
  quadros = quadros.filter((q) => q.id !== quadro.id);
  renderizar();
  toast('sucesso', 'Quadro excluído');
}

document.querySelectorAll('[data-acao="novo-quadro"]').forEach((botao) => botao.addEventListener('click', novoQuadro));
document.querySelector('[data-acao="tentar-novamente"]').addEventListener('click', carregar);

iniciarCabecalho();
carregar();
