"""Quick route test - uses test_client so no server needed."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import create_app

app = create_app()
app.config['TESTING'] = True

with app.test_client() as c:
    # Login first (works because USING_DEFAULT_SECRET is true in dev)
    c.get('/test-login')
    
    routes = [
        ('GET',  '/'),
        ('GET',  '/agents/'),
        ('GET',  '/users/'),
        ('GET',  '/reports/'),
        ('GET',  '/health/'),
        ('GET',  '/implementation/'),
        ('GET',  '/best-practices/'),
        ('GET',  '/api-keys/'),
        ('GET',  '/settings/'),
        ('GET',  '/reports/analytics'),
        # API routes
        ('GET',  '/api/'),
        ('GET',  '/api/users'),
        ('GET',  '/api/agents'),
        ('GET',  '/api/reports'),
        ('GET',  '/api/implementation'),
        ('GET',  '/api/health'),
        ('GET',  '/api/failures'),
        ('GET',  '/api/stats'),
        ('GET',  '/api/providers'),
        ('GET',  '/api/sla'),
        ('GET',  '/api/queue'),
        # Agent CLI status
        ('GET',  '/agents/cli-status'),
    ]
    
    all_ok = True
    for method, route in routes:
        if method == 'GET':
            r = c.get(route)
        else:
            r = c.post(route)
        status = r.status_code
        ok = '✓' if status == 200 else '✗'
        if status != 200:
            all_ok = False
        print(f'  {ok} {method} {route}: {status}')
    
    print()
    print('ALL PASS' if all_ok else 'SOME FAILED')
