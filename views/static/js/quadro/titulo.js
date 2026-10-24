// Título do quadro no topo do Kanban: clique para editar no lugar.
import { api } from '../api.js';
import { editarNoLugar } from '../ui/edicao-no-lugar.js';
import { toast } from '../ui/toast.js';

function escreverTitulo(botao, titulo) {
  botao.textContent = titulo;
  document.title = `${titulo} · AirPlan`;
}

export function mostrarTituloDoQuadro(contexto, cabecalho) {
  escreverTitulo(cabecalho.querySelector('.quadro-titulo__botao'), contexto.titulo);
}

export function ligarTituloDoQuadro(contexto, cabecalho) {
  // Guardamos o botão: durante a edição ele sai da página (o campo de texto ocupa o lugar).
  const botao = cabecalho.querySelector('.quadro-titulo__botao');
  botao.addEventListener('click', () => {
    editarNoLugar(botao, {
      valor: contexto.titulo,
      maxLength: 100,
      classe: 'quadro-titulo__entrada',
      rotulo: 'Título do quadro',
      aoConfirmar: async (texto) => {
        const titulo = texto.trim();
        if (!titulo) {
          toast('erro', 'O título do quadro não pode ficar vazio');
          return;
        }
        if (titulo === contexto.titulo) return;
        try {
          await api.put(`/api/quadros/${contexto.quadroId}`, { titulo });
          contexto.titulo = titulo;
          escreverTitulo(botao, titulo);
          toast('sucesso', 'Quadro renomeado');
        } catch (erro) {
          toast('erro', erro.message);
        }
      },
    });
  });
}
