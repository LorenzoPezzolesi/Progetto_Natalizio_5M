from app.db import get_db
from app.modelli import Session, create_session_from_row


class SessionRepository:
    """
    Repository per la gestione delle sessioni di pratica nel database.
    """

    @staticmethod
    def create(skill_id, user_id, date, duration_minutes, xp_gained, notes=None):
        """
        Crea una nuova sessione.

        Returns:
            int: ID della nuova sessione
        """
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO sessions (skill_id, user_id, date, duration_minutes, xp_gained, notes)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (skill_id, user_id, date, duration_minutes, xp_gained, notes)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(session_id):
        """
        Recupera una sessione per ID.

        Returns:
            Session o None
        """
        db = get_db()
        row = db.execute('''
            SELECT se.*, sk.name as skill_name
            FROM sessions se
            JOIN skills sk ON se.skill_id = sk.id
            WHERE se.id = ?
        ''', (session_id,)).fetchone()

        if row is None:
            return None
        return create_session_from_row(row)

    @staticmethod
    def get_all_by_user(user_id, limit=None):
        """
        Recupera tutte le sessioni di un utente.

        Returns:
            list[Session]
        """
        db = get_db()
        query = '''
            SELECT se.*, sk.name as skill_name
            FROM sessions se
            JOIN skills sk ON se.skill_id = sk.id
            WHERE se.user_id = ?
            ORDER BY se.date DESC, se.created_at DESC
        '''
        if limit:
            query += f' LIMIT {limit}'

        rows = db.execute(query, (user_id,)).fetchall()
        return [create_session_from_row(row) for row in rows]

    @staticmethod
    def get_by_skill(skill_id):
        """
        Recupera tutte le sessioni di una skill.

        Returns:
            list[Session]
        """
        db = get_db()
        rows = db.execute('''
            SELECT se.*, sk.name as skill_name
            FROM sessions se
            JOIN skills sk ON se.skill_id = sk.id
            WHERE se.skill_id = ?
            ORDER BY se.date DESC
        ''', (skill_id,)).fetchall()

        return [create_session_from_row(row) for row in rows]

    @staticmethod
    def update(session_id, date=None, duration_minutes=None, xp_gained=None, notes=None):
        """
        Aggiorna una sessione.

        Returns:
            bool: True se aggiornata con successo
        """
        db = get_db()
        session = SessionRepository.get_by_id(session_id)
        if session is None:
            return False

        new_date = date if date is not None else session.date
        new_duration = duration_minutes if duration_minutes is not None else session.duration_minutes
        new_xp = xp_gained if xp_gained is not None else session.xp_gained
        new_notes = notes if notes is not None else session.notes

        db.execute('''
            UPDATE sessions
            SET date = ?, duration_minutes = ?, xp_gained = ?, notes = ?
            WHERE id = ?
        ''', (new_date, new_duration, new_xp, new_notes, session_id))
        db.commit()
        return True

    @staticmethod
    def delete(session_id):
        """
        Elimina una sessione.

        Returns:
            bool: True se eliminata con successo
        """
        db = get_db()
        db.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        db.commit()
        return True

    @staticmethod
    def get_stats_by_user(user_id):
        """
        Recupera statistiche aggregate delle sessioni per l'utente.

        Returns:
            dict: Statistiche
        """
        db = get_db()
        row = db.execute('''
            SELECT
                COUNT(*) as total_sessions,
                COALESCE(SUM(duration_minutes), 0) as total_minutes,
                COALESCE(SUM(xp_gained), 0) as total_xp_gained,
                COALESCE(AVG(duration_minutes), 0) as avg_duration
            FROM sessions
            WHERE user_id = ?
        ''', (user_id,)).fetchone()

        return {
            'total_sessions': row['total_sessions'],
            'total_minutes': row['total_minutes'],
            'total_hours': round(row['total_minutes'] / 60, 1),
            'total_xp_gained': row['total_xp_gained'],
            'avg_duration': round(row['avg_duration'], 0)
        }

    @staticmethod
    def get_recent_by_user(user_id, days=7):
        """
        Recupera le sessioni degli ultimi N giorni.

        Returns:
            list[Session]
        """
        db = get_db()
        rows = db.execute('''
            SELECT se.*, sk.name as skill_name
            FROM sessions se
            JOIN skills sk ON se.skill_id = sk.id
            WHERE se.user_id = ? AND se.date >= date('now', ?)
            ORDER BY se.date DESC
        ''', (user_id, f'-{days} days')).fetchall()

        return [create_session_from_row(row) for row in rows]
