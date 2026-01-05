from app.db import get_db
from app.modelli import Category, create_category_from_row


class CategoryRepository:
    """
    Repository per la gestione delle categorie nel database.
    """

    @staticmethod
    def create(name, user_id, icon='📚'):
        """
        Crea una nuova categoria.

        Returns:
            int: ID della nuova categoria
        """
        db = get_db()
        cursor = db.execute(
            'INSERT INTO categories (name, icon, user_id) VALUES (?, ?, ?)',
            (name, icon, user_id)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(category_id):
        """
        Recupera una categoria per ID.

        Returns:
            Category o None
        """
        db = get_db()
        row = db.execute(
            'SELECT * FROM categories WHERE id = ?',
            (category_id,)
        ).fetchone()

        if row is None:
            return None
        return create_category_from_row(row)

    @staticmethod
    def get_all_by_user(user_id):
        """
        Recupera tutte le categorie di un utente.

        Returns:
            list[Category]
        """
        db = get_db()
        rows = db.execute(
            'SELECT * FROM categories WHERE user_id = ? ORDER BY name',
            (user_id,)
        ).fetchall()

        return [create_category_from_row(row) for row in rows]

    @staticmethod
    def update(category_id, name=None, icon=None):
        """
        Aggiorna una categoria.

        Returns:
            bool: True se aggiornata con successo
        """
        db = get_db()
        category = CategoryRepository.get_by_id(category_id)
        if category is None:
            return False

        new_name = name if name else category.name
        new_icon = icon if icon else category.icon

        db.execute(
            'UPDATE categories SET name = ?, icon = ? WHERE id = ?',
            (new_name, new_icon, category_id)
        )
        db.commit()
        return True

    @staticmethod
    def delete(category_id):
        """
        Elimina una categoria.

        Returns:
            bool: True se eliminata con successo
        """
        db = get_db()
        db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        db.commit()
        return True

    @staticmethod
    def get_with_skill_count(user_id):
        """
        Recupera le categorie con il conteggio delle skills.

        Returns:
            list[dict]: Lista di dizionari con dati categoria e conteggio
        """
        db = get_db()
        rows = db.execute('''
            SELECT c.*, COUNT(s.id) as skill_count
            FROM categories c
            LEFT JOIN skills s ON c.id = s.category_id
            WHERE c.user_id = ?
            GROUP BY c.id
            ORDER BY c.name
        ''', (user_id,)).fetchall()

        result = []
        for row in rows:
            category = create_category_from_row(row)
            result.append({
                'category': category,
                'skill_count': row['skill_count']
            })
        return result
