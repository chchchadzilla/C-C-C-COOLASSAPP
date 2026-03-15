<p align="center"># C-C-C-COOLASSAPP

  <img src="https://img.shields.io/badge/🧊-C--C--C--COOLASSAPP-6366f1?style=for-the-badge&labelColor=0a0e17" alt="C-C-C-COOLASSAPP" />

</p>A comprehensive web-based management platform for teams running **10 concurrent Claude Code instances per developer**. Built with Flask, Socket.IO, and Chart.js.



<h1 align="center">C-C-C-COOLASSAPP</h1>![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)

![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)

<p align="center">![License](https://img.shields.io/badge/License-MIT-yellow)

  <strong>C</strong>arefully-<strong>C</strong>rafted-<strong>C</strong>laude-<strong>C</strong>ode <strong>O</strong>riginal <strong>O</strong>rchestration <strong>L</strong>ayer <strong>A</strong>nd <strong>S</strong>uper <strong>S</strong>erious <strong>A</strong>ppropriately <strong>P</strong>ositioned <strong>P</strong>roject

</p>## Features



<p align="center">### Command Center

  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />- **Live Dashboard** — Real-time metrics, agent grid visualization, health scores

  <img src="https://img.shields.io/badge/Flask-3.1.0-000000?style=flat-square&logo=flask&logoColor=white" />- **Agent Fleet Management** — Deploy, monitor, pause, resume, and terminate agents

  <img src="https://img.shields.io/badge/Socket.IO-Real--time-010101?style=flat-square&logo=socketio&logoColor=white" />- **Remote Viewing** — Live terminal feed from any running agent instance

  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white" />- **WebSocket Updates** — Instant status changes without page refresh

  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" />

</p>### Team Management

- **User CRUD** — Add, edit, activate/deactivate team members

<p align="center">- **Role-Based Access** — Admin, Orchestrator, and Developer roles

  A comprehensive web-based management platform for teams running <strong>10 concurrent Claude Code instances per developer</strong>.<br/>- **Scaling Controls** — Adjust agent count per developer (1–10)

  Real-time monitoring · Nightly reports · Codebase health checks · 2-week implementation plan · Multi-provider LLM support- **Performance Tracking** — Adaptation scores and task metrics per user

</p>

### Reporting & Analytics

---- **Nightly Reports** — Auto-generated at 11 PM UTC with full metrics

- **On-Demand Reports** — Generate reports anytime with one click

## Table of Contents- **Analytics Dashboard** — Daily trends, user comparison, failure patterns (Chart.js)

- **Export-Ready** — Detailed breakdowns of tasks, conflicts, and recommendations

1. [What Is This?](#what-is-this)

2. [Screenshots](#screenshots)### 2-Week Implementation Strategy

3. [Features](#features)- **14-Day Plan** — Day-by-day guide from audit to full deployment

4. [Prerequisites](#prerequisites)- **Task Checklists** — Track completion for each day's objectives

5. [Installation](#installation)- **Troubleshooting Guides** — Problem/solution pairs with warning signs

   - [One-Click Installers](#one-click-installers)- **Failure Log** — Track and resolve issues during rollout

   - [Manual Installation](#manual-installation)

6. [First Run — What To Expect](#first-run--what-to-expect)### Knowledge Base

7. [Configuration](#configuration)- **CLAUDE.md Best Practices** — Structure, examples, and templates

8. [Project Structure](#project-structure)- **Parallel Agent Patterns** — Fan-out, pipeline, specialist team strategies

9. [All Pages & What They Do](#all-pages--what-they-do)- **Failure Mode Detection** — Context drift, merge conflicts, contradictions

10. [API Reference](#api-reference)- **Orchestration Architecture** — Hub-spoke, pipeline, swarm patterns

11. [LLM Provider Setup](#llm-provider-setup)- **CLI Reference** — Commands, configuration, hooks, and tips

12. [Security](#security)

13. [Troubleshooting](#troubleshooting)### Health Monitoring

14. [FAQ](#faq)- **Automated Checks** — Git health, code quality, context health (every 6 hours)

15. [Tech Stack](#tech-stack)- **Health Score** — 0–100 composite score with color-coded status

- **Historical Trends** — Track score changes over time with charts

---- **Alerts** — Toast notifications when health drops below thresholds



## What Is This?## Quick Start



**C-C-C-COOLASSAPP** is a Flask web application that lets you manage, monitor, and orchestrate a team of developers who are each running **up to 10 concurrent Claude Code AI agents**.### Prerequisites

- Python 3.10 or higher

Think of it as a **mission control dashboard** for AI-assisted software development at scale.- pip (Python package manager)

- Git (optional, for health checks)

### The Problem It Solves

### Windows Setup (Recommended)

When you go from 1 Claude Code instance to 10, everything changes:

```batch

- **Merge conflicts multiply** — 10 agents editing code at once creates chaosgit clone <repository-url>

- **Context drift** — Agent A makes architectural decisions that contradict Agent Bcd ClaudeCodeOrchestration

- **No visibility** — You have no idea what 10 agents are doing simultaneouslysetup.bat

- **No playbook** — There's no guide for scaling from 1 to 10 agents```



### What This App Gives YouThis creates a virtual environment, installs dependencies, initializes the database, and creates a default admin account.



| Capability | Description |### Manual Setup

|---|---|

| 🎛️ **Live Dashboard** | Real-time metrics, agent grid, health scores |```bash

| 👥 **Team Management** | Add/remove/manage developers and their agent quotas |# 1. Create virtual environment

| 🤖 **Agent Fleet Control** | Deploy, monitor, assign tasks, terminate agents |python -m venv venv

| 🖥️ **Remote View** | See what any agent is doing in real-time |

| 📊 **Nightly Reports** | Auto-generated performance reports with analytics |# 2. Activate it

| 🏥 **Health Checks** | Automated lint, test, and git health monitoring |# Windows:

| 📋 **14-Day Implementation Plan** | Step-by-step guide to scaling from 1 to 10 agents |venv\Scripts\activate.bat

| 📚 **Best Practices KB** | Battle-tested patterns for running Claude Code at scale |# macOS/Linux:

| 🚨 **Failure Log** | Track and learn from every failure across the team |source venv/bin/activate

| 🔌 **Multi-Provider LLM** | Claude CLI, Anthropic API, OpenRouter, GitHub Copilot |

| 🔑 **API Key Management** | Per-user encrypted API keys with usage tracking |# 3. Install dependencies

| 📈 **SLA Analytics** | Mean/median/P95 task durations, success rates |pip install -r requirements.txt

| ⚙️ **Task Queue** | Background task execution with ThreadPoolExecutor |

| 🔐 **RBAC** | Admin/Orchestrator/Developer role-based access |# 4. Run the application

| 📥 **Export** | CSV and PDF report downloads |python run.py

```

---

### First Login

## Screenshots

Open `http://localhost:5000` and log in with:

> The dashboard uses a clean dark/light theme with **Space Grotesk** headings, **Inter** body text, and **JetBrains Mono** for code. Sharp 2px border radius throughout.- **Username**: `admin`

- **Password**: `admin`

*(Screenshots are located in the project root as PNG files: `1_Scaling-Claude-Code-Agents-10x-in-2-Weeks.png` through `10_The-Honest-Part.png`)*

> ⚠ Change the admin password immediately in a production environment.

---

## Project Structure

## Features

```

### 🎛️ Command Center DashboardClaudeCodeOrchestration/

- Real-time WebSocket-powered metrics (total agents, active, idle, error counts)├── app.py                    # Application factory & entry point

- Agent grid with live status dots (green = active, yellow = idle, red = error)├── models.py                 # SQLAlchemy database models

- Tasks completed/failed counters, merge conflict tracker├── run.py                    # Quick launcher script

- Token usage overview, unresolved failure count├── setup.bat                 # Windows setup script

- One-click refresh and live indicator├── requirements.txt          # Python dependencies

├── example_CLAUDE.md         # Template for team CLAUDE.md files

### 👥 Team Management│

- Add, edit, and remove team members├── routes/                   # Flask blueprints

- Set per-user agent limits (1–10)│   ├── api.py               # REST API endpoints

- Role assignment: **Admin**, **Orchestrator**, **Developer**│   ├── auth.py              # Authentication (login/register)

- Adaptation score tracking per developer│   ├── dashboard.py         # Main dashboard

- Activity timeline and last-seen tracking│   ├── users.py             # User management

│   ├── agents.py            # Agent fleet management

### 🤖 Agent Fleet│   ├── reports.py           # Reports & analytics

- Deploy agents with custom names, types (general/reviewer/tester/writer/researcher)│   ├── implementation.py    # 2-week plan & failure log

- Assign tasks, set branches, track files being edited│   ├── bestpractices.py     # Knowledge base

- Permission modes: default, permissive, readonly, sandbox│   └── health.py            # Health monitoring

- Model selection per agent (sonnet, opus, etc.)│

- Full session history with duration and status├── services/                 # Business logic

- Terminate / pause / resume controls│   ├── report_generator.py  # Nightly report generation

- **Remote View**: Real-time output streaming for any active agent│   ├── health_checker.py    # Automated health checks

│   └── scheduler.py         # APScheduler job configuration

### 📊 Reports & Analytics│

- Automated nightly report generation (11 PM UTC, configurable)├── templates/                # Jinja2 HTML templates

- Manual report generation anytime│   ├── base.html            # Master layout (dark theme + sidebar)

- Performance charts (tasks over time, per-user performance)│   ├── auth/                # Login & registration

- CSV and PDF export with download buttons│   ├── dashboard/           # Main dashboard

- Report detail view with tasks completed/failed/conflicts breakdown│   ├── users/               # User management views

│   ├── agents/              # Agent fleet views + remote terminal

### 🏥 Codebase Health│   ├── reports/             # Report views + analytics charts

- Automated health checks every 6 hours (configurable)│   ├── implementation/      # 2-week plan + failure log

- Real subprocess execution: runs `flake8` for lint, `pytest` for tests│   ├── bestpractices/       # Knowledge base articles

- Git status monitoring (uncommitted changes, branch tracking)│   └── health/              # Health monitoring views

- Health score history with trend charts│

- One-click manual health check├── static/

│   ├── css/style.css        # Comprehensive dark theme stylesheet

### 📋 14-Day Implementation Plan│   └── js/app.js            # Client-side JavaScript

- Complete day-by-day guide from 1 agent → 10 agents│

- Each day includes: tasks, troubleshooting, warning signs, escalation paths, success criteria└── instance/

- Progress tracking with status updates per day    └── orchestration.db     # SQLite database (auto-created)

- Two phases: **Week 1** (Infrastructure & Mindset), **Week 2** (Scaling & Failure Modes)```



### 📚 Best Practices Knowledge Base## Architecture

- **CLAUDE.md Mastery**: How to write context files that work at scale

- **Parallel Agent Patterns**: Running 10 agents without chaos```

- **Failure Modes & Recovery**: Every failure mode documented with playbooks┌────────────────┐     WebSocket     ┌──────────────┐

- **Orchestration Patterns**: Skills, subagents, plugins, hooks│   Browser UI   │◄────────────────►│  Flask-SocketIO│

- **Commands & Configuration**: Every CLI flag and configuration knob│  (Chart.js +   │     HTTP/REST     │              │

│   Socket.IO)   │◄────────────────►│  Flask App    │

### 🚨 Failure Log└────────────────┘                   │  (Blueprints) │

- Team-wide shared failure log                                     └──────┬───────┘

- Categories: merge conflict, context drift, contradictions, resource contention                                            │

- Severity levels and resolution tracking                        ┌───────────┬───────┴───────┬────────────┐

- The philosophy: "Document every failure so the team learns collectively"                        │           │               │            │

                   ┌────▼───┐ ┌────▼────┐ ┌────────▼──┐ ┌──────▼──────┐

### 🔌 Multi-Provider LLM Integration                   │ Models │ │ Services│ │ Scheduler  │ │  Templates  │

- **Claude Code CLI**: Local subprocess (`claude --print`)                   │(SQLAlch│ │(Reports,│ │(APScheduler│ │ (Jinja2 +   │

- **Anthropic API**: Direct HTTP to `api.anthropic.com`                   │  emy)  │ │ Health) │ │  Cron)     │ │  Chart.js)  │

- **OpenRouter**: Unified gateway to 100+ models                   └────┬───┘ └─────────┘ └────────────┘ └─────────────┘

- **GitHub Copilot**: Chat completions endpoint                        │

- Per-user API keys (encrypted with Fernet) or shared provider keys                   ┌────▼───┐

- Provider test buttons with real connectivity checks                   │ SQLite │

- Priority-based fallback between providers                   │   DB   │

                   └────────┘

### 🔐 Security```

- Session-based auth with Flask-Login

- SECRET_KEY environment-based with runtime warnings## API Reference

- Default admin forced to change password on first login

- RBAC: `role_required()` decorator on all sensitive endpointsAll API endpoints are prefixed with `/api`. See `/api/docs` for the full list.

- Ownership filtering: developers only see their own data

- CORS configurable via environment variable| Method | Endpoint | Description |

- Encrypted API key storage (Fernet symmetric encryption)|--------|----------|-------------|

| GET | `/api/agents` | List all agents |

---| GET | `/api/agents/<id>` | Get agent details |

| POST | `/api/agents/<id>/assign` | Assign task to agent |

## Prerequisites| POST | `/api/agents/<id>/complete` | Mark task complete |

| POST | `/api/agents/<id>/terminate` | Terminate agent |

Before you install, you need these things on your computer. **If you don't have them, the installers will tell you.**| GET | `/api/users` | List all users |

| GET | `/api/reports` | List all reports |

### Required| POST | `/api/reports/generate` | Generate new report |

| GET | `/api/health` | Get latest health check |

| Thing | Version | How to Check | Where to Get It || POST | `/api/health/check` | Run health check now |

|---|---|---|---|| GET | `/api/dashboard` | Dashboard summary data |

| **Python** | 3.10 or newer | `python --version` | [python.org/downloads](https://www.python.org/downloads/) |

| **pip** | (comes with Python) | `pip --version` | Included with Python |## Configuration

| **Git** | Any recent version | `git --version` | [git-scm.com](https://git-scm.com/) |

Set these environment variables before running:

### Optional (for full functionality)

| Variable | Default | Description |

| Thing | What It's For | Where to Get It ||----------|---------|-------------|

|---|---|---|| `SECRET_KEY` | Auto-generated | Flask session key |

| **Claude CLI** | Real agent execution (the `claude` command) | [Anthropic docs](https://docs.anthropic.com/en/docs/claude-code) || `DATABASE_URL` | `sqlite:///orchestration.db` | Database URI |

| **Anthropic API Key** | Direct API access to Claude models | [console.anthropic.com](https://console.anthropic.com/) || `FLASK_ENV` | `development` | Environment mode |

| **OpenRouter API Key** | Access to 100+ LLM models | [openrouter.ai](https://openrouter.ai/) || `FLASK_DEBUG` | `1` | Enable debug mode |

| **flake8** | Automated code linting in health checks | `pip install flake8` |

| **pytest** | Automated test running in health checks | `pip install pytest` |## 2-Week Implementation Plan



### ⚠️ Important NotesThe system includes a built-in 14-day implementation strategy:



- **Windows Users**: When installing Python, **CHECK THE BOX** that says "Add Python to PATH". If you don't, nothing will work.| Week | Days | Focus |

- **macOS Users**: Use `python3` instead of `python`. The installers handle this automatically.|------|------|-------|

- **Linux Users**: Your distro probably has Python already. Try `python3 --version`.| **1** | 1–2 | Audit current workflow, identify bottlenecks |

| **1** | 3–4 | Establish CLAUDE.md standards across repos |

---| **1** | 5 | First parallel agent exercise (2–3 agents) |

| **2** | 6–8 | Identify and document failure modes |

## Installation| **2** | 9–10 | Build orchestration layer and monitoring |

| **2** | 11–14 | Full deployment with checkpoints |

### One-Click Installers

Access this plan at `/implementation` in the running application.

We provide installer scripts that do everything for you. Pick the one for your operating system.

## Tech Stack

#### 🪟 Windows — `install.bat`

- **Backend**: Flask 3.1, Flask-SocketIO, Flask-Login, Flask-SQLAlchemy

1. **Double-click** `install.bat` in the project folder- **Scheduling**: Flask-APScheduler (cron + interval jobs)

2. That's it. It will:- **Database**: SQLite (dev), upgradable to PostgreSQL

   - Check that Python 3.10+ is installed- **Frontend**: Jinja2 templates, Chart.js, Socket.IO client

   - Create a virtual environment (`venv/`)- **Styling**: Custom dark theme CSS (no framework dependency)

   - Install all dependencies- **Git Integration**: GitPython for repository health checks

   - Copy `.env.example` → `.env` (if `.env` doesn't exist)

   - Initialize the database with a default admin user## Contributing

   - Open your browser to `http://127.0.0.1:5000/login`

   - Start the server1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)

#### 🍎🐧 macOS / Linux — `install.sh`3. Commit changes (`git commit -m 'feat: add amazing feature'`)

4. Push to branch (`git push origin feature/amazing-feature`)

```bash5. Open a Pull Request

chmod +x install.sh

./install.sh## License

```

MIT License — see [LICENSE](LICENSE) for details.

It does the same thing as the Windows installer but for Unix systems.

---

#### 💻 PowerShell (any OS) — `install.ps1`

Built for teams scaling Claude Code to 10× productivity.

```powershell
# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

.\install.ps1
```

---

### Manual Installation

If you don't trust installer scripts (understandable) or they don't work for some reason, here's every step by hand.

#### Step 1: Clone or Download

```bash
git clone <your-repo-url> C-C-C-COOLASSAPP
cd C-C-C-COOLASSAPP
```

Or just download and extract the ZIP.

#### Step 2: Create a Virtual Environment

**Windows (cmd.exe):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> **How to tell it worked**: Your terminal prompt should now start with `(venv)`.

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: Flask, Flask-SocketIO, Flask-Login, Flask-SQLAlchemy, Flask-APScheduler, SQLAlchemy, Jinja2, Markdown, GitPython, psutil, requests, Rich, Click, PyYAML, Werkzeug, cryptography, and more.

> **If this fails**: Make sure you're in the virtual environment (you see `(venv)` in your prompt). If you get permission errors on macOS/Linux, try `pip install --user -r requirements.txt`.

#### Step 4: Create Your .env File

```bash
copy .env.example .env          &REM Windows
cp .env.example .env            # macOS/Linux
```

Then edit `.env` and change the `SECRET_KEY`:

```env
SECRET_KEY=replace-this-with-a-long-random-string-at-least-32-characters
DATABASE_URL=sqlite:///orchestration.db
FLASK_ENV=development
FLASK_DEBUG=1
```

> **How to generate a random key**: Run `python -c "import secrets; print(secrets.token_hex(32))"` and paste the output.

#### Step 5: Initialize the Database

```bash
python setup_db.py
```

This creates:
- The SQLite database at `instance/orchestration.db`
- All 9 tables (users, agents, agent_sessions, reports, health_checks, failure_logs, implementation_days, provider_configs, api_keys)
- A default admin user: **username** = `admin`, **password** = `admin`
- A 14-day implementation plan with all task data

#### Step 6: Start the Server

```bash
python run_server.py
```

You'll see:
```
Starting C-C-C-COOLASSAPP server on http://127.0.0.1:5000
```

#### Step 7: Open Your Browser

Go to: **http://127.0.0.1:5000/login**

---

## First Run — What To Expect

### 1. You'll See the Login Page

A clean login form with the 🧊 C-C-C-COOLASSAPP logo.

### 2. Log In with Default Credentials

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin` |

### 3. You'll Be Forced to Change Your Password

The default admin has `must_change_password = True`. You'll be redirected to a password change form. **This is intentional. Pick a real password.**

### 4. You'll Land on the Dashboard

The Command Center shows:
- **0 agents** (you haven't created any yet)
- **0 tasks** (nothing running yet)
- Health score placeholder
- Links to all sections

### 5. What To Do Next

1. **Go to Settings** → Add an LLM provider (see [LLM Provider Setup](#llm-provider-setup))
2. **Go to Team** → Your admin account is the only user. Add team members if needed.
3. **Go to Agents** → Deploy your first agent
4. **Go to Implementation Plan** → Follow the 14-day scaling guide
5. **Go to Best Practices** → Read before scaling to 10 agents

---

## Configuration

All configuration is done through environment variables. You can set them in the `.env` file or export them in your shell.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(insecure default)* | **REQUIRED IN PRODUCTION.** Random string for session encryption. |
| `DATABASE_URL` | `sqlite:///orchestration.db` | SQLAlchemy database URI. SQLite works great for single-team use. |
| `FLASK_ENV` | `development` | Set to `production` in production. |
| `FLASK_DEBUG` | `1` | Set to `0` in production. |
| `CORS_ORIGINS` | `*` (all origins) | Comma-separated list of allowed origins. Set in production. |
| `REPORT_HOUR` | `23` | Hour (UTC) to run nightly report generation. |
| `HEALTH_INTERVAL` | `6` | Hours between automated health checks. |

### Example `.env` for Production

```env
SECRET_KEY=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
DATABASE_URL=sqlite:///orchestration.db
FLASK_ENV=production
FLASK_DEBUG=0
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Project Structure

```
C-C-C-COOLASSAPP/
│
├── app.py                      # Application factory (create_app)
├── models.py                   # SQLAlchemy models (9 tables)
├── run_server.py               # Simple server launcher
├── run.py                      # Advanced launcher with CLI options
├── setup_db.py                 # Database initialization script
├── requirements.txt            # Python dependencies (19 packages)
├── .env.example                # Environment variable template
├── example_CLAUDE.md           # Template CLAUDE.md for your repos
│
├── routes/                     # Flask Blueprints (11 total)
│   ├── auth.py                 #   Login, logout, register, change-password
│   ├── dashboard.py            #   Main dashboard / command center
│   ├── users.py                #   Team management CRUD
│   ├── agents.py               #   Agent fleet management + remote view
│   ├── reports.py              #   Report listing, generation, export
│   ├── implementation.py       #   14-day plan views
│   ├── bestpractices.py        #   Knowledge base pages
│   ├── health.py               #   Health check views
│   ├── api.py                  #   REST API (JSON endpoints + RBAC)
│   ├── settings.py             #   Provider configuration
│   ├── apikeys.py              #   Per-user API key management
│   └── __init__.py
│
├── services/                   # Business logic layer
│   ├── llm_provider.py         #   Multi-provider LLM abstraction
│   ├── agent_runner.py         #   Claude CLI subprocess wrapper
│   ├── task_queue.py           #   ThreadPoolExecutor task queue
│   ├── health_checker.py       #   flake8 + pytest + git health
│   ├── report_generator.py     #   Nightly report generation
│   ├── scheduler.py            #   APScheduler initialization
│   ├── encryption.py           #   Fernet encryption for API keys
│   ├── openrouter_models.py    #   OpenRouter model catalog
│   └── __init__.py
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               #   Master layout (navbar, theme toggle)
│   ├── auth/                   #   login, register, change_password
│   ├── dashboard/              #   index (command center)
│   ├── users/                  #   list, add, detail, edit
│   ├── agents/                 #   list, create, detail, remote
│   ├── reports/                #   list, detail, analytics
│   ├── implementation/         #   overview, day_detail, failure_log
│   ├── bestpractices/          #   index, claude_md, parallel_agents, etc.
│   ├── health/                 #   overview, history
│   ├── settings/               #   index, create, edit
│   └── components/             #   api_key_prompt, session_log
│
├── static/
│   ├── css/style.css           #   Full CSS (dark/light themes, responsive)
│   └── js/app.js               #   Socket.IO, Chart.js, AJAX utilities
│
├── instance/
│   └── orchestration.db        #   SQLite database (created by setup_db.py)
│
├── test_routes.py              #   Route smoke tests (22+ tests)
│
├── install.bat                 #   One-click Windows installer
├── install.sh                  #   One-click macOS/Linux installer
├── install.ps1                 #   One-click PowerShell installer
├── setup.bat                   #   Legacy Windows setup script
│
└── *.png                       #   10 reference screenshots
```

---

## All Pages & What They Do

| URL Path | Page | What It Does |
|---|---|---|
| `/login` | Login | Enter username & password to log in |
| `/register` | Register | Create a new account (first user becomes admin) |
| `/change-password` | Change Password | Required on first admin login; available anytime |
| `/logout` | Logout | Ends your session |
| `/` or `/dashboard` | Command Center | Live metrics, agent grid, quick stats |
| `/users` | Team List | View all team members |
| `/users/add` | Add Member | Create a new team member account |
| `/users/<id>` | Member Detail | View a member's agents, stats, activity |
| `/users/<id>/edit` | Edit Member | Change name, role, agent limit |
| `/agents` | Agent Fleet | View all agents with filter buttons |
| `/agents/create` | Deploy Agent | Create a new Claude Code agent |
| `/agents/<id>` | Agent Detail | Session history, stats, task assignment |
| `/agents/<id>/remote` | Remote View | Live output streaming from the agent |
| `/reports` | Reports List | View all generated reports |
| `/reports/<id>` | Report Detail | Full report breakdown with metrics |
| `/reports/analytics` | Analytics | Charts: tasks over time, per-user perf |
| `/implementation` | 14-Day Plan | Overview of all 14 days with progress |
| `/implementation/day/<n>` | Day Detail | Tasks, troubleshooting, criteria for that day |
| `/implementation/failures` | Failure Log | Team-wide failure tracking and lessons |
| `/bestpractices` | Knowledge Base | Hub for all best practice guides |
| `/bestpractices/claude-md` | CLAUDE.md Guide | How to write effective context files |
| `/bestpractices/parallel-agents` | Parallel Patterns | Running agents in parallel safely |
| `/bestpractices/failure-modes` | Failure Modes | Every failure mode with recovery steps |
| `/bestpractices/orchestration` | Orchestration | Skills, subagents, hooks patterns |
| `/bestpractices/commands` | Commands & Config | Every CLI flag and knob |
| `/health` | Health Overview | Latest health check scores |
| `/health/history` | Health History | Health score trend over time |
| `/settings` | Provider Settings | Configure LLM providers |
| `/settings/create` | Add Provider | Add a new LLM provider |
| `/settings/<id>/edit` | Edit Provider | Modify provider config |
| `/apikeys` | API Keys | Manage your personal API keys |

---

## API Reference

All API endpoints are under `/api`. Most require authentication (session cookie).

### General

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/` | No | Any | API documentation (lists all endpoints) |
| `GET` | `/api/stats` | Yes | Any | Real-time aggregate statistics |

### Users

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/users` | Yes | Admin, Orchestrator | List all users |

### Agents

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/agents` | Yes | Any* | List agents (scoped by role) |
| `GET` | `/api/agents/<id>/sessions` | Yes | Any* | Get agent session history |
| `POST` | `/api/agents/<id>/assign` | Yes | Any | Assign a task to an agent |
| `POST` | `/api/agents/<id>/complete` | Yes | Any | Mark agent task as complete |

> \* Developers only see their own agents. Admins/Orchestrators see all.

### Reports

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/reports` | Yes | Any | List reports (last 30) |
| `POST` | `/api/reports/generate` | Yes | Admin, Orchestrator | Generate a report now |

### Implementation Plan

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/implementation` | Yes | Any | Get all 14 days of the plan |

### Health

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/health` | Yes | Any | Latest health check result |

### Failures

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/failures` | Yes | Any | List all failure log entries |
| `POST` | `/api/failures` | Yes | Any | Log a new failure |

### Providers

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/providers` | Yes | Admin, Orchestrator | List configured providers |
| `POST` | `/api/providers/<id>/test` | Yes | Admin, Orchestrator | Test provider connectivity |

### Chat (LLM)

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/chat` | Yes | Any | Send a message through an LLM provider |

**Request body:**
```json
{
  "provider_id": 1,
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {"role": "user", "content": "Hello, world!"}
  ],
  "max_tokens": 1024,
  "temperature": 0.0
}
```

**Response:**
```json
{
  "content": "Hello! How can I help you today?",
  "model": "claude-sonnet-4-20250514",
  "tokens_used": 42,
  "provider": "anthropic"
}
```

### SLA

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/sla` | Yes | Any | SLA stats (mean/median/P95 task duration) |

**Response:**
```json
{
  "count": 150,
  "mean": 12.5,
  "median": 10.0,
  "p95": 35.2,
  "min": 1.2,
  "max": 120.0,
  "completed": 140,
  "failed": 10,
  "success_rate": 93.3
}
```

### Task Queue

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/queue` | Yes | Any | Queue stats + recent tasks |
| `GET` | `/api/queue/<session_id>` | Yes | Any | Status of a specific queued task |

---

## LLM Provider Setup

Go to **Settings** in the app and click **+ Add Provider**.

### Provider 1: Claude Code CLI (Local)

This uses the `claude` CLI tool installed on your machine.

| Field | Value |
|---|---|
| Name | `Claude CLI` |
| Provider Type | `claude_code` |
| API Key | *(leave empty)* |
| API Base URL | *(leave empty)* |
| Default Model | `sonnet` |
| Priority | `1` |

**Prerequisites**: Install the Claude CLI tool. Check with `claude --version`.

### Provider 2: Anthropic API (Direct)

Direct HTTP calls to Anthropic's API.

| Field | Value |
|---|---|
| Name | `Anthropic API` |
| Provider Type | `anthropic` |
| API Key | `sk-ant-api03-...` |
| API Base URL | `https://api.anthropic.com` |
| Default Model | `claude-sonnet-4-20250514` |
| Priority | `2` |

### Provider 3: OpenRouter (Multi-Model)

Access to 100+ models through a single API.

| Field | Value |
|---|---|
| Name | `OpenRouter` |
| Provider Type | `openrouter` |
| API Key | `sk-or-v1-...` |
| API Base URL | `https://openrouter.ai/api/v1` |
| Default Model | `anthropic/claude-sonnet-4-20250514` |
| Priority | `3` |

### Provider 4: GitHub Copilot

Uses the GitHub Copilot chat completions endpoint.

| Field | Value |
|---|---|
| Name | `GitHub Copilot` |
| Provider Type | `github_copilot` |
| API Key | `ghu_...` |
| API Base URL | `https://api.githubcopilot.com` |
| Default Model | `gpt-4` |
| Priority | `4` |

### Per-User API Keys

Each user can also add their own API keys at **API Keys** → **+ Add Key**. Per-user keys take priority over the shared provider key. Keys are encrypted at rest with Fernet symmetric encryption.

---

## Security

### Production Checklist

- [ ] Set `SECRET_KEY` to a random 64+ character string
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=0`
- [ ] Set `CORS_ORIGINS` to your specific domain(s)
- [ ] Change the default admin password immediately
- [ ] Use HTTPS (put behind nginx/caddy with TLS)
- [ ] Consider switching from SQLite to PostgreSQL for multi-user production

### How Auth Works

1. **Flask-Login** manages sessions via secure cookies
2. **Passwords** are hashed with Werkzeug's `generate_password_hash` (PBKDF2)
3. **API keys** are encrypted at rest with Fernet (from `cryptography` library)
4. **RBAC** uses a `role_required()` decorator — three roles:
   - **Admin**: Full access to everything
   - **Orchestrator**: Same as admin but can't manage other admins
   - **Developer**: Can only see/manage their own agents and data

### Test Login Endpoint

The path `/test-login` is **only available** when running with the insecure default SECRET_KEY. It's a convenience for development. In production (with a real SECRET_KEY), this endpoint doesn't exist.

---

## Troubleshooting

### "I can't start the server"

**Symptom**: `ModuleNotFoundError: No module named 'flask'`

**Fix**: You're not in the virtual environment. Run:
```cmd
REM Windows
venv\Scripts\activate
python run_server.py
```
```bash
# macOS/Linux
source venv/bin/activate
python run_server.py
```

---

### "Python is not recognized"

**Symptom**: `'python' is not recognized as an internal or external command`

**Fix (Windows)**: Reinstall Python and **CHECK** the "Add Python to PATH" box. Or use the full path:
```cmd
C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe run_server.py
```

**Fix (macOS/Linux)**: Use `python3` instead of `python`:
```bash
python3 -m venv venv
source venv/bin/activate
python3 run_server.py
```

---

### "Database errors on startup"

**Symptom**: `OperationalError: no such table: users`

**Fix**: Run the database setup:
```bash
python setup_db.py
```

---

### "I forgot the admin password"

**Fix**: Delete the database and re-initialize:
```cmd
REM Windows
del instance\orchestration.db
python setup_db.py
```
```bash
# macOS/Linux
rm instance/orchestration.db
python setup_db.py
```

Default credentials will be reset to `admin` / `admin`.

---

### "Health checks show 'flake8 not found'"

**Fix**: Install flake8 in the virtual environment:
```bash
pip install flake8
```

---

### "The claude CLI command is not found"

**Fix**: The Claude CLI is a separate tool from Anthropic. Install it following the [official docs](https://docs.anthropic.com/en/docs/claude-code). After installation, verify with:
```bash
claude --version
```

If you don't need local CLI execution, use the Anthropic API or OpenRouter providers instead.

---

### "Provider test says 'Connection failed'"

**Possible causes**:
1. Wrong API key — double-check in Settings
2. Wrong API Base URL — must include the full URL (e.g., `https://api.anthropic.com`)
3. Network/firewall blocking outbound HTTPS
4. API key expired or rate-limited

---

### "Port 5000 is already in use"

**Fix**: Use a different port:
```bash
python run.py --port 8080
```

Or kill whatever is using port 5000:
```cmd
REM Windows
netstat -ano | findstr :5000
taskkill /PID <the_pid> /F
```
```bash
# macOS/Linux
lsof -i :5000
kill -9 <the_pid>
```

---

### "I see a SECRET_KEY warning"

**Symptom**: `⚠️ SECRET_KEY not set! Using insecure default.`

**Fix**: Set a real secret key:
```cmd
REM Windows
set SECRET_KEY=your-64-character-random-string-here
```
```bash
# macOS/Linux
export SECRET_KEY=your-64-character-random-string-here
```

Or add it to your `.env` file.

---

## FAQ

**Q: Can I use this without Claude Code CLI?**
A: Yes. The Claude CLI is just one provider. You can use the Anthropic API, OpenRouter, or GitHub Copilot instead. Or use the app purely for team management and the implementation plan without any LLM provider.

**Q: How many users can this support?**
A: SQLite handles single-team usage (5-20 users) easily. For larger teams, switch to PostgreSQL by changing the `DATABASE_URL` in `.env`.

**Q: Is this production-ready?**
A: For internal team use, yes. For public-facing deployment, add HTTPS, switch to PostgreSQL, and set all the production environment variables.

**Q: Can I run this on a server?**
A: Yes. Use `python run.py --host 0.0.0.0 --port 5000 --prod` to bind to all interfaces. Put it behind nginx or caddy for TLS.

**Q: What's the 14-day plan based on?**
A: Real-world experience scaling Claude Code from 1 to 10 concurrent instances per developer. Each day includes actual troubleshooting scenarios and escalation paths.

**Q: Can I customize the implementation plan?**
A: The plan is stored in the database. You can modify task text and status through the UI. To fully customize the plan data, edit the `_get_implementation_days()` function in `app.py`.

**Q: How do I add more users?**
A: Log in as admin → go to Team → click "+ Add Team Member". You set their username, password, role, and agent limit.

**Q: What roles are available?**
A: Three roles: **Admin** (full access), **Orchestrator** (manages agents and team, no admin settings), **Developer** (manages only their own agents).

---

## Tech Stack

| Category | Technology | Version |
|---|---|---|
| **Runtime** | Python | 3.10+ |
| **Framework** | Flask | 3.1.0 |
| **Real-time** | Flask-SocketIO + Socket.IO client | 5.5.0 |
| **Auth** | Flask-Login | 0.6.3 |
| **ORM** | Flask-SQLAlchemy + SQLAlchemy | 3.1.1 / 2.0.36 |
| **Database** | SQLite | (built-in) |
| **Scheduler** | Flask-APScheduler | 1.13.1 |
| **Templates** | Jinja2 | 3.1.5 |
| **Encryption** | cryptography (Fernet) | 42.0+ |
| **CLI Parsing** | Click | 8.1.8 |
| **Charts** | Chart.js | 4.x (CDN) |
| **Fonts** | Space Grotesk, Inter, JetBrains Mono | Google Fonts CDN |
| **HTTP Client** | requests | 2.32.3 |
| **System Monitor** | psutil | 6.1.1 |
| **Git Integration** | GitPython | 3.1.44 |
| **Markdown** | Markdown | 3.7 |
| **YAML** | PyYAML | 6.0.2 |
| **Rich Terminal** | Rich | 13.9.4 |

---

<p align="center">
  <strong>🧊 C-C-C-COOLASSAPP</strong><br/>
  <em>Carefully-Crafted-Claude-Code Original Orchestration Layer And Super Serious Appropriately Positioned Project</em><br/><br/>
  Built for teams who think running 10 AI coding agents simultaneously is a reasonable thing to do.<br/>
  <em>(It is.)</em>
</p>
