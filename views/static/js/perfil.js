// Tela "Meu perfil": trocar o nome, alterar a senha e sair.
import { api } from './api.js';
import { iniciarCabecalho, mostrarUsuarioNoCabecalho } from './header.js';
import { sair } from './sessao.js';
import { definirCarregando } from './ui/botao.js';
import { ligarForcaDaSenha, ligarOlhosDeSenha } from './ui/campo-senha.js';
import { juntarErros, limparErrosAoDigitar, mostrarErros, travarCampos } from './ui/formulario.js';
import { toast } from './ui/toast.js';
import { iniciais } from './utils/texto.js';
import { validarConfirmacao, validarNome, validarSenha, validarSenhaDiferente } from './utils/validacoes.js';

const formDados = document.getElementById('form-dados');
const formSenha = document.getElementById('form-senha');
const botaoDados = formDados.querySelector('[type="submit"]');
const botaoSenha = formSenha.querySelector('[type="submit"]');

// A API usa senha_atual / nova_senha; o formulário usa atual / nova.
const CAMPOS_DA_API = { senha_atual: 'atual', nova_senha: 'nova' };

function mostrarUsuario(usuario) {
  formDados.nome.value = usuario.nome;
  formDados.email.value = usuario.email;
  document.getElementById('perfil-avatar').textContent = iniciais(usuario.nome);
  document.getElementById('perfil-email-sessao').textContent = usuario.email;
}

formDados.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  if (mostrarErros(formDados, juntarErros({ nome: validarNome(formDados.nome.value) }))) return;

  definirCarregando(botaoDados, true, 'Salvando…');
  travarCampos(formDados, true);
  try {
    const usuario = await api.put('/api/usuarios/me', { nome: formDados.nome.value.trim() });
    mostrarUsuario(usuario);
    mostrarUsuarioNoCabecalho(usuario);
    toast('sucesso', 'Dados atualizados');
  } catch (erro) {
    if (!mostrarErros(formDados, erro.campos)) toast('erro', erro.message);
  } finally {
    definirCarregando(botaoDados, false);
    travarCampos(formDados, false);
  }
});

formSenha.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const { atual, nova, confirmar } = formSenha.elements;
  const erroNova = validarSenha(nova.value) || (atual.value && validarSenhaDiferente(atual.value, nova.value));
  const erros = juntarErros({
    atual: atual.value ? null : 'Informe sua senha atual',
    nova: erroNova,
    confirmar: validarConfirmacao(nova.value, confirmar.value),
  });
  if (mostrarErros(formSenha, erros)) return;

  definirCarregando(botaoSenha, true, 'Alterando…');
  travarCampos(formSenha, true);
  try {
    await api.put('/api/usuarios/me/senha', { senha_atual: atual.value, nova_senha: nova.value });
    formSenha.reset();
    nova.dispatchEvent(new Event('input')); // zera a barra de força
    toast('sucesso', 'Senha alterada com sucesso');
  } catch (erro) {
    const campos = Object.fromEntries(
      Object.entries(erro.campos).map(([campo, mensagem]) => [CAMPOS_DA_API[campo] || campo, mensagem]),
    );
    if (!mostrarErros(formSenha, campos)) toast('erro', erro.message);
  } finally {
    definirCarregando(botaoSenha, false);
    travarCampos(formSenha, false);
  }
});

ligarOlhosDeSenha(formSenha);
ligarForcaDaSenha(formSenha.nova, document.getElementById('nova-forca'));
limparErrosAoDigitar(formDados);
limparErrosAoDigitar(formSenha);
document.querySelector('.perfil__sessao [data-acao="sair"]').addEventListener('click', sair);

iniciarCabecalho().then((usuario) => {
  if (usuario) mostrarUsuario(usuario);
});
