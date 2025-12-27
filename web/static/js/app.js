// WebSocket подключение
const socket = io();

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
socket.on('connect', () => {
    console.log('Connected to server');
    appState.connected = true;
    updateStatusIndicator(true);
    checkServicesHealth();
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    appState.connected = false;
    updateStatusIndicator(false);
});

// Получение обновлений о новых объектах
socket.on('new_object', (data) => {
    console.log('New object detected:', data);
    appState.objects.unshift(data);
    updateStats(data.risk_level);
    
    // Показываем уведомление
    showNotification(`New object: ${data.object_name}`, data.risk_level);
});

// Обновление индикатора статуса
function updateStatusIndicator(isConnected) {
    const indicator = document.getElementById('statusIndicator');
    if (!indicator) return;
    
    const dot = indicator.querySelector('.status-dot');
    const text = indicator.querySelector('.status-text');
    
    if (isConnected) {
        dot.style.backgroundColor = '#22c55e';
        dot.style.boxShadow = '0 0 10px #22c55e';
        text.textContent = 'Online';
    } else {
        dot.style.backgroundColor = '#ef4444';
        dot.style.boxShadow = 'none';
        text.textContent = 'Offline';
    }
}

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

// Показать уведомление
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
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// API запросы
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Форматирование чисел
function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('StellarTracker initialized');
    
    // Одна проверка при загрузке
    checkServicesHealth();
    
    // Периодическая проверка здоровья сервисов - каждые 60 секунд
    setInterval(checkServicesHealth, 60000);
});
