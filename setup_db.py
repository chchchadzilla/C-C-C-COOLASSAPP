"""Setup helper — Initialize database and create default admin user."""
import sys
import os

# Ensure we can import from project root
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash


def main():
    app = create_app()
    with app.app_context():
        print("       Database initialized.")

        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@coolassapp.local',
                password_hash=generate_password_hash('admin'),
                display_name='Administrator',
                role='admin',
                is_active=True,
                must_change_password=True,
            )
            db.session.add(admin)
            db.session.commit()
            print("       Default admin created (admin / admin)")
            print("       ⚠️  Admin will be forced to change password on first login")
        else:
            print("       Admin user already exists.")


if __name__ == '__main__':
    main()
