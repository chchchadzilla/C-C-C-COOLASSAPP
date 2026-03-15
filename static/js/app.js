/**
 * C-C-C-COOLASSAPP
 * Main Application JavaScript
 * 
 * Handles:
 * - WebSocket real-time updates via Socket.IO
 * - Chart.js dashboard and analytics visualizations
 * - API utility functions
 * - UI interactions and dynamic components
 */

// ============================================================
// 1. Socket.IO Real-Time Connection
// ============================================================

const socket = io ? io() : null;

if (socket) {
    socket.on('connect', () => {
        console.log('[Orchestrator] WebSocket connected');
        showToast('Real-time updates active', 'success');
    });

    socket.on('disconnect', () => {
        console.log('[Orchestrator] WebSocket disconnected');
        showToast('Connection lost — reconnecting…', 'warning');
    });

    // Agent status changed
    socket.on('agent_update', (data) => {
        console.log('[Orchestrator] Agent update:', data);
        updateAgentCard(data);
        updateDashboardMetrics();
    });

    // New health check result
    socket.on('health_update', (data) => {
        console.log('[Orchestrator] Health update:', data);
        updateHealthRing(data.health_score);
        if (data.health_score < 60) {
            showToast(`Health score dropped to ${data.health_score}%`, 'danger');
        }
    });

    // Nightly report generated
    socket.on('new_report', (data) => {
        console.log('[Orchestrator] New report:', data);
        showToast('Nightly report generated — view it now', 'info');
    });

    // Remote view live output
    socket.on('agent_output', (data) => {
        appendTerminalOutput(data.output);
    });
}


// ============================================================
// 2. API Utility Functions
// ============================================================

const API = {
    baseUrl: '/api',

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaults = {
            headers: { 'Content-Type': 'application/json' },
        };
        const config = { ...defaults, ...options };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`[API] ${endpoint}:`, error);
            showToast(error.message, 'danger');
            throw error;
        }
    },

    // Agents
    getAgents()          { return this.request('/agents'); },
    getAgent(id)         { return this.request(`/agents/${id}`); },
    assignTask(id, data) { return this.request(`/agents/${id}/assign`, { method: 'POST', body: JSON.stringify(data) }); },
    completeTask(id)     { return this.request(`/agents/${id}/complete`, { method: 'POST' }); },
    terminateAgent(id)   { return this.request(`/agents/${id}/terminate`, { method: 'POST' }); },

    // Users
    getUsers()           { return this.request('/users'); },
    getUser(id)          { return this.request(`/users/${id}`); },

    // Reports
    getReports()         { return this.request('/reports'); },
    generateReport()     { return this.request('/reports/generate', { method: 'POST' }); },

    // Health
    getHealth()          { return this.request('/health'); },
    runHealthCheck()     { return this.request('/health/check', { method: 'POST' }); },

    // Dashboard summary
    getDashboard()       { return this.request('/dashboard'); },
};


// ============================================================
// 3. Toast / Flash Notification System
// ============================================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${getToastIcon(type)}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    container.appendChild(toast);

    // Auto-dismiss
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:10000;display:flex;flex-direction:column;gap:0.5rem;';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = { success: '✓', danger: '✕', warning: '⚠', info: 'ℹ' };
    return icons[type] || icons.info;
}


// ============================================================
// 4. Dashboard Real-Time Updates
// ============================================================

function updateAgentCard(data) {
    const card = document.querySelector(`[data-agent-id="${data.agent_id}"]`);
    if (!card) return;

    // Update status indicator
    const statusDot = card.querySelector('.status-dot, .agent-dot');
    if (statusDot) {
        statusDot.className = statusDot.className.replace(/status-\w+|dot-\w+/g, '');
        statusDot.classList.add(`status-${data.status}`, `dot-${data.status}`);
    }

    // Update task text
    const taskEl = card.querySelector('.agent-task, .current-task');
    if (taskEl) {
        taskEl.textContent = data.current_task || 'Idle';
    }
}

function updateDashboardMetrics() {
    // Refresh metric cards via API
    API.getDashboard().then(data => {
        updateMetricCard('total-agents', data.total_agents);
        updateMetricCard('active-agents', data.active_agents);
        updateMetricCard('tasks-today', data.tasks_completed_today);
        updateMetricCard('health-score', data.health_score);
        updateMetricCard('merge-conflicts', data.merge_conflicts);
        updateMetricCard('total-users', data.total_users);
    }).catch(() => {});
}

function updateMetricCard(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function updateHealthRing(score) {
    const circle = document.querySelector('.health-ring-progress');
    if (!circle) return;

    const radius = circle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    circle.style.strokeDashoffset = offset;

    const label = document.querySelector('.health-ring-label');
    if (label) label.textContent = `${score}%`;

    // Color based on score
    let color = '#10b981'; // green
    if (score < 60) color = '#ef4444'; // red
    else if (score < 80) color = '#f59e0b'; // amber
    circle.style.stroke = color;
}


// ============================================================
// 5. Chart.js Configurations & Initialization
// ============================================================

const ChartConfigs = {
    // Shared dark theme defaults
    defaults() {
        if (typeof Chart === 'undefined') return;

        Chart.defaults.color = '#94a3b8';
        Chart.defaults.borderColor = 'rgba(148, 163, 184, 0.1)';
        Chart.defaults.font.family = "'Inter', 'Segoe UI', system-ui, sans-serif";
    },

    // Daily activity trend (analytics page)
    dailyTrends(canvasId, labels, datasets) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: datasets.map((ds, i) => ({
                    label: ds.label,
                    data: ds.data,
                    borderColor: this.colors[i % this.colors.length],
                    backgroundColor: this.colors[i % this.colors.length] + '20',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderWidth: 1,
                    }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.08)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    },

    // User comparison bar chart
    userComparison(canvasId, labels, tasksCompleted, mergeConflicts) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Tasks Completed',
                        data: tasksCompleted,
                        backgroundColor: '#6366f1',
                        borderRadius: 4,
                    },
                    {
                        label: 'Merge Conflicts',
                        data: mergeConflicts,
                        backgroundColor: '#ef4444',
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.08)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    },

    // Failure pattern pie/doughnut
    failurePatterns(canvasId, labels, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: ['#ef4444', '#f59e0b', '#6366f1', '#10b981', '#8b5cf6'],
                    borderWidth: 0,
                    hoverOffset: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: { position: 'right' }
                }
            }
        });
    },

    // Health score history line chart
    healthHistory(canvasId, labels, scores) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Health Score',
                    data: scores,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    pointBackgroundColor: scores.map(s =>
                        s >= 80 ? '#10b981' : s >= 60 ? '#f59e0b' : '#ef4444'
                    ),
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `Score: ${ctx.parsed.y}%`
                        }
                    }
                },
                scales: {
                    y: { min: 0, max: 100, grid: { color: 'rgba(148,163,184,0.08)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    },

    colors: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899']
};


// ============================================================
// 6. Remote View Terminal
// ============================================================

const RemoteTerminal = {
    container: null,
    autoScroll: true,
    maxLines: 1000,

    init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        // Toggle auto-scroll on manual scroll
        this.container.addEventListener('scroll', () => {
            const { scrollTop, scrollHeight, clientHeight } = this.container;
            this.autoScroll = (scrollHeight - scrollTop - clientHeight) < 50;
        });
    },

    append(text) {
        if (!this.container) return;

        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.innerHTML = this.colorize(text);
        this.container.appendChild(line);

        // Trim excess lines
        while (this.container.children.length > this.maxLines) {
            this.container.removeChild(this.container.firstChild);
        }

        if (this.autoScroll) {
            this.container.scrollTop = this.container.scrollHeight;
        }
    },

    clear() {
        if (this.container) this.container.innerHTML = '';
    },

    colorize(text) {
        // Basic ANSI-like coloring for common patterns
        return text
            .replace(/\b(ERROR|FAIL|FAILED)\b/gi, '<span style="color:#ef4444;font-weight:600">$1</span>')
            .replace(/\b(WARN|WARNING)\b/gi, '<span style="color:#f59e0b;font-weight:600">$1</span>')
            .replace(/\b(OK|PASS|PASSED|SUCCESS)\b/gi, '<span style="color:#10b981;font-weight:600">$1</span>')
            .replace(/\b(INFO)\b/gi, '<span style="color:#6366f1;font-weight:600">$1</span>')
            .replace(/(\/[\w./\-]+\.\w+)/g, '<span style="color:#06b6d4">$1</span>')
            .replace(/(\d+\.\d+s)/g, '<span style="color:#f59e0b">$1</span>');
    }
};

function appendTerminalOutput(text) {
    RemoteTerminal.append(text);
}


// ============================================================
// 7. Agent Actions (used by detail / remote pages)
// ============================================================

async function pauseAgent(agentId) {
    if (!confirm('Pause this agent?')) return;
    try {
        await API.request(`/agents/${agentId}/pause`, { method: 'POST' });
        showToast('Agent paused', 'info');
        location.reload();
    } catch (e) { /* toast already shown */ }
}

async function resumeAgent(agentId) {
    try {
        await API.request(`/agents/${agentId}/resume`, { method: 'POST' });
        showToast('Agent resumed', 'success');
        location.reload();
    } catch (e) { /* toast already shown */ }
}

async function terminateAgent(agentId) {
    if (!confirm('⚠ Terminate this agent? This cannot be undone.')) return;
    try {
        await API.terminateAgent(agentId);
        showToast('Agent terminated', 'warning');
        setTimeout(() => window.location.href = '/agents', 800);
    } catch (e) { /* toast already shown */ }
}

async function assignTask(agentId) {
    const task = prompt('Enter task description:');
    if (!task) return;
    const branch = prompt('Branch name (optional):') || '';
    try {
        await API.assignTask(agentId, { task, branch });
        showToast('Task assigned', 'success');
        location.reload();
    } catch (e) { /* toast already shown */ }
}


// ============================================================
// 8. Report Generation
// ============================================================

async function generateReport() {
    const btn = document.getElementById('generate-report-btn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Generating…';
    }
    try {
        const result = await API.generateReport();
        showToast('Report generated successfully', 'success');
        if (result.report_id) {
            window.location.href = `/reports/${result.report_id}`;
        } else {
            location.reload();
        }
    } catch (e) {
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Generate Report';
        }
    }
}


// ============================================================
// 9. Health Check Trigger
// ============================================================

async function runHealthCheck() {
    const btn = document.getElementById('run-health-btn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Running…';
    }
    try {
        const result = await API.runHealthCheck();
        showToast(`Health check complete — Score: ${result.health_score}%`, 'success');
        location.reload();
    } catch (e) {
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Run Health Check';
        }
    }
}


// ============================================================
// 10. Implementation Plan Interactions
// ============================================================

function updateDayStatus(dayNumber, status) {
    fetch(`/implementation/day/${dayNumber}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `status=${status}`
    })
    .then(r => {
        if (r.ok) {
            showToast(`Day ${dayNumber} marked as ${status}`, 'success');
            location.reload();
        } else {
            showToast('Failed to update status', 'danger');
        }
    })
    .catch(() => showToast('Network error', 'danger'));
}


// ============================================================
// 11. Failure Log Form
// ============================================================

function toggleFailureForm() {
    const form = document.getElementById('failure-form');
    if (!form) return;
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function resolveFailure(failureId) {
    const resolution = prompt('Describe the resolution:');
    if (!resolution) return;

    fetch(`/implementation/failures/${failureId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `resolution=${encodeURIComponent(resolution)}`
    })
    .then(r => {
        if (r.ok) {
            showToast('Failure resolved', 'success');
            location.reload();
        } else {
            showToast('Failed to resolve', 'danger');
        }
    })
    .catch(() => showToast('Network error', 'danger'));
}


// ============================================================
// 12. Utility Functions
// ============================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function formatDuration(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard', 'success');
    }).catch(() => {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
        showToast('Copied to clipboard', 'success');
    });
}

// Confirmation wrapper for dangerous actions
function confirmAction(message, action) {
    if (confirm(message)) action();
}


// ============================================================
// 13. Auto-Refresh for Dashboard
// ============================================================

let dashboardRefreshInterval = null;

function startDashboardRefresh(intervalMs = 30000) {
    if (dashboardRefreshInterval) clearInterval(dashboardRefreshInterval);
    dashboardRefreshInterval = setInterval(() => {
        updateDashboardMetrics();
    }, intervalMs);
}

function stopDashboardRefresh() {
    if (dashboardRefreshInterval) {
        clearInterval(dashboardRefreshInterval);
        dashboardRefreshInterval = null;
    }
}


// ============================================================
// 14. Flash Message Auto-Dismiss
// ============================================================

function initFlashMessages() {
    document.querySelectorAll('.flash-message').forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 300);
        }, 6000);

        // Click to dismiss
        msg.addEventListener('click', () => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 200);
        });
    });
}


// ============================================================
// 15. Sidebar Active State
// ============================================================

function initSidebar() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
}


// ============================================================
// 16. Code Block Copy Buttons (Best Practices pages)
// ============================================================

function initCodeBlocks() {
    document.querySelectorAll('.code-block, pre code').forEach(block => {
        const wrapper = block.closest('.code-block') || block.parentElement;
        if (wrapper.querySelector('.copy-btn')) return; // already has one

        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.textContent = 'Copy';
        btn.title = 'Copy to clipboard';
        btn.addEventListener('click', () => {
            const code = block.textContent;
            copyToClipboard(code);
            btn.textContent = 'Copied!';
            setTimeout(() => btn.textContent = 'Copy', 2000);
        });
        wrapper.style.position = 'relative';
        wrapper.appendChild(btn);
    });
}


// ============================================================
// 17. Search / Filter for Tables
// ============================================================

function initTableSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!input || !table) return;

    input.addEventListener('input', () => {
        const query = input.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    });
}


// ============================================================
// 18. Agent Dot Grid Animation (Dashboard)
// ============================================================

function initAgentDots() {
    document.querySelectorAll('.agent-dot').forEach(dot => {
        dot.addEventListener('mouseenter', () => {
            const tooltip = dot.getAttribute('data-tooltip');
            if (tooltip) {
                dot.title = tooltip;
            }
        });
    });
}


// ============================================================
// 19. Scaling Slider (User Management)
// ============================================================

function initScalingSliders() {
    document.querySelectorAll('.scale-slider').forEach(slider => {
        const display = slider.nextElementSibling;
        slider.addEventListener('input', () => {
            if (display) display.textContent = slider.value;
        });
    });
}


// ============================================================
// 20. Keyboard Shortcuts
// ============================================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+/ -> Toggle sidebar (future)
        // Escape -> Close modals
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal.active');
            if (modal) modal.classList.remove('active');
        }

        // Ctrl+K -> Focus search (if present)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const search = document.querySelector('.search-input, #search-input');
            if (search) search.focus();
        }
    });
}


// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    // Set Chart.js defaults
    ChartConfigs.defaults();

    // Common initializations
    initFlashMessages();
    initSidebar();
    initCodeBlocks();
    initAgentDots();
    initScalingSliders();
    initKeyboardShortcuts();

    // Page-specific initialization
    const page = document.body.dataset.page || '';

    if (page === 'dashboard') {
        startDashboardRefresh(30000);
    }

    if (page === 'remote-view') {
        const agentId = document.body.dataset.agentId;
        RemoteTerminal.init('terminal-output');
        if (agentId && socket) {
            socket.emit('join_agent', { agent_id: agentId });
        }
    }

    if (page === 'analytics') {
        initAnalyticsCharts();
    }

    if (page === 'health-history') {
        initHealthHistoryChart();
    }

    console.log('[Orchestrator] Application initialized');
});


// ============================================================
// Page-specific chart initializers (called from templates)
// ============================================================

function initAnalyticsCharts() {
    // These expect data attributes or inline script vars set by the template
    const dailyEl = document.getElementById('daily-trends-chart');
    const userEl = document.getElementById('user-comparison-chart');
    const failEl = document.getElementById('failure-patterns-chart');

    if (dailyEl && window.dailyTrendsData) {
        ChartConfigs.dailyTrends(
            'daily-trends-chart',
            window.dailyTrendsData.labels,
            window.dailyTrendsData.datasets
        );
    }

    if (userEl && window.userComparisonData) {
        ChartConfigs.userComparison(
            'user-comparison-chart',
            window.userComparisonData.labels,
            window.userComparisonData.tasksCompleted,
            window.userComparisonData.mergeConflicts
        );
    }

    if (failEl && window.failurePatternsData) {
        ChartConfigs.failurePatterns(
            'failure-patterns-chart',
            window.failurePatternsData.labels,
            window.failurePatternsData.data
        );
    }
}

function initHealthHistoryChart() {
    const el = document.getElementById('health-history-chart');
    if (el && window.healthHistoryData) {
        ChartConfigs.healthHistory(
            'health-history-chart',
            window.healthHistoryData.labels,
            window.healthHistoryData.scores
        );
    }
}
