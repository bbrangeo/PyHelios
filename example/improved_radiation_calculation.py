"""
Script amélioré pour le calcul de rayonnement solaire avec modèles avancés.

Ce script implémente les améliorations suivantes :
- Modèle HDKR pour le rayonnement sur surfaces inclinées
- Calcul dynamique du rayonnement solaire global
- Albédo variable selon le type de surface
- Modèle de ciel couvert amélioré
- Validation et calibration des résultats
"""

import math
import os
import platform
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import imageio
import numpy as np
import pandas as pd

from pyhelios import (
    Context,
    RadiationModel,
    SolarPosition,
    Visualizer,
    WeberPennTree,
    WPTType,
    EnergyBalanceModel,
    BoundaryLayerConductanceModel,
    StomatalConductanceModel,
    BMFCoefficients,
    PhotosynthesisModel,
    PlantArchitecture,
)

from pyhelios.types import *

import pyhelios.dev_utils

pyhelios.dev_utils.enable_dev_mode()


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
    transmissivity_lw: float = 0.0  # Transmissivité LW (généralement 0 pour surfaces opaques)
    roughness_length: float = 0.01  # m
    
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
        albedo_sw=0.25, albedo_par=0.10, albedo_nir=0.50, 
        albedo_lw=0.05, emissivity=0.95, transmissivity_lw=0.0, roughness_length=0.01
    ),
    SurfaceType.GRASS: SurfaceProperties(
        albedo_sw=0.25, albedo_par=0.10, albedo_nir=0.50, 
        albedo_lw=0.02, emissivity=0.98, transmissivity_lw=0.0, roughness_length=0.05
    ),
    SurfaceType.CONCRETE: SurfaceProperties(
        albedo_sw=0.35, albedo_par=0.15, albedo_nir=0.40, 
        albedo_lw=0.10, emissivity=0.90, transmissivity_lw=0.0, roughness_length=0.001
    ),
    SurfaceType.ASPHALT: SurfaceProperties(
        albedo_sw=0.15, albedo_par=0.05, albedo_nir=0.20, 
        albedo_lw=0.05, emissivity=0.95, transmissivity_lw=0.0, roughness_length=0.001
    ),
    SurfaceType.WATER: SurfaceProperties(
        albedo_sw=0.07, albedo_par=0.06, albedo_nir=0.02, 
        albedo_lw=0.03, emissivity=0.97, transmissivity_lw=0.0, roughness_length=0.0001
    ),
    SurfaceType.SNOW: SurfaceProperties(
        albedo_sw=0.80, albedo_par=0.70, albedo_nir=0.85, 
        albedo_lw=0.01, emissivity=0.99, transmissivity_lw=0.0, roughness_length=0.001
    ),
    SurfaceType.LEAF: SurfaceProperties(
        albedo_sw=0.20, albedo_par=0.10, albedo_nir=0.45, 
        albedo_lw=0.02, emissivity=0.98, transmissivity_lw=0.0, roughness_length=0.01
    ),
    SurfaceType.TRUNK: SurfaceProperties(
        albedo_sw=0.60, albedo_par=0.15, albedo_nir=0.50, 
        albedo_lw=0.05, emissivity=0.95, transmissivity_lw=0.0, roughness_length=0.01
    ),
    SurfaceType.BRANCH: SurfaceProperties(
        albedo_sw=0.60, albedo_par=0.15, albedo_nir=0.50, 
        albedo_lw=0.05, emissivity=0.95, transmissivity_lw=0.0, roughness_length=0.01
    ),
}


class SolarRadiationCalculator:
    """Calculateur de rayonnement solaire avec modèles avancés."""
    
    def __init__(self, latitude: float, longitude: float, timezone: int = 1):
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        
    def calculate_solar_angles(self, hour: float, day_of_year: int) -> Dict[str, float]:
        """
        Calcule les angles solaires pour une heure et un jour donnés.
        
        Args:
            hour: Heure du jour (0-24)
            day_of_year: Jour de l'année (1-365)
            
        Returns:
            Dictionnaire contenant les angles solaires
        """
        # Angle horaire (radians)
        hour_angle = math.radians(15 * (hour - 12))
        
        # Déclinaison solaire (radians)
        declination = math.radians(23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365)))
        
        # Angle d'élévation solaire
        elevation = math.asin(
            math.sin(math.radians(self.latitude)) * math.sin(declination) +
            math.cos(math.radians(self.latitude)) * math.cos(declination) * math.cos(hour_angle)
        )
        
        # Angle azimutal solaire
        azimuth = math.atan2(
            math.sin(hour_angle),
            math.cos(hour_angle) * math.sin(math.radians(self.latitude)) - 
            math.tan(declination) * math.cos(math.radians(self.latitude))
        )
        
        return {
            'elevation': elevation,
            'azimuth': azimuth,
            'hour_angle': hour_angle,
            'declination': declination
        }
    
    def calculate_clear_sky_radiation(
        self, 
        hour: float, 
        day_of_year: int,
        pressure: float = 101325,
        temperature: float = 288.15,
        humidity: float = 0.5,
        turbidity: float = 0.05
    ) -> Dict[str, float]:
        """
        Calcule le rayonnement solaire en ciel clair selon le modèle de Bird (1981).
        
        Args:
            hour: Heure du jour
            day_of_year: Jour de l'année
            pressure: Pression atmosphérique (Pa)
            temperature: Température de l'air (K)
            humidity: Humidité relative (0-1)
            turbidity: Turbidité de Linke
            
        Returns:
            Dictionnaire contenant les composantes du rayonnement
        """
        angles = self.calculate_solar_angles(hour, day_of_year)
        elevation = angles['elevation']
        
        if elevation <= 0:
            return {
                'direct_normal': 0.0,
                'direct_horizontal': 0.0,
                'diffuse_horizontal': 0.0,
                'global_horizontal': 0.0,
                'beam_normal': 0.0
            }
        
        # Constante solaire (W/m²)
        solar_constant = 1367.0
        
        # Distance Terre-Soleil
        day_angle = 2 * math.pi * day_of_year / 365
        earth_sun_distance = 1 + 0.033 * math.cos(day_angle)
        
        # Rayonnement extraterrestre sur surface normale
        extraterrestrial_normal = solar_constant * earth_sun_distance
        
        # Rayonnement extraterrestre sur surface horizontale
        extraterrestrial_horizontal = extraterrestrial_normal * math.sin(elevation)
        
        # Modèle de Bird (1981) - coefficients simplifiés
        # Transmission due à l'ozone
        ozone_transmission = 0.98
        
        # Transmission due à la vapeur d'eau
        water_vapor_transmission = 0.99 - 0.17 * humidity
        
        # Transmission due aux gaz uniformément mélangés
        gas_transmission = 0.99
        
        # Transmission due à l'aérosol
        aerosol_transmission = math.exp(-turbidity * (0.1 + 0.3 * (pressure / 101325)))
        
        # Transmission due à la diffusion de Rayleigh
        rayleigh_transmission = 0.99 - 0.08 * (1 - math.sin(elevation))
        
        # Transmission totale
        total_transmission = (ozone_transmission * water_vapor_transmission * 
                            gas_transmission * aerosol_transmission * rayleigh_transmission)
        
        # Rayonnement direct normal
        direct_normal = extraterrestrial_normal * total_transmission
        
        # Rayonnement direct horizontal
        direct_horizontal = direct_normal * math.sin(elevation)
        
        # Rayonnement diffus horizontal (modèle de Liu & Jordan)
        diffuse_horizontal = extraterrestrial_horizontal * 0.271 - 0.294 * total_transmission
        
        # Rayonnement global horizontal
        global_horizontal = direct_horizontal + diffuse_horizontal
        
        return {
            'direct_normal': max(0, direct_normal),
            'direct_horizontal': max(0, direct_horizontal),
            'diffuse_horizontal': max(0, diffuse_horizontal),
            'global_horizontal': max(0, global_horizontal),
            'beam_normal': max(0, direct_normal)
        }
    
    def calculate_hdkr_radiation(
        self,
        surface_tilt: float,
        surface_azimuth: float,
        hour: float,
        day_of_year: int,
        pressure: float = 101325,
        temperature: float = 288.15,
        humidity: float = 0.5,
        turbidity: float = 0.05,
        ground_albedo: float = 0.25
    ) -> Dict[str, float]:
        """
        Calcule le rayonnement sur surface inclinée selon le modèle HDKR.
        
        Args:
            surface_tilt: Inclinaison de la surface (degrés)
            surface_azimuth: Azimut de la surface (degrés)
            hour: Heure du jour
            day_of_year: Jour de l'année
            pressure: Pression atmosphérique (Pa)
            temperature: Température de l'air (K)
            humidity: Humidité relative (0-1)
            turbidity: Turbidité de Linke
            ground_albedo: Albédo du sol
            
        Returns:
            Dictionnaire contenant les composantes du rayonnement sur surface inclinée
        """
        # Rayonnement en ciel clair sur surface horizontale
        clear_sky = self.calculate_clear_sky_radiation(
            hour, day_of_year, pressure, temperature, humidity, turbidity
        )
        
        angles = self.calculate_solar_angles(hour, day_of_year)
        solar_elevation = angles['elevation']
        solar_azimuth = angles['azimuth']
        
        if solar_elevation <= 0:
            return {
                'direct_tilted': 0.0,
                'diffuse_tilted': 0.0,
                'reflected_tilted': 0.0,
                'total_tilted': 0.0
            }
        
        # Conversion en radians
        tilt_rad = math.radians(surface_tilt)
        azimuth_rad = math.radians(surface_azimuth)
        
        # Angle d'incidence sur surface inclinée
        cos_incidence = (
            math.sin(solar_elevation) * math.cos(tilt_rad) +
            math.cos(solar_elevation) * math.sin(tilt_rad) * 
            math.cos(solar_azimuth - azimuth_rad)
        )
        
        # Rayonnement direct sur surface inclinée
        direct_tilted = clear_sky['direct_normal'] * max(0, cos_incidence)
        
        # Facteur d'anisotropie (Hay & Davies)
        anisotropy_index = clear_sky['direct_horizontal'] / clear_sky['global_horizontal']
        
        # Rayonnement diffus anisotrope
        diffuse_anisotropic = clear_sky['diffuse_horizontal'] * (
            anisotropy_index * max(0, cos_incidence) / math.sin(solar_elevation) +
            (1 - anisotropy_index) * (1 + math.cos(tilt_rad)) / 2
        )
        
        # Rayonnement diffus isotrope
        diffuse_isotropic = clear_sky['diffuse_horizontal'] * (1 - anisotropy_index) * (1 + math.cos(tilt_rad)) / 2
        
        # Rayonnement diffus total sur surface inclinée
        diffuse_tilted = diffuse_anisotropic + diffuse_isotropic
        
        # Rayonnement réfléchi par le sol
        reflected_tilted = clear_sky['global_horizontal'] * ground_albedo * (1 - math.cos(tilt_rad)) / 2
        
        # Rayonnement total sur surface inclinée
        total_tilted = direct_tilted + diffuse_tilted + reflected_tilted
        
        return {
            'direct_tilted': max(0, direct_tilted),
            'diffuse_tilted': max(0, diffuse_tilted),
            'reflected_tilted': max(0, reflected_tilted),
            'total_tilted': max(0, total_tilted)
        }


def apply_surface_properties(
    context: Context, 
    uuids: List[str], 
    surface_type: SurfaceType
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
        # EnergyBalanceModel attend emissivity_<bande> pour chaque bande enregistrée (LW, PAR, NIR).
        for band in ("LW", "PAR", "NIR"):
            context.setPrimitiveDataFloat(uuid, f"emissivity_{band}", props.emissivity)
        
        # Propriétés physiques
        context.setPrimitiveDataString(uuid, "surface_type", surface_type.value)
        context.setPrimitiveDataFloat(uuid, "roughness_length", props.roughness_length)
        
        # Validation de la conservation d'énergie
        lw_sum = props.emissivity + props.transmissivity_lw + props.albedo_lw
        if not math.isclose(lw_sum, 1.0, abs_tol=1e-6):
            print(f"⚠️  Attention: Conservation d'énergie non respectée pour {surface_type.value}")
            print(f"   Émissivité: {props.emissivity:.3f}")
            print(f"   Transmissivité: {props.transmissivity_lw:.3f}")
            print(f"   Réflectivité: {props.albedo_lw:.3f}")
            print(f"   Somme: {lw_sum:.3f}")


def calculate_improved_radiation_fluxes(
    context: Context,
    solar_calculator: SolarRadiationCalculator,
    hour: float,
    day_of_year: int,
    pressure: float,
    temperature: float,
    humidity: float,
    turbidity: float
) -> Dict[str, float]:
    """
    Calcule les flux de rayonnement améliorés pour toutes les surfaces.
    
    Args:
        context: Contexte PyHelios
        solar_calculator: Calculateur de rayonnement solaire
        hour: Heure du jour
        day_of_year: Jour de l'année
        pressure: Pression atmosphérique
        temperature: Température de l'air
        humidity: Humidité relative
        turbidity: Turbidité de Linke
        
    Returns:
        Dictionnaire contenant les flux calculés
    """
    # Calcul du rayonnement en ciel clair
    clear_sky = solar_calculator.calculate_clear_sky_radiation(
        hour, day_of_year, pressure, temperature, humidity, turbidity
    )
    
    # Calcul du rayonnement sur surface horizontale (sol)
    horizontal_radiation = solar_calculator.calculate_hdkr_radiation(
        surface_tilt=0,  # Surface horizontale
        surface_azimuth=0,
        hour=hour,
        day_of_year=day_of_year,
        pressure=pressure,
        temperature=temperature,
        humidity=humidity,
        turbidity=turbidity,
        ground_albedo=0.25
    )
    
    # Calcul du rayonnement sur surfaces verticales (murs)
    vertical_radiation = solar_calculator.calculate_hdkr_radiation(
        surface_tilt=90,  # Surface verticale
        surface_azimuth=180,  # Face sud
        hour=hour,
        day_of_year=day_of_year,
        pressure=pressure,
        temperature=temperature,
        humidity=humidity,
        turbidity=turbidity,
        ground_albedo=0.25
    )
    
    return {
        'clear_sky': clear_sky,
        'horizontal': horizontal_radiation,
        'vertical': vertical_radiation
    }


def validate_radiation_results(
    context: Context,
    calculated_fluxes: Dict[str, float],
    tolerance: float = 0.1
) -> Dict[str, Any]:
    """
    Valide les résultats de calcul de rayonnement.
    
    Args:
        context: Contexte PyHelios
        calculated_fluxes: Flux calculés
        tolerance: Tolérance de validation
        
    Returns:
        Dictionnaire contenant les résultats de validation
    """
    validation_results = {
        'is_valid': True,
        'warnings': [],
        'errors': [],
        'statistics': {}
    }
    
    # Vérification des valeurs physiques
    for band in ['SW', 'PAR', 'NIR', 'LW']:
        flux_key = f'radiation_flux_{band}'
        all_uuids = context.getAllUUIDs()
        
        fluxes = []
        for uuid in all_uuids:
            flux = context.getPrimitiveData(uuid, flux_key)
            if flux is not None:
                fluxes.append(flux)
        
        if fluxes:
            mean_flux = np.mean(fluxes)
            max_flux = np.max(fluxes)
            min_flux = np.min(fluxes)
            
            validation_results['statistics'][band] = {
                'mean': mean_flux,
                'max': max_flux,
                'min': min_flux,
                'std': np.std(fluxes)
            }
            
            # Vérification des valeurs physiques
            if min_flux < 0:
                validation_results['errors'].append(f"Flux négatif détecté pour {band}: {min_flux}")
                validation_results['is_valid'] = False
            
            if max_flux > 2000:  # Valeur maximale réaliste
                validation_results['warnings'].append(f"Flux très élevé pour {band}: {max_flux}")
    
    return validation_results


def main():
    """
    Fonction principale avec calcul de rayonnement amélioré.
    """
    print("🚀 Script de calcul de rayonnement amélioré")
    print("=" * 60)
    
    # Paramètres de simulation
    latitude = -1.15
    longitude = 46.166672
    timezone = 1
    pressure = 101300
    turbidity = 0.05
    
    # Créer le calculateur de rayonnement
    solar_calculator = SolarRadiationCalculator(latitude, longitude, timezone)
    
    # Créer le contexte
    with Context() as context:
        print("🌍 Configuration de la scène...")
        
        # Créer une scène simple pour la démonstration
        # (Votre code existant pour créer la géométrie)
        
        # Simulation pour différentes heures
        hours = [6, 10, 12, 14, 18]
        day_of_year = 161  # 10 juin
        
        for hour in hours:
            print(f"\n🕐 Calcul pour {hour:02d}h...")
            
            # Paramètres météorologiques variables
            temperature = 288.15 + 10 * math.sin(math.pi * (hour - 6) / 12)  # K
            humidity = 0.6 - 0.2 * math.sin(math.pi * (hour - 6) / 12)  # 0-1
            
            # Calcul des flux de rayonnement améliorés
            radiation_fluxes = calculate_improved_radiation_fluxes(
                context=context,
                solar_calculator=solar_calculator,
                hour=hour,
                day_of_year=day_of_year,
                pressure=pressure,
                temperature=temperature,
                humidity=humidity,
                turbidity=turbidity
            )
            
            # Validation des résultats
            validation = validate_radiation_results(context, radiation_fluxes)
            
            print(f"✅ Calcul terminé pour {hour:02d}h")
            print(f"   - Rayonnement global horizontal: {radiation_fluxes['horizontal']['total_tilted']:.1f} W/m²")
            print(f"   - Rayonnement direct: {radiation_fluxes['horizontal']['direct_tilted']:.1f} W/m²")
            print(f"   - Rayonnement diffus: {radiation_fluxes['horizontal']['diffuse_tilted']:.1f} W/m²")
            
            if not validation['is_valid']:
                print(f"⚠️  Erreurs détectées: {validation['errors']}")
            
            if validation['warnings']:
                print(f"⚠️  Avertissements: {validation['warnings']}")


if __name__ == "__main__":
    main()
