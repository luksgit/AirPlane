"""Preparação dos testes do back-end: banco de teste limpo e cliente HTTP do Flask."""
from pathlib import Path

import pytest

import db
from app import create_app
from config import TestConfig

PASTA_DATABASE = Path(__file__).resolve().parents[2] / "database"


@pytest.fixture(scope="session")
def url_banco():
    """Recria as tabelas antes da suíte e restaura os dados de exemplo no final.

    Os testes rodam no mesmo banco do desenvolvimento (Supabase) e apagam tudo
    que estiver nele; ao terminar, o seed.sql deixa a conta de exemplo pronta de novo.
    """
    url = TestConfig.DATABASE_URL
    if not url:
        pytest.exit("Configure DATABASE_URL no arquivo .env", returncode=1)

    with db.conectar(url) as conexao:
        conexao.execute("DROP TABLE IF EXISTS cartao, coluna, quadro, usuario CASCADE")
        conexao.execute((PASTA_DATABASE / "schema.sql").read_text(encoding="utf-8"))

    yield url

    with db.conectar(url) as conexao:
        conexao.execute("TRUNCATE usuario RESTART IDENTITY CASCADE")
        conexao.execute((PASTA_DATABASE / "seed.sql").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def conexao_teste(url_banco):
    """Uma conexão aberta para a suíte inteira (usada pelo app e pelos próprios testes)."""
    with db.conectar(url_banco) as conexao:
        yield conexao


@pytest.fixture(autouse=True)
def reaproveitar_conexao(monkeypatch, conexao_teste):
    """Faz o app usar a conexão da suíte em vez de abrir uma nova a cada requisição.

    Abrir uma conexão SSL até o Supabase leva cerca de 1 s; reaproveitar deixa a
    suíte várias vezes mais rápida. O comportamento das transações não muda.
    """
    monkeypatch.setattr(db, "obter_conexao", lambda: conexao_teste)


@pytest.fixture
def inserir_cartao(conexao_teste):
    """Grava um cartão direto no banco e devolve o id (para montar cenários sem a API de cartões)."""

    def _inserir_cartao(coluna_id, titulo, posicao, prazo=None, cor_etiqueta=None):
        return conexao_teste.execute(
            "INSERT INTO cartao (titulo, prazo, cor_etiqueta, posicao, coluna_id)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (titulo, prazo, cor_etiqueta, posicao, coluna_id),
        ).fetchone()["id"]

    return _inserir_cartao


@pytest.fixture
def contar(conexao_teste):
    """Conta as linhas de uma tabela."""

    def _contar(tabela):
        return conexao_teste.execute(f"SELECT count(*) AS total FROM {tabela}").fetchone()["total"]

    return _contar


@pytest.fixture(autouse=True)
def banco_limpo(conexao_teste):
    """Cada teste começa com o banco vazio (a cascata limpa as outras tabelas)."""
    conexao_teste.execute("TRUNCATE usuario RESTART IDENTITY CASCADE")


@pytest.fixture
def app(url_banco):
    return create_app(TestConfig)


@pytest.fixture
def cliente(app):
    """Cliente HTTP sem ninguém logado."""
    return app.test_client()


@pytest.fixture
def cadastrar(app):
    """Cadastra um usuário e devolve um cliente HTTP já logado com ele."""

    def _cadastrar(nome="Ana Souza", email="ana@email.com", senha="senha1234"):
        cliente = app.test_client()
        resposta = cliente.post("/api/auth/cadastro", json={"nome": nome, "email": email, "senha": senha})
        assert resposta.status_code == 201, resposta.get_json()
        return cliente

    return _cadastrar


@pytest.fixture
def criar_quadro():
    """Cria um quadro pela API com o cliente informado e devolve o quadro completo."""

    def _criar_quadro(cliente, titulo="Plano de teste"):
        resposta = cliente.post("/api/quadros", json={"titulo": titulo})
        assert resposta.status_code == 201, resposta.get_json()
        return cliente.get(f"/api/quadros/{resposta.get_json()['id']}").get_json()

    return _criar_quadro


@pytest.fixture
def quadro_da_ana(cadastrar, criar_quadro):
    """Cenário de isolamento: Ana cria um quadro e Bruno (outro usuário) tenta mexer nele.

    Devolve (cliente_ana, cliente_bruno, quadro_completo_da_ana).
    """
    ana = cadastrar(nome="Ana Souza", email="ana@email.com")
    quadro = criar_quadro(ana, "Quadro da Ana")
    bruno = cadastrar(nome="Bruno Lima", email="bruno@email.com")
    return ana, bruno, quadro
