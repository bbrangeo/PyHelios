/**
 * @file pyhelios_wrapper_common.h
 * @brief Common definitions and error handling for PyHelios C wrapper
 * 
 * This header provides common definitions, platform macros, error codes,
 * and error handling functions shared across all PyHelios wrapper modules.
 */

#ifndef PYHELIOS_WRAPPER_COMMON_H
#define PYHELIOS_WRAPPER_COMMON_H

// Windows DLL export/import declarations
#ifdef _WIN32
    #ifdef BUILDING_PYHELIOS_DLL
        #define PYHELIOS_API __declspec(dllexport)
    #else
        #define PYHELIOS_API __declspec(dllimport)
    #endif
#else
    #define PYHELIOS_API
#endif

#include <stddef.h>  // For size_t

#ifdef __cplusplus
#include <string>    // For std::string in setError function
#endif

// Error code enumeration for robust error handling
typedef enum {
    PYHELIOS_SUCCESS = 0,                         // No error
    PYHELIOS_ERROR_INVALID_PARAMETER = 1,         // Invalid parameter passed
    PYHELIOS_ERROR_UUID_NOT_FOUND = 2,            // UUID not found in context
    PYHELIOS_ERROR_FILE_IO = 3,                   // File I/O error
    PYHELIOS_ERROR_MEMORY_ALLOCATION = 4,         // Memory allocation failure
    PYHELIOS_ERROR_GPU_INITIALIZATION = 5,       // GPU initialization failed
    PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE = 6,     // Plugin not available
    PYHELIOS_ERROR_RUNTIME = 7,                  // Runtime error (general)
    PYHELIOS_ERROR_UNKNOWN = 99                  // Unknown error
} PyHeliosErrorCode;

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// Error Handling Functions
//=============================================================================

/**
 * @brief Get the last error code
 * @return Error code (0 = success, 1-99 = specific error types)
 */
PYHELIOS_API int getLastErrorCode();

/**
 * @brief Get the last error message
 * @return Pointer to error message string (null-terminated)
 */
PYHELIOS_API const char* getLastErrorMessage();

/**
 * @brief Clear the current error state
 */
PYHELIOS_API void clearError();

//=============================================================================
// Internal Helper Functions (for use by other wrapper modules)
//=============================================================================

#ifdef __cplusplus
/**
 * @brief Internal helper function to set error state
 * @param error_code Error code from PyHeliosErrorCode enum
 * @param message Error message string
 */
void setError(int error_code, const std::string& message);
}
#endif

#endif // PYHELIOS_WRAPPER_COMMON_H