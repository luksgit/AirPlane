// Estado "carregando" dos botões que chamam a API: desabilitado, spinner e texto
// trocado ("Salvando…"). Assim não existe clique duplo.

const conteudoOriginal = new WeakMap();

export function definirCarregando(botao, carregando, textoCarregando = 'Salvando…') {
  if (carregando) {
    if (conteudoOriginal.has(botao)) return;
    conteudoOriginal.set(botao, [...botao.childNodes]);
    const spinner = document.createElement('span');
    spinner.className = 'spinner';
    spinner.setAttribute('aria-hidden', 'true');
    botao.replaceChildren(spinner, textoCarregando);
    botao.disabled = true;
    botao.setAttribute('aria-busy', 'true');
  } else {
    if (!conteudoOriginal.has(botao)) return;
    botao.replaceChildren(...conteudoOriginal.get(botao));
    conteudoOriginal.delete(botao);
    botao.disabled = false;
    botao.removeAttribute('aria-busy');
  }
}
