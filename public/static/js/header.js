// Header das telas internas: avatar com as iniciais e menu (Meu perfil / Sair).
import { api } from './api.js';
import { sair } from './sessao.js';
import { ligarMenu } from './ui/menu.js';
import { toast } from './ui/toast.js';
import { iniciais } from './utils/texto.js';

/** Preenche o header com os dados do usuário. */
export function mostrarUsuarioNoCabecalho(usuario) {
  const avatar = document.getElementById('avatar');
  avatar.textContent = iniciais(usuario.nome);
  avatar.setAttribute('aria-label', `Menu do usuário ${usuario.nome}`);
  document.getElementById('menu-usuario-nome').textContent = usuario.nome;
  document.getElementById('menu-usuario-email').textContent = usuario.email;
}

/** Liga o menu do avatar e carrega o usuário logado. Devolve o usuário (ou null se falhar). */
export async function iniciarCabecalho() {
  ligarMenu(document.getElementById('avatar'), document.getElementById('menu-usuario'));
  document.querySelector('#menu-usuario [data-acao="sair"]').addEventListener('click', sair);

  try {
    const usuario = await api.get('/api/usuarios/me');
    mostrarUsuarioNoCabecalho(usuario);
    return usuario;
  } catch (erro) {
    toast('erro', erro.message);
    return null;
  }
}
