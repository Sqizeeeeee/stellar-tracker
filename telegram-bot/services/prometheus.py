import aiohttp
from typing import Dict, Any, List, Optional
from config import settings


class PrometheusService:
    """Сервис для работы с Prometheus API"""
    
    def __init__(self):
        self.base_url = settings.prometheus_url
        self.api_url = f"{self.base_url}/api/v1"
    
    async def _query(self, query: str) -> Optional[Dict[str, Any]]:
        """Выполнить PromQL запрос"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.api_url}/query",
                    params={"query": query}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {})
                    return None
            except Exception as e:
                print(f"Error querying Prometheus: {e}")
                return None
    
    async def get_service_status(self) -> Dict[str, bool]:
        """Получить статус всех сервисов (UP/DOWN)"""
        query = "up"
        data = await self._query(query)
        
        if not data or "result" not in data:
            return {}
        
        services = {}
        for metric in data["result"]:
            job = metric["metric"].get("job", "unknown")
            value = int(metric["value"][1])
            services[job] = value == 1
        
        return services
    
    async def get_stats_24h(self) -> Dict[str, Any]:
        """Получить статистику за последние 24 часа"""
        stats = {}
        
        # Total requests
        query = "sum(increase(process_requests_total[24h]))"
        data = await self._query(query)
        if data and data.get("result"):
            stats["total_requests"] = int(float(data["result"][0]["value"][1]))
        else:
            stats["total_requests"] = 0
        
        # Success requests
        query = "sum(increase(process_requests_success[24h]))"
        data = await self._query(query)
        if data and data.get("result"):
            stats["success_requests"] = int(float(data["result"][0]["value"][1]))
        else:
            stats["success_requests"] = 0
        
        # Failed requests
        query = "sum(increase(process_requests_failed[24h]))"
        data = await self._query(query)
        if data and data.get("result"):
            stats["failed_requests"] = int(float(data["result"][0]["value"][1]))
        else:
            stats["failed_requests"] = 0
        
        # Calculate success rate
        if stats["total_requests"] > 0:
            stats["success_rate"] = (stats["success_requests"] / stats["total_requests"]) * 100
        else:
            stats["success_rate"] = 0
        
        return stats
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Получить список активных алертов"""
        query = 'ALERTS{alertstate="firing"}'
        data = await self._query(query)
        
        if not data or "result" not in data:
            return []
        
        alerts = []
        for alert in data["result"]:
            metric = alert["metric"]
            alerts.append({
                "name": metric.get("alertname", "Unknown"),
                "severity": metric.get("severity", "unknown"),
                "service": metric.get("service", metric.get("job", "unknown")),
                "description": metric.get("description", "No description")
            })
        
        return alerts
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Получить детальную информацию о здоровье системы"""
        health = {}
        
        # CPU usage
        query = "avg(rate(process_cpu_seconds_total[5m]) * 100)"
        data = await self._query(query)
        if data and data.get("result"):
            health["cpu_usage"] = round(float(data["result"][0]["value"][1]), 2)
        else:
            health["cpu_usage"] = 0
        
        # Memory usage (в MB)
        query = "sum(process_resident_memory_bytes) / 1024 / 1024"
        data = await self._query(query)
        if data and data.get("result"):
            health["memory_mb"] = round(float(data["result"][0]["value"][1]), 2)
        else:
            health["memory_mb"] = 0
        
        # Disk usage (в процентах)
        query = '(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100'
        data = await self._query(query)
        if data and data.get("result"):
            health["disk_usage"] = round(float(data["result"][0]["value"][1]), 2)
        else:
            health["disk_usage"] = 0
        
        # Request rate (requests per second)
        query = "sum(rate(process_requests_total[1m]))"
        data = await self._query(query)
        if data and data.get("result"):
            health["request_rate"] = round(float(data["result"][0]["value"][1]), 2)
        else:
            health["request_rate"] = 0
        
        return health


# Singleton instance
prometheus = PrometheusService()
