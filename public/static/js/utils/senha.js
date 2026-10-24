// Força da senha mostrada na barrinha do cadastro e do perfil.

const ROTULOS = ['', 'fraca', 'média', 'forte'];

/**
 * 0 = vazia, 1 = fraca, 2 = média, 3 = forte.
 * Média: 8+ caracteres com letras e números (o mínimo aceito).
 * Forte: além disso, 12+ caracteres, ou um símbolo, ou letras maiúsculas e minúsculas.
 */
export function forcaDaSenha(senha) {
  if (!senha) return 0;
  let pontos = 0;
  if (senha.length >= 8) pontos++;
  if (/[a-z]/i.test(senha) && /\d/.test(senha)) pontos++;
  const extra = senha.length >= 12 || /[^a-z0-9]/i.test(senha) || (/[a-z]/.test(senha) && /[A-Z]/.test(senha));
  if (pontos === 2 && extra) pontos++;
  return Math.max(1, pontos);
}

/** Texto da força: "fraca", "média" ou "forte" ('' para senha vazia). */
export function rotuloDaForca(forca) {
  return ROTULOS[forca] ?? '';
}
