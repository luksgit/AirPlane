// Estados de tela (carregando / vazio / erro / preenchido): mostra um e esconde os outros.

/**
 * `elementos` é um objeto { nomeDoEstado: elemento }.
 * Ex.: mostrarEstado({ carregando, lista, vazio, erro }, 'vazio')
 */
export function mostrarEstado(elementos, ativo) {
  for (const [nome, elemento] of Object.entries(elementos)) {
    elemento.hidden = nome !== ativo;
  }
}
