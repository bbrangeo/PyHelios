/**
 * @file pyhelios_wrapper_radiation.h
 * @brief RadiationModel functions for PyHelios C wrapper
 * 
 * This header provides radiation modeling capabilities including
 * radiation bands, light sources, and simulation execution.
 */

#ifndef PYHELIOS_WRAPPER_RADIATION_H
#define PYHELIOS_WRAPPER_RADIATION_H

#include "pyhelios_wrapper_common.h"

// Forward declarations for RadiationModel interface
class RadiationModel;
namespace helios {
    class Context;
}

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// RadiationModel Functions
//=============================================================================

/**
 * @brief Create a new RadiationModel
 * @param context Pointer to the Helios context
 * @return Pointer to the created RadiationModel, or nullptr on error
 */
PYHELIOS_API RadiationModel* createRadiationModel(helios::Context* context);

/**
 * @brief Destroy a RadiationModel
 * @param radiation_model Pointer to the RadiationModel to destroy
 */
PYHELIOS_API void destroyRadiationModel(RadiationModel* radiation_model);

/**
 * @brief Disable RadiationModel status messages
 * @param radiation_model Pointer to the RadiationModel
 */
PYHELIOS_API void disableRadiationMessages(RadiationModel* radiation_model);

/**
 * @brief Enable RadiationModel status messages
 * @param radiation_model Pointer to the RadiationModel
 */
PYHELIOS_API void enableRadiationMessages(RadiationModel* radiation_model);

/**
 * @brief Add a radiation band
 * @param radiation_model Pointer to the RadiationModel
 * @param label Name/label for the radiation band
 */
PYHELIOS_API void addRadiationBand(RadiationModel* radiation_model, const char* label);

/**
 * @brief Add a radiation band with specified wavelength range
 * @param radiation_model Pointer to the RadiationModel
 * @param label Name/label for the radiation band
 * @param wavelength_min Minimum wavelength
 * @param wavelength_max Maximum wavelength
 */
PYHELIOS_API void addRadiationBandWithWavelengths(RadiationModel* radiation_model, const char* label, float wavelength_min, float wavelength_max);

/**
 * @brief Add a collimated radiation source with default direction
 * @param radiation_model Pointer to the RadiationModel
 * @return Source ID
 */
PYHELIOS_API unsigned int addCollimatedRadiationSourceDefault(RadiationModel* radiation_model);

/**
 * @brief Add a collimated radiation source with vec3 direction
 * @param radiation_model Pointer to the RadiationModel
 * @param x X component of direction vector
 * @param y Y component of direction vector
 * @param z Z component of direction vector
 * @return Source ID
 */
PYHELIOS_API unsigned int addCollimatedRadiationSourceVec3(RadiationModel* radiation_model, float x, float y, float z);

/**
 * @brief Add a collimated radiation source with spherical coordinates
 * @param radiation_model Pointer to the RadiationModel
 * @param elevation Elevation angle in spherical coordinates
 * @param azimuth Azimuth angle in spherical coordinates
 * @param radius Radius in spherical coordinates
 * @return Source ID
 */
PYHELIOS_API unsigned int addCollimatedRadiationSourceSpherical(RadiationModel* radiation_model, float elevation, float azimuth, float radius);

/**
 * @brief Run radiation simulation for a specific band
 * @param radiation_model Pointer to the RadiationModel
 * @param label Name/label of the radiation band to run
 */
PYHELIOS_API void runBand(RadiationModel* radiation_model, const char* label);

#ifdef __cplusplus
}
#endif

#endif // PYHELIOS_WRAPPER_RADIATION_H