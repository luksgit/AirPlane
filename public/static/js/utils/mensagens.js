// Textos que mudam com a quantidade (singular/plural), iguais aos do protótipo.
import { plural } from './texto.js';

/** "3 colunas · 1 cartão" (subtítulo do card do quadro). */
export function resumoDoQuadro(totalColunas, totalCartoes) {
  return `${plural(totalColunas, 'coluna', 'colunas')} · ${plural(totalCartoes, 'cartão', 'cartões')}`;
}

export function textoExcluirQuadro(titulo, totalColunas, totalCartoes) {
  const aviso = 'Essa ação não pode ser desfeita.';
  if (totalColunas === 0) return `Excluir o quadro '${titulo}'? ${aviso}`;
  const colunas = totalColunas === 1 ? 'A única coluna' : `Todas as ${totalColunas} colunas`;
  const cartoes = plural(totalCartoes, 'cartão', 'cartões');
  return `Excluir o quadro '${titulo}'? ${colunas} e ${cartoes} serão apagados. ${aviso}`;
}

export function textoExcluirColuna(titulo, totalCartoes) {
  if (totalCartoes === 0) return `Excluir a coluna '${titulo}'?`;
  if (totalCartoes === 1) return `Excluir a coluna '${titulo}' e seu único cartão?`;
  return `Excluir a coluna '${titulo}' e seus ${totalCartoes} cartões?`;
}

export function textoExcluirCartao(titulo) {
  return `Excluir o cartão '${titulo}'?`;
}
