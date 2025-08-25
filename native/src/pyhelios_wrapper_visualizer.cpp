// PyHelios C Interface - Visualizer Functions
// Provides OpenGL-based 3D visualization and rendering functions

#include "../include/pyhelios_wrapper_common.h"
#include "../include/pyhelios_wrapper_context.h"
#include "Context.h"
#include <string>
#include <exception>

#ifdef VISUALIZER_PLUGIN_AVAILABLE
#include "../include/pyhelios_wrapper_visualizer.h"
#include "Visualizer.h"

extern "C" {
    
    //=============================================================================
    // Visualizer Functions
    //=============================================================================

    Visualizer* createVisualizer(unsigned int width, unsigned int height, bool headless) {
        // Enable window decorations by default (true), headless parameter controls window visibility
        return new Visualizer(width, height, 4, true, headless); // 4 antialiasing samples, decorations enabled
    }
    
    Visualizer* createVisualizerWithAntialiasing(unsigned int width, unsigned int height, unsigned int samples, bool headless) {
        // Enable window decorations by default (true), headless parameter controls window visibility  
        return new Visualizer(width, height, samples, true, headless);
    }
    
    void destroyVisualizer(Visualizer* visualizer) {
        delete visualizer;
    }
    
    void buildContextGeometry(Visualizer* visualizer, helios::Context* context) {
        visualizer->buildContextGeometry(context);
    }
    
    void buildContextGeometryUUIDs(Visualizer* visualizer, helios::Context* context, unsigned int* uuids, unsigned int count) {
        std::vector<unsigned int> uuid_vector(uuids, uuids + count);
        visualizer->buildContextGeometry(context, uuid_vector);
    }
    
    void plotInteractive(Visualizer* visualizer) {
        visualizer->plotInteractive();
    }
    
    void plotUpdate(Visualizer* visualizer) {
        visualizer->plotUpdate();
    }
    
    void printWindow(Visualizer* visualizer, const char* filename) {
        visualizer->printWindow(filename);
    }
    
    void closeWindow(Visualizer* visualizer) {
        visualizer->closeWindow();
    }
    
    void setBackgroundColor(Visualizer* visualizer, float* color) {
        helios::RGBcolor bg_color(color[0], color[1], color[2]);
        visualizer->setBackgroundColor(bg_color);
    }
    
    void setLightDirection(Visualizer* visualizer, float* direction) {
        helios::vec3 light_dir(direction[0], direction[1], direction[2]);
        visualizer->setLightDirection(light_dir);
    }
    
    void setCameraPosition(Visualizer* visualizer, float* position, float* lookat) {
        helios::vec3 camera_pos(position[0], position[1], position[2]);
        helios::vec3 look_at(lookat[0], lookat[1], lookat[2]);
        visualizer->setCameraPosition(camera_pos, look_at);
    }
    
    void setCameraPositionSpherical(Visualizer* visualizer, float* angle, float* lookat) {
        // angle array: [radius, elevation, azimuth] - create SphericalCoord properly
        helios::SphericalCoord camera_angle = helios::make_SphericalCoord(angle[0], angle[1], angle[2]);
        helios::vec3 look_at(lookat[0], lookat[1], lookat[2]);
        visualizer->setCameraPosition(camera_angle, look_at);
    }
    
    void setLightingModel(Visualizer* visualizer, unsigned int model) {
        Visualizer::LightingModel lighting_model;
        
        switch (model) {
            case 0:
                lighting_model = Visualizer::LIGHTING_NONE;
                break;
            case 1:
                lighting_model = Visualizer::LIGHTING_PHONG;
                break;
            case 2:
                lighting_model = Visualizer::LIGHTING_PHONG_SHADOWED;
                break;
            default:
                // Default to phong if unknown
                lighting_model = Visualizer::LIGHTING_PHONG;
                break;
        }
        
        visualizer->setLightingModel(lighting_model);
    }
    
    bool validateTextureFile(const char* texture_file) {
        std::string filename(texture_file);
        return ::validateTextureFile(filename);
    }
    
    void colorContextPrimitivesByData(Visualizer* visualizer, const char* data_name) {
        try {
            clearError();
            if (!visualizer) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Visualizer pointer is null");
                return;
            }
            if (!data_name) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Data name is null");
                return;
            }
            
            visualizer->colorContextPrimitivesByData(data_name);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (Visualizer::colorContextPrimitivesByData): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (Visualizer::colorContextPrimitivesByData): Unknown error coloring primitives by data.");
        }
    }
    
    void colorContextPrimitivesByDataUUIDs(Visualizer* visualizer, const char* data_name, unsigned int* uuids, unsigned int count) {
        try {
            clearError();
            if (!visualizer) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Visualizer pointer is null");
                return;
            }
            if (!data_name) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "Data name is null");
                return;
            }
            if (!uuids && count > 0) {
                setError(PYHELIOS_ERROR_INVALID_PARAMETER, "UUID array is null but count > 0");
                return;
            }
            
            std::vector<unsigned int> uuid_vector(uuids, uuids + count);
            visualizer->colorContextPrimitivesByData(data_name, uuid_vector);
            
        } catch (const std::exception& e) {
            setError(PYHELIOS_ERROR_RUNTIME, std::string("ERROR (Visualizer::colorContextPrimitivesByData): ") + e.what());
        } catch (...) {
            setError(PYHELIOS_ERROR_UNKNOWN, "ERROR (Visualizer::colorContextPrimitivesByData): Unknown error coloring primitives by data with UUIDs.");
        }
    }

} //extern "C"

#endif //VISUALIZER_PLUGIN_AVAILABLE
