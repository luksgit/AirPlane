"""Rotas de autenticação: /api/auth/*"""
from flask import Blueprint, jsonify

from controllers.requisicao import ler_json
from controllers.sessao import encerrar_sessao, iniciar_sessao
from models import usuario_model

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/cadastro")
def cadastro():
    """Cria a conta e já deixa o usuário logado."""
    dados = ler_json()
    usuario = usuario_model.criar_usuario(dados.get("nome"), dados.get("email"), dados.get("senha"))
    iniciar_sessao(usuario)
    return jsonify(usuario), 201


@bp.post("/login")
def login():
    """Confere e-mail e senha e inicia a sessão."""
    dados = ler_json()
    usuario = usuario_model.autenticar(dados.get("email"), dados.get("senha"))
    if usuario is None:
        return jsonify(erro="E-mail ou senha incorretos"), 401
    iniciar_sessao(usuario)
    return jsonify(usuario)


@bp.post("/logout")
def logout():
    """Encerra a sessão."""
    encerrar_sessao()
    return "", 204
