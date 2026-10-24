// Tela de Cadastro.
import { api } from './api.js';
import { definirCarregando } from './ui/botao.js';
import { ligarForcaDaSenha, ligarOlhosDeSenha } from './ui/campo-senha.js';
import { juntarErros, limparErro, limparErrosAoDigitar, mostrarErro, mostrarErros, travarCampos } from './ui/formulario.js';
import { toast, toastNaProximaPagina } from './ui/toast.js';
import { validarConfirmacao, validarEmail, validarNome, validarSenha } from './utils/validacoes.js';

const formulario = document.getElementById('form-cadastro');
const botao = formulario.querySelector('[type="submit"]');

/** Erro de cada campo com os valores atuais do formulário (null = válido). */
function validarCampo(nome) {
  const valores = formulario.elements;
  const regras = {
    nome: () => validarNome(valores.nome.value),
    email: () => validarEmail(valores.email.value),
    senha: () => validarSenha(valores.senha.value),
    confirmar: () => validarConfirmacao(valores.senha.value, valores.confirmar.value),
  };
  return regras[nome]();
}

ligarOlhosDeSenha(formulario);
ligarForcaDaSenha(formulario.senha, document.getElementById('senha-forca'));
limparErrosAoDigitar(formulario);

// Ao sair de um campo já preenchido, ele é validado na hora.
formulario.addEventListener('focusout', (evento) => {
  const entrada = evento.target;
  if (!entrada.matches('.campo__entrada') || !entrada.value) return;
  const erro = validarCampo(entrada.name);
  if (erro) mostrarErro(entrada, erro);
  else limparErro(entrada);
});

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const erros = juntarErros({
    nome: validarCampo('nome'),
    email: validarCampo('email'),
    senha: validarCampo('senha'),
    confirmar: validarCampo('confirmar'),
  });
  if (mostrarErros(formulario, erros)) return;

  definirCarregando(botao, true, 'Criando conta…');
  travarCampos(formulario, true);
  try {
    const usuario = await api.post('/api/auth/cadastro', {
      nome: formulario.nome.value.trim(),
      email: formulario.email.value.trim(),
      senha: formulario.senha.value,
    });
    toastNaProximaPagina('sucesso', `Bem-vindo a bordo, ${usuario.nome}! ✈️`);
    window.location.assign('/quadros');
  } catch (erro) {
    definirCarregando(botao, false);
    travarCampos(formulario, false);
    // 409 (e-mail já cadastrado) e 400 vêm com o campo certo em erro.campos.
    if (!mostrarErros(formulario, erro.campos)) toast('erro', erro.message);
  }
});
