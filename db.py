"""Conexão com o PostgreSQL usando psycopg 3.

Cada requisição abre uma conexão (guardada em `flask.g`) e a fecha ao terminar.
Os models usam `transacao()` para executar SQL com commit/rollback automático.
"""
from contextlib import contextmanager
from urllib.parse import urlparse

import psycopg
from flask import current_app, g
from psycopg.rows import dict_row

HOSTS_LOCAIS = {"localhost", "127.0.0.1", "::1"}


def _exige_ssl(url):
    """Diz se a URL aponta para um servidor remoto (ex.: Supabase), que exige SSL."""
    return urlparse(url).hostname not in HOSTS_LOCAIS


def conectar(url):
    """Abre uma conexão nova. Usada pelo app e pelos scripts de teste."""
    opcoes = {"sslmode": "require"} if _exige_ssl(url) else {}
    # autocommit=True: cada `transacao()` vira um BEGIN/COMMIT explícito e
    # nenhuma transação fica aberta "sem querer" entre uma consulta e outra.
    return psycopg.connect(url, autocommit=True, row_factory=dict_row, **opcoes)


def obter_conexao():
    """Devolve a conexão da requisição atual, criando-a na primeira chamada."""
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE_URL"])
    return g.db


def fechar_conexao(_erro=None):
    """Fecha a conexão da requisição (registrado no teardown do Flask)."""
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


@contextmanager
def transacao():
    """Executa um bloco numa transação: commit se tudo der certo, rollback se der erro.

    Uso:
        with transacao() as cur:
            cur.execute("SELECT ... WHERE id = %s", (id,))
    """
    conexao = obter_conexao()
    with conexao.transaction(), conexao.cursor() as cur:
        yield cur


def init_app(app):
    """Liga o ciclo de vida da conexão ao app Flask."""
    app.teardown_appcontext(fechar_conexao)
