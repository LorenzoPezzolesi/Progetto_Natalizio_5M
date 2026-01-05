from datetime import date
from flask import render_template, redirect, url_for, flash, request, g

from app.blueprints.main import bp
from app.blueprints.auth.routes import login_required
from app.repositories import CategoryRepository, SkillRepository, SessionRepository


# ============================================================================
# DASHBOARD
# ============================================================================

@bp.route('/')
@login_required
def dashboard():
    """
    Dashboard principale con statistiche e panoramica.
    """
    skills = SkillRepository.get_all_by_user(g.user.id)
    skill_stats = SkillRepository.get_stats_by_user(g.user.id)
    session_stats = SessionRepository.get_stats_by_user(g.user.id)
    recent_sessions = SessionRepository.get_recent_by_user(g.user.id, days=7)
    categories = CategoryRepository.get_with_skill_count(g.user.id)

    return render_template('main/dashboard.html',
                           skills=skills,
                           skill_stats=skill_stats,
                           session_stats=session_stats,
                           recent_sessions=recent_sessions,
                           categories=categories)


# ============================================================================
# SKILLS CRUD
# ============================================================================

@bp.route('/skills')
@login_required
def skills_list():
    """
    Lista di tutte le skills dell'utente.
    """
    skills = SkillRepository.get_all_by_user(g.user.id)
    return render_template('main/skills/list.html', skills=skills)


@bp.route('/skills/new', methods=['GET', 'POST'])
@login_required
def skills_new():
    """
    Creazione di una nuova skill.
    """
    categories = CategoryRepository.get_all_by_user(g.user.id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        target_level = request.form.get('target_level', 10, type=int)
        category_id = request.form.get('category_id', type=int)

        error = None
        if not name:
            error = 'Il nome della skill è richiesto.'
        elif target_level < 1:
            error = 'Il livello obiettivo deve essere almeno 1.'

        if error is None:
            SkillRepository.create(
                name=name,
                user_id=g.user.id,
                description=description or None,
                target_level=target_level,
                category_id=category_id if category_id else None
            )
            flash(f'Skill "{name}" creata con successo!', 'success')
            return redirect(url_for('main.skills_list'))

        flash(error, 'danger')

    return render_template('main/skills/form.html',
                           skill=None,
                           categories=categories)


@bp.route('/skills/<int:skill_id>')
@login_required
def skills_detail(skill_id):
    """
    Dettaglio di una skill con le sessioni collegate.
    """
    skill = SkillRepository.get_by_id(skill_id)
    if skill is None or skill.user_id != g.user.id:
        flash('Skill non trovata.', 'danger')
        return redirect(url_for('main.skills_list'))

    sessions = SessionRepository.get_by_skill(skill_id)
    return render_template('main/skills/detail.html',
                           skill=skill,
                           sessions=sessions)


@bp.route('/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
@login_required
def skills_edit(skill_id):
    """
    Modifica di una skill esistente.
    """
    skill = SkillRepository.get_by_id(skill_id)
    if skill is None or skill.user_id != g.user.id:
        flash('Skill non trovata.', 'danger')
        return redirect(url_for('main.skills_list'))

    categories = CategoryRepository.get_all_by_user(g.user.id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        target_level = request.form.get('target_level', 10, type=int)
        category_id = request.form.get('category_id', type=int)

        error = None
        if not name:
            error = 'Il nome della skill è richiesto.'
        elif target_level < 1:
            error = 'Il livello obiettivo deve essere almeno 1.'

        if error is None:
            SkillRepository.update(
                skill_id=skill_id,
                name=name,
                description=description or None,
                target_level=target_level,
                category_id=category_id if category_id else None
            )
            flash(f'Skill "{name}" aggiornata con successo!', 'success')
            return redirect(url_for('main.skills_detail', skill_id=skill_id))

        flash(error, 'danger')

    return render_template('main/skills/form.html',
                           skill=skill,
                           categories=categories)


@bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def skills_delete(skill_id):
    """
    Eliminazione di una skill.
    """
    skill = SkillRepository.get_by_id(skill_id)
    if skill is None or skill.user_id != g.user.id:
        flash('Skill non trovata.', 'danger')
        return redirect(url_for('main.skills_list'))

    SkillRepository.delete(skill_id)
    flash(f'Skill "{skill.name}" eliminata.', 'info')
    return redirect(url_for('main.skills_list'))


# ============================================================================
# SESSIONS CRUD
# ============================================================================

@bp.route('/sessions')
@login_required
def sessions_list():
    """
    Lista di tutte le sessioni dell'utente.
    """
    sessions = SessionRepository.get_all_by_user(g.user.id)
    return render_template('main/sessions/list.html', sessions=sessions)


@bp.route('/sessions/new', methods=['GET', 'POST'])
@login_required
def sessions_new():
    """
    Creazione di una nuova sessione.
    """
    skills = SkillRepository.get_all_by_user(g.user.id)
    skill_id_preselected = request.args.get('skill_id', type=int)

    if request.method == 'POST':
        skill_id = request.form.get('skill_id', type=int)
        session_date = request.form.get('date', '')
        duration_minutes = request.form.get('duration_minutes', 0, type=int)
        xp_gained = request.form.get('xp_gained', 0, type=int)
        notes = request.form.get('notes', '').strip()

        error = None
        if not skill_id:
            error = 'Seleziona una skill.'
        elif not session_date:
            error = 'La data è richiesta.'
        elif duration_minutes < 1:
            error = 'La durata deve essere almeno 1 minuto.'
        elif xp_gained < 0:
            error = 'Gli XP non possono essere negativi.'

        # Verifica che la skill appartenga all'utente
        skill = SkillRepository.get_by_id(skill_id)
        if skill is None or skill.user_id != g.user.id:
            error = 'Skill non valida.'

        if error is None:
            SessionRepository.create(
                skill_id=skill_id,
                user_id=g.user.id,
                date=session_date,
                duration_minutes=duration_minutes,
                xp_gained=xp_gained,
                notes=notes or None
            )
            # Aggiorna gli XP della skill
            result = SkillRepository.add_xp(skill_id, xp_gained)
            if result and result['level_up']:
                flash(f'Congratulazioni! {skill.name} è salita al livello {result["new_level"]}!', 'warning')
            flash('Sessione registrata con successo!', 'success')
            return redirect(url_for('main.sessions_list'))

        flash(error, 'danger')

    return render_template('main/sessions/form.html',
                           session=None,
                           skills=skills,
                           skill_id_preselected=skill_id_preselected,
                           today=date.today().isoformat())


@bp.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
@login_required
def sessions_edit(session_id):
    """
    Modifica di una sessione esistente.
    """
    session_obj = SessionRepository.get_by_id(session_id)
    if session_obj is None or session_obj.user_id != g.user.id:
        flash('Sessione non trovata.', 'danger')
        return redirect(url_for('main.sessions_list'))

    skills = SkillRepository.get_all_by_user(g.user.id)

    if request.method == 'POST':
        session_date = request.form.get('date', '')
        duration_minutes = request.form.get('duration_minutes', 0, type=int)
        xp_gained = request.form.get('xp_gained', 0, type=int)
        notes = request.form.get('notes', '').strip()

        error = None
        if not session_date:
            error = 'La data è richiesta.'
        elif duration_minutes < 1:
            error = 'La durata deve essere almeno 1 minuto.'
        elif xp_gained < 0:
            error = 'Gli XP non possono essere negativi.'

        if error is None:
            SessionRepository.update(
                session_id=session_id,
                date=session_date,
                duration_minutes=duration_minutes,
                xp_gained=xp_gained,
                notes=notes or None
            )
            flash('Sessione aggiornata con successo!', 'success')
            return redirect(url_for('main.sessions_list'))

        flash(error, 'danger')

    return render_template('main/sessions/form.html',
                           session=session_obj,
                           skills=skills,
                           skill_id_preselected=None,
                           today=date.today().isoformat())


@bp.route('/sessions/<int:session_id>/delete', methods=['POST'])
@login_required
def sessions_delete(session_id):
    """
    Eliminazione di una sessione.
    """
    session_obj = SessionRepository.get_by_id(session_id)
    if session_obj is None or session_obj.user_id != g.user.id:
        flash('Sessione non trovata.', 'danger')
        return redirect(url_for('main.sessions_list'))

    # Sottrai gli XP dalla skill PRIMA di eliminare la sessione
    SkillRepository.add_xp(session_obj.skill_id, -session_obj.xp_gained)

    SessionRepository.delete(session_id)
    flash('Sessione eliminata.', 'info')
    return redirect(url_for('main.sessions_list'))


# ============================================================================
# CATEGORIES CRUD
# ============================================================================

@bp.route('/categories')
@login_required
def categories_list():
    """
    Lista di tutte le categorie dell'utente.
    """
    categories = CategoryRepository.get_with_skill_count(g.user.id)
    return render_template('main/categories/list.html', categories=categories)


@bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def categories_new():
    """
    Creazione di una nuova categoria.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        icon = request.form.get('icon', '').strip() or '📚'

        error = None
        if not name:
            error = 'Il nome della categoria è richiesto.'

        if error is None:
            CategoryRepository.create(name=name, user_id=g.user.id, icon=icon)
            flash(f'Categoria "{name}" creata con successo!', 'success')
            return redirect(url_for('main.categories_list'))

        flash(error, 'danger')

    return render_template('main/categories/form.html', category=None)


@bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def categories_edit(category_id):
    """
    Modifica di una categoria esistente.
    """
    category = CategoryRepository.get_by_id(category_id)
    if category is None or category.user_id != g.user.id:
        flash('Categoria non trovata.', 'danger')
        return redirect(url_for('main.categories_list'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        icon = request.form.get('icon', '').strip() or '📚'

        error = None
        if not name:
            error = 'Il nome della categoria è richiesto.'

        if error is None:
            CategoryRepository.update(category_id=category_id, name=name, icon=icon)
            flash(f'Categoria "{name}" aggiornata con successo!', 'success')
            return redirect(url_for('main.categories_list'))

        flash(error, 'danger')

    return render_template('main/categories/form.html', category=category)


@bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def categories_delete(category_id):
    """
    Eliminazione di una categoria.
    """
    category = CategoryRepository.get_by_id(category_id)
    if category is None or category.user_id != g.user.id:
        flash('Categoria non trovata.', 'danger')
        return redirect(url_for('main.categories_list'))

    CategoryRepository.delete(category_id)
    flash(f'Categoria "{category.name}" eliminata.', 'info')
    return redirect(url_for('main.categories_list'))
