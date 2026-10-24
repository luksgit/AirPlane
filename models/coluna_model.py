"""Model de coluna (etapa do quadro): criar, renomear e excluir.

A coluna pertence ao usuário através do quadro, então toda consulta junta
`coluna` com `quadro` e confere o `usuario_id`.
"""
from db import transacao
from models import validacoes
from models.erros import ErroValidacao, NaoEncontrado
from models.quadro_model import QUADRO_NAO_ENCONTRADO

COLUNA_NAO_ENCONTRADA = "Coluna não encontrada"


def _titulo_validado(titulo):
    """Devolve o título sem espaços nas pontas ou levanta ErroValidacao."""
    titulo = validacoes.limpar_texto(titulo)
    erro = validacoes.validar_titulo_coluna(titulo)
    if erro:
        raise ErroValidacao({"titulo": erro}, erro)
    return titulo


def criar_coluna(usuario_id, quadro_id, titulo):
    """Cria a coluna no final do quadro e devolve {id, titulo, posicao}."""
    titulo = _titulo_validado(titulo)
    with transacao() as cur:
        # FOR UPDATE trava o quadro até o fim da transação: duas colunas criadas
        # ao mesmo tempo não acabam com a mesma posição.
        cur.execute(
            "SELECT id FROM quadro WHERE id = %s AND usuario_id = %s FOR UPDATE",
            (quadro_id, usuario_id),
        )
        if cur.fetchone() is None:
            raise NaoEncontrado(QUADRO_NAO_ENCONTRADO)

        # As posições são contínuas (0, 1, 2…), então a quantidade atual é a próxima posição.
        cur.execute(
            """
            INSERT INTO coluna (titulo, posicao, quadro_id)
            SELECT %s, count(*), %s FROM coluna WHERE quadro_id = %s
            RETURNING id, titulo, posicao
            """,
            (titulo, quadro_id, quadro_id),
        )
        return cur.fetchone()


def renomear_coluna(usuario_id, coluna_id, titulo):
    """Troca o título da coluna e devolve {id, titulo, posicao}."""
    titulo = _titulo_validado(titulo)
    with transacao() as cur:
        cur.execute(
            """
            UPDATE coluna c SET titulo = %s
              FROM quadro q
             WHERE c.id = %s AND q.id = c.quadro_id AND q.usuario_id = %s
            RETURNING c.id, c.titulo, c.posicao
            """,
            (titulo, coluna_id, usuario_id),
        )
        coluna = cur.fetchone()
    if coluna is None:
        raise NaoEncontrado(COLUNA_NAO_ENCONTRADA)
    return coluna


def excluir_coluna(usuario_id, coluna_id):
    """Exclui a coluna (e seus cartões) e fecha o buraco nas posições das colunas seguintes."""
    with transacao() as cur:
        cur.execute(
            """
            DELETE FROM coluna c
             USING quadro q
             WHERE c.id = %s AND q.id = c.quadro_id AND q.usuario_id = %s
            RETURNING c.quadro_id, c.posicao
            """,
            (coluna_id, usuario_id),
        )
        excluida = cur.fetchone()
        if excluida is None:
            raise NaoEncontrado(COLUNA_NAO_ENCONTRADA)

        cur.execute(
            "UPDATE coluna SET posicao = posicao - 1 WHERE quadro_id = %s AND posicao > %s",
            (excluida["quadro_id"], excluida["posicao"]),
        )
