// Tela do quadro (Kanban): carrega o quadro e liga as peças da pasta quadro/.
import { api } from './api.js';
import { iniciarCabecalho } from './header.js';
import { ligarArrastar } from './quadro/arrastar.js';
import { abrirNovaColuna } from './quadro/colunas.js';
import { atualizarPontos, ligarPontos } from './quadro/pontos.js';
import { renderizarColunas } from './quadro/render.js';
import { ligarTituloDoQuadro, mostrarTituloDoQuadro } from './quadro/titulo.js';
import { mostrarEstado } from './ui/estados.js';

const tela = document.getElementById('tela-quadro');
const cabecalhoDoQuadro = document.getElementById('quadro-titulo');
const container = document.getElementById('quadro-colunas');
const pontos = document.getElementById('quadro-pontos');
const estados = {
  carregando: document.getElementById('quadro-carregando'),
  erro: document.getElementById('quadro-erro'),
  semColunas: document.getElementById('quadro-sem-colunas'),
  colunas: container,
};
const celular = window.matchMedia('(max-width: 767px)');

/**
 * Estado da tela, compartilhado com os módulos de quadro/.
 * - colunas: [{ id, titulo, posicao, cartoes: [...] }] como veio da API.
 * - ui: o que está aberto agora (formulário de cartão, nova coluna) e o que focar após redesenhar.
 */
const contexto = {
  quadroId: Number(tela.dataset.quadroId),
  titulo: '',
  colunas: [],
  carregado: false,
  ui: { adicionandoEm: null, novaColunaAberta: false, focarDepois: null },
  ehCelular: () => celular.matches,
  renderizar,
};

function renderizar() {
  if (!contexto.carregado) return;
  const temColunas = contexto.colunas.length > 0 || contexto.ui.novaColunaAberta;
  mostrarEstado(estados, temColunas ? 'colunas' : 'semColunas');
  pontos.hidden = !temColunas;
  if (temColunas) renderizarColunas(contexto, container);
  atualizarPontos(container, pontos);
}

async function carregar() {
  mostrarEstado(estados, 'carregando');
  pontos.hidden = true;
  try {
    const quadro = await api.get(`/api/quadros/${contexto.quadroId}`);
    contexto.titulo = quadro.titulo;
    contexto.colunas = quadro.colunas;
    contexto.carregado = true;
    mostrarTituloDoQuadro(contexto, cabecalhoDoQuadro);
    renderizar();
  } catch {
    mostrarEstado(estados, 'erro');
  }
}

document.querySelectorAll('[data-acao="nova-coluna"]').forEach((botao) => {
  botao.addEventListener('click', () => {
    if (contexto.carregado) abrirNovaColuna(contexto);
  });
});
document.querySelector('[data-acao="tentar-novamente"]').addEventListener('click', carregar);
celular.addEventListener('change', renderizar); // liga/desliga o arrastar ao girar ou redimensionar

ligarTituloDoQuadro(contexto, cabecalhoDoQuadro);
ligarArrastar(contexto, container);
ligarPontos(container, pontos);
iniciarCabecalho();
carregar();
