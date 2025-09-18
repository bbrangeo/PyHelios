"""
Tests for Context file loading methods (loadPLY, loadOBJ, loadXML)
"""

import pytest
import os
from pyhelios import Context
from pyhelios.types import vec3, RGBcolor, SphericalCoord
from pyhelios import HeliosError


@pytest.fixture
def sample_files():
    """Paths to sample files for testing."""
    from tests.conftest import get_example_file_path
    return {
        'ply': get_example_file_path("suzanne.ply"),
        'obj': get_example_file_path("suzanne.obj"),
        'xml': get_example_file_path("leaf_cube.xml")
    }


class TestContextFileLoading:
    """Test Context file loading functionality."""
    
    @pytest.fixture
    def context(self):
        """Create a Context instance for testing."""
        return Context()
    
    @pytest.mark.cross_platform
    def test_sample_files_exist(self):
        """Verify that sample files exist for testing (skip if in wheel environment)."""
        from tests.conftest import example_file_exists

        # Check if example files are available
        files_to_check = ["suzanne.ply", "suzanne.obj", "leaf_cube.xml"]
        missing_files = [f for f in files_to_check if not example_file_exists(f)]

        if missing_files:
            pytest.skip(f"Example files not available in wheel environment: {missing_files}")

        # If we get here, all files exist
        for filename in files_to_check:
            example_path = os.path.join("docs", "examples", "models", filename)
            assert os.path.exists(example_path), f"Sample file not found: {example_path}"
    
    # =================================================================================
    # PLY Loading Tests
    # =================================================================================
    
    @pytest.mark.native_only
    def test_loadPLY_basic(self, context, sample_files):
        """Test basic PLY loading without transformations."""
        uuids = context.loadPLY(sample_files['ply'])
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from PLY file")
        
        # Verify primitives exist in context
        for uuid in uuids[:5]:  # Check first 5 UUIDs
            assert uuid in context.getAllUUIDs()
    
    @pytest.mark.native_only
    def test_loadPLY_with_origin_height(self, context, sample_files):
        """Test PLY loading with origin and height transformation."""
        origin = vec3(1, 2, 3)
        height = 2.0
        
        uuids = context.loadPLY(
            sample_files['ply'], 
            origin=origin, 
            height=height
        )
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from PLY file with origin and height")
    
    @pytest.mark.native_only
    def test_loadPLY_with_rotation(self, context, sample_files):
        """Test PLY loading with rotation transformation."""
        origin = vec3(0, 0, 1)
        height = 1.5
        rotation = SphericalCoord(1, 0.5, 1.0)  # radius, elevation, azimuth
        
        uuids = context.loadPLY(
            sample_files['ply'],
            origin=origin,
            height=height, 
            rotation=rotation
        )
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from PLY file with rotation")
    
    @pytest.mark.native_only
    def test_loadPLY_with_color(self, context, sample_files):
        """Test PLY loading with default color."""
        origin = vec3(0, 0, 0)
        height = 1.0
        color = RGBcolor(1.0, 0.0, 0.0)  # Red
        
        uuids = context.loadPLY(
            sample_files['ply'],
            origin=origin,
            height=height,
            color=color
        )
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from PLY file with color")
    
    @pytest.mark.native_only  
    def test_loadPLY_all_parameters(self, context, sample_files):
        """Test PLY loading with all parameters."""
        origin = vec3(2, 3, 4)
        height = 2.5
        rotation = SphericalCoord(1, 0.3, 0.7)
        color = RGBcolor(0.0, 1.0, 0.0)  # Green
        upaxis = "ZUP"
        
        uuids = context.loadPLY(
            sample_files['ply'],
            origin=origin,
            height=height,
            rotation=rotation,
            color=color,
            upaxis=upaxis,
            silent=True
        )
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from PLY file with all parameters")
    
    @pytest.mark.cross_platform
    def test_loadPLY_file_validation(self, context):
        """Test PLY loading with invalid file paths."""
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            context.loadPLY("nonexistent.ply")
        
        # Test wrong extension
        with pytest.raises(ValueError, match="Invalid file extension"):
            context.loadPLY("file.txt")
    
    # =================================================================================
    # OBJ Loading Tests
    # =================================================================================
    
    @pytest.mark.native_only
    def test_loadOBJ_basic(self, context, sample_files):
        """Test basic OBJ loading without transformations."""
        uuids = context.loadOBJ(sample_files['obj'])
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from OBJ file")
        
        # Verify primitives exist in context
        for uuid in uuids[:5]:  # Check first 5 UUIDs
            assert uuid in context.getAllUUIDs()
    
    @pytest.mark.native_only
    def test_loadOBJ_with_transformations(self, context, sample_files):
        """Test OBJ loading with origin, height, rotation, and color."""
        origin = vec3(1, 1, 1)
        height = 3.0
        rotation = SphericalCoord(1, 0.2, 0.8)
        color = RGBcolor(0.0, 0.0, 1.0)  # Blue
        
        uuids = context.loadOBJ(
            sample_files['obj'],
            origin=origin,
            height=height,
            rotation=rotation,
            color=color
        )
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from OBJ file with transformations")
    
    @pytest.mark.native_only
    def test_loadOBJ_with_upaxis(self, context, sample_files):
        """Test OBJ loading with upaxis specification."""
        origin = vec3(0, 0, 2)
        height = 1.0
        rotation = SphericalCoord(1, 0, 0)
        color = RGBcolor(1.0, 1.0, 0.0)  # Yellow
        upaxis = "ZUP"
        
        uuids = context.loadOBJ(
            sample_files['obj'],
            origin=origin,
            height=height,
            rotation=rotation,
            color=color,
            upaxis=upaxis
        )
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from OBJ file with upaxis")
    
    @pytest.mark.native_only
    def test_loadOBJ_with_scale(self, context, sample_files):
        """Test OBJ loading with scale transformation."""
        origin = vec3(0, 0, 0)
        scale = vec3(2.0, 1.5, 0.5)  # Non-uniform scaling
        rotation = SphericalCoord(1, 0.1, 0.4)
        color = RGBcolor(1.0, 0.0, 1.0)  # Magenta
        upaxis = "YUP"
        
        uuids = context.loadOBJ(
            sample_files['obj'],
            origin=origin,
            scale=scale,
            rotation=rotation,
            color=color,
            upaxis=upaxis
        )
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from OBJ file with scale")
    
    @pytest.mark.cross_platform
    def test_loadOBJ_file_validation(self, context):
        """Test OBJ loading with invalid file paths."""
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            context.loadOBJ("nonexistent.obj")
        
        # Test wrong extension
        with pytest.raises(ValueError, match="Invalid file extension"):
            context.loadOBJ("file.ply")
    
    @pytest.mark.cross_platform
    def test_loadOBJ_parameter_validation(self, context, sample_files):
        """Test OBJ loading parameter validation."""
        # Test invalid parameter combinations
        with pytest.raises(ValueError, match="Invalid parameter combination"):
            context.loadOBJ(
                sample_files['obj'],
                origin=vec3(0, 0, 0),  # Missing other required parameters
                height=1.0
            )
    
    # =================================================================================
    # XML Loading Tests
    # =================================================================================
    
    @pytest.mark.native_only
    def test_loadXML_basic(self, context, sample_files):
        """Test basic XML loading."""
        uuids = context.loadXML(sample_files['xml'])
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from XML file")
        
        # Verify primitives exist in context
        for uuid in uuids[:5]:  # Check first 5 UUIDs
            assert uuid in context.getAllUUIDs()
    
    @pytest.mark.native_only
    def test_loadXML_quiet_mode(self, context, sample_files):
        """Test XML loading with quiet mode."""
        uuids = context.loadXML(sample_files['xml'], quiet=True)
        
        assert isinstance(uuids, list)
        assert len(uuids) > 0
        print(f"Loaded {len(uuids)} primitives from XML file (quiet mode)")
    
    @pytest.mark.cross_platform
    def test_loadXML_file_validation(self, context):
        """Test XML loading with invalid file paths."""
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            context.loadXML("nonexistent.xml")
        
        # Test wrong extension
        with pytest.raises(ValueError, match="Invalid file extension"):
            context.loadXML("file.obj")
    
    # =================================================================================
    # Integration Tests
    # =================================================================================
    
    @pytest.mark.native_only
    def test_load_multiple_files(self, context, sample_files):
        """Test loading multiple different file types in one context."""
        # Load PLY file
        ply_uuids = context.loadPLY(
            sample_files['ply'], 
            origin=vec3(0, 0, 0), 
            height=1.0,
            color=RGBcolor(1, 0, 0)
        )
        
        # Load OBJ file at different location
        obj_uuids = context.loadOBJ(
            sample_files['obj'],
            origin=vec3(5, 0, 0),
            height=1.0,
            rotation=SphericalCoord(1, 0, 0),
            color=RGBcolor(0, 1, 0)
        )
        
        # Load XML file at another location
        xml_uuids = context.loadXML(sample_files['xml'], quiet=True)
        
        # Verify all primitives are loaded
        all_context_uuids = context.getAllUUIDs()
        
        assert len(ply_uuids) > 0
        assert len(obj_uuids) > 0
        assert len(xml_uuids) > 0
        
        # Verify no UUID conflicts
        total_loaded = len(ply_uuids) + len(obj_uuids) + len(xml_uuids)
        unique_loaded = len(set(ply_uuids + obj_uuids + xml_uuids))
        assert total_loaded == unique_loaded, "UUID conflicts detected"
        
        print(f"Successfully loaded {len(ply_uuids)} PLY, {len(obj_uuids)} OBJ, and {len(xml_uuids)} XML primitives")
    
    @pytest.mark.native_only
    def test_primitive_properties_after_loading(self, context, sample_files):
        """Test that loaded primitives have correct properties."""
        color = RGBcolor(0.5, 0.8, 0.2)
        uuids = context.loadPLY(
            sample_files['ply'],
            origin=vec3(1, 2, 3),
            height=2.0,
            color=color
        )
        
        # Check properties of first primitive
        if uuids:
            uuid = uuids[0]
            
            # Get primitive info
            info = context.getPrimitiveInfo(uuid)
            assert info.uuid == uuid
            assert info.area > 0
            
            # Check that primitive has vertices
            assert len(info.vertices) > 0
            
            print(f"First primitive: type={info.primitive_type}, area={info.area:.6f}, vertices={len(info.vertices)}")
    
    # =================================================================================
    # Error Handling Tests
    # =================================================================================
    
    @pytest.mark.cross_platform
    def test_security_path_validation(self, context):
        """Test security validation of file paths."""
        # Test path traversal attempts
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for path in malicious_paths:
            with pytest.raises((ValueError, FileNotFoundError)):
                context.loadPLY(path)
    
    @pytest.mark.cross_platform
    def test_parameter_validation_edge_cases(self, context, sample_files):
        """Test edge cases in parameter validation."""
        # Test invalid parameter combinations for PLY
        with pytest.raises(ValueError, match="Invalid parameter combination"):
            context.loadPLY(
                sample_files['ply'],
                origin=vec3(0, 0, 0),  # Only origin, missing height
                rotation=SphericalCoord(1, 0, 0)
            )


class TestMockMode:
    """Test file loading in mock mode."""
    
    @pytest.mark.mock_mode
    def test_mock_mode_error_messages(self):
        """Test that mock mode provides helpful error messages."""
        from pyhelios.plugins.loader import get_library_info
        
        library_info = get_library_info()
        if library_info.get('is_mock', False):
            with Context() as context:
                with pytest.raises(RuntimeError, match="mock mode"):
                    context.loadPLY("test.ply")
                
                with pytest.raises(RuntimeError, match="mock mode"):
                    context.loadOBJ("test.obj")
                
                with pytest.raises(RuntimeError, match="mock mode"):
                    context.loadXML("test.xml")


# =================================================================================
# Performance Tests
# =================================================================================

@pytest.mark.slow
class TestFileLoadingPerformance:
    """Performance tests for file loading operations."""
    
    @pytest.mark.native_only
    def test_loading_performance(self, sample_files):
        """Test that file loading completes within reasonable time."""
        import time
        
        with Context() as context:
            # Time PLY loading
            start_time = time.time()
            ply_uuids = context.loadPLY(sample_files['ply'])
            ply_time = time.time() - start_time
            
            # Time OBJ loading
            start_time = time.time()
            obj_uuids = context.loadOBJ(sample_files['obj'])
            obj_time = time.time() - start_time
            
            # Time XML loading
            start_time = time.time()
            xml_uuids = context.loadXML(sample_files['xml'])
            xml_time = time.time() - start_time
            
            print(f"Loading times: PLY={ply_time:.3f}s, OBJ={obj_time:.3f}s, XML={xml_time:.3f}s")
            
            # All should complete within 10 seconds
            assert ply_time < 10.0, f"PLY loading too slow: {ply_time:.3f}s"
            assert obj_time < 10.0, f"OBJ loading too slow: {obj_time:.3f}s"  
            assert xml_time < 10.0, f"XML loading too slow: {xml_time:.3f}s"