// Conversa com a API do Flask: envia e recebe JSON e padroniza os erros.
// Toda tela usa este arquivo em vez de chamar fetch() direto.

const SEM_CONEXAO = 'Não foi possível conectar. Tente novamente.';
const ERRO_INESPERADO = 'Ocorreu um erro inesperado. Tente novamente.';

/** Erro devolvido pela API: status HTTP, mensagem amigável e erros por campo. */
export class ErroApi extends Error {
  constructor(status, mensagem, campos = {}) {
    super(mensagem);
    this.status = status;
    this.campos = campos;
  }
}

/**
 * Faz a requisição e devolve o JSON da resposta (ou null quando é 204).
 * Sessão expirada (401) leva para o login, exceto quando `redirecionarSe401` é false
 * (o próprio formulário de login trata o 401 como "senha incorreta").
 */
async function requisitar(metodo, url, corpo, { redirecionarSe401 = true } = {}) {
  let resposta;
  try {
    resposta = await fetch(url, {
      method: metodo,
      headers: corpo === undefined ? {} : { 'Content-Type': 'application/json' },
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
      credentials: 'same-origin',
    });
  } catch {
    throw new ErroApi(0, SEM_CONEXAO);
  }

  if (resposta.status === 401 && redirecionarSe401) {
    window.location.assign('/login');
    // A página já está saindo: a promessa fica pendente para a tela não mostrar erro.
    return new Promise(() => {});
  }
  if (resposta.status === 204) return null;

  const dados = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    throw new ErroApi(resposta.status, dados?.erro || ERRO_INESPERADO, dados?.campos || {});
  }
  return dados;
}

export const api = {
  get: (url, opcoes) => requisitar('GET', url, undefined, opcoes),
  post: (url, corpo = {}, opcoes) => requisitar('POST', url, corpo, opcoes),
  put: (url, corpo = {}, opcoes) => requisitar('PUT', url, corpo, opcoes),
  delete: (url, opcoes) => requisitar('DELETE', url, undefined, opcoes),
};
