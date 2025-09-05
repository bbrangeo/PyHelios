// PyHelios C Interface - StomatalConductance Header
// Provides stomatal conductance modeling and gas exchange functions

#ifndef PYHELIOS_WRAPPER_STOMATALCONDUCTANCE_H
#define PYHELIOS_WRAPPER_STOMATALCONDUCTANCE_H

#ifdef STOMATALCONDUCTANCE_PLUGIN_AVAILABLE

#include "Context.h"
#include "StomatalConductanceModel.h"

#ifdef __cplusplus
extern "C" {
#endif

// Core model management
StomatalConductanceModel* createStomatalConductanceModel(helios::Context* context);
void destroyStomatalConductanceModel(StomatalConductanceModel* model);

// Message control
void enableStomatalConductanceMessages(StomatalConductanceModel* model);
void disableStomatalConductanceMessages(StomatalConductanceModel* model);

// Core execution methods
void runStomatalConductanceModel(StomatalConductanceModel* model);
void runStomatalConductanceModelDynamic(StomatalConductanceModel* model, float dt);
void runStomatalConductanceModelForUUIDs(StomatalConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count);
void runStomatalConductanceModelForUUIDsDynamic(StomatalConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count, float dt);

// BWB Model Coefficient Functions
void setStomatalConductanceBWBCoefficients(StomatalConductanceModel* model, float gs0, float a1);
void setStomatalConductanceBWBCoefficientsForUUIDs(StomatalConductanceModel* model, float gs0, float a1, const unsigned int* uuids, unsigned int uuid_count);

// BBL Model Coefficient Functions  
void setStomatalConductanceBBLCoefficients(StomatalConductanceModel* model, float gs0, float a1, float D0);
void setStomatalConductanceBBLCoefficientsForUUIDs(StomatalConductanceModel* model, float gs0, float a1, float D0, const unsigned int* uuids, unsigned int uuid_count);

// MOPT Model Coefficient Functions
void setStomatalConductanceMOPTCoefficients(StomatalConductanceModel* model, float gs0, float g1);
void setStomatalConductanceMOPTCoefficientsForUUIDs(StomatalConductanceModel* model, float gs0, float g1, const unsigned int* uuids, unsigned int uuid_count);

// BMF Model Coefficient Functions
void setStomatalConductanceBMFCoefficients(StomatalConductanceModel* model, float Em, float i0, float k, float b);
void setStomatalConductanceBMFCoefficientsForUUIDs(StomatalConductanceModel* model, float Em, float i0, float k, float b, const unsigned int* uuids, unsigned int uuid_count);

// BB Model Coefficient Functions
void setStomatalConductanceBBCoefficients(StomatalConductanceModel* model, float pi_0, float pi_m, float theta, float sigma, float chi);
void setStomatalConductanceBBCoefficientsForUUIDs(StomatalConductanceModel* model, float pi_0, float pi_m, float theta, float sigma, float chi, const unsigned int* uuids, unsigned int uuid_count);

// Species Library Functions
void setStomatalConductanceBMFCoefficientsFromLibrary(StomatalConductanceModel* model, const char* species);
void setStomatalConductanceBMFCoefficientsFromLibraryForUUIDs(StomatalConductanceModel* model, const char* species, const unsigned int* uuids, unsigned int uuid_count);

// Dynamic Time Constants
void setStomatalConductanceDynamicTimeConstants(StomatalConductanceModel* model, float tau_open, float tau_close);
void setStomatalConductanceDynamicTimeConstantsForUUIDs(StomatalConductanceModel* model, float tau_open, float tau_close, const unsigned int* uuids, unsigned int uuid_count);

// Utility Functions
void addStomatalConductanceOptionalOutput(StomatalConductanceModel* model, const char* label);
void printStomatalConductanceDefaultValueReport(StomatalConductanceModel* model);
void printStomatalConductanceDefaultValueReportForUUIDs(StomatalConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count);

#ifdef __cplusplus
}
#endif

#endif // STOMATALCONDUCTANCE_PLUGIN_AVAILABLE

#endif // PYHELIOS_WRAPPER_STOMATALCONDUCTANCE_H