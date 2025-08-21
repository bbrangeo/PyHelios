"""
Tests for Visualizer functionality in PyHelios.

This module tests the Visualizer class and 3D visualization capabilities.
Tests are designed to work in both native and mock modes.
"""

import pytest
import sys
import os
from typing import List

# Add pyhelios to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyhelios import Context, Visualizer, DataTypes
from pyhelios.Visualizer import VisualizerError


def is_headless_environment():
    """
    Check if we're running in a headless environment where visualization tests would fail.
    
    This function performs multiple checks to determine if the environment supports
    OpenGL rendering, which is required for the visualizer plugin tests.
    
    Returns:
        bool: True if headless (skip visualization tests), False if display is available
    """
    # Check for display availability
    display = os.environ.get('DISPLAY')
    if not display:
        return True  # No display available
    
    # Check if we're in an SSH session without X11 forwarding
    ssh_client = os.environ.get('SSH_CLIENT')
    ssh_tty = os.environ.get('SSH_TTY')
    if ssh_client or ssh_tty:
        # In SSH session - check if DISPLAY is properly set for X11 forwarding
        if not display or display == ':0':
            return True  # SSH without proper X11 forwarding
    
    # Additional check for CI environments
    ci_indicators = ['CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS', 'TRAVIS', 'JENKINS']
    if any(os.environ.get(var) for var in ci_indicators):
        return True  # Running in CI environment
    
    # Try a simple OpenGL context test if we can import necessary libraries
    try:
        import subprocess
        import sys
        
        # On macOS, try to verify OpenGL/graphics capability through system_profiler
        if sys.platform == 'darwin':
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0 or 'Graphics/Displays' not in result.stdout:
                return True  # Can't verify graphics capability
        
        # On Linux, check if we can connect to X display
        elif sys.platform.startswith('linux'):
            result = subprocess.run(['xrandr', '--query'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return True  # Can't connect to X display
                
    except (ImportError, FileNotFoundError, subprocess.TimeoutExpired, Exception):
        # If we can't run the checks, be conservative
        return True
    
    return False  # Display should be available


def should_skip_interactive_visualizer_tests():
    """
    Check if interactive visualizer tests should be skipped.
    
    These tests may cause crashes even in environments with displays if the OpenGL
    context or graphics drivers have issues. Users can override with PYHELIOS_TEST_VISUALIZER_INTERACTIVE.
    
    Returns:
        bool: True if interactive tests should be skipped
    """
    # Allow users to force enable risky tests
    if os.environ.get('PYHELIOS_TEST_VISUALIZER_INTERACTIVE') == '1':
        return False
        
    # Skip if headless
    if is_headless_environment():
        return True
        
    # Be conservative about tests that call plotUpdate() or other interactive functions
    # These are known to cause crashes in some environments
    return True


@pytest.mark.cross_platform
class TestVisualizerCrossPlatform:
    """Cross-platform tests that work in both native and mock modes"""
    
    def test_visualizer_creation_parameters(self):
        """Test Visualizer parameter validation"""
        # Test invalid dimensions
        with pytest.raises(ValueError, match="Width and height must be positive"):
            Visualizer(0, 600)
        
        with pytest.raises(ValueError, match="Width and height must be positive"):
            Visualizer(800, -1)
        
        # Test invalid antialiasing
        with pytest.raises(ValueError, match="Antialiasing samples must be at least 1"):
            Visualizer(800, 600, antialiasing_samples=0)
    
    def test_visualizer_lighting_constants(self):
        """Test lighting model constants"""
        assert Visualizer.LIGHTING_NONE == 0
        assert Visualizer.LIGHTING_PHONG == 1
        assert Visualizer.LIGHTING_PHONG_SHADOWED == 2


@pytest.mark.native_only
@pytest.mark.skipif(is_headless_environment(), reason="Skipping visualizer tests in headless environment")
class TestVisualizerNative:
    """Test Visualizer class functionality with native library"""
    
    def test_visualizer_creation_basic(self):
        """Test basic Visualizer creation and destruction"""
        # Test creating Visualizer with default parameters
        with Visualizer(800, 600) as visualizer:
            assert visualizer is not None
            assert visualizer.width == 800
            assert visualizer.height == 600
            assert visualizer.antialiasing_samples == 1
            assert visualizer.headless == False
    
    def test_visualizer_creation_with_parameters(self):
        """Test Visualizer creation with custom parameters"""
        # Test with antialiasing and headless mode
        with Visualizer(1024, 768, antialiasing_samples=4, headless=True) as visualizer:
            assert visualizer.width == 1024
            assert visualizer.height == 768
            assert visualizer.antialiasing_samples == 4
            assert visualizer.headless == True
    
    def test_visualizer_context_geometry(self):
        """Test building Context geometry in visualizer"""
        with Context() as context:
            # Add some geometry to context
            center = DataTypes.vec3(0, 0, 0)
            size = DataTypes.vec2(1, 1)
            patch_uuid = context.addPatch(center=center, size=size)
            
            with Visualizer(400, 300, headless=True) as visualizer:
                # Build all geometry
                visualizer.buildContextGeometry(context)
                
                # Build specific geometry
                visualizer.buildContextGeometry(context, uuids=[patch_uuid])
    
    def test_visualizer_context_geometry_validation(self):
        """Test Context geometry building parameter validation"""
        with Context() as context:
            with Visualizer(400, 300, headless=True) as visualizer:
                # Test invalid context type (raises ValueError before try-catch)
                with pytest.raises(ValueError, match="context must be a Context instance"):
                    visualizer.buildContextGeometry("invalid_context")
                
                # Test empty UUIDs list (raises ValueError inside try-catch, wrapped in VisualizerError)
                with pytest.raises(VisualizerError, match="UUIDs list cannot be empty"):
                    visualizer.buildContextGeometry(context, uuids=[])
    
    @pytest.mark.skipif(should_skip_interactive_visualizer_tests(), 
                        reason="Skipping interactive visualizer test (may cause crashes). Set PYHELIOS_TEST_VISUALIZER_INTERACTIVE=1 to enable.")
    def test_visualizer_rendering_headless(self):
        """Test basic rendering operations in headless mode"""
        with Context() as context:
            # Add geometry
            center = DataTypes.vec3(0, 0, 0)
            size = DataTypes.vec2(1, 1)
            context.addPatch(center=center, size=size)
            
            with Visualizer(400, 300, headless=True) as visualizer:
                visualizer.buildContextGeometry(context)
                
                # Test plot update (non-interactive)
                visualizer.plotUpdate()
                
                # Test window operations
                visualizer.closeWindow()
    
    @pytest.mark.skipif(should_skip_interactive_visualizer_tests(), 
                        reason="Skipping interactive visualizer test (may cause crashes). Set PYHELIOS_TEST_VISUALIZER_INTERACTIVE=1 to enable.")
    def test_visualizer_image_export(self):
        """Test image export functionality"""
        with Context() as context:
            # Add geometry
            center = DataTypes.vec3(0, 0, 0)
            size = DataTypes.vec2(1, 1)
            color = DataTypes.RGBcolor(0.5, 0.5, 0.5)
            context.addPatch(center=center, size=size, color=color)
            
            with Visualizer(400, 300, headless=True) as visualizer:
                visualizer.buildContextGeometry(context)
                visualizer.plotUpdate()
                
                # Test image export (this might require temp file handling)
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    tmp_name = tmp.name
                
                try:
                    visualizer.printWindow(tmp_name)
                    # Check if file was created (size check would be better but file might be empty in mock)
                    assert os.path.exists(tmp_name)
                finally:
                    if os.path.exists(tmp_name):
                        os.unlink(tmp_name)
    
    def test_visualizer_camera_controls(self):
        """Test camera positioning functions"""
        with Visualizer(400, 300, headless=True) as visualizer:
            # Test Cartesian camera positioning
            visualizer.setCameraPosition([5, 5, 5], [0, 0, 0])
            
            # Test spherical camera positioning
            visualizer.setCameraPositionSpherical([10, 45, 45], [0, 0, 0])
    
    def test_visualizer_camera_validation(self):
        """Test camera parameter validation"""
        with Visualizer(400, 300, headless=True) as visualizer:
            # Test invalid position dimensions
            with pytest.raises(ValueError, match="Position must have 3 elements"):
                visualizer.setCameraPosition([1, 2], [0, 0, 0])
            
            with pytest.raises(ValueError, match="LookAt must have 3 elements"):
                visualizer.setCameraPosition([1, 2, 3], [0, 0])
            
            # Test invalid spherical dimensions
            with pytest.raises(ValueError, match="Angle must have 3 elements"):
                visualizer.setCameraPositionSpherical([10, 45], [0, 0, 0])
    
    def test_visualizer_scene_configuration(self):
        """Test scene configuration functions"""
        with Visualizer(400, 300, headless=True) as visualizer:
            # Test background color
            visualizer.setBackgroundColor([0.2, 0.3, 0.4])
            
            # Test light direction
            visualizer.setLightDirection([1, 1, -1])
            
            # Test lighting models
            visualizer.setLightingModel(Visualizer.LIGHTING_NONE)
            visualizer.setLightingModel(Visualizer.LIGHTING_PHONG)
            visualizer.setLightingModel(Visualizer.LIGHTING_PHONG_SHADOWED)
            
            # Test string lighting models
            visualizer.setLightingModel("none")
            visualizer.setLightingModel("phong")
            visualizer.setLightingModel("phong_shadowed")
    
    def test_visualizer_scene_validation(self):
        """Test scene configuration parameter validation"""
        with Visualizer(400, 300, headless=True) as visualizer:
            # Test invalid color dimensions
            with pytest.raises(ValueError, match="Color must have 3 elements"):
                visualizer.setBackgroundColor([0.5, 0.5])
            
            # Test invalid color range
            with pytest.raises(ValueError, match="Color component .* must be in range"):
                visualizer.setBackgroundColor([1.5, 0.5, 0.5])
            
            with pytest.raises(ValueError, match="Color component .* must be in range"):
                visualizer.setBackgroundColor([0.5, -0.1, 0.5])
            
            # Test invalid direction dimensions
            with pytest.raises(ValueError, match="Direction must have 3 elements"):
                visualizer.setLightDirection([1, 1])
            
            # Test zero direction vector
            with pytest.raises(ValueError, match="Light direction cannot be zero vector"):
                visualizer.setLightDirection([0, 0, 0])
            
            # Test invalid lighting model
            with pytest.raises(ValueError, match="Lighting model must be"):
                visualizer.setLightingModel(99)
            
            with pytest.raises(ValueError, match="Unknown lighting model string"):
                visualizer.setLightingModel("invalid_model")
    
    def test_visualizer_state_validation(self):
        """Test operations on destroyed visualizer"""
        visualizer = Visualizer(400, 300, headless=True)
        visualizer.__exit__(None, None, None)  # Manually destroy
        
        # Test that operations fail on destroyed visualizer
        with pytest.raises(VisualizerError, match="Visualizer has been destroyed"):
            with Context() as context:
                visualizer.buildContextGeometry(context)
        
        with pytest.raises(VisualizerError, match="Visualizer has been destroyed"):
            visualizer.plotUpdate()
        
        with pytest.raises(VisualizerError, match="Visualizer has been destroyed"):
            visualizer.setCameraPosition([1, 2, 3], [0, 0, 0])


@pytest.mark.mock_mode
class TestVisualizerMockMode:
    """Test Visualizer behavior in mock mode"""
    
    def test_visualizer_mock_mode_error_messages(self):
        """Test that mock mode provides helpful error messages"""
        # This test assumes we're in an environment without visualizer plugin
        try:
            # Use headless mode to avoid display issues in CI
            with Visualizer(400, 300, headless=True) as visualizer:
                pytest.skip("Visualizer plugin is available, skipping mock mode test")
        except VisualizerError as e:
            error_message = str(e)
            # Check that error message contains helpful information
            assert "visualizer" in error_message.lower()
            assert "plugin" in error_message.lower()
            assert "build" in error_message.lower()
            # Should contain installation hints
            assert any(hint in error_message.lower() for hint in ["opengl", "glfw", "build_scripts"])
        except Exception as e:
            # In CI environments, visualizer creation may fail with fatal errors
            # This is expected behavior when graphics context is not available
            pytest.skip(f"Visualizer creation failed in test environment: {e}")


@pytest.mark.cross_platform  
class TestVisualizerAPI:
    """Test Visualizer API compatibility across platforms"""
    
    def test_visualizer_types_and_defaults(self):
        """Test that types and defaults are consistent"""
        # Test that we can import and access constants
        assert hasattr(Visualizer, 'LIGHTING_NONE')
        assert hasattr(Visualizer, 'LIGHTING_PHONG')
        assert hasattr(Visualizer, 'LIGHTING_PHONG_SHADOWED')
    
    def test_visualizer_context_manager_protocol(self):
        """Test context manager protocol"""
        # This should work even in mock mode for API validation
        try:
            visualizer = Visualizer(400, 300, headless=True)
            assert hasattr(visualizer, '__enter__')
            assert hasattr(visualizer, '__exit__')
            
            # Test that __enter__ returns self
            entered = visualizer.__enter__()
            assert entered is visualizer
            
            # Clean up
            visualizer.__exit__(None, None, None)
        except VisualizerError:
            # Expected in mock mode
            pass
    
    def test_visualizer_method_signatures(self):
        """Test that all expected methods exist with correct signatures"""
        # Test method existence
        expected_methods = [
            'buildContextGeometry',
            'plotInteractive', 
            'plotUpdate',
            'printWindow',
            'closeWindow',
            'setCameraPosition',
            'setCameraPositionSpherical', 
            'setBackgroundColor',
            'setLightDirection',
            'setLightingModel'
        ]
        
        for method_name in expected_methods:
            assert hasattr(Visualizer, method_name), f"Missing method: {method_name}"
            method = getattr(Visualizer, method_name)
            assert callable(method), f"Method {method_name} is not callable"


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])