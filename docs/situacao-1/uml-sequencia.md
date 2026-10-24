# UML: Diagramas de sequência

Três fluxos que mostram as camadas do MVC conversando: **View** (navegador) → **Controller** (Flask) → **Model** (SQL) → **PostgreSQL**.

---

## 1. Entrar no sistema (UC02)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant V as View<br/>login.html + login.js
    participant C as auth_controller
    participant M as usuario_model
    participant BD as PostgreSQL

    U->>V: Digita e-mail e senha e clica em "Decolar"
    V->>V: Valida os campos (validacoes.js)
    alt campos inválidos
        V-->>U: Mostra o erro abaixo do campo e foca nele
    else campos válidos
        V->>V: Botão vira "Decolando…" (desabilitado)
        V->>C: POST /api/auth/login {email, senha}
        C->>M: autenticar(email, senha)
        M->>BD: SELECT ... FROM usuario WHERE email = %s
        BD-->>M: linha do usuário (ou nada)
        M->>M: check_password_hash(senha_hash, senha)
        alt e-mail ou senha incorretos
            M-->>C: None
            C-->>V: 401 {"erro": "E-mail ou senha incorretos"}
            V-->>U: Alerta vermelho e botão volta ao normal
        else credenciais corretas
            M-->>C: {id, nome, email}
            C->>C: session["usuario_id"] = id (cookie HttpOnly)
            C-->>V: 200 {id, nome, email}
            V-->>U: Abre /quadros
        end
    end
```

---

## 2. Criar um quadro (UC05)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant V as View<br/>quadros.js
    participant C as quadro_controller
    participant M as quadro_model
    participant BD as PostgreSQL

    U->>V: "Novo quadro" → digita o título → "Criar quadro"
    V->>C: POST /api/quadros {titulo}
    C->>C: login_obrigatorio (sem sessão → 401)
    C->>M: criar_quadro(usuario_id, titulo)
    M->>M: Valida o título (obrigatório, até 100)
    M->>BD: BEGIN
    M->>BD: INSERT INTO quadro ... RETURNING id, titulo
    M->>BD: INSERT INTO coluna (Embarque 0, Em voo 1, Pousou 2)
    M->>BD: COMMIT
    M-->>C: {id, titulo}
    C-->>V: 201 {id, titulo}
    V->>V: Guarda o toast "Quadro criado" para a próxima página
    V-->>U: Abre /quadros/{id} com as 3 colunas
```

---

## 3. Mover um cartão arrastando (UC12)

O movimento é **otimista**: a tela muda na hora e só volta atrás se a API falhar.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant V as View<br/>quadro/arrastar.js
    participant C as cartao_controller
    participant M as cartao_model
    participant BD as PostgreSQL

    U->>V: Arrasta o cartão e solta em outra coluna
    V->>V: antes = estado atual<br/>estado = moverCartao(...) e redesenha
    V->>C: PUT /api/cartoes/{id}/mover {coluna_id, posicao}
    C->>M: mover_cartao(usuario_id, id, coluna_id, posicao)
    M->>BD: BEGIN
    M->>BD: SELECT ... quadro FOR UPDATE (trava o quadro do usuário)
    alt cartão não é do usuário
        M-->>C: NaoEncontrado
        C-->>V: 404
    else coluna de outro quadro
        M-->>C: ErroValidacao
        C-->>V: 400
    else tudo certo
        M->>BD: UPDATE origem: posicao - 1 abaixo do cartão
        M->>BD: UPDATE destino: posicao + 1 a partir da nova posição
        M->>BD: UPDATE cartao SET coluna_id, posicao
        M->>BD: COMMIT
        M-->>C: cartão atualizado
        C-->>V: 200 {cartao}
    end
    alt resposta de erro ou sem conexão
        V->>V: estado = antes e redesenha
        V-->>U: Toast "Não foi possível mover o cartão"
    else 200
        V-->>U: Cartão continua na nova posição
    end
```
