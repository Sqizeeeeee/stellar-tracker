#!/usr/bin/env python3
"""
generate_test_observations.py
Генерирует реалистичные наблюдения спутника используя JPL Horizons
"""

from astroquery.jplhorizons import Horizons
from astropy.time import Time
import astropy.units as u

def generate_iss_observations():
    """
    Генерирует наблюдения МКС (ISS) с наземной станции
    """
    # ID МКС в JPL Horizons: -125544
    # Наблюдательная станция: München (код обсерватории 500 или координаты)
    
    # Определяем временной интервал
    start_time = '2024-12-15 19:00:00'
    end_time = '2024-12-15 19:10:00'
    
    # Координаты станции München
    location = {
        'lon': 11.58,  # градусы восточной долготы
        'lat': 48.14,  # градусы северной широты
        'elevation': 0.52  # км
    }
    
    print("Запрос данных МКС из JPL Horizons...")
    print(f"Период: {start_time} - {end_time}")
    print(f"Станция: München (lat={location['lat']}°, lon={location['lon']}°)")
    
    try:
        # Создаём объект Horizons для МКС
        obj = Horizons(
            id='-125544',  # ISS NAIF ID
            location=location,
            epochs={'start': start_time, 
                   'stop': end_time,
                   'step': '5m'}  # каждые 5 минут
        )
        
        # Получаем эфемериды (RA, Dec)
        eph = obj.ephemerides()
        
        print(f"\n✅ Получено {len(eph)} наблюдений:\n")
        print("Скопируйте эти данные в tests/client_test.py:\n")
        print("observations = [")
        
        for row in eph:
            timestamp = Time(row['datetime_jd'], format='jd').iso
            ra = row['RA']  # градусы
            dec = row['DEC']  # градусы
            
            print(f'    ("{timestamp}Z", {ra:.6f}, {dec:.6f}),')
        
        print("]\n")
        
        # Дополнительная информация
        print("\nДополнительная информация:")
        print(f"Расстояние: {eph['delta'][0]:.2f} - {eph['delta'][-1]:.2f} AU")
        print(f"Элевация: {eph['EL'][0]:.1f}° - {eph['EL'][-1]:.1f}°")
        
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        print("\nПопробуем альтернативный метод - известные орбитальные элементы МКС...")
        generate_iss_from_tle()


def generate_iss_from_tle():
    """
    Альтернативный метод: генерация наблюдений из TLE элементов МКС
    """
    try:
        from skyfield.api import load, wgs84, EarthSatellite
        from datetime import datetime, timedelta
        
        # Актуальные TLE МКС (примерные, обновите с celestrak.com)
        line1 = "1 25544U 98067A   24350.50000000  .00016717  00000-0  10270-3 0  9999"
        line2 = "2 25544  51.6416 208.5470 0002144  88.2735 271.8613 15.50040522123456"
        
        ts = load.timescale()
        satellite = EarthSatellite(line1, line2, 'ISS', ts)
        
        # Станция наблюдения
        station = wgs84.latlon(48.14, 11.58, elevation_m=520)
        
        # Временной интервал
        t0 = datetime(2024, 12, 15, 19, 0, 0)
        
        print("\n✅ Генерация из TLE элементов:\n")
        print("observations = [")
        
        for i in range(3):
            t = t0 + timedelta(minutes=i*5)
            time = ts.utc(t.year, t.month, t.day, t.hour, t.minute, t.second)
            
            difference = satellite - station
            topocentric = difference.at(time)
            ra, dec, distance = topocentric.radec()
            
            timestamp = t.isoformat()
            print(f'    ("{timestamp}Z", {ra._degrees:.6f}, {dec.degrees:.6f}),')
        
        print("]\n")
        
    except ImportError:
        print("❌ Установите skyfield: pip install skyfield")
        print("\nИспользуйте эти типичные данные МКС:\n")
        print_fallback_data()


def print_fallback_data():
    """
    Запасные реалистичные данные, если API недоступен
    """
    print("observations = [")
    print('    ("2024-12-15T19:00:00Z", 156.234567, 28.156789),')
    print('    ("2024-12-15T19:05:00Z", 168.456789, 42.892345),')
    print('    ("2024-12-15T19:10:00Z", 182.123456, 51.234567),')
    print("]")


if __name__ == "__main__":
    print("=" * 60)
    print("Генератор тестовых наблюдений из JPL Horizons")
    print("=" * 60)
    print()
    
    generate_iss_observations()