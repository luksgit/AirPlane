// Ações de sessão usadas em mais de uma tela.
import { api } from './api.js';
import { definirCarregando } from './ui/botao.js';
import { toast, toastNaProximaPagina } from './ui/toast.js';

/**
 * Encerra a sessão e volta para o login com a mensagem de despedida.
 * Se for chamado por um botão (.botao), ele fica em "Saindo…" até a resposta.
 */
export async function sair(evento) {
  const botao = evento?.currentTarget?.classList?.contains('botao') ? evento.currentTarget : null;
  if (botao) definirCarregando(botao, true, 'Saindo…');
  try {
    await api.post('/api/auth/logout');
    toastNaProximaPagina('info', 'Até a próxima viagem! 👋');
    window.location.assign('/login');
  } catch (erro) {
    if (botao) definirCarregando(botao, false);
    toast('erro', erro.message);
  }
}
