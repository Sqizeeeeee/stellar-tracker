let riskChart = null;
let activityChart = null;

// Получаем данные из data-атрибутов
const dashboardEl = document.querySelector('.dashboard');

let DASHBOARD_DATA = {
    objectStats: {low: 0, moderate: 0, high: 0, unknown: 0, total: 0},
    processingStats: {total: 0, success: 0, error: 0, success_rate: 0, avg_processing_time: 0},
    highRiskObjects: [],
    userRecent: [],
    popularObjects: [],
    totalObservations: 0
};

if (dashboardEl) {
    console.log('📦 Raw data attributes:', {
        stats: dashboardEl.dataset.stats,
        processing: dashboardEl.dataset.processing,
        highRisk: dashboardEl.dataset.highRisk,
        userRecent: dashboardEl.dataset.userRecent,
        popular: dashboardEl.dataset.popular,
        totalObs: dashboardEl.dataset.totalObs
    });
    
    try {
        DASHBOARD_DATA.objectStats = JSON.parse(dashboardEl.dataset.stats || '{}');
        DASHBOARD_DATA.processingStats = JSON.parse(dashboardEl.dataset.processing || '{}');
        DASHBOARD_DATA.highRiskObjects = JSON.parse(dashboardEl.dataset.highRisk || '[]');
        DASHBOARD_DATA.userRecent = JSON.parse(dashboardEl.dataset.userRecent || '[]');
        DASHBOARD_DATA.popularObjects = JSON.parse(dashboardEl.dataset.popular || '[]');
        DASHBOARD_DATA.totalObservations = parseInt(dashboardEl.dataset.totalObs || '0');
        
        console.log('✅ Dashboard data loaded:', DASHBOARD_DATA);
    } catch (e) {
        console.error('❌ Error parsing dashboard data:', e);
    }
} else {
    console.error('❌ Dashboard element not found!');
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎨 Initializing dashboard...');
    initRiskChart();
    console.log('Dashboard initialized');
});

function initRiskChart() {
    const canvas = document.getElementById('riskChart');
    if (!canvas) {
        console.warn('⚠️ Risk chart canvas not found');
        return;
    }

    const stats = DASHBOARD_DATA.objectStats;
    
    const chartData = [
        stats.high || 0,
        stats.moderate || 0,
        stats.low || 0,
        stats.unknown || 0
    ];
    
    const total = chartData.reduce((a, b) => a + b, 0);
    
    console.log('📊 Creating risk chart with data:', {stats, chartData, total});
    
    if (total === 0) {
        console.warn('⚠️ No data for chart, showing empty state');
        // Показываем заглушку если нет данных
        canvas.parentElement.innerHTML = `
            <h3>Risk Distribution</h3>
            <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
                <p>📊 No objects tracked yet</p>
                <p style="font-size: 0.9em; margin-top: 10px;">Upload observations to see risk distribution</p>
            </div>
        `;
        return;
    }
    
    try {
        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['High Risk', 'Moderate Risk', 'Low Risk', 'Unknown'],
                datasets: [{
                    data: chartData,
                    backgroundColor: [
                        '#ef4444', // red
                        '#f59e0b', // yellow
                        '#10b981', // green
                        '#6b7280'  // gray
                    ],
                    borderWidth: 2,
                    borderColor: '#1a1a2e'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#e0e0e0',
                            font: {
                                size: 12
                            },
                            padding: 15
                        }
                    }
                }
            }
        });
        console.log('✅ Risk chart created successfully');
    } catch (error) {
        console.error('❌ Error creating chart:', error);
    }
}
