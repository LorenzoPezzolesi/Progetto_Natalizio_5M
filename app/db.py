import sqlite3
import click
from flask import current_app, g


def get_db():
    """
    Ottiene la connessione al database per la richiesta corrente.
    Se non esiste, ne crea una nuova.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Chiude la connessione al database se esiste.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """
    Inizializza il database eseguendo lo schema SQL.
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """
    Comando CLI per inizializzare il database.
    Uso: flask init-db
    """
    init_db()
    click.echo('Database inizializzato.')


def init_app(app):
    """
    Registra le funzioni del database con l'app Flask.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
