# CLAUDE.md — AirPlan ✈️☁️

Contexto do projeto para o Claude Code. Leia este arquivo inteiro antes de escrever qualquer código.

---

## 1. Quem sou eu e o que é este projeto

- **Autor:** Lucas, estudante de **Engenharia de Software** (EAD, Cruzeiro do Sul Virtual).
- **Disciplina:** *Projeto Integrador Transdisciplinar em Engenharia de Software II* (PIT II).
- **Prazo final de entrega:** **17/11/2026, 23:59 (horário de Brasília).** Não há envio depois disso.
- **Nível:** sei JavaScript básico e banco de dados. Explique decisões não óbvias em 1–2 frases e prefira código simples e legível a código "esperto".
- **Objetivo pessoal:** entregar um projeto **completo, funcionando e bem documentado** dentro do prazo, sem inventar moda.

### O que é o AirPlan
O **AirPlan** é um gerenciador de tarefas no estilo **Kanban** (inspirado no Trello), com identidade visual de **céu, nuvens e aviação**.

- O usuário cria **quadros** (chamados na interface de "planos de voo").
- Cada quadro tem **colunas**, que são as etapas (padrão: **Embarque → Em voo → Pousou**).
- Cada coluna tem **cartões**, que são as tarefas.
- O usuário **arrasta cartões entre colunas** conforme as tarefas avançam.
- Cada usuário vê **somente os próprios quadros** (não há compartilhamento).

**Slogan:** *"Organize suas tarefas com a leveza de arrastar um cartão."*

---

## 2. A missão (o que a faculdade pede)

O PIT II tem 3 "situações-problema" que se complementam:

| Situação | O que fazer | Entregáveis |
|---|---|---|
| **1 — Planejamento** | Revisar/criar a documentação do projeto (o PIT I foi feito no papel e a ideia mudou, o que o material permite como "Kaizen") | UML (casos de uso, classes, sequência), protótipo de telas, modelo conceitual + lógico normalizado, **projeto físico do banco** + **dicionário de dados** |
| **2 — Codificação** | Construir o app de verdade | Front-end em HTML/CSS/JS, back-end em **MVC**, **testes** no front e no back, erros tratados, **app hospedado**, manual de uso, tudo no GitHub |
| **3 — Testes com usuários** | 5 colegas testam o app | Formulário de bugs com prints, correções aplicadas, **laudo de qualidade**, vídeo mostrando as mudanças |

### Critério de avaliação (10 pontos)
| Critério | Peso |
|---|---|
| Vídeo explicativo (narrado, mín. 5 min, só tela + voz) | 30% |
| Teste da solução (5 testadores) | 25% |
| Laudo de qualidade | 25% |
| **Codificação** | **20%** |

➡️ Código **limpo, funcionando e fácil de demonstrar** vale mais do que código sofisticado.
➡️ O envio passa pelo **SafeAssign** (antiplágio): toda a documentação deve ser original.

---

## 3. Condições obrigatórias do código (regras da faculdade)

1. **Front-end:** HTML, CSS e JavaScript.
2. **Back-end:** padrão de projeto **MVC** (indicado explicitamente no material).
3. **Linguagem do back-end:** Java, PHP, C#, .NET **ou Python**. ➜ Usamos **Python**.
4. **Front-end e back-end testados**, funcionais, completos e **com erros tratados**.
5. **Banco de dados:** SGBD **popular** e de fácil manutenção ("nada de SGBD obscuro"). ➜ **PostgreSQL**.
6. **Projeto físico do banco documentado** + **dicionário de dados**.
7. Tudo versionado no **GitHub**, com **uma pasta de documentação para cada situação-problema**.
8. **Link da solução funcionando** (app hospedado e acessível).
9. **Manual de uso** do sistema.
10. Modo de codificação declarado no template da faculdade: **Tradicional**.

---

## 4. Stack (decidida — não trocar sem me perguntar)

| Camada | Tecnologia | Observação |
|---|---|---|
| Front-end | **HTML5 + CSS3 + JavaScript puro (vanilla)** | **Proibido:** React, Vue, Angular, jQuery, Tailwind, Bootstrap ou qualquer framework/lib de UI |
| Back-end | **Python 3.12+ com Flask** | Micro-framework; estrutura MVC explícita em pastas |
| Banco | **PostgreSQL 16+** | **Só Supabase** (sem Postgres local). O projeto atual é o ambiente de desenvolvimento; na entrega o banco é zerado e vira produção |
| Driver | **psycopg 3** (`psycopg[binary]`) | SQL escrito à mão, **sem ORM** (fica mais didático pro dicionário de dados) |
| Senhas | `werkzeug.security` (`generate_password_hash` / `check_password_hash`) | Nunca guardar senha em texto puro |
| Sessão | Cookie de sessão do Flask (`HttpOnly`, `SameSite=Lax`, `Secure` em produção) | Front e back na **mesma origem**, sem CORS |
| Testes back | **Pytest** | Roda no mesmo banco Supabase de desenvolvimento (sem banco de teste separado) |
| Testes front | **`node --test`** (runner nativo do Node, sem dependências) | Testa funções puras de `views/js/utils/` |
| Servidor (prod) | **gunicorn** | |
| Hospedagem | **Render** (app Flask, plano grátis) + **Supabase** (Postgres, plano grátis) | Ver seção 12 |
| Config | `python-dotenv` + arquivo `.env` (no `.gitignore`) | Fornecer `.env.example` |

### Regra de ouro sobre o Supabase
Usar o Supabase **somente como banco PostgreSQL**, conectando pelo Flask via `DATABASE_URL`.
**NÃO** usar `supabase-js`, Supabase Auth, a API REST automática nem as Edge Functions. O front **nunca** fala direto com o banco. Sem o Flask no meio, não existe back-end MVC e o projeto perde o critério de codificação.

---

## 5. Arquitetura MVC e estrutura de pastas

```
airplan/
├── app.py                    # cria o app Flask, registra blueprints, error handlers
├── config.py                 # lê variáveis do .env
├── db.py                     # conexão psycopg (pool simples) + helpers de transação
├── models/                   # M — acesso a dados (SQL puro), validações de domínio
│   ├── usuario_model.py
│   ├── quadro_model.py
│   ├── coluna_model.py
│   ├── cartao_model.py
│   ├── validacoes.py         # regras dos campos (mesmas mensagens do front)
│   └── erros.py              # ErroValidacao / ErroConflito / NaoEncontrado (sem HTTP)
├── controllers/              # C — rotas Flask (blueprints): recebem a requisição, chamam o model, devolvem JSON/HTML
│   ├── auth_controller.py    # /api/auth/*
│   ├── usuario_controller.py # /api/usuarios/*
│   ├── quadro_controller.py  # /api/quadros/*
│   ├── coluna_controller.py  # /api/quadros/<id>/colunas e /api/colunas/*
│   ├── cartao_controller.py  # /api/colunas/<id>/cartoes e /api/cartoes/*
│   ├── pagina_controller.py  # serve as páginas HTML + proteção de rotas + 404
│   ├── sessao.py             # login_obrigatorio, iniciar/encerrar sessão
│   ├── requisicao.py         # ler_json()
│   ├── tratador_erros.py     # erros de domínio → 400/404/409/500 no formato padrão
│   └── json_provider.py      # datas em ISO (prazo "2026-11-17")
├── views/                    # V — tudo que o usuário vê
│   ├── templates/            # HTML de cada tela (Jinja só para montar o esqueleto; sem lógica)
│   │   ├── base.html, base_auth.html, _header.html, _toasts.html, _confirmar.html, _macros.html
│   │   ├── login.html, cadastro.html, quadros.html, quadro.html, perfil.html, 404.html
│   └── static/
│       ├── css/
│       │   ├── tokens.css    # variáveis CSS (cores, raios, sombras, fonte)
│       │   ├── base.css      # reset, botões, inputs, toasts, modais, menus, skeleton
│       │   ├── header.css
│       │   └── <tela>.css    # auth, quadros, quadro, perfil, erro404
│       ├── js/
│       │   ├── api.js        # wrapper do fetch (JSON, tratamento de erro, 401 → /login)
│       │   ├── header.js, sessao.js
│       │   ├── ui/           # toast, modal (focus trap), confirmar, menu, botao, formulario, campo-senha, estados, edicao-no-lugar
│       │   ├── utils/        # funções PURAS e testáveis (validacoes, prazo, senha, texto, mensagens, kanban)
│       │   ├── quadros/      # modal Novo/Renomear quadro
│       │   ├── quadro/       # Kanban: render, colunas, modal-cartao, arrastar, titulo, pontos
│       │   └── <tela>.js     # login, cadastro, quadros, quadro, perfil
│       └── img/              # assets copiados do protótipo
├── database/
│   ├── schema.sql            # CREATE TABLE ...
│   └── seed.sql              # usuário e quadros de exemplo
├── tests/
│   ├── back/                 # pytest
│   └── front/                # node --test
├── docs/
│   ├── situacao-1/           # UML, protótipo, modelo conceitual/lógico, dicionário de dados
│   ├── situacao-2/           # manual de uso, prints, decisões técnicas
│   └── situacao-3/           # template de teste, 5 laudos, correções, laudo de qualidade
├── prototipo/                # bundle do Claude Design (só referência, não é servido)
├── requirements.txt
├── render.yaml
├── .env.example
├── .gitignore
└── README.md
```

**Regras do MVC aqui:**
- **Controller nunca escreve SQL.** Model nunca lê `request` nem devolve resposta HTTP.
- Toda rota de API verifica a sessão e se o recurso **pertence ao usuário logado** (senão, 404, para não revelar que existe).
- No README e no vídeo, a estrutura de pastas é o que "prova" o MVC. Mantenha-a limpa.

---

## 6. Banco de dados (PostgreSQL)

**Entidades:** `usuario` 1:N `quadro` 1:N `coluna` 1:N `cartao` (exclusão em cascata).

```sql
CREATE TABLE usuario (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome        VARCHAR(100) NOT NULL CHECK (char_length(trim(nome)) >= 2),
  email       VARCHAR(150) NOT NULL UNIQUE,          -- sempre salvo em minúsculas
  senha_hash  VARCHAR(255) NOT NULL,
  criado_em   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE quadro (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  titulo      VARCHAR(100) NOT NULL CHECK (char_length(trim(titulo)) >= 1),
  usuario_id  INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE coluna (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  titulo      VARCHAR(50) NOT NULL CHECK (char_length(trim(titulo)) >= 1),
  posicao     INTEGER NOT NULL CHECK (posicao >= 0),
  quadro_id   INTEGER NOT NULL REFERENCES quadro(id) ON DELETE CASCADE,
  criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cartao (
  id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  titulo        VARCHAR(100) NOT NULL CHECK (char_length(trim(titulo)) >= 1),
  descricao     VARCHAR(2000),
  prazo         DATE,
  cor_etiqueta  VARCHAR(10) CHECK (cor_etiqueta IN ('verde','amarelo','laranja','vermelho','roxo','azul')),
  posicao       INTEGER NOT NULL CHECK (posicao >= 0),
  coluna_id     INTEGER NOT NULL REFERENCES coluna(id) ON DELETE CASCADE,
  criado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_quadro_usuario ON quadro(usuario_id);
CREATE INDEX idx_coluna_quadro  ON coluna(quadro_id, posicao);
CREATE INDEX idx_cartao_coluna  ON cartao(coluna_id, posicao);
```

- Ao **criar um quadro**, criar na mesma transação as 3 colunas padrão: `Embarque` (0), `Em voo` (1), `Pousou` (2).
- `posicao` começa em 0 e é **contínua** (0, 1, 2…). Ao mover ou excluir, reordenar na mesma transação.
- `seed.sql`: usuário **Lucas Santos / lucas@email.com / senha `voo12345`** (gerar o hash em Python) e os 3 quadros de exemplo do protótipo (`AirPlan App.dc.html`, método `semente()`). Prazos relativos a `CURRENT_DATE`.
- O **dicionário de dados** (`docs/situacao-1/dicionario-de-dados.md`) deve listar, para cada coluna: nome, tipo, tamanho, obrigatório, chave, domínio/regra (os `CHECK`) e descrição.

---

## 7. API REST

Todas as rotas `/api/*` recebem e devolvem **JSON**.

**Formato de erro padrão:**
```json
{ "erro": "Mensagem amigável em português", "campos": { "email": "Este e-mail já está cadastrado" } }
```
`campos` é opcional (usado em erros de validação de formulário).

**Status:** `200` ok · `201` criado · `204` sem conteúdo · `400` validação · `401` não logado · `404` não existe/não é seu · `409` conflito (e-mail duplicado) · `500` erro inesperado (logar no servidor, mensagem genérica pro usuário).

| Método | Rota | Corpo | Resposta |
|---|---|---|---|
| POST | `/api/auth/cadastro` | `{nome, email, senha}` | `201 {id, nome, email}` + inicia sessão |
| POST | `/api/auth/login` | `{email, senha}` | `200 {id, nome, email}` · `401 {"erro":"E-mail ou senha incorretos"}` |
| POST | `/api/auth/logout` | — | `204` |
| GET | `/api/usuarios/me` | — | `{id, nome, email}` |
| PUT | `/api/usuarios/me` | `{nome}` | `{id, nome, email}` |
| PUT | `/api/usuarios/me/senha` | `{senha_atual, nova_senha}` | `204` · `400` senha atual incorreta / igual à atual |
| GET | `/api/quadros` | — | `[{id, titulo, total_colunas, total_cartoes}]` |
| POST | `/api/quadros` | `{titulo}` | `201 {id, titulo}` (já com as 3 colunas) |
| GET | `/api/quadros/{id}` | — | `{id, titulo, colunas:[{id, titulo, posicao, cartoes:[{id, titulo, descricao, prazo, cor_etiqueta, posicao}]}]}` |
| PUT | `/api/quadros/{id}` | `{titulo}` | `{id, titulo}` |
| DELETE | `/api/quadros/{id}` | — | `204` |
| POST | `/api/quadros/{id}/colunas` | `{titulo}` | `201 {id, titulo, posicao}` (vai pro final) |
| PUT | `/api/colunas/{id}` | `{titulo}` | `{id, titulo, posicao}` |
| DELETE | `/api/colunas/{id}` | — | `204` (reordena as restantes) |
| POST | `/api/colunas/{id}/cartoes` | `{titulo}` | `201 {cartao}` (vai pro final da coluna) |
| PUT | `/api/cartoes/{id}` | `{titulo, descricao, prazo, cor_etiqueta, coluna_id?}` | `{cartao}` (se `coluna_id` mudar, vai pro final da nova coluna) |
| DELETE | `/api/cartoes/{id}` | — | `204` |
| PUT | `/api/cartoes/{id}/mover` | `{coluna_id, posicao}` | `{cartao}` — move e **reordena origem e destino na mesma transação**; a coluna de destino tem que ser do mesmo quadro |

**Validações no back-end** (as mesmas do front — o back é a fonte da verdade):
- Nome: 2–100 caracteres (após `trim`).
- E-mail: formato válido, até 150, único (comparação sem diferenciar maiúsculas).
- Senha: mínimo 8 caracteres, com pelo menos 1 letra e 1 número.
- Títulos: obrigatórios após `trim`; quadro e cartão até 100, coluna até 50.
- Descrição: até 2000. Prazo: data válida `YYYY-MM-DD` ou `null`. Cor: uma das 6 ou `null`.

**Páginas (servidas pelo `pagina_controller`):** `/` → redireciona · `/login` · `/cadastro` · `/quadros` · `/quadros/<id>` · `/perfil` · qualquer outra → `404.html`.
- Não logado acessando página interna → redireciona para `/login`.
- Logado acessando `/login` ou `/cadastro` → redireciona para `/quadros`.
- `/quadros/<id>` de outro usuário ou inexistente → `404.html`.

---

## 8. O protótipo (fonte da verdade visual)

O protótipo foi feito no **Claude Design** e está em `prototipo/` (bundle de handoff).

- **Arquivo principal:** `prototipo/project/AirPlan App.dc.html`. Ele importa as telas abaixo. Leia-o inteiro e siga os imports.
- Os arquivos `.dc.html` usam uma sintaxe de template parecida com React (`{{ }}`, `<sc-if>`, `<sc-for>`, `<dc-import>`, `class Component extends DCLogic`). **Não copie essa estrutura.** Recrie o **resultado visual** pixel a pixel em HTML/CSS/JS puro.
- Todas as medidas, cores, textos, estados e comportamentos estão no código-fonte. Leia o HTML/CSS em vez de tirar screenshot.

| Arquivo do protótipo | Tela / componente no app |
|---|---|
| `AirPlanAuth.dc.html` | `login.html` e `cadastro.html` (prop `modo`) |
| `AirPlanHangar.dc.html` | `quadros.html` + modais Novo/Renomear quadro |
| `AirPlanKanban.dc.html` | `quadro.html` + modal Detalhe do Cartão + drag and drop |
| `AirPlanPerfil.dc.html` | `perfil.html` |
| `AirPlan404.dc.html` | `404.html` |
| `AirPlanHeader.dc.html` | header global (Jinja include) |
| `AirPlanConfirmar.dc.html` | modal de confirmação reutilizável (`ui.js`) |
| `AirPlanToast.dc.html` | toast (`ui.js`) |
| `AirPlanGuia.dc.html` | guia de estilo (referência de tokens e componentes) |
| `AirPlan.dc.html` | canvas com todas as telas em todos os estados (referência) |
| `assets/*.png` | copiar para `views/static/img/` |

### O que é SÓ do protótipo e NÃO vai para o app
- A **barra escura do topo** (mostra a senha de teste, "Ir para…", "Reiniciar demo").
- **localStorage** guardando usuários, senhas e quadros → no app, tudo vem da API/PostgreSQL.
- Os `setTimeout` de 700–1400 ms que **simulam** carregamento → no app, o loading dura o tempo real do `fetch`.
- Checagem de "e-mail já cadastrado" no front → vem da API (`409`).
- Os props de "estado" (`estado`, `modal`, `falharMover`…) que existem só para mostrar variações no canvas.

### Correção conhecida (aplicar no app)
No protótipo, todos os menus usam o mesmo atributo `data-menu-area` para detectar clique fora, o que deixa **dois menus abertos ao mesmo tempo** (ex.: avatar + "⋯" de um quadro). No app: **só um menu aberto por vez** e o clique fora é checado contra o próprio elemento do menu (`menu.contains(e.target)`). Esc fecha o menu e devolve o foco ao botão que o abriu.

---

## 9. Design (tokens)

Fonte: **Nunito** (Google Fonts, pesos 400/600/700/800), fallback `system-ui, sans-serif`.

```css
:root {
  --ceu-topo: #5AB2F0;   --ceu-base: #E8F5FF;
  --primaria: #1F6FC9;   --primaria-hover: #185AA3;
  --nuvem: #FFFFFF;      --nuvem-borda: #D6E8F7;
  --texto: #1E2A3A;      --texto-suave: #5B6B7F;
  --sucesso: #2EAD6B;    --alerta: #F5A524;
  --erro: #E5484D;       --erro-texto: #C42F35;   --perigo: #D13B40;
  --sombra: 0 4px 12px rgba(30,42,58,.08);
  --sombra-elevada: 0 12px 32px rgba(30,42,58,.18);
  --raio-card: 10px; --raio-coluna: 16px; --raio-modal: 20px; --raio-botao: 10px; --raio-input: 8px;
}
```
**Etiquetas:** verde `#2EAD6B` · amarelo `#F5C524` · laranja `#F5822A` · vermelho `#E5484D` · roxo `#8B5CF6` · azul `#1F6FC9`.

**Badge de prazo:** normal (fundo `#EEF3F8`, texto `#4A5A6E`) · vence em ≤ 2 dias (fundo `#FEF0D6`, texto `#8A5300`) · vencido (fundo `#FDE8E8`, texto `#B4262B`, texto "Atrasado · dd mmm"). **Use sempre a data real** (`new Date()`), nunca uma data fixa.

**Responsividade:** desktop ≥ 1024 px (grid de 4 quadros) · tablet 768–1023 (grid de 2) · mobile < 768 (grid de 1; Kanban com uma coluna de 85% por vez + `scroll-snap` + pontinhos indicadores; **drag and drop desligado**, use "Mover para" no modal do cartão; modais em tela cheia).

**Animações:** respeitar `prefers-reduced-motion`.

---

## 10. Regras de UX (não podem faltar — os testadores vão procurar)

- **Todo formulário:** label visível, mensagem de erro em vermelho abaixo do campo (`aria-describedby`), borda vermelha, foco vai para o primeiro campo com erro.
- **Todo botão que chama a API:** fica desabilitado + spinner + texto alterado ("Decolando…", "Criando conta…", "Salvando…", "Excluindo…") até a resposta. Nada de clique duplo.
- **Toda ação tem feedback** via toast (até 3 empilhados, somem em 4 s, botão fechar, `aria-live`):
  - Sucesso: "Bem-vindo a bordo, {nome}! ✈️" · "Quadro criado" · "Quadro renomeado" · "Quadro excluído" · "Coluna criada" · "Coluna renomeada" · "Coluna excluída" · "Cartão salvo" · "Cartão excluído" · "Dados atualizados" · "Senha alterada com sucesso"
  - Info: "Até a próxima viagem! 👋" (ao sair)
  - Erro: "Não foi possível mover o cartão" · "O título do quadro não pode ficar vazio" · "O título da coluna não pode ficar vazio" · "Não foi possível conectar. Tente novamente."
- **Toda exclusão** pede confirmação (modal "Tem certeza?", botão Cancelar com foco padrão). Os textos tratam singular e plural ("seu único cartão", "A única coluna e 1 cartão").
- **Modal do cartão com alterações não salvas** → "Descartar alterações?" antes de fechar.
- **Drag and drop otimista:** move na tela na hora; se a API falhar, **volta o cartão para a posição original** + toast de erro.
- **Estados de tela:** carregando (skeleton), vazio (mascote + texto + botão), erro (mensagem + "Tentar novamente") e preenchido.
- **Sessão expirada (401)** em qualquer chamada → redireciona para `/login`.
- **Acessibilidade:** foco visível em tudo, modais com `role="dialog"`/`aria-modal` + focus trap + retorno do foco, Enter abre cartão, cor nunca é a única informação.

---

## 11. Testes

### Back-end (Pytest) — `tests/back/`
- Usa o **mesmo banco** do `.env` (`DATABASE_URL`, Supabase de desenvolvimento). Decisão do Lucas: projeto de faculdade, sem ambiente de teste separado.
- Antes da suíte, as tabelas são recriadas a partir de `database/schema.sql`; cada teste começa com o banco vazio; ao final, o `seed.sql` é aplicado de novo (a conta de exemplo volta).
- Usar o `app.test_client()` do Flask.
- Cobrir no mínimo:
  - Cadastro (sucesso, e-mail duplicado `409`, validações `400`), login (sucesso, senha errada `401`), logout.
  - Rotas protegidas sem sessão → `401`.
  - **Isolamento:** usuário A não acessa nem altera o quadro do usuário B (`404`).
  - CRUD de quadro (criar já gera 3 colunas), coluna e cartão.
  - Mover cartão: entre colunas, dentro da mesma coluna, posições continuam contínuas, coluna de outro quadro → erro.
  - Exclusão em cascata.
  - Alterar senha (atual incorreta, igual à atual, sucesso).

### Front-end (`node --test`) — `tests/front/`
- Testar as **funções puras** de `views/static/js/utils/`:
  - `validacoes.js`: nome, e-mail, senha, títulos.
  - `prazo.js`: status (normal / em breve / atrasado) e formato "dd mmm", recebendo a data de hoje por parâmetro.
  - `senha.js`: força da senha (fraca / média / forte).
- Por isso, essas funções **não podem tocar no DOM** e devem ser exportadas como ES modules.

### Comandos
```bash
pytest -v
node --test "tests/front/**/*.test.js"   # no Node 24, passar a pasta sozinha não funciona; use o glob (= npm run test:front)
```

---

## 12. Ambiente e deploy

### Desenvolvimento (PC do Lucas + Supabase)
**Não usar o PostgreSQL instalado no PC.** O banco é sempre o Supabase (projeto `svuhxnxkzyjxxboibmsh`, região us-east-1); o Lucas visualiza pelo DataGrip. O MCP do Supabase está configurado em `.mcp.json`.
```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # colar a connection string do Session pooler
npm start                   # = flask --app app run --debug
```
`schema.sql` e `seed.sql` são aplicados pelo MCP, pelo SQL Editor do Supabase ou pelo DataGrip.

`.env.example`:
```env
FLASK_SECRET_KEY=troque-por-uma-chave-aleatoria
DATABASE_URL=postgresql://postgres.SEU_PROJETO:SUA_SENHA@aws-0-us-east-1.pooler.supabase.com:5432/postgres
FLASK_ENV=development
```

### Produção: Render (app) + Supabase (banco)
- **Render (Web Service, plano grátis):** build `pip install -r requirements.txt`, start `gunicorn app:app`. Configurar `FLASK_SECRET_KEY` e `DATABASE_URL` nas variáveis de ambiente. Versionar um `render.yaml`.
  - O plano grátis **dorme após 15 min sem acesso** e leva **~1 min para acordar**. Avisar isso no README e no manual de uso.
- **Supabase (Postgres, plano grátis):** usar a connection string do **Supavisor em modo session** (host `*.pooler.supabase.com`, porta **5432**), porque a conexão direta usa IPv6 e o Render precisa de IPv4. Rodar `schema.sql` e `seed.sql` pelo SQL Editor do Supabase.
  - O plano grátis **pausa o projeto após 7 dias sem uso**. Até sair a nota, o Lucas precisa acessar pelo menos 1x por semana.
- O `db.py` deve funcionar com as duas URLs (local e Supabase) sem mudar código, e exigir SSL quando a URL não for `localhost`.

---

## 13. Convenções

- **Idioma:** nomes de variáveis, funções, tabelas e rotas em **português, sem acento** (`quadro`, `cartao`, `criar_quadro`, `posicao`). Textos da interface em **português do Brasil** com acento.
- **Python:** PEP 8, funções pequenas, docstring curta em português nas funções de model e controller.
- **JS:** ES modules (`type="module"`), `const`/`let`, `async/await`, sem variáveis globais soltas. Nada de `innerHTML` com dados do usuário (usar `textContent` ou criar elementos), para evitar XSS.
- **SQL:** sempre com parâmetros (`%s`), **nunca** concatenar strings (SQL injection).
- **Commits:** Conventional Commits em português: `feat: drag and drop de cartões`, `fix: plural na exclusão de coluna`, `docs: dicionário de dados`, `test: mover cartão entre colunas`.
- **Não adicionar dependências** além das listadas sem perguntar.

---

## 14. Fora do escopo (NÃO implementar)

Compartilhamento de quadros, múltiplos membros, comentários, anexos/upload, checklists no cartão, notificações, busca, modo escuro, login social, **recuperação de senha por e-mail**, arquivamento, favoritos, histórico de atividades, reordenar colunas, capa/cor por quadro e qualquer integração de pagamento.

Se algo disso aparecer como sugestão dos testadores, vai para o laudo como "funcionalidade não implementada (fora do escopo do MVP)".

---

## 15. Ordem de trabalho sugerida

1. Esqueleto do projeto (pastas, `app.py`, `config.py`, `db.py`, `requirements.txt`, `.env.example`, `.gitignore`, README inicial).
2. `schema.sql` + `seed.sql` + dicionário de dados.
3. Models + testes Pytest de cada model/rota (auth → quadro → coluna → cartão → mover).
4. Controllers + páginas protegidas.
5. CSS base (tokens, botões, inputs, toasts, modais, skeleton) seguindo o protótipo.
6. Telas na ordem: Login/Cadastro → Meus Quadros → Quadro Kanban → Perfil → 404.
7. Utils do front + testes `node --test`.
8. Deploy (Render + Supabase) e teste do link público.
9. Manual de uso (`docs/situacao-2/manual-de-uso.md`) com prints.
10. Material da situação 3: template de teste para os colegas e estrutura do laudo de qualidade.

**Antes de começar cada etapa, me diga em 1–2 frases o que vai fazer. Ao terminar, rode os testes e me mostre o resultado.**

---

## 16. Checklist final de entrega (17/11)

- [ ] App no ar (Render + Supabase) e testado pelo link público
- [ ] Repositório público no GitHub com código, `docs/situacao-1`, `docs/situacao-2` e `docs/situacao-3`
- [ ] `pytest` e `node --test` passando
- [ ] README com: descrição, stack, como rodar local, como testar, link do app, aviso do "primeiro acesso lento"
- [ ] Manual de uso com prints
- [ ] Dicionário de dados + diagramas UML
- [ ] 5 testes de colegas + laudo de qualidade + correções aplicadas
- [ ] Vídeo narrado da solução (mín. 5 min) + vídeo das modificações (até 5 min)
- [ ] Template da faculdade preenchido (linguagem: Python · banco: PostgreSQL · hospedagem: Render + Supabase · plataforma: Web · modo: Tradicional · links)
