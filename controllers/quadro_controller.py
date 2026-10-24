"""Rotas dos quadros do usuário logado: /api/quadros/*"""
from flask import Blueprint, jsonify

from controllers.requisicao import ler_json
from controllers.sessao import login_obrigatorio, usuario_logado_id
from models import quadro_model

bp = Blueprint("quadros", __name__, url_prefix="/api/quadros")


@bp.get("")
@login_obrigatorio
def listar():
    """Lista os quadros com os totais de colunas e cartões."""
    return jsonify(quadro_model.listar_quadros(usuario_logado_id()))


@bp.post("")
@login_obrigatorio
def criar():
    """Cria um quadro com as 3 colunas padrão."""
    dados = ler_json()
    quadro = quadro_model.criar_quadro(usuario_logado_id(), dados.get("titulo"))
    return jsonify(quadro), 201


@bp.get("/<int:quadro_id>")
@login_obrigatorio
def ver(quadro_id):
    """Devolve o quadro completo: colunas e cartões."""
    return jsonify(quadro_model.buscar_quadro_completo(usuario_logado_id(), quadro_id))


@bp.put("/<int:quadro_id>")
@login_obrigatorio
def renomear(quadro_id):
    """Troca o título do quadro."""
    dados = ler_json()
    quadro = quadro_model.renomear_quadro(usuario_logado_id(), quadro_id, dados.get("titulo"))
    return jsonify(quadro)


@bp.delete("/<int:quadro_id>")
@login_obrigatorio
def excluir(quadro_id):
    """Exclui o quadro com tudo que há dentro."""
    quadro_model.excluir_quadro(usuario_logado_id(), quadro_id)
    return "", 204
