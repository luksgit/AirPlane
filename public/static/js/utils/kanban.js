// Operações no estado do quadro (lista de colunas, cada uma com seus cartões).
// Funções puras: recebem as colunas e devolvem uma cópia nova, sem mexer na original.
// Assim, se a API falhar, basta voltar para a lista antiga (drag and drop otimista).

/** Reescreve as posições 0, 1, 2… na ordem atual da lista. */
function renumerar(itens) {
  itens.forEach((item, indice) => {
    item.posicao = indice;
  });
}

/** Acha o cartão: devolve { coluna, cartao, indice } ou null. */
export function encontrarCartao(colunas, cartaoId) {
  for (const coluna of colunas) {
    const indice = coluna.cartoes.findIndex((cartao) => cartao.id === cartaoId);
    if (indice !== -1) return { coluna, cartao: coluna.cartoes[indice], indice };
  }
  return null;
}

/**
 * Move o cartão para `posicao` na coluna de destino (mesma regra do back-end):
 * a posição conta os cartões do destino sem o próprio cartão; além do fim, vai para o fim.
 */
export function moverCartao(colunas, cartaoId, colunaDestinoId, posicao) {
  const novas = structuredClone(colunas);
  const origem = encontrarCartao(novas, cartaoId);
  const destino = novas.find((coluna) => coluna.id === colunaDestinoId);
  if (!origem || !destino) return novas;

  const [cartao] = origem.coluna.cartoes.splice(origem.indice, 1);
  destino.cartoes.splice(Math.min(posicao, destino.cartoes.length), 0, cartao);
  renumerar(origem.coluna.cartoes);
  renumerar(destino.cartoes);
  return novas;
}

/** Coloca um cartão novo no fim da coluna. */
export function adicionarCartao(colunas, colunaId, cartao) {
  const novas = structuredClone(colunas);
  const coluna = novas.find((c) => c.id === colunaId);
  coluna?.cartoes.push(cartao);
  if (coluna) renumerar(coluna.cartoes);
  return novas;
}

/**
 * Troca os dados do cartão pelos salvos na API.
 * Se `coluna_id` mudou, o cartão vai para o fim da nova coluna.
 */
export function salvarCartao(colunas, cartaoSalvo) {
  const novas = structuredClone(colunas);
  const atual = encontrarCartao(novas, cartaoSalvo.id);
  if (!atual) return novas;

  const { coluna_id: colunaId, ...dados } = cartaoSalvo;
  if (colunaId === undefined || colunaId === atual.coluna.id) {
    atual.coluna.cartoes[atual.indice] = { ...atual.cartao, ...dados, posicao: atual.indice };
    return novas;
  }
  const destino = novas.find((coluna) => coluna.id === colunaId);
  atual.coluna.cartoes.splice(atual.indice, 1);
  destino.cartoes.push({ ...atual.cartao, ...dados });
  renumerar(atual.coluna.cartoes);
  renumerar(destino.cartoes);
  return novas;
}

export function removerCartao(colunas, cartaoId) {
  const novas = structuredClone(colunas);
  const atual = encontrarCartao(novas, cartaoId);
  if (atual) {
    atual.coluna.cartoes.splice(atual.indice, 1);
    renumerar(atual.coluna.cartoes);
  }
  return novas;
}

export function removerColuna(colunas, colunaId) {
  const novas = structuredClone(colunas).filter((coluna) => coluna.id !== colunaId);
  renumerar(novas);
  return novas;
}
