// PyHelios C Interface - SkyViewFactor Functions Header
// Provides sky view factor calculation functions

#ifndef PYHELIOS_WRAPPER_SKYVIEWFACTOR_H
#define PYHELIOS_WRAPPER_SKYVIEWFACTOR_H

#include "pyhelios_wrapper_common.h"
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Forward declarations for SkyViewFactorModel interface
class SkyViewFactorModel;
class SkyViewFactorCamera;
namespace helios {
    class Context;
}

// SkyViewFactorModel C interface functions

/**
 * Create a new SkyViewFactorModel instance
 * @param context Helios context pointer
 * @return Pointer to SkyViewFactorModel instance or NULL on error
 */
PYHELIOS_API SkyViewFactorModel* createSkyViewFactorModel(helios::Context* context);

/**
 * Destroy a SkyViewFactorModel instance
 * @param skyviewfactor_model Pointer to SkyViewFactorModel instance
 */
PYHELIOS_API void destroySkyViewFactorModel(SkyViewFactorModel* skyviewfactor_model);

// Message control
PYHELIOS_API void disableSkyViewFactorMessages(SkyViewFactorModel* skyviewfactor_model);
PYHELIOS_API void enableSkyViewFactorMessages(SkyViewFactorModel* skyviewfactor_model);

// Ray count configuration
PYHELIOS_API void setSkyViewFactorRayCount(SkyViewFactorModel* skyviewfactor_model, uint ray_count);
PYHELIOS_API uint getSkyViewFactorRayCount(SkyViewFactorModel* skyviewfactor_model);

// Ray length configuration
PYHELIOS_API void setSkyViewFactorMaxRayLength(SkyViewFactorModel* skyviewfactor_model, float max_length);
PYHELIOS_API float getSkyViewFactorMaxRayLength(SkyViewFactorModel* skyviewfactor_model);

// Single point calculation
PYHELIOS_API float calculateSkyViewFactor(SkyViewFactorModel* skyviewfactor_model, float x, float y, float z);
PYHELIOS_API float calculateSkyViewFactorCPU(SkyViewFactorModel* skyviewfactor_model, float x, float y, float z);

// Multiple points calculation
PYHELIOS_API void calculateSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, float* points, size_t num_points, float* results, int num_threads);

// Primitive centers calculation
PYHELIOS_API size_t calculateSkyViewFactorsForPrimitives(SkyViewFactorModel* skyviewfactor_model, float* results, uint* primitive_ids, size_t num_primitives, int num_threads);

// Export/Import functionality
PYHELIOS_API bool exportSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, const char* filename);
PYHELIOS_API bool loadSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, const char* filename);

// Get results
PYHELIOS_API float* getSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, size_t* size);
PYHELIOS_API float* getSamplePoints(SkyViewFactorModel* skyviewfactor_model, size_t* size);

// Statistics
PYHELIOS_API const char* getSkyViewFactorStatistics(SkyViewFactorModel* skyviewfactor_model);

// CUDA/OptiX availability
PYHELIOS_API bool isSkyViewFactorCudaAvailable(SkyViewFactorModel* skyviewfactor_model);
PYHELIOS_API bool isSkyViewFactorOptiXAvailable(SkyViewFactorModel* skyviewfactor_model);

// Force CPU control
PYHELIOS_API void setForceCPU(SkyViewFactorModel* skyviewfactor_model, bool force);
PYHELIOS_API bool getForceCPU(SkyViewFactorModel* skyviewfactor_model);

// Reset functionality
PYHELIOS_API void resetSkyViewFactorModel(SkyViewFactorModel* skyviewfactor_model);

// SkyViewFactorCamera functions

/**
 * Create a new SkyViewFactorCamera instance
 * @param context Helios context pointer
 * @return Pointer to SkyViewFactorCamera instance or NULL on error
 */
PYHELIOS_API SkyViewFactorCamera* createSkyViewFactorCamera(helios::Context* context);

/**
 * Destroy a SkyViewFactorCamera instance
 * @param camera Pointer to SkyViewFactorCamera instance
 */
PYHELIOS_API void destroySkyViewFactorCamera(SkyViewFactorCamera* camera);

// Camera configuration
PYHELIOS_API void setSkyViewFactorCameraPosition(SkyViewFactorCamera* camera, float x, float y, float z);
PYHELIOS_API void setSkyViewFactorCameraTarget(SkyViewFactorCamera* camera, float x, float y, float z);
PYHELIOS_API void setSkyViewFactorCameraUp(SkyViewFactorCamera* camera, float x, float y, float z);
PYHELIOS_API void setSkyViewFactorCameraFieldOfView(SkyViewFactorCamera* camera, float fov);
PYHELIOS_API void setSkyViewFactorCameraResolution(SkyViewFactorCamera* camera, uint width, uint height);
PYHELIOS_API void setSkyViewFactorCameraRayCount(SkyViewFactorCamera* camera, uint ray_count);
PYHELIOS_API void setSkyViewFactorCameraMaxRayLength(SkyViewFactorCamera* camera, float max_length);

// Camera rendering
PYHELIOS_API bool renderSkyViewFactorCamera(SkyViewFactorCamera* camera);

// Camera results
PYHELIOS_API float* getSkyViewFactorCameraImage(SkyViewFactorCamera* camera, size_t* size);
PYHELIOS_API float getSkyViewFactorCameraPixelValue(SkyViewFactorCamera* camera, uint x, uint y);
PYHELIOS_API bool exportSkyViewFactorCameraImage(SkyViewFactorCamera* camera, const char* filename);

// Camera statistics
PYHELIOS_API const char* getSkyViewFactorCameraStatistics(SkyViewFactorCamera* camera);

// Camera reset
PYHELIOS_API void resetSkyViewFactorCamera(SkyViewFactorCamera* camera);

#ifdef __cplusplus
}
#endif

#endif // PYHELIOS_WRAPPER_SKYVIEWFACTOR_H
