"""Traduz os erros do app para respostas HTTP no formato padrão da API.

Formato: {"erro": "mensagem", "campos": {"campo": "mensagem"}} (campos é opcional).
"""
from flask import jsonify, request
from werkzeug.exceptions import HTTPException, InternalServerError

from controllers.pagina_controller import pagina_nao_encontrada
from models.erros import ErroConflito, ErroValidacao, NaoEncontrado

MENSAGENS_HTTP = {
    404: "Recurso não encontrado",
    405: "Método não permitido",
}


def _resposta(mensagem, status, campos=None):
    corpo = {"erro": mensagem}
    if campos:
        corpo["campos"] = campos
    return jsonify(corpo), status


def _eh_api():
    return request.path.startswith("/api/")


def registrar_tratadores_de_erro(app):
    """Liga cada tipo de erro à sua resposta."""

    @app.errorhandler(ErroValidacao)
    def validacao(erro):
        return _resposta(erro.mensagem, 400, erro.campos)

    @app.errorhandler(ErroConflito)
    def conflito(erro):
        return _resposta(erro.mensagem, 409, erro.campos)

    @app.errorhandler(NaoEncontrado)
    def nao_encontrado(erro):
        return _resposta(erro.mensagem, 404)

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        if _eh_api():
            return _resposta(MENSAGENS_HTTP.get(erro.code, erro.name), erro.code)
        if erro.code == 404:
            return pagina_nao_encontrada()
        return erro

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        # Detalhes vão para o log do servidor; o usuário recebe uma mensagem genérica.
        app.logger.exception("Erro inesperado em %s %s", request.method, request.path)
        if _eh_api():
            return _resposta("Ocorreu um erro inesperado. Tente novamente.", 500)
        return InternalServerError()
