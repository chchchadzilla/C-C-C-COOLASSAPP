# ═══════════════════════════════════════════════════════════════════════════════
# SCHEDULER SERVICE — Nightly reports and periodic health checks
# ═══════════════════════════════════════════════════════════════════════════════

from flask_apscheduler import APScheduler

scheduler = APScheduler()
_app = None  # Store app reference for context


def init_scheduler(app):
    """Initialize the scheduler for periodic tasks."""
    global _app
    _app = app
    
    class Config:
        SCHEDULER_API_ENABLED = True
        SCHEDULER_TIMEZONE = "UTC"
        JOBS = [
            {
                'id': 'nightly_report',
                'func': 'services.scheduler:generate_nightly',
                'trigger': 'cron',
                'hour': app.config.get('NIGHTLY_REPORT_HOUR', 23),
                'minute': app.config.get('NIGHTLY_REPORT_MINUTE', 0)
            },
            {
                'id': 'health_check',
                'func': 'services.scheduler:run_periodic_health_check',
                'trigger': 'interval',
                'hours': 6
            }
        ]
    
    app.config.from_object(Config)
    
    try:
        scheduler.init_app(app)
        scheduler.start()
    except Exception:
        pass  # Scheduler may already be running in debug mode


def generate_nightly():
    """Scheduled nightly report generation."""
    from services.report_generator import generate_nightly_report
    if _app is None:
        print("[Scheduler] Nightly report skipped: no app context available")
        return
    with _app.app_context():
        try:
            generate_nightly_report()
        except Exception as e:
            print(f"[Scheduler] Nightly report failed: {e}")


def run_periodic_health_check():
    """Scheduled health check."""
    from services.health_checker import run_health_check
    if _app is None:
        print("[Scheduler] Health check skipped: no app context available")
        return
    with _app.app_context():
        try:
            run_health_check()
        except Exception as e:
            print(f"[Scheduler] Health check failed: {e}")
