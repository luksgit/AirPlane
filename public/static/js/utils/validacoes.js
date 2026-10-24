// Regras de validação dos formulários (as mesmas do back-end, em models/validacoes.py).
// Cada função devolve a mensagem de erro ou null se o valor for válido.

const EMAIL_FORMATO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function limpar(valor) {
  return typeof valor === 'string' ? valor.trim() : '';
}

export function validarNome(nome) {
  const texto = limpar(nome);
  if (!texto) return 'Informe seu nome';
  if (texto.length < 2) return 'O nome deve ter pelo menos 2 caracteres';
  if (texto.length > 100) return 'O nome deve ter no máximo 100 caracteres';
  return null;
}

export function validarEmail(email) {
  const texto = limpar(email);
  if (!texto) return 'Informe seu e-mail';
  if (texto.length > 150) return 'O e-mail deve ter no máximo 150 caracteres';
  if (!EMAIL_FORMATO.test(texto)) return 'Digite um e-mail válido';
  return null;
}

/** No login só conferimos se a senha foi digitada. */
export function validarSenhaPreenchida(senha) {
  return senha ? null : 'Informe sua senha';
}

/** Senha nova: mínimo de 8 caracteres, com pelo menos 1 letra e 1 número. */
export function validarSenha(senha) {
  const valor = typeof senha === 'string' ? senha : '';
  if (valor.length < 8 || !/\p{L}/u.test(valor) || !/\d/.test(valor)) {
    return 'A senha deve ter no mínimo 8 caracteres, com letras e números';
  }
  return null;
}

export function validarConfirmacao(senha, confirmacao) {
  return confirmacao && confirmacao === senha ? null : 'As senhas não coincidem';
}

export function validarSenhaDiferente(senhaAtual, novaSenha) {
  return senhaAtual === novaSenha ? 'A nova senha deve ser diferente da atual' : null;
}

export function validarTituloQuadro(titulo) {
  const texto = limpar(titulo);
  if (!texto) return 'Dê um nome ao seu quadro';
  if (texto.length > 100) return 'O título do quadro deve ter no máximo 100 caracteres';
  return null;
}

export function validarTituloColuna(titulo) {
  const texto = limpar(titulo);
  if (!texto) return 'O título da coluna não pode ficar vazio';
  if (texto.length > 50) return 'O título da coluna deve ter no máximo 50 caracteres';
  return null;
}

export function validarTituloCartao(titulo) {
  const texto = limpar(titulo);
  if (!texto) return 'Dê um título ao cartão';
  if (texto.length > 100) return 'O título do cartão deve ter no máximo 100 caracteres';
  return null;
}
