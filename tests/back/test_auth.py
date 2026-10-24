"""Testes de cadastro, login, logout e proteção das rotas."""
import pytest

DADOS_VALIDOS = {"nome": "Ana Souza", "email": "ana@email.com", "senha": "senha1234"}


# --- Cadastro ---------------------------------------------------------------

def test_cadastro_cria_usuario_e_inicia_sessao(cliente):
    resposta = cliente.post("/api/auth/cadastro", json=DADOS_VALIDOS)

    assert resposta.status_code == 201
    assert resposta.get_json() == {"id": 1, "nome": "Ana Souza", "email": "ana@email.com"}
    assert cliente.get("/api/usuarios/me").status_code == 200


def test_cadastro_limpa_espacos_e_salva_email_em_minusculas(cliente):
    resposta = cliente.post(
        "/api/auth/cadastro",
        json={"nome": "  Ana Souza  ", "email": "  ANA@Email.COM ", "senha": "senha1234"},
    )

    assert resposta.status_code == 201
    assert resposta.get_json()["nome"] == "Ana Souza"
    assert resposta.get_json()["email"] == "ana@email.com"


def test_cadastro_nao_guarda_senha_em_texto_puro(cliente, conexao_teste):
    cliente.post("/api/auth/cadastro", json=DADOS_VALIDOS)

    senha_hash = conexao_teste.execute("SELECT senha_hash FROM usuario").fetchone()["senha_hash"]
    assert senha_hash != "senha1234"
    assert senha_hash.startswith("scrypt:")


def test_cadastro_com_email_duplicado_retorna_409(cliente):
    cliente.post("/api/auth/cadastro", json=DADOS_VALIDOS)

    resposta = cliente.post("/api/auth/cadastro", json={**DADOS_VALIDOS, "email": "ANA@email.com"})

    assert resposta.status_code == 409
    assert resposta.get_json()["campos"] == {"email": "Este e-mail já está cadastrado"}


@pytest.mark.parametrize(
    "campo, valor, mensagem",
    [
        ("nome", "", "Informe seu nome"),
        ("nome", "   ", "Informe seu nome"),
        ("nome", "A", "O nome deve ter pelo menos 2 caracteres"),
        ("nome", "A" * 101, "O nome deve ter no máximo 100 caracteres"),
        ("email", "", "Informe seu e-mail"),
        ("email", "ana.email.com", "Digite um e-mail válido"),
        ("email", "ana@email", "Digite um e-mail válido"),
        ("email", "a" * 141 + "@email.com", "O e-mail deve ter no máximo 150 caracteres"),
        ("senha", "", "Informe sua senha"),
        ("senha", "abc1234", "A senha deve ter no mínimo 8 caracteres, com letras e números"),
        ("senha", "somenteletras", "A senha deve ter no mínimo 8 caracteres, com letras e números"),
        ("senha", "12345678", "A senha deve ter no mínimo 8 caracteres, com letras e números"),
    ],
)
def test_cadastro_valida_campos(cliente, campo, valor, mensagem):
    resposta = cliente.post("/api/auth/cadastro", json={**DADOS_VALIDOS, campo: valor})

    assert resposta.status_code == 400
    assert resposta.get_json()["campos"] == {campo: mensagem}


def test_cadastro_sem_corpo_aponta_todos_os_campos(cliente):
    resposta = cliente.post("/api/auth/cadastro", data="isso não é JSON")

    assert resposta.status_code == 400
    assert set(resposta.get_json()["campos"]) == {"nome", "email", "senha"}


# --- Login e logout ---------------------------------------------------------

def test_login_com_dados_corretos(cadastrar, cliente):
    cadastrar()

    resposta = cliente.post("/api/auth/login", json={"email": "ana@email.com", "senha": "senha1234"})

    assert resposta.status_code == 200
    assert resposta.get_json()["email"] == "ana@email.com"
    assert cliente.get("/api/usuarios/me").status_code == 200


def test_login_nao_diferencia_maiusculas_no_email(cadastrar, cliente):
    cadastrar()

    resposta = cliente.post("/api/auth/login", json={"email": " ANA@Email.com ", "senha": "senha1234"})

    assert resposta.status_code == 200


@pytest.mark.parametrize(
    "email, senha",
    [
        ("ana@email.com", "senhaErrada1"),
        ("naoexiste@email.com", "senha1234"),
        ("", ""),
    ],
)
def test_login_invalido_retorna_401_com_mensagem_unica(cadastrar, cliente, email, senha):
    cadastrar()

    resposta = cliente.post("/api/auth/login", json={"email": email, "senha": senha})

    assert resposta.status_code == 401
    assert resposta.get_json() == {"erro": "E-mail ou senha incorretos"}
    assert cliente.get("/api/usuarios/me").status_code == 401


def test_logout_encerra_a_sessao(cadastrar):
    cliente = cadastrar()

    resposta = cliente.post("/api/auth/logout")

    assert resposta.status_code == 204
    assert cliente.get("/api/usuarios/me").status_code == 401


# --- Rotas protegidas -------------------------------------------------------

@pytest.mark.parametrize(
    "metodo, rota",
    [
        ("get", "/api/usuarios/me"),
        ("put", "/api/usuarios/me"),
        ("put", "/api/usuarios/me/senha"),
        ("get", "/api/quadros"),
        ("post", "/api/quadros"),
        ("get", "/api/quadros/1"),
        ("put", "/api/quadros/1"),
        ("delete", "/api/quadros/1"),
        ("post", "/api/quadros/1/colunas"),
        ("put", "/api/colunas/1"),
        ("delete", "/api/colunas/1"),
        ("post", "/api/colunas/1/cartoes"),
        ("put", "/api/cartoes/1"),
        ("delete", "/api/cartoes/1"),
        ("put", "/api/cartoes/1/mover"),
    ],
)
def test_rotas_protegidas_sem_sessao_retornam_401(cliente, metodo, rota):
    resposta = getattr(cliente, metodo)(rota, json={})

    assert resposta.status_code == 401
    assert "erro" in resposta.get_json()


def test_rota_inexistente_da_api_retorna_404_em_json(cliente):
    resposta = cliente.get("/api/nao-existe")

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Recurso não encontrado"}
