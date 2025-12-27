let riskChart = null;
let activityChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    loadInitialData();
});

// Initialize Chart.js charts
function initializeCharts() {
    const riskCtx = document.getElementById('riskChart');
    if (riskCtx) {
        riskChart = new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: ['High Risk', 'Moderate Risk', 'Low Risk'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#22c55e'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#f1f5f9', padding: 15 }
                    }
                }
            }
        });
    }

    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        activityChart = new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Objects Detected',
                    data: [],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    y: {
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f1f5f9' } }
                }
            }
        });
    }
}

// Load initial data
function loadInitialData() {
    // This would normally fetch from an API
    console.log('Dashboard initialized');
}

// Update stats when new object is detected
socket.on('new_object', (data) => {
    updateObjectList(data);
    updateCharts(data);
});

// Update object list
function updateObjectList(data) {
    const list = document.getElementById('recentObjects');
    if (!list) return;
    
    const empty = list.querySelector('.empty-state');
    if (empty) empty.remove();
    
    const item = document.createElement('div');
    item.className = 'object-item';
    item.innerHTML = `
        <div class="object-header">
            <span class="object-name">${data.object_name}</span>
            <span class="object-risk risk-${data.risk_level}">${data.risk_level}</span>
        </div>
        <div class="object-details">
            <span>MOID: ${data.moid ? data.moid.toFixed(4) : 'N/A'} AU</span>
            <span>${new Date(data.timestamp).toLocaleString('ru-RU')}</span>
        </div>
    `;
    
    list.insertBefore(item, list.firstChild);
    
    // Keep only last 10 items
    while (list.children.length > 10) {
        list.removeChild(list.lastChild);
    }
}

// Update charts
function updateCharts(data) {
    if (riskChart) {
        const riskIndex = data.risk_level === 'high' ? 0 : 
                         data.risk_level === 'moderate' ? 1 : 2;
        riskChart.data.datasets[0].data[riskIndex]++;
        riskChart.update();
    }
    
    if (activityChart) {
        const now = new Date().toLocaleTimeString('ru-RU');
        activityChart.data.labels.push(now);
        activityChart.data.datasets[0].data.push(
            activityChart.data.datasets[0].data.length + 1
        );
        
        // Keep only last 10 data points
        if (activityChart.data.labels.length > 10) {
            activityChart.data.labels.shift();
            activityChart.data.datasets[0].data.shift();
        }
        
        activityChart.update();
    }
}
