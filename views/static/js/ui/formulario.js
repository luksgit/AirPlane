// Erros dos campos de formulário: borda vermelha, mensagem abaixo do campo
// (ligada por aria-describedby) e foco no primeiro campo com erro.

const SVG = 'http://www.w3.org/2000/svg';

function criarIconeAlerta() {
  const svg = document.createElementNS(SVG, 'svg');
  svg.setAttribute('class', 'icone');
  svg.setAttribute('width', '15');
  svg.setAttribute('height', '15');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('aria-hidden', 'true');
  const circulo = document.createElementNS(SVG, 'circle');
  circulo.setAttribute('cx', '12');
  circulo.setAttribute('cy', '12');
  circulo.setAttribute('r', '10');
  svg.append(circulo);
  for (const d of ['M12 8v4', 'M12 16h.01']) {
    const linha = document.createElementNS(SVG, 'path');
    linha.setAttribute('d', d);
    svg.append(linha);
  }
  return svg;
}

/**
 * Mostra (ou troca) a mensagem de erro de um campo.
 * Por padrão ela vai no fim do .campo; se o campo tiver um elemento [data-lugar-erro]
 * (ex.: a linha do contador "0/100"), ela entra no começo dele.
 */
export function mostrarErro(entrada, mensagem) {
  const campo = entrada.closest('.campo');
  const idErro = `${entrada.id}-erro`;
  let paragrafo = document.getElementById(idErro);
  if (!paragrafo) {
    paragrafo = document.createElement('p');
    paragrafo.id = idErro;
    paragrafo.className = 'campo__erro';
    paragrafo.append(criarIconeAlerta(), document.createElement('span'));
    const lugar = campo.querySelector('[data-lugar-erro]');
    if (lugar) lugar.prepend(paragrafo);
    else campo.append(paragrafo);
  }
  paragrafo.querySelector('span').textContent = mensagem;
  entrada.setAttribute('aria-invalid', 'true');
  entrada.setAttribute('aria-describedby', idErro);
}

/** Tira o erro de um campo (usado quando o usuário volta a digitar). */
export function limparErro(entrada) {
  document.getElementById(`${entrada.id}-erro`)?.remove();
  entrada.removeAttribute('aria-invalid');
  if (entrada.getAttribute('aria-describedby') === `${entrada.id}-erro`) {
    entrada.removeAttribute('aria-describedby');
  }
}

/**
 * Mostra os erros { nomeDoCampo: mensagem } de um formulário e foca o primeiro.
 * Devolve true se havia algum erro.
 */
export function mostrarErros(formulario, erros) {
  const comErro = [];
  for (const [nome, mensagem] of Object.entries(erros)) {
    const entrada = formulario.elements[nome];
    if (entrada && mensagem) {
      mostrarErro(entrada, mensagem);
      comErro.push(entrada);
    }
  }
  // O primeiro na ordem da tela, não na ordem do objeto.
  const primeiro = [...formulario.elements].find((el) => comErro.includes(el));
  primeiro?.focus();
  return comErro.length > 0;
}

/** Junta { campo: mensagem|null } deixando só os campos com erro. */
export function juntarErros(erros) {
  return Object.fromEntries(Object.entries(erros).filter(([, mensagem]) => mensagem));
}

/** Ao digitar num campo, o erro dele some. */
export function limparErrosAoDigitar(formulario, depois) {
  formulario.addEventListener('input', (evento) => {
    if (evento.target.matches('input, textarea')) limparErro(evento.target);
    depois?.(evento);
  });
}

/** Desabilita (ou habilita) os campos enquanto o formulário está sendo enviado. */
export function travarCampos(formulario, travado) {
  formulario.querySelectorAll('input:not([readonly]), textarea, select, .campo__olho').forEach((el) => {
    el.disabled = travado;
  });
}
