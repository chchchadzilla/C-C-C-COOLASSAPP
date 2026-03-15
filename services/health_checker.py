# ═══════════════════════════════════════════════════════════════════════════════
# CODEBASE HEALTH CHECKER SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

import os
import json
import subprocess
from datetime import datetime, timezone
from app import db
from models import HealthCheck


def run_health_check(repo_path=None):
    """Run a comprehensive codebase health check."""
    
    check = HealthCheck(check_date=datetime.now(timezone.utc))
    details = {}
    
    # ─── Git Health ───────────────────────────────────────────────────────
    git_health = _check_git_health(repo_path)
    check.total_branches = git_health.get('total_branches', 0)
    check.stale_branches = git_health.get('stale_branches', 0)
    check.unmerged_prs = git_health.get('unmerged_prs', 0)
    check.merge_conflicts_active = git_health.get('merge_conflicts', 0)
    details['git'] = git_health
    
    # ─── Code Quality ─────────────────────────────────────────────────────
    code_quality = _check_code_quality(repo_path)
    check.lint_errors = code_quality.get('lint_errors', 0)
    check.lint_warnings = code_quality.get('lint_warnings', 0)
    check.test_coverage_pct = code_quality.get('test_coverage', 0.0)
    check.tests_passing = code_quality.get('tests_passing', 0)
    check.tests_failing = code_quality.get('tests_failing', 0)
    details['code_quality'] = code_quality
    
    # ─── Claude Context Health ────────────────────────────────────────────
    context_health = _check_context_health(repo_path)
    check.claude_md_files = context_health.get('claude_md_count', 0)
    check.claude_md_avg_lines = context_health.get('claude_md_avg_lines', 0.0)
    check.skills_count = context_health.get('skills_count', 0)
    check.agents_defined = context_health.get('agents_count', 0)
    details['context'] = context_health
    
    # ─── Calculate overall score ──────────────────────────────────────────
    check.health_score = _calculate_health_score(check)
    check.details = json.dumps(details)
    
    db.session.add(check)
    db.session.commit()
    
    return check


def _check_git_health(repo_path=None):
    """Check git repository health."""
    result = {
        'total_branches': 0,
        'stale_branches': 0,
        'unmerged_prs': 0,
        'merge_conflicts': 0,
        'recent_commits_24h': 0,
        'status': 'unknown'
    }
    
    try:
        if repo_path:
            # Count branches
            output = subprocess.run(
                ['git', 'branch', '-a'], 
                capture_output=True, text=True, cwd=repo_path
            )
            if output.returncode == 0:
                branches = [b.strip() for b in output.stdout.strip().split('\n') if b.strip()]
                result['total_branches'] = len(branches)
            
            # Check for merge conflicts
            output = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=U'],
                capture_output=True, text=True, cwd=repo_path
            )
            if output.returncode == 0:
                conflicts = [f for f in output.stdout.strip().split('\n') if f.strip()]
                result['merge_conflicts'] = len(conflicts)
            
            result['status'] = 'healthy' if result['merge_conflicts'] == 0 else 'conflicts'
    except Exception as e:
        result['status'] = f'error: {str(e)}'
    
    return result


def _check_code_quality(repo_path=None):
    """Check code quality metrics by running real lint/test commands."""
    result = {
        'lint_errors': 0,
        'lint_warnings': 0,
        'test_coverage': 0.0,
        'tests_passing': 0,
        'tests_failing': 0,
        'status': 'unknown'
    }

    if not repo_path:
        result['status'] = 'no repo_path configured'
        return result

    # ── Lint with flake8 or ruff (whichever is available) ─────────────
    lint_ran = False
    for linter, args in [
        ('ruff', ['ruff', 'check', '--output-format', 'json', '.']),
        ('flake8', ['flake8', '--format', 'json', '--statistics', '.']),
    ]:
        try:
            out = subprocess.run(
                args, capture_output=True, text=True,
                cwd=repo_path, timeout=60,
            )
            if linter == 'ruff':
                # ruff --output-format json emits a JSON array of issues
                try:
                    issues = json.loads(out.stdout) if out.stdout.strip() else []
                    for issue in issues:
                        # E/F codes are errors, W codes are warnings
                        code = issue.get('code', '')
                        if code.startswith('W'):
                            result['lint_warnings'] += 1
                        else:
                            result['lint_errors'] += 1
                except (json.JSONDecodeError, TypeError):
                    # Fallback: count non-empty lines
                    lines = [l for l in out.stdout.strip().splitlines() if l.strip()]
                    result['lint_errors'] = len(lines)
            else:
                # flake8 text output: count lines
                lines = [l for l in out.stdout.strip().splitlines() if l.strip()]
                result['lint_errors'] = len(lines)

            lint_ran = True
            result['linter'] = linter
            break  # Use whichever linter we found first
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            result['status'] = f'{linter} timed out'
            lint_ran = True
            break
        except Exception as e:
            result['lint_error_detail'] = str(e)

    if not lint_ran:
        result['lint_note'] = 'No linter found (install ruff or flake8)'

    # ── Run pytest (if available) ─────────────────────────────────────
    test_ran = False
    try:
        out = subprocess.run(
            ['python', '-m', 'pytest', '--tb=no', '-q', '--no-header'],
            capture_output=True, text=True,
            cwd=repo_path, timeout=120,
        )
        # pytest -q output last line: "X passed, Y failed" or "X passed"
        summary_line = ''
        for line in reversed(out.stdout.strip().splitlines()):
            if 'passed' in line or 'failed' in line or 'error' in line:
                summary_line = line
                break

        import re
        passed_m = re.search(r'(\d+)\s+passed', summary_line)
        failed_m = re.search(r'(\d+)\s+failed', summary_line)
        error_m = re.search(r'(\d+)\s+error', summary_line)

        result['tests_passing'] = int(passed_m.group(1)) if passed_m else 0
        result['tests_failing'] = (
            (int(failed_m.group(1)) if failed_m else 0) +
            (int(error_m.group(1)) if error_m else 0)
        )
        test_ran = True
    except FileNotFoundError:
        result['test_note'] = 'pytest not found'
    except subprocess.TimeoutExpired:
        result['test_note'] = 'pytest timed out (>120s)'
        test_ran = True
    except Exception as e:
        result['test_error_detail'] = str(e)

    if not test_ran and 'test_note' not in result:
        result['test_note'] = 'Could not run tests'

    # ── Coverage (try pytest-cov) ─────────────────────────────────────
    try:
        out = subprocess.run(
            ['python', '-m', 'pytest', '--cov', '--cov-report=json',
             '--tb=no', '-q', '--no-header'],
            capture_output=True, text=True,
            cwd=repo_path, timeout=180,
        )
        cov_json_path = os.path.join(repo_path, 'coverage.json')
        if os.path.exists(cov_json_path):
            with open(cov_json_path, 'r') as fh:
                cov_data = json.load(fh)
            result['test_coverage'] = round(
                cov_data.get('totals', {}).get('percent_covered', 0.0), 1
            )
            # Clean up
            try:
                os.remove(cov_json_path)
            except OSError:
                pass
    except Exception:
        pass  # Coverage is optional

    total_checks = lint_ran or test_ran
    if total_checks:
        if result['lint_errors'] == 0 and result['tests_failing'] == 0:
            result['status'] = 'healthy'
        elif result['tests_failing'] > 0:
            result['status'] = 'failing tests'
        else:
            result['status'] = 'lint issues'
    else:
        result['status'] = 'no tools available — install ruff and pytest'

    return result


def _check_context_health(repo_path=None):
    """Check Claude Code context configuration health."""
    result = {
        'claude_md_count': 0,
        'claude_md_avg_lines': 0.0,
        'claude_md_over_limit': 0,
        'skills_count': 0,
        'agents_count': 0,
        'hooks_configured': False,
        'permissions_configured': False,
        'recommendations': []
    }
    
    if not repo_path:
        return result
    
    try:
        # Find CLAUDE.md files
        claude_files = []
        for root, dirs, files in os.walk(repo_path):
            for f in files:
                if f.upper() == 'CLAUDE.MD':
                    filepath = os.path.join(root, f)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                        lines = fh.readlines()
                    claude_files.append({'path': filepath, 'lines': len(lines)})
        
        result['claude_md_count'] = len(claude_files)
        if claude_files:
            result['claude_md_avg_lines'] = sum(f['lines'] for f in claude_files) / len(claude_files)
            result['claude_md_over_limit'] = len([f for f in claude_files if f['lines'] > 100])
        
        # Check for skills
        skills_dir = os.path.join(repo_path, '.claude', 'skills')
        if os.path.exists(skills_dir):
            result['skills_count'] = len([
                d for d in os.listdir(skills_dir)
                if os.path.isdir(os.path.join(skills_dir, d))
            ])
        
        # Check for agents
        agents_dir = os.path.join(repo_path, '.claude', 'agents')
        if os.path.exists(agents_dir):
            result['agents_count'] = len([
                f for f in os.listdir(agents_dir)
                if f.endswith('.md')
            ])
        
        # Check for settings
        settings_file = os.path.join(repo_path, '.claude', 'settings.json')
        if os.path.exists(settings_file):
            result['permissions_configured'] = True
            with open(settings_file, 'r') as fh:
                settings = json.load(fh)
                if 'hooks' in settings:
                    result['hooks_configured'] = True
        
        # Generate recommendations
        if result['claude_md_count'] == 0:
            result['recommendations'].append('No CLAUDE.md found! Run /init to create one.')
        if result['claude_md_avg_lines'] > 100:
            result['recommendations'].append('CLAUDE.md files are too long. Split into skills for domain-specific context.')
        if result['skills_count'] == 0:
            result['recommendations'].append('No skills configured. Create .claude/skills/ for reusable workflows.')
        if not result['permissions_configured']:
            result['recommendations'].append('No permissions configured. Use /permissions to set up safe command allowlists.')
    
    except Exception as e:
        result['error'] = str(e)
    
    return result


def _calculate_health_score(check):
    """Calculate an overall health score (0-100)."""
    score = 100.0
    
    # Git health penalties
    if check.merge_conflicts_active > 0:
        score -= min(check.merge_conflicts_active * 10, 30)
    if check.stale_branches > 10:
        score -= 10
    
    # Code quality penalties
    if check.lint_errors > 0:
        score -= min(check.lint_errors * 2, 20)
    if check.tests_failing > 0:
        score -= min(check.tests_failing * 5, 25)
    
    # Context health penalties
    if check.claude_md_files == 0:
        score -= 15
    if check.claude_md_avg_lines > 100:
        score -= 10
    
    # Bonuses
    if check.skills_count > 0:
        score = min(score + 5, 100)
    if check.agents_defined > 0:
        score = min(score + 5, 100)
    
    return max(score, 0)
