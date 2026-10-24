# Registro de correções

Consolida os registros dos 5 testadores e o que foi feito com cada um. Cada correção vira um commit `fix: …` no GitHub, citado na última coluna.

**Status:** ✅ Corrigido · 🔁 Melhorado · ➖ Não é bug (comportamento esperado) · 🚫 Fora do escopo do MVP

| ID | Testador(es) | Tela | Tipo | Gravidade | Descrição resumida | Decisão / correção aplicada | Status | Commit |
|---|---|---|---|---|---|---|---|---|
| B01 | | | | | | | | |
| B02 | | | | | | | | |
| B03 | | | | | | | | |

## Funcionalidades sugeridas e não implementadas

Itens fora do escopo do MVP (definido no planejamento) entram aqui, com a justificativa:

| Sugestão | Testador(es) | Justificativa |
|---|---|---|
| | | Funcionalidade não implementada (fora do escopo do MVP) |

## Correções feitas antes dos testes com usuários

Problemas encontrados pelo próprio desenvolvedor nos testes automatizados de interface, antes de entregar o link aos colegas:

| ID | Tela | Descrição | Correção |
|---|---|---|---|
| D01 | Quadro (Kanban) | Ao renomear o quadro pelo título, o nome novo era salvo no banco mas a tela mostrava o antigo. | `quadro/titulo.js` passou a guardar a referência do botão do título, em vez de procurá-lo na página enquanto o campo de edição ocupa o lugar dele. |
| D02 | Kanban, menus | Ao escolher uma opção do menu "⋯", o foco não voltava para o botão do menu depois de fechar o modal aberto pela opção. | `ui/menu.js` fecha o menu e devolve o foco ao botão antes de executar a opção. |
