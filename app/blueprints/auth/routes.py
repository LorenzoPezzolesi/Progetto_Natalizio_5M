import functools
from flask import (
    render_template, redirect, url_for, flash, request, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.blueprints.auth import bp
from app.repositories import UserRepository


def login_required(view):
    """
    Decoratore che richiede l'autenticazione per accedere a una route.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """
    Carica l'utente loggato prima di ogni richiesta.
    """
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = UserRepository.get_by_id(user_id)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registrazione nuovo utente.
    """
    if g.user is not None:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        error = None

        if not username:
            error = 'Username richiesto.'
        elif not email:
            error = 'Email richiesta.'
        elif not password:
            error = 'Password richiesta.'
        elif password != confirm_password:
            error = 'Le password non corrispondono.'
        elif len(password) < 6:
            error = 'La password deve essere di almeno 6 caratteri.'
        elif UserRepository.exists_username(username):
            error = f'Username "{username}" già registrato.'
        elif UserRepository.exists_email(email):
            error = f'Email "{email}" già registrata.'

        if error is None:
            password_hash = generate_password_hash(password)
            user_id = UserRepository.create(username, email, password_hash)
            session.clear()
            session['user_id'] = user_id
            flash('Registrazione completata con successo!', 'success')
            return redirect(url_for('main.dashboard'))

        flash(error, 'danger')

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login utente.
    """
    if g.user is not None:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        error = None
        user = UserRepository.get_by_username(username)

        if user is None:
            error = 'Credenziali non valide.'
        elif not check_password_hash(user.password_hash, password):
            error = 'Credenziali non valide.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            flash(f'Bentornato, {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))

        flash(error, 'danger')

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """
    Logout utente.
    """
    session.clear()
    flash('Logout effettuato con successo.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Richiesta reset password - verifica username e email.
    """
    if g.user is not None:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()

        error = None

        if not username:
            error = 'Username richiesto.'
        elif not email:
            error = 'Email richiesta.'
        else:
            user = UserRepository.get_by_username(username)
            if user is None or user.email.lower() != email.lower():
                error = 'Credenziali non valide.'

        if error is None:
            session['reset_user_id'] = user.id
            return redirect(url_for('auth.reset_password'))

        flash(error, 'danger')

    return render_template('auth/forgot_password.html')


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    Reset della password - inserimento nuova password.
    """
    if g.user is not None:
        return redirect(url_for('main.dashboard'))

    user_id = session.get('reset_user_id')
    if user_id is None:
        flash('Sessione scaduta. Riprova.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    user = UserRepository.get_by_id(user_id)
    if user is None:
        session.pop('reset_user_id', None)
        flash('Utente non trovato.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        error = None

        if not password:
            error = 'Password richiesta.'
        elif password != confirm_password:
            error = 'Le password non corrispondono.'
        elif len(password) < 6:
            error = 'La password deve essere di almeno 6 caratteri.'

        if error is None:
            password_hash = generate_password_hash(password)
            UserRepository.update(user_id, password_hash=password_hash)
            session.pop('reset_user_id', None)
            flash('Password aggiornata con successo! Effettua il login.', 'success')
            return redirect(url_for('auth.login'))

        flash(error, 'danger')

    # Maschera l'email (es. t***@gmail.com)
    email = user.email
    at_pos = email.find('@')
    if at_pos > 1:
        masked_email = email[0] + '*' * (at_pos - 1) + email[at_pos:]
    else:
        masked_email = email

    return render_template('auth/reset_password.html', masked_email=masked_email)
