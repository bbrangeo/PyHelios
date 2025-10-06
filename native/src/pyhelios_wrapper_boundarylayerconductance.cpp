// PyHelios C Interface - BoundaryLayerConductance Functions
// Provides boundary layer conductance modeling for heat and mass transfer

#include "../include/pyhelios_wrapper_common.h"
#include "../include/pyhelios_wrapper_context.h"
#include "Context.h"
#include <string>
#include <exception>

#ifdef BOUNDARYLAYERCONDUCTANCE_PLUGIN_AVAILABLE
#include "../include/pyhelios_wrapper_boundarylayerconductance.h"
#include "BoundaryLayerConductanceModel.h"

extern "C" {

    PYHELIOS_API BLConductanceModel* createBoundaryLayerConductanceModel(helios::Context* context) {
        try {
            clearError();
            if (!context) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Context pointer is null");
                return nullptr;
            }

            return new BLConductanceModel(context);

        } catch (const std::runtime_error& e) {
            setError(PYHELIOS_ERROR_RUNTIME, e.what());
            return nullptr;
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (createBoundaryLayerConductanceModel): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (createBoundaryLayerConductanceModel): Unknown error creating BLConductanceModel.");
            return nullptr;
        }
    }

    PYHELIOS_API void destroyBoundaryLayerConductanceModel(BLConductanceModel* model) {
        if (model) {
            delete model;
        }
    }

    PYHELIOS_API void enableBoundaryLayerMessages(BLConductanceModel* model) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "BLConductanceModel pointer is null");
                return;
            }

            model->enableMessages();

        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (BLConductanceModel::enableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (BLConductanceModel::enableMessages): Unknown error enabling messages.");
        }
    }

    PYHELIOS_API void disableBoundaryLayerMessages(BLConductanceModel* model) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "BLConductanceModel pointer is null");
                return;
            }

            model->disableMessages();

        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (BLConductanceModel::disableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (BLConductanceModel::disableMessages): Unknown error disabling messages.");
        }
    }

    PYHELIOS_API void setBoundaryLayerModel(BLConductanceModel* model, const char* model_name) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "BLConductanceModel pointer is null");
                return;
            }
            if (!model_name) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Model name is null");
                return;
            }

            model->setBoundaryLayerModel(model_name);

        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (BLConductanceModel::setBoundaryLayerModel): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (BLConductanceModel::setBoundaryLayerModel): Unknown error setting boundary layer model.");
        }
    }

    PYHELIOS_API void setBoundaryLayerModelForUUID(BLConductanceModel* model, unsigned int uuid, const char* model_name) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "BLConductanceModel pointer is null");
                return;
            }
            if (!model_name) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Model name is null");
                return;
            }

            model->setBoundaryLayerModel(uuid, model_name);

        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (BLConductanceModel::setBoundaryLayerModel): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (BLConductanceModel::setBoundaryLayerModel): Unknown error setting boundary layer model for UUID.");
        }
    }

    PYHELIOS_API void setBoundaryLayerModelForUUIDs(BLConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count, const char* model_name) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "BLConductanceModel pointer is null");
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
            if (!model_name) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Model name is null");
                return;
            }

            std::vector<uint> uuid_vector(uuids, uuids + uuid_count);
            model->setBoundaryLayerModel(uuid_vector, model_name);

        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (BLConductanceModel::setBoundaryLayerModel): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (BLConductanceModel::setBoundaryLayerModel): Unknown error setting boundary layer model for UUIDs.");
        }
    }

    PYHELIOS_API void runBoundaryLayerModel(BLConductanceModel* model) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "BLConductanceModel pointer is null");
                return;
            }

            model->run();

        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (BLConductanceModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (BLConductanceModel::run): Unknown error running boundary layer conductance model.");
        }
    }

    PYHELIOS_API void runBoundaryLayerModelForUUIDs(BLConductanceModel* model, const unsigned int* uuids, unsigned int uuid_count) {
        try {
            clearError();
            if (!model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "BLConductanceModel pointer is null");
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
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (BLConductanceModel::run): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (BLConductanceModel::run): Unknown error running boundary layer conductance model for UUIDs.");
        }
    }

} // extern "C"

#endif // BOUNDARYLAYERCONDUCTANCE_PLUGIN_AVAILABLE
