import assert from 'node:assert/strict';
import { describe, test } from 'node:test';

import { forcaDaSenha, rotuloDaForca } from '../../public/static/js/utils/senha.js';

describe('forcaDaSenha', () => {
  test('vazia = 0', () => {
    assert.equal(forcaDaSenha(''), 0);
  });

  test('fraca: curta ou sem letras e números juntos', () => {
    assert.equal(forcaDaSenha('abc'), 1);
    assert.equal(forcaDaSenha('abc1'), 1);
    assert.equal(forcaDaSenha('somenteletras'), 1);
    assert.equal(forcaDaSenha('12345678'), 1);
  });

  test('média: 8+ caracteres com letras e números', () => {
    assert.equal(forcaDaSenha('voo12345'), 2);
    assert.equal(forcaDaSenha('aviao2026'), 2);
  });

  test('forte: média + (12+ caracteres, símbolo ou maiúsculas e minúsculas)', () => {
    assert.equal(forcaDaSenha('aviao2026voa'), 3);
    assert.equal(forcaDaSenha('voo12345!'), 3);
    assert.equal(forcaDaSenha('Voo12345'), 3);
  });
});

describe('rotuloDaForca', () => {
  test('traduz o número em texto', () => {
    assert.equal(rotuloDaForca(0), '');
    assert.equal(rotuloDaForca(1), 'fraca');
    assert.equal(rotuloDaForca(2), 'média');
    assert.equal(rotuloDaForca(3), 'forte');
  });
});
