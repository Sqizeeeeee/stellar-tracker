#ifndef ORBIT_CALCULATOR_H
#define ORBIT_CALCULATOR_H

#include "astro.pb.h"

class OrbitCalculator {
public:
    astro::OrbitResponse CalculateOrbit(const astro::ObservationsRequest& request);
    
private:
    bool ValidateRequest(const astro::ObservationsRequest& request);
    std::string PrepareObservationsFile(const astro::ObservationsRequest& request);
    bool RunFindOrb(const std::string& observations_file, std::string& output);
    astro::OrbitElements ParseFindOrbOutput(const std::string& findorb_output);
};

#endif