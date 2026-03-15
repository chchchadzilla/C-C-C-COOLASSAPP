# ═══════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from models import User

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            # Force password change if flagged
            if user.must_change_password:
                flash('You must change your password before continuing.', 'warning')
                return redirect(url_for('auth.change_password'))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Invalid credentials', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/test-login')
def test_login():
    """Quick dev endpoint — only available when USING_DEFAULT_SECRET (dev mode)."""
    if not current_app.config.get('USING_DEFAULT_SECRET'):
        flash('Test login is disabled in production.', 'error')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username='admin').first()
    if user:
        login_user(user, remember=True)
        if user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return redirect(url_for('dashboard.index'))
    return 'No admin user found', 404


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Force or voluntary password change."""
    if request.method == 'POST':
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if not check_password_hash(current_user.password_hash, current_pw):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html',
                                   forced=current_user.must_change_password)

        if len(new_pw) < 8:
            flash('New password must be at least 8 characters.', 'error')
            return render_template('auth/change_password.html',
                                   forced=current_user.must_change_password)

        if new_pw != confirm_pw:
            flash('Passwords do not match.', 'error')
            return render_template('auth/change_password.html',
                                   forced=current_user.must_change_password)

        if current_pw == new_pw:
            flash('New password must be different from current password.', 'error')
            return render_template('auth/change_password.html',
                                   forced=current_user.must_change_password)

        current_user.password_hash = generate_password_hash(new_pw)
        current_user.must_change_password = False
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html',
                           forced=current_user.must_change_password)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        display_name = request.form.get('display_name', username)
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            display_name=display_name,
            role='admin' if User.query.count() == 0 else 'developer'
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
