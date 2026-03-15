# ============================================================================
#  C-C-C-COOLASSAPP — One-Click PowerShell Installer
#
#  Carefully-Crafted-Claude-Code Original Orchestration Layer
#  And Super Serious Appropriately Positioned Project
#
#  Usage:
#    .\install.ps1
#
#  If you get an execution policy error:
#    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#    .\install.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

function Write-Step($step, $total, $msg) {
    Write-Host " [$step/$total] " -ForegroundColor Cyan -NoNewline
    Write-Host $msg
}

function Write-Ok($msg) {
    Write-Host "        $msg " -NoNewline
    Write-Host "✓" -ForegroundColor Green
}

function Write-Err($msg) {
    Write-Host " [ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $msg
}

Write-Host ""
Write-Host " ============================================================================" -ForegroundColor Cyan
Write-Host "  🧊 C-C-C-COOLASSAPP — One-Click Installer (PowerShell)" -ForegroundColor Cyan
Write-Host " ============================================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 0: Check we're in the right folder ──────────────────────────────────

if (-not (Test-Path "app.py")) {
    Write-Err "app.py not found in the current directory."
    Write-Host "         Make sure you run this from the C-C-C-COOLASSAPP project folder."
    Write-Host ""
    Write-Host " Current directory: $(Get-Location)"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "requirements.txt")) {
    Write-Err "requirements.txt not found."
    Write-Host "         This doesn't look like the right project folder."
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host " " -NoNewline
Write-Host "[OK]" -ForegroundColor Green -NoNewline
Write-Host " Project files found."
Write-Host ""

# ── Step 1: Check Python ────────────────────────────────────────────────────

Write-Step 1 6 "Checking Python installation..."

$pythonCmd = $null
$pythonCmds = @("python", "python3", "py")

foreach ($cmd in $pythonCmds) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $pythonCmd = $cmd
                break
            }
        }
    }
    catch {
        # Command not found, try next
    }
}

if (-not $pythonCmd) {
    Write-Host ""
    Write-Err "Python 3.10+ is NOT installed, or not on your PATH."
    Write-Host ""
    Write-Host "  ┌─────────────────────────────────────────────────────────────┐"
    Write-Host "  │  HOW TO FIX THIS:                                          │"
    Write-Host "  │                                                             │"
    Write-Host "  │  1. Go to https://www.python.org/downloads/                 │"
    Write-Host "  │  2. Download Python 3.10 or newer                           │"
    Write-Host "  │  3. Run the installer                                       │"
    Write-Host "  │  4. *** CHECK THE BOX: 'Add Python to PATH' ***             │"
    Write-Host "  │     (This is the most common mistake. Don't skip it.)       │"
    Write-Host "  │  5. RESTART PowerShell                                      │"
    Write-Host "  │  6. Run this script again                                   │"
    Write-Host "  └─────────────────────────────────────────────────────────────┘"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

$pyVersion = & $pythonCmd --version 2>&1
Write-Ok "$(($pyVersion -replace 'Python ', 'Python '))"
Write-Host ""

# ── Step 2: Create virtual environment ───────────────────────────────────────

Write-Step 2 6 "Creating virtual environment..."

if (Test-Path "venv\Scripts\python.exe") {
    Write-Ok "Virtual environment already exists"
}
elseif (Test-Path "venv/bin/python") {
    # Unix-style venv (WSL or cross-platform)
    Write-Ok "Virtual environment already exists"
}
else {
    try {
        & $pythonCmd -m venv venv
        Write-Ok "Created venv/"
    }
    catch {
        Write-Err "Failed to create virtual environment."
        Write-Host "         Try running: $pythonCmd -m venv venv"
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host ""

# ── Detect pip path ──────────────────────────────────────────────────────────

$pipPath = $null
$pythonPath = $null

if (Test-Path "venv\Scripts\pip.exe") {
    $pipPath = "venv\Scripts\pip.exe"
    $pythonPath = "venv\Scripts\python.exe"
}
elseif (Test-Path "venv/bin/pip") {
    $pipPath = "venv/bin/pip"
    $pythonPath = "venv/bin/python"
}
else {
    Write-Err "Could not find pip in the virtual environment."
    Read-Host "Press Enter to exit"
    exit 1
}

# ── Step 3: Install dependencies ─────────────────────────────────────────────

Write-Step 3 6 "Installing dependencies (this may take a minute)..."

try {
    & $pipPath install -r requirements.txt --quiet 2>&1 | Out-Null
    Write-Ok "All dependencies installed"
}
catch {
    Write-Err "Failed to install dependencies."
    Write-Host "         Try running manually:"
    Write-Host "           & $pipPath install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# ── Step 4: Create .env file ─────────────────────────────────────────────────

Write-Step 4 6 "Setting up configuration..."

if (Test-Path ".env") {
    Write-Ok ".env already exists, keeping your settings"
}
elseif (Test-Path ".env.example") {
    Copy-Item ".env.example" ".env"
    Write-Ok "Copied .env.example to .env"
    Write-Host "        " -NoNewline
    Write-Host "TIP: Edit .env to set a real SECRET_KEY for production" -ForegroundColor Yellow
}
else {
    @"
SECRET_KEY=dev-key-change-me-in-production
DATABASE_URL=sqlite:///orchestration.db
FLASK_ENV=development
FLASK_DEBUG=1
"@ | Set-Content ".env" -Encoding UTF8
    Write-Ok "Created default .env"
}
Write-Host ""

# ── Step 5: Initialize database ──────────────────────────────────────────────

Write-Step 5 6 "Initializing database..."

try {
    & $pythonPath setup_db.py
    Write-Ok "Database ready"
}
catch {
    Write-Err "Database initialization failed."
    Write-Host "         Try running manually:"
    Write-Host "           & $pythonPath setup_db.py"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# ── Step 6: Launch ───────────────────────────────────────────────────────────

Write-Step 6 6 "Starting server..."
Write-Host ""
Write-Host " ============================================================================" -ForegroundColor Cyan
Write-Host "  🧊 C-C-C-COOLASSAPP is starting!" -ForegroundColor Cyan
Write-Host " ============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  URL:       http://127.0.0.1:5000"
Write-Host "  Login:     http://127.0.0.1:5000/login"
Write-Host ""
Write-Host "  Default credentials:"
Write-Host "    Username: admin"
Write-Host "    Password: admin"
Write-Host "    (You'll be asked to change the password on first login)"
Write-Host ""
Write-Host "  Press Ctrl+C to stop the server."
Write-Host " ============================================================================" -ForegroundColor Cyan
Write-Host ""

# Open browser
try {
    Start-Process "http://127.0.0.1:5000/login"
}
catch {
    # Silently ignore if browser can't be opened
}

# Start the server (this blocks)
& $pythonPath run_server.py
