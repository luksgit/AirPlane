-- =============================================================
-- AirPlan: dados de exemplo (rodar depois do schema.sql)
-- Conta: lucas@email.com / senha voo12345
-- Os prazos são relativos à data de hoje (CURRENT_DATE), então
-- os selos "vence em breve" e "atrasado" sempre aparecem.
-- Pode ser executado de novo para restaurar a demonstração.
-- =============================================================

-- Remove a conta de exemplo (e, em cascata, seus quadros, colunas e cartões).
DELETE FROM usuario WHERE email = 'lucas@email.com';

DO $$
DECLARE
  v_usuario INTEGER;
  v_quadro  INTEGER;
  v_coluna  INTEGER;
BEGIN
  INSERT INTO usuario (nome, email, senha_hash)
  VALUES ('Lucas Santos', 'lucas@email.com',
          'scrypt:32768:8:1$QngyiR5X03wmEXVL$dc32653eed87d2cb8e26aa793ed4c91a73de724ff0d719e34e64f42800c121fcc33c45d4ae0f3c71481376d04cee1bfd6846046d40780fd40c421db2bf9bdc7f')
  RETURNING id INTO v_usuario;

  -- Quadro 1: PIT II – AirPlan ------------------------------------
  INSERT INTO quadro (titulo, usuario_id) VALUES ('PIT II – AirPlan', v_usuario) RETURNING id INTO v_quadro;

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Embarque', 0, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Revisar diagrama de classes', NULL, CURRENT_DATE + 1,  'roxo',     0, v_coluna),
    ('Criar dicionário de dados',   NULL, CURRENT_DATE + 14, 'azul',     1, v_coluna),
    ('Gravar vídeo narrado',        NULL, NULL,              'vermelho', 2, v_coluna);

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Em voo', 1, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Codificar API de cartões',
     'Implementar POST, PUT e DELETE em /api/cartoes e a rota PUT /api/cartoes/{id}/mover, validando coluna_id e posicao.',
     CURRENT_DATE + 8, 'laranja', 0, v_coluna),
    ('Layout da tela Kanban', NULL, CURRENT_DATE - 4, 'verde', 1, v_coluna);

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Pousou', 2, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Definir escopo do MVP',      NULL, NULL, 'verde', 0, v_coluna),
    ('Criar repositório no GitHub', NULL, NULL, NULL,    1, v_coluna),
    ('Escolher nome do app ✈️',     NULL, NULL, NULL,    2, v_coluna);

  -- Quadro 2: Treino da semana ------------------------------------
  INSERT INTO quadro (titulo, usuario_id) VALUES ('Treino da semana', v_usuario) RETURNING id INTO v_quadro;

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Embarque', 0, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Corrida leve de 5 km', NULL, CURRENT_DATE + 5, 'verde',   0, v_coluna),
    ('Treino de pernas',     NULL, NULL,             'laranja', 1, v_coluna);

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Em voo', 1, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Alongamento diário', '10 minutos ao acordar e antes de dormir.', NULL, 'azul', 0, v_coluna),
    ('Natação terça e quinta', NULL, NULL, NULL, 1, v_coluna);

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Pousou', 2, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Treino de costas', NULL, NULL, 'verde', 0, v_coluna);

  -- Quadro 3: Estudos de Banco de Dados ---------------------------
  INSERT INTO quadro (titulo, usuario_id) VALUES ('Estudos de Banco de Dados', v_usuario) RETURNING id INTO v_quadro;

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Embarque', 0, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Normalização até a 3FN', NULL, CURRENT_DATE + 6, 'roxo', 0, v_coluna),
    ('Exercícios de JOIN',     NULL, NULL,             NULL,   1, v_coluna);

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Em voo', 1, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Modelo ER do projeto', 'Entidades: usuario, quadro, coluna e cartao (1:N em cascata).', NULL, 'azul', 0, v_coluna);

  INSERT INTO coluna (titulo, posicao, quadro_id) VALUES ('Pousou', 2, v_quadro) RETURNING id INTO v_coluna;
  INSERT INTO cartao (titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id) VALUES
    ('Revisar chaves primárias e estrangeiras', NULL, NULL, 'verde', 0, v_coluna);
END $$;
