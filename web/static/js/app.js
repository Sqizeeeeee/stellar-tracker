// WebSocket подключение
// const socket = io();

// Глобальное состояние
const appState = {
    connected: false,
    objects: [],
    stats: {
        total: 0,
        high_risk: 0,
        moderate_risk: 0,
        low_risk: 0
    },
    lastHealthCheck: null
};

// Подключение к WebSocket
// socket.on('connect', () => {
//     console.log('Connected to server');
//     appState.connected = true;
//     updateStatusIndicator(true);
//     checkServicesHealth();
// });

// socket.on('disconnect', () => {
//     console.log('Disconnected from server');
//     appState.connected = false;
//     updateStatusIndicator(false);
// });

// Получение обновлений о новых объектах
// socket.on('new_object', (data) => {
//     console.log('New object detected:', data);
//     appState.objects.unshift(data);
//     updateStats(data.risk_level);
    
//     // Показываем уведомление
//     showNotification(`New object: ${data.object_name}`, data.risk_level);
// });

// Обновление индикатора статуса
// function updateStatusIndicator(isConnected) {
//     const indicator = document.getElementById('statusIndicator');
//     if (!indicator) return;
    
//     const dot = indicator.querySelector('.status-dot');
//     const text = indicator.querySelector('.status-text');
    
//     if (isConnected) {
//         dot.style.backgroundColor = '#22c55e';
//         dot.style.boxShadow = '0 0 10px #22c55e';
//         text.textContent = 'Online';
//     } else {
//         dot.style.backgroundColor = '#ef4444';
//         dot.style.boxShadow = 'none';
//         text.textContent = 'Offline';
//     }
// }

// Проверка здоровья сервисов с debouncing
async function checkServicesHealth() {
    const now = Date.now();
    
    // Проверяем не чаще чем раз в 5 секунд
    if (appState.lastHealthCheck && (now - appState.lastHealthCheck) < 5000) {
        return;
    }
    
    appState.lastHealthCheck = now;
    
    try {
        const response = await fetch('/api/health');
        const health = await response.json();
        console.log('Services health:', health);
        
        const allHealthy = Object.values(health).every(status => status === 'healthy');
        if (!allHealthy) {
            console.warn('Some services are unhealthy:', health);
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Обновление статистики
function updateStats(riskLevel) {
    appState.stats.total++;
    
    switch(riskLevel) {
        case 'high':
            appState.stats.high_risk++;
            break;
        case 'moderate':
            appState.stats.moderate_risk++;
            break;
        case 'low':
            appState.stats.low_risk++;
            break;
    }
    
    // Обновляем UI если элементы существуют
    const totalEl = document.getElementById('totalObjects');
    const highEl = document.getElementById('highRiskCount');
    const modEl = document.getElementById('moderateRiskCount');
    const lowEl = document.getElementById('lowRiskCount');
    
    if (totalEl) totalEl.textContent = appState.stats.total;
    if (highEl) highEl.textContent = appState.stats.high_risk;
    if (modEl) modEl.textContent = appState.stats.moderate_risk;
    if (lowEl) lowEl.textContent = appState.stats.low_risk;
}

// Показываем уведомление (оставляем реализацию)
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    const icon = type === 'high' ? '🔴' :
                 type === 'moderate' ? '🟡' :
                 type === 'low' ? '🟢' :
                 type === 'warning' ? '⚠️' : 'ℹ️';
    notification.innerHTML = `
        <span class="notification-icon">${icon}</span>
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Сохраняем id последних объектов, чтобы не дублировать уведомления
let lastObjectIds = [];

// Polling новых объектов
async function pollRecentObjects() {
    try {
        const resp = await apiRequest('/api/objects/recent?limit=5');
        if (resp.success && Array.isArray(resp.objects)) {
            // Проверяем новые объекты
            const newIds = resp.objects.map(obj => obj.id);
            if (lastObjectIds.length > 0) {
                resp.objects.forEach(obj => {
                    if (!lastObjectIds.includes(obj.id)) {
                        showNotification(
                            `New object: ${obj.object_name}`,
                            obj.risk?.risk_level || 'info'
                        );
                    }
                });
            }
            lastObjectIds = newIds;
            // Можно обновлять список объектов на странице, если нужно
        }
    } catch (e) {
        // ignore polling errors
    }
}

// Polling статистики
async function pollStats() {
    try {
        const resp = await apiRequest('/api/objects/stats');
        if (resp.success && resp.stats) {
            // Обновляем элементы на странице, если они есть
            const totalEl = document.getElementById('totalObjects');
            const highEl = document.getElementById('highRiskCount');
            const modEl = document.getElementById('moderateRiskCount');
            const lowEl = document.getElementById('lowRiskCount');
            if (totalEl) totalEl.textContent = resp.stats.total;
            if (highEl) highEl.textContent = resp.stats.high;
            if (modEl) modEl.textContent = resp.stats.moderate;
            if (lowEl) lowEl.textContent = resp.stats.low;
        }
    } catch (e) {
        // ignore polling errors
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('StellarTracker initialized');
    
    // Одна проверка при загрузке
    checkServicesHealth();
    
    // Периодическая проверка здоровья сервисов - каждые 60 секунд
    setInterval(checkServicesHealth, 60000);

    pollRecentObjects();
    pollStats();
    setInterval(pollRecentObjects, 5000); // каждые 5 секунд
    setInterval(pollStats, 10000);        // каждые 10 секунд
});
