-- =============================================================
-- AirPlan: projeto físico do banco de dados (PostgreSQL 16+)
-- Relacionamentos: usuario 1:N quadro 1:N coluna 1:N cartao
-- Excluir um registro pai apaga os filhos em cascata.
-- =============================================================

CREATE TABLE usuario (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome        VARCHAR(100) NOT NULL CHECK (char_length(trim(nome)) >= 2),
  email       VARCHAR(150) NOT NULL UNIQUE CHECK (email = lower(email)),  -- sempre salvo em minúsculas
  senha_hash  VARCHAR(255) NOT NULL,                                      -- hash scrypt (werkzeug), nunca a senha
  criado_em   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE quadro (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  titulo      VARCHAR(100) NOT NULL CHECK (char_length(trim(titulo)) >= 1),
  usuario_id  INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  criado_em   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE coluna (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  titulo      VARCHAR(50)  NOT NULL CHECK (char_length(trim(titulo)) >= 1),
  posicao     INTEGER      NOT NULL CHECK (posicao >= 0),                 -- ordem no quadro: 0, 1, 2…
  quadro_id   INTEGER      NOT NULL REFERENCES quadro(id) ON DELETE CASCADE,
  criado_em   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE cartao (
  id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  titulo        VARCHAR(100)  NOT NULL CHECK (char_length(trim(titulo)) >= 1),
  descricao     VARCHAR(2000),
  prazo         DATE,
  cor_etiqueta  VARCHAR(10)   CHECK (cor_etiqueta IN ('verde', 'amarelo', 'laranja', 'vermelho', 'roxo', 'azul')),
  posicao       INTEGER       NOT NULL CHECK (posicao >= 0),              -- ordem na coluna: 0, 1, 2…
  coluna_id     INTEGER       NOT NULL REFERENCES coluna(id) ON DELETE CASCADE,
  criado_em     TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- Índices das chaves estrangeiras, já na ordem em que as listas são exibidas.
CREATE INDEX idx_quadro_usuario ON quadro(usuario_id);
CREATE INDEX idx_coluna_quadro  ON coluna(quadro_id, posicao);
CREATE INDEX idx_cartao_coluna  ON cartao(coluna_id, posicao);

-- Segurança: o Supabase publica as tabelas do schema "public" numa API REST
-- automática. Ligar o RLS sem nenhuma política bloqueia esse acesso direto.
-- O Flask conecta como dono das tabelas, que não é afetado pelo RLS.
ALTER TABLE usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE quadro  ENABLE ROW LEVEL SECURITY;
ALTER TABLE coluna  ENABLE ROW LEVEL SECURITY;
ALTER TABLE cartao  ENABLE ROW LEVEL SECURITY;
