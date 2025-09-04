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

//=============================================================================
// Camera and Image Functions (v1.3.47)
//=============================================================================

/**
 * @brief Write camera image to file (returns output filename)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera Camera label
 * @param bands Array of band labels
 * @param band_count Number of bands
 * @param imagefile_base Base filename for output
 * @param image_path Output directory path
 * @param frame Frame number (-1 for all)
 * @param flux_to_pixel_conversion Conversion factor
 * @return Output filename string
 */
PYHELIOS_API const char* writeCameraImage(RadiationModel* radiation_model, const char* camera, 
                                          const char** bands, size_t band_count,
                                          const char* imagefile_base, const char* image_path, 
                                          int frame, float flux_to_pixel_conversion);

/**
 * @brief Write normalized camera image to file (returns output filename)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera Camera label
 * @param bands Array of band labels
 * @param band_count Number of bands
 * @param imagefile_base Base filename for output
 * @param image_path Output directory path
 * @param frame Frame number (-1 for all)
 * @return Output filename string
 */
PYHELIOS_API const char* writeNormCameraImage(RadiationModel* radiation_model, const char* camera, 
                                              const char** bands, size_t band_count,
                                              const char* imagefile_base, const char* image_path, int frame);

/**
 * @brief Write camera image data to file (ASCII format)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera Camera label
 * @param band Band label
 * @param imagefile_base Base filename for output
 * @param image_path Output directory path
 * @param frame Frame number (-1 for all)
 */
PYHELIOS_API void writeCameraImageData(RadiationModel* radiation_model, const char* camera, const char* band,
                                       const char* imagefile_base, const char* image_path, int frame);

/**
 * @brief Write image bounding boxes (single primitive data label)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param primitive_data_label Primitive data label
 * @param object_class_id Object class ID
 * @param image_file Image filename
 * @param classes_txt_file Classes file
 * @param image_path Image output path
 */
PYHELIOS_API void writeImageBoundingBoxes(RadiationModel* radiation_model, const char* camera_label,
                                          const char* primitive_data_label, unsigned int object_class_id,
                                          const char* image_file, const char* classes_txt_file, const char* image_path);

/**
 * @brief Write image bounding boxes (vector primitive data labels)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param primitive_data_labels Array of primitive data labels
 * @param label_count Number of labels
 * @param object_class_ids Array of class IDs
 * @param image_file Image filename
 * @param classes_txt_file Classes file
 * @param image_path Image output path
 */
PYHELIOS_API void writeImageBoundingBoxesVector(RadiationModel* radiation_model, const char* camera_label,
                                                const char** primitive_data_labels, size_t label_count,
                                                unsigned int* object_class_ids, const char* image_file,
                                                const char* classes_txt_file, const char* image_path);

/**
 * @brief Write image bounding boxes with object data (single label)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param object_data_label Object data label
 * @param object_class_id Object class ID
 * @param image_file Image filename
 * @param classes_txt_file Classes file
 * @param image_path Image output path
 */
PYHELIOS_API void writeImageBoundingBoxes_ObjectData(RadiationModel* radiation_model, const char* camera_label,
                                                     const char* object_data_label, unsigned int object_class_id,
                                                     const char* image_file, const char* classes_txt_file, const char* image_path);

/**
 * @brief Write image bounding boxes with object data (vector labels)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param object_data_labels Array of object data labels
 * @param label_count Number of labels
 * @param object_class_ids Array of class IDs
 * @param image_file Image filename
 * @param classes_txt_file Classes file
 * @param image_path Image output path
 */
PYHELIOS_API void writeImageBoundingBoxes_ObjectDataVector(RadiationModel* radiation_model, const char* camera_label,
                                                           const char** object_data_labels, size_t label_count,
                                                           unsigned int* object_class_ids, const char* image_file,
                                                           const char* classes_txt_file, const char* image_path);

/**
 * @brief Write image segmentation masks (single primitive data label)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param primitive_data_label Primitive data label
 * @param object_class_id Object class ID
 * @param json_filename JSON output filename
 * @param image_file Image filename
 * @param append_file Whether to append to file (1 = true, 0 = false)
 */
PYHELIOS_API void writeImageSegmentationMasks(RadiationModel* radiation_model, const char* camera_label,
                                              const char* primitive_data_label, unsigned int object_class_id,
                                              const char* json_filename, const char* image_file, int append_file);

/**
 * @brief Write image segmentation masks (vector primitive data labels)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param primitive_data_labels Array of primitive data labels
 * @param label_count Number of labels
 * @param object_class_ids Array of class IDs
 * @param json_filename JSON output filename
 * @param image_file Image filename
 * @param append_file Whether to append to file (1 = true, 0 = false)
 */
PYHELIOS_API void writeImageSegmentationMasksVector(RadiationModel* radiation_model, const char* camera_label,
                                                    const char** primitive_data_labels, size_t label_count,
                                                    unsigned int* object_class_ids, const char* json_filename,
                                                    const char* image_file, int append_file);

/**
 * @brief Write image segmentation masks with object data (single label)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param object_data_label Object data label
 * @param object_class_id Object class ID
 * @param json_filename JSON output filename
 * @param image_file Image filename
 * @param append_file Whether to append to file (1 = true, 0 = false)
 */
PYHELIOS_API void writeImageSegmentationMasks_ObjectData(RadiationModel* radiation_model, const char* camera_label,
                                                         const char* object_data_label, unsigned int object_class_id,
                                                         const char* json_filename, const char* image_file, int append_file);

/**
 * @brief Write image segmentation masks with object data (vector labels)
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param object_data_labels Array of object data labels
 * @param label_count Number of labels
 * @param object_class_ids Array of class IDs
 * @param json_filename JSON output filename
 * @param image_file Image filename
 * @param append_file Whether to append to file (1 = true, 0 = false)
 */
PYHELIOS_API void writeImageSegmentationMasks_ObjectDataVector(RadiationModel* radiation_model, const char* camera_label,
                                                               const char** object_data_labels, size_t label_count,
                                                               unsigned int* object_class_ids, const char* json_filename,
                                                               const char* image_file, int append_file);

/**
 * @brief Auto-calibrate camera image with color correction
 * @param radiation_model Pointer to the RadiationModel
 * @param camera_label Camera label
 * @param red_band_label Red band label
 * @param green_band_label Green band label
 * @param blue_band_label Blue band label
 * @param output_file_path Output file path
 * @param print_quality_report Whether to print quality report (1 = true, 0 = false)
 * @param algorithm ColorCorrectionAlgorithm (0=DIAGONAL_ONLY, 1=MATRIX_3X3_AUTO, 2=MATRIX_3X3_FORCE)
 * @param ccm_export_file_path Path to export color correction matrix (optional)
 * @return Output filename string
 */
PYHELIOS_API const char* autoCalibrateCameraImage(RadiationModel* radiation_model, const char* camera_label,
                                                  const char* red_band_label, const char* green_band_label, const char* blue_band_label,
                                                  const char* output_file_path, int print_quality_report,
                                                  int algorithm, const char* ccm_export_file_path);

#ifdef __cplusplus
}
#endif

#endif // PYHELIOS_WRAPPER_RADIATION_H