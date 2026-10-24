"""Ponto de entrada do AirPlan: cria e configura o app Flask."""
from flask import Flask

import db
from config import Config
from controllers import (
    auth_controller,
    cartao_controller,
    coluna_controller,
    pagina_controller,
    quadro_controller,
    usuario_controller,
)
from controllers.json_provider import JsonProvider
from controllers.tratador_erros import registrar_tratadores_de_erro


def create_app(config=Config):
    """Cria o app Flask com a configuração informada (produção/dev ou testes)."""
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="public/static",
    )
    app.config.from_object(config)

    if not app.config.get("SECRET_KEY") or not app.config.get("DATABASE_URL"):
        raise RuntimeError(
            "Configure FLASK_SECRET_KEY e DATABASE_URL no arquivo .env "
            "(use o .env.example como modelo)."
        )

    app.json = JsonProvider(app)

    db.init_app(app)
    registrar_tratadores_de_erro(app)
    app.register_blueprint(auth_controller.bp)
    app.register_blueprint(usuario_controller.bp)
    app.register_blueprint(quadro_controller.bp)
    app.register_blueprint(coluna_controller.bp)
    app.register_blueprint(cartao_controller.bp)
    app.register_blueprint(pagina_controller.bp)
    return app


# Instância usada por `flask --app app run` e pelo gunicorn (`gunicorn app:app`).
app = create_app()
