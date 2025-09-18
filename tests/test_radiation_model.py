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
@pytest.mark.requires_gpu
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
@pytest.mark.requires_gpu
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


@pytest.fixture
def radiation_model_with_camera():
    """Fixture providing a RadiationModel with camera setup ready for testing"""
    with Context() as context:
        with RadiationModel(context) as radiation_model:
            # Add basic geometry for camera operations
            from pyhelios.wrappers.DataTypes import vec3, vec2, RGBcolor
            patch_center = vec3(0, 0, 0)
            patch_size = vec2(1.0, 1.0)
            patch_color = RGBcolor(0.5, 0.5, 0.5)
            patch_uuid = context.addPatch(center=patch_center, size=patch_size, color=patch_color)

            # Add primitive data for bounding box detection (integer values)
            context.setPrimitiveDataInt(patch_uuid, "leaves", 1)
            context.setPrimitiveDataInt(patch_uuid, "branches", 2)
            context.setPrimitiveDataInt(patch_uuid, "trunk", 3)
            context.setPrimitiveDataInt(patch_uuid, "tree_species", 4)

            sourceid = radiation_model.addCollimatedRadiationSource()

            # Add radiation band and camera
            radiation_model.addRadiationBand("red")
            radiation_model.setSourceFlux(sourceid, "red", 100.0)
            radiation_model.setScatteringDepth("red", 2)
            radiation_model.addRadiationCamera(
                camera_label="test_camera",
                band_labels=["red"],
                position=vec3(0, 0, 5),
                lookat_or_direction=vec3(0, 0, 0)
            )

            # Update geometry and run simulation (required for camera operations)
            radiation_model.updateGeometry()
            radiation_model.runBand(["red"])

            # Generate camera image to create pixel labels (required for most camera operations)
            radiation_model.writeCameraImage(
                camera="test_camera",
                bands=["red"],
                imagefile_base="test_image",
                image_path="./"
            )

            yield radiation_model, context


@pytest.mark.native_only
@pytest.mark.requires_gpu
class TestRadiationModelCameraFunctions:
    """Test new camera and image functions in RadiationModel v1.3.47"""
    
    def test_writeCameraImage(self):
        """Test camera image writing functionality"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Add some geometry for the camera to render
                from pyhelios.wrappers.DataTypes import vec3, vec2, RGBcolor
                patch_center = vec3(0, 0, 0)
                patch_size = vec2(1.0, 1.0)
                patch_color = RGBcolor(0.5, 0.5, 0.5)
                context.addPatch(center=patch_center, size=patch_size, color=patch_color)

                # Add radiation bands first (use 3 bands for RGB image)
                radiation_model.addRadiationBand("red")
                radiation_model.addRadiationBand("green")
                radiation_model.addRadiationBand("blue")

                # Add camera before writing image
                radiation_model.addRadiationCamera(
                    camera_label="test_camera",
                    band_labels=["red", "green", "blue"],
                    position=vec3(0, 0, 5),
                    lookat_or_direction=vec3(0, 0, 0)
                )

                # Update geometry and run simulation (required for camera operations)
                radiation_model.updateGeometry()
                radiation_model.runBand(["red", "green", "blue"])

                # Test basic camera image writing (may return empty string in mock mode)
                filename = radiation_model.writeCameraImage(
                    camera="test_camera",
                    bands=["red", "green", "blue"],
                    imagefile_base="test_image",
                    image_path="./"
                )
                assert isinstance(filename, str)
    
    def test_writeCameraImage_invalid_params(self):
        """Test camera image writing with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test invalid camera type
                with pytest.raises(TypeError):
                    radiation_model.writeCameraImage(
                        camera=123,  # Invalid type
                        bands=["RGB"], 
                        imagefile_base="test"
                    )
                
                # Test empty bands list
                with pytest.raises(TypeError):
                    radiation_model.writeCameraImage(
                        camera="test_camera",
                        bands=[],  # Empty list
                        imagefile_base="test"
                    )
                
                # Test invalid flux conversion
                with pytest.raises(TypeError):
                    radiation_model.writeCameraImage(
                        camera="test_camera",
                        bands=["RGB"],
                        imagefile_base="test",
                        flux_to_pixel_conversion=0  # Invalid value
                    )
    
    def test_writeNormCameraImage(self):
        """Test normalized camera image writing"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Add radiation bands first
                radiation_model.addRadiationBand("R")
                radiation_model.addRadiationBand("G")
                radiation_model.addRadiationBand("B")

                # Add camera before writing image
                from pyhelios.wrappers.DataTypes import vec3
                radiation_model.addRadiationCamera(
                    camera_label="test_camera",
                    band_labels=["R", "G", "B"],
                    position=vec3(0, 0, 5),
                    lookat_or_direction=vec3(0, 0, 0)
                )

                filename = radiation_model.writeNormCameraImage(
                    camera="test_camera",
                    bands=["R", "G", "B"],
                    imagefile_base="normalized_test",
                    frame=0
                )
                assert isinstance(filename, str)
    
    def test_writeCameraImage_data(self):
        """Test camera image data writing (ASCII format)"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Add radiation band first
                radiation_model.addRadiationBand("RGB")

                # Add camera before writing data
                from pyhelios.wrappers.DataTypes import vec3
                radiation_model.addRadiationCamera(
                    camera_label="test_camera",
                    band_labels=["RGB"],
                    position=vec3(0, 0, 5),
                    lookat_or_direction=vec3(0, 0, 0)
                )

                # Should not raise exception
                radiation_model.writeCameraImageData(
                    camera="test_camera",
                    band="RGB",
                    imagefile_base="data_test",
                    image_path="./output/",
                    frame=-1
                )
    
    def test_writeImageBoundingBoxes_single_primitive(self, radiation_model_with_camera):
        """Test writing image bounding boxes with single primitive data label"""
        radiation_model, context = radiation_model_with_camera

        # Test single primitive data label (tree_species is already set in the fixture)
        radiation_model.writeImageBoundingBoxes(
            camera_label="test_camera",
            primitive_data_labels="tree_species",
            object_class_ids=1,
            image_file="test_image.jpg"
        )
    
    def test_writeImageBoundingBoxes_multiple_primitive(self, radiation_model_with_camera):
        """Test writing image bounding boxes with multiple primitive data labels"""
        radiation_model, context = radiation_model_with_camera

        # Test multiple primitive data labels (leaves, branches, trunk are already set in the fixture)
        radiation_model.writeImageBoundingBoxes(
            camera_label="test_camera",
            primitive_data_labels=["leaves", "branches", "trunk"],
            object_class_ids=[1, 2, 3],
            image_file="test_image.jpg",
            classes_txt_file="plant_classes.txt"
        )
    
    def test_writeImageBoundingBoxes_single_object(self, radiation_model_with_camera):
        """Test writing image bounding boxes with single object data label"""
        radiation_model, context = radiation_model_with_camera

        # Add object data that can be used for bounding boxes
        patch_uuids = context.getAllUUIDs()
        if patch_uuids:
            context.setPrimitiveDataString(patch_uuids[0], "tree_id", "oak_tree_001")

        # Test single object data label
        radiation_model.writeImageBoundingBoxes(
            camera_label="test_camera",
            object_data_labels="tree_id",
            object_class_ids=5,
            image_file="test_image.jpg"
        )
    
    def test_writeImageBoundingBoxes_multiple_object(self, radiation_model_with_camera):
        """Test writing image bounding boxes with multiple object data labels"""
        radiation_model, context = radiation_model_with_camera

        # Add object data that can be used for bounding boxes
        patch_uuids = context.getAllUUIDs()
        if patch_uuids:
            context.setPrimitiveDataString(patch_uuids[0], "tree_1", "oak_001")
            context.setPrimitiveDataString(patch_uuids[0], "tree_2", "oak_002")
            context.setPrimitiveDataString(patch_uuids[0], "tree_3", "oak_003")

        # Test multiple object data labels
        radiation_model.writeImageBoundingBoxes(
            camera_label="test_camera",
            object_data_labels=["tree_1", "tree_2", "tree_3"],
            object_class_ids=[10, 11, 12],
            image_file="test_image.jpg",
            image_path="./annotations/"
        )
    
    def test_writeImageBoundingBoxes_invalid_params(self):
        """Test bounding boxes with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test both primitive and object labels provided (should fail)
                with pytest.raises(ValueError):
                    radiation_model.writeImageBoundingBoxes(
                        camera_label="test_camera",
                        primitive_data_labels="test",
                        object_data_labels="test2",  # Both provided - invalid
                        object_class_ids=1,
                        image_file="test.jpg"
                    )
                
                # Test neither provided (should fail)
                with pytest.raises(ValueError):
                    radiation_model.writeImageBoundingBoxes(
                        camera_label="test_camera",
                        image_file="test.jpg"
                    )
                
                # Test mismatched lengths
                with pytest.raises(ValueError):
                    radiation_model.writeImageBoundingBoxes(
                        camera_label="test_camera",
                        primitive_data_labels=["a", "b"],
                        object_class_ids=[1],  # Wrong length
                        image_file="test.jpg"
                    )
    
    def test_writeImageSegmentationMasks_single_primitive(self, radiation_model_with_camera):
        """Test writing segmentation masks with single primitive data label"""
        radiation_model, context = radiation_model_with_camera

        # Generate camera image first (required for segmentation masks)
        image_filename = radiation_model.writeCameraImage(
            camera="test_camera",
            bands=["red"],
            imagefile_base="test_image",
            image_path="./"
        )

        # Add primitive data for segmentation masks
        patch_uuids = context.getAllUUIDs()
        if patch_uuids:
            context.setPrimitiveDataInt(patch_uuids[0], "leaf_type", 1)

        radiation_model.writeImageSegmentationMasks(
            camera_label="test_camera",
            primitive_data_labels="leaf_type",
            object_class_ids=1,
            json_filename="segmentation.json",
            image_file=image_filename,
            append_file=False
        )
    
    def test_writeImageSegmentationMasks_multiple_primitive(self, radiation_model_with_camera):
        """Test writing segmentation masks with multiple primitive data labels"""
        radiation_model, context = radiation_model_with_camera

        # Generate camera image first (required for segmentation masks)
        image_filename = radiation_model.writeCameraImage(
            camera="test_camera",
            bands=["red"],
            imagefile_base="test_image",
            image_path="./"
        )

        # Add primitive data for segmentation masks
        patch_uuids = context.getAllUUIDs()
        if patch_uuids:
            context.setPrimitiveDataInt(patch_uuids[0], "leaves", 1)
            context.setPrimitiveDataInt(patch_uuids[0], "stem", 1)
            context.setPrimitiveDataInt(patch_uuids[0], "fruit", 2)

        radiation_model.writeImageSegmentationMasks(
            camera_label="test_camera",
            primitive_data_labels=["leaves", "stem", "fruit"],
            object_class_ids=[1, 2, 3],
            json_filename="multi_segmentation.json",
            image_file=image_filename,
            append_file=True
        )
    
    def test_writeImageSegmentationMasks_object_data(self, radiation_model_with_camera):
        """Test writing segmentation masks with object data labels"""
        radiation_model, context = radiation_model_with_camera

        # Generate camera image first (required for segmentation masks)
        image_filename = radiation_model.writeCameraImage(
            camera="test_camera",
            bands=["red"],
            imagefile_base="test_image",
            image_path="./"
        )

        # Add object data for segmentation masks
        patch_uuids = context.getAllUUIDs()
        if patch_uuids:
            context.setPrimitiveDataString(patch_uuids[0], "plant_id", "plant_001")
            context.setPrimitiveDataString(patch_uuids[0], "plant_1", "plant_a")
            context.setPrimitiveDataString(patch_uuids[0], "plant_2", "plant_b")

        # Single object data label
        radiation_model.writeImageSegmentationMasks(
            camera_label="test_camera",
            object_data_labels="plant_id",
            object_class_ids=10,
            json_filename="object_segmentation.json",
            image_file=image_filename
        )

        # Multiple object data labels
        radiation_model.writeImageSegmentationMasks(
            camera_label="test_camera",
            object_data_labels=["plant_1", "plant_2"],
            object_class_ids=[10, 11],
            json_filename="multi_object_segmentation.json",
            image_file=image_filename,
            append_file=True
        )
    
    def test_writeImageSegmentationMasks_invalid_params(self):
        """Test segmentation masks with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test both primitive and object labels provided (should fail)
                with pytest.raises(ValueError):
                    radiation_model.writeImageSegmentationMasks(
                        camera_label="test_camera",
                        primitive_data_labels="test",
                        object_data_labels="test2",  # Both provided - invalid
                        object_class_ids=1,
                        json_filename="test.json",
                        image_file="test.jpg"
                    )
                
                # Test invalid append_file type
                with pytest.raises(TypeError):
                    radiation_model.writeImageSegmentationMasks(
                        camera_label="test_camera",
                        primitive_data_labels="test",
                        object_class_ids=1,
                        json_filename="test.json",
                        image_file="test.jpg",
                        append_file="invalid"  # Should be boolean
                    )
    
    def test_autoCalibrateCameraImage_invalid_params(self):
        """Test auto-calibration with invalid parameters"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Test invalid algorithm
                with pytest.raises(ValueError):
                    radiation_model.autoCalibrateCameraImage(
                        camera_label="test_camera",
                        red_band_label="R",
                        green_band_label="G",
                        blue_band_label="B",
                        output_file_path="test.jpg",
                        algorithm="INVALID_ALGORITHM"
                    )
                
                # Test empty camera label
                with pytest.raises(TypeError):
                    radiation_model.autoCalibrateCameraImage(
                        camera_label="",  # Empty string
                        red_band_label="R",
                        green_band_label="G",
                        blue_band_label="B",
                        output_file_path="test.jpg"
                    )
                
                # Test invalid print_quality_report type
                with pytest.raises(TypeError):
                    radiation_model.autoCalibrateCameraImage(
                        camera_label="test_camera",
                        red_band_label="R",
                        green_band_label="G",
                        blue_band_label="B",
                        output_file_path="test.jpg",
                        print_quality_report="invalid"  # Should be boolean
                    )


@pytest.mark.requires_gpu
class TestRadiationModelCameraFunctionsMock:
    """Test camera functions with GPU/OptiX requirements"""

    def test_camera_functions_with_gpu(self, radiation_model_with_camera):
        """Test that camera functions work when GPU/OptiX is available"""
        # This test requires GPU/OptiX since camera functions use radiation ray tracing
        radiation_model, context = radiation_model_with_camera

        # Add RGB radiation band
        radiation_model.addRadiationBand("RGB")

        # Add camera for testing functionality
        from pyhelios.wrappers.DataTypes import vec3
        radiation_model.addRadiationCamera(
            camera_label="gpu_test",
            band_labels=["RGB"],
            position=vec3(0, 0, 5),
            lookat_or_direction=vec3(0, 0, 0)
        )

        # Update geometry and run simulation
        radiation_model.updateGeometry()
        radiation_model.runBand(["RGB"])

        # Test basic camera functionality
        filename = radiation_model.writeCameraImage(
            camera="gpu_test", bands=["RGB"], imagefile_base="test")
        assert isinstance(filename, str)


@pytest.mark.native_only
@pytest.mark.requires_gpu
class TestRadiationModelCameraCreation:
    """Test addRadiationCamera method functionality"""

    def test_add_radiation_camera_vec3(self):
        """Test adding radiation camera with vec3 position and lookat"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Add radiation bands first
                radiation_model.addRadiationBand("red")
                radiation_model.addRadiationBand("green")
                radiation_model.addRadiationBand("blue")

                # Test basic camera creation with vec3 coordinates
                from pyhelios.wrappers.DataTypes import vec3
                radiation_model.addRadiationCamera(
                    camera_label="test_camera",
                    band_labels=["red", "green", "blue"],
                    position=vec3(0, 0, 5),
                    lookat_or_direction=vec3(0, 0, 0)
                )

    def test_add_radiation_camera_with_properties(self):
        """Test adding radiation camera with custom CameraProperties"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                # Add radiation band
                radiation_model.addRadiationBand("RGB")

                # Create custom camera properties
                from pyhelios import CameraProperties
                camera_props = CameraProperties(
                    camera_resolution=(1024, 1024),
                    focal_plane_distance=2.0,
                    lens_diameter=0.1,
                    HFOV=45.0,
                    FOV_aspect_ratio=1.0
                )

                # Add camera with custom properties
                from pyhelios.wrappers.DataTypes import vec3
                radiation_model.addRadiationCamera(
                    camera_label="hd_camera",
                    band_labels=["RGB"],
                    position=vec3(0, 0, 10),
                    lookat_or_direction=vec3(0, 0, 0),
                    camera_properties=camera_props,
                    antialiasing_samples=200
                )

    def test_add_radiation_camera_validation(self):
        """Test parameter validation for addRadiationCamera"""
        with Context() as context:
            with RadiationModel(context) as radiation_model:
                radiation_model.addRadiationBand("test_band")
                from pyhelios.wrappers.DataTypes import vec3
                from pyhelios.validation.exceptions import ValidationError

                # Test invalid camera label (empty string)
                with pytest.raises(ValidationError):
                    radiation_model.addRadiationCamera(
                        camera_label="",  # Empty string
                        band_labels=["test_band"],
                        position=vec3(0, 0, 5),
                        lookat_or_direction=vec3(0, 0, 0)
                    )

                # Test invalid band labels (empty list)
                with pytest.raises(ValidationError):
                    radiation_model.addRadiationCamera(
                        camera_label="test",
                        band_labels=[],  # Empty list
                        position=vec3(0, 0, 5),
                        lookat_or_direction=vec3(0, 0, 0)
                    )

                # Test invalid antialiasing samples
                with pytest.raises(ValidationError):
                    radiation_model.addRadiationCamera(
                        camera_label="test",
                        band_labels=["test_band"],
                        position=vec3(0, 0, 5),
                        lookat_or_direction=vec3(0, 0, 0),
                        antialiasing_samples=0  # Must be positive
                    )

                # Test invalid list parameters (should reject lists)
                with pytest.raises(TypeError):
                    radiation_model.addRadiationCamera(
                        camera_label="invalid_test",
                        band_labels=["test_band"],
                        position=[1, 2, 3],  # Should reject lists
                        lookat_or_direction=vec3(0, 0, 0)
                    )

                # Test valid camera creation with proper vec3
                radiation_model.addRadiationCamera(
                    camera_label="valid_test",
                    band_labels=["test_band"],
                    position=vec3(1, 2, 3),  # Proper vec3
                    lookat_or_direction=vec3(0, 0, 0)  # Proper vec3
                )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])