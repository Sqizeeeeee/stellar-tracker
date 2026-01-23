from typing import Dict, Any, List


def format_service_status(services: Dict[str, bool]) -> str:
    """Форматировать статус сервисов для вывода"""
    if not services:
        return "⚠️ Не удалось получить статус сервисов"
    
    message = "📊 <b>Статус сервисов:</b>\n\n"
    
    service_icons = {
        "orchestrator": "🎯",
        "orbit-service": "🛰️",
        "collision-service": "💥",
        "web-service": "🌐",
        "prometheus": "📈",
        "node-exporter": "💻",
        "cadvisor": "🐳"
    }
    
    for service, is_up in services.items():
        icon = service_icons.get(service, "⚙️")
        status = "✅ UP" if is_up else "❌ DOWN"
        message += f"{icon} <b>{service}</b>: {status}\n"
    
    return message


def format_stats(stats: Dict[str, Any]) -> str:
    """Форматировать статистику для вывода"""
    if not stats:
        return "⚠️ Не удалось получить статистику"
    
    total = stats.get("total_requests", 0)
    success = stats.get("success_requests", 0)
    failed = stats.get("failed_requests", 0)
    success_rate = stats.get("success_rate", 0)
    
    message = "📈 <b>Статистика за последние 24ч:</b>\n\n"
    message += f"📊 Всего запросов: <b>{total:,}</b>\n"
    message += f"✅ Успешных: <b>{success:,}</b>\n"
    message += f"❌ Неудачных: <b>{failed:,}</b>\n"
    message += f"📈 Success rate: <b>{success_rate:.1f}%</b>\n"
    
    return message


def format_alerts(alerts: List[Dict[str, Any]]) -> str:
    """Форматировать алерты для вывода"""
    if not alerts:
        return "✅ <b>Активных алертов нет!</b>\n\nВсе системы работают нормально 🎉"
    
    message = f"🚨 <b>Активных алертов: {len(alerts)}</b>\n\n"
    
    for alert in alerts:
        severity = alert.get("severity", "unknown")
        icon = "🔴" if severity == "critical" else "⚠️"
        
        message += f"{icon} <b>{alert['name']}</b>\n"
        message += f"   Service: {alert.get('service', 'unknown')}\n"
        message += f"   Severity: {severity}\n"
        if alert.get('description'):
            message += f"   {alert['description']}\n"
        message += "\n"
    
    return message


def format_health(health: Dict[str, Any]) -> str:
    """Форматировать здоровье системы для вывода"""
    if not health:
        return "⚠️ Не удалось получить данные о здоровье системы"
    
    cpu = health.get("cpu_usage", 0)
    memory = health.get("memory_mb", 0)
    disk = health.get("disk_usage", 0)
    req_rate = health.get("request_rate", 0)
    
    # Определяем статус по CPU
    cpu_status = "🟢" if cpu < 70 else "🟡" if cpu < 90 else "🔴"
    disk_status = "🟢" if disk < 70 else "🟡" if disk < 90 else "🔴"
    
    message = "💚 <b>Здоровье системы:</b>\n\n"
    message += f"{cpu_status} <b>CPU:</b> {cpu:.1f}%\n"
    message += f"💾 <b>Memory:</b> {memory:.0f} MB\n"
    message += f"{disk_status} <b>Disk:</b> {disk:.1f}%\n"
    message += f"🔄 <b>Request rate:</b> {req_rate:.2f} req/s\n"
    
    return message
