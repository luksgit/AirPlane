# Decisões técnicas: AirPlan

Este documento explica **como** o AirPlan foi construído e **por quê**, atendendo às condições da Situação-Problema 2.

## 1. Stack

| Camada | Tecnologia | Motivo |
|---|---|---|
| Front-end | HTML5, CSS3 e JavaScript puro (ES modules) | Exigência da disciplina; sem frameworks, o código mostra o que cada parte faz |
| Back-end | Python 3.12 + Flask | Linguagem permitida pela disciplina; o Flask é pequeno e deixa a estrutura MVC explícita em pastas |
| Banco | PostgreSQL 16+ (Supabase) | SGBD popular e de fácil manutenção; o Supabase oferece um Postgres gerenciado gratuito |
| Acesso ao banco | psycopg 3 com **SQL escrito à mão** (sem ORM) | O SQL fica visível e casa 1 para 1 com o dicionário de dados |
| Senhas | `werkzeug.security` (hash scrypt) | A senha nunca é guardada; só o hash |
| Sessão | Cookie de sessão do Flask (`HttpOnly`, `SameSite=Lax`, `Secure` em produção) | Front e back na mesma origem: sem CORS e sem token no JavaScript |
| Testes | Pytest (back) e `node --test` (front) | Runners padrão das linguagens, sem dependências extras no front |
| Hospedagem | Vercel (app) + Supabase (banco) | Planos gratuitos suficientes para a avaliação; a Vercel publica a cada `git push` e não deixa o app "dormindo" por minutos |

## 2. Arquitetura MVC

```
models/        M: SQL e regras de negócio (não conhece HTTP)
controllers/   C: rotas Flask; recebem a requisição, chamam o model e devolvem JSON/HTML (não escrevem SQL)
views/         V: templates HTML (Jinja)
public/static/ V: CSS, JavaScript e imagens (na Vercel, entregues pela CDN)
```

- **Model** (`models/*_model.py`): cada função recebe o `usuario_id` do dono e filtra por ele, de modo que um usuário nunca alcança dados de outro. Erros de negócio são **exceções de domínio** (`ErroValidacao`, `ErroConflito`, `NaoEncontrado`), sem nenhum código HTTP.
- **Controller** (`controllers/*_controller.py`): blueprints do Flask. O `tratador_erros.py` traduz as exceções de domínio para `400`, `409` e `404` no formato `{ "erro": "...", "campos": {...} }`, e erros inesperados viram `500` com mensagem genérica (o detalhe vai só para o log).
- **View** (`views/`): o Jinja serve só para montar o esqueleto da página (header, toasts, peças `<template>`); os dados chegam pelo JavaScript via `fetch` na API REST.

### Organização do front-end

| Pasta | Responsabilidade |
|---|---|
| `js/api.js` | Único ponto que chama `fetch`: JSON, erros padronizados e 401 → `/login` |
| `js/ui/` | Componentes de interface reutilizáveis: toast, modal (focus trap), confirmar, menu, botão carregando, erros de formulário, campo de senha, edição no lugar |
| `js/utils/` | **Funções puras** (sem DOM): validações, prazo, força da senha, textos no singular/plural e operações do Kanban; são as funções testadas com `node --test` |
| `js/<tela>.js` | Um arquivo de entrada por tela (`login.js`, `quadros.js`, `quadro.js`, `perfil.js`…) |
| `js/quadro/` | Partes do Kanban: desenho, colunas, modal do cartão, arrastar e soltar, título e indicadores do celular |

## 3. Decisões importantes

### Posições contínuas e transações
Colunas e cartões guardam `posicao` (0, 1, 2…). Toda operação que tira ou põe um item (criar, excluir, mover) **renumera os vizinhos na mesma transação**, com commit ou rollback juntos. Assim, a ordem nunca fica com lacunas ou repetida.

### Concorrência no mover
Antes de mexer em posições, o `cartao_model` faz `SELECT … FOR UPDATE` na linha do **quadro**. Duas operações no mesmo quadro acontecem uma depois da outra. Como existe uma única trava por quadro, não há risco de *deadlock*.

### Drag and drop otimista
O front move o cartão na tela **antes** da resposta da API (`utils/kanban.js` devolve uma cópia nova do estado). Se a API falhar, a tela volta para a cópia anterior e mostra "Não foi possível mover o cartão". As regras de posição do front e do back são as mesmas, e as duas têm testes.

### Validação em dois lugares
O front valida para dar resposta imediata; o **back-end é a fonte da verdade** e repete todas as regras (`models/validacoes.py` e `js/utils/validacoes.js` têm as mesmas mensagens).

### Isolamento entre usuários
Toda rota da API verifica a sessão (`login_obrigatorio`) e todo SQL filtra pelo `usuario_id`. Pedir um quadro, coluna ou cartão de outro usuário devolve **404**, e não 403, para não revelar que o recurso existe.

### Segurança
- **SQL injection:** todo SQL usa parâmetros (`%s`); nunca há concatenação de texto do usuário.
- **XSS:** o JavaScript nunca usa `innerHTML` com dados do usuário; tudo entra via `textContent` ou clonando `<template>`.
- **CSRF:** o cookie é `SameSite=Lax` e a API só lê corpo `application/json`, que um formulário de outro site não consegue enviar.
- **Supabase:** o *Row Level Security* fica ligado sem políticas, o que bloqueia a API REST automática do Supabase. Só o Flask acessa o banco.

## 4. Tratamento de erros (resumo)

| Situação | Back-end | Front-end |
|---|---|---|
| Campo inválido | `400` com `campos` | Mensagem vermelha abaixo do campo, borda vermelha, foco no primeiro erro |
| E-mail já cadastrado | `409` | Erro no campo e-mail |
| Sem sessão | `401` | Redireciona para `/login` |
| Recurso de outro usuário / inexistente | `404` | Página "Turbulência!" ou toast |
| Erro inesperado | `500` genérico + log no servidor | Toast "Ocorreu um erro inesperado" |
| Sem internet | — | Toast "Não foi possível conectar. Tente novamente." |

## 5. Testes

| Suíte | Comando | O que cobre |
|---|---|---|
| Back-end (Pytest) | `pytest -v` | Cadastro, login e logout; rotas protegidas (401); isolamento entre usuários (404); CRUD de quadro, coluna e cartão; mover cartão (mesma coluna, entre colunas, posições contínuas, outro quadro); cascata; perfil e senha; páginas e redirecionamentos |
| Front-end (Node) | `npm run test:front` | Validações, selo de prazo, força da senha, textos singular/plural e operações do Kanban (mover, salvar, remover) |

> Os testes do back-end rodam no mesmo banco do desenvolvimento (Supabase). Eles recriam as tabelas no início e, no fim, aplicam o `seed.sql` de novo, deixando a conta de demonstração pronta.

## 6. Hospedagem

- **Vercel** (plano Hobby, grátis): o repositório do GitHub é importado e a Vercel detecta o Flask pelo `app.py`; cada `git push` na `main` gera um deploy. O app vira uma *Vercel Function* (sem gunicorn) e a versão do Python vem do `.python-version`. A Vercel só serve arquivos estáticos pela pasta `public/`, por isso o CSS, o JS e as imagens ficam em `public/static/` (o Flask usa a mesma pasta no computador, então as URLs `/static/...` não mudam). O `.vercelignore` deixa de fora o que não é servido (`prototipo/`, `docs/`, `tests/`). Depois de um tempo sem uso, a função desliga e o primeiro acesso leva alguns segundos.
- **Supabase** (Postgres grátis): conexão pelo *Session pooler* (porta 5432, IPv4). O `db.py` exige SSL sempre que a URL não é local. O plano grátis pausa o projeto depois de 7 dias sem uso.
