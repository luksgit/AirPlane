"""Rotas do perfil do usuário logado: /api/usuarios/me*"""
from flask import Blueprint, jsonify

from controllers.requisicao import ler_json
from controllers.sessao import SESSAO_EXPIRADA, encerrar_sessao, login_obrigatorio, usuario_logado_id
from models import usuario_model

bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@bp.get("/me")
@login_obrigatorio
def ver_perfil():
    """Devolve os dados do usuário logado."""
    usuario = usuario_model.buscar_por_id(usuario_logado_id())
    if usuario is None:
        # A conta deixou de existir: a sessão não vale mais.
        encerrar_sessao()
        return jsonify(erro=SESSAO_EXPIRADA), 401
    return jsonify(usuario)


@bp.put("/me")
@login_obrigatorio
def atualizar_perfil():
    """Atualiza o nome do usuário logado."""
    dados = ler_json()
    usuario = usuario_model.atualizar_nome(usuario_logado_id(), dados.get("nome"))
    return jsonify(usuario)


@bp.put("/me/senha")
@login_obrigatorio
def alterar_senha():
    """Troca a senha do usuário logado."""
    dados = ler_json()
    usuario_model.alterar_senha(usuario_logado_id(), dados.get("senha_atual"), dados.get("nova_senha"))
    return "", 204
