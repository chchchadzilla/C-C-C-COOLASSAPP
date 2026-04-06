ï»¿# C-C-C-COOLASSAPP

**Carefully-Crafted-Claude-Code Original Orchestration Layer And Super Serious Appropriately Positioned Project**

A web-based command center for teams running **10 concurrent Claude Code AI agents per developer**.
Real-time monitoring, nightly reports, codebase health checks, and a 14-day implementation
playbook --- all in one dashboard.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask 3.1](https://img.shields.io/badge/Flask-3.1-000?logo=flask)
![Socket.IO](https://img.shields.io/badge/Socket.IO-realtime-010101?logo=socketio)
![SQLite](https://img.shields.io/badge/SQLite-database-003B57?logo=sqlite)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)

---

## Table of Contents

- [What Is This](#what-is-this)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [First Login](#first-login)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Pages and Routes](#pages-and-routes)
- [API Reference](#api-reference)
- [LLM Provider Setup](#llm-provider-setup)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Tech Stack](#tech-stack)

---

## What Is This

When you go from 1 Claude Code agent to 10, everything breaks:

- **Merge conflicts multiply** --- 10 agents editing code at once
- **Context drift** --- Agent A contradicts Agent B's architecture
- **Zero visibility** --- no idea what 10 agents are doing simultaneously
- **No playbook** --- nobody has written a guide for this yet

C-C-C-COOLASSAPP fixes all of that. It is a **mission control dashboard** for AI-assisted
development at scale.

---

## Features

**Command Center** --- Real-time dashboard with agent grid, health scores, task counters,
and live WebSocket updates.

**Agent Fleet** --- Deploy, monitor, pause, resume, and terminate agents. Assign tasks,
set branches, pick permission modes. View any agent's live terminal output via Remote View.

**Team Management** --- CRUD for team members with role-based access
(Admin / Orchestrator / Developer). Per-user agent limits (1 to 10), adaptation scores,
activity tracking.

**Reports and Analytics** --- Automated nightly reports at 11 PM UTC. On-demand generation.
Chart.js analytics with daily trends, per-user comparisons, failure patterns.
CSV and PDF exports.

**14-Day Implementation Plan** --- Day-by-day playbook for scaling from 1 to 10 agents.
Task checklists, troubleshooting guides, and a failure log to track issues during rollout.

**Knowledge Base** --- Battle-tested best practices: CLAUDE.md templates, parallel agent
patterns, failure mode detection, orchestration architectures, CLI reference.

**Health Monitoring** --- Automated checks every 6 hours (git health, lint, tests,
context health). 0 to 100 composite health score with historical trends.

**Multi-Provider LLM** --- Four backends: Claude CLI, Anthropic API, OpenRouter,
GitHub Copilot. Per-user encrypted API key management.

**Task Queue** --- Background execution via ThreadPoolExecutor. Queue status,
cancel running tasks.

**SLA Analytics** --- Mean, median, and P95 task durations. Success and failure rates
over time.

---

## Prerequisites

You need two things:

| Requirement | Minimum | Check |
|-------------|---------|-------|
| Python | 3.10+ | `python --version` |
| pip | any | `pip --version` |

Optional: **Git** (enables codebase health checks). **Claude CLI** (enables agent execution).

---

## Installation

### Option A --- One-Click Installers

Pick the one that matches your system. Each script does everything: creates a virtual
environment, installs dependencies, initializes the database, and starts the server.

**Windows (CMD):**

```
install.bat
```

**Windows (PowerShell):**

```
.\install.ps1
```

If PowerShell blocks execution, run this first:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS / Linux:**

```
chmod +x install.sh
./install.sh
```

### Option B --- Manual Setup (Any OS)

**Step 1 --- Clone and enter the project:**

```bash
git clone https://github.com/chchchadzilla/C-C-C-COOLASSAPP.git
cd C-C-C-COOLASSAPP
```

**Step 2 --- Create a virtual environment:**

```bash
python -m venv venv
```

**Step 3 --- Activate the virtual environment:**

| OS | Command |
|----|---------|
| Windows CMD | `venv\Scripts\activate.bat` |
| Windows PowerShell | `.\venv\Scripts\Activate.ps1` |
| macOS / Linux | `source venv/bin/activate` |

**Step 4 --- Install dependencies:**

```bash
pip install -r requirements.txt
```

**Step 5 --- Create your environment file:**

```bash
cp .env.example .env
```

Then open `.env` and set a real `SECRET_KEY` (any long random string).

**Step 6 --- Initialize the database:**

```bash
python setup_db.py
```

**Step 7 --- Start the server:**

```bash
python run_server.py
```

The server starts at **http://127.0.0.1:5000**.

---

## First Login

1. Open **http://127.0.0.1:5000/login**
2. Username: `admin`
3. Password: `admin`
4. You will be forced to change the password immediately.

After logging in, the dashboard loads with seed data for the 14-day implementation plan.

---

## Configuration

All settings live in the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | (insecure default) | **Set this.** Any long random string. Required for session security. |
| DATABASE_URL | sqlite:///orchestration.db | Database connection string. SQLite works out of the box. |
| FLASK_ENV | development | Set to `production` for production use. |
| FLASK_DEBUG | 1 | Set to `0` in production. |
| REPORT_HOUR | 23 | Hour (UTC) for automatic nightly report generation. |
| HEALTH_INTERVAL | 6 | Hours between automated health checks. |
| CORS_ORIGINS | * (all) | Comma-separated allowed origins. Set explicitly in production. |

---

## Project Structure

```
C-C-C-COOLASSAPP/
|-- app.py                  # Flask app factory, extensions, blueprint registration
|-- models.py               # 9 SQLAlchemy models (User, Agent, AgentSession, etc.)
|-- run_server.py           # Production-style server launcher
|-- run.py                  # CLI launcher with --port / --host / --prod flags
|-- setup_db.py             # Database init + default admin creation
|-- requirements.txt        # 19 Python dependencies
|-- .env.example            # Environment variable template
|-- example_CLAUDE.md       # CLAUDE.md template for teams
|
|-- routes/
|   |-- dashboard.py        # Main dashboard
|   |-- auth.py             # Login, logout, register, change password
|   |-- users.py            # User CRUD + scaling controls
|   |-- agents.py           # Agent fleet management + remote view
|   |-- reports.py          # Report generation, detail, analytics, export
|   |-- implementation.py   # 14-day plan, day details, failure log
|   |-- bestpractices.py    # Knowledge base pages
|   |-- health.py           # Health checks + history
|   |-- settings.py         # LLM provider configuration
|   |-- apikeys.py          # Per-user API key management
|   |-- api.py              # REST API (18+ endpoints)
|
|-- services/
|   |-- llm_provider.py     # Multi-provider LLM routing (4 backends)
|   |-- agent_runner.py     # Claude CLI wrapper (sync/async execution)
|   |-- task_queue.py       # ThreadPoolExecutor task queue
|   |-- health_checker.py   # Git, lint, test, context health checks
|   |-- report_generator.py # Nightly report builder
|   |-- scheduler.py        # APScheduler job config
|   |-- encryption.py       # API key encryption (Fernet)
|   |-- openrouter_models.py# OpenRouter model catalog
|
|-- templates/
|   |-- base.html           # Master layout (top navbar, dark/light theme toggle)
|   |-- dashboard/          # Dashboard
|   |-- auth/               # Login, register, change password
|   |-- users/              # User list, add, detail, edit
|   |-- agents/             # Agent list, create, detail, remote view, session log
|   |-- reports/            # Report list, detail, analytics
|   |-- implementation/     # 14-day overview, day detail, failure log
|   |-- bestpractices/      # 6 knowledge base pages
|   |-- health/             # Health overview, history
|   |-- settings/           # Provider config CRUD
|   |-- apikeys/            # API key management
|   |-- components/         # Reusable partials
|
|-- static/
|   |-- css/style.css       # Full stylesheet (dark/light themes)
|   |-- js/app.js           # Theme toggle, WebSocket, Chart.js
|
|-- install.bat             # One-click installer (Windows CMD)
|-- install.ps1             # One-click installer (PowerShell)
|-- install.sh              # One-click installer (macOS/Linux)
|-- setup.bat               # Quick setup script (Windows)
|-- test_routes.py          # Route smoke test (hits every page)
```

---

## Pages and Routes

### Web Pages

| Page | URL | What It Does |
|------|-----|--------------|
| Dashboard | / | Real-time command center with agent grid and health score |
| Login | /login | Username and password authentication |
| Register | /register | New account creation |
| Change Password | /change-password | Forced on first login, available anytime |
| Users | /users/ | Team member list with role badges and agent counts |
| Add User | /users/add | Create a new team member |
| User Detail | /users/(id) | Profile, stats, agent list, activity timeline |
| Edit User | /users/(id)/edit | Update role, agent limit, notes |
| Agents | /agents/ | Fleet overview with status, tasks, branches, models |
| Create Agent | /agents/create | Deploy a new agent instance |
| Agent Detail | /agents/(id) | Full agent info and session history |
| Remote View | /agents/remote/(id) | Live terminal feed from a running agent |
| Session Log | /agents/(id)/sessions/(sid)/log | Detailed output from a past session |
| Reports | /reports/ | All generated reports |
| Report Detail | /reports/(id) | Full report with tasks, conflicts, recommendations |
| Analytics | /reports/analytics | Chart.js dashboards with daily trends |
| Implementation | /implementation/ | 14-day plan overview with progress bars |
| Day Detail | /implementation/day/(n) | Single day objectives and checklist |
| Failure Log | /implementation/failure-log | Tracked failures with resolution status |
| Best Practices | /best-practices/ | Knowledge base index |
| CLAUDE.md Guide | /best-practices/claude-md | How to write effective CLAUDE.md files |
| Parallel Agents | /best-practices/parallel-agents | Fan-out, pipeline, specialist patterns |
| Failure Modes | /best-practices/failure-modes | Context drift, merge conflicts, contradictions |
| Orchestration | /best-practices/orchestration-patterns | Hub-spoke, pipeline, swarm architectures |
| CLI Reference | /best-practices/commands | Claude CLI commands, flags, hooks |
| Health | /health/ | Latest health check results (0 to 100 score) |
| Health History | /health/history | Score trends over time with charts |
| Settings | /settings/ | LLM provider configuration |
| API Keys | /api-keys/ | Manage your personal API keys |
| API Keys Admin | /api-keys/admin | Admin view of all user keys |

### REST API

All API endpoints are under `/api`. Authentication required (session-based).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/ | API info and version |
| GET | /api/users | List all users (admin: all, others: self only) |
| GET | /api/agents | List agents (filtered by ownership for non-admins) |
| GET | /api/agents/(id)/sessions | Session history for an agent |
| GET | /api/reports | List all reports |
| GET | /api/stats | Aggregate statistics (users, agents, tasks, health) |
| GET | /api/implementation | 14-day plan status |
| GET | /api/health | Latest health check results |
| GET | /api/failures | All failure log entries |
| GET | /api/providers | Configured LLM providers |
| GET | /api/providers/(id)/test | Test a provider connection |
| GET | /api/sla | SLA metrics (mean, median, P95 durations) |
| GET | /api/queue | Task queue status |
| GET | /api/queue/(session_id) | Status of a specific queued task |
| GET | /api/dashboard/stats | Dashboard widget data |
| POST | /api/chat | Send a message to the configured LLM provider |

---

## LLM Provider Setup

C-C-C-COOLASSAPP supports four LLM backends. Configure them at Settings in the web UI.

### Claude CLI (Default)

Requires the Claude CLI installed locally. No API key needed.

```bash
npm install -g @anthropic-ai/claude-code
```

The agent runner calls `claude --print` under the hood.

### Anthropic API

1. Get an API key at https://console.anthropic.com
2. Go to API Keys in the web UI
3. Add your key with provider type `anthropic`
4. Go to Settings and create an Anthropic provider

### OpenRouter

1. Get an API key at https://openrouter.ai/keys
2. Add your key with provider type `openrouter`
3. Create an OpenRouter provider in Settings
4. Pick from 100+ models (GPT-4o, Llama, Mistral, etc.)

### GitHub Copilot

1. Requires an active GitHub Copilot subscription
2. Add your GitHub token with provider type `github`
3. Create a GitHub Copilot provider in Settings

---

## Security Notes

Do these before deploying to a real network:

1. **Set SECRET_KEY** --- Open `.env`, replace the default with a long random string.
   Without this, sessions are insecure.

2. **Change the admin password** --- Default is admin/admin. The app forces a password
   change on first login, but do not skip it.

3. **Set CORS_ORIGINS** --- Default allows all origins. Set it to your actual domains,
   comma-separated.

4. **Set FLASK_ENV=production** --- Disables debug mode, hides tracebacks.

5. **Disable /test-login** --- This route exists for development testing. It is
   automatically disabled when SECRET_KEY is set to a non-default value.

6. **API key encryption** --- User API keys are encrypted at rest with Fernet
   (from the cryptography package). The encryption key derives from your SECRET_KEY.

---

## Troubleshooting

**ModuleNotFoundError: No module named flask**

You are not in the virtual environment. Activate it first:
- Windows: `venv\Scripts\activate.bat`
- macOS/Linux: `source venv/bin/activate`

**Address already in use (port 5000 conflict)**

Something else is using port 5000. Kill it or use a different port:

```bash
python run.py --port 8080
```

**SECRET_KEY not set warning at startup**

Copy `.env.example` to `.env` and set `SECRET_KEY` to any long random string.

**CORS_ORIGINS not set warning**

Not a problem in development. For production, set `CORS_ORIGINS=https://yourdomain.com`
in `.env`.

**Database is empty or no admin user**

Run `python setup_db.py` to create the database and the default admin account.

**Health checks show Git not found**

Install Git. Health checks run `git status` and `git log` to assess repository health.

**Claude CLI agent will not execute**

Verify Claude CLI is installed: `claude --version`.
If not, run `npm install -g @anthropic-ai/claude-code`.

**Charts on Analytics page are empty**

You need at least 2 reports for trend charts to render. Generate a couple of reports first.

**must_change_password loop**

The admin has not changed the default password yet. Log in as admin/admin and you will be
redirected to the change password page.

**PowerShell blocks install.ps1**

Run this command, then try again:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## FAQ

**Do I need Claude Code CLI installed to use this?**

No. The dashboard, team management, reports, and implementation plan all work without it.
You only need Claude CLI if you want to actually execute agents from the web UI.

**Can this run on a server for my whole team?**

Yes. Set `FLASK_ENV=production`, configure a real `SECRET_KEY`, and run behind a
reverse proxy (nginx or caddy). Each team member logs in with their own account.

**How do nightly reports work?**

APScheduler runs a job at 11 PM UTC (configurable via `REPORT_HOUR` in `.env`).
It aggregates task stats, health scores, and failure data into a report.
You can also generate reports manually from the Reports page.

**What database does it use?**

SQLite by default. The database file lives at `instance/orchestration.db`.
You can point `DATABASE_URL` at PostgreSQL or MySQL if needed --- it is standard SQLAlchemy.

**Is this production-ready?**

It is production-capable for internal team use. For public internet exposure, put it behind
a reverse proxy with HTTPS, set all the security env vars, and follow the Security Notes
section above.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3.1, SQLAlchemy 2.0, Flask-Login, Flask-SocketIO |
| Database | SQLite (default), any SQLAlchemy-compatible DB |
| Real-time | Socket.IO (WebSocket with threading async mode) |
| Scheduling | APScheduler (nightly reports, health checks) |
| Frontend | Jinja2 templates, vanilla JS, Chart.js |
| Fonts | Space Grotesk, Inter, JetBrains Mono |
| Theme | Dark/light toggle with animated SVG sun/moon icon |
| Security | Werkzeug password hashing, Fernet encryption, RBAC |
| LLM | Claude CLI, Anthropic API, OpenRouter, GitHub Copilot |

---

*Built for teams who think running 10 AI agents at once is a perfectly reasonable thing to do.*

---

## Support

If this project helps you, you can support my work here: **https://buymeacoffee.com/chadpkeith**
