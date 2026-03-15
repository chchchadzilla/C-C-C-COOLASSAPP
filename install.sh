#!/usr/bin/env bash
# ============================================================================
#  C-C-C-COOLASSAPP — One-Click macOS / Linux Installer
#
#  Carefully-Crafted-Claude-Code Original Orchestration Layer
#  And Super Serious Appropriately Positioned Project
#
#  Usage:
#    chmod +x install.sh
#    ./install.sh
# ============================================================================

set -e

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo ""
echo -e "${CYAN}${BOLD} ============================================================================${NC}"
echo -e "${CYAN}${BOLD}  🧊 C-C-C-COOLASSAPP — One-Click Installer${NC}"
echo -e "${CYAN}${BOLD} ============================================================================${NC}"
echo ""

# ── Step 0: Check we're in the right folder ──────────────────────────────────

if [ ! -f "app.py" ]; then
    echo -e "${RED} [ERROR] app.py not found in the current directory.${NC}"
    echo "         Make sure you run this from the C-C-C-COOLASSAPP project folder."
    echo ""
    echo " Current directory: $(pwd)"
    echo ""
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED} [ERROR] requirements.txt not found.${NC}"
    echo "         This doesn't look like the right project folder."
    echo ""
    exit 1
fi

echo -e " ${GREEN}[OK]${NC} Project files found."
echo ""

# ── Detect Python command ────────────────────────────────────────────────────

PYTHON_CMD=""

if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

# ── Step 1: Check Python ────────────────────────────────────────────────────

echo " [1/6] Checking Python installation..."

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo -e "${RED} [ERROR] Python is NOT installed.${NC}"
    echo ""
    echo "  ┌─────────────────────────────────────────────────────────────┐"
    echo "  │  HOW TO FIX THIS:                                          │"
    echo "  │                                                             │"
    echo "  │  macOS:                                                     │"
    echo "  │    brew install python3                                     │"
    echo "  │    OR download from https://www.python.org/downloads/       │"
    echo "  │                                                             │"
    echo "  │  Ubuntu/Debian:                                             │"
    echo "  │    sudo apt update && sudo apt install python3 python3-venv │"
    echo "  │                                                             │"
    echo "  │  Fedora/RHEL:                                               │"
    echo "  │    sudo dnf install python3                                 │"
    echo "  │                                                             │"
    echo "  │  Arch:                                                      │"
    echo "  │    sudo pacman -S python                                    │"
    echo "  └─────────────────────────────────────────────────────────────┘"
    echo ""
    exit 1
fi

# Check version is 3.10+
PYVER=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYMAJOR=$(echo "$PYVER" | cut -d. -f1)
PYMINOR=$(echo "$PYVER" | cut -d. -f2)

if [ "$PYMAJOR" -lt 3 ] || ([ "$PYMAJOR" -eq 3 ] && [ "$PYMINOR" -lt 10 ]); then
    echo -e "${RED} [ERROR] Python $PYVER is too old. You need Python 3.10 or newer.${NC}"
    echo "         Download it from https://www.python.org/downloads/"
    exit 1
fi

echo -e "        Python $PYVER ${GREEN}✓${NC}"
echo ""

# ── Step 2: Check for python3-venv (common Linux issue) ─────────────────────

echo " [2/6] Creating virtual environment..."

if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    echo -e "        Virtual environment already exists ${GREEN}✓${NC}"
else
    # Try creating venv - if it fails on Linux, suggest installing python3-venv
    if ! $PYTHON_CMD -m venv venv 2>/dev/null; then
        echo ""
        echo -e "${RED} [ERROR] Failed to create virtual environment.${NC}"
        echo ""
        echo "  This often happens on Ubuntu/Debian because python3-venv"
        echo "  is not installed by default."
        echo ""
        echo "  Fix:"
        echo "    sudo apt install python3-venv"
        echo ""
        echo "  Then run this script again."
        exit 1
    fi
    echo -e "        Created venv/ ${GREEN}✓${NC}"
fi
echo ""

# ── Step 3: Install dependencies ─────────────────────────────────────────────

echo " [3/6] Installing dependencies (this may take a minute)..."

venv/bin/pip install -r requirements.txt --quiet 2>&1 | tail -1
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo ""
    echo -e "${RED} [ERROR] Failed to install dependencies.${NC}"
    echo "         Try running manually:"
    echo "           source venv/bin/activate"
    echo "           pip install -r requirements.txt"
    exit 1
fi

echo -e "        All dependencies installed ${GREEN}✓${NC}"
echo ""

# ── Step 4: Create .env file ─────────────────────────────────────────────────

echo " [4/6] Setting up configuration..."

if [ -f ".env" ]; then
    echo -e "        .env already exists, keeping your settings ${GREEN}✓${NC}"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "        Copied .env.example to .env ${GREEN}✓${NC}"
        echo -e "        ${YELLOW}TIP: Edit .env to set a real SECRET_KEY for production${NC}"
    else
        cat > .env << 'EOF'
SECRET_KEY=dev-key-change-me-in-production
DATABASE_URL=sqlite:///orchestration.db
FLASK_ENV=development
FLASK_DEBUG=1
EOF
        echo -e "        Created default .env ${GREEN}✓${NC}"
    fi
fi
echo ""

# ── Step 5: Initialize database ──────────────────────────────────────────────

echo " [5/6] Initializing database..."

venv/bin/python setup_db.py
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED} [ERROR] Database initialization failed.${NC}"
    echo "         Try running manually:"
    echo "           venv/bin/python setup_db.py"
    exit 1
fi

echo -e "        Database ready ${GREEN}✓${NC}"
echo ""

# ── Step 6: Launch ───────────────────────────────────────────────────────────

echo " [6/6] Starting server..."
echo ""
echo -e "${CYAN}${BOLD} ============================================================================${NC}"
echo -e "${CYAN}${BOLD}  🧊 C-C-C-COOLASSAPP is starting!${NC}"
echo -e "${CYAN}${BOLD} ============================================================================${NC}"
echo ""
echo "  URL:       http://127.0.0.1:5000"
echo "  Login:     http://127.0.0.1:5000/login"
echo ""
echo "  Default credentials:"
echo "    Username: admin"
echo "    Password: admin"
echo "    (You'll be asked to change the password on first login)"
echo ""
echo "  Press Ctrl+C to stop the server."
echo -e "${CYAN} ============================================================================${NC}"
echo ""

# Try to open browser
if command -v xdg-open &>/dev/null; then
    xdg-open "http://127.0.0.1:5000/login" 2>/dev/null &
elif command -v open &>/dev/null; then
    open "http://127.0.0.1:5000/login" 2>/dev/null &
fi

# Start the server (this blocks)
exec venv/bin/python run_server.py
