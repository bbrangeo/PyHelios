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
    # Store original state
    original_dev_mode = dev_utils.is_dev_mode_enabled()
    
    if not is_native_library_available():
        # Enable development mode for tests when native libraries aren't available
        dev_utils.enable_dev_mode()
        yield
        # Clean up after tests - always restore original state
        dev_utils.enable_dev_mode(original_dev_mode)
        # Reset plugin registry to prevent state contamination
        _reset_plugin_registry_if_available()
    else:
        # Native libraries are available, no need for dev mode
        yield
        # Reset plugin registry to prevent state contamination
        _reset_plugin_registry_if_available()


def _reset_plugin_registry_if_available():
    """Reset plugin registry to prevent test contamination."""
    try:
        from pyhelios.plugins.registry import reset_plugin_registry
        reset_plugin_registry()
    except ImportError:
        # Registry module not available, skip reset
        pass


@pytest.fixture(scope="module", autouse=True)
def reset_plugin_state():
    """Reset plugin registry state between test modules to prevent contamination."""
    # Reset at the start of each test module
    _reset_plugin_registry_if_available()
    yield
    # Reset at the end of each test module
    _reset_plugin_registry_if_available()


# No longer skip all tests on non-Windows platforms
# Tests will use mock mode when native libraries aren't available


@pytest.fixture(scope="session")
def check_native_library():
    """Session-scoped fixture to check native library availability."""
    if not is_native_library_available():
        pytest.skip("Native Helios library not available - skipping tests requiring native functionality")


@pytest.fixture(scope="session")
def check_dll():
    """Session-scoped fixture to check native library availability (deprecated: use check_native_library)."""
    import warnings
    warnings.warn(
        "check_dll fixture is deprecated and uses Windows-centric terminology. "
        "Use check_native_library fixture instead for cross-platform clarity.",
        DeprecationWarning,
        stacklevel=2
    )
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
    """Fixture providing a mocked Context for testing without native library dependency."""
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
    """Fixture providing a mocked WeberPennTree for testing without native library dependency."""
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

    # Skip GPU tests when GPU runtime is not available
    if "requires_gpu" in item.keywords:
        from pyhelios.runtime import is_gpu_runtime_available, get_gpu_runtime_info
        if not is_gpu_runtime_available():
            gpu_info = get_gpu_runtime_info()
            error_msg = gpu_info.get('error_message', 'GPU hardware/drivers not available')
            pytest.skip(f"Skipping GPU test - {error_msg}")

    # Platform-specific skips
    if "windows_only" in item.keywords and not is_windows():
        pytest.skip("Skipping Windows-only test on non-Windows platform")

    if "macos_only" in item.keywords and not is_macos():
        pytest.skip("Skipping macOS-only test on non-macOS platform")

    if "linux_only" in item.keywords and not is_linux():
        pytest.skip("Skipping Linux-only test on non-Linux platform")


def example_file_exists(filename):
    """
    Check if an example file exists in the docs/examples/models directory.

    Args:
        filename: Name of the file to check (e.g., "Helios_logo.jpeg")

    Returns:
        bool: True if file exists, False otherwise
    """
    example_path = os.path.join("docs", "examples", "models", filename)
    return os.path.exists(example_path)


def get_example_file_path(filename):
    """
    Get the path to an example file, checking if it exists.

    Args:
        filename: Name of the file (e.g., "Helios_logo.jpeg")

    Returns:
        str: Path to the file if it exists

    Raises:
        pytest.skip: If the file doesn't exist (for wheel environments)
    """
    example_path = os.path.join("docs", "examples", "models", filename)
    if not os.path.exists(example_path):
        pytest.skip(f"Example file not available in wheel environment: {filename}")
    return example_path


def create_dummy_image_file(suffix=".jpeg"):
    """
    Create a minimal dummy image file for testing texture functionality.

    Args:
        suffix: File extension (e.g., ".jpeg", ".png")

    Returns:
        str: Path to the temporary file
    """
    import tempfile

    # Create a minimal JPEG-like file (just headers, won't be valid but tests loading behavior)
    dummy_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9'

    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        os.write(fd, dummy_content)
    finally:
        os.close(fd)

    return path