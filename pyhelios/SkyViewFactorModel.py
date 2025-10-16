"""
High-level SkyViewFactorModel interface for PyHelios.

This module provides a user-friendly interface to the sky view factor modeling
capabilities with graceful plugin handling and informative error messages.
"""

import logging
from typing import List, Optional, Tuple, Union
from contextlib import contextmanager
from pathlib import Path
import os

from .plugins.registry import (
    get_plugin_registry,
    require_plugin,
    graceful_plugin_fallback,
)
from .wrappers import USkyViewFactorModelWrapper as skyviewfactor_wrapper
from .validation.plugins import (
    validate_ray_count,
    validate_direction_vector,
)
from .validation.files import validate_file_path
from .Context import Context
from .assets import get_asset_manager

logger = logging.getLogger(__name__)


@contextmanager
def _skyviewfactor_working_directory():
    """
    Context manager that temporarily changes working directory to where SkyViewFactorModel assets are located.

    SkyViewFactorModel C++ code uses hardcoded relative paths expecting assets relative to working directory.
    This manager temporarily changes to the build directory where assets are actually located.

    Raises:
        RuntimeError: If build directory or SkyViewFactorModel assets are not found, indicating a build system error.
    """
    # Find the build directory containing SkyViewFactorModel assets
    # Try asset manager first (works for both development and wheel installations)
    asset_manager = get_asset_manager()
    working_dir = asset_manager._get_helios_build_path()

    if working_dir and working_dir.exists():
        skyviewfactor_assets = working_dir / "plugins" / "skyviewfactor"
    else:
        # For wheel installations, check packaged assets
        current_dir = Path(__file__).parent
        packaged_build = current_dir / "assets" / "build"

        if packaged_build.exists():
            working_dir = packaged_build
            skyviewfactor_assets = working_dir / "plugins" / "skyviewfactor"
        else:
            # Fallback to development paths
            repo_root = current_dir.parent
            build_lib_dir = repo_root / "pyhelios_build" / "build" / "lib"
            working_dir = build_lib_dir.parent
            skyviewfactor_assets = working_dir / "plugins" / "skyviewfactor"

            if not build_lib_dir.exists():
                raise RuntimeError(
                    f"PyHelios build directory not found at {build_lib_dir}. "
                    f"Run: python build_scripts/build_helios.py --plugins skyviewfactor"
                )

    if not skyviewfactor_assets.exists():
        raise RuntimeError(
            f"SkyViewFactorModel assets not found at {skyviewfactor_assets}. "
            f"This indicates a build system error. The build script should copy PTX files to this location."
        )

    # Change to the build directory temporarily
    original_dir = os.getcwd()
    try:
        os.chdir(working_dir)
        logger.debug(
            f"Changed working directory to {working_dir} for SkyViewFactorModel asset access"
        )
        yield working_dir
    finally:
        os.chdir(original_dir)
        logger.debug(f"Restored working directory to {original_dir}")


class SkyViewFactorModelError(Exception):
    """Raised when SkyViewFactorModel operations fail."""

    pass


class SkyViewFactorCamera:
    """
    Sky View Factor Camera for visualization and analysis.

    This class provides functionality to visualize sky view factors
    using camera-based rendering techniques.
    """

    def __init__(self, context: Context):
        """
        Initialize SkyViewFactorCamera.

        Args:
            context: HELIOS context containing the 3D scene
        """
        self.context = context
        self._camera_ptr = None
        self._is_rendered = False

        # Camera parameters
        self._position = (0.0, 0.0, 10.0)
        self._target = (0.0, 0.0, 0.0)
        self._up = (0.0, 1.0, 0.0)
        self._field_of_view = 60.0
        self._resolution = (512, 512)
        self._ray_count = 100
        self._max_ray_length = 1000.0

        # Results
        self._image_data = []
        self._statistics = ""

        # Initialize camera
        self._initialize_camera()

    def _initialize_camera(self):
        """Initialize the native camera object."""
        try:
            self._camera_ptr = skyviewfactor_wrapper.createSkyViewFactorCamera(
                self.context.context
            )
            if self._camera_ptr is None:
                raise SkyViewFactorModelError("Failed to create SkyViewFactorCamera")
        except Exception as e:
            raise SkyViewFactorModelError(
                f"Failed to initialize SkyViewFactorCamera: {e}"
            )

    def __del__(self):
        """Clean up camera resources."""
        if self._camera_ptr is not None:
            try:
                skyviewfactor_wrapper.destroySkyViewFactorCamera(self._camera_ptr)
            except:
                pass  # Ignore errors during cleanup

    def set_position(self, x: float, y: float, z: float):
        """Set camera position."""
        self._position = (x, y, z)
        skyviewfactor_wrapper.setCameraPosition(self._camera_ptr, x, y, z)

    def set_target(self, x: float, y: float, z: float):
        """Set camera target."""
        self._target = (x, y, z)
        skyviewfactor_wrapper.setCameraTarget(self._camera_ptr, x, y, z)

    def set_up(self, x: float, y: float, z: float):
        """Set camera up vector."""
        self._up = (x, y, z)
        skyviewfactor_wrapper.setCameraUp(self._camera_ptr, x, y, z)

    def set_field_of_view(self, fov: float):
        """Set field of view in degrees."""
        if fov <= 0 or fov >= 180:
            raise ValueError("Field of view must be between 0 and 180 degrees")
        self._field_of_view = fov
        skyviewfactor_wrapper.setCameraFieldOfView(self._camera_ptr, fov)

    def set_resolution(self, width: int, height: int):
        """Set image resolution."""
        if width <= 0 or height <= 0:
            raise ValueError("Resolution must be positive")
        self._resolution = (width, height)
        skyviewfactor_wrapper.setCameraResolution(self._camera_ptr, width, height)

    def set_ray_count(self, ray_count: int):
        """Set number of rays per pixel."""
        validate_ray_count(ray_count)
        self._ray_count = ray_count
        skyviewfactor_wrapper.setCameraRayCount(self._camera_ptr, ray_count)

    def set_max_ray_length(self, max_length: float):
        """Set maximum ray length."""
        if max_length <= 0:
            raise ValueError("Max ray length must be positive")
        self._max_ray_length = max_length
        skyviewfactor_wrapper.setCameraMaxRayLength(self._camera_ptr, max_length)

    def render(self) -> bool:
        """Render the sky view factor image."""
        try:
            with _skyviewfactor_working_directory():
                success = skyviewfactor_wrapper.renderCamera(self._camera_ptr)
                if success:
                    self._is_rendered = True
                    self._image_data = skyviewfactor_wrapper.getCameraImage(
                        self._camera_ptr
                    )
                    self._statistics = skyviewfactor_wrapper.getCameraStatistics(
                        self._camera_ptr
                    )
                return success
        except Exception as e:
            raise SkyViewFactorModelError(f"Failed to render camera: {e}")

    def get_image(self) -> List[float]:
        """Get the rendered sky view factor image as a list of values."""
        if not self._is_rendered:
            raise SkyViewFactorModelError(
                "Camera must be rendered before getting image data"
            )
        return self._image_data.copy()

    def get_pixel_value(self, x: int, y: int) -> float:
        """Get sky view factor value at specific pixel."""
        if not self._is_rendered:
            raise SkyViewFactorModelError(
                "Camera must be rendered before getting pixel values"
            )
        if x < 0 or x >= self._resolution[0] or y < 0 or y >= self._resolution[1]:
            raise ValueError(
                f"Pixel coordinates ({x}, {y}) out of bounds for resolution {self._resolution}"
            )
        return skyviewfactor_wrapper.getCameraPixelValue(self._camera_ptr, x, y)

    def export_image(self, filename: str) -> bool:
        """Export the rendered image to file."""
        if not self._is_rendered:
            raise SkyViewFactorModelError(
                "Camera must be rendered before exporting image"
            )
        validate_file_path(filename, must_exist=False)
        return skyviewfactor_wrapper.exportCameraImage(self._camera_ptr, filename)

    def get_statistics(self) -> str:
        """Get rendering statistics."""
        return self._statistics

    def reset(self):
        """Reset camera data."""
        skyviewfactor_wrapper.resetCamera(self._camera_ptr)
        self._is_rendered = False
        self._image_data = []
        self._statistics = ""


class SkyViewFactorModel:
    """
    Sky View Factor Model for calculating sky view factors in 3D scenes.

    The sky view factor (SVF) measures the fraction of the sky hemisphere
    visible from a given point, ranging from 0 (completely enclosed) to 1 (completely open).
    """

    def __init__(self, context: Context):
        """
        Initialize SkyViewFactorModel.

        Args:
            context: HELIOS context containing the 3D scene
        """
        self.context = context
        self._model_ptr = None
        self._is_initialized = False

        # Model parameters
        self._ray_count = 1000
        self._max_ray_length = 1000.0
        self._message_flag = True

        # Results
        self._sky_view_factors = []
        self._sample_points = []
        self._statistics = ""

        # Initialize model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the native model object."""
        try:
            self._model_ptr = skyviewfactor_wrapper.createSkyViewFactorModel(
                self.context.context
            )
            if self._model_ptr is None:
                raise SkyViewFactorModelError("Failed to create SkyViewFactorModel")

            # Set default parameters
            self.set_ray_count(self._ray_count)
            self.set_max_ray_length(self._max_ray_length)

            self._is_initialized = True
        except Exception as e:
            raise SkyViewFactorModelError(
                f"Failed to initialize SkyViewFactorModel: {e}"
            )

    def __del__(self):
        """Clean up model resources."""
        if self._model_ptr is not None:
            try:
                skyviewfactor_wrapper.destroySkyViewFactorModel(self._model_ptr)
            except:
                pass  # Ignore errors during cleanup

    def set_ray_count(self, ray_count: int):
        """Set the number of rays for sky view factor calculation."""
        validate_ray_count(ray_count)
        self._ray_count = ray_count
        skyviewfactor_wrapper.setRayCount(self._model_ptr, ray_count)

    def get_ray_count(self) -> int:
        """Get the current number of rays."""
        return skyviewfactor_wrapper.getRayCount(self._model_ptr)

    def set_max_ray_length(self, max_length: float):
        """Set the maximum ray length for intersection testing."""
        if max_length <= 0:
            raise ValueError("Max ray length must be positive")
        self._max_ray_length = max_length
        skyviewfactor_wrapper.setMaxRayLength(self._model_ptr, max_length)

    def get_max_ray_length(self) -> float:
        """Get the maximum ray length."""
        return skyviewfactor_wrapper.getMaxRayLength(self._model_ptr)

    def set_message_flag(self, flag: bool):
        """Enable or disable console output."""
        self._message_flag = flag
        if flag:
            skyviewfactor_wrapper.enableMessages(self._model_ptr)
        else:
            skyviewfactor_wrapper.disableMessages(self._model_ptr)

    def calculate_sky_view_factor(self, x: float, y: float, z: float) -> float:
        """
        Calculate sky view factor for a single point.

        Args:
            x, y, z: 3D coordinates of the point

        Returns:
            Sky view factor value (0-1)
        """
        try:
            with _skyviewfactor_working_directory():
                return skyviewfactor_wrapper.calculateSkyViewFactor(
                    self._model_ptr, x, y, z
                )
        except Exception as e:
            raise SkyViewFactorModelError(f"Failed to calculate sky view factor: {e}")

    def calculate_sky_view_factor_cpu(self, x: float, y: float, z: float) -> float:
        """
        Calculate sky view factor for a single point using CPU implementation.

        Args:
            x, y, z: 3D coordinates of the point

        Returns:
            Sky view factor value (0-1)
        """
        try:
            with _skyviewfactor_working_directory():
                return skyviewfactor_wrapper.calculateSkyViewFactorCPU(
                    self._model_ptr, x, y, z
                )
        except Exception as e:
            raise SkyViewFactorModelError(
                f"Failed to calculate sky view factor (CPU): {e}"
            )

    def calculate_sky_view_factors(
        self, points: List[Tuple[float, float, float]]
    ) -> List[float]:
        """
        Calculate sky view factors for multiple points.

        Args:
            points: List of (x, y, z) tuples representing 3D points

        Returns:
            List of sky view factor values (0-1)
        """
        if not points:
            return []

        try:
            with _skyviewfactor_working_directory():
                results = skyviewfactor_wrapper.calculateSkyViewFactors(
                    self._model_ptr, points
                )
                self._sky_view_factors = results
                self._sample_points = points
                return results
        except Exception as e:
            raise SkyViewFactorModelError(f"Failed to calculate sky view factors: {e}")

    def calculate_sky_view_factors_for_primitives(self) -> List[float]:
        """
        Calculate sky view factors for all primitive centers.

        Returns:
            List of sky view factor values for each primitive
        """
        try:
            with _skyviewfactor_working_directory():
                results = skyviewfactor_wrapper.calculateSkyViewFactorsForPrimitives(
                    self._model_ptr
                )
                self._sky_view_factors = results
                return results
        except Exception as e:
            raise SkyViewFactorModelError(
                f"Failed to calculate sky view factors for primitives: {e}"
            )

    def export_sky_view_factors(self, filename: str) -> bool:
        """
        Export sky view factors to file.

        Args:
            filename: Output filename

        Returns:
            True if successful
        """
        validate_file_path(filename, must_exist=False)
        return skyviewfactor_wrapper.exportSkyViewFactors(self._model_ptr, filename)

    def load_sky_view_factors(self, filename: str) -> bool:
        """
        Load sky view factors from file.

        Args:
            filename: Input filename

        Returns:
            True if successful
        """
        validate_file_path(filename, must_exist=True)
        return skyviewfactor_wrapper.loadSkyViewFactors(self._model_ptr, filename)

    def get_sky_view_factors(self) -> List[float]:
        """Get the last calculated sky view factors."""
        return self._sky_view_factors.copy()

    def get_statistics(self) -> str:
        """Get statistics about the last calculation."""
        return skyviewfactor_wrapper.getStatistics(self._model_ptr)

    def is_cuda_available(self) -> bool:
        """Check if CUDA is available."""
        return skyviewfactor_wrapper.isCudaAvailable(self._model_ptr)

    def is_optix_available(self) -> bool:
        """Check if OptiX is available."""
        return skyviewfactor_wrapper.isOptiXAvailable(self._model_ptr)

    def reset(self):
        """Reset all calculated data."""
        skyviewfactor_wrapper.reset(self._model_ptr)
        self._sky_view_factors = []
        self._sample_points = []
        self._statistics = ""

    def create_camera(self) -> SkyViewFactorCamera:
        """Create a new SkyViewFactorCamera for visualization."""
        return SkyViewFactorCamera(self.context)


# Plugin availability check
def is_skyviewfactor_available() -> bool:
    """Check if SkyViewFactor plugin is available."""
    return skyviewfactor_wrapper.areSkyViewFactorFunctionsAvailable()


# Graceful fallback for when plugin is not available
@graceful_plugin_fallback(
    plugin_name="skyviewfactor",
    warning_message="SkyViewFactor plugin is not available. Install with: python build_scripts/build_helios.py --plugins skyviewfactor",
)
def create_skyviewfactor_model(context: Context) -> SkyViewFactorModel:
    """Create a SkyViewFactorModel instance with plugin availability check."""
    return SkyViewFactorModel(context)
