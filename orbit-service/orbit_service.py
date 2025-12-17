"""
Orbit Service - микросервис для определения орбиты по наблюдениям
Использует Orekit для вычисления орбитальных элементов методом Gooding IOD
"""

import os
import math
import glob
from concurrent import futures
from datetime import datetime

import grpc
import jpype
import jpype.imports
from prometheus_client import start_http_server, Counter, Histogram, Gauge

# ============================================================
# 1) ИНИЦИАЛИЗАЦИЯ JVM И OREKIT
# ============================================================

def init_orekit():
    """Инициализирует JVM и настраивает Orekit data"""
    # Находим JAR файл Orekit
    orekit_jars = glob.glob('/usr/local/lib/python*/site-packages/**/*.jar', recursive=True)
    if not orekit_jars:
        raise FileNotFoundError("Orekit JAR file not found")

    classpath = ':'.join(orekit_jars)

    # Запускаем JVM
    if not jpype.isJVMStarted():
        jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={classpath}")

    # Импортируем классы Java ПОСЛЕ запуска JVM
    from org.orekit.data import DataContext, DirectoryCrawler
    from java.io import File

    # Указываем путь к данным
    orekit_data_dir = os.environ.get('OREKIT_DATA', '/app/orekit-data')

    # Проверяем существование директории
    if not os.path.exists(orekit_data_dir):
        raise FileNotFoundError(f"Orekit data directory not found: {orekit_data_dir}")

    # Настраиваем источник данных
    data_context = DataContext.getDefault()
    data_manager = data_context.getDataProvidersManager()
    data_manager.clearProviders()
    crawler = DirectoryCrawler(File(orekit_data_dir))
    data_manager.addProvider(crawler)
    
    print(f"✓ Orekit initialized with data from {orekit_data_dir}")

# Инициализируем Orekit при загрузке модуля
init_orekit()

# Импортируем необходимые классы Orekit
from org.orekit.time import TimeScalesFactory, AbsoluteDate
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint
from org.orekit.utils import IERSConventions, Constants, PVCoordinates
from org.orekit.orbits import KeplerianOrbit, CartesianOrbit
from org.orekit.estimation.measurements import AngularRaDec, ObservableSatellite, GroundStation
from org.orekit.estimation.iod import IodGooding
from org.hipparchus.geometry.euclidean.threed import Vector3D

# Импортируем proto
from proto import astro_pb2
from proto import astro_pb2_grpc

# ============================================================
# 2) УТИЛИТЫ
# ============================================================

def parse_iso_time(iso_string):
    """Конвертирует ISO 8601 строку в AbsoluteDate"""
    utc = TimeScalesFactory.getUTC()
    # Парсим ISO формат: 2024-12-15T12:30:45.123Z
    iso_string = str(iso_string).replace('Z', '+00:00')
    dt = datetime.fromisoformat(iso_string)
    return AbsoluteDate(dt.year, dt.month, dt.day, 
                       dt.hour, dt.minute, float(dt.second + dt.microsecond/1e6), 
                       utc)


def ra_dec_to_direction(ra_deg, dec_deg):
    """Конвертирует RA/Dec в единичный вектор направления"""
    ra_rad = math.radians(ra_deg)
    dec_rad = math.radians(dec_deg)
    
    x = math.cos(dec_rad) * math.cos(ra_rad)
    y = math.cos(dec_rad) * math.sin(ra_rad)
    z = math.sin(dec_rad)
    
    return Vector3D(x, y, z)


# ============================================================
# 3) ОПРЕДЕЛЕНИЕ ОРБИТЫ
# ============================================================

def determine_orbit_simplified(observations, station_lat_deg=0.0, station_lon_deg=0.0, station_alt_m=0.0):
    """
    Упрощённый метод определения орбиты для LEO спутников.
    Использует приближение постоянной высоты и скорости.
    
    Args:
        observations: список объектов astro_pb2.Observation (минимум 3)
        station_lat_deg: широта станции
        station_lon_deg: долгота станции
        station_alt_m: высота станции
    
    Returns:
        KeplerianOrbit
    """
    if len(observations) < 3:
        raise ValueError("Необходимо минимум 3 наблюдения")
    
    utc = TimeScalesFactory.getUTC()
    earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                            Constants.WGS84_EARTH_FLATTENING,
                            FramesFactory.getITRF(IERSConventions.IERS_2010, True))
    
    inertial_frame = FramesFactory.getEME2000()
    mu = Constants.EGM96_EARTH_MU
    
    # Используем первые 3 наблюдения
    obs = observations[:3]
    dates = [parse_iso_time(o.obs_time) for o in obs]
    directions = [ra_dec_to_direction(o.ra_deg, o.dec_deg) for o in obs]
    
    # Создаём topocentric frame
    observer_position = GeodeticPoint(math.radians(station_lat_deg),
                                     math.radians(station_lon_deg),
                                     station_alt_m)
    topo_frame = TopocentricFrame(earth, observer_position, "observer")
    
    # Позиции наблюдателя в инерциальной системе
    observer_positions = []
    for date in dates:
        transform = topo_frame.getTransformTo(inertial_frame, date)
        obs_pv = transform.transformPVCoordinates(PVCoordinates.ZERO)
        observer_positions.append(obs_pv.getPosition())
    
    # Предполагаем типичную высоту LEO: 400 км
    estimated_altitude = 400000.0  # метры
    estimated_range = Constants.WGS84_EARTH_EQUATORIAL_RADIUS + estimated_altitude
    
    # Вычисляем позиции спутника
    r1 = directions[0].scalarMultiply(estimated_range).add(observer_positions[0])
    r2 = directions[1].scalarMultiply(estimated_range).add(observer_positions[1])
    r3 = directions[2].scalarMultiply(estimated_range).add(observer_positions[2])
    
    # Временные интервалы
    tau_total = dates[2].durationFrom(dates[0])
    
    # Оценка скорости (численная производная)
    v2 = r3.subtract(r1).scalarMultiply(1.0 / tau_total)
    
    # Создаём орбиту
    pv = PVCoordinates(r2, v2)
    orbit = KeplerianOrbit(pv, inertial_frame, dates[1], mu)
    
    print(f"✓ Упрощённый метод IOD завершён")
    
    return orbit


def determine_orbit_gooding(observations, station_lat_deg=0.0, station_lon_deg=0.0, station_alt_m=0.0):
    """
    Использует метод Gooding для определения орбиты по трем угловым наблюдениям.
    
    Args:
        observations: список объектов astro_pb2.Observation (минимум 3)
        station_lat_deg: широта станции в градусах
        station_lon_deg: долгота станции в градусах
        station_alt_m: высота станции в метрах
    
    Returns:
        KeplerianOrbit
    """
    if len(observations) < 3:
        raise ValueError("Необходимо минимум 3 наблюдения")
    
    utc = TimeScalesFactory.getUTC()
    earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                            Constants.WGS84_EARTH_FLATTENING,
                            FramesFactory.getITRF(IERSConventions.IERS_2010, True))
    
    inertial_frame = FramesFactory.getEME2000()
    mu = Constants.EGM96_EARTH_MU
    
    # Используем первые 3 наблюдения
    obs = observations[:3]
    
    # Создаем позицию наблюдателя
    observer_position = GeodeticPoint(math.radians(station_lat_deg),
                                     math.radians(station_lon_deg),
                                     station_alt_m)
    
    # Создаем topocentric frame для наблюдателя
    topo_frame = TopocentricFrame(earth, observer_position, "observer")
    station = GroundStation(topo_frame)
    satellite = ObservableSatellite(0)
    
    # Получаем даты и создаем AngularRaDec measurements
    measurements = []
    
    for o in obs:
        date = parse_iso_time(o.obs_time)
        ra_rad = math.radians(o.ra_deg)
        dec_rad = math.radians(o.dec_deg)
        
        # Sigma в радианах (переводим из угловых секунд, если указаны)
        sigma_ra = math.radians(o.rms_ra / 3600.0) if o.rms_ra > 0 else math.radians(1.0 / 3600.0)
        sigma_dec = math.radians(o.rms_dec / 3600.0) if o.rms_dec > 0 else math.radians(1.0 / 3600.0)
        
        measurement = AngularRaDec(station, inertial_frame, date,
                                   [ra_rad, dec_rad],
                                   [sigma_ra, sigma_dec],
                                   [1.0, 1.0],
                                   satellite)
        measurements.append(measurement)
    
    # Используем Gooding IOD
    iod = IodGooding(mu)
    
    # Estimate orbit using AngularRaDec measurements
    estimated_orbit = iod.estimate(
        inertial_frame,
        measurements[0],
        measurements[1],
        measurements[2]
    )
    
    # Проверяем, что орбита реалистична
    if estimated_orbit.getE() >= 1.0:
        raise ValueError(f"Гиперболическая орбита (e={estimated_orbit.getE():.3f})")
    
    # Конвертируем в Keplerian
    keplerian_orbit = KeplerianOrbit(estimated_orbit)
    
    print(f"✓ Gooding IOD успешно завершен")
    
    return keplerian_orbit


# ============================================================
# 4) gRPC СЕРВИС
# ============================================================

class OrbitServiceServicer(astro_pb2_grpc.OrbitServiceServicer):
    """Реализация OrbitService"""

    def Calculate(self, request, context):
        """
        Вычисляет орбитальные элементы по наблюдениям
        
        Args:
            request: ObservationsRequest с наблюдениями
            context: gRPC context
            
        Returns:
            OrbitResponse с орбитальными элементами
        """
        ACTIVE_ORBIT_REQUESTS.inc()
        ORBIT_CALCULATIONS.inc()
        
        try:
            with ORBIT_DURATION.time():
                print(f"📡 Получен запрос {request.request_id} для объекта '{request.object_name}'")
                print(f"   Наблюдений: {len(request.observations)}")
                
                if len(request.observations) < 3:
                    raise ValueError("Необходимо минимум 3 наблюдения для определения орбиты")
            
            # Извлекаем координаты станции
            first_obs = request.observations[0]
            station_lat = 48.0  # По умолчанию Европа
            station_lon = 11.0
            station_alt = 500.0
            
            if first_obs.station and ',' in first_obs.station:
                try:
                    parts = first_obs.station.split(',')
                    if len(parts) >= 3:
                        station_lat = float(parts[0])
                        station_lon = float(parts[1])
                        station_alt = float(parts[2])
                except:
                    pass
            
            # Пробуем сначала Gooding, потом fallback на упрощённый метод
            orbit = None
            method_used = "unknown"
            
            try:
                print("   Пробую метод Gooding IOD...")
                orbit = determine_orbit_gooding(
                    request.observations,
                    station_lat,
                    station_lon,
                    station_alt
                )
                method_used = "Gooding IOD"
                
                # Проверяем реалистичность
                altitude_km = (orbit.getA() / 1000.0) - 6371
                if altitude_km < 100 or altitude_km > 100000:
                    print(f"   ⚠️ Gooding дал нереалистичную орбиту (высота {altitude_km:.0f} км), пробую упрощённый метод...")
                    raise ValueError("Unrealistic orbit from Gooding")
                    
            except Exception as e:
                print(f"   ⚠️ Gooding не сработал: {str(e)}")
                print("   Пробую упрощённый метод...")
                orbit = determine_orbit_simplified(
                    request.observations,
                    station_lat,
                    station_lon,
                    station_alt
                )
                method_used = "Simplified"
            
            # Конвертируем в OrbitElements
            a_au = orbit.getA() / Constants.IAU_2012_ASTRONOMICAL_UNIT
            e = orbit.getE()
            i_deg = math.degrees(orbit.getI())
            omega_deg = math.degrees(orbit.getPerigeeArgument())
            big_mega_deg = math.degrees(orbit.getRightAscensionOfAscendingNode())
            m_deg = math.degrees(orbit.getMeanAnomaly())
            epoch = str(orbit.getDate().toString())
            
            altitude_km = (orbit.getA() / 1000.0) - 6371
            print(f"✓ Орбита вычислена ({method_used}): a={orbit.getA()/1000:.1f} km, e={e:.6f}, i={i_deg:.2f}°, высота={altitude_km:.0f} км")
            
            return astro_pb2.OrbitResponse(
                request_id=request.request_id,
                success=True,
                orbit=astro_pb2.OrbitElements(
                    a_au=a_au,
                    e=e,
                    i_deg=i_deg,
                    omega_deg=omega_deg,
                    big_mega_deg=big_mega_deg,
                    m_deg=m_deg,
                    epoch=epoch
                )
            )
            
        except Exception as ex:
            print(f"❌ Ошибка при вычислении орбиты: {str(ex)}")
            import traceback
            traceback.print_exc()
            
            return astro_pb2.OrbitResponse(
                request_id=request.request_id,
                success=False,
                error=f"OrbitService error: {str(ex)}"
            )
        except Exception as ex:
            ORBIT_ERRORS.inc()
            print(f"❌ Ошибка в OrbitService: {str(ex)}")
            import traceback
            traceback.print_exc()
            
            return astro_pb2.OrbitResponse(
                request_id=request.request_id,
                success=False,
                error=f"OrbitService error: {str(ex)}"
            )
        finally:
            ACTIVE_ORBIT_REQUESTS.dec()


# ============================================================
# 5) ЗАПУСК СЕРВИСА
# ============================================================

# Prometheus метрики
ORBIT_CALCULATIONS = Counter('orbit_calculations_total', 'Total orbit calculations performed')
ORBIT_DURATION = Histogram('orbit_calculation_duration_seconds', 'Time spent on orbit calculation')
ORBIT_ERRORS = Counter('orbit_calculation_errors_total', 'Total orbit calculation errors')
ACTIVE_ORBIT_REQUESTS = Gauge('orbit_service_active_requests', 'Number of active orbit requests')

def serve():
    """Запускает gRPC сервер"""
    # Запускаем HTTP сервер для Prometheus метрик на порту 8002
    start_http_server(8002)
    print("📊 Prometheus metrics доступны на http://localhost:8002/metrics")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    astro_pb2_grpc.add_OrbitServiceServicer_to_server(OrbitServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    print("🚀 OrbitService started at 0.0.0.0:50052")
    print("   Методы: Gooding IOD (primary) + Simplified (fallback)")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()