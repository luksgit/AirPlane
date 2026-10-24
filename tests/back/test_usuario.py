"""Testes do perfil: ver dados, trocar o nome e alterar a senha."""


def test_ver_perfil_do_usuario_logado(cadastrar):
    cliente = cadastrar()

    resposta = cliente.get("/api/usuarios/me")

    assert resposta.status_code == 200
    assert resposta.get_json() == {"id": 1, "nome": "Ana Souza", "email": "ana@email.com"}


def test_perfil_mostra_somente_o_proprio_usuario(cadastrar):
    cadastrar(nome="Ana Souza", email="ana@email.com")
    cliente_bruno = cadastrar(nome="Bruno Lima", email="bruno@email.com")

    assert cliente_bruno.get("/api/usuarios/me").get_json()["email"] == "bruno@email.com"


def test_perfil_de_conta_excluida_encerra_a_sessao(cadastrar, conexao_teste):
    cliente = cadastrar()
    conexao_teste.execute("DELETE FROM usuario")

    assert cliente.get("/api/usuarios/me").status_code == 401


# --- Nome -------------------------------------------------------------------

def test_atualizar_nome(cadastrar):
    cliente = cadastrar()

    resposta = cliente.put("/api/usuarios/me", json={"nome": "  Ana Paula Souza "})

    assert resposta.status_code == 200
    assert resposta.get_json()["nome"] == "Ana Paula Souza"
    assert cliente.get("/api/usuarios/me").get_json()["nome"] == "Ana Paula Souza"


def test_atualizar_nome_invalido_retorna_400(cadastrar):
    cliente = cadastrar()

    resposta = cliente.put("/api/usuarios/me", json={"nome": "A"})

    assert resposta.status_code == 400
    assert resposta.get_json()["campos"] == {"nome": "O nome deve ter pelo menos 2 caracteres"}
    assert cliente.get("/api/usuarios/me").get_json()["nome"] == "Ana Souza"


# --- Senha ------------------------------------------------------------------

def test_alterar_senha_com_sucesso(cadastrar, app):
    cliente = cadastrar()

    resposta = cliente.put(
        "/api/usuarios/me/senha", json={"senha_atual": "senha1234", "nova_senha": "novaSenha99"}
    )

    assert resposta.status_code == 204
    outro = app.test_client()
    assert outro.post("/api/auth/login", json={"email": "ana@email.com", "senha": "senha1234"}).status_code == 401
    assert outro.post("/api/auth/login", json={"email": "ana@email.com", "senha": "novaSenha99"}).status_code == 200


def test_alterar_senha_com_senha_atual_incorreta(cadastrar):
    cliente = cadastrar()

    resposta = cliente.put(
        "/api/usuarios/me/senha", json={"senha_atual": "errada123", "nova_senha": "novaSenha99"}
    )

    assert resposta.status_code == 400
    assert resposta.get_json()["campos"] == {"senha_atual": "Senha atual incorreta"}


def test_alterar_senha_igual_a_atual(cadastrar):
    cliente = cadastrar()

    resposta = cliente.put(
        "/api/usuarios/me/senha", json={"senha_atual": "senha1234", "nova_senha": "senha1234"}
    )

    assert resposta.status_code == 400
    assert resposta.get_json()["campos"] == {"nova_senha": "A nova senha deve ser diferente da atual"}


def test_alterar_senha_valida_campos(cadastrar):
    cliente = cadastrar()

    resposta = cliente.put("/api/usuarios/me/senha", json={"senha_atual": "", "nova_senha": "fraca"})

    assert resposta.status_code == 400
    assert resposta.get_json()["campos"] == {
        "senha_atual": "Informe sua senha atual",
        "nova_senha": "A senha deve ter no mínimo 8 caracteres, com letras e números",
    }
