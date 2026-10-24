"""Rotas dos cartões: /api/colunas/<id>/cartoes e /api/cartoes/<id>*"""
from flask import Blueprint, jsonify

from controllers.requisicao import ler_json
from controllers.sessao import login_obrigatorio, usuario_logado_id
from models import cartao_model

bp = Blueprint("cartoes", __name__, url_prefix="/api")


@bp.post("/colunas/<int:coluna_id>/cartoes")
@login_obrigatorio
def criar(coluna_id):
    """Cria um cartão no final da coluna."""
    dados = ler_json()
    cartao = cartao_model.criar_cartao(usuario_logado_id(), coluna_id, dados.get("titulo"))
    return jsonify(cartao), 201


@bp.put("/cartoes/<int:cartao_id>")
@login_obrigatorio
def atualizar(cartao_id):
    """Salva título, descrição, prazo, etiqueta e (opcionalmente) a coluna do cartão."""
    dados = ler_json()
    cartao = cartao_model.atualizar_cartao(
        usuario_logado_id(),
        cartao_id,
        titulo=dados.get("titulo"),
        descricao=dados.get("descricao"),
        prazo=dados.get("prazo"),
        cor_etiqueta=dados.get("cor_etiqueta"),
        coluna_id=dados.get("coluna_id"),
    )
    return jsonify(cartao)


@bp.delete("/cartoes/<int:cartao_id>")
@login_obrigatorio
def excluir(cartao_id):
    """Exclui o cartão."""
    cartao_model.excluir_cartao(usuario_logado_id(), cartao_id)
    return "", 204


@bp.put("/cartoes/<int:cartao_id>/mover")
@login_obrigatorio
def mover(cartao_id):
    """Move o cartão para outra posição/coluna do mesmo quadro."""
    dados = ler_json()
    cartao = cartao_model.mover_cartao(
        usuario_logado_id(), cartao_id, dados.get("coluna_id"), dados.get("posicao")
    )
    return jsonify(cartao)
