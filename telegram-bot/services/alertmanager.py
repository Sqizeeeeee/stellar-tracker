from typing import Dict, Any, List
from datetime import datetime


def format_alert_notification(alert_data: Dict[str, Any]) -> str:
    """Форматировать алерт от Alertmanager для Telegram"""
    alerts = alert_data.get("alerts", [])
    
    if not alerts:
        return None
    
    # Группируем по severity
    critical = [a for a in alerts if a.get("labels", {}).get("severity") == "critical"]
    warning = [a for a in alerts if a.get("labels", {}).get("severity") == "warning"]
    
    messages = []
    
    # Critical alerts
    if critical:
        msg = "🔴 <b>CRITICAL ALERT!</b>\n\n"
        for alert in critical:
            labels = alert.get("labels", {})
            annotations = alert.get("annotations", {})
            
            msg += f"🚨 <b>{labels.get('alertname', 'Unknown')}</b>\n"
            msg += f"Service: {labels.get('service', labels.get('job', 'unknown'))}\n"
            
            if annotations.get('summary'):
                msg += f"📝 {annotations['summary']}\n"
            
            if annotations.get('description'):
                msg += f"ℹ️ {annotations['description']}\n"
            
            # Время начала
            starts_at = alert.get("startsAt")
            if starts_at:
                try:
                    dt = datetime.fromisoformat(starts_at.replace('Z', '+00:00'))
                    msg += f"⏰ Started: {dt.strftime('%H:%M:%S')}\n"
                except:
                    pass
            
            msg += "\n"
        
        messages.append(msg)
    
    # Warning alerts (группируем)
    if warning:
        msg = "⚠️ <b>Warning Alerts</b>\n\n"
        msg += f"Count: {len(warning)}\n\n"
        
        for alert in warning[:3]:  # Показываем только первые 3
            labels = alert.get("labels", {})
            msg += f"• {labels.get('alertname', 'Unknown')} ({labels.get('service', 'unknown')})\n"
        
        if len(warning) > 3:
            msg += f"\n...and {len(warning) - 3} more warnings\n"
        
        messages.append(msg)
    
    return messages


def parse_alertmanager_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Парсим webhook от Alertmanager"""
    return {
        "status": payload.get("status"),
        "alerts": payload.get("alerts", []),
        "groupLabels": payload.get("groupLabels", {}),
        "commonLabels": payload.get("commonLabels", {}),
        "externalURL": payload.get("externalURL", "")
    }
