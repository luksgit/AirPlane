// Tela de Login.
import { api } from './api.js';
import { definirCarregando } from './ui/botao.js';
import { ligarOlhosDeSenha } from './ui/campo-senha.js';
import { juntarErros, limparErrosAoDigitar, mostrarErros, travarCampos } from './ui/formulario.js';
import { toast } from './ui/toast.js';
import { validarEmail, validarSenhaPreenchida } from './utils/validacoes.js';

const formulario = document.getElementById('form-login');
const botao = formulario.querySelector('[type="submit"]');
const alerta = document.getElementById('alerta-login');

ligarOlhosDeSenha(formulario);
limparErrosAoDigitar(formulario, () => {
  alerta.hidden = true;
});

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const dados = { email: formulario.email.value.trim(), senha: formulario.senha.value };

  alerta.hidden = true;
  const erros = juntarErros({ email: validarEmail(dados.email), senha: validarSenhaPreenchida(dados.senha) });
  if (mostrarErros(formulario, erros)) return;

  definirCarregando(botao, true, 'Decolando…');
  travarCampos(formulario, true);
  try {
    await api.post('/api/auth/login', dados, { redirecionarSe401: false });
    window.location.assign('/quadros');
  } catch (erro) {
    definirCarregando(botao, false);
    travarCampos(formulario, false);
    if (erro.status === 401) {
      alerta.hidden = false;
      formulario.senha.focus();
    } else if (!mostrarErros(formulario, erro.campos)) {
      toast('erro', erro.message);
    }
  }
});
