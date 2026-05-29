"""Référence des libellés de données primitives d'entrée/sortie du plugin RadiationModel Helios.

Documentation officielle :
https://plantsimulationlab.github.io/Helios/_radiation_doc.html#Input/Output_Primitive_Data
"""

from __future__ import annotations

from typing import Any

# Données lues par RadiationModel (suffixe * = nom de bande, ex. PAR, NIR, LW, SW) :
#   temperature        — Kelvin, float. Température de surface. Requis pour l'émission (ε·σ·T⁴).
#   reflectivity_*     — sans unité, float. Réflectivité hemisphérique pour la bande * (défaut 0).
#   transmissivity_*   — sans unité, float. Transmissivité pour la bande * (défaut 0). Absorptivité = 1−ρ−τ.
#   emissivity_*       — sans unité, float. Émissivité pour la bande * (défaut 1). Requis si émission active.
#   twosided_flag      — uint. 1 = deux faces (défaut), 0 = une face (sol : côté +normal uniquement).
#   specular_exponent  — float. Réflexion spéculaire caméra (défaut −1 = désactivé).
#   specular_scale     — float. Intensité spéculaire (défaut 1).
#
# Sortie principale : radiation_flux_* (W/m²) — flux absorbé par bande.
#
# Spectres : reflectivity_spectrum, transmissivity_spectrum (string → global data XML).
# Ne pas utiliser le libellé nu « emissivity » : RadiationModel lit emissivity_<bande> uniquement.
#
# Hors table radiation (autres plugins) : air_temperature, air_humidity, wind_speed,
# air_pressure, surface_type, sky_view_factor, plant_part, species, etc.


def get_emissivity_lw(context: Any, uuid: int, default: float = 0.96) -> float:
    """Retourne emissivity_LW si présent, sinon l'ancien libellé emissivity (déprécié)."""
    if context.doesPrimitiveDataExist(uuid, "emissivity_LW"):
        return float(context.getPrimitiveData(uuid, "emissivity_LW"))
    if context.doesPrimitiveDataExist(uuid, "emissivity"):
        return float(context.getPrimitiveData(uuid, "emissivity"))
    return default
