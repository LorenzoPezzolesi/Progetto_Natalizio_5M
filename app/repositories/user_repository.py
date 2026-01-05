from app.db import get_db
from app.modelli import User, create_user_from_row


class UserRepository:
    """
    Repository per la gestione degli utenti nel database.
    Implementa il pattern Repository per separare la logica di accesso ai dati.
    """

    @staticmethod
    def create(username, email, password_hash):
        """
        Crea un nuovo utente nel database.

        Returns:
            int: ID del nuovo utente
        """
        db = get_db()
        cursor = db.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(user_id):
        """
        Recupera un utente per ID.

        Returns:
            User o None
        """
        db = get_db()
        row = db.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if row is None:
            return None
        return create_user_from_row(row)

    @staticmethod
    def get_by_username(username):
        """
        Recupera un utente per username.

        Returns:
            User o None
        """
        db = get_db()
        row = db.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        if row is None:
            return None
        return create_user_from_row(row)

    @staticmethod
    def get_by_email(email):
        """
        Recupera un utente per email.

        Returns:
            User o None
        """
        db = get_db()
        row = db.execute(
            'SELECT * FROM users WHERE email = ?',
            (email,)
        ).fetchone()

        if row is None:
            return None
        return create_user_from_row(row)

    @staticmethod
    def update(user_id, username=None, email=None, password_hash=None):
        """
        Aggiorna i dati di un utente.

        Returns:
            bool: True se aggiornato con successo
        """
        db = get_db()
        user = UserRepository.get_by_id(user_id)
        if user is None:
            return False

        new_username = username if username else user.username
        new_email = email if email else user.email
        new_password = password_hash if password_hash else user.password_hash

        db.execute(
            'UPDATE users SET username = ?, email = ?, password_hash = ? WHERE id = ?',
            (new_username, new_email, new_password, user_id)
        )
        db.commit()
        return True

    @staticmethod
    def delete(user_id):
        """
        Elimina un utente dal database.

        Returns:
            bool: True se eliminato con successo
        """
        db = get_db()
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        return True

    @staticmethod
    def exists_username(username):
        """
        Verifica se esiste già un utente con questo username.
        """
        db = get_db()
        row = db.execute(
            'SELECT 1 FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        return row is not None

    @staticmethod
    def exists_email(email):
        """
        Verifica se esiste già un utente con questa email.
        """
        db = get_db()
        row = db.execute(
            'SELECT 1 FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        return row is not None
