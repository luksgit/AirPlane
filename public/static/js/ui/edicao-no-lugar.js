// Edição "no lugar": troca um botão de título por um campo de texto.
// Enter ou sair do campo confirma; Esc cancela. Usado no título do quadro e das colunas.

/**
 * - valor, maxLength, classe, rotulo: configuração do campo.
 * - aoConfirmar(texto): chamado uma única vez com o texto digitado (pode ser async).
 * Ao terminar (confirmando ou cancelando), o botão original volta para o lugar.
 */
export function editarNoLugar(botao, { valor, maxLength, classe, rotulo, aoConfirmar }) {
  const entrada = document.createElement('input');
  entrada.className = classe;
  entrada.value = valor;
  entrada.maxLength = maxLength;
  entrada.setAttribute('aria-label', rotulo);
  let terminou = false;

  const restaurar = (devolverFoco) => {
    if (entrada.isConnected) entrada.replaceWith(botao);
    if (devolverFoco && botao.isConnected) botao.focus();
  };

  const confirmar = async (devolverFoco) => {
    if (terminou) return;
    terminou = true;
    entrada.disabled = true;
    await aoConfirmar(entrada.value);
    restaurar(devolverFoco);
  };

  entrada.addEventListener('keydown', (evento) => {
    if (evento.key === 'Enter') {
      evento.preventDefault();
      confirmar(true);
    } else if (evento.key === 'Escape') {
      evento.stopPropagation();
      terminou = true;
      restaurar(true);
    }
  });
  entrada.addEventListener('blur', () => confirmar(false));

  botao.replaceWith(entrada);
  entrada.focus();
  entrada.select();
}
