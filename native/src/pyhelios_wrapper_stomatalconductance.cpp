// PyHelios C Interface - StomatalConductance Functions
// Provides stomatal conductance modeling and gas exchange functions

#include "../include/pyhelios_wrapper_common.h"
#include "../include/pyhelios_wrapper_context.h"
#include "Context.h"
#include <string>
#include <exception>

#ifdef STOMATALCONDUCTANCE_PLUGIN_AVAILABLE
#include "../include/pyhelios_wrapper_stomatalconductance.h"
#include "StomatalConductanceModel.h"

extern "C" {
    
    StomatalConductanceModel* createStomatalConductanceModel(helios::Context* context) {
        try {
            clearError();
            if (!context) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Context pointer is null");
                return nullptr;
            }
            
            return new StomatalConductanceModel(context);
            
        } catch (const std::runtime_error& e) {
            setError(PYHELIOS_ERROR_RUNTIME, e.what());
            return nullptr;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (createStomatalConductanceModel): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (createStomatalConductanceModel): Unknown error creating StomatalConductanceModel.");
            return nullptr;
        }
    }
    
    void destroyStomatalConductanceModel(StomatalConductanceModel* model) {
        if (model) {
            delete model;
        }
    }
    
    void enableStomatalConductanceMessages(StomatalConductanceModel* model) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            model->enableMessages();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::enableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::enableMessages): Unknown error enabling messages.");
        }
    }
    
    void disableStomatalConductanceMessages(StomatalConductanceModel* model) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            model->disableMessages();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::disableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::disableMessages): Unknown error disabling messages.");
        }
    }
    
    void runStomatalConductanceModel(StomatalConductanceModel* model) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            model->run();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::run): Unknown error running stomatal conductance model.");
        }
    }
    
    void runStomatalConductanceModelDynamic(StomatalConductanceModel* model, float dt) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            if (dt <= 0.0f) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Time step must be positive");
                return;
            }
            
            model->run(dt);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::run): Unknown error running dynamic stomatal conductance model.");
        }
    }
    
    void runStomatalConductanceModelForUUIDs(StomatalConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            model->run(uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::run): Unknown error running stomatal conductance model for UUIDs.");
        }
    }
    
    void runStomatalConductanceModelForUUIDsDynamic(StomatalConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count, float dt) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            if (dt <= 0.0f) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Time step must be positive");
                return;
            }
            
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            model->run(uuid_vector, dt);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::run): Unknown error running dynamic stomatal conductance model for UUIDs.");
        }
    }

    // BWB Model Coefficient Functions
    void setStomatalConductanceBWBCoefficients(StomatalConductanceModel* model, float gs0, float a1) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            BWBcoefficients coeffs;
            coeffs.gs0 = gs0;
            coeffs.a1 = a1;
            model->setModelCoefficients(coeffs);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BWB coefficients.");
        }
    }
    
    void setStomatalConductanceBWBCoefficientsForUUIDs(StomatalConductanceModel* model, float gs0, float a1, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            
            BWBcoefficients coeffs;
            coeffs.gs0 = gs0;
            coeffs.a1 = a1;
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            model->setModelCoefficients(coeffs, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BWB coefficients for UUIDs.");
        }
    }

    // BBL Model Coefficient Functions  
    void setStomatalConductanceBBLCoefficients(StomatalConductanceModel* model, float gs0, float a1, float D0) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            BBLcoefficients coeffs;
            coeffs.gs0 = gs0;
            coeffs.a1 = a1;
            coeffs.D0 = D0;
            model->setModelCoefficients(coeffs);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BBL coefficients.");
        }
    }
    
    void setStomatalConductanceBBLCoefficientsForUUIDs(StomatalConductanceModel* model, float gs0, float a1, float D0, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            
            BBLcoefficients coeffs;
            coeffs.gs0 = gs0;
            coeffs.a1 = a1;
            coeffs.D0 = D0;
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            model->setModelCoefficients(coeffs, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BBL coefficients for UUIDs.");
        }
    }

    // MOPT Model Coefficient Functions
    void setStomatalConductanceMOPTCoefficients(StomatalConductanceModel* model, float gs0, float g1) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            MOPTcoefficients coeffs;
            coeffs.gs0 = gs0;
            coeffs.g1 = g1;
            model->setModelCoefficients(coeffs);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting MOPT coefficients.");
        }
    }
    
    void setStomatalConductanceMOPTCoefficientsForUUIDs(StomatalConductanceModel* model, float gs0, float g1, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            
            MOPTcoefficients coeffs;
            coeffs.gs0 = gs0;
            coeffs.g1 = g1;
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            model->setModelCoefficients(coeffs, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting MOPT coefficients for UUIDs.");
        }
    }

    // BMF Model Coefficient Functions
    void setStomatalConductanceBMFCoefficients(StomatalConductanceModel* model, float Em, float i0, float k, float b) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            BMFcoefficients coeffs;
            coeffs.Em = Em;
            coeffs.i0 = i0;
            coeffs.k = k;
            coeffs.b = b;
            model->setModelCoefficients(coeffs);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BMF coefficients.");
        }
    }
    
    void setStomatalConductanceBMFCoefficientsForUUIDs(StomatalConductanceModel* model, float Em, float i0, float k, float b, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            
            BMFcoefficients coeffs;
            coeffs.Em = Em;
            coeffs.i0 = i0;
            coeffs.k = k;
            coeffs.b = b;
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            model->setModelCoefficients(coeffs, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BMF coefficients for UUIDs.");
        }
    }

    // BB Model Coefficient Functions
    void setStomatalConductanceBBCoefficients(StomatalConductanceModel* model, float pi_0, float pi_m, float theta, float sigma, float chi) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            BBcoefficients coeffs;
            coeffs.pi_0 = pi_0;
            coeffs.pi_m = pi_m;
            coeffs.theta = theta;
            coeffs.sigma = sigma;
            coeffs.chi = chi;
            model->setModelCoefficients(coeffs);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BB coefficients.");
        }
    }
    
    void setStomatalConductanceBBCoefficientsForUUIDs(StomatalConductanceModel* model, float pi_0, float pi_m, float theta, float sigma, float chi, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            
            BBcoefficients coeffs;
            coeffs.pi_0 = pi_0;
            coeffs.pi_m = pi_m;
            coeffs.theta = theta;
            coeffs.sigma = sigma;
            coeffs.chi = chi;
            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            model->setModelCoefficients(coeffs, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setModelCoefficients): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setModelCoefficients): Unknown error setting BB coefficients for UUIDs.");
        }
    }

    // Species Library Functions
    void setStomatalConductanceBMFCoefficientsFromLibrary(StomatalConductanceModel* model, const char* species) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            if (!species) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Species name is null");
                return;
            }
            
            model->setBMFCoefficientsFromLibrary(std::string(species));
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setBMFCoefficientsFromLibrary): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setBMFCoefficientsFromLibrary): Unknown error setting BMF coefficients from library.");
        }
    }
    
    void setStomatalConductanceBMFCoefficientsFromLibraryForUUIDs(StomatalConductanceModel* model, const char* species, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            model->setBMFCoefficientsFromLibrary(std::string(species), uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setBMFCoefficientsFromLibrary): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setBMFCoefficientsFromLibrary): Unknown error setting BMF coefficients from library for UUIDs.");
        }
    }

    // Dynamic Time Constants
    void setStomatalConductanceDynamicTimeConstants(StomatalConductanceModel* model, float tau_open, float tau_close) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            if (tau_open <= 0.0f) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Opening time constant must be positive");
                return;
            }
            if (tau_close <= 0.0f) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Closing time constant must be positive");
                return;
            }
            
            model->setDynamicTimeConstants(tau_open, tau_close);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setDynamicTimeConstants): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setDynamicTimeConstants): Unknown error setting dynamic time constants.");
        }
    }
    
    void setStomatalConductanceDynamicTimeConstantsForUUIDs(StomatalConductanceModel* model, float tau_open, float tau_close, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            if (tau_open <= 0.0f) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Opening time constant must be positive");
                return;
            }
            if (tau_close <= 0.0f) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Closing time constant must be positive");
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
            model->setDynamicTimeConstants(tau_open, tau_close, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::setDynamicTimeConstants): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::setDynamicTimeConstants): Unknown error setting dynamic time constants for UUIDs.");
        }
    }
    
    // Utility Functions
    void addStomatalConductanceOptionalOutput(StomatalConductanceModel* model, const char* label) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            
            model->optionalOutputPrimitiveData(label);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::optionalOutputPrimitiveData): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::optionalOutputPrimitiveData): Unknown error adding optional output data.");
        }
    }
    
    void printStomatalConductanceDefaultValueReport(StomatalConductanceModel* model) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
                return;
            }
            
            model->printDefaultValueReport();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::printDefaultValueReport): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::printDefaultValueReport): Unknown error printing default value report.");
        }
    }
    
    void printStomatalConductanceDefaultValueReportForUUIDs(StomatalConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "StomatalConductanceModel pointer is null");
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
            model->printDefaultValueReport(uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (StomatalConductanceModel::printDefaultValueReport): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (StomatalConductanceModel::printDefaultValueReport): Unknown error printing default value report for UUIDs.");
        }
    }
    
} //extern "C"

#endif //STOMATALCONDUCTANCE_PLUGIN_AVAILABLE