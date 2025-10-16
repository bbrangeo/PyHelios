"""
Ctypes wrapper for SkyViewFactorModel C++ bindings.

This module provides low-level ctypes bindings to interface with 
the native Helios SkyViewFactorModel plugin via the C++ wrapper layer.
"""

import ctypes
from typing import List, Tuple, Optional

from ..plugins import helios_lib
from ..exceptions import check_helios_error

# Define the USkyViewFactorModel struct
class USkyViewFactorModel(ctypes.Structure):
    pass

# Define the USkyViewFactorCamera struct
class USkyViewFactorCamera(ctypes.Structure):
    pass

# Import UContext from main wrapper to avoid type conflicts
from .UContextWrapper import UContext

# Error checking callback
def _check_error(result, func, args):
    """
    Errcheck callback that automatically checks for Helios errors after each SkyViewFactorModel function call.
    This ensures that C++ exceptions are properly converted to Python exceptions.
    """
    check_helios_error(helios_lib.getLastErrorCode, helios_lib.getLastErrorMessage)
    return result

# Try to set up SkyViewFactorModel function prototypes
try:
    # SkyViewFactorModel creation and destruction
    helios_lib.createSkyViewFactorModel.argtypes = [ctypes.POINTER(UContext)]
    helios_lib.createSkyViewFactorModel.restype = ctypes.POINTER(USkyViewFactorModel)

    helios_lib.destroySkyViewFactorModel.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.destroySkyViewFactorModel.restype = None

    # Message control
    helios_lib.disableSkyViewFactorMessages.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.disableSkyViewFactorMessages.restype = None

    helios_lib.enableSkyViewFactorMessages.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.enableSkyViewFactorMessages.restype = None

    # Ray count configuration
    helios_lib.setSkyViewFactorRayCount.argtypes = [ctypes.POINTER(USkyViewFactorModel), ctypes.c_uint]
    helios_lib.setSkyViewFactorRayCount.restype = None

    helios_lib.getSkyViewFactorRayCount.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.getSkyViewFactorRayCount.restype = ctypes.c_uint

    # Ray length configuration
    helios_lib.setSkyViewFactorMaxRayLength.argtypes = [ctypes.POINTER(USkyViewFactorModel), ctypes.c_float]
    helios_lib.setSkyViewFactorMaxRayLength.restype = None

    helios_lib.getSkyViewFactorMaxRayLength.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.getSkyViewFactorMaxRayLength.restype = ctypes.c_float

    # Single point calculation
    helios_lib.calculateSkyViewFactor.argtypes = [ctypes.POINTER(USkyViewFactorModel), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.calculateSkyViewFactor.restype = ctypes.c_float

    helios_lib.calculateSkyViewFactorCPU.argtypes = [ctypes.POINTER(USkyViewFactorModel), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.calculateSkyViewFactorCPU.restype = ctypes.c_float

    # Multiple points calculation
    helios_lib.calculateSkyViewFactors.argtypes = [ctypes.POINTER(USkyViewFactorModel), 
                                                   ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
                                                   ctypes.POINTER(ctypes.c_float)]
    helios_lib.calculateSkyViewFactors.restype = None

    # Primitive centers calculation
    helios_lib.calculateSkyViewFactorsForPrimitives.argtypes = [ctypes.POINTER(USkyViewFactorModel),
                                                               ctypes.POINTER(ctypes.c_float)]
    helios_lib.calculateSkyViewFactorsForPrimitives.restype = ctypes.c_size_t

    # Export/Import functionality
    helios_lib.exportSkyViewFactors.argtypes = [ctypes.POINTER(USkyViewFactorModel), ctypes.c_char_p]
    helios_lib.exportSkyViewFactors.restype = ctypes.c_bool

    helios_lib.loadSkyViewFactors.argtypes = [ctypes.POINTER(USkyViewFactorModel), ctypes.c_char_p]
    helios_lib.loadSkyViewFactors.restype = ctypes.c_bool

    # Get results
    helios_lib.getSkyViewFactors.argtypes = [ctypes.POINTER(USkyViewFactorModel), ctypes.POINTER(ctypes.c_size_t)]
    helios_lib.getSkyViewFactors.restype = ctypes.POINTER(ctypes.c_float)

    # Statistics
    helios_lib.getSkyViewFactorStatistics.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.getSkyViewFactorStatistics.restype = ctypes.c_char_p

    # CUDA/OptiX availability
    helios_lib.isSkyViewFactorCudaAvailable.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.isSkyViewFactorCudaAvailable.restype = ctypes.c_bool

    helios_lib.isSkyViewFactorOptiXAvailable.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.isSkyViewFactorOptiXAvailable.restype = ctypes.c_bool

    # Reset functionality
    helios_lib.resetSkyViewFactorModel.argtypes = [ctypes.POINTER(USkyViewFactorModel)]
    helios_lib.resetSkyViewFactorModel.restype = None

    # SkyViewFactorCamera functions
    helios_lib.createSkyViewFactorCamera.argtypes = [ctypes.POINTER(UContext)]
    helios_lib.createSkyViewFactorCamera.restype = ctypes.POINTER(USkyViewFactorCamera)

    helios_lib.destroySkyViewFactorCamera.argtypes = [ctypes.POINTER(USkyViewFactorCamera)]
    helios_lib.destroySkyViewFactorCamera.restype = None

    # Camera configuration
    helios_lib.setSkyViewFactorCameraPosition.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.setSkyViewFactorCameraPosition.restype = None

    helios_lib.setSkyViewFactorCameraTarget.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.setSkyViewFactorCameraTarget.restype = None

    helios_lib.setSkyViewFactorCameraUp.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.setSkyViewFactorCameraUp.restype = None

    helios_lib.setSkyViewFactorCameraFieldOfView.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_float]
    helios_lib.setSkyViewFactorCameraFieldOfView.restype = None

    helios_lib.setSkyViewFactorCameraResolution.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_uint, ctypes.c_uint]
    helios_lib.setSkyViewFactorCameraResolution.restype = None

    helios_lib.setSkyViewFactorCameraRayCount.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_uint]
    helios_lib.setSkyViewFactorCameraRayCount.restype = None

    helios_lib.setSkyViewFactorCameraMaxRayLength.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_float]
    helios_lib.setSkyViewFactorCameraMaxRayLength.restype = None

    # Camera rendering
    helios_lib.renderSkyViewFactorCamera.argtypes = [ctypes.POINTER(USkyViewFactorCamera)]
    helios_lib.renderSkyViewFactorCamera.restype = ctypes.c_bool

    # Camera results
    helios_lib.getSkyViewFactorCameraImage.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.POINTER(ctypes.c_size_t)]
    helios_lib.getSkyViewFactorCameraImage.restype = ctypes.POINTER(ctypes.c_float)

    helios_lib.getSkyViewFactorCameraPixelValue.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_uint, ctypes.c_uint]
    helios_lib.getSkyViewFactorCameraPixelValue.restype = ctypes.c_float

    helios_lib.exportSkyViewFactorCameraImage.argtypes = [ctypes.POINTER(USkyViewFactorCamera), ctypes.c_char_p]
    helios_lib.exportSkyViewFactorCameraImage.restype = ctypes.c_bool

    # Camera statistics
    helios_lib.getSkyViewFactorCameraStatistics.argtypes = [ctypes.POINTER(USkyViewFactorCamera)]
    helios_lib.getSkyViewFactorCameraStatistics.restype = ctypes.c_char_p

    # Camera reset
    helios_lib.resetSkyViewFactorCamera.argtypes = [ctypes.POINTER(USkyViewFactorCamera)]
    helios_lib.resetSkyViewFactorCamera.restype = None

    # Add automatic error checking to all SkyViewFactorModel functions
    helios_lib.createSkyViewFactorModel.errcheck = _check_error
    # Note: destroySkyViewFactorModel doesn't need errcheck as it doesn't fail

    # Message control
    helios_lib.disableSkyViewFactorMessages.errcheck = _check_error
    helios_lib.enableSkyViewFactorMessages.errcheck = _check_error

    # Ray count configuration
    helios_lib.setSkyViewFactorRayCount.errcheck = _check_error
    helios_lib.getSkyViewFactorRayCount.errcheck = _check_error

    # Ray length configuration
    helios_lib.setSkyViewFactorMaxRayLength.errcheck = _check_error
    helios_lib.getSkyViewFactorMaxRayLength.errcheck = _check_error

    # Calculation functions
    helios_lib.calculateSkyViewFactor.errcheck = _check_error
    helios_lib.calculateSkyViewFactors.errcheck = _check_error
    helios_lib.calculateSkyViewFactorsForPrimitives.errcheck = _check_error

    # Export/Import functions
    helios_lib.exportSkyViewFactors.errcheck = _check_error
    helios_lib.loadSkyViewFactors.errcheck = _check_error

    # Results and statistics
    helios_lib.getSkyViewFactors.errcheck = _check_error
    helios_lib.getSkyViewFactorStatistics.errcheck = _check_error

    # CUDA/OptiX availability
    helios_lib.isSkyViewFactorCudaAvailable.errcheck = _check_error
    helios_lib.isSkyViewFactorOptiXAvailable.errcheck = _check_error

    # Reset functionality
    helios_lib.resetSkyViewFactorModel.errcheck = _check_error

    # Camera functions
    helios_lib.createSkyViewFactorCamera.errcheck = _check_error
    helios_lib.destroySkyViewFactorCamera.errcheck = _check_error

    # Camera configuration
    helios_lib.setSkyViewFactorCameraPosition.errcheck = _check_error
    helios_lib.setSkyViewFactorCameraTarget.errcheck = _check_error
    helios_lib.setSkyViewFactorCameraUp.errcheck = _check_error
    helios_lib.setSkyViewFactorCameraFieldOfView.errcheck = _check_error
    helios_lib.setSkyViewFactorCameraResolution.errcheck = _check_error
    helios_lib.setSkyViewFactorCameraRayCount.errcheck = _check_error
    helios_lib.setSkyViewFactorCameraMaxRayLength.errcheck = _check_error

    # Camera rendering and results
    helios_lib.renderSkyViewFactorCamera.errcheck = _check_error
    helios_lib.getSkyViewFactorCameraImage.errcheck = _check_error
    helios_lib.getSkyViewFactorCameraPixelValue.errcheck = _check_error
    helios_lib.exportSkyViewFactorCameraImage.errcheck = _check_error
    helios_lib.getSkyViewFactorCameraStatistics.errcheck = _check_error
    helios_lib.resetSkyViewFactorCamera.errcheck = _check_error

    # Mark that SkyViewFactorModel functions are available
    _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE = True

except AttributeError:
    # SkyViewFactorModel functions not available in current native library
    _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE = False

# Python wrapper functions

def createSkyViewFactorModel(context):
    """Create a new SkyViewFactorModel instance"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        return None  # Return None for mock mode
    return helios_lib.createSkyViewFactorModel(context)

def destroySkyViewFactorModel(skyviewfactor_model):
    """Destroy SkyViewFactorModel instance"""
    if skyviewfactor_model is None:
        return  # Destroying None is acceptable - no-op
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.destroySkyViewFactorModel(skyviewfactor_model)

def disableMessages(skyviewfactor_model):
    """Disable console output for SkyViewFactorModel"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.disableSkyViewFactorMessages(skyviewfactor_model)

def enableMessages(skyviewfactor_model):
    """Enable console output for SkyViewFactorModel"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.enableSkyViewFactorMessages(skyviewfactor_model)

def setRayCount(skyviewfactor_model, ray_count):
    """Set the number of rays for sky view factor calculation"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorRayCount(skyviewfactor_model, ray_count)

def getRayCount(skyviewfactor_model):
    """Get the current number of rays"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.getSkyViewFactorRayCount(skyviewfactor_model)

def setMaxRayLength(skyviewfactor_model, max_length):
    """Set the maximum ray length for intersection testing"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorMaxRayLength(skyviewfactor_model, max_length)

def getMaxRayLength(skyviewfactor_model):
    """Get the maximum ray length"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.getSkyViewFactorMaxRayLength(skyviewfactor_model)

def calculateSkyViewFactor(skyviewfactor_model, x, y, z):
    """Calculate sky view factor for a single point"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.calculateSkyViewFactor(skyviewfactor_model, x, y, z)

def calculateSkyViewFactorCPU(skyviewfactor_model, x, y, z):
    """Calculate sky view factor for a single point using CPU implementation"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.calculateSkyViewFactorCPU(skyviewfactor_model, x, y, z)

def calculateSkyViewFactors(skyviewfactor_model, points):
    """Calculate sky view factors for multiple points"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    
    if not points:
        return []
    
    # Convert points to C arrays
    num_points = len(points)
    points_array = (ctypes.c_float * (3 * num_points))()
    
    for i, point in enumerate(points):
        points_array[3*i] = point[0]
        points_array[3*i + 1] = point[1]
        points_array[3*i + 2] = point[2]
    
    # Create output array
    results_array = (ctypes.c_float * num_points)()
    
    # Call C++ function
    helios_lib.calculateSkyViewFactors(skyviewfactor_model, points_array, num_points, results_array)
    
    # Convert back to Python list
    return [results_array[i] for i in range(num_points)]

def calculateSkyViewFactorsForPrimitives(skyviewfactor_model):
    """Calculate sky view factors for all primitive centers"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    
    # Get number of primitives
    num_primitives = helios_lib.calculateSkyViewFactorsForPrimitives(skyviewfactor_model, None)
    
    if num_primitives == 0:
        return []
    
    # Create output array
    results_array = (ctypes.c_float * num_primitives)()
    
    # Call C++ function
    helios_lib.calculateSkyViewFactorsForPrimitives(skyviewfactor_model, results_array)
    
    # Convert back to Python list
    return [results_array[i] for i in range(num_primitives)]

def exportSkyViewFactors(skyviewfactor_model, filename):
    """Export sky view factors to file"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.exportSkyViewFactors(skyviewfactor_model, filename.encode('utf-8'))

def loadSkyViewFactors(skyviewfactor_model, filename):
    """Load sky view factors from file"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.loadSkyViewFactors(skyviewfactor_model, filename.encode('utf-8'))

def getSkyViewFactors(skyviewfactor_model):
    """Get the last calculated sky view factors"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    
    # Get array size
    size = ctypes.c_size_t()
    results_ptr = helios_lib.getSkyViewFactors(skyviewfactor_model, ctypes.byref(size))
    
    if results_ptr is None or size.value == 0:
        return []
    
    # Convert to Python list
    results = []
    for i in range(size.value):
        results.append(results_ptr[i])
    
    return results

def getStatistics(skyviewfactor_model):
    """Get statistics about the last calculation"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    
    stats_ptr = helios_lib.getSkyViewFactorStatistics(skyviewfactor_model)
    if stats_ptr is None:
        return ""
    
    return stats_ptr.decode('utf-8')

def isCudaAvailable(skyviewfactor_model):
    """Check if CUDA is available"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        return False
    return helios_lib.isSkyViewFactorCudaAvailable(skyviewfactor_model)

def isOptiXAvailable(skyviewfactor_model):
    """Check if OptiX is available"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        return False
    return helios_lib.isSkyViewFactorOptiXAvailable(skyviewfactor_model)

def reset(skyviewfactor_model):
    """Reset all calculated data"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorModel functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.resetSkyViewFactorModel(skyviewfactor_model)

# Camera wrapper functions

def createSkyViewFactorCamera(context):
    """Create a new SkyViewFactorCamera instance"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        return None  # Return None for mock mode
    return helios_lib.createSkyViewFactorCamera(context)

def destroySkyViewFactorCamera(camera):
    """Destroy SkyViewFactorCamera instance"""
    if camera is None:
        return  # Destroying None is acceptable - no-op
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.destroySkyViewFactorCamera(camera)

def setCameraPosition(camera, x, y, z):
    """Set camera position"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorCameraPosition(camera, x, y, z)

def setCameraTarget(camera, x, y, z):
    """Set camera target"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorCameraTarget(camera, x, y, z)

def setCameraUp(camera, x, y, z):
    """Set camera up vector"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorCameraUp(camera, x, y, z)

def setCameraFieldOfView(camera, fov):
    """Set camera field of view in degrees"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorCameraFieldOfView(camera, fov)

def setCameraResolution(camera, width, height):
    """Set camera resolution"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorCameraResolution(camera, width, height)

def setCameraRayCount(camera, ray_count):
    """Set number of rays per pixel"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorCameraRayCount(camera, ray_count)

def setCameraMaxRayLength(camera, max_length):
    """Set maximum ray length for camera"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.setSkyViewFactorCameraMaxRayLength(camera, max_length)

def renderCamera(camera):
    """Render sky view factor image"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.renderSkyViewFactorCamera(camera)

def getCameraImage(camera):
    """Get sky view factor image as list of values"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    
    # Get array size
    size = ctypes.c_size_t()
    results_ptr = helios_lib.getSkyViewFactorCameraImage(camera, ctypes.byref(size))
    
    if results_ptr is None or size.value == 0:
        return []
    
    # Convert to Python list
    results = []
    for i in range(size.value):
        results.append(results_ptr[i])
    
    return results

def getCameraPixelValue(camera, x, y):
    """Get sky view factor value at specific pixel"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.getSkyViewFactorCameraPixelValue(camera, x, y)

def exportCameraImage(camera, filename):
    """Export camera image to file"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    return helios_lib.exportSkyViewFactorCameraImage(camera, filename.encode('utf-8'))

def getCameraStatistics(camera):
    """Get camera rendering statistics"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    
    stats_ptr = helios_lib.getSkyViewFactorCameraStatistics(camera)
    if stats_ptr is None:
        return ""
    
    return stats_ptr.decode('utf-8')

def resetCamera(camera):
    """Reset camera data"""
    if not _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("SkyViewFactorCamera functions are not available. Native library missing or skyviewfactor plugin not enabled.")
    helios_lib.resetSkyViewFactorCamera(camera)

# Check if functions are available
def areSkyViewFactorFunctionsAvailable():
    """Check if SkyViewFactor functions are available in the native library"""
    return _SKYVIEWFACTOR_MODEL_FUNCTIONS_AVAILABLE
