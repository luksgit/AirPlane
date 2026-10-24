# Dicionário de dados: AirPlan

**SGBD:** PostgreSQL 16+ (hospedado no Supabase em produção)
**Script de criação:** [`database/schema.sql`](../../database/schema.sql)
**Dados de exemplo:** [`database/seed.sql`](../../database/seed.sql)

## Visão geral

O banco possui quatro tabelas em uma hierarquia de propriedade. Cada nível pertence a exatamente um registro do nível acima:

```
usuario  1 ──── N  quadro  1 ──── N  coluna  1 ──── N  cartao
```

| Tabela | Representa | Na interface |
|---|---|---|
| `usuario` | Pessoa cadastrada no sistema | Conta / perfil |
| `quadro` | Conjunto de tarefas de um assunto | "Plano de voo" |
| `coluna` | Etapa de andamento dentro de um quadro | Ex.: Embarque, Em voo, Pousou |
| `cartao` | Tarefa individual | Cartão arrastável |

**Convenções adotadas**

- Nomes de tabelas e colunas em português, no singular, sem acento.
- Toda tabela tem chave primária substituta `id` (`INTEGER GENERATED ALWAYS AS IDENTITY`), gerada pelo banco.
- Toda tabela tem `criado_em` (`TIMESTAMPTZ`, com fuso horário) preenchido automaticamente com `now()`.
- Chaves estrangeiras usam `ON DELETE CASCADE`: ao excluir um quadro, por exemplo, suas colunas e cartões são excluídos junto, sem deixar registros órfãos.
- Campos de texto obrigatórios não aceitam valor só com espaços (regra `char_length(trim(...))`).
- Todas as tabelas têm *Row Level Security* ligado e sem políticas. Isso bloqueia o acesso direto pela API REST automática do Supabase, e o banco só é acessado através do back-end Flask.

**Legenda:** PK = chave primária · FK = chave estrangeira · UK = valor único

---

## Tabela `usuario`

Guarda as contas de acesso. O e-mail identifica o usuário no login; a senha nunca é armazenada, apenas o seu hash.

| Coluna | Tipo | Tamanho | Obrigatório | Chave | Domínio / regra | Descrição |
|---|---|---|---|---|---|---|
| `id` | INTEGER | — | Sim | PK | Gerado automaticamente (identity) | Identificador único do usuário |
| `nome` | VARCHAR | 100 | Sim | — | Mínimo de 2 caracteres desconsiderando espaços nas pontas | Nome exibido no cabeçalho e no perfil |
| `email` | VARCHAR | 150 | Sim | UK | Único; deve estar em minúsculas (`email = lower(email)`); formato validado pela aplicação | E-mail de login (não pode ser alterado após o cadastro) |
| `senha_hash` | VARCHAR | 255 | Sim | — | Hash scrypt gerado pelo `werkzeug.security`. A senha original deve ter ao menos 8 caracteres, com letra e número (validado pela aplicação) | Resultado do hash da senha; usado para conferir o login |
| `criado_em` | TIMESTAMPTZ | — | Sim | — | Padrão `now()` | Data e hora do cadastro |

## Tabela `quadro`

Cada quadro pertence a um único usuário, e só ele pode vê-lo ou alterá-lo.

| Coluna | Tipo | Tamanho | Obrigatório | Chave | Domínio / regra | Descrição |
|---|---|---|---|---|---|---|
| `id` | INTEGER | — | Sim | PK | Gerado automaticamente (identity) | Identificador único do quadro |
| `titulo` | VARCHAR | 100 | Sim | — | Não pode ser vazio nem só espaços | Nome do plano de voo |
| `usuario_id` | INTEGER | — | Sim | FK → `usuario.id` | `ON DELETE CASCADE` | Dono do quadro |
| `criado_em` | TIMESTAMPTZ | — | Sim | — | Padrão `now()` | Data e hora de criação; define a ordem de exibição |

**Regra de negócio:** ao criar um quadro, a aplicação cria na mesma transação três colunas padrão: `Embarque` (posição 0), `Em voo` (1) e `Pousou` (2).

## Tabela `coluna`

Etapas de um quadro, exibidas da esquerda para a direita conforme `posicao`.

| Coluna | Tipo | Tamanho | Obrigatório | Chave | Domínio / regra | Descrição |
|---|---|---|---|---|---|---|
| `id` | INTEGER | — | Sim | PK | Gerado automaticamente (identity) | Identificador único da coluna |
| `titulo` | VARCHAR | 50 | Sim | — | Não pode ser vazio nem só espaços | Nome da etapa |
| `posicao` | INTEGER | — | Sim | — | `>= 0`; sequência contínua (0, 1, 2…) dentro do quadro, mantida pela aplicação | Ordem da coluna no quadro |
| `quadro_id` | INTEGER | — | Sim | FK → `quadro.id` | `ON DELETE CASCADE` | Quadro ao qual a coluna pertence |
| `criado_em` | TIMESTAMPTZ | — | Sim | — | Padrão `now()` | Data e hora de criação |

**Regra de negócio:** uma coluna nova entra no final do quadro. Ao excluir uma coluna, as posições das restantes são renumeradas na mesma transação para continuarem sem lacunas.

## Tabela `cartao`

Tarefas. A posição define a ordem de cima para baixo dentro da coluna.

| Coluna | Tipo | Tamanho | Obrigatório | Chave | Domínio / regra | Descrição |
|---|---|---|---|---|---|---|
| `id` | INTEGER | — | Sim | PK | Gerado automaticamente (identity) | Identificador único do cartão |
| `titulo` | VARCHAR | 100 | Sim | — | Não pode ser vazio nem só espaços | Resumo da tarefa, exibido no cartão |
| `descricao` | VARCHAR | 2000 | Não | — | Até 2000 caracteres | Detalhes da tarefa; o cartão mostra um ícone quando há descrição |
| `prazo` | DATE | — | Não | — | Data válida ou nulo | Data limite. Gera o selo de prazo: normal, "vence em breve" (até 2 dias) ou "Atrasado" |
| `cor_etiqueta` | VARCHAR | 10 | Não | — | Um de: `verde`, `amarelo`, `laranja`, `vermelho`, `roxo`, `azul`, ou nulo | Cor da faixa de etiqueta no topo do cartão |
| `posicao` | INTEGER | — | Sim | — | `>= 0`; sequência contínua (0, 1, 2…) dentro da coluna, mantida pela aplicação | Ordem do cartão na coluna |
| `coluna_id` | INTEGER | — | Sim | FK → `coluna.id` | `ON DELETE CASCADE` | Coluna em que o cartão está |
| `criado_em` | TIMESTAMPTZ | — | Sim | — | Padrão `now()` | Data e hora de criação |

**Regras de negócio:**

- Um cartão novo entra no final da coluna.
- Ao mover um cartão (arrastar ou "Mover para"), as posições da coluna de origem e da de destino são renumeradas na mesma transação. A coluna de destino precisa pertencer ao mesmo quadro.
- Ao excluir um cartão, os cartões abaixo dele sobem uma posição.

---

## Índices

| Índice | Tabela | Colunas | Motivo |
|---|---|---|---|
| PK de cada tabela | todas | `id` | Criado automaticamente pela chave primária |
| `usuario_email_key` | `usuario` | `email` | Criado automaticamente pelo `UNIQUE`; acelera o login |
| `idx_quadro_usuario` | `quadro` | `usuario_id` | Listar os quadros de um usuário |
| `idx_coluna_quadro` | `coluna` | `quadro_id, posicao` | Listar as colunas de um quadro já ordenadas |
| `idx_cartao_coluna` | `cartao` | `coluna_id, posicao` | Listar os cartões de uma coluna já ordenados |

## Normalização

- **1FN:** todos os atributos são atômicos (não há listas nem campos multivalorados; as etiquetas, por exemplo, são um único valor por cartão).
- **2FN:** todas as chaves primárias são simples (`id`), então não existe dependência parcial.
- **3FN:** nenhum atributo não-chave depende de outro atributo não-chave. Totais como "quantidade de cartões de um quadro" não são armazenados; são calculados por consulta (`COUNT`), evitando redundância e inconsistência.
