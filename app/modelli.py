from datetime import datetime, date

class User:
    """
    Rappresenta un utente registrato nel sistema.
    """

    def __init__(self, id, username, email, password_hash, created_at):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
    
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.id == other.id


class Category:
    """
    Rappresenta una categoria per raggruppare skills.
    """
    
    def __init__(self, id, name, icon, user_id):
        self.id = id
        self.name = name
        self.icon = icon
        self.user_id = user_id
    
    def __repr__(self):
        return f"Category(id={self.id}, name='{self.name}', icon='{self.icon}')"
    
    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def __eq__(self, other):
        if not isinstance(other, Category):
            return False
        return self.id == other.id


class Skill:
    """
    Rappresenta una competenza che l'utente vuole sviluppare.
    Include logica per calcolare progressi e XP necessari.
    """
    
    def __init__(self, id, name, description, current_level, target_level, 
                 total_xp, category_id, user_id, created_at, category_name=None):
        self.id = id
        self.name = name
        self.description = description
        self.current_level = current_level
        self.target_level = target_level
        self.total_xp = total_xp
        self.category_id = category_id
        self.user_id = user_id
        self.created_at = created_at
        self.category_name = category_name  # Campo aggiunto dai JOIN
    
    def __repr__(self):
        return (f"Skill(id={self.id}, name='{self.name}', "
                f"level={self.current_level}/{self.target_level}, xp={self.total_xp})")
    
    def __str__(self):
        return f"{self.name} (Livello {self.current_level})"
    
    def __eq__(self, other):
        if not isinstance(other, Skill):
            return False
        return self.id == other.id
    
    # ========================================================================
    # METODI DI BUSINESS LOGIC
    # ========================================================================
    
    def get_progress_percentage(self):
        """
        Calcola la percentuale di progresso verso l'obiettivo finale.
        
        Returns:
            float: Percentuale tra 0 e 100
            
        Esempio:
            skill.current_level = 7
            skill.target_level = 10
            -> ritorna 70.0
        """
        if self.target_level == 0:
            return 0
        return min(100, (self.current_level / self.target_level) * 100)
    
    def get_xp_for_next_level(self):
        """
        Calcola quanti XP totali servono per passare al livello successivo.
        
        Formula: livello_attuale * 100
        
        Returns:
            int: XP necessari per il prossimo livello
            
        Esempio:
            skill.current_level = 3
            -> ritorna 300 (servono 300 XP per passare da livello 3 a 4)
        """
        return self.current_level * 100
    
    def get_current_level_xp(self):
        """
        Calcola quanti XP hai accumulato NEL livello attuale.
        (non gli XP totali, ma solo quelli del livello corrente)
        
        Formula: total_xp - (somma XP dei livelli precedenti)
        
        Returns:
            int: XP accumulati nel livello attuale
            
        Esempio:
            skill.current_level = 3
            skill.total_xp = 450
            
            XP usati per i livelli precedenti:
            - Livello 1: 100 XP
            - Livello 2: 200 XP
            - Totale: 300 XP
            
            XP nel livello attuale: 450 - 300 = 150 XP
        """
        # Calcola la somma degli XP usati per i livelli precedenti
        xp_used_for_previous_levels = sum(i * 100 for i in range(1, self.current_level))
        
        # XP rimanenti nel livello attuale
        return self.total_xp - xp_used_for_previous_levels
    
    def get_xp_needed_for_next_level(self):
        """
        Calcola quanti XP mancano per raggiungere il prossimo livello.
        
        Returns:
            int: XP mancanti
            
        Esempio:
            skill.current_level = 3 (serve 300 XP per passare a 4)
            current_level_xp = 150
            -> ritorna 150 (mancano 150 XP)
        """
        xp_for_next = self.get_xp_for_next_level()
        current_xp = self.get_current_level_xp()
        return max(0, xp_for_next - current_xp)
    
    def is_complete(self):
        """
        Verifica se la skill ha raggiunto l'obiettivo.
        
        Returns:
            bool: True se current_level >= target_level
        """
        return self.current_level >= self.target_level
    
    def get_completion_percentage(self):
        """
        Alias più esplicito di get_progress_percentage.
        """
        return self.get_progress_percentage()


class Session:
    """
    Rappresenta una sessione di pratica per una skill.
    """
    
    def __init__(self, id, skill_id, date, duration_minutes, xp_gained, 
                 notes, user_id, created_at, skill_name=None):
        self.id = id
        self.skill_id = skill_id
        self.date = date
        self.duration_minutes = duration_minutes
        self.xp_gained = xp_gained
        self.notes = notes
        self.user_id = user_id
        self.created_at = created_at
        self.skill_name = skill_name  # Campo aggiunto dai JOIN
    
    def __repr__(self):
        return (f"Session(id={self.id}, skill_id={self.skill_id}, "
                f"date='{self.date}', duration={self.duration_minutes}min, xp={self.xp_gained})")
    
    def __str__(self):
        return f"Sessione del {self.date} - {self.duration_minutes} min (+{self.xp_gained} XP)"
    
    def __eq__(self, other):
        if not isinstance(other, Session):
            return False
        return self.id == other.id
    
    # ========================================================================
    # METODI DI BUSINESS LOGIC
    # ========================================================================
    
    def get_duration_hours(self):
        """
        Converte la durata da minuti a ore (formato decimale).
        
        Returns:
            float: Durata in ore
            
        Esempio:
            duration_minutes = 90
            -> ritorna 1.5
        """
        return self.duration_minutes / 60
    
    def format_duration(self):
        """
        Formatta la durata in modo leggibile.
        
        Returns:
            str: Durata formattata (es: "1h 30m", "45m")
        """
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    def has_notes(self):
        """
        Verifica se la sessione ha delle note.
        
        Returns:
            bool: True se ci sono note
        """
        return self.notes is not None and self.notes.strip() != ""


# ============================================================================
# FUNZIONI HELPER (opzionali ma utili)
# ============================================================================

def create_user_from_row(row):
    """
    Crea un oggetto User da una row del database.
    
    Args:
        row: sqlite3.Row object
        
    Returns:
        User: Oggetto User creato
    """
    return User(
        id=row['id'],
        username=row['username'],
        email=row['email'],
        password_hash=row['password_hash'],
        created_at=row['created_at']
    )


def create_category_from_row(row):
    """
    Crea un oggetto Category da una row del database.
    """
    return Category(
        id=row['id'],
        name=row['name'],
        icon=row['icon'],
        user_id=row['user_id']
    )


def create_skill_from_row(row):
    """
    Crea un oggetto Skill da una row del database.
    """
    # sqlite3.Row non ha .get(), usiamo row.keys() per verificare campi opzionali
    keys = row.keys()
    return Skill(
        id=row['id'],
        name=row['name'],
        description=row['description'],
        current_level=row['current_level'],
        target_level=row['target_level'],
        total_xp=row['total_xp'],
        category_id=row['category_id'],
        user_id=row['user_id'],
        created_at=row['created_at'],
        category_name=row['category_name'] if 'category_name' in keys else None
    )


def create_session_from_row(row):
    """
    Crea un oggetto Session da una row del database.
    """
    # sqlite3.Row non ha .get(), usiamo row.keys() per verificare campi opzionali
    keys = row.keys()
    return Session(
        id=row['id'],
        skill_id=row['skill_id'],
        date=row['date'],
        duration_minutes=row['duration_minutes'],
        xp_gained=row['xp_gained'],
        notes=row['notes'],
        user_id=row['user_id'],
        created_at=row['created_at'],
        skill_name=row['skill_name'] if 'skill_name' in keys else None
    )


# ============================================================================
# ESEMPIO D'USO (per capire come funziona)
# ============================================================================

if __name__ == '__main__':
    # Crea una skill di esempio
    skill = Skill(
        id=1,
        name="Python",
        description="Imparare la programmazione Python",
        current_level=3,
        target_level=10,
        total_xp=450,
        category_id=1,
        user_id=1,
        created_at=datetime.now(),
        category_name="Programmazione"
    )
    
    print(skill)  # Python (Livello 3)
    print(repr(skill))  # Skill(id=1, name='Python', level=3/10, xp=450)
    
    # Usa i metodi
    print(f"Progresso: {skill.get_progress_percentage():.1f}%")  # 30.0%
    print(f"XP per livello successivo: {skill.get_xp_for_next_level()}")  # 300
    print(f"XP nel livello attuale: {skill.get_current_level_xp()}")  # 150
    print(f"XP mancanti: {skill.get_xp_needed_for_next_level()}")  # 150
    print(f"Completato? {skill.is_complete()}")  # False
    
    # Crea una sessione
    session = Session(
        id=1,
        skill_id=1,
        date=date.today(),
        duration_minutes=90,
        xp_gained=30,
        notes="Studiato le liste e i dizionari",
        user_id=1,
        created_at=datetime.now(),
        skill_name="Python"
    )
    
    print(session)  # Sessione del 2025-01-05 - 90 min (+30 XP)
    print(f"Durata: {session.format_duration()}")  # 1h 30m
    print(f"Ha note? {session.has_notes()}")  # True