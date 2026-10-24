// Notificações (toasts): até 3 empilhadas, somem em 4 s e têm botão de fechar.

const LIMITE = 3;
const DURACAO_MS = 4000;
const CHAVE_PROXIMA_PAGINA = 'airplan:toast';

/** Mostra um toast. tipo: "sucesso" | "erro" | "info". */
export function toast(tipo, mensagem) {
  const container = document.getElementById('toasts');
  const elemento = document.getElementById('tpl-toast').content.firstElementChild.cloneNode(true);

  elemento.dataset.tipo = tipo;
  elemento.querySelectorAll('.toast__icone svg').forEach((icone) => {
    if (icone.dataset.tipo !== tipo) icone.remove();
  });
  elemento.querySelector('.toast__mensagem').textContent = mensagem;

  const remover = () => elemento.remove();
  elemento.querySelector('button').addEventListener('click', remover);
  setTimeout(remover, DURACAO_MS);

  container.append(elemento);
  while (container.children.length > LIMITE) container.firstElementChild.remove();
}

/**
 * Guarda um toast para aparecer depois de trocar de página
 * (ex.: "Quadro criado" ao abrir o quadro recém-criado).
 */
export function toastNaProximaPagina(tipo, mensagem) {
  try {
    sessionStorage.setItem(CHAVE_PROXIMA_PAGINA, JSON.stringify({ tipo, mensagem }));
  } catch {
    // Sem sessionStorage (modo privado restrito): o toast só não aparece.
  }
}

function mostrarToastGuardado() {
  try {
    const guardado = JSON.parse(sessionStorage.getItem(CHAVE_PROXIMA_PAGINA));
    sessionStorage.removeItem(CHAVE_PROXIMA_PAGINA);
    if (guardado) toast(guardado.tipo, guardado.mensagem);
  } catch {
    // Nada guardado ou sessionStorage indisponível.
  }
}

mostrarToastGuardado();
