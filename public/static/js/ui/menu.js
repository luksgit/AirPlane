// Menus "⋯" e do avatar. Regras: só um menu aberto por vez; clique fora fecha
// (conferido contra o próprio menu e o botão dele); Esc fecha e devolve o foco ao botão.

let aberto = null; // { botao, menu } do menu aberto agora

/** Liga um botão ao seu menu (elemento com o atributo hidden). */
export function ligarMenu(botao, menu) {
  botao.addEventListener('click', (evento) => {
    evento.stopPropagation();
    if (aberto?.menu === menu) fecharMenu();
    else abrirMenu(botao, menu);
  });
  // Clicar numa opção fecha o menu e devolve o foco ao botão "⋯". Roda na fase de
  // captura (antes da ação da opção), para que um modal aberto pela opção saiba
  // devolver o foco ao botão quando fechar.
  menu.addEventListener('click', (evento) => {
    if (evento.target.closest('[role="menuitem"]')) fecharMenu(true);
  }, true);
}

function abrirMenu(botao, menu) {
  fecharMenu();
  menu.hidden = false;
  botao.setAttribute('aria-expanded', 'true');
  aberto = { botao, menu };
}

/** Fecha o menu aberto (se houver). Com devolverFoco, o foco volta para o botão do menu. */
export function fecharMenu(devolverFoco = false) {
  if (!aberto) return;
  const { botao, menu } = aberto;
  aberto = null;
  menu.hidden = true;
  botao.setAttribute('aria-expanded', 'false');
  if (devolverFoco && botao.isConnected) botao.focus();
}

document.addEventListener('mousedown', (evento) => {
  if (aberto && !aberto.menu.contains(evento.target) && !aberto.botao.contains(evento.target)) {
    fecharMenu();
  }
});

document.addEventListener('keydown', (evento) => {
  if (evento.key === 'Escape' && aberto) fecharMenu(true);
});
