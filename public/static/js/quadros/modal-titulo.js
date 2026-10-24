// Modal "Novo plano de voo" / "Renomear quadro" da tela Meus quadros.
import { definirCarregando } from '../ui/botao.js';
import { limparErro, mostrarErro, mostrarErros } from '../ui/formulario.js';
import { abrirModal, clonarTemplate } from '../ui/modal.js';
import { toast } from '../ui/toast.js';
import { validarTituloQuadro } from '../utils/validacoes.js';

/**
 * Abre o modal com o campo de título.
 * `salvar(titulo)` chama a API; se der certo o modal fecha, se falhar o erro aparece no campo.
 */
export function abrirModalTitulo({ tituloModal, valorInicial = '', textoBotao, textoCarregando, salvar }) {
  const sobreposicao = clonarTemplate('tpl-modal-quadro');
  const formulario = sobreposicao.querySelector('form');
  const entrada = formulario.titulo;
  const contador = formulario.querySelector('.modal-quadro__contador');
  const botaoSalvar = formulario.querySelector('[type="submit"]');
  let salvando = false;

  formulario.querySelector('#modal-quadro-titulo').textContent = tituloModal;
  botaoSalvar.textContent = textoBotao;
  entrada.value = valorInicial;

  const atualizarContador = () => {
    contador.textContent = `${entrada.value.length}/100`;
  };
  atualizarContador();

  entrada.addEventListener('input', () => {
    limparErro(entrada);
    atualizarContador();
  });

  const pedirFechar = () => {
    if (!salvando) fechar();
  };
  formulario.querySelectorAll('[data-acao="fechar"]').forEach((botao) => botao.addEventListener('click', pedirFechar));

  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    if (salvando) return;
    const erro = validarTituloQuadro(entrada.value);
    if (erro) {
      mostrarErro(entrada, erro);
      entrada.focus();
      return;
    }

    salvando = true;
    definirCarregando(botaoSalvar, true, textoCarregando);
    try {
      await salvar(entrada.value.trim());
      fechar();
    } catch (falha) {
      salvando = false;
      definirCarregando(botaoSalvar, false);
      if (!mostrarErros(formulario, falha.campos || {})) toast('erro', falha.message);
    }
  });

  const fechar = abrirModal(sobreposicao, { aoPedirFechar: pedirFechar, focoInicial: entrada });
}
