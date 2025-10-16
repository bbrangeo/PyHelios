// PyHelios C Interface - SkyViewFactor Functions  
// Provides sky view factor calculation functions

#include "../include/pyhelios_wrapper_common.h"
#include "../include/pyhelios_wrapper_context.h"
#include "Context.h"
#include <string>
#include <exception>

#ifdef SKYVIEWFACTOR_PLUGIN_AVAILABLE
// Include complete class definitions
// Note: We don't include the wrapper header here to avoid forward declaration conflicts

#include "SkyViewFactorModel.h"
#include "SkyViewFactorCamera.h"

// Bring classes into global namespace for C interface
using helios::SkyViewFactorModel;
using helios::SkyViewFactorCamera;

extern "C" {
    // SkyViewFactorModel C interface functions
    
    PYHELIOS_API SkyViewFactorModel* createSkyViewFactorModel(helios::Context* context) {
        try {
            clearError();
            if (!context) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Context pointer is null");
                return nullptr;
            }
            return new SkyViewFactorModel(context);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::constructor): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::constructor): Unknown error creating SkyViewFactorModel.");
            return nullptr;
        }
    }
    
    PYHELIOS_API void destroySkyViewFactorModel(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (skyviewfactor_model != nullptr) {
                delete skyviewfactor_model;
            }
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::destructor): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::destructor): Unknown error destroying SkyViewFactorModel.");
        }
    }
    
    // Message control
    PYHELIOS_API void disableSkyViewFactorMessages(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return;
            }
            skyviewfactor_model->setMessageFlag(false);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::disableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::disableMessages): Unknown error disabling messages.");
        }
    }
    
    PYHELIOS_API void enableSkyViewFactorMessages(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return;
            }
            skyviewfactor_model->setMessageFlag(true);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::enableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::enableMessages): Unknown error enabling messages.");
        }
    }
    
    // Ray count configuration
    PYHELIOS_API void setSkyViewFactorRayCount(SkyViewFactorModel* skyviewfactor_model, uint ray_count) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return;
            }
            skyviewfactor_model->setRayCount(ray_count);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::setRayCount): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::setRayCount): Unknown error setting ray count.");
        }
    }
    
    PYHELIOS_API uint getSkyViewFactorRayCount(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return 0;
            }
            return skyviewfactor_model->getRayCount();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::getRayCount): ") + e.what());
            return 0;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::getRayCount): Unknown error getting ray count.");
            return 0;
        }
    }
    
    // Ray length configuration
    PYHELIOS_API void setSkyViewFactorMaxRayLength(SkyViewFactorModel* skyviewfactor_model, float max_length) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return;
            }
            skyviewfactor_model->setMaxRayLength(max_length);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::setMaxRayLength): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::setMaxRayLength): Unknown error setting max ray length.");
        }
    }
    
    PYHELIOS_API float getSkyViewFactorMaxRayLength(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return 0.0f;
            }
            return skyviewfactor_model->getMaxRayLength();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::getMaxRayLength): ") + e.what());
            return 0.0f;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::getMaxRayLength): Unknown error getting max ray length.");
            return 0.0f;
        }
    }
    
    // Single point calculation
    PYHELIOS_API float calculateSkyViewFactor(SkyViewFactorModel* skyviewfactor_model, float x, float y, float z) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return 0.0f;
            }
            return skyviewfactor_model->calculateSkyViewFactor(helios::vec3(x, y, z));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::calculateSkyViewFactor): ") + e.what());
            return 0.0f;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::calculateSkyViewFactor): Unknown error calculating sky view factor.");
            return 0.0f;
        }
    }
    
    PYHELIOS_API float calculateSkyViewFactorCPU(SkyViewFactorModel* skyviewfactor_model, float x, float y, float z) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return 0.0f;
            }
            return skyviewfactor_model->calculateSkyViewFactorCPU(helios::vec3(x, y, z));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::calculateSkyViewFactorCPU): ") + e.what());
            return 0.0f;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::calculateSkyViewFactorCPU): Unknown error calculating sky view factor (CPU).");
            return 0.0f;
        }
    }
    
    // Multiple points calculation
    PYHELIOS_API void calculateSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, float* points, size_t num_points, float* results) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return;
            }
            if (!points || !results) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Points or results pointer is null");
                return;
            }
            
            std::vector<helios::vec3> point_vec;
            for (size_t i = 0; i < num_points; ++i) {
                point_vec.push_back(helios::vec3(points[3*i], points[3*i+1], points[3*i+2]));
            }
            
            std::vector<float> svf_results = skyviewfactor_model->calculateSkyViewFactors(point_vec);
            
            for (size_t i = 0; i < svf_results.size() && i < num_points; ++i) {
                results[i] = svf_results[i];
            }
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::calculateSkyViewFactors): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::calculateSkyViewFactors): Unknown error calculating sky view factors.");
        }
    }
    
    // Primitive centers calculation
    PYHELIOS_API size_t calculateSkyViewFactorsForPrimitives(SkyViewFactorModel* skyviewfactor_model, float* results) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return 0;
            }
            
            std::vector<float> svf_results = skyviewfactor_model->calculateSkyViewFactorsForPrimitives();
            
            if (results && svf_results.size() > 0) {
                for (size_t i = 0; i < svf_results.size(); ++i) {
                    results[i] = svf_results[i];
                }
            }
            
            return svf_results.size();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::calculateSkyViewFactorsForPrimitives): ") + e.what());
            return 0;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::calculateSkyViewFactorsForPrimitives): Unknown error calculating sky view factors for primitives.");
            return 0;
        }
    }
    
    // Export/Import functionality
    PYHELIOS_API bool exportSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, const char* filename) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return false;
            }
            if (!filename) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Filename is null");
                return false;
            }
            return skyviewfactor_model->exportSkyViewFactors(std::string(filename));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::exportSkyViewFactors): ") + e.what());
            return false;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::exportSkyViewFactors): Unknown error exporting sky view factors.");
            return false;
        }
    }
    
    PYHELIOS_API bool loadSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, const char* filename) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return false;
            }
            if (!filename) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Filename is null");
                return false;
            }
            return skyviewfactor_model->loadSkyViewFactors(std::string(filename));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::loadSkyViewFactors): ") + e.what());
            return false;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::loadSkyViewFactors): Unknown error loading sky view factors.");
            return false;
        }
    }
    
    // Get results
    PYHELIOS_API float* getSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, size_t* size) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return nullptr;
            }
            
            std::vector<float> svf_results = skyviewfactor_model->getSkyViewFactors();
            
            if (size) {
                *size = svf_results.size();
            }
            
            if (svf_results.empty()) {
                return nullptr;
            }
            
            // Allocate memory for results (caller must free this)
            float* results = new float[svf_results.size()];
            for (size_t i = 0; i < svf_results.size(); ++i) {
                results[i] = svf_results[i];
            }
            
            return results;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::getSkyViewFactors): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::getSkyViewFactors): Unknown error getting sky view factors.");
            return nullptr;
        }
    }
    
    // Statistics
    PYHELIOS_API const char* getSkyViewFactorStatistics(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return nullptr;
            }
            
            std::string stats = skyviewfactor_model->getStatistics();
            if (stats.empty()) {
                return nullptr;
            }
            
            // Allocate memory for string (caller must free this)
            char* result = new char[stats.length() + 1];
            strcpy(result, stats.c_str());
            return result;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::getStatistics): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::getStatistics): Unknown error getting statistics.");
            return nullptr;
        }
    }
    
    // CUDA/OptiX availability
    PYHELIOS_API bool isSkyViewFactorCudaAvailable(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return false;
            }
            return skyviewfactor_model->isCudaAvailable();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::isCudaAvailable): ") + e.what());
            return false;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::isCudaAvailable): Unknown error checking CUDA availability.");
            return false;
        }
    }
    
    PYHELIOS_API bool isSkyViewFactorOptiXAvailable(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return false;
            }
            return skyviewfactor_model->isOptiXAvailable();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::isOptiXAvailable): ") + e.what());
            return false;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::isOptiXAvailable): Unknown error checking OptiX availability.");
            return false;
        }
    }
    
    // Reset functionality
    PYHELIOS_API void resetSkyViewFactorModel(SkyViewFactorModel* skyviewfactor_model) {
        try {
            clearError();
            if (!skyviewfactor_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorModel pointer is null");
                return;
            }
            skyviewfactor_model->reset();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorModel::reset): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorModel::reset): Unknown error resetting sky view factor model.");
        }
    }
    
    // SkyViewFactorCamera functions
    PYHELIOS_API SkyViewFactorCamera* createSkyViewFactorCamera(helios::Context* context) {
        try {
            clearError();
            if (!context) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Context pointer is null");
                return nullptr;
            }
            return new SkyViewFactorCamera(context);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::constructor): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::constructor): Unknown error creating SkyViewFactorCamera.");
            return nullptr;
        }
    }
    
    PYHELIOS_API void destroySkyViewFactorCamera(SkyViewFactorCamera* camera) {
        try {
            clearError();
            if (camera != nullptr) {
                delete camera;
            }
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::destructor): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::destructor): Unknown error destroying SkyViewFactorCamera.");
        }
    }
    
    // Camera configuration
    PYHELIOS_API void setSkyViewFactorCameraPosition(SkyViewFactorCamera* camera, float x, float y, float z) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->setPosition(helios::vec3(x, y, z));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::setPosition): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::setPosition): Unknown error setting camera position.");
        }
    }
    
    PYHELIOS_API void setSkyViewFactorCameraTarget(SkyViewFactorCamera* camera, float x, float y, float z) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->setTarget(helios::vec3(x, y, z));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::setTarget): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::setTarget): Unknown error setting camera target.");
        }
    }
    
    PYHELIOS_API void setSkyViewFactorCameraUp(SkyViewFactorCamera* camera, float x, float y, float z) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->setUp(helios::vec3(x, y, z));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::setUp): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::setUp): Unknown error setting camera up vector.");
        }
    }
    
    PYHELIOS_API void setSkyViewFactorCameraFieldOfView(SkyViewFactorCamera* camera, float fov) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->setFieldOfView(fov);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::setFieldOfView): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::setFieldOfView): Unknown error setting camera field of view.");
        }
    }
    
    PYHELIOS_API void setSkyViewFactorCameraResolution(SkyViewFactorCamera* camera, uint width, uint height) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->setResolution(width, height);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::setResolution): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::setResolution): Unknown error setting camera resolution.");
        }
    }
    
    PYHELIOS_API void setSkyViewFactorCameraRayCount(SkyViewFactorCamera* camera, uint ray_count) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->setRayCount(ray_count);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::setRayCount): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::setRayCount): Unknown error setting camera ray count.");
        }
    }
    
    PYHELIOS_API void setSkyViewFactorCameraMaxRayLength(SkyViewFactorCamera* camera, float max_length) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->setMaxRayLength(max_length);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::setMaxRayLength): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::setMaxRayLength): Unknown error setting camera max ray length.");
        }
    }
    
    // Camera rendering
    PYHELIOS_API bool renderSkyViewFactorCamera(SkyViewFactorCamera* camera) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return false;
            }
            return camera->render();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::render): ") + e.what());
            return false;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::render): Unknown error rendering camera.");
            return false;
        }
    }
    
    // Camera results
    PYHELIOS_API float* getSkyViewFactorCameraImage(SkyViewFactorCamera* camera, size_t* size) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return nullptr;
            }
            
            // TODO: Implement getImage() method in SkyViewFactorCamera
            // For now, return nullptr as this functionality is not yet implemented
            if (size) {
                *size = 0;
            }
            setError(PYHELIOS_ERROR_RUNTIME, "ERROR (SkyViewFactorCamera::getImage): Not yet implemented");
            return nullptr;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::getImage): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::getImage): Unknown error getting camera image.");
            return nullptr;
        }
    }
    
    PYHELIOS_API float getSkyViewFactorCameraPixelValue(SkyViewFactorCamera* camera, uint x, uint y) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return 0.0f;
            }
            // TODO: Implement getPixelValue() method in SkyViewFactorCamera
            // For now, return 0.0 as this functionality is not yet implemented
            setError(PYHELIOS_ERROR_RUNTIME, "ERROR (SkyViewFactorCamera::getPixelValue): Not yet implemented");
            return 0.0f;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::getPixelValue): ") + e.what());
            return 0.0f;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::getPixelValue): Unknown error getting pixel value.");
            return 0.0f;
        }
    }
    
    PYHELIOS_API bool exportSkyViewFactorCameraImage(SkyViewFactorCamera* camera, const char* filename) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return false;
            }
            if (!filename) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Filename is null");
                return false;
            }
            return camera->exportImage(std::string(filename));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::exportImage): ") + e.what());
            return false;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::exportImage): Unknown error exporting camera image.");
            return false;
        }
    }
    
    // Camera statistics
    PYHELIOS_API const char* getSkyViewFactorCameraStatistics(SkyViewFactorCamera* camera) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return nullptr;
            }
            
            std::string stats = camera->getStatistics();
            if (stats.empty()) {
                return nullptr;
            }
            
            // Allocate memory for string (caller must free this)
            char* result = new char[stats.length() + 1];
            strcpy(result, stats.c_str());
            return result;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::getStatistics): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::getStatistics): Unknown error getting camera statistics.");
            return nullptr;
        }
    }
    
    // Camera reset
    PYHELIOS_API void resetSkyViewFactorCamera(SkyViewFactorCamera* camera) {
        try {
            clearError();
            if (!camera) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "SkyViewFactorCamera pointer is null");
                return;
            }
            camera->reset();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (SkyViewFactorCamera::reset): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (SkyViewFactorCamera::reset): Unknown error resetting camera.");
        }
    }
}

#else
// Stub implementations when plugin is not available
extern "C" {
    PYHELIOS_API SkyViewFactorModel* createSkyViewFactorModel(helios::Context* context) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return nullptr;
    }
    
    PYHELIOS_API void destroySkyViewFactorModel(SkyViewFactorModel* skyviewfactor_model) {
        // No-op when plugin not available
    }
    
    // All other functions return appropriate error values when plugin not available
    PYHELIOS_API void disableSkyViewFactorMessages(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void enableSkyViewFactorMessages(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void setSkyViewFactorRayCount(SkyViewFactorModel* skyviewfactor_model, uint ray_count) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API uint getSkyViewFactorRayCount(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return 0;
    }
    
    PYHELIOS_API void setSkyViewFactorMaxRayLength(SkyViewFactorModel* skyviewfactor_model, float max_length) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API float getSkyViewFactorMaxRayLength(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return 0.0f;
    }
    
    PYHELIOS_API float calculateSkyViewFactor(SkyViewFactorModel* skyviewfactor_model, float x, float y, float z) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return 0.0f;
    }
    
    PYHELIOS_API float calculateSkyViewFactorCPU(SkyViewFactorModel* skyviewfactor_model, float x, float y, float z) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return 0.0f;
    }
    
    PYHELIOS_API void calculateSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, float* points, size_t num_points, float* results) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API size_t calculateSkyViewFactorsForPrimitives(SkyViewFactorModel* skyviewfactor_model, float* results) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return 0;
    }
    
    PYHELIOS_API bool exportSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, const char* filename) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return false;
    }
    
    PYHELIOS_API bool loadSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, const char* filename) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return false;
    }
    
    PYHELIOS_API float* getSkyViewFactors(SkyViewFactorModel* skyviewfactor_model, size_t* size) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return nullptr;
    }
    
    PYHELIOS_API const char* getSkyViewFactorStatistics(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return nullptr;
    }
    
    PYHELIOS_API bool isSkyViewFactorCudaAvailable(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return false;
    }
    
    PYHELIOS_API bool isSkyViewFactorOptiXAvailable(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return false;
    }
    
    PYHELIOS_API void resetSkyViewFactorModel(SkyViewFactorModel* skyviewfactor_model) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    // Camera stub functions
    PYHELIOS_API SkyViewFactorCamera* createSkyViewFactorCamera(helios::Context* context) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return nullptr;
    }
    
    PYHELIOS_API void destroySkyViewFactorCamera(SkyViewFactorCamera* camera) {
        // No-op when plugin not available
    }
    
    PYHELIOS_API void setSkyViewFactorCameraPosition(SkyViewFactorCamera* camera, float x, float y, float z) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void setSkyViewFactorCameraTarget(SkyViewFactorCamera* camera, float x, float y, float z) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void setSkyViewFactorCameraUp(SkyViewFactorCamera* camera, float x, float y, float z) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void setSkyViewFactorCameraFieldOfView(SkyViewFactorCamera* camera, float fov) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void setSkyViewFactorCameraResolution(SkyViewFactorCamera* camera, uint width, uint height) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void setSkyViewFactorCameraRayCount(SkyViewFactorCamera* camera, uint ray_count) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API void setSkyViewFactorCameraMaxRayLength(SkyViewFactorCamera* camera, float max_length) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
    
    PYHELIOS_API bool renderSkyViewFactorCamera(SkyViewFactorCamera* camera) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return false;
    }
    
    PYHELIOS_API float* getSkyViewFactorCameraImage(SkyViewFactorCamera* camera, size_t* size) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return nullptr;
    }
    
    PYHELIOS_API float getSkyViewFactorCameraPixelValue(SkyViewFactorCamera* camera, uint x, uint y) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return 0.0f;
    }
    
    PYHELIOS_API bool exportSkyViewFactorCameraImage(SkyViewFactorCamera* camera, const char* filename) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return false;
    }
    
    PYHELIOS_API const char* getSkyViewFactorCameraStatistics(SkyViewFactorCamera* camera) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
        return nullptr;
    }
    
    PYHELIOS_API void resetSkyViewFactorCamera(SkyViewFactorCamera* camera) {
        setError(PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE, "SkyViewFactor plugin is not available");
    }
}

#endif
