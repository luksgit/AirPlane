import assert from 'node:assert/strict';
import { describe, test } from 'node:test';

import { diasAtePrazo, formatarDiaMes, statusDoPrazo } from '../../views/static/js/utils/prazo.js';

// "Hoje" fixo nos testes: 24/10/2026, à tarde (o horário não pode influenciar).
const HOJE = new Date(2026, 9, 24, 15, 30);

describe('formatarDiaMes', () => {
  test('formata como "dd mmm" em português', () => {
    assert.equal(formatarDiaMes('2026-11-07'), '07 nov');
    assert.equal(formatarDiaMes('2026-01-31'), '31 jan');
    assert.equal(formatarDiaMes('2026-12-25'), '25 dez');
  });
});

describe('diasAtePrazo', () => {
  test('conta dias inteiros a partir de hoje', () => {
    assert.equal(diasAtePrazo('2026-10-24', HOJE), 0);
    assert.equal(diasAtePrazo('2026-10-25', HOJE), 1);
    assert.equal(diasAtePrazo('2026-10-20', HOJE), -4);
    assert.equal(diasAtePrazo('2026-11-17', HOJE), 24);
  });
});

describe('statusDoPrazo', () => {
  test('sem prazo devolve null', () => {
    assert.equal(statusDoPrazo(null, HOJE), null);
    assert.equal(statusDoPrazo('', HOJE), null);
  });

  test('vencido: "Atrasado · dd mmm"', () => {
    assert.deepEqual(statusDoPrazo('2026-10-20', HOJE), {
      status: 'atrasado',
      texto: 'Atrasado · 20 out',
      descricao: 'atrasado, venceu em 20 out',
    });
    assert.equal(statusDoPrazo('2026-10-23', HOJE).status, 'atrasado');
  });

  test('hoje, amanhã e depois de amanhã: "em breve"', () => {
    for (const iso of ['2026-10-24', '2026-10-25', '2026-10-26']) {
      assert.equal(statusDoPrazo(iso, HOJE).status, 'em-breve', iso);
    }
    assert.equal(statusDoPrazo('2026-10-25', HOJE).texto, '25 out');
  });

  test('3 dias ou mais: normal', () => {
    assert.deepEqual(statusDoPrazo('2026-10-27', HOJE), {
      status: 'normal',
      texto: '27 out',
      descricao: 'prazo 27 out',
    });
  });

  test('funciona na virada do ano', () => {
    const fimDoAno = new Date(2026, 11, 31);
    assert.equal(statusDoPrazo('2027-01-02', fimDoAno).status, 'em-breve');
    assert.equal(statusDoPrazo('2027-01-03', fimDoAno).status, 'normal');
    assert.equal(statusDoPrazo('2026-12-30', fimDoAno).status, 'atrasado');
  });
});
