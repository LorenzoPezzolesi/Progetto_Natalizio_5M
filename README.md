# Skill Tracker

Applicazione web per monitorare lo sviluppo delle competenze personali con un sistema di esperienza (XP) e livelli.

![Flask](https://img.shields.io/badge/Flask-3.0+-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![SQLite](https://img.shields.io/badge/SQLite-3-green)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

---

## Indice

- [Funzionalita](#funzionalita)
- [Tecnologie](#tecnologie)
- [Installazione](#installazione)
- [Struttura Progetto](#struttura-progetto)
- [Schema Database](#schema-database)
- [Sistema XP e Livelli](#sistema-xp-e-livelli)

---

## Funzionalita

### Gestione Utenti
- Registrazione con username, email e password
- Login e logout sicuro
- Recupero password dimenticata (verifica username + email)
- Isolamento dati per utente (multi-tenant)

### Sistema Skills
- Creazione di skill personalizzate
- Definizione di livello attuale e target
- Associazione a categorie
- Calcolo automatico dei progressi
- Visualizzazione XP totali per skill
- Barre di progresso visive

### Sessioni di Pratica
- Registrazione sessioni di allenamento
- Tracciamento durata e XP guadagnati
- Data della sessione e note personalizzate
- Aggiornamento automatico livelli skill

### Categorie
- Creazione categorie personalizzate
- Assegnazione icone emoji
- Raggruppamento logico delle skill
- Conteggio skill per categoria

### Dashboard
- Panoramica statistiche (totale skills, XP, livello medio, ore totali)
- Visualizzazione ultimi 5 skill con barre di progresso
- Sessioni recenti (ultimi 7 giorni)
- Lista categorie create

---

## Tecnologie

### Backend
| Tecnologia | Versione | Descrizione |
|------------|----------|-------------|
| Flask | 3.0+ | Framework web Python |
| Werkzeug | 3.0+ | Sicurezza e password hashing |
| SQLite | 3 | Database file-based |
| Python | 3.10+ | Linguaggio di programmazione |

### Frontend
| Tecnologia | Versione | Descrizione |
|------------|----------|-------------|
| Bootstrap | 5 | Framework CSS responsive |
| jQuery | 3.7.1 | Libreria JavaScript |
| DataTables | 1.13+ | Tabelle interattive |
| Jinja2 | - | Template engine (Flask) |

---

## Installazione

### Prerequisiti
- Python 3.10 o superiore
- pip (package manager Python)

### Passaggi

1. **Posizionarsi nella cartella del progetto**
```bash
cd "path/to/Progetto_Natalizio_5M"
```

2. **Creare ambiente virtuale (raccomandato)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Installare dipendenze**
```bash
pip install -r requirements.txt
```

4. **Inizializzare il database**
```bash
flask init-db
```

5. **Avviare l'applicazione**
```bash
python run.py
```

6. **Accedere all'applicazione**
- Aprire browser: `http://localhost:5000`
- Registrare nuovo utente
- Iniziare a tracciare le skill!

---

## Struttura Progetto

```
Progetto_Natalizio_5M/
├── app/
│   ├── __init__.py              # Application Factory
│   ├── db.py                    # Configurazione Database
│   ├── modelli.py               # Modelli dati
│   ├── schema.sql               # Schema database
│   ├── blueprints/
│   │   ├── auth/                # Autenticazione
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── main/                # Funzionalita principali
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── repositories/            # Pattern Repository
│   │   ├── user_repository.py
│   │   ├── category_repository.py
│   │   ├── skill_repository.py
│   │   └── session_repository.py
│   ├── static/
│   │   ├── css/                 # Bootstrap + stili custom
│   │   └── js/                  # jQuery, DataTables, app.js
│   └── templates/
│       ├── base.html            # Template base
│       ├── auth/                # Template autenticazione
│       └── main/                # Template applicazione
├── instance/
│   └── skilltracker.db          # Database SQLite
├── run.py                       # Entry point
├── requirements.txt             # Dipendenze Python
└── README.md
```

---

## Schema Database

### Tabelle

**USERS**
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| id | INTEGER PK | ID univoco |
| username | TEXT UNIQUE | Nome utente |
| email | TEXT UNIQUE | Email |
| password_hash | TEXT | Hash password |
| created_at | TIMESTAMP | Data creazione |

**CATEGORIES**
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| id | INTEGER PK | ID univoco |
| name | TEXT | Nome categoria |
| icon | TEXT | Emoji icona |
| user_id | INTEGER FK | Riferimento utente |

**SKILLS**
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| id | INTEGER PK | ID univoco |
| name | TEXT | Nome skill |
| description | TEXT | Descrizione |
| current_level | INTEGER | Livello attuale |
| target_level | INTEGER | Livello obiettivo |
| total_xp | INTEGER | XP totali |
| category_id | INTEGER FK | Riferimento categoria |
| user_id | INTEGER FK | Riferimento utente |
| created_at | TIMESTAMP | Data creazione |

**SESSIONS**
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| id | INTEGER PK | ID univoco |
| skill_id | INTEGER FK | Riferimento skill |
| date | DATE | Data sessione |
| duration_minutes | INTEGER | Durata in minuti |
| xp_gained | INTEGER | XP guadagnati |
| notes | TEXT | Note |
| user_id | INTEGER FK | Riferimento utente |
| created_at | TIMESTAMP | Data creazione |

### Diagramma ER

```
USERS (1) ──────────── (N) CATEGORIES
   │                         │
   │                         │
   │                    (1)  │
   │                         ▼
   └──────────────── (N) SKILLS (1) ────── (N) SESSIONS
```

---

## Sistema XP e Livelli

### Formula Calcolo

Gli XP necessari per passare al livello successivo sono calcolati con la formula:

```
XP necessari per livello N = N * 100
```

**Esempio:**
- Livello 1 → 2: 100 XP
- Livello 2 → 3: 200 XP
- Livello 3 → 4: 300 XP
- Livello 4 → 5: 400 XP

**XP totali per raggiungere un livello:**
- Livello 2: 100 XP
- Livello 3: 300 XP (100 + 200)
- Livello 4: 600 XP (100 + 200 + 300)
- Livello 5: 1000 XP (100 + 200 + 300 + 400)

### XP Suggeriti

L'applicazione suggerisce automaticamente gli XP da assegnare basandosi sulla durata della sessione:

```
XP suggeriti = durata_minuti * 2
(equivalente a 120 XP per ora)
```

### Level-Up Automatico

Quando una skill accumula abbastanza XP, il sistema aggiorna automaticamente il livello:

```python
# Calcolo nuovo livello
while total_xp >= xp_for_next_level:
    current_level += 1
    total_xp -= xp_for_next_level
    xp_for_next_level = current_level * 100
```

### Barre di Progresso

Il progresso verso l'obiettivo viene mostrato con barre colorate:
- **0-50%** - Blu (primary)
- **50-99%** - Cyan (info)
- **100%** - Verde (success) - Obiettivo raggiunto!
