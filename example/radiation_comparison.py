"""
Script de comparaison entre l'ancien et le nouveau calcul de rayonnement.

Ce script compare les résultats obtenus avec :
1. L'ancienne méthode (valeurs fixes)
2. La nouvelle méthode (modèles avancés)
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from improved_radiation_calculation import SolarRadiationCalculator, SurfaceType, SURFACE_PROPERTIES


def old_radiation_calculation(hour: float) -> Dict[str, float]:
    """
    Ancienne méthode de calcul de rayonnement (valeurs fixes).
    
    Args:
        hour: Heure du jour
        
    Returns:
        Dictionnaire avec les flux calculés
    """
    # Valeurs fixes de l'ancien script
    sw_flux = 800.0  # Valeur fixe
    diffuse_sw = 200.0  # Valeur fixe
    par_flux = 400.0  # Estimation
    nir_flux = 400.0  # Estimation
    lw_flux = 300.0  # Estimation
    
    return {
        'SW_direct': sw_flux,
        'SW_diffuse': diffuse_sw,
        'SW_total': sw_flux + diffuse_sw,
        'PAR': par_flux,
        'NIR': nir_flux,
        'LW': lw_flux
    }


def new_radiation_calculation(
    hour: float, 
    day_of_year: int = 161,
    latitude: float = -1.15,
    longitude: float = 46.166672
) -> Dict[str, float]:
    """
    Nouvelle méthode de calcul de rayonnement (modèles avancés).
    
    Args:
        hour: Heure du jour
        day_of_year: Jour de l'année
        latitude: Latitude
        longitude: Longitude
        
    Returns:
        Dictionnaire avec les flux calculés
    """
    calculator = SolarRadiationCalculator(latitude, longitude)
    
    # Paramètres météorologiques
    pressure = 101325
    temperature = 288.15 + 10 * math.sin(math.pi * (hour - 6) / 12)
    humidity = 0.6 - 0.2 * math.sin(math.pi * (hour - 6) / 12)
    turbidity = 0.05
    
    # Calcul du rayonnement en ciel clair
    clear_sky = calculator.calculate_clear_sky_radiation(
        hour, day_of_year, pressure, temperature, humidity, turbidity
    )
    
    # Calcul du rayonnement sur surface horizontale
    horizontal = calculator.calculate_hdkr_radiation(
        surface_tilt=0,
        surface_azimuth=0,
        hour=hour,
        day_of_year=day_of_year,
        pressure=pressure,
        temperature=temperature,
        humidity=humidity,
        turbidity=turbidity,
        ground_albedo=0.25
    )
    
    # Estimation des bandes spectrales (simplifiée)
    par_fraction = 0.45  # Fraction PAR du rayonnement visible
    nir_fraction = 0.55  # Fraction NIR du rayonnement visible
    
    return {
        'SW_direct': clear_sky['direct_horizontal'],
        'SW_diffuse': clear_sky['diffuse_horizontal'],
        'SW_total': clear_sky['global_horizontal'],
        'PAR': clear_sky['global_horizontal'] * par_fraction,
        'NIR': clear_sky['global_horizontal'] * nir_fraction,
        'LW': calculator.calculate_clear_sky_radiation(
            hour, day_of_year, pressure, temperature, humidity, turbidity
        )['global_horizontal'] * 0.1  # Estimation simplifiée
    }


def compare_radiation_methods() -> None:
    """
    Compare les deux méthodes de calcul de rayonnement.
    """
    print("📊 Comparaison des méthodes de calcul de rayonnement")
    print("=" * 60)
    
    # Heures de simulation
    hours = np.arange(6, 19, 0.5)
    
    # Stockage des résultats
    old_results = []
    new_results = []
    
    for hour in hours:
        old_flux = old_radiation_calculation(hour)
        new_flux = new_radiation_calculation(hour)
        
        old_results.append(old_flux)
        new_results.append(new_flux)
    
    # Création des DataFrames
    df_old = pd.DataFrame(old_results, index=hours)
    df_new = pd.DataFrame(new_results, index=hours)
    
    # Affichage des résultats
    print("\n📈 Résultats comparatifs (W/m²):")
    print("-" * 40)
    
    for hour in [6, 10, 12, 14, 18]:
        print(f"\nHeure {hour:02d}h:")
        print(f"  Ancienne méthode:")
        print(f"    - SW total: {df_old.loc[hour, 'SW_total']:.1f}")
        print(f"    - PAR: {df_old.loc[hour, 'PAR']:.1f}")
        print(f"    - NIR: {df_old.loc[hour, 'NIR']:.1f}")
        print(f"  Nouvelle méthode:")
        print(f"    - SW total: {df_new.loc[hour, 'SW_total']:.1f}")
        print(f"    - PAR: {df_new.loc[hour, 'PAR']:.1f}")
        print(f"    - NIR: {df_new.loc[hour, 'NIR']:.1f}")
        print(f"  Différence:")
        print(f"    - SW total: {df_new.loc[hour, 'SW_total'] - df_old.loc[hour, 'SW_total']:.1f}")
        print(f"    - PAR: {df_new.loc[hour, 'PAR'] - df_old.loc[hour, 'PAR']:.1f}")
        print(f"    - NIR: {df_new.loc[hour, 'NIR'] - df_old.loc[hour, 'NIR']:.1f}")
    
    # Création des graphiques
    create_comparison_plots(df_old, df_new, hours)


def create_comparison_plots(df_old: pd.DataFrame, df_new: pd.DataFrame, hours: np.ndarray) -> None:
    """
    Crée des graphiques de comparaison.
    
    Args:
        df_old: DataFrame des résultats anciens
        df_new: DataFrame des résultats nouveaux
        hours: Heures de simulation
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Comparaison des méthodes de calcul de rayonnement', fontsize=16)
    
    # Graphique 1: Rayonnement SW total
    axes[0, 0].plot(hours, df_old['SW_total'], 'r-', label='Ancienne méthode', linewidth=2)
    axes[0, 0].plot(hours, df_new['SW_total'], 'b-', label='Nouvelle méthode', linewidth=2)
    axes[0, 0].set_xlabel('Heure')
    axes[0, 0].set_ylabel('Rayonnement SW (W/m²)')
    axes[0, 0].set_title('Rayonnement SW Total')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Graphique 2: Rayonnement PAR
    axes[0, 1].plot(hours, df_old['PAR'], 'r-', label='Ancienne méthode', linewidth=2)
    axes[0, 1].plot(hours, df_new['PAR'], 'b-', label='Nouvelle méthode', linewidth=2)
    axes[0, 1].set_xlabel('Heure')
    axes[0, 1].set_ylabel('Rayonnement PAR (W/m²)')
    axes[0, 1].set_title('Rayonnement PAR')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Graphique 3: Rayonnement NIR
    axes[1, 0].plot(hours, df_old['NIR'], 'r-', label='Ancienne méthode', linewidth=2)
    axes[1, 0].plot(hours, df_new['NIR'], 'b-', label='Nouvelle méthode', linewidth=2)
    axes[1, 0].set_xlabel('Heure')
    axes[1, 0].set_ylabel('Rayonnement NIR (W/m²)')
    axes[1, 0].set_title('Rayonnement NIR')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Graphique 4: Différences
    diff_sw = df_new['SW_total'] - df_old['SW_total']
    diff_par = df_new['PAR'] - df_old['PAR']
    diff_nir = df_new['NIR'] - df_old['NIR']
    
    axes[1, 1].plot(hours, diff_sw, 'g-', label='Différence SW', linewidth=2)
    axes[1, 1].plot(hours, diff_par, 'orange', label='Différence PAR', linewidth=2)
    axes[1, 1].plot(hours, diff_nir, 'purple', label='Différence NIR', linewidth=2)
    axes[1, 1].set_xlabel('Heure')
    axes[1, 1].set_ylabel('Différence (W/m²)')
    axes[1, 1].set_title('Différences entre les méthodes')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('radiation_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n📊 Graphiques sauvegardés: radiation_comparison.png")


def analyze_surface_properties() -> None:
    """
    Analyse les propriétés des différentes surfaces.
    """
    print("\n🏗️ Analyse des propriétés de surface:")
    print("=" * 50)
    
    for surface_type, properties in SURFACE_PROPERTIES.items():
        print(f"\n{surface_type.value.upper()}:")
        print(f"  - Albédo SW: {properties.albedo_sw:.2f}")
        print(f"  - Albédo PAR: {properties.albedo_par:.2f}")
        print(f"  - Albédo NIR: {properties.albedo_nir:.2f}")
        print(f"  - Émissivité: {properties.emissivity:.2f}")
        print(f"  - Longueur de rugosité: {properties.roughness_length:.4f} m")


def main():
    """
    Fonction principale de comparaison.
    """
    print("🔬 Analyse comparative des méthodes de calcul de rayonnement")
    print("=" * 70)
    
    # Comparaison des méthodes
    compare_radiation_methods()
    
    # Analyse des propriétés de surface
    analyze_surface_properties()
    
    print("\n✅ Analyse terminée!")
    print("\n📋 Résumé des améliorations:")
    print("  1. Calcul dynamique du rayonnement solaire")
    print("  2. Modèle HDKR pour surfaces inclinées")
    print("  3. Propriétés de surface réalistes")
    print("  4. Validation des résultats")
    print("  5. Considération des conditions météorologiques")


if __name__ == "__main__":
    main()
