// Pequenas regras de texto usadas em várias telas.

/** "Lucas Santos" → "LS"; "Ana" → "A". */
export function iniciais(nome) {
  const partes = (nome || '').trim().split(/\s+/).filter(Boolean);
  if (partes.length === 0) return '?';
  const primeira = partes[0][0];
  const ultima = partes.length > 1 ? partes[partes.length - 1][0] : '';
  return (primeira + ultima).toUpperCase();
}

/** plural(1, 'cartão', 'cartões') → "1 cartão"; plural(3, …) → "3 cartões". */
export function plural(quantidade, singular, pluralTexto) {
  return `${quantidade} ${quantidade === 1 ? singular : pluralTexto}`;
}
