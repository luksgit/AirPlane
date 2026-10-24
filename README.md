# AirPlan ✈️☁️

> Organize suas tarefas com a leveza de arrastar um cartão.

O **AirPlan** é um gerenciador de tarefas no estilo Kanban, com identidade visual de céu, nuvens e aviação. Cada usuário cria seus **planos de voo** (quadros), divididos em **colunas** (etapas como *Embarque → Em voo → Pousou*) que guardam **cartões** (tarefas). Os cartões são arrastados entre as colunas conforme as tarefas avançam.

Projeto desenvolvido para a disciplina *Projeto Integrador Transdisciplinar em Engenharia de Software II* (Cruzeiro do Sul Virtual).

![Quadro Kanban do AirPlan](docs/situacao-2/prints/06-quadro-kanban.png)

## 🔗 Acesse

- **App:** `https://<link-do-app-na-vercel>`
- **Conta de demonstração:** `lucas@email.com` / senha `voo12345`

> ⏳ **Primeiro acesso:** o app fica no plano gratuito da Vercel. Depois de um tempo sem uso, a primeira página pode levar alguns segundos para abrir; em seguida, ele responde normalmente.

## Funcionalidades

- Cadastro, login e logout (senha com hash, sessão por cookie seguro)
- Quadros: criar (já com Embarque, Em voo e Pousou), renomear, excluir
- Colunas: criar, renomear, excluir
- Cartões: criar, editar título, descrição, prazo e etiqueta colorida, excluir
- **Arrastar e soltar** cartões entre colunas (no celular: "Mover para")
- Selo de prazo: normal, vence em breve (até 2 dias) e atrasado
- Perfil: alterar nome e senha
- Responsivo (desktop, tablet e celular), acessível por teclado e com `prefers-reduced-motion`

## Stack

| Camada | Tecnologia |
|---|---|
| Front-end | HTML5, CSS3 e JavaScript puro (ES modules), sem frameworks |
| Back-end | Python 3.12 + Flask, padrão **MVC** |
| Banco de dados | PostgreSQL (Supabase) com SQL escrito à mão (psycopg 3) |
| Testes | Pytest (back-end) e `node --test` (front-end) |
| Hospedagem | Vercel (app) + Supabase (banco) |

## Estrutura (MVC)

```
app.py            cria o app Flask e registra os controllers
config.py         configurações lidas do .env
db.py             conexão com o PostgreSQL e transações
models/           M: SQL e regras de negócio (usuario, quadro, coluna, cartao, validacoes, erros)
controllers/      C: rotas da API (/api/*) e das páginas; tratamento de erros
views/
  templates/      V: HTML das telas (Jinja só para montar o esqueleto)
public/static/    V: arquivos estáticos do navegador (na Vercel, servidos direto pela CDN)
  css/            estilos (tokens, base e um arquivo por tela)
  js/             um arquivo por tela + ui/ (componentes) + utils/ (funções puras) + quadro/ (Kanban)
  img/            imagens e mascote
database/         schema.sql (tabelas) e seed.sql (dados de exemplo)
tests/back/       testes do back-end (pytest)
tests/front/      testes do front-end (node --test)
docs/             documentação de cada situação-problema
prototipo/        protótipo de telas (apenas referência, não é servido)
```

## Como rodar localmente (Windows)

Pré-requisitos: Python 3.12+, Node 20+ (só para os testes do front) e um banco PostgreSQL (usamos o Supabase).

```powershell
npm run setup                # cria a .venv e instala as dependências Python
copy .env.example .env       # depois cole a sua DATABASE_URL no .env
```

Crie as tabelas e os dados de exemplo executando `database/schema.sql` e depois `database/seed.sql` no banco (pelo SQL Editor do Supabase ou por um cliente como o DataGrip).

```powershell
npm start                    # = .venv\Scripts\flask --app app run --debug
```

Acesse **http://127.0.0.1:5000**.

## Como testar

```powershell
npm run test:back            # pytest -v
npm run test:front           # node --test "tests/front/**/*.test.js"
npm test                     # os dois
```

> **Atenção:** os testes do back-end rodam no banco configurado no `.env` (o Supabase de desenvolvimento). Eles apagam todos os dados e, ao final, restauram os dados de exemplo do `seed.sql`.

### Atalhos npm

O `package.json` não instala nenhuma dependência JavaScript. Ele só guarda atalhos:

| Comando | O que faz |
|---|---|
| `npm run setup` | Cria a `.venv` e instala as dependências Python |
| `npm start` ou `npm run dev` | Sobe o servidor de desenvolvimento com recarga automática |
| `npm run prototipo` | Serve o protótipo de telas em http://localhost:8000 (só referência visual) |
| `npm test` | Roda os testes do back-end e do front-end |

## Deploy (Vercel + Supabase)

1. **Supabase:** no SQL Editor, execute `database/schema.sql` e `database/seed.sql`. Copie a connection string do **Session pooler** (porta 5432).
2. **Vercel:** *Add New → Project*, importe este repositório do GitHub. O Flask é detectado sozinho pelo `app.py` (a variável `app`), e a versão do Python vem do `.python-version`. Antes de clicar em *Deploy*, cadastre em *Environment Variables*:
   - `DATABASE_URL`: a connection string do Supabase;
   - `FLASK_SECRET_KEY`: uma chave aleatória (gere com `python -c "import secrets; print(secrets.token_hex(32))"`);
   - `FLASK_ENV`: `production` (liga o cookie de sessão `Secure`).
3. Acesse o link gerado pela Vercel e faça login com a conta de demonstração. Cada `git push` na `main` gera um deploy novo automaticamente.

> Na Vercel, o Flask vira uma *Vercel Function* e os arquivos de `public/` são entregues pela CDN, por isso o CSS, o JS e as imagens ficam em `public/static/`. As URLs (`/static/...`) são as mesmas no computador e na Vercel.

> O plano grátis do Supabase pausa o projeto depois de 7 dias sem uso: acesse o app pelo menos uma vez por semana até a avaliação.

## Documentação

| Situação-problema | Conteúdo |
|---|---|
| [Situação 1: Planejamento](docs/situacao-1/) | [Protótipo](docs/situacao-1/prototipo.md) · [Casos de uso](docs/situacao-1/uml-casos-de-uso.md) · [Classes](docs/situacao-1/uml-classes.md) · [Sequência](docs/situacao-1/uml-sequencia.md) · [Modelo de dados](docs/situacao-1/modelo-de-dados.md) · [Dicionário de dados](docs/situacao-1/dicionario-de-dados.md) |
| [Situação 2: Codificação](docs/situacao-2/) | [Manual de uso](docs/situacao-2/manual-de-uso.md) · [Decisões técnicas](docs/situacao-2/decisoes-tecnicas.md) |
| [Situação 3: Testes](docs/situacao-3/) | [Roteiro de teste](docs/situacao-3/roteiro-de-teste.md) · [Formulário de bugs](docs/situacao-3/formulario-de-bugs.md) · [Registro de correções](docs/situacao-3/registro-de-correcoes.md) · [Laudo de qualidade](docs/situacao-3/laudo-de-qualidade.md) |
