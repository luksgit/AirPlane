"""Sessão do usuário logado (cookie de sessão do Flask)."""
from functools import wraps

from flask import jsonify, session

SESSAO_EXPIRADA = "Sua sessão expirou. Entre novamente."


def iniciar_sessao(usuario):
    """Guarda o id do usuário no cookie de sessão (assinado pelo Flask)."""
    session.clear()
    session["usuario_id"] = usuario["id"]


def encerrar_sessao():
    session.clear()


def usuario_logado_id():
    """Id do usuário logado ou None."""
    return session.get("usuario_id")


def login_obrigatorio(rota):
    """Decorator das rotas da API: sem sessão, responde 401."""

    @wraps(rota)
    def verificar(*args, **kwargs):
        if usuario_logado_id() is None:
            return jsonify(erro=SESSAO_EXPIRADA), 401
        return rota(*args, **kwargs)

    return verificar
