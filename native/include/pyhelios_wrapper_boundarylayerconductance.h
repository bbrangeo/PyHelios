// PyHelios C Interface - BoundaryLayerConductance Header
// Provides boundary layer conductance modeling for heat and mass transfer

#ifndef PYHELIOS_WRAPPER_BOUNDARYLAYERCONDUCTANCE_H
#define PYHELIOS_WRAPPER_BOUNDARYLAYERCONDUCTANCE_H

#ifdef BOUNDARYLAYERCONDUCTANCE_PLUGIN_AVAILABLE

#include "pyhelios_wrapper_common.h"
#include "Context.h"
#include "BoundaryLayerConductanceModel.h"

#ifdef __cplusplus
extern "C" {
#endif

// Core model management
PYHELIOS_API BLConductanceModel* createBoundaryLayerConductanceModel(helios::Context* context);
PYHELIOS_API void destroyBoundaryLayerConductanceModel(BLConductanceModel* model);

// Message control
PYHELIOS_API void enableBoundaryLayerMessages(BLConductanceModel* model);
PYHELIOS_API void disableBoundaryLayerMessages(BLConductanceModel* model);

// Model configuration
PYHELIOS_API void setBoundaryLayerModel(BLConductanceModel* model, const char* model_name);
PYHELIOS_API void setBoundaryLayerModelForUUID(BLConductanceModel* model, unsigned int uuid, const char* model_name);
PYHELIOS_API void setBoundaryLayerModelForUUIDs(BLConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count, const char* model_name);

// Core execution methods
PYHELIOS_API void runBoundaryLayerModel(BLConductanceModel* model);
PYHELIOS_API void runBoundaryLayerModelForUUIDs(BLConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count);

#ifdef __cplusplus
}
#endif

#endif // BOUNDARYLAYERCONDUCTANCE_PLUGIN_AVAILABLE

#endif // PYHELIOS_WRAPPER_BOUNDARYLAYERCONDUCTANCE_H
