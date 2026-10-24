"""Conversão das respostas para JSON.

Por padrão o Flask escreve datas como "Sat, 25 Oct 2026 00:00:00 GMT".
Aqui elas saem no formato ISO ("2026-10-25"), que é o que o front espera no prazo.
"""
from datetime import date

from flask.json.provider import DefaultJSONProvider


class JsonProvider(DefaultJSONProvider):
    @staticmethod
    def default(valor):
        if isinstance(valor, date):
            return valor.isoformat()
        return DefaultJSONProvider.default(valor)
