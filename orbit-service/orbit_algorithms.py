"""
orbit_algorithms.py - Дополнительные алгоритмы определения орбиты
Включает методы Batch Least-Squares и Laplace для более точного определения
"""

import math
from org.orekit.time import TimeScalesFactory
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint
from org.orekit.utils import IERSConventions, Constants, PVCoordinates
from org.orekit.orbits import KeplerianOrbit, CartesianOrbit, PositionAngleType
from org.orekit.propagation.conversion import NumericalPropagatorBuilder, DormandPrince853IntegratorBuilder
from org.orekit.estimation.measurements import AngularRaDec, ObservableSatellite, GroundStation
from org.orekit.estimation.leastsquares import BatchLSEstimator
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel
from org.hipparchus.optim.nonlinear.vector.leastsquares import GaussNewtonOptimizer
from org.hipparchus.linear import QRDecomposer
from org.hipparchus.geometry.euclidean.threed import Vector3D


def determine_orbit_batch_ls(observations, observer_position, parse_iso_time_fn, ra_dec_to_direction_fn):
    """
    Batch Least-Squares метод для определения орбиты.
    Использует полноценный Orekit BatchLSEstimator для высокой точности.
    
    Args:
        observations: список объектов Observation (минимум 3, лучше 5+)
        observer_position: GeodeticPoint
        parse_iso_time_fn: функция для парсинга времени
        ra_dec_to_direction_fn: функция для конвертации RA/Dec
    
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
    
    # Создаем ground station
    topo_frame = TopocentricFrame(earth, observer_position, "observer")
    station = GroundStation(topo_frame)
    satellite = ObservableSatellite(0)
    
    # Создаем начальное приближение орбиты
    first_obs = observations[0]
    middle_obs = observations[len(observations)//2]
    last_obs = observations[-1]
    
    date_initial = parse_iso_time_fn(middle_obs.obs_time)
    
    # Получаем направления наблюдений
    dir_first = ra_dec_to_direction_fn(first_obs.ra_deg, first_obs.dec_deg)
    dir_middle = ra_dec_to_direction_fn(middle_obs.ra_deg, middle_obs.dec_deg)
    dir_last = ra_dec_to_direction_fn(last_obs.ra_deg, last_obs.dec_deg)
    
    # Позиция наблюдателя для среднего момента
    transform = topo_frame.getTransformTo(inertial_frame, date_initial)
    obs_pos = transform.transformPosition(Vector3D.ZERO)
    
    # Оцениваем расстояние: используем типичную LEO орбиту
    estimated_range = 7.0e6  # 7000 км
    
    # Позиция спутника
    sat_pos = dir_middle.scalarMultiply(estimated_range).add(obs_pos)
    
    # Оцениваем скорость по изменению направления
    date_first = parse_iso_time_fn(first_obs.obs_time)
    date_last = parse_iso_time_fn(last_obs.obs_time)
    dt = date_last.durationFrom(date_first)
    
    transform_first = topo_frame.getTransformTo(inertial_frame, date_first)
    obs_pos_first = transform_first.transformPosition(Vector3D.ZERO)
    sat_pos_first = dir_first.scalarMultiply(estimated_range).add(obs_pos_first)
    
    transform_last = topo_frame.getTransformTo(inertial_frame, date_last)
    obs_pos_last = transform_last.transformPosition(Vector3D.ZERO)
    sat_pos_last = dir_last.scalarMultiply(estimated_range).add(obs_pos_last)
    
    sat_vel = sat_pos_last.subtract(sat_pos_first).scalarMultiply(1.0 / dt)
    
    # Создаем начальную орбиту
    pv_init = PVCoordinates(sat_pos, sat_vel)
    initial_orbit = CartesianOrbit(pv_init, inertial_frame, date_initial, mu)
    
    # Создаем propagator builder
    min_step = 0.001
    max_step = 300.0
    dP = 1.0
    integrator_builder = DormandPrince853IntegratorBuilder(min_step, max_step, dP)
    
    propagator_builder = NumericalPropagatorBuilder(
        initial_orbit,
        integrator_builder,
        PositionAngleType.TRUE,
        dP
    )
    
    propagator_builder.setMass(1000.0)
    
    # Добавляем гравитацию
    gravity_provider = GravityFieldFactory.getNormalizedProvider(4, 4)
    gravity = HolmesFeatherstoneAttractionModel(earth.getBodyFrame(), gravity_provider)
    propagator_builder.addForceModel(gravity)
    
    # Создаем estimator
    optimizer = GaussNewtonOptimizer(QRDecomposer(1.0e-11), True)
    estimator = BatchLSEstimator(optimizer, propagator_builder)
    estimator.setParametersConvergenceThreshold(1.0e-2)
    estimator.setMaxIterations(50)
    estimator.setMaxEvaluations(100)
    
    # Добавляем measurements
    for obs in observations:
        date = parse_iso_time_fn(obs.obs_time)
        ra_rad = math.radians(obs.ra_deg)
        dec_rad = math.radians(obs.dec_deg)
        
        sigma_ra = math.radians(obs.rms_ra / 3600.0) if obs.rms_ra > 0 else math.radians(1.0 / 3600.0)
        sigma_dec = math.radians(obs.rms_dec / 3600.0) if obs.rms_dec > 0 else math.radians(1.0 / 3600.0)
        
        measurement = AngularRaDec(station, inertial_frame, date, 
                                   [ra_rad, dec_rad],
                                   [sigma_ra, sigma_dec],
                                   [1.0, 1.0],
                                   satellite)
        estimator.addMeasurement(measurement)
    
    # Запускаем оценку
    print(f"Запуск batch least-squares с {len(observations)} наблюдениями...")
    estimated = estimator.estimate()
    
    # Получаем оцененную орбиту
    estimated_orbit = estimated[0].getInitialState().getOrbit()
    keplerian_orbit = KeplerianOrbit(estimated_orbit)
    
    print(f"Сходимость достигнута за {estimated[0].getIterations()} итераций")
    print(f"RMS остатков: {estimated[0].getRMS():.6f}")
    
    return keplerian_orbit


def determine_orbit_laplace(observations, observer_position, parse_iso_time_fn, ra_dec_to_direction_fn):
    """
    Метод Лапласа для определения орбиты (быстрый, приближенный).
    
    Args:
        observations: список объектов Observation (минимум 3)
        observer_position: GeodeticPoint
        parse_iso_time_fn: функция для парсинга времени
        ra_dec_to_direction_fn: функция для конвертации RA/Dec
    
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
    
    obs = observations[:3]
    dates = [parse_iso_time_fn(o.obs_time) for o in obs]
    directions = [ra_dec_to_direction_fn(o.ra_deg, o.dec_deg) for o in obs]
    
    topo_frame = TopocentricFrame(earth, observer_position, "observer")
    observer_positions = []
    
    for date in dates:
        transform = topo_frame.getTransformTo(inertial_frame, date)
        obs_pv = transform.transformPVCoordinates(PVCoordinates.ZERO)
        observer_positions.append(obs_pv.getPosition())
    
    tau1 = dates[0].durationFrom(dates[1])
    tau3 = dates[2].durationFrom(dates[1])
    tau = dates[2].durationFrom(dates[0])
    
    estimated_range = 7000000.0  # 7000 км
    
    r2 = directions[1].scalarMultiply(estimated_range).add(observer_positions[1])
    r1 = directions[0].scalarMultiply(estimated_range).add(observer_positions[0])
    r3 = directions[2].scalarMultiply(estimated_range).add(observer_positions[2])
    
    v2 = r3.subtract(r1).scalarMultiply(1.0 / tau)
    
    pv = PVCoordinates(r2, v2)
    mu = Constants.EGM96_EARTH_MU
    
    orbit = KeplerianOrbit(pv, inertial_frame, dates[1], mu)
    
    return orbit
