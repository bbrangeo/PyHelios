// PyHelios C Interface - PhotosynthesisModel Functions
// Provides photosynthesis modeling capabilities including empirical and Farquhar models

#include "../include/pyhelios_wrapper_common.h"
#include "../include/pyhelios_wrapper_context.h"
#include "Context.h"
#include <string>
#include <exception>
#include <vector>

#ifdef PHOTOSYNTHESIS_PLUGIN_AVAILABLE
#include "../include/pyhelios_wrapper_photosynthesis.h"
#include "PhotosynthesisModel.h"

extern "C" {
    
    //=============================================================================
    // PhotosynthesisModel Lifecycle
    //=============================================================================
    
    PYHELIOS_API PhotosynthesisModel* createPhotosynthesisModel(helios::Context* context) {
        try {
            clearError();
            if (!context) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Context pointer is null");
                return nullptr;
            }
            
            return new PhotosynthesisModel(context);
            
        } catch (const std::runtime_error& e) {
            setError(PYHELIOS_ERROR_RUNTIME, e.what());
            return nullptr;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (createPhotosynthesisModel): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (createPhotosynthesisModel): Unknown error creating PhotosynthesisModel.");
            return nullptr;
        }
    }
    
    PYHELIOS_API void destroyPhotosynthesisModel(PhotosynthesisModel* photosynthesis_model) {
        if (photosynthesis_model) {
            delete photosynthesis_model;
        }
    }
    
    //=============================================================================
    // Model Type Configuration
    //=============================================================================
    
    PYHELIOS_API void setPhotosynthesisModelTypeEmpirical(PhotosynthesisModel* photosynthesis_model) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            photosynthesis_model->setModelType_Empirical();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setModelType_Empirical): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setModelType_Empirical): Unknown error setting empirical model type.");
        }
    }
    
    PYHELIOS_API void setPhotosynthesisModelTypeFarquhar(PhotosynthesisModel* photosynthesis_model) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            photosynthesis_model->setModelType_Farquhar();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setModelType_Farquhar): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setModelType_Farquhar): Unknown error setting Farquhar model type.");
        }
    }
    
    //=============================================================================
    // Model Execution
    //=============================================================================
    
    PYHELIOS_API void runPhotosynthesisModel(PhotosynthesisModel* photosynthesis_model) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            photosynthesis_model->run();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::run): Unknown error running photosynthesis model.");
        }
    }
    
    PYHELIOS_API void runPhotosynthesisModelForUUIDs(PhotosynthesisModel* photosynthesis_model, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!uuids) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUIDs array is null");
                return;
            }
            if (uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUID count must be greater than 0");
                return;
            }
            
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            photosynthesis_model->run(uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::run): Unknown error running photosynthesis model for UUIDs.");
        }
    }
    
    //=============================================================================
    // Species Library Integration
    //=============================================================================
    
    PYHELIOS_API void setFarquharCoefficientsFromLibrary(PhotosynthesisModel* photosynthesis_model, const char* species) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!species) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Species name is null");
                return;
            }
            
            photosynthesis_model->setFarquharCoefficientsFromLibrary(species);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setFarquharCoefficientsFromLibrary): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setFarquharCoefficientsFromLibrary): Unknown error setting coefficients from library.");
        }
    }
    
    PYHELIOS_API void setFarquharCoefficientsFromLibraryForUUIDs(PhotosynthesisModel* photosynthesis_model, const char* species, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!species) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Species name is null");
                return;
            }
            if (!uuids) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUIDs array is null");
                return;
            }
            if (uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUID count must be greater than 0");
                return;
            }
            
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            photosynthesis_model->setFarquharCoefficientsFromLibrary(species, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setFarquharCoefficientsFromLibrary): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setFarquharCoefficientsFromLibrary): Unknown error setting coefficients from library for UUIDs.");
        }
    }
    
    PYHELIOS_API void getFarquharCoefficientsFromLibrary(PhotosynthesisModel* photosynthesis_model, const char* species, float* coefficients, unsigned int coeff_size) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!species) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Species name is null");
                return;
            }
            if (!coefficients) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array is null");
                return;
            }
            if (coeff_size < 18) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array size must be at least 18");
                return;
            }
            
            // Get coefficients from library
            FarquharModelCoefficients farquhar_coeffs = photosynthesis_model->getFarquharCoefficientsFromLibrary(species);
            
            // Pack into float array: [Vcmax, Jmax, alpha, Rd, O, TPU_flag, ...temp_params]
            coefficients[0] = farquhar_coeffs.Vcmax;
            coefficients[1] = farquhar_coeffs.Jmax;
            coefficients[2] = farquhar_coeffs.alpha;
            coefficients[3] = farquhar_coeffs.Rd;
            coefficients[4] = farquhar_coeffs.O;
            coefficients[5] = static_cast<float>(farquhar_coeffs.TPU_flag);
            
            // Temperature parameters (simplified - just the main ones)
            coefficients[6] = farquhar_coeffs.c_Vcmax;
            coefficients[7] = farquhar_coeffs.dH_Vcmax;
            coefficients[8] = farquhar_coeffs.c_Jmax;
            coefficients[9] = farquhar_coeffs.dH_Jmax;
            coefficients[10] = farquhar_coeffs.c_Rd;
            coefficients[11] = farquhar_coeffs.dH_Rd;
            coefficients[12] = farquhar_coeffs.c_Kc;
            coefficients[13] = farquhar_coeffs.dH_Kc;
            coefficients[14] = farquhar_coeffs.c_Ko;
            coefficients[15] = farquhar_coeffs.dH_Ko;
            coefficients[16] = farquhar_coeffs.c_Gamma;
            coefficients[17] = farquhar_coeffs.dH_Gamma;
            
            // Fill remaining with zeros if array is larger
            for (unsigned int i = 18; i < coeff_size; ++i) {
                coefficients[i] = 0.0f;
            }
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::getFarquharCoefficientsFromLibrary): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::getFarquharCoefficientsFromLibrary): Unknown error getting coefficients from library.");
        }
    }
    
    //=============================================================================
    // Model Parameter Configuration - Empirical Model
    //=============================================================================
    
    PYHELIOS_API void setEmpiricalModelCoefficients(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!coefficients) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array is null");
                return;
            }
            if (coeff_count < 10) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Empirical model coefficients array must have at least 10 elements");
                return;
            }
            
            // Create empirical coefficients from array [Tref, Ci_ref, Asat, theta, Tmin, Topt, q, R, ER, kC]
            EmpiricalModelCoefficients empirical_coeffs;
            empirical_coeffs.Tref = coefficients[0];
            empirical_coeffs.Ci_ref = coefficients[1];
            empirical_coeffs.Asat = coefficients[2];
            empirical_coeffs.theta = coefficients[3];
            empirical_coeffs.Tmin = coefficients[4];
            empirical_coeffs.Topt = coefficients[5];
            empirical_coeffs.q = coefficients[6];
            empirical_coeffs.R = coefficients[7];
            empirical_coeffs.ER = coefficients[8];
            empirical_coeffs.kC = coefficients[9];
            
            photosynthesis_model->setModelCoefficients(empirical_coeffs);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setModelCoefficients): Unknown error setting empirical model coefficients.");
        }
    }
    
    PYHELIOS_API void setEmpiricalModelCoefficientsForUUIDs(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!coefficients) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array is null");
                return;
            }
            if (coeff_count < 10) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Empirical model coefficients array must have at least 10 elements");
                return;
            }
            if (!uuids) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUIDs array is null");
                return;
            }
            if (uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUID count must be greater than 0");
                return;
            }
            
            // Create empirical coefficients from array
            EmpiricalModelCoefficients empirical_coeffs;
            empirical_coeffs.Tref = coefficients[0];
            empirical_coeffs.Ci_ref = coefficients[1];
            empirical_coeffs.Asat = coefficients[2];
            empirical_coeffs.theta = coefficients[3];
            empirical_coeffs.Tmin = coefficients[4];
            empirical_coeffs.Topt = coefficients[5];
            empirical_coeffs.q = coefficients[6];
            empirical_coeffs.R = coefficients[7];
            empirical_coeffs.ER = coefficients[8];
            empirical_coeffs.kC = coefficients[9];
            
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            photosynthesis_model->setModelCoefficients(empirical_coeffs, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setModelCoefficients): Unknown error setting empirical model coefficients for UUIDs.");
        }
    }
    
    //=============================================================================
    // Model Parameter Configuration - Farquhar Model
    //=============================================================================
    
    PYHELIOS_API void setFarquharModelCoefficients(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!coefficients) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array is null");
                return;
            }
            if (coeff_count < 18) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Farquhar model coefficients array must have at least 18 elements");
                return;
            }
            
            // Create Farquhar coefficients from array [Vcmax, Jmax, alpha, Rd, O, TPU_flag, ...temp_params]
            FarquharModelCoefficients farquhar_coeffs;
            farquhar_coeffs.Vcmax = coefficients[0];
            farquhar_coeffs.Jmax = coefficients[1];
            farquhar_coeffs.alpha = coefficients[2];
            farquhar_coeffs.Rd = coefficients[3];
            farquhar_coeffs.O = coefficients[4];
            farquhar_coeffs.TPU_flag = static_cast<int>(coefficients[5]);
            
            // Basic temperature parameters (using simplified interface)
            if (coeff_count >= 18) {
                farquhar_coeffs.c_Vcmax = coefficients[6];
                farquhar_coeffs.dH_Vcmax = coefficients[7];
                farquhar_coeffs.c_Jmax = coefficients[8];
                farquhar_coeffs.dH_Jmax = coefficients[9];
                farquhar_coeffs.c_Rd = coefficients[10];
                farquhar_coeffs.dH_Rd = coefficients[11];
                farquhar_coeffs.c_Kc = coefficients[12];
                farquhar_coeffs.dH_Kc = coefficients[13];
                farquhar_coeffs.c_Ko = coefficients[14];
                farquhar_coeffs.dH_Ko = coefficients[15];
                farquhar_coeffs.c_Gamma = coefficients[16];
                farquhar_coeffs.dH_Gamma = coefficients[17];
            }
            
            photosynthesis_model->setModelCoefficients(farquhar_coeffs);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setModelCoefficients): Unknown error setting Farquhar model coefficients.");
        }
    }
    
    PYHELIOS_API void setFarquharModelCoefficientsForUUIDs(PhotosynthesisModel* photosynthesis_model, const float* coefficients, unsigned int coeff_count, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!coefficients) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array is null");
                return;
            }
            if (coeff_count < 18) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Farquhar model coefficients array must have at least 18 elements");
                return;
            }
            if (!uuids) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUIDs array is null");
                return;
            }
            if (uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUID count must be greater than 0");
                return;
            }
            
            // Create Farquhar coefficients from array
            FarquharModelCoefficients farquhar_coeffs;
            farquhar_coeffs.Vcmax = coefficients[0];
            farquhar_coeffs.Jmax = coefficients[1];
            farquhar_coeffs.alpha = coefficients[2];
            farquhar_coeffs.Rd = coefficients[3];
            farquhar_coeffs.O = coefficients[4];
            farquhar_coeffs.TPU_flag = static_cast<int>(coefficients[5]);
            
            // Basic temperature parameters
            if (coeff_count >= 18) {
                farquhar_coeffs.c_Vcmax = coefficients[6];
                farquhar_coeffs.dH_Vcmax = coefficients[7];
                farquhar_coeffs.c_Jmax = coefficients[8];
                farquhar_coeffs.dH_Jmax = coefficients[9];
                farquhar_coeffs.c_Rd = coefficients[10];
                farquhar_coeffs.dH_Rd = coefficients[11];
                farquhar_coeffs.c_Kc = coefficients[12];
                farquhar_coeffs.dH_Kc = coefficients[13];
                farquhar_coeffs.c_Ko = coefficients[14];
                farquhar_coeffs.dH_Ko = coefficients[15];
                farquhar_coeffs.c_Gamma = coefficients[16];
                farquhar_coeffs.dH_Gamma = coefficients[17];
            }
            
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            photosynthesis_model->setModelCoefficients(farquhar_coeffs, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setModelCoefficients): Unknown error setting Farquhar model coefficients for UUIDs.");
        }
    }
    
    //=============================================================================
    // Individual Farquhar Parameter Setters with Temperature Response
    //=============================================================================
    
    PYHELIOS_API void setFarquharVcmax(PhotosynthesisModel* photosynthesis_model, float vcmax_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            // Individual parameter setters require explicit UUIDs
            if (uuids == nullptr || uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Individual parameter setters require explicit UUIDs. Use setFarquharModelCoefficients() for all primitives.");
                return;
            }
            
            std::vector<uint> target_uuids(uuids, uuids + uuid_count);
            
            // For each UUID, get existing coefficients, modify only Vcmax, then set back
            for (uint uuid : target_uuids) {
                try {
                    // Get existing coefficients for this UUID
                    FarquharModelCoefficients existing_coeffs = photosynthesis_model->getFarquharModelCoefficients(uuid);
                    
                    // Modify only the Vcmax parameter using the appropriate overload
                    if (dha < 0) {
                        existing_coeffs.setVcmax(vcmax_at_25c);
                    } else if (topt < 0) {
                        existing_coeffs.setVcmax(vcmax_at_25c, dha);
                    } else if (dhd < 0) {
                        existing_coeffs.setVcmax(vcmax_at_25c, dha, topt);
                    } else {
                        existing_coeffs.setVcmax(vcmax_at_25c, dha, topt, dhd);
                    }
                    
                    // Set the modified coefficients back for this UUID
                    std::vector<uint> single_uuid = {uuid};
                    photosynthesis_model->setModelCoefficients(existing_coeffs, single_uuid);
                    
                } catch (const std::exception& e) {
                    // If this UUID doesn't have photosynthesis data yet, skip it silently
                    // This allows the function to work on mixed primitive sets
                    continue;
                }
            }
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setVcmax): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setVcmax): Unknown error setting Vcmax parameter.");
        }
    }
    
    PYHELIOS_API void setFarquharJmax(PhotosynthesisModel* photosynthesis_model, float jmax_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            // Individual parameter setters require explicit UUIDs
            if (uuids == nullptr || uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Individual parameter setters require explicit UUIDs. Use setFarquharModelCoefficients() for all primitives.");
                return;
            }
            
            std::vector<uint> target_uuids(uuids, uuids + uuid_count);
            
            // For each UUID, get existing coefficients, modify only Jmax, then set back
            for (uint uuid : target_uuids) {
                try {
                    // Get existing coefficients for this UUID
                    FarquharModelCoefficients existing_coeffs = photosynthesis_model->getFarquharModelCoefficients(uuid);
                    
                    // Modify only the Jmax parameter using the appropriate overload
                    if (dha < 0) {
                        existing_coeffs.setJmax(jmax_at_25c);
                    } else if (topt < 0) {
                        existing_coeffs.setJmax(jmax_at_25c, dha);
                    } else if (dhd < 0) {
                        existing_coeffs.setJmax(jmax_at_25c, dha, topt);
                    } else {
                        existing_coeffs.setJmax(jmax_at_25c, dha, topt, dhd);
                    }
                    
                    // Set the modified coefficients back for this UUID
                    std::vector<uint> single_uuid = {uuid};
                    photosynthesis_model->setModelCoefficients(existing_coeffs, single_uuid);
                    
                } catch (const std::exception& e) {
                    // If this UUID doesn't have photosynthesis data yet, skip it silently
                    continue;
                }
            }
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setJmax): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setJmax): Unknown error setting Jmax parameter.");
        }
    }
    
    PYHELIOS_API void setFarquharRd(PhotosynthesisModel* photosynthesis_model, float rd_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            // Individual parameter setters require explicit UUIDs
            if (uuids == nullptr || uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Individual parameter setters require explicit UUIDs. Use setFarquharModelCoefficients() for all primitives.");
                return;
            }
            
            std::vector<uint> target_uuids(uuids, uuids + uuid_count);
            
            // For each UUID, get existing coefficients, modify only Rd, then set back
            for (uint uuid : target_uuids) {
                try {
                    // Get existing coefficients for this UUID
                    FarquharModelCoefficients existing_coeffs = photosynthesis_model->getFarquharModelCoefficients(uuid);
                    
                    // Modify only the Rd parameter using the appropriate overload
                    if (dha < 0) {
                        existing_coeffs.setRd(rd_at_25c);
                    } else if (topt < 0) {
                        existing_coeffs.setRd(rd_at_25c, dha);
                    } else if (dhd < 0) {
                        existing_coeffs.setRd(rd_at_25c, dha, topt);
                    } else {
                        existing_coeffs.setRd(rd_at_25c, dha, topt, dhd);
                    }
                    
                    // Set the modified coefficients back for this UUID
                    std::vector<uint> single_uuid = {uuid};
                    photosynthesis_model->setModelCoefficients(existing_coeffs, single_uuid);
                    
                } catch (const std::exception& e) {
                    // If this UUID doesn't have photosynthesis data yet, skip it silently
                    continue;
                }
            }
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setRd): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setRd): Unknown error setting Rd parameter.");
        }
    }
    
    PYHELIOS_API void setFarquharQuantumEfficiency(PhotosynthesisModel* photosynthesis_model, float alpha_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            // Individual parameter setters require explicit UUIDs
            if (uuids == nullptr || uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Individual parameter setters require explicit UUIDs. Use setFarquharModelCoefficients() for all primitives.");
                return;
            }
            
            std::vector<uint> target_uuids(uuids, uuids + uuid_count);
            
            // For each UUID, get existing coefficients, modify only alpha, then set back
            for (uint uuid : target_uuids) {
                try {
                    // Get existing coefficients for this UUID
                    FarquharModelCoefficients existing_coeffs = photosynthesis_model->getFarquharModelCoefficients(uuid);
                    
                    // Modify only the quantum efficiency parameter using the appropriate overload
                    if (dha < 0) {
                        existing_coeffs.setQuantumEfficiency_alpha(alpha_at_25c);
                    } else if (topt < 0) {
                        existing_coeffs.setQuantumEfficiency_alpha(alpha_at_25c, dha);
                    } else if (dhd < 0) {
                        existing_coeffs.setQuantumEfficiency_alpha(alpha_at_25c, dha, topt);
                    } else {
                        existing_coeffs.setQuantumEfficiency_alpha(alpha_at_25c, dha, topt, dhd);
                    }
                    
                    // Set the modified coefficients back for this UUID
                    std::vector<uint> single_uuid = {uuid};
                    photosynthesis_model->setModelCoefficients(existing_coeffs, single_uuid);
                    
                } catch (const std::exception& e) {
                    // If this UUID doesn't have photosynthesis data yet, skip it silently
                    continue;
                }
            }
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setQuantumEfficiency_alpha): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setQuantumEfficiency_alpha): Unknown error setting quantum efficiency parameter.");
        }
    }
    
    PYHELIOS_API void setFarquharLightResponseCurvature(PhotosynthesisModel* photosynthesis_model, float theta_at_25c, float dha, float topt, float dhd, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            // Individual parameter setters require explicit UUIDs
            if (uuids == nullptr || uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Individual parameter setters require explicit UUIDs. Use setFarquharModelCoefficients() for all primitives.");
                return;
            }
            
            std::vector<uint> target_uuids(uuids, uuids + uuid_count);
            
            // For each UUID, get existing coefficients, modify only theta, then set back
            for (uint uuid : target_uuids) {
                try {
                    // Get existing coefficients for this UUID
                    FarquharModelCoefficients existing_coeffs = photosynthesis_model->getFarquharModelCoefficients(uuid);
                    
                    // Modify only the light response curvature parameter using the appropriate overload
                    if (dha < 0) {
                        existing_coeffs.setLightResponseCurvature_theta(theta_at_25c);
                    } else if (topt < 0) {
                        existing_coeffs.setLightResponseCurvature_theta(theta_at_25c, dha);
                    } else if (dhd < 0) {
                        existing_coeffs.setLightResponseCurvature_theta(theta_at_25c, dha, topt);
                    } else {
                        existing_coeffs.setLightResponseCurvature_theta(theta_at_25c, dha, topt, dhd);
                    }
                    
                    // Set the modified coefficients back for this UUID
                    std::vector<uint> single_uuid = {uuid};
                    photosynthesis_model->setModelCoefficients(existing_coeffs, single_uuid);
                    
                } catch (const std::exception& e) {
                    // If this UUID doesn't have photosynthesis data yet, skip it silently
                    continue;
                }
            }
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::setLightResponseCurvature_theta): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::setLightResponseCurvature_theta): Unknown error setting light response curvature parameter.");
        }
    }
    
    //=============================================================================
    // Parameter Getters
    //=============================================================================
    
    PYHELIOS_API void getEmpiricalModelCoefficients(PhotosynthesisModel* photosynthesis_model, unsigned int uuid, float* coefficients, unsigned int coeff_size) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!coefficients) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array is null");
                return;
            }
            if (coeff_size < 10) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array size must be at least 10");
                return;
            }
            
            EmpiricalModelCoefficients empirical_coeffs = photosynthesis_model->getEmpiricalModelCoefficients(uuid);
            
            // Pack into float array [Tref, Ci_ref, Asat, theta, Tmin, Topt, q, R, ER, kC]
            coefficients[0] = empirical_coeffs.Tref;
            coefficients[1] = empirical_coeffs.Ci_ref;
            coefficients[2] = empirical_coeffs.Asat;
            coefficients[3] = empirical_coeffs.theta;
            coefficients[4] = empirical_coeffs.Tmin;
            coefficients[5] = empirical_coeffs.Topt;
            coefficients[6] = empirical_coeffs.q;
            coefficients[7] = empirical_coeffs.R;
            coefficients[8] = empirical_coeffs.ER;
            coefficients[9] = empirical_coeffs.kC;
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::getEmpiricalModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::getEmpiricalModelCoefficients): Unknown error getting empirical model coefficients.");
        }
    }
    
    PYHELIOS_API void getFarquharModelCoefficients(PhotosynthesisModel* photosynthesis_model, unsigned int uuid, float* coefficients, unsigned int coeff_size) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!coefficients) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array is null");
                return;
            }
            if (coeff_size < 18) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Coefficients array size must be at least 18");
                return;
            }
            
            FarquharModelCoefficients farquhar_coeffs = photosynthesis_model->getFarquharModelCoefficients(uuid);
            
            // Pack into float array [Vcmax, Jmax, alpha, Rd, O, TPU_flag, ...temp_params]
            coefficients[0] = farquhar_coeffs.Vcmax;
            coefficients[1] = farquhar_coeffs.Jmax;
            coefficients[2] = farquhar_coeffs.alpha;
            coefficients[3] = farquhar_coeffs.Rd;
            coefficients[4] = farquhar_coeffs.O;
            coefficients[5] = static_cast<float>(farquhar_coeffs.TPU_flag);
            
            // Temperature parameters
            coefficients[6] = farquhar_coeffs.c_Vcmax;
            coefficients[7] = farquhar_coeffs.dH_Vcmax;
            coefficients[8] = farquhar_coeffs.c_Jmax;
            coefficients[9] = farquhar_coeffs.dH_Jmax;
            coefficients[10] = farquhar_coeffs.c_Rd;
            coefficients[11] = farquhar_coeffs.dH_Rd;
            coefficients[12] = farquhar_coeffs.c_Kc;
            coefficients[13] = farquhar_coeffs.dH_Kc;
            coefficients[14] = farquhar_coeffs.c_Ko;
            coefficients[15] = farquhar_coeffs.dH_Ko;
            coefficients[16] = farquhar_coeffs.c_Gamma;
            coefficients[17] = farquhar_coeffs.dH_Gamma;
            
            // Fill remaining with zeros if array is larger
            for (unsigned int i = 18; i < coeff_size; ++i) {
                coefficients[i] = 0.0f;
            }
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::getFarquharModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::getFarquharModelCoefficients): Unknown error getting Farquhar model coefficients.");
        }
    }
    
    //=============================================================================
    // Model Configuration and Utilities
    //=============================================================================
    
    PYHELIOS_API void enablePhotosynthesisMessages(PhotosynthesisModel* photosynthesis_model) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            photosynthesis_model->enableMessages();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::enableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::enableMessages): Unknown error enabling messages.");
        }
    }
    
    PYHELIOS_API void disablePhotosynthesisMessages(PhotosynthesisModel* photosynthesis_model) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            photosynthesis_model->disableMessages();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::disableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::disableMessages): Unknown error disabling messages.");
        }
    }
    
    PYHELIOS_API void optionalOutputPhotosynthesisPrimitiveData(PhotosynthesisModel* photosynthesis_model, const char* label) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            
            photosynthesis_model->optionalOutputPrimitiveData(label);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::optionalOutputPrimitiveData): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::optionalOutputPrimitiveData): Unknown error setting optional output.");
        }
    }
    
    PYHELIOS_API void printPhotosynthesisDefaultValueReport(PhotosynthesisModel* photosynthesis_model) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            
            photosynthesis_model->printDefaultValueReport();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::printDefaultValueReport): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::printDefaultValueReport): Unknown error printing default value report.");
        }
    }
    
    PYHELIOS_API void printPhotosynthesisDefaultValueReportForUUIDs(PhotosynthesisModel* photosynthesis_model, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!photosynthesis_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "PhotosynthesisModel pointer is null");
                return;
            }
            if (!uuids) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUIDs array is null");
                return;
            }
            if (uuid_count == 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUID count must be greater than 0");
                return;
            }
            
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            photosynthesis_model->printDefaultValueReport(uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (PhotosynthesisModel::printDefaultValueReport): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (PhotosynthesisModel::printDefaultValueReport): Unknown error printing default value report for UUIDs.");
        }
    }
    
} // extern "C"

#endif // PHOTOSYNTHESIS_PLUGIN_AVAILABLE