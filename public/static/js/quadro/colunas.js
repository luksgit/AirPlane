// Ações das colunas do Kanban: renomear, excluir, adicionar cartão e criar coluna.
// Todas recebem o `contexto` do quadro (estado + renderizar), criado em quadro.js.
import { api } from '../api.js';
import { definirCarregando } from '../ui/botao.js';
import { confirmar } from '../ui/confirmar.js';
import { editarNoLugar } from '../ui/edicao-no-lugar.js';
import { clonarTemplate } from '../ui/modal.js';
import { toast } from '../ui/toast.js';
import { adicionarCartao, removerColuna } from '../utils/kanban.js';
import { textoExcluirColuna } from '../utils/mensagens.js';
import { validarTituloColuna } from '../utils/validacoes.js';

const seletorColuna = (colunaId) => `[data-coluna-id="${colunaId}"]`;

export function renomearColuna(contexto, coluna, botaoTitulo) {
  editarNoLugar(botaoTitulo, {
    valor: coluna.titulo,
    maxLength: 50,
    classe: 'coluna__titulo-entrada',
    rotulo: 'Título da coluna',
    aoConfirmar: async (texto) => {
      const titulo = texto.trim();
      if (validarTituloColuna(titulo)) {
        toast('erro', validarTituloColuna(titulo));
        return;
      }
      if (titulo === coluna.titulo) return;
      try {
        await api.put(`/api/colunas/${coluna.id}`, { titulo });
        contexto.colunas = contexto.colunas.map((c) => (c.id === coluna.id ? { ...c, titulo } : c));
        contexto.ui.focarDepois = `${seletorColuna(coluna.id)} .coluna__titulo-botao`;
        contexto.renderizar();
        toast('sucesso', 'Coluna renomeada');
      } catch (erro) {
        toast('erro', erro.message);
      }
    },
  });
}

export async function excluirColuna(contexto, coluna) {
  const excluiu = await confirmar({
    texto: textoExcluirColuna(coluna.titulo, coluna.cartoes.length),
    acao: () => api.delete(`/api/colunas/${coluna.id}`),
  });
  if (!excluiu) return;
  contexto.colunas = removerColuna(contexto.colunas, coluna.id);
  contexto.renderizar();
  toast('sucesso', 'Coluna excluída');
}

/** Liga o "Adicionar cartão" do rodapé da coluna (botão ↔ formulário). */
export function ligarAdicionarCartao(contexto, coluna, secao) {
  const botaoAbrir = secao.querySelector('[data-acao="abrir-adicionar"]');
  const formulario = secao.querySelector('form[data-acao="adicionar"]');
  const texto = formulario.titulo;
  const botaoAdicionar = formulario.querySelector('[type="submit"]');
  const aberto = contexto.ui.adicionandoEm === coluna.id;

  botaoAbrir.hidden = aberto;
  formulario.hidden = !aberto;

  botaoAbrir.addEventListener('click', () => {
    contexto.ui.adicionandoEm = coluna.id;
    contexto.ui.focarDepois = `${seletorColuna(coluna.id)} textarea`;
    contexto.renderizar();
  });

  const fechar = () => {
    contexto.ui.adicionandoEm = null;
    contexto.ui.focarDepois = `${seletorColuna(coluna.id)} [data-acao="abrir-adicionar"]`;
    contexto.renderizar();
  };
  formulario.querySelector('[data-acao="cancelar-adicionar"]').addEventListener('click', fechar);

  texto.addEventListener('keydown', (evento) => {
    if (evento.key === 'Enter' && !evento.shiftKey) {
      evento.preventDefault();
      formulario.requestSubmit();
    } else if (evento.key === 'Escape') {
      fechar();
    }
  });

  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const titulo = texto.value.trim();
    if (!titulo || botaoAdicionar.disabled) return;

    definirCarregando(botaoAdicionar, true, 'Adicionando…');
    texto.disabled = true;
    try {
      const cartao = await api.post(`/api/colunas/${coluna.id}/cartoes`, { titulo });
      contexto.colunas = adicionarCartao(contexto.colunas, coluna.id, cartao);
      // O formulário continua aberto (e vazio) para adicionar outro cartão em seguida.
      contexto.ui.focarDepois = `${seletorColuna(coluna.id)} textarea`;
      contexto.renderizar();
    } catch (erro) {
      definirCarregando(botaoAdicionar, false);
      texto.disabled = false;
      texto.focus();
      toast('erro', erro.message);
    }
  });
}

export function abrirNovaColuna(contexto) {
  contexto.ui.novaColunaAberta = true;
  contexto.ui.focarDepois = '.nova-coluna-form input';
  contexto.renderizar();
}

function fecharNovaColuna(contexto) {
  contexto.ui.novaColunaAberta = false;
  contexto.ui.focarDepois = '.nova-coluna';
  contexto.renderizar();
}

/** Último item da fila de colunas: o botão tracejado ou o formulário de nova coluna. */
export function criarFimDasColunas(contexto) {
  if (!contexto.ui.novaColunaAberta) {
    const botao = clonarTemplate('tpl-nova-coluna');
    botao.addEventListener('click', () => abrirNovaColuna(contexto));
    return botao;
  }

  const formulario = clonarTemplate('tpl-nova-coluna-form');
  const entrada = formulario.titulo;
  const botaoCriar = formulario.querySelector('[type="submit"]');

  formulario.querySelector('[data-acao="cancelar"]').addEventListener('click', () => fecharNovaColuna(contexto));
  entrada.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape') fecharNovaColuna(contexto);
  });

  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const titulo = entrada.value.trim();
    if (!titulo || botaoCriar.disabled) return;

    definirCarregando(botaoCriar, true, 'Criando…');
    entrada.disabled = true;
    try {
      const coluna = await api.post(`/api/quadros/${contexto.quadroId}/colunas`, { titulo });
      contexto.colunas = [...contexto.colunas, { ...coluna, cartoes: [] }];
      contexto.ui.novaColunaAberta = false;
      contexto.ui.focarDepois = `${seletorColuna(coluna.id)} .coluna__titulo-botao`;
      contexto.renderizar();
      toast('sucesso', 'Coluna criada');
    } catch (erro) {
      definirCarregando(botaoCriar, false);
      entrada.disabled = false;
      entrada.focus();
      toast('erro', erro.message);
    }
  });
  return formulario;
}
