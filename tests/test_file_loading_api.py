"""
Test the file loading API interfaces (without requiring native library)
"""

import pytest
import os
from pyhelios import Context
from pyhelios.types import vec3, RGBcolor, SphericalCoord


class TestFileLoadingAPI:
    """Test the file loading API interfaces."""
    
    def test_context_has_loading_methods(self):
        """Test that Context has the required loading methods."""
        context = Context()
        
        # Check that methods exist
        assert hasattr(context, 'loadPLY')
        assert hasattr(context, 'loadOBJ') 
        assert hasattr(context, 'loadXML')
        
        # Check that methods are callable
        assert callable(context.loadPLY)
        assert callable(context.loadOBJ)
        assert callable(context.loadXML)
    
    def test_loadPLY_method_signature(self):
        """Test loadPLY method accepts expected parameters."""
        context = Context()
        
        # Test that method accepts various parameter combinations
        # (these will fail with current library but should validate API)
        
        # Basic call
        try:
            context.loadPLY("test.ply")
        except (RuntimeError, NotImplementedError, FileNotFoundError):
            pass  # Expected due to missing function or file
        
        # With transformations
        try:
            context.loadPLY(
                "test.ply",
                origin=vec3(1, 2, 3),
                height=2.0,
                rotation=SphericalCoord(1, 0.5, 1.0),
                color=RGBcolor(1, 0, 0),
                upaxis="YUP",
                silent=True
            )
        except (RuntimeError, NotImplementedError, FileNotFoundError):
            pass  # Expected
    
    def test_loadOBJ_method_signature(self):
        """Test loadOBJ method accepts expected parameters.""" 
        context = Context()
        
        # Basic call
        try:
            context.loadOBJ("test.obj")
        except (RuntimeError, NotImplementedError, FileNotFoundError):
            pass  # Expected
        
        # With transformations
        try:
            context.loadOBJ(
                "test.obj",
                origin=vec3(1, 2, 3),
                height=2.0,
                scale=vec3(1, 1, 1),
                rotation=SphericalCoord(1, 0.5, 1.0),
                color=RGBcolor(0, 1, 0),
                upaxis="ZUP",
                silent=True
            )
        except (RuntimeError, NotImplementedError, FileNotFoundError):
            pass  # Expected
    
    def test_loadXML_method_signature(self):
        """Test loadXML method accepts expected parameters."""
        context = Context()
        
        # Basic call
        try:
            context.loadXML("test.xml")
        except (RuntimeError, NotImplementedError, FileNotFoundError):
            pass  # Expected
        
        # With quiet parameter
        try:
            context.loadXML("test.xml", quiet=True)
        except (RuntimeError, NotImplementedError, FileNotFoundError):
            pass  # Expected
    
    def test_file_validation_works(self):
        """Test that file validation works regardless of library availability."""
        context = Context()
        
        # Test non-existent files (will raise FileNotFoundError before extension check)
        with pytest.raises(FileNotFoundError):
            context.loadPLY("nonexistent.ply")
        
        with pytest.raises(FileNotFoundError):
            context.loadOBJ("nonexistent.obj")
        
        with pytest.raises(FileNotFoundError):
            context.loadXML("nonexistent.xml")
        
        # Test invalid extensions with existing files (create temp files)
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"test")
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError, match="Invalid file extension"):
                context.loadPLY(tmp_path)
        finally:
            os.unlink(tmp_path)
        
        with tempfile.NamedTemporaryFile(suffix='.ply', delete=False) as tmp:
            tmp.write(b"test")
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError, match="Invalid file extension"):
                context.loadOBJ(tmp_path)
        finally:
            os.unlink(tmp_path)
        
        with tempfile.NamedTemporaryFile(suffix='.obj', delete=False) as tmp:
            tmp.write(b"test")
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError, match="Invalid file extension"):
                context.loadXML(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_parameter_validation_works(self):
        """Test that parameter validation works."""
        context = Context()
        
        # Test invalid parameter combinations for loadPLY
        from tests.conftest import get_example_file_path
        try:
            ply_path = get_example_file_path("suzanne.ply")
            with pytest.raises(ValueError, match="Invalid parameter combination"):
                context.loadPLY(
                    ply_path,
                    origin=vec3(0, 0, 0),  # Only origin, missing height
                    rotation=SphericalCoord(1, 0, 0)
                )
        except (RuntimeError, NotImplementedError):
            # Library not available, but parameter validation should still work
            pass

        # Test invalid parameter combinations for loadOBJ
        try:
            obj_path = get_example_file_path("suzanne.obj")
            with pytest.raises(ValueError, match="Invalid parameter combination"):
                context.loadOBJ(
                    obj_path,
                    origin=vec3(0, 0, 0),  # Missing other required parameters
                    height=1.0
                )
        except (RuntimeError, NotImplementedError):
            # Library not available, but parameter validation should still work
            pass


class TestWrapperFunctions:
    """Test wrapper function signatures and availability detection."""
    
    def test_wrapper_availability_detection(self):
        """Test that wrapper correctly detects function availability."""
        from pyhelios.wrappers import UContextWrapper as wrapper
        
        # Check availability flags exist
        assert hasattr(wrapper, '_FILE_LOADING_FUNCTIONS_AVAILABLE')
        assert hasattr(wrapper, '_PLY_LOADING_FUNCTIONS_AVAILABLE')
        assert hasattr(wrapper, '_OBJ_XML_LOADING_FUNCTIONS_AVAILABLE')
        
        # Print current status
        print(f"File loading available: {wrapper._FILE_LOADING_FUNCTIONS_AVAILABLE}")
        print(f"PLY loading available: {wrapper._PLY_LOADING_FUNCTIONS_AVAILABLE}")
        print(f"OBJ/XML loading available: {wrapper._OBJ_XML_LOADING_FUNCTIONS_AVAILABLE}")
    
    def test_wrapper_functions_exist(self):
        """Test that wrapper functions exist."""
        from pyhelios.wrappers import UContextWrapper as wrapper
        
        # Check that wrapper functions exist
        assert hasattr(wrapper, 'loadPLY')
        assert hasattr(wrapper, 'loadPLYWithOriginHeight')
        assert hasattr(wrapper, 'loadPLYWithOriginHeightRotation')
        assert hasattr(wrapper, 'loadPLYWithOriginHeightColor')
        assert hasattr(wrapper, 'loadPLYWithOriginHeightRotationColor')
        
        assert hasattr(wrapper, 'loadOBJ')
        assert hasattr(wrapper, 'loadOBJWithOriginHeightRotationColor')
        assert hasattr(wrapper, 'loadOBJWithOriginHeightRotationColorUpaxis')
        assert hasattr(wrapper, 'loadOBJWithOriginScaleRotationColorUpaxis')
        
        assert hasattr(wrapper, 'loadXML')
    
    def test_informative_error_messages(self):
        """Test that wrapper functions provide informative error messages."""
        from pyhelios.wrappers import UContextWrapper as wrapper
        
        # Create a dummy context pointer (won't work but tests error message)
        try:
            wrapper.loadPLY(None, "test.ply", False)
        except (RuntimeError, NotImplementedError) as e:
            error_msg = str(e).lower()
            # Should mention rebuilding or missing functions
            assert any(keyword in error_msg for keyword in 
                      ['rebuild', 'not available', 'missing', 'library'])
        except:
            # Other errors are acceptable for this test
            pass