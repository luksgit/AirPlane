import assert from 'node:assert/strict';
import { describe, test } from 'node:test';

import {
  resumoDoQuadro,
  textoExcluirCartao,
  textoExcluirColuna,
  textoExcluirQuadro,
} from '../../views/static/js/utils/mensagens.js';
import { iniciais, plural } from '../../views/static/js/utils/texto.js';

describe('iniciais', () => {
  test('primeira letra do primeiro e do último nome', () => {
    assert.equal(iniciais('Lucas Santos'), 'LS');
    assert.equal(iniciais('ana maria de souza'), 'AS');
    assert.equal(iniciais('  Bruno  '), 'B');
    assert.equal(iniciais(''), '?');
  });
});

describe('plural', () => {
  test('singular só para 1', () => {
    assert.equal(plural(0, 'cartão', 'cartões'), '0 cartões');
    assert.equal(plural(1, 'cartão', 'cartões'), '1 cartão');
    assert.equal(plural(2, 'cartão', 'cartões'), '2 cartões');
  });
});

describe('mensagens de exclusão (singular e plural)', () => {
  test('resumo do card do quadro', () => {
    assert.equal(resumoDoQuadro(3, 8), '3 colunas · 8 cartões');
    assert.equal(resumoDoQuadro(1, 1), '1 coluna · 1 cartão');
  });

  test('excluir quadro', () => {
    assert.equal(
      textoExcluirQuadro('Treino', 3, 5),
      "Excluir o quadro 'Treino'? Todas as 3 colunas e 5 cartões serão apagados. Essa ação não pode ser desfeita.",
    );
    assert.equal(
      textoExcluirQuadro('Treino', 1, 1),
      "Excluir o quadro 'Treino'? A única coluna e 1 cartão serão apagados. Essa ação não pode ser desfeita.",
    );
    assert.equal(textoExcluirQuadro('Vazio', 0, 0), "Excluir o quadro 'Vazio'? Essa ação não pode ser desfeita.");
  });

  test('excluir coluna', () => {
    assert.equal(textoExcluirColuna('Pousou', 0), "Excluir a coluna 'Pousou'?");
    assert.equal(textoExcluirColuna('Pousou', 1), "Excluir a coluna 'Pousou' e seu único cartão?");
    assert.equal(textoExcluirColuna('Pousou', 3), "Excluir a coluna 'Pousou' e seus 3 cartões?");
  });

  test('excluir cartão', () => {
    assert.equal(textoExcluirCartao('Gravar vídeo'), "Excluir o cartão 'Gravar vídeo'?");
  });
});
