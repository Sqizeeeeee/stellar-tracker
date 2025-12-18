import grpc
from concurrent import futures
import time
import math
from prometheus_client import start_http_server, Counter, Histogram, Gauge

# Импортируем сгенерированные файлы
from proto import astro_pb2, astro_pb2_grpc

# Prometheus метрики
RISK_ASSESSMENTS = Counter('risk_assessments_total', 'Total risk assessments performed')
RISK_ASSESSMENT_DURATION = Histogram('risk_assessment_duration_seconds', 'Time spent on risk assessment')
HIGH_RISK_DETECTIONS = Counter('high_risk_detections_total', 'Total high risk detections')
MODERATE_RISK_DETECTIONS = Counter('moderate_risk_detections_total', 'Total moderate risk detections')
LOW_RISK_DETECTIONS = Counter('low_risk_detections_total', 'Total low risk detections')
ACTIVE_REQUESTS = Gauge('collision_service_active_requests', 'Number of active risk assessment requests')


class CollisionService(astro_pb2_grpc.CollisionServiceServicer):
    """
    Сервис оценки рисков столкновения астероидов с Землей.
    Принимает орбитальные элементы и возвращает оценку риска.
    """
    
    def AssessRisk(self, request, context):
        """
        Оценивает риск столкновения на основе орбитальных элементов.
        
        Args:
            request: OrbitElements - орбитальные элементы объекта
            context: gRPC контекст
            
        Returns:
            RiskResponse - оценка риска столкновения
        """
        ACTIVE_REQUESTS.inc()
        RISK_ASSESSMENTS.inc()
        
        try:
            with RISK_ASSESSMENT_DURATION.time():
                # Имитация вычислений (в реальности здесь сложная астродинамика)
                time.sleep(0.2 + 0.1 * (request.e if request.e else 0))
                
                # Рассчитываем перигелий: q = a(1 - e)
                perihelion_au = request.a_au * (1.0 - request.e)
                
                # Упрощенный расчет MOID (Minimum Orbit Intersection Distance)
                # В реальности это сложная задача небесной механики
                moid_earth_au = self._calculate_moid(request)
                
                # Определяем уровень риска
                potential_impact = False
                risk_level = "low"
                
                if moid_earth_au < 0.05:  # Менее 0.05 AU (около 7.5 млн км)
                    if perihelion_au < 1.3:  # Близко к орбите Земли
                        potential_impact = True
                        risk_level = "high"
                        HIGH_RISK_DETECTIONS.inc()
                elif moid_earth_au < 0.2:  # 0.05 - 0.2 AU
                    if perihelion_au < 1.5:
                        risk_level = "moderate"
                        MODERATE_RISK_DETECTIONS.inc()
                else:
                    LOW_RISK_DETECTIONS.inc()
                
                # Создаем объект риска
                collision_risk = astro_pb2.CollisionRisk(
                    perihelion_au=perihelion_au,
                    moid_earth_au=moid_earth_au,
                    potential_impact=potential_impact,
                    risk_level=risk_level
                )
                
                response = astro_pb2.RiskResponse(
                    risk=collision_risk,
                    request_id="",  # request_id не передается в OrbitElements
                    success=True,
                    error=""
                )
                
        except Exception as e:
            response = astro_pb2.RiskResponse(
                success=False,
                error=f"Risk assessment failed: {str(e)}"
            )
        finally:
            ACTIVE_REQUESTS.dec()
        
        return response
    
    def _calculate_moid(self, orbit_elements):
        """
        Упрощенный расчет MOID (Minimum Orbit Intersection Distance).
        В реальности требуется решение сложной оптимизационной задачи.
        
        Args:
            orbit_elements: OrbitElements
            
        Returns:
            float: MOID в астрономических единицах
        """
        # Радиус орбиты Земли (примерно)
        earth_orbit_radius = 1.0  # AU
        
        # Перигелий и афелий орбиты объекта
        q = orbit_elements.a_au * (1.0 - orbit_elements.e)  # перигелий
        Q = orbit_elements.a_au * (1.0 + orbit_elements.e)  # афелий
        
        # Если орбита не пересекает орбиту Земли
        if q > earth_orbit_radius:
            # Объект всегда дальше Земли
            return q - earth_orbit_radius
        elif Q < earth_orbit_radius:
            # Объект всегда ближе к Солнцу
            return earth_orbit_radius - Q
        else:
            # Орбиты пересекаются - учитываем наклон
            # Упрощенная формула с учетом наклона орбиты
            inclination_factor = abs(math.sin(math.radians(orbit_elements.i_deg)))
            base_distance = abs(orbit_elements.a_au - earth_orbit_radius)
            
            # MOID уменьшается с увеличением наклона
            moid = base_distance * (0.1 + 0.9 * inclination_factor)
            
            return max(0.001, moid)  # Минимум 0.001 AU


def main():
    # Запускаем HTTP сервер для Prometheus метрик на порту 8003
    start_http_server(8003)
    print("✓ Prometheus metrics доступны на http://localhost:8003/metrics")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    astro_pb2_grpc.add_CollisionServiceServicer_to_server(CollisionService(), server)
    server.add_insecure_port('[::]:50053')
    print("✓ CollisionService запущен на порту 50053")
    print("✓ Метод: AssessRisk(OrbitElements) -> RiskResponse")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()