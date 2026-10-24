"""Configurações do AirPlan, lidas das variáveis de ambiente (arquivo .env)."""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuração usada no desenvolvimento e em produção."""

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # Cookie de sessão: inacessível ao JavaScript e enviado só para o próprio site.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Em produção (HTTPS no Render) o cookie só trafega criptografado.
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"


class TestConfig(Config):
    """Configuração dos testes: usa o mesmo banco do desenvolvimento (Supabase)."""

    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SESSION_COOKIE_SECURE = False
