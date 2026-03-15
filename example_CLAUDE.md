# C-C-C-COOLASSAPP — Example CLAUDE.md Template
#
# This file is a TEMPLATE showing best practices for CLAUDE.md files
# that your team's Claude Code instances will use.
# Copy and customize this for each project repository.

---
description: AI coding agent context for [PROJECT NAME]
applyTo: "**"
---

# CLAUDE.md — [PROJECT NAME]

## PROJECT OVERVIEW
[One paragraph describing what this project does, who it's for, and its current state.]

**Tech Stack**: [Language] + [Framework] + [Database] + [Key Libraries]
**Status**: [Active Development / Maintenance / Pre-release]
**Team Size**: [N developers] × [M Claude Code agents each]

## BUILD & TEST COMMANDS

```bash
# Install dependencies
[npm install / pip install -r requirements.txt / etc.]

# Run development server
[npm run dev / python manage.py runserver / etc.]

# Run all tests
[npm test / pytest / etc.]

# Run specific test file
[npm test -- path/to/test / pytest path/to/test.py / etc.]

# Lint / format
[npm run lint / ruff check . / etc.]

# Build for production
[npm run build / python setup.py build / etc.]
```

## CODE STYLE & CONVENTIONS

- **Language version**: [e.g., Python 3.12, TypeScript 5.3, Node 20]
- **Formatting**: [e.g., Black with 88-char lines, Prettier with tabs]
- **Naming conventions**: [e.g., snake_case for Python, camelCase for JS]
- **Import ordering**: [e.g., stdlib → third-party → local, alphabetical within groups]
- **Error handling**: [e.g., Always use custom exception classes, never bare except]
- **Comments**: [e.g., Docstrings required for all public functions, JSDoc for exports]

## FOLDER STRUCTURE

```
project-root/
├── src/              # Source code
│   ├── models/       # Data models / ORM
│   ├── routes/       # API endpoints / controllers
│   ├── services/     # Business logic
│   ├── utils/        # Shared utilities
│   └── types/        # Type definitions
├── tests/            # Test files (mirror src/ structure)
├── docs/             # Documentation
├── scripts/          # Build / deploy scripts
└── config/           # Configuration files
```

## ARCHITECTURE DECISIONS

### [Decision 1: e.g., "Why we use SQLAlchemy over raw SQL"]
**Context**: [What problem we were solving]
**Decision**: [What we chose]
**Consequences**: [Trade-offs and implications]

### [Decision 2: e.g., "Event-driven architecture for notifications"]
**Context**: [...]
**Decision**: [...]
**Consequences**: [...]

## CRITICAL RULES — DO NOT VIOLATE

1. **Never commit directly to `main`** — always use feature branches
2. **All PRs require tests** — no merging without test coverage
3. **Database migrations must be reversible** — always include downgrade
4. **No secrets in code** — use environment variables or vault
5. **[Project-specific rule]** — [explanation]

## CURRENT FOCUS AREAS

- [ ] [Current sprint goal or feature being built]
- [ ] [Known bug being investigated]
- [ ] [Technical debt being addressed]
- [ ] [Performance optimization target]

## AGENT-SPECIFIC GUIDANCE

### For Code Review Agents
- Check for: [security issues, performance problems, style violations]
- Always verify: [test coverage, error handling, type safety]
- Flag if: [new dependencies added, API contracts changed, migrations present]

### For Test Writing Agents
- Framework: [pytest / jest / etc.]
- Patterns: [Arrange-Act-Assert / Given-When-Then]
- Coverage target: [e.g., 80% minimum, 100% for critical paths]
- Mock strategy: [e.g., unittest.mock, jest.mock, dependency injection]

### For Feature Development Agents
- Branch naming: [feature/TICKET-description, bugfix/TICKET-description]
- Commit format: [conventional commits: feat:, fix:, docs:, etc.]
- PR template: [description, testing notes, screenshots if UI]
- Before submitting: [run linter, run tests, update docs if needed]

## KNOWN ISSUES & WORKAROUNDS

| Issue | Workaround | Tracking |
|-------|-----------|----------|
| [Brief description] | [How to work around it] | [Link to issue] |

## ENVIRONMENT VARIABLES

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Database connection string | — |
| `SECRET_KEY` | Yes | Session encryption key | — |
| `DEBUG` | No | Enable debug mode | `false` |
| `[OTHER_VAR]` | [Yes/No] | [Description] | [Default] |

## DEBUGGING TIPS

- **Common error 1**: [Error message] → [How to fix]
- **Common error 2**: [Error message] → [How to fix]
- **Logs location**: [Where to find logs]
- **Health check**: [How to verify system is working]

## CONTEXT FOR AI AGENTS

When working on this codebase, keep in mind:

1. **Scope your changes** — modify only what's needed, don't refactor unrelated code
2. **Check existing patterns** — look at similar files before creating new approaches
3. **Run tests before committing** — never assume your changes are correct
4. **Ask if uncertain** — flag ambiguity rather than guessing
5. **Document non-obvious choices** — add comments explaining "why", not "what"
