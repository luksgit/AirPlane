import assert from 'node:assert/strict';
import { describe, test } from 'node:test';

import {
  validarConfirmacao,
  validarEmail,
  validarNome,
  validarSenha,
  validarSenhaDiferente,
  validarSenhaPreenchida,
  validarTituloCartao,
  validarTituloColuna,
  validarTituloQuadro,
} from '../../views/static/js/utils/validacoes.js';

const SENHA_FRACA = 'A senha deve ter no mínimo 8 caracteres, com letras e números';

describe('validarNome', () => {
  test('aceita nome com 2 a 100 caracteres', () => {
    assert.equal(validarNome('Lu'), null);
    assert.equal(validarNome('  Lucas Santos  '), null);
    assert.equal(validarNome('A'.repeat(100)), null);
  });

  test('recusa vazio, curto e longo', () => {
    assert.equal(validarNome(''), 'Informe seu nome');
    assert.equal(validarNome('   '), 'Informe seu nome');
    assert.equal(validarNome(undefined), 'Informe seu nome');
    assert.equal(validarNome(' L '), 'O nome deve ter pelo menos 2 caracteres');
    assert.equal(validarNome('A'.repeat(101)), 'O nome deve ter no máximo 100 caracteres');
  });
});

describe('validarEmail', () => {
  test('aceita e-mail válido (com espaços nas pontas)', () => {
    assert.equal(validarEmail('lucas@email.com'), null);
    assert.equal(validarEmail('  Lucas.Santos@Email.com.br '), null);
  });

  test('recusa vazio, formato errado e longo demais', () => {
    assert.equal(validarEmail(''), 'Informe seu e-mail');
    assert.equal(validarEmail('lucas.email.com'), 'Digite um e-mail válido');
    assert.equal(validarEmail('lucas@email'), 'Digite um e-mail válido');
    assert.equal(validarEmail('lu cas@email.com'), 'Digite um e-mail válido');
    assert.equal(validarEmail(`${'a'.repeat(141)}@email.com`), 'O e-mail deve ter no máximo 150 caracteres');
  });
});

describe('senhas', () => {
  test('validarSenha exige 8+ caracteres com letra e número', () => {
    assert.equal(validarSenha('voo12345'), null);
    assert.equal(validarSenha('Avião2026'), null);
    assert.equal(validarSenha('abc1234'), SENHA_FRACA);
    assert.equal(validarSenha('somenteletras'), SENHA_FRACA);
    assert.equal(validarSenha('12345678'), SENHA_FRACA);
    assert.equal(validarSenha(''), SENHA_FRACA);
  });

  test('no login basta a senha estar preenchida', () => {
    assert.equal(validarSenhaPreenchida('x'), null);
    assert.equal(validarSenhaPreenchida(''), 'Informe sua senha');
  });

  test('confirmação precisa ser igual e não vazia', () => {
    assert.equal(validarConfirmacao('voo12345', 'voo12345'), null);
    assert.equal(validarConfirmacao('voo12345', 'voo1234'), 'As senhas não coincidem');
    assert.equal(validarConfirmacao('', ''), 'As senhas não coincidem');
  });

  test('nova senha precisa ser diferente da atual', () => {
    assert.equal(validarSenhaDiferente('voo12345', 'novaSenha1'), null);
    assert.equal(validarSenhaDiferente('voo12345', 'voo12345'), 'A nova senha deve ser diferente da atual');
  });
});

describe('títulos', () => {
  test('quadro: obrigatório e até 100', () => {
    assert.equal(validarTituloQuadro('PIT II'), null);
    assert.equal(validarTituloQuadro('   '), 'Dê um nome ao seu quadro');
    assert.equal(validarTituloQuadro('A'.repeat(101)), 'O título do quadro deve ter no máximo 100 caracteres');
  });

  test('coluna: obrigatório e até 50', () => {
    assert.equal(validarTituloColuna('Em voo'), null);
    assert.equal(validarTituloColuna(''), 'O título da coluna não pode ficar vazio');
    assert.equal(validarTituloColuna('A'.repeat(50)), null);
    assert.equal(validarTituloColuna('A'.repeat(51)), 'O título da coluna deve ter no máximo 50 caracteres');
  });

  test('cartão: obrigatório e até 100', () => {
    assert.equal(validarTituloCartao('Gravar vídeo'), null);
    assert.equal(validarTituloCartao(' '), 'Dê um título ao cartão');
    assert.equal(validarTituloCartao('A'.repeat(101)), 'O título do cartão deve ter no máximo 100 caracteres');
  });
});
