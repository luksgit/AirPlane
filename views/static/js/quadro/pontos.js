// Pontinhos do celular: mostram qual coluna está visível ("Coluna 2 de 3").

export function atualizarPontos(container, pontos) {
  const colunas = container.querySelectorAll('.coluna');
  if (colunas.length === 0) {
    pontos.replaceChildren();
    return;
  }
  const passo = colunas[0].offsetWidth + 12; // largura da coluna + espaço entre colunas
  const ativo = passo > 12 ? Math.min(colunas.length - 1, Math.round(container.scrollLeft / passo)) : 0;

  pontos.replaceChildren(...[...colunas].map((_, indice) => {
    const ponto = document.createElement('span');
    ponto.className = indice === ativo ? 'quadro-pontos__ponto quadro-pontos__ponto--ativo' : 'quadro-pontos__ponto';
    ponto.setAttribute('aria-hidden', 'true');
    return ponto;
  }));
  pontos.setAttribute('aria-label', `Coluna ${ativo + 1} de ${colunas.length}`);
}

export function ligarPontos(container, pontos) {
  container.addEventListener('scroll', () => atualizarPontos(container, pontos), { passive: true });
}
