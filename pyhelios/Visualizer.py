"""
High-level Visualizer interface for PyHelios.

This module provides a user-friendly interface to the 3D visualization
capabilities with graceful plugin handling and informative error messages.
"""

import logging
import os
from pathlib import Path
from contextlib import contextmanager
from typing import List, Optional, Tuple, Union

from .plugins.registry import get_plugin_registry
from .wrappers import UVisualizerWrapper as visualizer_wrapper
from .Context import Context

logger = logging.getLogger(__name__)


@contextmanager
def _visualizer_working_directory():
    """
    Context manager that temporarily changes working directory for visualizer operations.
    
    The C++ visualizer code expects to find assets at 'plugins/visualizer/' relative
    to the current working directory. This context manager ensures the working directory
    is set correctly during visualizer initialization and operations.
    """
    # Find the build directory where assets are located
    current_dir = Path(__file__).parent
    repo_root = current_dir.parent
    build_lib_dir = repo_root / 'pyhelios_build' / 'build' / 'lib'
    
    if not build_lib_dir.exists():
        logger.warning(f"Build directory not found: {build_lib_dir}")
        # Fallback to current directory - may not work but don't break
        yield
        return
    
    # The correct working directory is the parent of 'plugins' directory
    # In the build system, assets are at: pyhelios_build/build/plugins/visualizer/
    # So we need working directory to be: pyhelios_build/build/
    working_dir = build_lib_dir.parent
    
    if not (working_dir / 'plugins' / 'visualizer' / 'shaders').exists():
        logger.warning(f"Visualizer assets not found at: {working_dir / 'plugins' / 'visualizer'}")
        # Continue anyway - may be using source assets or alternative setup
    
    # Change working directory temporarily
    original_cwd = Path.cwd()
    
    try:
        logger.debug(f"Changing working directory from {original_cwd} to {working_dir}")
        os.chdir(working_dir)
        yield
    finally:
        logger.debug(f"Restoring working directory to {original_cwd}")
        os.chdir(original_cwd)


class VisualizerError(Exception):
    """Raised when Visualizer operations fail."""
    pass


class Visualizer:
    """
    High-level interface for 3D visualization and rendering.
    
    This class provides a user-friendly wrapper around the native Helios
    visualizer plugin with automatic plugin availability checking and
    graceful error handling.
    
    The visualizer provides OpenGL-based 3D rendering with interactive controls,
    image export, and comprehensive scene configuration options.
    """
    
    # Lighting model constants
    LIGHTING_NONE = 0
    LIGHTING_PHONG = 1
    LIGHTING_PHONG_SHADOWED = 2
    
    def __init__(self, width: int, height: int, antialiasing_samples: int = 1, headless: bool = False):
        """
        Initialize Visualizer with graceful plugin handling.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            antialiasing_samples: Number of antialiasing samples (default: 1)
            headless: Enable headless mode for offscreen rendering (default: False)
            
        Raises:
            VisualizerError: If visualizer plugin is not available
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        if antialiasing_samples < 1:
            raise ValueError("Antialiasing samples must be at least 1")
        
        self.width = width
        self.height = height
        self.antialiasing_samples = antialiasing_samples
        self.headless = headless
        self.visualizer = None
        
        # Check plugin availability using registry
        registry = get_plugin_registry()
        
        if not registry.is_plugin_available('visualizer'):
            # Get helpful information about the missing plugin
            available_plugins = registry.get_available_plugins()
            
            error_msg = (
                "Visualizer requires the 'visualizer' plugin which is not available.\n\n"
                "The visualizer plugin provides OpenGL-based 3D rendering and visualization.\n"
                "System requirements:\n"
                "- OpenGL 3.3 or higher\n"
                "- GLFW library for window management\n"
                "- FreeType library for text rendering\n"
                "- Display/graphics drivers (X11 on Linux, native on Windows/macOS)\n\n"
                "To enable visualization:\n"
                "1. Build PyHelios with visualizer plugin:\n"
                "   build_scripts/build_helios --plugins visualizer\n"
                f"\nCurrently available plugins: {available_plugins}"
            )
            
            # Add platform-specific installation hints
            import platform
            system = platform.system().lower()
            if 'linux' in system:
                error_msg += (
                    "\n\nLinux installation hints:\n"
                    "- Ubuntu/Debian: sudo apt-get install libx11-dev xorg-dev libgl1-mesa-dev libglu1-mesa-dev\n"
                    "- CentOS/RHEL: sudo yum install libX11-devel mesa-libGL-devel mesa-libGLU-devel"
                )
            elif 'darwin' in system:
                error_msg += (
                    "\n\nmacOS installation hints:\n"
                    "- Install XQuartz: brew install --cask xquartz\n"
                    "- OpenGL should be available by default"
                )
            elif 'windows' in system:
                error_msg += (
                    "\n\nWindows installation hints:\n"
                    "- OpenGL drivers should be provided by graphics card drivers\n"
                    "- Visual Studio runtime may be required"
                )
            
            raise VisualizerError(error_msg)
        
        # Plugin is available - create visualizer with correct working directory
        try:
            with _visualizer_working_directory():
                if antialiasing_samples > 1:
                    self.visualizer = visualizer_wrapper.create_visualizer_with_antialiasing(
                        width, height, antialiasing_samples, headless
                    )
                else:
                    self.visualizer = visualizer_wrapper.create_visualizer(
                        width, height, headless
                    )
                    
                if self.visualizer is None:
                    raise VisualizerError(
                        "Failed to create Visualizer instance. "
                        "This may indicate a problem with graphics drivers or OpenGL initialization."
                    )
                logger.info(f"Visualizer created successfully ({width}x{height}, AA:{antialiasing_samples}, headless:{headless})")
            
        except Exception as e:
            raise VisualizerError(f"Failed to initialize Visualizer: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit with proper cleanup."""
        if self.visualizer is not None:
            try:
                with _visualizer_working_directory():
                    visualizer_wrapper.destroy_visualizer(self.visualizer)
                logger.debug("Visualizer destroyed successfully")
            except Exception as e:
                logger.warning(f"Error destroying Visualizer: {e}")
            finally:
                self.visualizer = None
    
    def buildContextGeometry(self, context: Context, uuids: Optional[List[int]] = None) -> None:
        """
        Build Context geometry in the visualizer.
        
        This method loads geometry from a Helios Context into the visualizer
        for rendering. If no UUIDs are specified, all geometry is loaded.
        
        Args:
            context: Helios Context instance containing geometry
            uuids: Optional list of primitive UUIDs to visualize (default: all)
            
        Raises:
            VisualizerError: If geometry building fails
            ValueError: If parameters are invalid
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        if not isinstance(context, Context):
            raise ValueError("context must be a Context instance")
        
        try:
            with _visualizer_working_directory():
                if uuids is None:
                    # Load all geometry
                    visualizer_wrapper.build_context_geometry(self.visualizer, context.getNativePtr())
                    logger.debug("Built all Context geometry in visualizer")
                else:
                    # Load specific UUIDs
                    if not uuids:
                        raise ValueError("UUIDs list cannot be empty")
                    visualizer_wrapper.build_context_geometry_uuids(
                        self.visualizer, context.getNativePtr(), uuids
                    )
                    logger.debug(f"Built {len(uuids)} primitives in visualizer")
                
        except Exception as e:
            raise VisualizerError(f"Failed to build Context geometry: {e}")
    
    def plotInteractive(self) -> None:
        """
        Open interactive visualization window.
        
        This method opens a window with the current scene and allows user
        interaction (camera rotation, zooming, etc.). The program will pause
        until the window is closed by the user.
        
        Interactive controls:
        - Mouse scroll: Zoom in/out
        - Left mouse + drag: Rotate camera
        - Right mouse + drag: Pan camera
        - Arrow keys: Camera movement
        - +/- keys: Zoom in/out
        
        Raises:
            VisualizerError: If visualization fails
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        try:
            with _visualizer_working_directory():
                visualizer_wrapper.plot_interactive(self.visualizer)
                logger.debug("Interactive visualization completed")
        except Exception as e:
            raise VisualizerError(f"Interactive visualization failed: {e}")
    
    def plotUpdate(self) -> None:
        """
        Update visualization (non-interactive).
        
        This method updates the visualization window without user interaction.
        The program continues immediately after rendering. Useful for batch
        processing or creating image sequences.
        
        Raises:
            VisualizerError: If visualization update fails
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        try:
            with _visualizer_working_directory():
                visualizer_wrapper.plot_update(self.visualizer)
            logger.debug("Visualization updated")
        except Exception as e:
            raise VisualizerError(f"Visualization update failed: {e}")
    
    def printWindow(self, filename: str) -> None:
        """
        Save current visualization to image file.
        
        This method exports the current visualization to an image file.
        Supported formats are determined by the native implementation
        (typically JPEG).
        
        Args:
            filename: Output filename for image (should include .jpg extension)
            
        Raises:
            VisualizerError: If image saving fails
            ValueError: If filename is invalid
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        try:
            with _visualizer_working_directory():
                visualizer_wrapper.print_window(self.visualizer, filename)
            logger.debug(f"Visualization saved to {filename}")
        except Exception as e:
            raise VisualizerError(f"Failed to save image: {e}")
    
    def closeWindow(self) -> None:
        """
        Close visualization window.
        
        This method closes any open visualization window. It's safe to call
        even if no window is open.
        
        Raises:
            VisualizerError: If window closing fails
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        try:
            visualizer_wrapper.close_window(self.visualizer)
            logger.debug("Visualization window closed")
        except Exception as e:
            raise VisualizerError(f"Failed to close window: {e}")
    
    def setCameraPosition(self, position: Union[List[float], Tuple[float, float, float]], 
                         lookAt: Union[List[float], Tuple[float, float, float]]) -> None:
        """
        Set camera position using Cartesian coordinates.
        
        Args:
            position: Camera position [x, y, z] in world coordinates
            lookAt: Camera look-at point [x, y, z] in world coordinates
            
        Raises:
            VisualizerError: If camera positioning fails
            ValueError: If parameters are invalid
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        # Validate and convert parameters
        if len(position) != 3:
            raise ValueError("Position must have 3 elements [x, y, z]")
        if len(lookAt) != 3:
            raise ValueError("LookAt must have 3 elements [x, y, z]")
        
        position_list = list(position)
        lookAt_list = list(lookAt)
        
        try:
            visualizer_wrapper.set_camera_position(self.visualizer, position_list, lookAt_list)
            logger.debug(f"Camera position set to {position}, looking at {lookAt}")
        except Exception as e:
            raise VisualizerError(f"Failed to set camera position: {e}")
    
    def setCameraPositionSpherical(self, angle: Union[List[float], Tuple[float, float, float]], 
                                  lookAt: Union[List[float], Tuple[float, float, float]]) -> None:
        """
        Set camera position using spherical coordinates.
        
        Args:
            angle: Camera position [radius, zenith, azimuth] in spherical coordinates
            lookAt: Camera look-at point [x, y, z] in world coordinates
            
        Raises:
            VisualizerError: If camera positioning fails
            ValueError: If parameters are invalid
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        # Validate and convert parameters
        if len(angle) != 3:
            raise ValueError("Angle must have 3 elements [radius, zenith, azimuth]")
        if len(lookAt) != 3:
            raise ValueError("LookAt must have 3 elements [x, y, z]")
        
        angle_list = list(angle)
        lookAt_list = list(lookAt)
        
        try:
            visualizer_wrapper.set_camera_position_spherical(self.visualizer, angle_list, lookAt_list)
            logger.debug(f"Camera position set to spherical {angle}, looking at {lookAt}")
        except Exception as e:
            raise VisualizerError(f"Failed to set camera position (spherical): {e}")
    
    def setBackgroundColor(self, color: Union[List[float], Tuple[float, float, float]]) -> None:
        """
        Set background color.
        
        Args:
            color: Background color [r, g, b] with values in range [0, 1]
            
        Raises:
            VisualizerError: If color setting fails
            ValueError: If color values are invalid
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        # Validate parameters
        if len(color) != 3:
            raise ValueError("Color must have 3 elements [r, g, b]")
        
        color_list = list(color)
        
        # Validate color range
        for i, c in enumerate(color_list):
            if not 0 <= c <= 1:
                raise ValueError(f"Color component {i} ({c}) must be in range [0, 1]")
        
        try:
            visualizer_wrapper.set_background_color(self.visualizer, color_list)
            logger.debug(f"Background color set to {color}")
        except Exception as e:
            raise VisualizerError(f"Failed to set background color: {e}")
    
    def setLightDirection(self, direction: Union[List[float], Tuple[float, float, float]]) -> None:
        """
        Set light direction.
        
        Args:
            direction: Light direction vector [x, y, z] (will be normalized)
            
        Raises:
            VisualizerError: If light direction setting fails
            ValueError: If direction is invalid
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        # Validate parameters
        if len(direction) != 3:
            raise ValueError("Direction must have 3 elements [x, y, z]")
        
        direction_list = list(direction)
        
        # Check for zero vector
        if all(d == 0 for d in direction_list):
            raise ValueError("Light direction cannot be zero vector")
        
        try:
            visualizer_wrapper.set_light_direction(self.visualizer, direction_list)
            logger.debug(f"Light direction set to {direction}")
        except Exception as e:
            raise VisualizerError(f"Failed to set light direction: {e}")
    
    def setLightingModel(self, lighting_model: Union[int, str]) -> None:
        """
        Set lighting model.
        
        Args:
            lighting_model: Lighting model, either:
                - 0 or "none": No lighting
                - 1 or "phong": Phong shading
                - 2 or "phong_shadowed": Phong shading with shadows
            
        Raises:
            VisualizerError: If lighting model setting fails
            ValueError: If lighting model is invalid
        """
        if self.visualizer is None:
            raise VisualizerError("Visualizer has been destroyed")
        
        # Convert string to integer if needed
        if isinstance(lighting_model, str):
            lighting_model_lower = lighting_model.lower()
            if lighting_model_lower in ['none', 'no', 'off']:
                lighting_model = self.LIGHTING_NONE
            elif lighting_model_lower in ['phong', 'phong_lighting']:
                lighting_model = self.LIGHTING_PHONG
            elif lighting_model_lower in ['phong_shadowed', 'phong_shadows', 'shadowed']:
                lighting_model = self.LIGHTING_PHONG_SHADOWED
            else:
                raise ValueError(f"Unknown lighting model string: {lighting_model}")
        
        # Validate integer value
        if lighting_model not in [self.LIGHTING_NONE, self.LIGHTING_PHONG, self.LIGHTING_PHONG_SHADOWED]:
            raise ValueError(f"Lighting model must be 0 (NONE), 1 (PHONG), or 2 (PHONG_SHADOWED), got {lighting_model}")
        
        try:
            visualizer_wrapper.set_lighting_model(self.visualizer, lighting_model)
            model_names = {0: "NONE", 1: "PHONG", 2: "PHONG_SHADOWED"}
            logger.debug(f"Lighting model set to {model_names.get(lighting_model, lighting_model)}")
        except Exception as e:
            raise VisualizerError(f"Failed to set lighting model: {e}")
    
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        if hasattr(self, 'visualizer') and self.visualizer is not None:
            try:
                with _visualizer_working_directory():
                    visualizer_wrapper.destroy_visualizer(self.visualizer)
            except Exception:
                pass  # Ignore errors during destruction