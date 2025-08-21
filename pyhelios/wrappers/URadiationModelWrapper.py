"""
Ctypes wrapper for RadiationModel C++ bindings.

This module provides low-level ctypes bindings to interface with 
the native Helios RadiationModel plugin via the C++ wrapper layer.
"""

import ctypes
from typing import List

from ..plugins import helios_lib

# Define the URadiationModel struct
class URadiationModel(ctypes.Structure):
    pass

# Import UContext from main wrapper to avoid type conflicts
from .UContextWrapper import UContext

# Try to set up RadiationModel function prototypes
try:
    # RadiationModel creation and destruction
    helios_lib.createRadiationModel.argtypes = [ctypes.POINTER(UContext)]
    helios_lib.createRadiationModel.restype = ctypes.POINTER(URadiationModel)

    helios_lib.destroyRadiationModel.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.destroyRadiationModel.restype = None

    # Message control
    helios_lib.disableRadiationMessages.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.disableRadiationMessages.restype = None

    helios_lib.enableRadiationMessages.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.enableRadiationMessages.restype = None

    # Band management
    helios_lib.addRadiationBand.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.addRadiationBand.restype = None

    helios_lib.addRadiationBandWithWavelengths.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_float, ctypes.c_float]
    helios_lib.addRadiationBandWithWavelengths.restype = None

    helios_lib.copyRadiationBand.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_char_p]
    helios_lib.copyRadiationBand.restype = None

    # Source management  
    helios_lib.addCollimatedRadiationSourceDefault.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.addCollimatedRadiationSourceDefault.restype = ctypes.c_uint

    helios_lib.addCollimatedRadiationSourceVec3.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addCollimatedRadiationSourceVec3.restype = ctypes.c_uint

    helios_lib.addCollimatedRadiationSourceSpherical.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addCollimatedRadiationSourceSpherical.restype = ctypes.c_uint

    helios_lib.addSphereRadiationSource.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addSphereRadiationSource.restype = ctypes.c_uint

    helios_lib.addSunSphereRadiationSource.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addSunSphereRadiationSource.restype = ctypes.c_uint

    # Ray count configuration
    helios_lib.setDirectRayCount.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_size_t]
    helios_lib.setDirectRayCount.restype = None

    helios_lib.setDiffuseRayCount.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_size_t]
    helios_lib.setDiffuseRayCount.restype = None

    # Flux configuration
    helios_lib.setDiffuseRadiationFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_float]
    helios_lib.setDiffuseRadiationFlux.restype = None

    helios_lib.setSourceFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_uint, ctypes.c_char_p, ctypes.c_float]
    helios_lib.setSourceFlux.restype = None

    helios_lib.setSourceFluxMultiple.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t, ctypes.c_char_p, ctypes.c_float]
    helios_lib.setSourceFluxMultiple.restype = None

    helios_lib.getSourceFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_uint, ctypes.c_char_p]
    helios_lib.getSourceFlux.restype = ctypes.c_float

    # Scattering configuration
    helios_lib.setScatteringDepth.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_uint]
    helios_lib.setScatteringDepth.restype = None

    helios_lib.setMinScatterEnergy.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_float]
    helios_lib.setMinScatterEnergy.restype = None

    # Emission control
    helios_lib.disableEmission.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.disableEmission.restype = None

    helios_lib.enableEmission.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.enableEmission.restype = None

    # Geometry and simulation
    helios_lib.updateRadiationGeometry.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.updateRadiationGeometry.restype = None

    helios_lib.updateRadiationGeometryUUIDs.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t]
    helios_lib.updateRadiationGeometryUUIDs.restype = None

    helios_lib.runRadiationBand.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.runRadiationBand.restype = None

    helios_lib.runRadiationBandMultiple.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t]
    helios_lib.runRadiationBandMultiple.restype = None

    # Results and information
    helios_lib.getTotalAbsorbedFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_size_t)]
    helios_lib.getTotalAbsorbedFlux.restype = ctypes.POINTER(ctypes.c_float)

    
    # Mark that RadiationModel functions are available
    _RADIATION_MODEL_FUNCTIONS_AVAILABLE = True

except AttributeError:
    # RadiationModel functions not available in current native library
    _RADIATION_MODEL_FUNCTIONS_AVAILABLE = False

# Python wrapper functions

def createRadiationModel(context):
    """Create a new RadiationModel instance"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        return None  # Return None for mock mode
    return helios_lib.createRadiationModel(context)

def destroyRadiationModel(radiation_model):
    """Destroy RadiationModel instance"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        return  # Destroying None is acceptable - no-op
    helios_lib.destroyRadiationModel(radiation_model)

def disableMessages(radiation_model):
    """Disable RadiationModel status messages"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot disable messages.")
    helios_lib.disableRadiationMessages(radiation_model)

def enableMessages(radiation_model):
    """Enable RadiationModel status messages"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot enable messages.")
    helios_lib.enableRadiationMessages(radiation_model)

def addRadiationBand(radiation_model, label: str):
    """Add radiation band with label"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot add radiation band.")
    label_encoded = label.encode('utf-8')
    helios_lib.addRadiationBand(radiation_model, label_encoded)

def addRadiationBandWithWavelengths(radiation_model, label: str, wavelength_min: float, wavelength_max: float):
    """Add radiation band with wavelength bounds"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot add radiation band.")
    label_encoded = label.encode('utf-8')
    helios_lib.addRadiationBandWithWavelengths(radiation_model, label_encoded, wavelength_min, wavelength_max)

def copyRadiationBand(radiation_model, old_label: str, new_label: str):
    """Copy existing radiation band to new label"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot copy radiation band.")
    old_encoded = old_label.encode('utf-8')
    new_encoded = new_label.encode('utf-8')
    helios_lib.copyRadiationBand(radiation_model, old_encoded, new_encoded)

def addCollimatedRadiationSourceDefault(radiation_model):
    """Add default collimated radiation source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addCollimatedRadiationSourceDefault(radiation_model)

def addCollimatedRadiationSourceVec3(radiation_model, x: float, y: float, z: float):
    """Add collimated radiation source with vec3 direction"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addCollimatedRadiationSourceVec3(radiation_model, x, y, z)

def addCollimatedRadiationSourceSpherical(radiation_model, radius: float, zenith: float, azimuth: float):
    """Add collimated radiation source with spherical direction"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addCollimatedRadiationSourceSpherical(radiation_model, radius, zenith, azimuth)

def addSphereRadiationSource(radiation_model, x: float, y: float, z: float, radius: float):
    """Add spherical radiation source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addSphereRadiationSource(radiation_model, x, y, z, radius)

def addSunSphereRadiationSource(radiation_model, radius: float, zenith: float, azimuth: float, 
                               position_scaling: float, angular_width: float, flux_scaling: float):
    """Add sun sphere radiation source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addSunSphereRadiationSource(radiation_model, radius, zenith, azimuth, 
                                                 position_scaling, angular_width, flux_scaling)

def setDirectRayCount(radiation_model, label: str, count: int):
    """Set direct ray count for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set ray count.")
    label_encoded = label.encode('utf-8')
    helios_lib.setDirectRayCount(radiation_model, label_encoded, count)

def setDiffuseRayCount(radiation_model, label: str, count: int):
    """Set diffuse ray count for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set ray count.")
    label_encoded = label.encode('utf-8')
    helios_lib.setDiffuseRayCount(radiation_model, label_encoded, count)

def setDiffuseRadiationFlux(radiation_model, label: str, flux: float):
    """Set diffuse radiation flux for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set radiation flux.")
    label_encoded = label.encode('utf-8')
    helios_lib.setDiffuseRadiationFlux(radiation_model, label_encoded, flux)

def setSourceFlux(radiation_model, source_id: int, label: str, flux: float):
    """Set source flux for single source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set source flux.")
    label_encoded = label.encode('utf-8')
    helios_lib.setSourceFlux(radiation_model, source_id, label_encoded, flux)

def setSourceFluxMultiple(radiation_model, source_ids: List[int], label: str, flux: float):
    """Set source flux for multiple sources"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set source flux.")
    label_encoded = label.encode('utf-8')
    source_array = (ctypes.c_uint * len(source_ids))(*source_ids)
    helios_lib.setSourceFluxMultiple(radiation_model, source_array, len(source_ids), label_encoded, flux)

def getSourceFlux(radiation_model, source_id: int, label: str) -> float:
    """Get source flux for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot get source flux.")
    label_encoded = label.encode('utf-8')
    return helios_lib.getSourceFlux(radiation_model, source_id, label_encoded)

def setScatteringDepth(radiation_model, label: str, depth: int):
    """Set scattering depth for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set scattering depth.")
    label_encoded = label.encode('utf-8')
    helios_lib.setScatteringDepth(radiation_model, label_encoded, depth)

def setMinScatterEnergy(radiation_model, label: str, energy: float):
    """Set minimum scatter energy for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set scatter energy.")
    label_encoded = label.encode('utf-8')
    helios_lib.setMinScatterEnergy(radiation_model, label_encoded, energy)

def disableEmission(radiation_model, label: str):
    """Disable emission for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot disable emission.")
    label_encoded = label.encode('utf-8')
    helios_lib.disableEmission(radiation_model, label_encoded)

def enableEmission(radiation_model, label: str):
    """Enable emission for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot enable emission.")
    label_encoded = label.encode('utf-8')
    helios_lib.enableEmission(radiation_model, label_encoded)

def updateGeometry(radiation_model):
    """Update all geometry in radiation model"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot update geometry.")
    helios_lib.updateRadiationGeometry(radiation_model)

def updateGeometryUUIDs(radiation_model, uuids: List[int]):
    """Update specific geometry UUIDs in radiation model"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot update geometry.")
    uuid_array = (ctypes.c_uint * len(uuids))(*uuids)
    helios_lib.updateRadiationGeometryUUIDs(radiation_model, uuid_array, len(uuids))

def runBand(radiation_model, label: str):
    """Run simulation for single band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot run simulation.")
    label_encoded = label.encode('utf-8')
    helios_lib.runRadiationBand(radiation_model, label_encoded)

def runBandMultiple(radiation_model, labels: List[str]):
    """Run simulation for multiple bands"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot run simulation.")
    # Convert list of strings to array of c_char_p
    encoded_labels = [label.encode('utf-8') for label in labels]
    label_array = (ctypes.c_char_p * len(encoded_labels))(*encoded_labels)
    helios_lib.runRadiationBandMultiple(radiation_model, label_array, len(encoded_labels))

def getTotalAbsorbedFlux(radiation_model) -> List[float]:
    """Get total absorbed flux for all primitives"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot get absorbed flux.")
    size = ctypes.c_size_t()
    flux_ptr = helios_lib.getTotalAbsorbedFlux(radiation_model, ctypes.byref(size))
    return list(flux_ptr[:size.value])

