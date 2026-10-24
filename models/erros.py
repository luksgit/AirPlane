"""Erros de domínio levantados pelos models.

O model não conhece HTTP: ele só diz *o que* deu errado. Quem traduz cada erro
para um status (400, 404, 409) é o `controllers/tratador_erros.py`.
"""


class ErroValidacao(Exception):
    """Dados inválidos. `campos` liga cada campo do formulário à sua mensagem."""

    def __init__(self, campos, mensagem="Verifique os campos destacados"):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campos = campos


class ErroConflito(Exception):
    """A operação conflita com dados existentes (ex.: e-mail já cadastrado)."""

    def __init__(self, mensagem, campos=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campos = campos


class NaoEncontrado(Exception):
    """O registro não existe ou não pertence ao usuário logado."""

    def __init__(self, mensagem="Não encontrado"):
        super().__init__(mensagem)
        self.mensagem = mensagem
