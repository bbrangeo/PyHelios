"""
PyHelios Test Configuration and Fixtures

This file provides common fixtures and configuration for PyHelios tests.
"""

import pytest
import platform
import os
from unittest.mock import Mock, MagicMock
from typing import Optional

import pyhelios
from pyhelios import Context, WeberPennTree, DataTypes
from pyhelios import dev_utils


def is_native_library_available():
    """Check if native Helios library is available."""
    try:
        from pyhelios.plugins import is_native_library_available
        return is_native_library_available()
    except Exception:
        return False


def get_platform_name():
    """Get current platform name."""
    return platform.system()


def is_windows():
    """Check if running on Windows platform."""
    return platform.system() == 'Windows'


def is_macos():
    """Check if running on macOS platform."""
    return platform.system() == 'Darwin'


def is_linux():
    """Check if running on Linux platform.""" 
    return platform.system() == 'Linux'


def library_exists():
    """Check if native library exists and can be loaded."""
    try:
        # Try to create a context to verify library availability
        context = Context()
        context.__exit__(None, None, None)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def setup_development_mode():
    """
    Set up development mode for tests that need mock functionality.
    This fixture automatically runs before any tests to enable dev mode
    if native libraries aren't available.
    """
    if not is_native_library_available():
        # Enable development mode for tests when native libraries aren't available
        dev_utils.enable_dev_mode()
        yield
        # Clean up after tests
        dev_utils.enable_dev_mode(False)
    else:
        # Native libraries are available, no need for dev mode
        yield


# No longer skip all tests on non-Windows platforms
# Tests will use mock mode when native libraries aren't available


@pytest.fixture(scope="session")
def check_native_library():
    """Session-scoped fixture to check native library availability."""
    if not is_native_library_available():
        pytest.skip("Native Helios library not available - skipping tests requiring native functionality")


@pytest.fixture(scope="session")
def check_dll():
    """Session-scoped fixture to check native library availability (legacy alias)."""
    if not is_native_library_available():
        pytest.skip("Native Helios library not available - skipping tests requiring native functionality")


@pytest.fixture
def basic_context(check_native_library):
    """Fixture providing a basic Helios Context for testing."""
    context = Context()
    yield context
    context.__exit__(None, None, None)


@pytest.fixture
def mock_context():
    """Fixture providing a mocked Context for testing without DLL dependency."""
    mock_ctx = Mock(spec=Context)
    mock_ctx.getPrimitiveCount.return_value = 0
    mock_ctx.getAllUUIDs.return_value = []
    mock_ctx.addPatch.return_value = 1
    mock_ctx.getPrimitiveType.return_value = pyhelios.PrimitiveType.Patch
    mock_ctx.getPrimitiveArea.return_value = 1.0
    mock_ctx.getPrimitiveNormal.return_value = DataTypes.vec3(0, 0, 1)
    mock_ctx.getPrimitiveColor.return_value = DataTypes.RGBcolor(1, 1, 1)
    return mock_ctx


@pytest.fixture
def weber_penn_tree(basic_context):
    """Fixture providing a WeberPennTree instance."""
    wpt = WeberPennTree(basic_context)
    yield wpt
    wpt.__exit__(None, None, None)


@pytest.fixture
def mock_weber_penn_tree():
    """Fixture providing a mocked WeberPennTree for testing without DLL dependency."""
    mock_wpt = Mock(spec=WeberPennTree)
    mock_wpt.buildTree.return_value = 1
    mock_wpt.getTrunkUUIDs.return_value = [1, 2, 3]
    mock_wpt.getBranchUUIDs.return_value = [4, 5, 6]
    mock_wpt.getLeafUUIDs.return_value = [7, 8, 9]
    mock_wpt.getAllUUIDs.return_value = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    return mock_wpt


@pytest.fixture
def sample_vectors():
    """Fixture providing sample vector data for testing."""
    return {
        'vec2_zero': DataTypes.vec2(0, 0),
        'vec2_unit': DataTypes.vec2(1, 1),
        'vec3_zero': DataTypes.vec3(0, 0, 0),
        'vec3_unit': DataTypes.vec3(1, 1, 1),
        'vec3_xyz': DataTypes.vec3(2, 3, 4),
        'color_black': DataTypes.RGBcolor(0, 0, 0),
        'color_white': DataTypes.RGBcolor(1, 1, 1),
        'color_red': DataTypes.RGBcolor(1, 0, 0),
    }


@pytest.fixture
def sample_patch_parameters():
    """Fixture providing sample parameters for creating patches."""
    return {
        'center': DataTypes.vec3(2, 3, 4),
        'size': DataTypes.vec2(1, 1),
        'color': DataTypes.RGBcolor(0.25, 0.25, 0.25),
        'rotation': DataTypes.SphericalCoord(1, 0, 0)
    }


# Platform detection fixtures
@pytest.fixture(scope="session")
def platform_info():
    """Fixture providing platform information."""
    return {
        'name': get_platform_name(),
        'is_windows': is_windows(),
        'is_macos': is_macos(), 
        'is_linux': is_linux(),
        'native_available': is_native_library_available(),
    }


# Utility functions for test assertions
def assert_vec3_equal(v1: DataTypes.vec3, v2: DataTypes.vec3, tolerance=1e-6):
    """Assert that two Vec3 objects are approximately equal."""
    assert abs(v1.x - v2.x) < tolerance, f"Vec3 x components differ: {v1.x} vs {v2.x}"
    assert abs(v1.y - v2.y) < tolerance, f"Vec3 y components differ: {v1.y} vs {v2.y}"
    assert abs(v1.z - v2.z) < tolerance, f"Vec3 z components differ: {v1.z} vs {v2.z}"


def assert_vec2_equal(v1: DataTypes.vec2, v2: DataTypes.vec2, tolerance=1e-6):
    """Assert that two Vec2 objects are approximately equal."""
    assert abs(v1.x - v2.x) < tolerance, f"Vec2 x components differ: {v1.x} vs {v2.x}"
    assert abs(v1.y - v2.y) < tolerance, f"Vec2 y components differ: {v1.y} vs {v2.y}"


def assert_color_equal(c1: DataTypes.RGBcolor, c2: DataTypes.RGBcolor, tolerance=1e-6):
    """Assert that two RGBcolor objects are approximately equal."""
    assert abs(c1.r - c2.r) < tolerance, f"Color r components differ: {c1.r} vs {c2.r}"
    assert abs(c1.g - c2.g) < tolerance, f"Color g components differ: {c1.g} vs {c2.g}"
    assert abs(c1.b - c2.b) < tolerance, f"Color b components differ: {c1.b} vs {c2.b}"


# Test helper functions
def skip_if_no_native_library():
    """Skip test if no native library is available."""
    if not is_native_library_available():
        pytest.skip("Native library not available")


def expect_mock_mode_error():
    """Expect a RuntimeError indicating mock mode."""
    return pytest.raises(RuntimeError, match="mock mode")


def _get_required_plugins_for_test(item):
    """
    Determine which plugins are required for a test based on test file path and name.
    Uses the official plugin metadata system to get comprehensive plugin information.
    
    Returns:
        List of plugin names that are required for this test
    """
    test_file = str(item.fspath).lower()
    test_name = str(item.name).lower()
    
    required_plugins = []
    
    # Get all known plugins from the metadata system
    try:
        from pyhelios.config.plugin_metadata import PLUGIN_METADATA
        all_plugin_names = list(PLUGIN_METADATA.keys())
    except ImportError:
        # Fallback to known plugins if metadata system not available
        all_plugin_names = [
            'radiation', 'visualizer', 'weberpenntree', 'lidar', 'aeriallidar',
            'energybalance', 'voxelintersection', 'collisiondetection', 
            'projectbuilder', 'photosynthesis', 'canopygenerator'
        ]
    
    # Check if test file or name contains any plugin names
    for plugin_name in all_plugin_names:
        if plugin_name in test_file or plugin_name in test_name:
            required_plugins.append(plugin_name)
    
    return list(set(required_plugins))  # Remove duplicates


def _check_plugin_availability(required_plugins):
    """
    Check if all required plugins are available at runtime.
    Provides enhanced information about why plugins are missing (GPU dependencies, etc.).
    
    Args:
        required_plugins: List of plugin names required
        
    Returns:
        tuple: (all_available: bool, missing_info: dict)
            missing_info format: {
                'missing_plugins': list,
                'gpu_required': list,  # subset of missing that require GPU
                'reason': str          # human-readable reason
            }
    """
    if not required_plugins:
        return True, {'missing_plugins': [], 'gpu_required': [], 'reason': ''}
    
    try:
        from pyhelios import Context
        context = Context()
        available_plugins = getattr(context, 'get_available_plugins', lambda: [])()
        context.__exit__(None, None, None)
        
        missing_plugins = [p for p in required_plugins if p not in available_plugins]
        
        if not missing_plugins:
            return True, {'missing_plugins': [], 'gpu_required': [], 'reason': ''}
        
        # Check which missing plugins require GPU
        gpu_required_missing = []
        try:
            from pyhelios.config.plugin_metadata import PLUGIN_METADATA
            for plugin in missing_plugins:
                if plugin in PLUGIN_METADATA and PLUGIN_METADATA[plugin].gpu_required:
                    gpu_required_missing.append(plugin)
        except ImportError:
            # Known GPU-dependent plugins if metadata system not available
            known_gpu_plugins = {'radiation', 'lidar', 'aeriallidar', 'energybalance', 
                               'voxelintersection', 'collisiondetection', 'projectbuilder'}
            gpu_required_missing = [p for p in missing_plugins if p in known_gpu_plugins]
        
        # Generate informative reason
        if gpu_required_missing:
            if len(gpu_required_missing) == len(missing_plugins):
                reason = f"GPU-dependent plugin(s) not available: {', '.join(gpu_required_missing)}"
            else:
                regular_missing = [p for p in missing_plugins if p not in gpu_required_missing]
                reason = f"Missing plugins: {', '.join(regular_missing)} (regular), {', '.join(gpu_required_missing)} (GPU-dependent)"
        else:
            reason = f"Plugin(s) not available: {', '.join(missing_plugins)}"
            
        return False, {
            'missing_plugins': missing_plugins,
            'gpu_required': gpu_required_missing,
            'reason': reason
        }
        
    except Exception:
        # If we can't check, assume plugins are missing
        return False, {
            'missing_plugins': required_plugins,
            'gpu_required': [],
            'reason': f"Unable to check plugin availability: {', '.join(required_plugins)}"
        }


def pytest_runtest_setup(item):
    """Handle pytest marker-based test skipping."""
    # Skip native_only tests when running in mock mode
    if "native_only" in item.keywords:
        if not is_native_library_available():
            pytest.skip("Skipping native_only test - native library not available")
        
        # General plugin availability check for native tests
        required_plugins = _get_required_plugins_for_test(item)
        if required_plugins:
            all_available, missing_info = _check_plugin_availability(required_plugins)
            if not all_available:
                pytest.skip(f"Skipping test - {missing_info['reason']}")
    
    
    # Platform-specific skips
    if "windows_only" in item.keywords and not is_windows():
        pytest.skip("Skipping Windows-only test on non-Windows platform")
    
    if "macos_only" in item.keywords and not is_macos():
        pytest.skip("Skipping macOS-only test on non-macOS platform")
    
    if "linux_only" in item.keywords and not is_linux():
        pytest.skip("Skipping Linux-only test on non-Linux platform")