// PyHelios C Interface - Common Functions
// Provides shared error handling and utilities for all PyHelios wrapper modules

#include "../include/pyhelios_wrapper_common.h"
#include <string>
#include <exception>
#include <cstdio>

// Global error state for thread-safe error handling - matches PyHelios error codes
static thread_local std::string last_error_message;
static thread_local int last_error_code = PYHELIOS_SUCCESS;

// Helper function to set error state with PyHelios error codes
void setError(int error_code, const std::string& message) {
    last_error_code = error_code;
    last_error_message = message;
}

extern "C" {

    //=============================================================================
    // Error Handling Functions
    //=============================================================================
    
    PYHELIOS_API int getLastErrorCode() {
        return last_error_code;
    }

    PYHELIOS_API const char* getLastErrorMessage() {
        return last_error_message.c_str();
    }
    
    PYHELIOS_API void clearError() {
        last_error_code = PYHELIOS_SUCCESS;
        last_error_message.clear();
    }

} //extern "C"