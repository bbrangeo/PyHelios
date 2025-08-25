// PyHelios C Interface - Radiation Functions  
// Provides OptiX-accelerated ray tracing and radiation modeling functions

#include "../include/pyhelios_wrapper_common.h"
#include "../include/pyhelios_wrapper_context.h"
#include "Context.h"
#include <string>
#include <exception>

#ifdef RADIATION_PLUGIN_AVAILABLE
#include "../include/pyhelios_wrapper_radiation.h"
#include "RadiationModel.h"

extern "C" {
    // RadiationModel C interface functions
    
    RadiationModel* createRadiationModel(helios::Context* context) {
        try {
            clearError();
            if (!context) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Context pointer is null");
                return nullptr;
            }
            return new RadiationModel(context);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::constructor): ") + e.what());
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::constructor): Unknown error creating RadiationModel.");
            return nullptr;
        }
    }
    
    void destroyRadiationModel(RadiationModel* radiation_model) {
        try {
            clearError();
            if (radiation_model != nullptr) {
                delete radiation_model;
            }
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::destructor): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::destructor): Unknown error destroying RadiationModel.");
        }
    }
    
    void disableRadiationMessages(RadiationModel* radiation_model) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            radiation_model->disableMessages();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::disableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::disableMessages): Unknown error disabling messages.");
        }
    }
    
    void enableRadiationMessages(RadiationModel* radiation_model) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            radiation_model->enableMessages();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::enableMessages): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::enableMessages): Unknown error enabling messages.");
        }
    }
    
    void addRadiationBand(RadiationModel* radiation_model, const char* label) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->addRadiationBand(std::string(label));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::addRadiationBand): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::addRadiationBand): Unknown error adding radiation band.");
        }
    }
    
    void addRadiationBandWithWavelengths(RadiationModel* radiation_model, const char* label, float wavelength_min, float wavelength_max) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->addRadiationBand(std::string(label), wavelength_min, wavelength_max);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::addRadiationBandWithWavelengths): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::addRadiationBandWithWavelengths): Unknown error adding radiation band with wavelengths.");
        }
    }
    
    void copyRadiationBand(RadiationModel* radiation_model, const char* old_label, const char* new_label) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!old_label || !new_label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->copyRadiationBand(std::string(old_label), std::string(new_label));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::copyRadiationBand): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::copyRadiationBand): Unknown error copying radiation band.");
        }
    }
    
    unsigned int addCollimatedRadiationSourceDefault(RadiationModel* radiation_model) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return 0;
            }
            return radiation_model->addCollimatedRadiationSource();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::addCollimatedRadiationSource): ") + e.what());
            return 0;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::addCollimatedRadiationSource): Unknown error adding collimated radiation source.");
            return 0;
        }
    }
    
    unsigned int addCollimatedRadiationSourceVec3(RadiationModel* radiation_model, float x, float y, float z) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return 0;
            }
            helios::vec3 direction(x, y, z);
            return radiation_model->addCollimatedRadiationSource(direction);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::addCollimatedRadiationSource): ") + e.what());
            return 0;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::addCollimatedRadiationSource): Unknown error adding collimated radiation source with vec3.");
            return 0;
        }
    }
    
    unsigned int addCollimatedRadiationSourceSpherical(RadiationModel* radiation_model, float radius, float elevation, float azimuth) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return 0;
            }
            helios::SphericalCoord direction(radius, elevation, azimuth);
            return radiation_model->addCollimatedRadiationSource(direction);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::addCollimatedRadiationSource): ") + e.what());
            return 0;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::addCollimatedRadiationSource): Unknown error adding collimated radiation source with spherical coordinates.");
            return 0;
        }
    }
    
    unsigned int addSphereRadiationSource(RadiationModel* radiation_model, float x, float y, float z, float radius) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return 0;
            }
            helios::vec3 position(x, y, z);
            return radiation_model->addSphereRadiationSource(position, radius);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::addSphereRadiationSource): ") + e.what());
            return 0;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::addSphereRadiationSource): Unknown error adding sphere radiation source.");
            return 0;
        }
    }
    
    unsigned int addSunSphereRadiationSource(RadiationModel* radiation_model, float radius, float zenith, float azimuth, float position_scaling, float angular_width, float flux_scaling) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return 0;
            }
            helios::SphericalCoord sun_direction(radius, zenith, azimuth);
            return radiation_model->addSunSphereRadiationSource(sun_direction);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::addSunSphereRadiationSource): ") + e.what());
            return 0;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::addSunSphereRadiationSource): Unknown error adding sun sphere radiation source.");
            return 0;
        }
    }
    
    void setDirectRayCount(RadiationModel* radiation_model, const char* label, size_t count) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->setDirectRayCount(std::string(label), count);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::setDirectRayCount): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::setDirectRayCount): Unknown error setting direct ray count.");
        }
    }
    
    void setDiffuseRayCount(RadiationModel* radiation_model, const char* label, size_t count) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->setDiffuseRayCount(std::string(label), count);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::setDiffuseRayCount): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::setDiffuseRayCount): Unknown error setting diffuse ray count.");
        }
    }
    
    void setDiffuseRadiationFlux(RadiationModel* radiation_model, const char* label, float flux) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->setDiffuseRadiationFlux(std::string(label), flux);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::setDiffuseRadiationFlux): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::setDiffuseRadiationFlux): Unknown error setting diffuse radiation flux.");
        }
    }
    
    void setSourceFlux(RadiationModel* radiation_model, unsigned int source_id, const char* label, float flux) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->setSourceFlux(source_id, std::string(label), flux);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::setSourceFlux): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::setSourceFlux): Unknown error setting source flux.");
        }
    }
    
    void setSourceFluxMultiple(RadiationModel* radiation_model, unsigned int* source_ids, size_t count, const char* label, float flux) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!source_ids || !label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Parameters are null");
                return;
            }
            std::vector<unsigned int> id_vector(source_ids, source_ids + count);
            radiation_model->setSourceFlux(id_vector, std::string(label), flux);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::setSourceFlux): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::setSourceFlux): Unknown error setting multiple source flux.");
        }
    }
    
    float getSourceFlux(RadiationModel* radiation_model, unsigned int source_id, const char* label) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return 0.0f;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return 0.0f;
            }
            return radiation_model->getSourceFlux(source_id, std::string(label));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::getSourceFlux): ") + e.what());
            return 0.0f;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::getSourceFlux): Unknown error getting source flux.");
            return 0.0f;
        }
    }
    
    void setScatteringDepth(RadiationModel* radiation_model, const char* label, unsigned int depth) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->setScatteringDepth(std::string(label), depth);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::setScatteringDepth): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::setScatteringDepth): Unknown error setting scattering depth.");
        }
    }
    
    void setMinScatterEnergy(RadiationModel* radiation_model, const char* label, float energy) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->setMinScatterEnergy(std::string(label), energy);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::setMinScatterEnergy): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::setMinScatterEnergy): Unknown error setting min scatter energy.");
        }
    }
    
    void disableEmission(RadiationModel* radiation_model, const char* label) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->disableEmission(std::string(label));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::disableEmission): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::disableEmission): Unknown error disabling emission.");
        }
    }
    
    void enableEmission(RadiationModel* radiation_model, const char* label) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->enableEmission(std::string(label));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::enableEmission): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::enableEmission): Unknown error enabling emission.");
        }
    }
    
    void updateRadiationGeometry(RadiationModel* radiation_model) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            radiation_model->updateGeometry();
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::updateGeometry): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::updateGeometry): Unknown error updating geometry.");
        }
    }
    
    void updateRadiationGeometryUUIDs(RadiationModel* radiation_model, unsigned int* uuids, size_t count) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!uuids) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUIDs array is null");
                return;
            }
            std::vector<unsigned int> uuid_vector(uuids, uuids + count);
            radiation_model->updateGeometry(uuid_vector);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::updateGeometry): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::updateGeometry): Unknown error updating specific geometry.");
        }
    }
    
    void runRadiationBand(RadiationModel* radiation_model, const char* label) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!label) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Label is null");
                return;
            }
            radiation_model->runBand(std::string(label));
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::runBand): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::runBand): Unknown error running radiation band.");
        }
    }
    
    void runRadiationBandMultiple(RadiationModel* radiation_model, const char** labels, size_t count) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                return;
            }
            if (!labels) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Labels array is null");
                return;
            }
            std::vector<std::string> label_vector;
            for (size_t i = 0; i < count; i++) {
                if (labels[i]) {
                    label_vector.push_back(std::string(labels[i]));
                }
            }
            radiation_model->runBand(label_vector);
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::runBand): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::runBand): Unknown error running multiple radiation bands.");
        }
    }
    
    float* getTotalAbsorbedFlux(RadiationModel* radiation_model, size_t* size) {
        try {
            clearError();
            if (!radiation_model) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "RadiationModel pointer is null");
                if (size) *size = 0;
                return nullptr;
            }
            if (!size) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Size pointer is null");
                return nullptr;
            }
            
            std::vector<float> flux_data = radiation_model->getTotalAbsorbedFlux();
            
            // Allocate static buffer for flux data
            static std::vector<float> flux_buffer;
            flux_buffer = flux_data;
            *size = flux_buffer.size();
            return flux_buffer.data();
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (RadiationModel::getTotalAbsorbedFlux): ") + e.what());
            if (size) *size = 0;
            return nullptr;
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (RadiationModel::getTotalAbsorbedFlux): Unknown error getting absorbed flux.");
            if (size) *size = 0;
            return nullptr;
        }
    }


} //extern "C"

#endif //RADIATION_PLUGIN_AVAILABLE
