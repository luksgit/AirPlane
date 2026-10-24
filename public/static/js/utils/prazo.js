// Selo de prazo dos cartões: "normal", "em breve" (vence em até 2 dias) ou "atrasado".
// A data de hoje vem por parâmetro, para os testes não dependerem do relógio.

const MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
const UM_DIA_MS = 24 * 60 * 60 * 1000;

/** Converte "AAAA-MM-DD" numa data local à meia-noite (sem fuso: o prazo é só um dia). */
function lerData(iso) {
  const [ano, mes, dia] = iso.split('-').map(Number);
  return new Date(ano, mes - 1, dia);
}

function meiaNoite(data) {
  return new Date(data.getFullYear(), data.getMonth(), data.getDate());
}

/** "2026-11-07" → "07 nov" */
export function formatarDiaMes(iso) {
  const data = lerData(iso);
  return `${String(data.getDate()).padStart(2, '0')} ${MESES[data.getMonth()]}`;
}

/** Quantos dias faltam até o prazo (negativo se já passou). */
export function diasAtePrazo(iso, hoje) {
  return Math.round((lerData(iso) - meiaNoite(hoje)) / UM_DIA_MS);
}

/**
 * Devolve { status, texto, descricao } para desenhar o selo, ou null se não houver prazo.
 * status: "normal" | "em-breve" | "atrasado"; descricao é o texto para leitores de tela.
 */
export function statusDoPrazo(iso, hoje = new Date()) {
  if (!iso) return null;
  const diaMes = formatarDiaMes(iso);
  const dias = diasAtePrazo(iso, hoje);
  if (dias < 0) {
    return { status: 'atrasado', texto: `Atrasado · ${diaMes}`, descricao: `atrasado, venceu em ${diaMes}` };
  }
  if (dias <= 2) {
    return { status: 'em-breve', texto: diaMes, descricao: `vence em breve, ${diaMes}` };
  }
  return { status: 'normal', texto: diaMes, descricao: `prazo ${diaMes}` };
}
