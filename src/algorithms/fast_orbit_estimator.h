#ifndef FAST_ORBIT_ESTIMATOR_H
#define FAST_ORBIT_ESTIMATOR_H

#include "../models/observation.h"
#include "../models/orbital_elements.h"
#include <vector>
#include <string>


class OrbitPredictor {
public:
    virtual ~OrbitPredictor() = default;
    virtual std::vector<double> predict(const OrbitalElements& orbit, 
                                      double jd, 
                                      const std::vector<double>& earth_pos) = 0;
};

class CometPredictor : public OrbitPredictor {
public:
    std::vector<double> predict(const OrbitalElements& orbit, 
                              double jd, 
                              const std::vector<double>& earth_pos) override;
};

class AsteroidPredictor : public OrbitPredictor {
public:
    std::vector<double> predict(const OrbitalElements& orbit, 
                              double jd, 
                              const std::vector<double>& earth_pos) override;
};

class PlanetPredictor : public OrbitPredictor {
public:
    std::vector<double> predict(const OrbitalElements& orbit, 
                              double jd, 
                              const std::vector<double>& earth_pos) override;
};


class FastOrbitEstimator {
public:
    static OrbitalElements estimateWithPrecision(const std::vector<Observation>& observations);
    
private:
    static std::string autoDetectObjectType(const std::vector<Observation>& observations);
    static std::vector<Observation> selectKeyObservations(const std::vector<Observation>& observations);
    static int getAttemptsCount(const std::string& obj_type);
    static OrbitalElements createInitialGuess(const std::string& obj_type,
                                            const std::vector<Observation>& observations,
                                            int attempt);
    static void applyQuickCorrections(OrbitalElements& orbit, double residual, const std::string& obj_type);
    static void adjustForObjectType(OrbitalElements& orbit, const std::string& obj_type);
    
    // ОБНОВЛЕННАЯ сигнатура с третьим параметром
    static double computeQuickResiduals(const OrbitalElements& orbit, 
                                      const std::vector<Observation>& observations,
                                      OrbitPredictor& predictor);
};

#endif // FAST_ORBIT_ESTIMATOR_H