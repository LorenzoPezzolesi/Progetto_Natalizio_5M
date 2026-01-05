import os
from flask import Flask


def create_app(test_config=None):
    """
    Application Factory per creare l'istanza Flask.
    Segue le best practices Flask per la configurazione modulare.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        DATABASE=os.path.join(app.instance_path, 'skilltracker.db'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Assicura che la cartella instance esista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inizializza il database
    from app.db import init_app
    init_app(app)

    # Registra i Blueprints
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
