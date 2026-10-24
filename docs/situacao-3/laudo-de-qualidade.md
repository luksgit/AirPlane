# Laudo de qualidade: AirPlan

> Estrutura do laudo. Os campos entre `< >` são preenchidos depois dos testes com os 5 colegas.

## 1. Identificação

| Item | Descrição |
|---|---|
| Produto | AirPlan: gerenciador de tarefas Kanban |
| Versão avaliada | `<tag ou commit>` |
| Endereço | `<link do Render>` |
| Responsável | Lucas Santos |
| Disciplina | Projeto Integrador Transdisciplinar em Engenharia de Software II |
| Período dos testes | `<data inicial> a <data final>` |

## 2. Objetivo

Avaliar se o AirPlan atende aos requisitos definidos na Situação-Problema 1 e se está pronto para uso, combinando **testes automatizados** (feitos pelo desenvolvedor) e **testes exploratórios com 5 usuários** (colegas de turma).

## 3. Metodologia

1. **Testes automatizados**
   - Back-end: Pytest, com requisições reais à API e ao banco PostgreSQL.
   - Front-end: `node --test`, sobre as funções puras de validação, prazo, força de senha, mensagens e Kanban.
   - Interface: roteiros automatizados em navegador *headless* (Edge), cobrindo os fluxos principais no desktop e no celular.
2. **Testes com usuários:** cada colega seguiu o [roteiro de teste](roteiro-de-teste.md) e registrou os problemas no [formulário de bugs](formulario-de-bugs.md), com prints.
3. **Consolidação:** registros iguais foram agrupados, classificados por gravidade e tratados no [registro de correções](registro-de-correcoes.md).
4. **Reteste:** cada correção foi verificada de novo e as suítes automatizadas foram executadas outra vez.

### Critérios de qualidade (baseados na ISO/IEC 25010)

| Característica | Como foi avaliada |
|---|---|
| Adequação funcional | Todas as tarefas do roteiro concluídas; testes de API cobrindo cada rota |
| Usabilidade | Notas do formulário; mensagens claras; acessibilidade por teclado |
| Confiabilidade | Erros tratados (sem conexão, sessão expirada, 404); desfazer do arrastar quando a API falha |
| Segurança | Isolamento entre usuários (404), senhas com hash, SQL parametrizado, sem `innerHTML` com dados do usuário |
| Compatibilidade | Navegadores e dispositivos usados pelos testadores |
| Desempenho | Tempo de resposta percebido (o primeiro acesso no plano grátis é registrado à parte) |

## 4. Ambiente de teste

| Testador | Dispositivo / sistema | Navegador |
|---|---|---|
| 1 | `< >` | `< >` |
| 2 | `< >` | `< >` |
| 3 | `< >` | `< >` |
| 4 | `< >` | `< >` |
| 5 | `< >` | `< >` |

## 5. Resultados dos testes automatizados

| Suíte | Antes dos testes com usuários | Depois das correções |
|---|---|---|
| Pytest (back-end) | 141 testes: 141 aprovados | `< >` |
| node --test (front-end) | 39 testes: 39 aprovados | `< >` |
| Roteiros de interface | 47 verificações: todas aprovadas após 2 correções (D01, D02) | `< >` |

## 6. Resultados dos testes com usuários

### 6.1 Registros por gravidade

| Gravidade | Quantidade | Corrigidos |
|---|---|---|
| Crítica | `< >` | `< >` |
| Alta | `< >` | `< >` |
| Média | `< >` | `< >` |
| Baixa | `< >` | `< >` |
| Sugestões | `< >` | `< >` |

### 6.2 Notas médias (1 a 5)

| Pergunta | Média |
|---|---|
| Facilidade de uso | `< >` |
| Clareza das mensagens | `< >` |
| Rapidez | `< >` |
| Visual | `< >` |
| Uso no celular | `< >` |
| Usaria o app | `< >` |

### 6.3 Principais observações

`<resumo do que os testadores mais elogiaram e criticaram>`

## 7. Correções aplicadas

Ver [registro de correções](registro-de-correcoes.md). Resumo: `<n>` registros corrigidos, `<n>` melhorados, `<n>` fora do escopo.

## 8. Funcionalidades não implementadas

Itens sugeridos que estão fora do escopo do MVP: `<lista>`. Ficam registrados como funcionalidades não implementadas (fora do escopo do MVP).

## 9. Parecer final

`<Aprovado / Aprovado com ressalvas>`. Justificativa: `<texto curto relacionando os critérios da seção 3 com os resultados>`.
