#!/usr/bin/env python3
"""
C-C-C-COOLASSAPP — Quick Launcher

Usage:
    python run.py              # Run in development mode
    python run.py --port 8080  # Custom port
    python run.py --prod       # Production mode (no debug)
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description='C-C-C-COOLASSAPP')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--prod', action='store_true', help='Run in production mode')
    args = parser.parse_args()

    # Set environment
    if not args.prod:
        os.environ.setdefault('FLASK_ENV', 'development')
        os.environ.setdefault('FLASK_DEBUG', '1')

    os.environ.setdefault('SECRET_KEY', 'claude-orchestration-dev-key-2026')

    from app import create_app, socketio

    app = create_app()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          C-C-C-COOLASSAPP         ║
╠══════════════════════════════════════════════════════════════╣
║  URL:   http://{args.host}:{args.port}                          ║
║  Mode:  {'Production' if args.prod else 'Development'}                                        ║
║  Debug: {'Off' if args.prod else 'On'}                                             ║
╚══════════════════════════════════════════════════════════════╝
    """)

    socketio.run(
        app,
        host=args.host,
        port=args.port,
        debug=not args.prod,
        allow_unsafe_werkzeug=not args.prod,
    )


if __name__ == '__main__':
    main()
