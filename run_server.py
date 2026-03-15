"""Simple server launcher - run this file directly."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # ─── Security warnings ────────────────────────────────────────────
    warnings = []
    if app.config.get('USING_DEFAULT_SECRET'):
        warnings.append("SECRET_KEY is using the insecure default — set SECRET_KEY env var")
    if os.environ.get('CORS_ORIGINS', '*') == '*':
        warnings.append("CORS_ORIGINS not set — all origins allowed")
    if not os.environ.get('FLASK_ENV') and not os.environ.get('PRODUCTION'):
        warnings.append("Running in development mode")

    print("Starting C-C-C-COOLASSAPP server on http://127.0.0.1:5000")
    if warnings:
        print("\n  ⚠️  Security Warnings:")
        for w in warnings:
            print(f"     • {w}")
        print()
    print("Open http://127.0.0.1:5000/login for normal login")
    app.run(host='127.0.0.1', port=5000, debug=False)
