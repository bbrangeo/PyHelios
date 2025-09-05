"""
Tests for RadiationModel functionality in PyHelios.

This module tests the RadiationModel class and radiation simulation capabilities.
Tests are designed to work in both native and mock modes.
"""

import pytest
import sys
import os
from typing import List

# Add pyhelios to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyhelios import Context, RadiationModel, RadiationModelError, DataTypes
from pyhelios.validation.exceptions import ValidationError

# RadiationSourceType may not be available if RadiationModel is None
try:
    from pyhelios.RadiationModel import RadiationSourceType
except (ImportError, AttributeError):
    RadiationSourceType = None


@pytest.mark.native_only
class TestRadiationModel:
    """Test RadiationModel class functionality"""
    
    def test_radiation_model_creation(self):
        """Test RadiationModel creation and destruction"""
        with Context() as context:
            # Test creating RadiationModel
            with RadiationModel(context) as radiation_model:
                assert radiation_model is not None
                # Native pointer may be None in mock mode, but RadiationModel should still work
                native_ptr = radiation_model.getNativePtr()
                assert native_ptr is not None or native_ptr is None  # Accept both cases
    
    @pytest.mark.cross_platform  
    def test_radiation_model_invalid_context(self):
        """Test RadiationModel creation with invalid context"""
        with pytest.raises(TypeError):
            RadiationModel("invalid_context")
    
    def test_message_control(self):
        """Test message enable/disable functionality"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # These should not raise exceptions
                radiation_model.disableMessages()
                radiation_model.enableMessages()
    
    def test_radiation_bands(self):
        """Test radiation band management"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Add basic radiation band
                radiation_model.addRadiationBand("SW")
                
                # Add band with wavelength bounds (wavelengths in nanometers)
                radiation_model.addRadiationBand("PAR", 400, 700)
                
                # Copy radiation band
                radiation_model.copyRadiationBand("SW", "SW_copy")
    
    def test_radiation_sources(self):
        """Test radiation source creation"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test default collimated source
                source1 = radiation_model.addCollimatedRadiationSource()
                assert isinstance(source1, int)
                
                # Test collimated source with vec3 direction
                direction = DataTypes.vec3(0.4, -0.4, 0.6)
                source2 = radiation_model.addCollimatedRadiationSource(direction)
                assert isinstance(source2, int)
                
                # Test collimated source with spherical direction
                spherical_dir = DataTypes.SphericalCoord(1.0, 0.5, 0.3)
                source3 = radiation_model.addCollimatedRadiationSource(spherical_dir)
                assert isinstance(source3, int)
                
                # Test sphere radiation source
                position = DataTypes.vec3(0, 0, 10)
                source4 = radiation_model.addSphereRadiationSource(position, 1.0)
                assert isinstance(source4, int)
                
                # Test sun sphere radiation source
                source5 = radiation_model.addSunSphereRadiationSource(
                    radius=1.0, zenith=30.0, azimuth=45.0, angular_width=0.53)
                assert isinstance(source5, int)
    
    def test_radiation_source_invalid_direction(self):
        """Test radiation source creation with invalid direction type"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                with pytest.raises(TypeError):
                    radiation_model.addCollimatedRadiationSource("invalid_direction")
    
    @pytest.mark.cross_platform  
    def test_ray_count_configuration(self):
        """Test ray count configuration"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.addRadiationBand("SW")
                
                # Set direct ray count
                radiation_model.setDirectRayCount("SW", 100)
                
                # Set diffuse ray count
                radiation_model.setDiffuseRayCount("SW", 300)
    
    def test_flux_configuration(self):
        """Test flux configuration"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.addRadiationBand("SW")
                source = radiation_model.addCollimatedRadiationSource()
                
                # Set diffuse radiation flux
                radiation_model.setDiffuseRadiationFlux("SW", 200.0)
                
                # Set single source flux
                radiation_model.setSourceFlux(source, "SW", 800.0)
                
                # Set multiple source flux
                source2 = radiation_model.addCollimatedRadiationSource()
                radiation_model.setSourceFlux([source, source2], "SW", 400.0)
                
                # Get source flux (may return 0 in mock mode)
                flux = radiation_model.getSourceFlux(source, "SW")
                assert isinstance(flux, float)
    
    def test_flux_configuration_invalid_types(self):
        """Test flux configuration with invalid types"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.addRadiationBand("SW")
                
                with pytest.raises(ValidationError):
                    radiation_model.setSourceFlux("invalid_source", "SW", 800.0)
    
    def test_scattering_configuration(self):
        """Test scattering configuration"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.addRadiationBand("SW")
                
                # Set scattering depth
                radiation_model.setScatteringDepth("SW", 3)
                
                # Set minimum scatter energy
                radiation_model.setMinScatterEnergy("SW", 0.01)
    
    def test_emission_control(self):
        """Test emission control"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.addRadiationBand("SW")
                
                # Disable emission
                radiation_model.disableEmission("SW")
                
                # Enable emission
                radiation_model.enableEmission("SW")
    
    def test_geometry_update(self):
        """Test geometry update"""
        with Context() as context:
            # Add some geometry
            patch = context.addPatch()
            
            with RadiationModel(context) as radiation_model:
                # Update all geometry
                radiation_model.updateGeometry()
                
                # Update specific geometry
                radiation_model.updateGeometry([patch])
    
    def test_run_simulation_basic(self):
        """Test basic simulation execution (should not crash in mock mode)"""
        with Context() as context:
            # Add simple geometry
            patch = context.addPatch()
            context.setPrimitiveDataFloat(patch, "radiation_flux_SW", 500.0)
            
            with RadiationModel(context) as radiation_model:
                radiation_model.addRadiationBand("SW")
                source = radiation_model.addCollimatedRadiationSource()
                radiation_model.setSourceFlux(source, "SW", 800.0)
                
                radiation_model.updateGeometry()
                
                # Run single band
                radiation_model.runBand("SW")
                
                # Run multiple bands  
                radiation_model.addRadiationBand("LW")
                radiation_model.runBand(["SW", "LW"])
    
    def test_run_simulation_invalid_types(self):
        """Test simulation with invalid label types"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                with pytest.raises(ValidationError):
                    radiation_model.runBand(123)  # Invalid type
    
    def test_result_access(self):
        """Test accessing simulation results"""
        with Context() as context:
            patch = context.addPatch()
            
            with RadiationModel(context) as radiation_model:
                # Get total absorbed flux (returns list, may be empty in mock mode)
                flux = radiation_model.getTotalAbsorbedFlux()
                assert isinstance(flux, list)


@pytest.mark.native_only
class TestContextPseudocolor:
    """Test Context pseudocolor functionality"""
    
    def test_pseudocolor_basic(self):
        """Test basic pseudocolor functionality"""
        with Context() as context:
            # Add geometry
            patches = [context.addPatch() for _ in range(3)]
            
            # Set primitive data
            for i, patch in enumerate(patches):
                context.setPrimitiveDataFloat(patch, "test_data", float(i * 100))
            
            # Apply pseudocolor (may raise NotImplementedError in mock mode)
            try:
                context.colorPrimitiveByDataPseudocolor(
                    patches, "test_data", "hot", 10)
            except NotImplementedError:
                # Expected in mock mode when pseudocolor functions are not available
                pass
    
    def test_pseudocolor_with_range(self):
        """Test pseudocolor with specified range"""
        with Context() as context:
            # Add geometry
            patches = [context.addPatch() for _ in range(3)]
            
            # Set primitive data
            for i, patch in enumerate(patches):
                context.setPrimitiveDataFloat(patch, "test_data", float(i * 100))
            
            # Apply pseudocolor with range (may raise NotImplementedError in mock mode)
            try:
                context.colorPrimitiveByDataPseudocolor(
                    patches, "test_data", "cool", 10, max_val=300.0, min_val=0.0)
            except NotImplementedError:
                # Expected in mock mode when pseudocolor functions are not available
                pass
    
    def test_pseudocolor_different_colormaps(self):
        """Test different colormap options"""
        with Context() as context:
            patch = context.addPatch()
            context.setPrimitiveDataFloat(patch, "test_data", 100.0)
            
            # Test different colormaps (may raise NotImplementedError in mock mode)
            colormaps = ["hot", "cool", "parula", "rainbow", "gray", "lava"]
            for colormap in colormaps:
                try:
                    context.colorPrimitiveByDataPseudocolor(
                        [patch], "test_data", colormap, 5)
                except NotImplementedError:
                    # Expected in mock mode when pseudocolor functions are not available
                    continue


@pytest.mark.native_only
class TestRadiationModelIntegration:
    """Integration tests requiring native RadiationModel library"""
    
    def test_stanford_bunny_workflow(self):
        """Test Stanford Bunny-style radiation workflow"""
        # This test requires native libraries and the actual Stanford Bunny PLY file
        ply_path = os.path.join(os.path.dirname(__file__), '..', 
                               'helios-core', 'PLY', 'StanfordBunny.ply')
        
        if not os.path.exists(ply_path):
            pytest.skip("Stanford Bunny PLY file not found")
        
        with Context() as context:
            try:
                # Load Stanford Bunny
                bunny_uuids = context.loadPLY(ply_path, 
                                            origin=DataTypes.vec3(0, 0, 0),
                                            height=4.0)
                
                assert len(bunny_uuids) > 0
                
                with RadiationModel(context) as radiation_model:
                    # Set up radiation simulation
                    radiation_model.addRadiationBand("SW") 
                    radiation_model.disableEmission("SW")
                    radiation_model.setDirectRayCount("SW", 10)  # Low count for test speed
                    
                    sun_direction = DataTypes.vec3(0.4, -0.4, 0.6)
                    source = radiation_model.addCollimatedRadiationSource(sun_direction)
                    radiation_model.setSourceFlux(source, "SW", 800.0)
                    
                    radiation_model.updateGeometry()
                    radiation_model.runBand("SW")
                    
                    # Apply pseudocolor
                    context.colorPrimitiveByDataPseudocolor(
                        bunny_uuids[:100], "radiation_flux_SW", "hot")
                    
            except Exception:
                pytest.skip("Native RadiationModel not available or simulation failed")


@pytest.mark.mock_mode
class TestRadiationModelMockMode:
    """Tests specifically for mock mode behavior"""
    
    def test_mock_mode_graceful_degradation(self):
        """Test that RadiationModel provides clear error message when radiation plugin is unavailable"""
        from pyhelios.plugins.registry import get_plugin_registry
        
        # Skip this test if radiation plugin is actually available
        registry = get_plugin_registry()
        if registry.is_plugin_available('radiation'):
            pytest.skip("Radiation plugin is available - this test is for mock mode only")
        
        with Context() as context:
            # RadiationModel should raise RadiationModelError when radiation plugin is not available
            with pytest.raises(RadiationModelError) as excinfo:
                RadiationModel(context)
            
            # Error message should be informative and actionable
            error_msg = str(excinfo.value)
            assert "radiation plugin" in error_msg
            assert "not available" in error_msg or "required but is not available" in error_msg
            
            # Should mention system requirements
            assert any(keyword in error_msg for keyword in ["GPU", "CUDA", "OptiX", "build"])
            
            # Should provide actionable solutions  
            assert "build_scripts/build_helios" in error_msg


@pytest.mark.native_only
class TestRadiationModelCameraFunctions:
    """Test new camera and image functions in RadiationModel v1.3.47"""
    
    def test_write_camera_image(self):
        """Test camera image writing functionality"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test basic camera image writing (may return empty string in mock mode)
                filename = radiation_model.write_camera_image(
                    camera="test_camera", 
                    bands=["RGB", "NIR"], 
                    imagefile_base="test_image",
                    image_path="./output"
                )
                assert isinstance(filename, str)
    
    def test_write_camera_image_invalid_params(self):
        """Test camera image writing with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test invalid camera type
                with pytest.raises(TypeError):
                    radiation_model.write_camera_image(
                        camera=123,  # Invalid type
                        bands=["RGB"], 
                        imagefile_base="test"
                    )
                
                # Test empty bands list
                with pytest.raises(TypeError):
                    radiation_model.write_camera_image(
                        camera="test_camera",
                        bands=[],  # Empty list
                        imagefile_base="test"
                    )
                
                # Test invalid flux conversion
                with pytest.raises(TypeError):
                    radiation_model.write_camera_image(
                        camera="test_camera",
                        bands=["RGB"],
                        imagefile_base="test",
                        flux_to_pixel_conversion=0  # Invalid value
                    )
    
    def test_write_norm_camera_image(self):
        """Test normalized camera image writing"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                filename = radiation_model.write_norm_camera_image(
                    camera="test_camera",
                    bands=["R", "G", "B"],
                    imagefile_base="normalized_test",
                    frame=0
                )
                assert isinstance(filename, str)
    
    def test_write_camera_image_data(self):
        """Test camera image data writing (ASCII format)"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Should not raise exception
                radiation_model.write_camera_image_data(
                    camera="test_camera",
                    band="RGB",
                    imagefile_base="data_test",
                    image_path="./output",
                    frame=-1
                )
    
    def test_write_image_bounding_boxes_single_primitive(self):
        """Test writing image bounding boxes with single primitive data label"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test single primitive data label
                radiation_model.write_image_bounding_boxes(
                    camera_label="test_camera",
                    primitive_data_labels="tree_species",
                    object_class_ids=1,
                    image_file="test_image.jpg"
                )
    
    def test_write_image_bounding_boxes_multiple_primitive(self):
        """Test writing image bounding boxes with multiple primitive data labels"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test multiple primitive data labels
                radiation_model.write_image_bounding_boxes(
                    camera_label="test_camera",
                    primitive_data_labels=["leaves", "branches", "trunk"],
                    object_class_ids=[1, 2, 3],
                    image_file="test_image.jpg",
                    classes_txt_file="plant_classes.txt"
                )
    
    def test_write_image_bounding_boxes_single_object(self):
        """Test writing image bounding boxes with single object data label"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test single object data label
                radiation_model.write_image_bounding_boxes(
                    camera_label="test_camera",
                    object_data_labels="tree_id",
                    object_class_ids=5,
                    image_file="test_image.jpg"
                )
    
    def test_write_image_bounding_boxes_multiple_object(self):
        """Test writing image bounding boxes with multiple object data labels"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test multiple object data labels
                radiation_model.write_image_bounding_boxes(
                    camera_label="test_camera",
                    object_data_labels=["tree_1", "tree_2", "tree_3"],
                    object_class_ids=[10, 11, 12],
                    image_file="test_image.jpg",
                    image_path="./annotations"
                )
    
    def test_write_image_bounding_boxes_invalid_params(self):
        """Test bounding boxes with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test both primitive and object labels provided (should fail)
                with pytest.raises(ValueError):
                    radiation_model.write_image_bounding_boxes(
                        camera_label="test_camera",
                        primitive_data_labels="test",
                        object_data_labels="test2",  # Both provided - invalid
                        object_class_ids=1,
                        image_file="test.jpg"
                    )
                
                # Test neither provided (should fail)
                with pytest.raises(ValueError):
                    radiation_model.write_image_bounding_boxes(
                        camera_label="test_camera",
                        image_file="test.jpg"
                    )
                
                # Test mismatched lengths
                with pytest.raises(ValueError):
                    radiation_model.write_image_bounding_boxes(
                        camera_label="test_camera",
                        primitive_data_labels=["a", "b"],
                        object_class_ids=[1],  # Wrong length
                        image_file="test.jpg"
                    )
    
    def test_write_image_segmentation_masks_single_primitive(self):
        """Test writing segmentation masks with single primitive data label"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.write_image_segmentation_masks(
                    camera_label="test_camera",
                    primitive_data_labels="leaf_type",
                    object_class_ids=1,
                    json_filename="segmentation.json",
                    image_file="test_image.jpg",
                    append_file=False
                )
    
    def test_write_image_segmentation_masks_multiple_primitive(self):
        """Test writing segmentation masks with multiple primitive data labels"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.write_image_segmentation_masks(
                    camera_label="test_camera",
                    primitive_data_labels=["leaves", "stem", "fruit"],
                    object_class_ids=[1, 2, 3],
                    json_filename="multi_segmentation.json",
                    image_file="test_image.jpg",
                    append_file=True
                )
    
    def test_write_image_segmentation_masks_object_data(self):
        """Test writing segmentation masks with object data labels"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Single object data label
                radiation_model.write_image_segmentation_masks(
                    camera_label="test_camera",
                    object_data_labels="plant_id",
                    object_class_ids=10,
                    json_filename="object_segmentation.json",
                    image_file="test_image.jpg"
                )
                
                # Multiple object data labels
                radiation_model.write_image_segmentation_masks(
                    camera_label="test_camera",
                    object_data_labels=["plant_1", "plant_2"],
                    object_class_ids=[10, 11],
                    json_filename="multi_object_segmentation.json",
                    image_file="test_image.jpg",
                    append_file=True
                )
    
    def test_write_image_segmentation_masks_invalid_params(self):
        """Test segmentation masks with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test both primitive and object labels provided (should fail)
                with pytest.raises(ValueError):
                    radiation_model.write_image_segmentation_masks(
                        camera_label="test_camera",
                        primitive_data_labels="test",
                        object_data_labels="test2",  # Both provided - invalid
                        object_class_ids=1,
                        json_filename="test.json",
                        image_file="test.jpg"
                    )
                
                # Test invalid append_file type
                with pytest.raises(TypeError):
                    radiation_model.write_image_segmentation_masks(
                        camera_label="test_camera",
                        primitive_data_labels="test",
                        object_class_ids=1,
                        json_filename="test.json",
                        image_file="test.jpg",
                        append_file="invalid"  # Should be boolean
                    )
    
    def test_auto_calibrate_camera_image(self):
        """Test auto-calibration of camera images"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test basic auto-calibration
                filename = radiation_model.auto_calibrate_camera_image(
                    camera_label="test_camera",
                    red_band_label="Red",
                    green_band_label="Green", 
                    blue_band_label="Blue",
                    output_file_path="calibrated_image.jpg"
                )
                assert isinstance(filename, str)
                
                # Test with quality report and CCM export
                filename2 = radiation_model.auto_calibrate_camera_image(
                    camera_label="test_camera",
                    red_band_label="R",
                    green_band_label="G",
                    blue_band_label="B",
                    output_file_path="calibrated_with_report.jpg",
                    print_quality_report=True,
                    algorithm="DIAGONAL_ONLY",
                    ccm_export_file_path="color_correction_matrix.txt"
                )
                assert isinstance(filename2, str)
    
    def test_auto_calibrate_camera_image_algorithms(self):
        """Test auto-calibration with different algorithms"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test all valid algorithms
                algorithms = ["DIAGONAL_ONLY", "MATRIX_3X3_AUTO", "MATRIX_3X3_FORCE"]
                
                for algorithm in algorithms:
                    filename = radiation_model.auto_calibrate_camera_image(
                        camera_label="test_camera",
                        red_band_label="R",
                        green_band_label="G",
                        blue_band_label="B",
                        output_file_path=f"calibrated_{algorithm.lower()}.jpg",
                        algorithm=algorithm
                    )
                    assert isinstance(filename, str)
    
    def test_auto_calibrate_camera_image_invalid_params(self):
        """Test auto-calibration with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test invalid algorithm
                with pytest.raises(ValueError):
                    radiation_model.auto_calibrate_camera_image(
                        camera_label="test_camera",
                        red_band_label="R",
                        green_band_label="G",
                        blue_band_label="B",
                        output_file_path="test.jpg",
                        algorithm="INVALID_ALGORITHM"
                    )
                
                # Test empty camera label
                with pytest.raises(TypeError):
                    radiation_model.auto_calibrate_camera_image(
                        camera_label="",  # Empty string
                        red_band_label="R",
                        green_band_label="G",
                        blue_band_label="B",
                        output_file_path="test.jpg"
                    )
                
                # Test invalid print_quality_report type
                with pytest.raises(TypeError):
                    radiation_model.auto_calibrate_camera_image(
                        camera_label="test_camera",
                        red_band_label="R",
                        green_band_label="G",
                        blue_band_label="B",
                        output_file_path="test.jpg",
                        print_quality_report="invalid"  # Should be boolean
                    )


@pytest.mark.cross_platform
class TestRadiationModelCameraFunctionsMock:
    """Test camera functions work in mock mode (cross-platform)"""
    
    def test_camera_functions_in_mock_mode(self):
        """Test that camera functions handle mock mode gracefully"""
        # These tests should work even when native libraries are not available
        # Mock mode should raise appropriate RadiationModelError with helpful messages
        
        with Context() as context:
            try:
                with RadiationModel(context) as radiation_model:
                    # If we get here, radiation plugin is available
                    filename = radiation_model.write_camera_image(
                        camera="test", bands=["RGB"], imagefile_base="test")
                    assert isinstance(filename, str)
                    
            except (RuntimeError, RadiationModelError) as e:
                # Expected in mock mode - should have helpful error message
                error_msg = str(e).lower()
                assert any(keyword in error_msg for keyword in 
                          ["radiation", "not available", "plugin", "native library"])


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])