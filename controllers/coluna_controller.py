"""Rotas das colunas: /api/quadros/<id>/colunas e /api/colunas/<id>"""
from flask import Blueprint, jsonify

from controllers.requisicao import ler_json
from controllers.sessao import login_obrigatorio, usuario_logado_id
from models import coluna_model

bp = Blueprint("colunas", __name__, url_prefix="/api")


@bp.post("/quadros/<int:quadro_id>/colunas")
@login_obrigatorio
def criar(quadro_id):
    """Cria uma coluna no final do quadro."""
    dados = ler_json()
    coluna = coluna_model.criar_coluna(usuario_logado_id(), quadro_id, dados.get("titulo"))
    return jsonify(coluna), 201


@bp.put("/colunas/<int:coluna_id>")
@login_obrigatorio
def renomear(coluna_id):
    """Troca o título da coluna."""
    dados = ler_json()
    coluna = coluna_model.renomear_coluna(usuario_logado_id(), coluna_id, dados.get("titulo"))
    return jsonify(coluna)


@bp.delete("/colunas/<int:coluna_id>")
@login_obrigatorio
def excluir(coluna_id):
    """Exclui a coluna com seus cartões."""
    coluna_model.excluir_coluna(usuario_logado_id(), coluna_id)
    return "", 204
