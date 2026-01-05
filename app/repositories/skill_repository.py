from app.db import get_db
from app.modelli import Skill, create_skill_from_row


class SkillRepository:
    """
    Repository per la gestione delle skills nel database.
    """

    @staticmethod
    def create(name, user_id, description=None, target_level=10, category_id=None):
        """
        Crea una nuova skill.

        Returns:
            int: ID della nuova skill
        """
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO skills (name, description, target_level, category_id, user_id)
               VALUES (?, ?, ?, ?, ?)''',
            (name, description, target_level, category_id, user_id)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(skill_id):
        """
        Recupera una skill per ID con il nome della categoria.

        Returns:
            Skill o None
        """
        db = get_db()
        row = db.execute('''
            SELECT s.*, c.name as category_name
            FROM skills s
            LEFT JOIN categories c ON s.category_id = c.id
            WHERE s.id = ?
        ''', (skill_id,)).fetchone()

        if row is None:
            return None
        return create_skill_from_row(row)

    @staticmethod
    def get_all_by_user(user_id):
        """
        Recupera tutte le skills di un utente.

        Returns:
            list[Skill]
        """
        db = get_db()
        rows = db.execute('''
            SELECT s.*, c.name as category_name
            FROM skills s
            LEFT JOIN categories c ON s.category_id = c.id
            WHERE s.user_id = ?
            ORDER BY s.name
        ''', (user_id,)).fetchall()

        return [create_skill_from_row(row) for row in rows]

    @staticmethod
    def get_by_category(category_id, user_id):
        """
        Recupera le skills di una specifica categoria.

        Returns:
            list[Skill]
        """
        db = get_db()
        rows = db.execute('''
            SELECT s.*, c.name as category_name
            FROM skills s
            LEFT JOIN categories c ON s.category_id = c.id
            WHERE s.category_id = ? AND s.user_id = ?
            ORDER BY s.name
        ''', (category_id, user_id)).fetchall()

        return [create_skill_from_row(row) for row in rows]

    @staticmethod
    def update(skill_id, name=None, description=None, target_level=None, category_id=None):
        """
        Aggiorna una skill.

        Returns:
            bool: True se aggiornata con successo
        """
        db = get_db()
        skill = SkillRepository.get_by_id(skill_id)
        if skill is None:
            return False

        new_name = name if name is not None else skill.name
        new_description = description if description is not None else skill.description
        new_target_level = target_level if target_level is not None else skill.target_level
        new_category_id = category_id if category_id is not None else skill.category_id

        db.execute('''
            UPDATE skills
            SET name = ?, description = ?, target_level = ?, category_id = ?
            WHERE id = ?
        ''', (new_name, new_description, new_target_level, new_category_id, skill_id))
        db.commit()
        return True

    @staticmethod
    def add_xp(skill_id, xp_amount):
        """
        Aggiunge XP a una skill e aggiorna il livello se necessario.

        Returns:
            dict: Informazioni sull'aggiornamento (level_up, new_level, etc.)
        """
        db = get_db()
        skill = SkillRepository.get_by_id(skill_id)
        if skill is None:
            return None

        old_level = skill.current_level
        new_total_xp = skill.total_xp + xp_amount

        # Calcola il nuovo livello basandosi sugli XP totali
        new_level = 1
        xp_threshold = 0
        while True:
            xp_for_this_level = new_level * 100
            if new_total_xp >= xp_threshold + xp_for_this_level:
                xp_threshold += xp_for_this_level
                new_level += 1
            else:
                break

        db.execute('''
            UPDATE skills SET total_xp = ?, current_level = ? WHERE id = ?
        ''', (new_total_xp, new_level, skill_id))
        db.commit()

        return {
            'old_level': old_level,
            'new_level': new_level,
            'level_up': new_level > old_level,
            'total_xp': new_total_xp
        }

    @staticmethod
    def delete(skill_id):
        """
        Elimina una skill.

        Returns:
            bool: True se eliminata con successo
        """
        db = get_db()
        db.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
        db.commit()
        return True

    @staticmethod
    def get_stats_by_user(user_id):
        """
        Recupera statistiche aggregate per l'utente.

        Returns:
            dict: Statistiche (total_skills, total_xp, avg_level, etc.)
        """
        db = get_db()
        row = db.execute('''
            SELECT
                COUNT(*) as total_skills,
                COALESCE(SUM(total_xp), 0) as total_xp,
                COALESCE(AVG(current_level), 0) as avg_level,
                COALESCE(MAX(current_level), 0) as max_level
            FROM skills
            WHERE user_id = ?
        ''', (user_id,)).fetchone()

        return {
            'total_skills': row['total_skills'],
            'total_xp': row['total_xp'],
            'avg_level': round(row['avg_level'], 1),
            'max_level': row['max_level']
        }
