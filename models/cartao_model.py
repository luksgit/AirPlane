"""Model de cartão (tarefa): criar, editar, excluir e mover entre posições/colunas.

O cartão pertence ao usuário através de coluna → quadro, então as consultas juntam
as três tabelas e conferem o `usuario_id`. As posições dentro de cada coluna são
sempre contínuas (0, 1, 2…): toda operação que tira ou põe um cartão reordena os
vizinhos na mesma transação.

Concorrência: toda operação começa travando a linha do *quadro* (FOR UPDATE).
Assim, duas operações no mesmo quadro acontecem uma depois da outra e as posições
nunca se embaralham. Como é uma trava só por quadro, não há risco de deadlock.
"""
from db import transacao
from models import validacoes
from models.coluna_model import COLUNA_NAO_ENCONTRADA
from models.erros import ErroValidacao, NaoEncontrado

CAMPOS = "id, titulo, descricao, prazo, cor_etiqueta, posicao, coluna_id"
CARTAO_NAO_ENCONTRADO = "Cartão não encontrado"
COLUNA_DE_OUTRO_QUADRO = "A coluna de destino precisa ser do mesmo quadro"


def _travar_quadro_da_coluna(cur, usuario_id, coluna_id):
    """Trava o quadro dono da coluna; levanta NaoEncontrado se a coluna não for do usuário."""
    cur.execute(
        """
        SELECT q.id
          FROM coluna c JOIN quadro q ON q.id = c.quadro_id
         WHERE c.id = %s AND q.usuario_id = %s
           FOR UPDATE OF q
        """,
        (coluna_id, usuario_id),
    )
    if cur.fetchone() is None:
        raise NaoEncontrado(COLUNA_NAO_ENCONTRADA)


def _travar_e_ler_cartao(cur, usuario_id, cartao_id):
    """Trava o quadro dono do cartão e devolve {id, coluna_id, posicao, quadro_id}.

    A leitura do cartão é feita só depois da trava, para pegar a posição mais atual
    (outra operação pode tê-la mudado enquanto esperávamos).
    """
    cur.execute(
        """
        SELECT q.id
          FROM cartao k
          JOIN coluna c ON c.id = k.coluna_id
          JOIN quadro q ON q.id = c.quadro_id
         WHERE k.id = %s AND q.usuario_id = %s
           FOR UPDATE OF q
        """,
        (cartao_id, usuario_id),
    )
    if cur.fetchone() is not None:
        cur.execute(
            """
            SELECT k.id, k.coluna_id, k.posicao, c.quadro_id
              FROM cartao k JOIN coluna c ON c.id = k.coluna_id
             WHERE k.id = %s
            """,
            (cartao_id,),
        )
        cartao = cur.fetchone()
        if cartao is not None:
            return cartao
    raise NaoEncontrado(CARTAO_NAO_ENCONTRADO)


def _conferir_coluna_de_destino(cur, usuario_id, cartao, coluna_id):
    """A coluna de destino tem que ser do usuário (senão 404) e do mesmo quadro do cartão (senão 400)."""
    cur.execute(
        """
        SELECT c.quadro_id
          FROM coluna c JOIN quadro q ON q.id = c.quadro_id
         WHERE c.id = %s AND q.usuario_id = %s
        """,
        (coluna_id, usuario_id),
    )
    coluna = cur.fetchone()
    if coluna is None:
        raise NaoEncontrado(COLUNA_NAO_ENCONTRADA)
    if coluna["quadro_id"] != cartao["quadro_id"]:
        raise ErroValidacao({"coluna_id": COLUNA_DE_OUTRO_QUADRO}, COLUNA_DE_OUTRO_QUADRO)


def _reposicionar(cur, cartao, coluna_destino_id, posicao_desejada=None):
    """Tira o cartão do lugar atual e o coloca na coluna/posição de destino.

    1. Na coluna de origem, os cartões abaixo dele sobem uma posição.
    2. Na coluna de destino, os cartões a partir da nova posição descem uma, abrindo espaço.
    Funciona igual para mover dentro da mesma coluna ou entre colunas.
    `posicao_desejada=None` (ou maior que o tamanho da coluna) coloca no final.
    """
    cur.execute(
        "UPDATE cartao SET posicao = posicao - 1 WHERE coluna_id = %s AND posicao > %s",
        (cartao["coluna_id"], cartao["posicao"]),
    )

    cur.execute(
        "SELECT count(*) AS total FROM cartao WHERE coluna_id = %s AND id <> %s",
        (coluna_destino_id, cartao["id"]),
    )
    total_no_destino = cur.fetchone()["total"]
    nova_posicao = total_no_destino if posicao_desejada is None else min(posicao_desejada, total_no_destino)

    cur.execute(
        "UPDATE cartao SET posicao = posicao + 1 WHERE coluna_id = %s AND posicao >= %s AND id <> %s",
        (coluna_destino_id, nova_posicao, cartao["id"]),
    )
    cur.execute(
        "UPDATE cartao SET coluna_id = %s, posicao = %s WHERE id = %s",
        (coluna_destino_id, nova_posicao, cartao["id"]),
    )


def criar_cartao(usuario_id, coluna_id, titulo):
    """Cria o cartão no final da coluna e devolve o cartão completo."""
    titulo = validacoes.limpar_texto(titulo)
    erro = validacoes.validar_titulo_cartao(titulo)
    if erro:
        raise ErroValidacao({"titulo": erro}, erro)

    with transacao() as cur:
        _travar_quadro_da_coluna(cur, usuario_id, coluna_id)
        # Posições contínuas: a quantidade atual de cartões é a próxima posição.
        cur.execute(
            f"""
            INSERT INTO cartao (titulo, posicao, coluna_id)
            SELECT %s, count(*), %s FROM cartao WHERE coluna_id = %s
            RETURNING {CAMPOS}
            """,
            (titulo, coluna_id, coluna_id),
        )
        return cur.fetchone()


def atualizar_cartao(usuario_id, cartao_id, titulo, descricao, prazo, cor_etiqueta, coluna_id=None):
    """Salva os dados do cartão (todos os campos editáveis são substituídos).

    Se `coluna_id` vier e for diferente da atual, o cartão vai para o final da nova coluna.
    """
    titulo = validacoes.limpar_texto(titulo)
    descricao = validacoes.texto_opcional(descricao)
    prazo = validacoes.texto_opcional(prazo)
    cor_etiqueta = validacoes.texto_opcional(cor_etiqueta)
    erros = validacoes.juntar_erros(
        titulo=validacoes.validar_titulo_cartao(titulo),
        descricao=validacoes.validar_descricao(descricao),
        prazo=validacoes.validar_prazo(prazo),
        cor_etiqueta=validacoes.validar_cor_etiqueta(cor_etiqueta),
        coluna_id=None if coluna_id is None or validacoes.eh_inteiro(coluna_id, 1) else "Coluna inválida",
    )
    if erros:
        raise ErroValidacao(erros)

    with transacao() as cur:
        cartao = _travar_e_ler_cartao(cur, usuario_id, cartao_id)
        if coluna_id is not None and coluna_id != cartao["coluna_id"]:
            _conferir_coluna_de_destino(cur, usuario_id, cartao, coluna_id)
            _reposicionar(cur, cartao, coluna_id)

        cur.execute(
            f"""
            UPDATE cartao SET titulo = %s, descricao = %s, prazo = %s, cor_etiqueta = %s
             WHERE id = %s
            RETURNING {CAMPOS}
            """,
            (titulo, descricao, prazo, cor_etiqueta, cartao_id),
        )
        return cur.fetchone()


def excluir_cartao(usuario_id, cartao_id):
    """Exclui o cartão e fecha o buraco nas posições dos cartões abaixo dele."""
    with transacao() as cur:
        cartao = _travar_e_ler_cartao(cur, usuario_id, cartao_id)
        cur.execute("DELETE FROM cartao WHERE id = %s", (cartao_id,))
        cur.execute(
            "UPDATE cartao SET posicao = posicao - 1 WHERE coluna_id = %s AND posicao > %s",
            (cartao["coluna_id"], cartao["posicao"]),
        )


def mover_cartao(usuario_id, cartao_id, coluna_id, posicao):
    """Move o cartão para a coluna e posição indicadas (usado pelo arrastar e soltar)."""
    erros = validacoes.juntar_erros(
        coluna_id=None if validacoes.eh_inteiro(coluna_id, 1) else "Coluna inválida",
        posicao=None if validacoes.eh_inteiro(posicao, 0) else "Posição inválida",
    )
    if erros:
        raise ErroValidacao(erros)

    with transacao() as cur:
        cartao = _travar_e_ler_cartao(cur, usuario_id, cartao_id)
        if coluna_id != cartao["coluna_id"]:
            _conferir_coluna_de_destino(cur, usuario_id, cartao, coluna_id)
        _reposicionar(cur, cartao, coluna_id, posicao)

        cur.execute(f"SELECT {CAMPOS} FROM cartao WHERE id = %s", (cartao_id,))
        return cur.fetchone()
