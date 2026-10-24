"""Testes dos cartões: criar, editar, excluir, mover (com reordenação) e isolamento."""
import pytest


@pytest.fixture
def cenario(cadastrar, criar_quadro):
    """Usuário logado com um quadro e cartões A, B e C em Embarque e D em Em voo.

    Devolve (cliente, quadro_id, {"embarque": id, "em_voo": id, "pousou": id}, {"A": id, ...}).
    """
    cliente = cadastrar()
    quadro = criar_quadro(cliente)
    colunas = dict(zip(("embarque", "em_voo", "pousou"), (c["id"] for c in quadro["colunas"])))
    cartoes = {}
    for titulo, coluna in (("A", "embarque"), ("B", "embarque"), ("C", "embarque"), ("D", "em_voo")):
        resposta = cliente.post(f"/api/colunas/{colunas[coluna]}/cartoes", json={"titulo": titulo})
        cartoes[titulo] = resposta.get_json()["id"]
    return cliente, quadro["id"], colunas, cartoes


def disposicao(cliente, quadro_id):
    """Títulos dos cartões de cada coluna, conferindo que as posições são contínuas (0, 1, 2…)."""
    quadro = cliente.get(f"/api/quadros/{quadro_id}").get_json()
    resultado = []
    for coluna in quadro["colunas"]:
        posicoes = [c["posicao"] for c in coluna["cartoes"]]
        assert posicoes == list(range(len(posicoes))), f"posições com buraco em {coluna['titulo']}: {posicoes}"
        resultado.append([c["titulo"] for c in coluna["cartoes"]])
    return resultado


DADOS_COMPLETOS = {
    "titulo": "  Gravar vídeo  ",
    "descricao": "Mínimo de 5 minutos, só tela e voz.",
    "prazo": "2026-11-17",
    "cor_etiqueta": "vermelho",
}


# --- Criar ------------------------------------------------------------------

def test_criar_cartao_vai_para_o_final_da_coluna(cenario):
    cliente, quadro_id, colunas, _ = cenario

    resposta = cliente.post(f"/api/colunas/{colunas['embarque']}/cartoes", json={"titulo": "  Novo  "})

    assert resposta.status_code == 201
    assert resposta.get_json() == {
        "id": 5,
        "titulo": "Novo",
        "descricao": None,
        "prazo": None,
        "cor_etiqueta": None,
        "posicao": 3,
        "coluna_id": colunas["embarque"],
    }
    assert disposicao(cliente, quadro_id) == [["A", "B", "C", "Novo"], ["D"], []]


@pytest.mark.parametrize(
    "titulo, mensagem",
    [("", "Dê um título ao cartão"), ("   ", "Dê um título ao cartão"),
     ("A" * 101, "O título do cartão deve ter no máximo 100 caracteres")],
)
def test_criar_cartao_valida_titulo(cenario, contar, titulo, mensagem):
    cliente, _, colunas, _ = cenario

    resposta = cliente.post(f"/api/colunas/{colunas['pousou']}/cartoes", json={"titulo": titulo})

    assert resposta.status_code == 400
    assert resposta.get_json() == {"erro": mensagem, "campos": {"titulo": mensagem}}
    assert contar("cartao") == 4


def test_criar_cartao_em_coluna_inexistente_retorna_404(cenario):
    cliente, *_ = cenario

    resposta = cliente.post("/api/colunas/999/cartoes", json={"titulo": "Novo"})

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Coluna não encontrada"}


# --- Editar -----------------------------------------------------------------

def test_editar_cartao_salva_todos_os_campos(cenario):
    cliente, _, colunas, cartoes = cenario

    resposta = cliente.put(f"/api/cartoes/{cartoes['B']}", json=DADOS_COMPLETOS)

    assert resposta.status_code == 200
    assert resposta.get_json() == {
        "id": cartoes["B"],
        "titulo": "Gravar vídeo",
        "descricao": "Mínimo de 5 minutos, só tela e voz.",
        "prazo": "2026-11-17",
        "cor_etiqueta": "vermelho",
        "posicao": 1,
        "coluna_id": colunas["embarque"],
    }


def test_editar_cartao_com_campos_vazios_limpa_os_opcionais(cenario):
    cliente, _, _, cartoes = cenario
    cliente.put(f"/api/cartoes/{cartoes['A']}", json=DADOS_COMPLETOS)

    resposta = cliente.put(
        f"/api/cartoes/{cartoes['A']}",
        json={"titulo": "A", "descricao": "   ", "prazo": "", "cor_etiqueta": None},
    )

    corpo = resposta.get_json()
    assert resposta.status_code == 200
    assert (corpo["descricao"], corpo["prazo"], corpo["cor_etiqueta"]) == (None, None, None)


@pytest.mark.parametrize(
    "campo, valor, mensagem",
    [
        ("titulo", "", "Dê um título ao cartão"),
        ("titulo", "A" * 101, "O título do cartão deve ter no máximo 100 caracteres"),
        ("descricao", "x" * 2001, "A descrição deve ter no máximo 2000 caracteres"),
        ("prazo", "17/11/2026", "Informe uma data válida"),
        ("prazo", "2026-02-30", "Informe uma data válida"),
        ("cor_etiqueta", "rosa", "Escolha uma das cores disponíveis"),
        ("coluna_id", "abc", "Coluna inválida"),
    ],
)
def test_editar_cartao_valida_campos(cenario, campo, valor, mensagem):
    cliente, _, _, cartoes = cenario

    resposta = cliente.put(f"/api/cartoes/{cartoes['A']}", json={**DADOS_COMPLETOS, campo: valor})

    assert resposta.status_code == 400
    assert resposta.get_json()["campos"] == {campo: mensagem}


def test_editar_cartao_aceita_todas_as_cores(cenario):
    cliente, _, _, cartoes = cenario

    for cor in ("verde", "amarelo", "laranja", "vermelho", "roxo", "azul"):
        resposta = cliente.put(f"/api/cartoes/{cartoes['A']}", json={**DADOS_COMPLETOS, "cor_etiqueta": cor})
        assert resposta.get_json()["cor_etiqueta"] == cor


def test_editar_cartao_trocando_de_coluna_vai_para_o_final_da_nova(cenario):
    cliente, quadro_id, colunas, cartoes = cenario

    resposta = cliente.put(
        f"/api/cartoes/{cartoes['A']}", json={**DADOS_COMPLETOS, "coluna_id": colunas["em_voo"]}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["coluna_id"] == colunas["em_voo"]
    assert resposta.get_json()["posicao"] == 1
    assert disposicao(cliente, quadro_id) == [["B", "C"], ["D", "Gravar vídeo"], []]


def test_editar_cartao_com_a_mesma_coluna_nao_muda_a_posicao(cenario):
    cliente, quadro_id, colunas, cartoes = cenario

    cliente.put(f"/api/cartoes/{cartoes['A']}", json={"titulo": "A2", "coluna_id": colunas["embarque"]})

    assert disposicao(cliente, quadro_id) == [["A2", "B", "C"], ["D"], []]


def test_editar_cartao_inexistente_retorna_404(cenario):
    cliente, *_ = cenario

    resposta = cliente.put("/api/cartoes/999", json=DADOS_COMPLETOS)

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Cartão não encontrado"}


# --- Excluir ----------------------------------------------------------------

def test_excluir_cartao_reordena_a_coluna(cenario):
    cliente, quadro_id, _, cartoes = cenario

    resposta = cliente.delete(f"/api/cartoes/{cartoes['A']}")

    assert resposta.status_code == 204
    assert disposicao(cliente, quadro_id) == [["B", "C"], ["D"], []]


def test_excluir_cartao_inexistente_retorna_404(cenario):
    cliente, *_ = cenario

    assert cliente.delete("/api/cartoes/999").status_code == 404


# --- Mover ------------------------------------------------------------------

@pytest.mark.parametrize(
    "cartao, coluna, posicao, esperado",
    [
        # Dentro da mesma coluna
        ("A", "embarque", 2, [["B", "C", "A"], ["D"], []]),
        ("C", "embarque", 0, [["C", "A", "B"], ["D"], []]),
        ("B", "embarque", 1, [["A", "B", "C"], ["D"], []]),
        # Entre colunas
        ("B", "em_voo", 0, [["A", "C"], ["B", "D"], []]),
        ("B", "em_voo", 1, [["A", "C"], ["D", "B"], []]),
        ("A", "pousou", 0, [["B", "C"], ["D"], ["A"]]),
        ("D", "embarque", 1, [["A", "D", "B", "C"], [], []]),
        # Posição além do fim vai para o final
        ("A", "em_voo", 50, [["B", "C"], ["D", "A"], []]),
        ("A", "embarque", 50, [["B", "C", "A"], ["D"], []]),
    ],
)
def test_mover_cartao_reordena_origem_e_destino(cenario, cartao, coluna, posicao, esperado):
    cliente, quadro_id, colunas, cartoes = cenario

    resposta = cliente.put(
        f"/api/cartoes/{cartoes[cartao]}/mover", json={"coluna_id": colunas[coluna], "posicao": posicao}
    )

    assert resposta.status_code == 200
    assert resposta.get_json()["coluna_id"] == colunas[coluna]
    assert disposicao(cliente, quadro_id) == esperado


def test_mover_varias_vezes_mantem_posicoes_continuas(cenario):
    cliente, quadro_id, colunas, cartoes = cenario
    movimentos = [("A", "pousou", 0), ("D", "pousou", 0), ("B", "em_voo", 0), ("A", "embarque", 0), ("C", "pousou", 1)]

    for cartao, coluna, posicao in movimentos:
        cliente.put(f"/api/cartoes/{cartoes[cartao]}/mover", json={"coluna_id": colunas[coluna], "posicao": posicao})

    assert disposicao(cliente, quadro_id) == [["A"], ["B"], ["D", "C"]]


def test_mover_para_coluna_de_outro_quadro_retorna_400(cenario, criar_quadro):
    cliente, quadro_id, _, cartoes = cenario
    outro_quadro = criar_quadro(cliente, "Outro")

    resposta = cliente.put(
        f"/api/cartoes/{cartoes['A']}/mover",
        json={"coluna_id": outro_quadro["colunas"][0]["id"], "posicao": 0},
    )

    assert resposta.status_code == 400
    assert resposta.get_json()["erro"] == "A coluna de destino precisa ser do mesmo quadro"
    assert disposicao(cliente, quadro_id) == [["A", "B", "C"], ["D"], []]


def test_trocar_coluna_na_edicao_para_outro_quadro_retorna_400(cenario, criar_quadro):
    cliente, quadro_id, _, cartoes = cenario
    outro_quadro = criar_quadro(cliente, "Outro")

    resposta = cliente.put(
        f"/api/cartoes/{cartoes['A']}", json={**DADOS_COMPLETOS, "coluna_id": outro_quadro["colunas"][0]["id"]}
    )

    assert resposta.status_code == 400
    assert disposicao(cliente, quadro_id) == [["A", "B", "C"], ["D"], []]


def test_mover_para_coluna_inexistente_retorna_404(cenario):
    cliente, _, _, cartoes = cenario

    resposta = cliente.put(f"/api/cartoes/{cartoes['A']}/mover", json={"coluna_id": 999, "posicao": 0})

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Coluna não encontrada"}


@pytest.mark.parametrize(
    "corpo, campos",
    [
        ({}, {"coluna_id": "Coluna inválida", "posicao": "Posição inválida"}),
        ({"coluna_id": 1, "posicao": -1}, {"posicao": "Posição inválida"}),
        ({"coluna_id": 1, "posicao": "0"}, {"posicao": "Posição inválida"}),
        ({"coluna_id": True, "posicao": 0}, {"coluna_id": "Coluna inválida"}),
    ],
)
def test_mover_valida_corpo(cenario, corpo, campos):
    cliente, _, _, cartoes = cenario

    resposta = cliente.put(f"/api/cartoes/{cartoes['A']}/mover", json=corpo)

    assert resposta.status_code == 400
    assert resposta.get_json()["campos"] == campos


# --- Isolamento entre usuários ----------------------------------------------

@pytest.fixture
def cartao_da_ana(quadro_da_ana):
    """Ana tem um cartão em Embarque; o teste age como Bruno."""
    ana, bruno, quadro = quadro_da_ana
    embarque = quadro["colunas"][0]["id"]
    cartao = ana.post(f"/api/colunas/{embarque}/cartoes", json={"titulo": "Da Ana"}).get_json()
    return ana, bruno, quadro, cartao


def test_usuario_nao_cria_cartao_na_coluna_de_outro(cartao_da_ana, contar):
    _, bruno, quadro, _ = cartao_da_ana

    resposta = bruno.post(f"/api/colunas/{quadro['colunas'][0]['id']}/cartoes", json={"titulo": "Intruso"})

    assert resposta.status_code == 404
    assert contar("cartao") == 1


@pytest.mark.parametrize(
    "metodo, sufixo, corpo",
    [
        ("put", "", {"titulo": "Invadido"}),
        ("delete", "", None),
        ("put", "/mover", {"coluna_id": 1, "posicao": 0}),
    ],
)
def test_usuario_nao_altera_cartao_de_outro(cartao_da_ana, metodo, sufixo, corpo):
    ana, bruno, quadro, cartao = cartao_da_ana

    resposta = getattr(bruno, metodo)(f"/api/cartoes/{cartao['id']}{sufixo}", json=corpo)

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Cartão não encontrado"}
    assert disposicao(ana, quadro["id"]) == [["Da Ana"], [], []]


def test_usuario_nao_move_proprio_cartao_para_coluna_de_outro(cartao_da_ana, criar_quadro):
    _, bruno, quadro_ana, _ = cartao_da_ana
    quadro_bruno = criar_quadro(bruno, "Do Bruno")
    cartao_bruno = bruno.post(
        f"/api/colunas/{quadro_bruno['colunas'][0]['id']}/cartoes", json={"titulo": "Do Bruno"}
    ).get_json()

    resposta = bruno.put(
        f"/api/cartoes/{cartao_bruno['id']}/mover", json={"coluna_id": quadro_ana["colunas"][1]["id"], "posicao": 0}
    )

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Coluna não encontrada"}
