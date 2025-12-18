// Level 33 Dashboard - Frontend Application

// Global state
let currentPage = 'dashboard';
let metricsChart = null;
let performanceChart = null;
let ws = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Level 33 Dashboard initialized');
    
    // Setup navigation
    setupNavigation();
    
    // Connect WebSocket
    connectWebSocket();
    
    // Load initial data
    loadDashboardData();
    
    // Setup auto-refresh
    setInterval(refreshData, 30000); // Refresh every 30 seconds
});

// Navigation
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Switch page
            const page = item.dataset.page;
            switchPage(page);
        });
    });
}

function switchPage(page) {
    currentPage = page;
    
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // Show selected page
    const pageElement = document.getElementById(`page-${page}`);
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    // Update title
    const titles = {
        'dashboard': 'Dashboard',
        'activities': 'Activities',
        'metrics': 'Metrics',
        'automations': 'Automations',
        'llm': 'LLM Logs',
        'config': 'Configuration',
        'health': 'Health'
    };
    document.getElementById('page-title').textContent = titles[page] || page;
    
    // Load page data
    loadPageData(page);
}

function loadPageData(page) {
    switch(page) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'activities':
            loadActivities();
            break;
        case 'metrics':
            loadMetrics();
            break;
        case 'automations':
            loadAutomations();
            break;
        case 'llm':
            loadLLMInteractions();
            break;
        case 'config':
            loadConfig();
            break;
        case 'health':
            loadHealth();
            break;
    }
}

// WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('✅ WebSocket connected');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('🔌 WebSocket disconnected, reconnecting...');
        setTimeout(connectWebSocket, 5000);
    };
}

function handleWebSocketMessage(data) {
    if (data.type === 'status_update') {
        updateSystemStats(data.data);
    }
}

// API Calls
async function apiCall(endpoint) {
    try {
        const response = await fetch(`/api${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error calling ${endpoint}:`, error);
        return null;
    }
}

// Dashboard
async function loadDashboardData() {
    const data = await apiCall('/status');
    if (!data) return;
    
    // Update stats
    updateSystemStats(data.system);
    
    // Update Ollama status
    const ollamaStatus = document.getElementById('ollama-status');
    if (ollamaStatus) {
        ollamaStatus.textContent = data.services.ollama ? '✅ Running' : '❌ Offline';
        ollamaStatus.style.color = data.services.ollama ? 'var(--success)' : 'var(--error)';
    }
    
    // Update recent activities
    if (data.recent_activities) {
        displayRecentActivities(data.recent_activities);
    }
    
    // Load metrics chart
    loadMetricsChart();
    
    updateLastUpdate();
}

function updateSystemStats(stats) {
    const cpuUsage = document.getElementById('cpu-usage');
    const memoryUsage = document.getElementById('memory-usage');
    const diskUsage = document.getElementById('disk-usage');
    
    if (cpuUsage && stats.cpu_percent !== undefined) {
        cpuUsage.textContent = `${stats.cpu_percent.toFixed(1)}%`;
        cpuUsage.style.color = stats.cpu_percent > 80 ? 'var(--error)' : 'var(--success)';
    }
    
    if (memoryUsage && stats.memory_percent !== undefined) {
        memoryUsage.textContent = `${stats.memory_percent.toFixed(1)}%`;
        memoryUsage.style.color = stats.memory_percent > 80 ? 'var(--error)' : 'var(--success)';
    }
    
    if (diskUsage && stats.disk_percent !== undefined) {
        diskUsage.textContent = `${stats.disk_percent.toFixed(1)}%`;
        diskUsage.style.color = stats.disk_percent > 80 ? 'var(--error)' : 'var(--success)';
    }
}

function displayRecentActivities(activities) {
    const container = document.getElementById('recent-activities');
    if (!container) return;
    
    if (activities.length === 0) {
        container.innerHTML = '<p class="loading">No recent activities</p>';
        return;
    }
    
    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-info">
                <div class="activity-type">${activity.component} - ${activity.action}</div>
                <div class="activity-details">${activity.type}</div>
            </div>
            <div>
                <div class="activity-status ${activity.status}">${activity.status}</div>
                <div class="activity-time">${formatTime(activity.timestamp)}</div>
            </div>
        </div>
    `).join('');
}

// Activities
async function loadActivities() {
    const data = await apiCall('/activities?limit=100');
    if (!data) return;
    
    const container = document.getElementById('activities-table');
    if (!container) return;
    
    if (data.activities.length === 0) {
        container.innerHTML = '<p class="loading">No activities found</p>';
        return;
    }
    
    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Component</th>
                    <th>Action</th>
                    <th>Status</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
                ${data.activities.map(activity => `
                    <tr>
                        <td>${formatTime(activity.timestamp)}</td>
                        <td>${activity.type}</td>
                        <td>${activity.component}</td>
                        <td>${activity.action}</td>
                        <td><span class="activity-status ${activity.status}">${activity.status}</span></td>
                        <td>${activity.duration ? activity.duration.toFixed(2) + 's' : '-'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Metrics
async function loadMetrics() {
    const data = await apiCall('/metrics?hours=24');
    if (!data) return;
    
    // Create performance chart
    const ctx = document.getElementById('performance-chart');
    if (!ctx) return;
    
    if (performanceChart) {
        performanceChart.destroy();
    }
    
    // Prepare data for chart
    const datasets = [];
    const colors = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    let colorIndex = 0;
    
    for (const [metricName, metricData] of Object.entries(data.metrics)) {
        datasets.push({
            label: metricName,
            data: metricData.map(m => ({
                x: new Date(m.timestamp),
                y: m.value
            })),
            borderColor: colors[colorIndex % colors.length],
            backgroundColor: colors[colorIndex % colors.length] + '20',
            tension: 0.4
        });
        colorIndex++;
    }
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour'
                    },
                    grid: {
                        color: '#4b5563'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                },
                y: {
                    grid: {
                        color: '#4b5563'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#f3f4f6'
                    }
                }
            }
        }
    });
}

async function loadMetricsChart() {
    const ctx = document.getElementById('metrics-chart');
    if (!ctx) return;
    
    // For now, create a simple demo chart
    if (metricsChart) {
        metricsChart.destroy();
    }
    
    metricsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now'],
            datasets: [{
                label: 'CPU Usage',
                data: [45, 52, 48, 55, 50, 47, 49],
                borderColor: '#2563eb',
                backgroundColor: '#2563eb20',
                tension: 0.4
            }, {
                label: 'Memory Usage',
                data: [60, 62, 61, 65, 63, 64, 62],
                borderColor: '#10b981',
                backgroundColor: '#10b98120',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: '#4b5563'
                    },
                    ticks: {
                        color: '#9ca3af',
                        callback: (value) => value + '%'
                    }
                },
                x: {
                    grid: {
                        color: '#4b5563'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#f3f4f6'
                    }
                }
            }
        }
    });
}

// Automations
async function loadAutomations() {
    const data = await apiCall('/automations');
    if (!data) return;
    
    const container = document.getElementById('automations-grid');
    if (!container) return;
    
    container.innerHTML = data.automations.map(automation => `
        <div class="automation-card">
            <div class="automation-header">
                <div class="automation-icon">${automation.icon}</div>
                <div class="automation-title">${automation.name}</div>
            </div>
            <div class="automation-description">${automation.description}</div>
            ${automation.stats ? `
                <div class="automation-stats">
                    <div class="automation-stat">
                        <span class="automation-stat-label">Total Runs</span>
                        <span class="automation-stat-value">${automation.stats.total_runs || 0}</span>
                    </div>
                    <div class="automation-stat">
                        <span class="automation-stat-label">Success Rate</span>
                        <span class="automation-stat-value">${automation.stats.total_runs ? ((automation.stats.successful_runs / automation.stats.total_runs) * 100).toFixed(0) : 0}%</span>
                    </div>
                </div>
            ` : ''}
            <div class="automation-actions">
                <button class="btn btn-primary" onclick="runAutomation('${automation.id}')">▶️ Run</button>
            </div>
        </div>
    `).join('');
}

async function runAutomation(automationId) {
    try {
        const response = await fetch(`/api/automations/${automationId}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        alert(`✅ ${result.message}`);
        
        // Refresh automations list
        loadAutomations();
    } catch (error) {
        console.error('Error running automation:', error);
        alert('❌ Failed to run automation');
    }
}

// LLM Interactions
async function loadLLMInteractions() {
    const data = await apiCall('/llm/interactions?limit=50');
    if (!data) return;
    
    const container = document.getElementById('llm-interactions');
    if (!container) return;
    
    if (data.interactions.length === 0) {
        container.innerHTML = '<p class="loading">No LLM interactions found</p>';
        return;
    }
    
    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Model</th>
                    <th>Prompt</th>
                    <th>Response</th>
                    <th>Tokens</th>
                    <th>Duration</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${data.interactions.map(interaction => `
                    <tr>
                        <td>${formatTime(interaction.timestamp)}</td>
                        <td>${interaction.model}</td>
                        <td title="${interaction.prompt}">${interaction.prompt}</td>
                        <td title="${interaction.response}">${interaction.response || '-'}</td>
                        <td>${interaction.tokens || '-'}</td>
                        <td>${interaction.duration ? interaction.duration.toFixed(2) + 's' : '-'}</td>
                        <td><span class="activity-status ${interaction.success ? 'success' : 'error'}">${interaction.success ? '✅' : '❌'}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Configuration
async function loadConfig() {
    const data = await apiCall('/config');
    if (!data) return;
    
    const container = document.getElementById('config-viewer');
    if (!container) return;
    
    container.innerHTML = `<pre class="config-viewer">${JSON.stringify(data.config, null, 2)}</pre>`;
}

// Health
async function loadHealth() {
    const data = await apiCall('/health');
    if (!data) return;
    
    const container = document.getElementById('health-status');
    if (!container) return;
    
    const statusColors = {
        'healthy': 'var(--success)',
        'degraded': 'var(--warning)',
        'error': 'var(--error)'
    };
    
    let html = `
        <div style="margin-bottom: 2rem;">
            <h4>Overall Status: <span style="color: ${statusColors[data.status]}">${data.status.toUpperCase()}</span></h4>
            <p style="color: var(--text-gray); font-size: 0.875rem;">Last checked: ${formatTime(data.timestamp)}</p>
        </div>
        <div class="health-grid">
    `;
    
    for (const [checkName, checkData] of Object.entries(data.checks)) {
        html += `
            <div class="health-check">
                <div class="health-check-header">
                    <span class="health-check-name">${checkName}</span>
                    <span class="health-check-status ${checkData.status}">${checkData.status.toUpperCase()}</span>
                </div>
                ${checkData.error ? `<div class="health-check-details">Error: ${checkData.error}</div>` : ''}
                ${checkData.percent !== undefined ? `<div class="health-check-details">Usage: ${checkData.percent.toFixed(1)}%</div>` : ''}
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// Utility Functions
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) {
        return 'Just now';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}m ago`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}h ago`;
    } else {
        return date.toLocaleString();
    }
}

function updateLastUpdate() {
    const now = new Date();
    document.getElementById('last-update').textContent = `Last update: ${now.toLocaleTimeString()}`;
}

function refreshData() {
    loadPageData(currentPage);
}
