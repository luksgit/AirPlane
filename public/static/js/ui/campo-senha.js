// Comportamentos dos campos de senha: botão "olho" (mostrar/ocultar) e barra de força.
import { forcaDaSenha, rotuloDaForca } from '../utils/senha.js';

/** Liga todos os botões .campo__olho dentro de `raiz`. */
export function ligarOlhosDeSenha(raiz) {
  raiz.querySelectorAll('.campo__olho').forEach((botao) => {
    const entrada = document.getElementById(botao.getAttribute('aria-controls'));
    botao.addEventListener('click', () => {
      const mostrando = entrada.type === 'password';
      entrada.type = mostrando ? 'text' : 'password';
      botao.setAttribute('aria-pressed', String(mostrando));
      botao.setAttribute('aria-label', mostrando ? 'Ocultar senha' : 'Mostrar senha');
      botao.querySelector('[data-olho="aberto"]').hidden = mostrando;
      botao.querySelector('[data-olho="fechado"]').hidden = !mostrando;
    });
  });
}

/** Atualiza a barra de força (.forca) conforme o usuário digita a senha. */
export function ligarForcaDaSenha(entrada, barra) {
  const atualizar = () => {
    const forca = forcaDaSenha(entrada.value);
    barra.hidden = forca === 0;
    barra.dataset.forca = String(forca);
    barra.querySelector('.forca__texto').textContent = `Senha ${rotuloDaForca(forca)}`;
  };
  entrada.addEventListener('input', atualizar);
  atualizar();
}
