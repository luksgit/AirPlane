import assert from 'node:assert/strict';
import { describe, test } from 'node:test';

import {
  adicionarCartao,
  encontrarCartao,
  moverCartao,
  removerCartao,
  removerColuna,
  salvarCartao,
} from '../../public/static/js/utils/kanban.js';

/** Quadro de exemplo: Embarque [A, B, C], Em voo [D], Pousou []. */
function quadroDeExemplo() {
  const cartao = (id, titulo, posicao) => ({ id, titulo, posicao, descricao: null, prazo: null, cor_etiqueta: null });
  return [
    { id: 1, titulo: 'Embarque', posicao: 0, cartoes: [cartao(11, 'A', 0), cartao(12, 'B', 1), cartao(13, 'C', 2)] },
    { id: 2, titulo: 'Em voo', posicao: 1, cartoes: [cartao(21, 'D', 0)] },
    { id: 3, titulo: 'Pousou', posicao: 2, cartoes: [] },
  ];
}

/** [['A','B','C'], ['D'], []] e confere que as posições estão contínuas. */
function disposicao(colunas) {
  return colunas.map((coluna) => {
    assert.deepEqual(coluna.cartoes.map((c) => c.posicao), coluna.cartoes.map((_, i) => i));
    return coluna.cartoes.map((c) => c.titulo);
  });
}

describe('moverCartao', () => {
  test('dentro da mesma coluna', () => {
    assert.deepEqual(disposicao(moverCartao(quadroDeExemplo(), 11, 1, 2)), [['B', 'C', 'A'], ['D'], []]);
    assert.deepEqual(disposicao(moverCartao(quadroDeExemplo(), 13, 1, 0)), [['C', 'A', 'B'], ['D'], []]);
  });

  test('entre colunas, na posição escolhida', () => {
    assert.deepEqual(disposicao(moverCartao(quadroDeExemplo(), 12, 2, 0)), [['A', 'C'], ['B', 'D'], []]);
    assert.deepEqual(disposicao(moverCartao(quadroDeExemplo(), 21, 1, 1)), [['A', 'D', 'B', 'C'], [], []]);
    assert.deepEqual(disposicao(moverCartao(quadroDeExemplo(), 11, 3, 0)), [['B', 'C'], ['D'], ['A']]);
  });

  test('posição além do fim vai para o fim', () => {
    assert.deepEqual(disposicao(moverCartao(quadroDeExemplo(), 11, 2, 99)), [['B', 'C'], ['D', 'A'], []]);
  });

  test('não altera a lista original (permite desfazer se a API falhar)', () => {
    const original = quadroDeExemplo();
    moverCartao(original, 11, 3, 0);
    assert.deepEqual(disposicao(original), [['A', 'B', 'C'], ['D'], []]);
  });
});

describe('outras operações', () => {
  test('encontrarCartao', () => {
    const achado = encontrarCartao(quadroDeExemplo(), 12);
    assert.equal(achado.coluna.id, 1);
    assert.equal(achado.indice, 1);
    assert.equal(encontrarCartao(quadroDeExemplo(), 999), null);
  });

  test('adicionarCartao vai para o fim da coluna', () => {
    const novas = adicionarCartao(quadroDeExemplo(), 2, { id: 22, titulo: 'E', posicao: 1 });
    assert.deepEqual(disposicao(novas), [['A', 'B', 'C'], ['D', 'E'], []]);
  });

  test('salvarCartao na mesma coluna mantém a posição', () => {
    const novas = salvarCartao(quadroDeExemplo(), { id: 12, titulo: 'B2', coluna_id: 1, prazo: '2026-11-17' });
    assert.deepEqual(disposicao(novas), [['A', 'B2', 'C'], ['D'], []]);
    assert.equal(novas[0].cartoes[1].prazo, '2026-11-17');
  });

  test('salvarCartao trocando de coluna vai para o fim da nova', () => {
    const novas = salvarCartao(quadroDeExemplo(), { id: 11, titulo: 'A', coluna_id: 2 });
    assert.deepEqual(disposicao(novas), [['B', 'C'], ['D', 'A'], []]);
  });

  test('removerCartao reordena a coluna', () => {
    assert.deepEqual(disposicao(removerCartao(quadroDeExemplo(), 11)), [['B', 'C'], ['D'], []]);
  });

  test('removerColuna reordena as colunas', () => {
    const novas = removerColuna(quadroDeExemplo(), 2);
    assert.deepEqual(novas.map((c) => [c.titulo, c.posicao]), [['Embarque', 0], ['Pousou', 1]]);
  });
});
