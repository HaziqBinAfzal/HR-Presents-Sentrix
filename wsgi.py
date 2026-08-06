"""Production WSGI entrypoint for Sentrix."""

from app import create_app


application = create_app()
app = application
