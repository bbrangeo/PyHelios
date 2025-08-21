"""
Ctypes wrapper for Visualizer C++ bindings.

This module provides low-level ctypes bindings to interface with 
the native Helios Visualizer plugin via the C++ wrapper layer.
"""

import ctypes
from typing import List, Optional

from ..plugins import helios_lib
from ..exceptions import check_helios_error

# Define the UVisualizer struct
class UVisualizer(ctypes.Structure):
    pass

# Import UContext from main wrapper to avoid type conflicts
from .UContextWrapper import UContext

# Try to set up Visualizer function prototypes
try:
    # Visualizer creation and destruction
    helios_lib.createVisualizer.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_bool]
    helios_lib.createVisualizer.restype = ctypes.POINTER(UVisualizer)

    helios_lib.createVisualizerWithAntialiasing.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_bool]
    helios_lib.createVisualizerWithAntialiasing.restype = ctypes.POINTER(UVisualizer)

    helios_lib.destroyVisualizer.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.destroyVisualizer.restype = None

    # Context geometry building
    helios_lib.buildContextGeometry.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(UContext)]
    helios_lib.buildContextGeometry.restype = None

    helios_lib.buildContextGeometryUUIDs.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(UContext), ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t]
    helios_lib.buildContextGeometryUUIDs.restype = None

    # Visualization functions
    helios_lib.plotInteractive.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.plotInteractive.restype = None

    helios_lib.plotUpdate.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.plotUpdate.restype = None

    helios_lib.printWindow.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p]
    helios_lib.printWindow.restype = None

    helios_lib.closeWindow.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.closeWindow.restype = None

    # Camera control
    helios_lib.setCameraPosition.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setCameraPosition.restype = None

    helios_lib.setCameraPositionSpherical.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setCameraPositionSpherical.restype = None

    # Scene configuration
    helios_lib.setBackgroundColor.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setBackgroundColor.restype = None

    helios_lib.setLightDirection.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setLightDirection.restype = None

    helios_lib.setLightingModel.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_uint32]
    helios_lib.setLightingModel.restype = None

    # Error management functions availability check
    try:
        helios_lib.getLastError.restype = ctypes.c_int
        helios_lib.getLastErrorMessage.restype = ctypes.c_char_p
        helios_lib.clearLastError.restype = None
        _ERROR_MANAGEMENT_AVAILABLE = True
    except AttributeError:
        _ERROR_MANAGEMENT_AVAILABLE = False

    _VISUALIZER_FUNCTIONS_AVAILABLE = True
except AttributeError:
    _VISUALIZER_FUNCTIONS_AVAILABLE = False
    _ERROR_MANAGEMENT_AVAILABLE = False

def _check_for_helios_error():
    """Check for and raise Helios errors if error management is available."""
    if _ERROR_MANAGEMENT_AVAILABLE:
        check_helios_error(helios_lib.getLastError, helios_lib.getLastErrorMessage)

# Wrapper functions

def create_visualizer(width: int, height: int, headless: bool = False) -> Optional[ctypes.POINTER(UVisualizer)]:
    """
    Create a new Visualizer instance.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        headless: Enable headless mode (no window display)
        
    Returns:
        Pointer to UVisualizer or None if not available
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualizer creation fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    visualizer = helios_lib.createVisualizer(
        ctypes.c_uint32(width),
        ctypes.c_uint32(height), 
        ctypes.c_bool(headless)
    )
    _check_for_helios_error()
    
    if not visualizer:
        raise RuntimeError("Failed to create Visualizer")
    
    return visualizer

def create_visualizer_with_antialiasing(width: int, height: int, antialiasing_samples: int, headless: bool = False) -> Optional[ctypes.POINTER(UVisualizer)]:
    """
    Create a new Visualizer instance with antialiasing.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        antialiasing_samples: Number of antialiasing samples
        headless: Enable headless mode (no window display)
        
    Returns:
        Pointer to UVisualizer or None if not available
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualizer creation fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    visualizer = helios_lib.createVisualizerWithAntialiasing(
        ctypes.c_uint32(width),
        ctypes.c_uint32(height),
        ctypes.c_uint32(antialiasing_samples),
        ctypes.c_bool(headless)
    )
    _check_for_helios_error()
    
    if not visualizer:
        raise RuntimeError("Failed to create Visualizer with antialiasing")
    
    return visualizer

def destroy_visualizer(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Destroy a Visualizer instance.
    
    Args:
        visualizer: Pointer to UVisualizer to destroy
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        return  # Silent no-op for cleanup
    
    if visualizer:
        helios_lib.destroyVisualizer(visualizer)
        _check_for_helios_error()

def build_context_geometry(visualizer: ctypes.POINTER(UVisualizer), context: ctypes.POINTER(UContext)) -> None:
    """
    Build Context geometry in the visualizer.
    
    Args:
        visualizer: Pointer to UVisualizer
        context: Pointer to UContext
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If geometry building fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not context:
        raise ValueError("Context pointer is null")
    
    helios_lib.buildContextGeometry(visualizer, context)
    _check_for_helios_error()

def build_context_geometry_uuids(visualizer: ctypes.POINTER(UVisualizer), context: ctypes.POINTER(UContext), uuids: List[int]) -> None:
    """
    Build specific Context geometry UUIDs in the visualizer.
    
    Args:
        visualizer: Pointer to UVisualizer
        context: Pointer to UContext
        uuids: List of primitive UUIDs to visualize
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If geometry building fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not context:
        raise ValueError("Context pointer is null")
    if not uuids:
        raise ValueError("UUIDs list cannot be empty")
    
    # Convert Python list to ctypes array
    uuid_array = (ctypes.c_uint32 * len(uuids))(*uuids)
    
    helios_lib.buildContextGeometryUUIDs(visualizer, context, uuid_array, ctypes.c_size_t(len(uuids)))
    _check_for_helios_error()

def plot_interactive(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Open interactive visualization window.
    
    Args:
        visualizer: Pointer to UVisualizer
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualization fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    helios_lib.plotInteractive(visualizer)
    _check_for_helios_error()

def plot_update(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Update visualization (non-interactive).
    
    Args:
        visualizer: Pointer to UVisualizer
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualization update fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    helios_lib.plotUpdate(visualizer)
    _check_for_helios_error()

def print_window(visualizer: ctypes.POINTER(UVisualizer), filename: str) -> None:
    """
    Save current visualization to image file.
    
    Args:
        visualizer: Pointer to UVisualizer
        filename: Output filename for image
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If image saving fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    filename_encoded = filename.encode('utf-8')
    helios_lib.printWindow(visualizer, filename_encoded)
    _check_for_helios_error()

def close_window(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Close visualization window.
    
    Args:
        visualizer: Pointer to UVisualizer
        
    Raises:
        NotImplementedError: If visualizer functions not available
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    helios_lib.closeWindow(visualizer)
    _check_for_helios_error()

def set_camera_position(visualizer: ctypes.POINTER(UVisualizer), position: List[float], look_at: List[float]) -> None:
    """
    Set camera position using Cartesian coordinates.
    
    Args:
        visualizer: Pointer to UVisualizer
        position: Camera position [x, y, z]
        look_at: Camera look-at point [x, y, z]
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If camera positioning fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if len(position) != 3:
        raise ValueError("Position must be a list of 3 floats [x, y, z]")
    if len(look_at) != 3:
        raise ValueError("Look-at must be a list of 3 floats [x, y, z]")
    
    # Convert Python lists to ctypes arrays
    pos_array = (ctypes.c_float * 3)(*position)
    look_array = (ctypes.c_float * 3)(*look_at)
    
    helios_lib.setCameraPosition(visualizer, pos_array, look_array)
    _check_for_helios_error()

def set_camera_position_spherical(visualizer: ctypes.POINTER(UVisualizer), angle: List[float], look_at: List[float]) -> None:
    """
    Set camera position using spherical coordinates.
    
    Args:
        visualizer: Pointer to UVisualizer
        angle: Camera position [radius, zenith, azimuth]
        look_at: Camera look-at point [x, y, z]
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If camera positioning fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if len(angle) != 3:
        raise ValueError("Angle must be a list of 3 floats [radius, zenith, azimuth]")
    if len(look_at) != 3:
        raise ValueError("Look-at must be a list of 3 floats [x, y, z]")
    
    # Convert Python lists to ctypes arrays
    angle_array = (ctypes.c_float * 3)(*angle)
    look_array = (ctypes.c_float * 3)(*look_at)
    
    helios_lib.setCameraPositionSpherical(visualizer, angle_array, look_array)
    _check_for_helios_error()

def set_background_color(visualizer: ctypes.POINTER(UVisualizer), color: List[float]) -> None:
    """
    Set background color.
    
    Args:
        visualizer: Pointer to UVisualizer
        color: Background color [r, g, b]
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If color setting fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if len(color) != 3:
        raise ValueError("Color must be a list of 3 floats [r, g, b]")
    
    # Convert Python list to ctypes array
    color_array = (ctypes.c_float * 3)(*color)
    
    helios_lib.setBackgroundColor(visualizer, color_array)
    _check_for_helios_error()

def set_light_direction(visualizer: ctypes.POINTER(UVisualizer), direction: List[float]) -> None:
    """
    Set light direction.
    
    Args:
        visualizer: Pointer to UVisualizer
        direction: Light direction vector [x, y, z]
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If light direction setting fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if len(direction) != 3:
        raise ValueError("Direction must be a list of 3 floats [x, y, z]")
    
    # Convert Python list to ctypes array
    dir_array = (ctypes.c_float * 3)(*direction)
    
    helios_lib.setLightDirection(visualizer, dir_array)
    _check_for_helios_error()

def set_lighting_model(visualizer: ctypes.POINTER(UVisualizer), lighting_model: int) -> None:
    """
    Set lighting model.
    
    Args:
        visualizer: Pointer to UVisualizer
        lighting_model: Lighting model (0=NONE, 1=PHONG, 2=PHONG_SHADOWED)
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If lighting model setting fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if lighting_model not in [0, 1, 2]:
        raise ValueError("Lighting model must be 0 (NONE), 1 (PHONG), or 2 (PHONG_SHADOWED)")
    
    helios_lib.setLightingModel(visualizer, ctypes.c_uint32(lighting_model))
    _check_for_helios_error()

# Mock implementations when visualizer is not available
if not _VISUALIZER_FUNCTIONS_AVAILABLE:
    def _mock_function(*args, **kwargs):
        raise RuntimeError(
            "Mock mode: Visualizer plugin not available. "
            "This would perform visualization with native Helios library. "
            "To enable visualizer functionality:\n"
            "1. Build PyHelios with visualizer plugin: build_scripts/build_helios --plugins visualizer\n"
            "2. Ensure OpenGL, GLFW, and graphics dependencies are available\n"
            "3. Rebuild PyHelios with graphics system support"
        )
    
    # Replace all wrapper functions with mock
    create_visualizer = _mock_function
    create_visualizer_with_antialiasing = _mock_function
    build_context_geometry = _mock_function
    build_context_geometry_uuids = _mock_function
    plot_interactive = _mock_function
    plot_update = _mock_function
    print_window = _mock_function
    close_window = _mock_function
    set_camera_position = _mock_function
    set_camera_position_spherical = _mock_function
    set_background_color = _mock_function
    set_light_direction = _mock_function
    set_lighting_model = _mock_function