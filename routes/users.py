# ═══════════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User, Agent

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@login_required
def list_users():
    """List all team members."""
    users = User.query.all()
    return render_template('users/list.html', users=users)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """Add a new team member."""
    if current_user.role not in ('admin', 'orchestrator'):
        flash('Only admins and orchestrators can add users', 'error')
        return redirect(url_for('users.list_users'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        display_name = request.form.get('display_name', username)
        role = request.form.get('role', 'developer')
        max_agents = int(request.form.get('max_agents', 10))
        password = request.form.get('password', 'changeme123')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('users/add.html')
        
        user = User(
            username=username,
            email=email,
            display_name=display_name,
            password_hash=generate_password_hash(password),
            role=role,
            max_agents=max_agents,
            target_agent_count=3  # Start at 3 per Day 5 plan
        )
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {display_name} added successfully', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/add.html')


@users_bp.route('/<int:user_id>')
@login_required
def view_user(user_id):
    """View detailed user profile with their agents."""
    user = User.query.get_or_404(user_id)
    agents = Agent.query.filter_by(user_id=user_id).all()
    return render_template('users/detail.html', user=user, agents=agents)


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user settings."""
    if current_user.role not in ('admin', 'orchestrator') and current_user.id != user_id:
        flash('Insufficient permissions', 'error')
        return redirect(url_for('users.list_users'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.display_name = request.form.get('display_name', user.display_name)
        user.email = request.form.get('email', user.email)
        user.role = request.form.get('role', user.role)
        user.max_agents = int(request.form.get('max_agents', user.max_agents))
        user.target_agent_count = int(request.form.get('target_agent_count', user.target_agent_count))
        user.notes = request.form.get('notes', user.notes)
        
        if request.form.get('password'):
            user.password_hash = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash('User updated', 'success')
        return redirect(url_for('users.view_user', user_id=user_id))
    
    return render_template('users/edit.html', user=user)


@users_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@login_required
def deactivate_user(user_id):
    """Deactivate a user and their agents."""
    if current_user.role not in ('admin', 'orchestrator'):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('users.list_users'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = False
    
    # Terminate all their agents
    for agent in user.agents:
        agent.status = 'terminated'
    
    db.session.commit()
    flash(f'User {user.display_name} deactivated', 'warning')
    return redirect(url_for('users.list_users'))


@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@login_required
def activate_user(user_id):
    """Re-activate a user."""
    if current_user.role not in ('admin', 'orchestrator'):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('users.list_users'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f'User {user.display_name} activated', 'success')
    return redirect(url_for('users.list_users'))


@users_bp.route('/<int:user_id>/scale', methods=['POST'])
@login_required
def scale_agents(user_id):
    """Scale agent count for a user (during 2-week ramp)."""
    if current_user.role not in ('admin', 'orchestrator'):
        if request.is_json:
            return jsonify({'error': 'Insufficient permissions'}), 403
        flash('Insufficient permissions', 'error')
        return redirect(url_for('users.list_users'))
    
    user = User.query.get_or_404(user_id)
    data = request.json if request.is_json else request.form
    target = int(data.get('target_count', user.target_agent_count))
    
    if target > user.max_agents:
        if request.is_json:
            return jsonify({'error': f'Cannot exceed max agents ({user.max_agents})'}), 400
        flash(f'Cannot exceed max agents ({user.max_agents})', 'error')
        return redirect(url_for('users.user_detail', user_id=user_id))
    
    user.target_agent_count = target
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'target': target})
    
    flash(f'Agent target scaled to {target}', 'success')
    return redirect(url_for('users.user_detail', user_id=user_id))
