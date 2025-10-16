import math
from dataclasses import dataclass
from enum import Enum
from typing import List

from pyhelios import Context


class SurfaceType(Enum):
    """Types de surfaces avec leurs propriétés optiques."""

    SOIL = "soil"
    GRASS = "grass"
    CONCRETE = "concrete"
    ASPHALT = "asphalt"
    WATER = "water"
    SNOW = "snow"
    LEAF = "leaf"
    TRUNK = "trunk"
    BRANCH = "branch"


@dataclass
class SurfaceProperties:
    """Propriétés optiques d'une surface."""

    albedo_sw: float
    albedo_par: float
    albedo_nir: float
    albedo_lw: float
    emissivity: float
    roughness_length: float = 0.01  # m
    transmissivity_lw: float = (
        0.0  # Transmissivité LW (généralement 0 pour surfaces opaques)
    )

    def __post_init__(self):
        """Valide que les propriétés radiatives respectent la conservation d'énergie."""
        # Pour la bande LW : émissivité + transmissivité + réflectivité = 1
        lw_sum = self.emissivity + self.transmissivity_lw + self.albedo_lw
        if not math.isclose(lw_sum, 1.0, abs_tol=1e-6):
            # Ajuster automatiquement pour respecter la conservation d'énergie
            if lw_sum > 1.0:
                # Réduire proportionnellement
                scale_factor = 1.0 / lw_sum
                self.emissivity *= scale_factor
                self.transmissivity_lw *= scale_factor
                self.albedo_lw *= scale_factor
            else:
                # Augmenter l'émissivité pour atteindre 1.0
                self.emissivity = 1.0 - self.transmissivity_lw - self.albedo_lw


# Base de données des propriétés de surface (avec conservation d'énergie)
SURFACE_PROPERTIES = {
    SurfaceType.SOIL: SurfaceProperties(
        albedo_sw=0.25,
        albedo_par=0.10,
        albedo_nir=0.50,
        albedo_lw=0.05,
        emissivity=0.95,
        transmissivity_lw=0.0,
        roughness_length=0.01,
    ),
    SurfaceType.GRASS: SurfaceProperties(
        albedo_sw=0.25,
        albedo_par=0.10,
        albedo_nir=0.50,
        albedo_lw=0.02,
        emissivity=0.98,
        transmissivity_lw=0.0,
        roughness_length=0.05,
    ),
    SurfaceType.CONCRETE: SurfaceProperties(
        albedo_sw=0.35,
        albedo_par=0.15,
        albedo_nir=0.40,
        albedo_lw=0.10,
        emissivity=0.90,
        transmissivity_lw=0.0,
        roughness_length=0.001,
    ),
    SurfaceType.ASPHALT: SurfaceProperties(
        albedo_sw=0.15,
        albedo_par=0.05,
        albedo_nir=0.20,
        albedo_lw=0.05,
        emissivity=0.95,
        transmissivity_lw=0.0,
        roughness_length=0.001,
    ),
    SurfaceType.WATER: SurfaceProperties(
        albedo_sw=0.07,
        albedo_par=0.06,
        albedo_nir=0.02,
        albedo_lw=0.03,
        emissivity=0.97,
        transmissivity_lw=0.0,
        roughness_length=0.0001,
    ),
    SurfaceType.SNOW: SurfaceProperties(
        albedo_sw=0.80,
        albedo_par=0.70,
        albedo_nir=0.85,
        albedo_lw=0.01,
        emissivity=0.99,
        transmissivity_lw=0.0,
        roughness_length=0.001,
    ),
    SurfaceType.LEAF: SurfaceProperties(
        albedo_sw=0.20,
        albedo_par=0.10,
        albedo_nir=0.45,
        albedo_lw=0.02,
        emissivity=0.98,
        transmissivity_lw=0.0,
        roughness_length=0.01,
    ),
    SurfaceType.TRUNK: SurfaceProperties(
        albedo_sw=0.60,
        albedo_par=0.15,
        albedo_nir=0.50,
        albedo_lw=0.05,
        emissivity=0.95,
        transmissivity_lw=0.0,
        roughness_length=0.01,
    ),
    SurfaceType.BRANCH: SurfaceProperties(
        albedo_sw=0.60,
        albedo_par=0.15,
        albedo_nir=0.50,
        albedo_lw=0.05,
        emissivity=0.95,
        transmissivity_lw=0.0,
        roughness_length=0.01,
    ),
}


def apply_surface_properties(
    context: Context, uuids: List[str], surface_type: SurfaceType
) -> None:
    """
    Applique les propriétés optiques d'une surface à une liste d'UUIDs.

    Args:
        context: Contexte PyHelios
        uuids: Liste des UUIDs des primitives
        surface_type: Type de surface
    """
    props = SURFACE_PROPERTIES[surface_type]

    for uuid in uuids:
        # Propriétés SW (Short Wave)
        context.setPrimitiveDataFloat(uuid, "reflectivity_SW", props.albedo_sw)
        context.setPrimitiveDataFloat(uuid, "reflectivity_PAR", props.albedo_par)
        context.setPrimitiveDataFloat(uuid, "reflectivity_NIR", props.albedo_nir)

        # Propriétés LW (Long Wave) - Conservation d'énergie
        context.setPrimitiveDataFloat(uuid, "reflectivity_LW", props.albedo_lw)
        context.setPrimitiveDataFloat(uuid, "transmissivity_LW", props.transmissivity_lw)
        context.setPrimitiveDataFloat(uuid, "emissivity", props.emissivity)

        # Propriétés physiques
        context.setPrimitiveDataString(uuid, "surface_type", surface_type.value)
        context.setPrimitiveDataFloat(uuid, "roughness_length", props.roughness_length)
