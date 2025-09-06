/**
 * @file pyhelios_wrapper_photosynthesis.h
 * @brief PhotosynthesisModel functions for PyHelios C wrapper
 * 
 * This header provides photosynthesis modeling capabilities including
 * empirical and Farquhar-von Caemmerer-Berry models, species library
 * integration, and comprehensive parameter management.
 */

#ifndef PYHELIOS_WRAPPER_PHOTOSYNTHESIS_H
#define PYHELIOS_WRAPPER_PHOTOSYNTHESIS_H

#include "pyhelios_wrapper_common.h"

// Forward declarations for PhotosynthesisModel interface
class PhotosynthesisModel;
namespace helios {
    class Context;
}

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// PhotosynthesisModel Functions
//=============================================================================

/**
 * @brief Create a new PhotosynthesisModel
 * @param context Pointer to the Helios context
 * @return Pointer to the created PhotosynthesisModel, or nullptr on error
 */
PYHELIOS_API PhotosynthesisModel* createPhotosynthesisModel(helios::Context* context);

/**
 * @brief Destroy a PhotosynthesisModel
 * @param photosynthesis_model Pointer to the PhotosynthesisModel to destroy
 */
PYHELIOS_API void destroyPhotosynthesisModel(PhotosynthesisModel* photosynthesis_model);

//=============================================================================
// Model Type Configuration
//=============================================================================

/**
 * @brief Set photosynthesis model to use empirical model
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 */
PYHELIOS_API void setPhotosynthesisModelTypeEmpirical(PhotosynthesisModel* photosynthesis_model);

/**
 * @brief Set photosynthesis model to use Farquhar-von Caemmerer-Berry model
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 */
PYHELIOS_API void setPhotosynthesisModelTypeFarquhar(PhotosynthesisModel* photosynthesis_model);

//=============================================================================
// Model Execution
//=============================================================================

/**
 * @brief Run photosynthesis model for all primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 */
PYHELIOS_API void runPhotosynthesisModel(PhotosynthesisModel* photosynthesis_model);

/**
 * @brief Run photosynthesis model for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param uuids Array of primitive UUIDs
 * @param uuid_count Number of UUIDs in the array
 */
PYHELIOS_API void runPhotosynthesisModelForUUIDs(PhotosynthesisModel* photosynthesis_model, const unsigned int* uuids, unsigned int uuid_count);

//=============================================================================
// Species Library Integration
//=============================================================================

/**
 * @brief Set Farquhar model coefficients from species library for all primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param species Name of the species (case insensitive, supports aliases)
 */
PYHELIOS_API void setFarquharCoefficientsFromLibrary(PhotosynthesisModel* photosynthesis_model, const char* species);

/**
 * @brief Set Farquhar model coefficients from species library for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param species Name of the species (case insensitive, supports aliases)
 * @param uuids Array of primitive UUIDs
 * @param uuid_count Number of UUIDs in the array
 */
PYHELIOS_API void setFarquharCoefficientsFromLibraryForUUIDs(PhotosynthesisModel* photosynthesis_model, const char* species, const unsigned int* uuids, unsigned int uuid_count);

/**
 * @brief Get Farquhar model coefficients from species library
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param species Name of the species (case insensitive, supports aliases)
 * @param coefficients Output array for coefficients [Vcmax, Jmax, alpha, Rd, O, TPU_flag, ...temp_params]
 * @param coeff_size Size of coefficients array (must be at least 20)
 */
PYHELIOS_API void getFarquharCoefficientsFromLibrary(PhotosynthesisModel* photosynthesis_model, const char* species, float* coefficients, unsigned int coeff_size);

//=============================================================================
// Model Parameter Configuration
//=============================================================================

/**
 * @brief Set empirical model coefficients for all primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param coefficients Array of empirical coefficients [Tref, Ci_ref, Asat, theta, Tmin, Topt, q, R, ER, kC]
 * @param coeff_count Number of coefficients (must be 10)
 */
PYHELIOS_API void setEmpiricalModelCoefficients(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count);

/**
 * @brief Set empirical model coefficients for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param coefficients Array of empirical coefficients [Tref, Ci_ref, Asat, theta, Tmin, Topt, q, R, ER, kC]
 * @param coeff_count Number of coefficients (must be 10)
 * @param uuids Array of primitive UUIDs
 * @param uuid_count Number of UUIDs in the array
 */
PYHELIOS_API void setEmpiricalModelCoefficientsForUUIDs(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count, const unsigned int* uuids, unsigned int uuid_count);

/**
 * @brief Set Farquhar model coefficients for all primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param coefficients Array of Farquhar coefficients [Vcmax, Jmax, alpha, Rd, O, TPU_flag, ...temp_params]
 * @param coeff_count Number of coefficients (must be at least 20)
 */
PYHELIOS_API void setFarquharModelCoefficients(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count);

/**
 * @brief Set Farquhar model coefficients for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param coefficients Array of Farquhar coefficients [Vcmax, Jmax, alpha, Rd, O, TPU_flag, ...temp_params]
 * @param coeff_count Number of coefficients (must be at least 20)
 * @param uuids Array of primitive UUIDs
 * @param uuid_count Number of UUIDs in the array
 */
PYHELIOS_API void setFarquharModelCoefficientsForUUIDs(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count, const unsigned int* uuids, unsigned int uuid_count);

//=============================================================================
// Individual Farquhar Parameter Setters with Temperature Response
//=============================================================================

/**
 * @brief Set Vcmax parameter with temperature response for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param vcmax_at_25c Value at 25°C
 * @param dha Rate of increase parameter (optional, -1 for default)
 * @param topt Optimum temperature in °C (optional, -1 for default)
 * @param dhd Rate of decrease parameter (optional, -1 for default)
 * @param uuids Array of primitive UUIDs (nullptr for all primitives)
 * @param uuid_count Number of UUIDs in the array (0 for all primitives)
 */
PYHELIOS_API void setFarquharVcmax(PhotosynthesisModel* photosynthesis_model, float vcmax_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count);

/**
 * @brief Set Jmax parameter with temperature response for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param jmax_at_25c Value at 25°C
 * @param dha Rate of increase parameter (optional, -1 for default)
 * @param topt Optimum temperature in °C (optional, -1 for default)
 * @param dhd Rate of decrease parameter (optional, -1 for default)
 * @param uuids Array of primitive UUIDs (nullptr for all primitives)
 * @param uuid_count Number of UUIDs in the array (0 for all primitives)
 */
PYHELIOS_API void setFarquharJmax(PhotosynthesisModel* photosynthesis_model, float jmax_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count);

/**
 * @brief Set dark respiration (Rd) parameter with temperature response for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param rd_at_25c Value at 25°C
 * @param dha Rate of increase parameter (optional, -1 for default)
 * @param topt Optimum temperature in °C (optional, -1 for default)
 * @param dhd Rate of decrease parameter (optional, -1 for default)
 * @param uuids Array of primitive UUIDs (nullptr for all primitives)
 * @param uuid_count Number of UUIDs in the array (0 for all primitives)
 */
PYHELIOS_API void setFarquharRd(PhotosynthesisModel* photosynthesis_model, float rd_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count);

/**
 * @brief Set quantum efficiency (alpha) parameter with temperature response for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param alpha_at_25c Value at 25°C
 * @param dha Rate of increase parameter (optional, -1 for default)
 * @param topt Optimum temperature in °C (optional, -1 for default)
 * @param dhd Rate of decrease parameter (optional, -1 for default)
 * @param uuids Array of primitive UUIDs (nullptr for all primitives)
 * @param uuid_count Number of UUIDs in the array (0 for all primitives)
 */
PYHELIOS_API void setFarquharQuantumEfficiency(PhotosynthesisModel* photosynthesis_model, float alpha_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count);

/**
 * @brief Set light response curvature (theta) parameter with temperature response for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param theta_at_25c Value at 25°C
 * @param dha Rate of increase parameter (optional, -1 for default)
 * @param topt Optimum temperature in °C (optional, -1 for default)
 * @param dhd Rate of decrease parameter (optional, -1 for default)
 * @param uuids Array of primitive UUIDs (nullptr for all primitives)
 * @param uuid_count Number of UUIDs in the array (0 for all primitives)
 */
PYHELIOS_API void setFarquharLightResponseCurvature(PhotosynthesisModel* photosynthesis_model, float theta_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count);

//=============================================================================
// Parameter Getters
//=============================================================================

/**
 * @brief Get empirical model coefficients for a specific primitive
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param uuid Primitive UUID
 * @param coefficients Output array for coefficients [Tref, Ci_ref, Asat, theta, Tmin, Topt, q, R, ER, kC]
 * @param coeff_size Size of coefficients array (must be at least 10)
 */
PYHELIOS_API void getEmpiricalModelCoefficients(PhotosynthesisModel* photosynthesis_model, unsigned int uuid, float* coefficients, unsigned int coeff_size);

/**
 * @brief Get Farquhar model coefficients for a specific primitive
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param uuid Primitive UUID
 * @param coefficients Output array for coefficients [Vcmax, Jmax, alpha, Rd, O, TPU_flag, ...temp_params]
 * @param coeff_size Size of coefficients array (must be at least 20)
 */
PYHELIOS_API void getFarquharModelCoefficients(PhotosynthesisModel* photosynthesis_model, unsigned int uuid, float* coefficients, unsigned int coeff_size);

//=============================================================================
// Model Configuration and Utilities
//=============================================================================

/**
 * @brief Enable PhotosynthesisModel status messages
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 */
PYHELIOS_API void enablePhotosynthesisMessages(PhotosynthesisModel* photosynthesis_model);

/**
 * @brief Disable PhotosynthesisModel status messages
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 */
PYHELIOS_API void disablePhotosynthesisMessages(PhotosynthesisModel* photosynthesis_model);

/**
 * @brief Add optional output primitive data
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param label Name of the primitive data to add (e.g., "Ci", "limitation_state", "Gamma_CO2")
 */
PYHELIOS_API void optionalOutputPhotosynthesisPrimitiveData(PhotosynthesisModel* photosynthesis_model, const char* label);

/**
 * @brief Print default value report for all primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 */
PYHELIOS_API void printPhotosynthesisDefaultValueReport(PhotosynthesisModel* photosynthesis_model);

/**
 * @brief Print default value report for specific primitives
 * @param photosynthesis_model Pointer to the PhotosynthesisModel
 * @param uuids Array of primitive UUIDs
 * @param uuid_count Number of UUIDs in the array
 */
PYHELIOS_API void printPhotosynthesisDefaultValueReportForUUIDs(PhotosynthesisModel* photosynthesis_model, const unsigned int* uuids, unsigned int uuid_count);

#ifdef __cplusplus
}
#endif

#endif // PYHELIOS_WRAPPER_PHOTOSYNTHESIS_H