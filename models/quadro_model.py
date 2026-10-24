"""Model de quadro ("plano de voo"): listar, criar, ver completo, renomear e excluir.

Toda função recebe o `usuario_id` do dono e só enxerga os quadros dele.
"""
from db import transacao
from models import validacoes
from models.erros import ErroValidacao, NaoEncontrado

COLUNAS_PADRAO = ("Embarque", "Em voo", "Pousou")
QUADRO_NAO_ENCONTRADO = "Quadro não encontrado"


def _titulo_validado(titulo):
    """Devolve o título sem espaços nas pontas ou levanta ErroValidacao."""
    titulo = validacoes.limpar_texto(titulo)
    erro = validacoes.validar_titulo_quadro(titulo)
    if erro:
        raise ErroValidacao({"titulo": erro}, erro)
    return titulo


def listar_quadros(usuario_id):
    """Lista os quadros do usuário (do mais antigo ao mais novo) com totais de colunas e cartões."""
    with transacao() as cur:
        cur.execute(
            """
            SELECT q.id, q.titulo,
                   (SELECT count(*) FROM coluna c WHERE c.quadro_id = q.id) AS total_colunas,
                   (SELECT count(*) FROM cartao k JOIN coluna c ON c.id = k.coluna_id
                     WHERE c.quadro_id = q.id) AS total_cartoes
              FROM quadro q
             WHERE q.usuario_id = %s
             ORDER BY q.criado_em, q.id
            """,
            (usuario_id,),
        )
        return cur.fetchall()


def quadro_pertence_ao_usuario(usuario_id, quadro_id):
    """Diz se o quadro existe e é do usuário (usado para proteger a página do quadro)."""
    with transacao() as cur:
        cur.execute("SELECT 1 FROM quadro WHERE id = %s AND usuario_id = %s", (quadro_id, usuario_id))
        return cur.fetchone() is not None


def criar_quadro(usuario_id, titulo):
    """Cria o quadro já com as colunas padrão (Embarque, Em voo, Pousou) e devolve {id, titulo}."""
    titulo = _titulo_validado(titulo)
    with transacao() as cur:
        cur.execute(
            "INSERT INTO quadro (titulo, usuario_id) VALUES (%s, %s) RETURNING id, titulo",
            (titulo, usuario_id),
        )
        quadro = cur.fetchone()
        cur.executemany(
            "INSERT INTO coluna (titulo, posicao, quadro_id) VALUES (%s, %s, %s)",
            [(nome, posicao, quadro["id"]) for posicao, nome in enumerate(COLUNAS_PADRAO)],
        )
        return quadro


def buscar_quadro_completo(usuario_id, quadro_id):
    """Devolve o quadro com suas colunas e, dentro de cada coluna, seus cartões (em ordem)."""
    with transacao() as cur:
        cur.execute(
            "SELECT id, titulo FROM quadro WHERE id = %s AND usuario_id = %s",
            (quadro_id, usuario_id),
        )
        quadro = cur.fetchone()
        if quadro is None:
            raise NaoEncontrado(QUADRO_NAO_ENCONTRADO)

        cur.execute(
            "SELECT id, titulo, posicao FROM coluna WHERE quadro_id = %s ORDER BY posicao",
            (quadro_id,),
        )
        colunas = cur.fetchall()

        cur.execute(
            """
            SELECT k.id, k.titulo, k.descricao, k.prazo, k.cor_etiqueta, k.posicao, k.coluna_id
              FROM cartao k JOIN coluna c ON c.id = k.coluna_id
             WHERE c.quadro_id = %s
             ORDER BY k.posicao
            """,
            (quadro_id,),
        )
        cartoes = cur.fetchall()

    # Distribui os cartões nas suas colunas (já vieram ordenados por posição).
    cartoes_por_coluna = {coluna["id"]: [] for coluna in colunas}
    for cartao in cartoes:
        cartoes_por_coluna[cartao.pop("coluna_id")].append(cartao)
    for coluna in colunas:
        coluna["cartoes"] = cartoes_por_coluna[coluna["id"]]

    quadro["colunas"] = colunas
    return quadro


def renomear_quadro(usuario_id, quadro_id, titulo):
    """Troca o título do quadro e devolve {id, titulo}."""
    titulo = _titulo_validado(titulo)
    with transacao() as cur:
        cur.execute(
            "UPDATE quadro SET titulo = %s WHERE id = %s AND usuario_id = %s RETURNING id, titulo",
            (titulo, quadro_id, usuario_id),
        )
        quadro = cur.fetchone()
    if quadro is None:
        raise NaoEncontrado(QUADRO_NAO_ENCONTRADO)
    return quadro


def excluir_quadro(usuario_id, quadro_id):
    """Exclui o quadro (colunas e cartões vão junto, em cascata)."""
    with transacao() as cur:
        cur.execute("DELETE FROM quadro WHERE id = %s AND usuario_id = %s", (quadro_id, usuario_id))
        excluiu = cur.rowcount > 0
    if not excluiu:
        raise NaoEncontrado(QUADRO_NAO_ENCONTRADO)
