"""
Calculateur simple de Sky View Factor pour Helios.

Ce script fournit une interface simple pour calculer le SVF
en utilisant les capacités de rayonnement d'Helios.
"""

import math
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt

from pyhelios import Context, RadiationModel, Visualizer
from pyhelios.types import *


def calculate_svf_simple(
    context: Context, point: vec3, resolution: int = 50, ray_count: int = 1000
) -> float:
    """
    Calcule le Sky View Factor de manière simple en utilisant le rayonnement diffus.

    Args:
        context: Contexte Helios
        point: Position du point d'évaluation
        resolution: Résolution angulaire
        ray_count: Nombre de rayons pour la simulation

    Returns:
        Valeur du SVF (0-1)
    """
    print(f"🌌 Calcul du SVF au point ({point.x:.2f}, {point.y:.2f}, {point.z:.2f})")

    try:
        with RadiationModel(context) as rad:
            # Créer une bande de rayonnement pour le SVF
            rad.addRadiationBand("SVF")
            rad.setDiffuseRayCount("SVF", ray_count)

            # Créer un petit patch de test au point d'évaluation
            test_patch = context.addPatch(
                center=point,
                size=vec2(0.01, 0.01),  # Très petit patch
                color=RGBcolor(1, 0, 0),  # Rouge pour identification
            )

            # Configurer le rayonnement diffus isotrope (ciel uniforme)
            rad.setDiffuseRadiationFlux("SVF", 1000.0)  # Flux unitaire

            # Exécuter la simulation
            rad.updateGeometry()
            rad.runBand("SVF")

            # Récupérer le flux reçu
            flux_received = context.getPrimitiveData(test_patch, "radiation_flux_SVF")

            if flux_received is None:
                print("⚠️  Aucun flux reçu, SVF = 0")
                return 0.0

            # Le SVF est proportionnel au flux reçu
            # Flux maximal théorique (ciel complètement dégagé)
            max_flux = 1000.0
            svf_value = min(flux_received / max_flux, 1.0)

            print(f"   Flux reçu: {flux_received:.1f} W/m²")
            print(f"   SVF calculé: {svf_value:.3f}")

            return svf_value

    except Exception as e:
        print(f"❌ Erreur lors du calcul du SVF: {e}")
        return 0.0


def calculate_svf_grid_simple(
    context: Context,
    grid_center: vec3,
    grid_size: vec2,
    grid_resolution: int = 10,
    height: float = 1.0,
) -> pd.DataFrame:
    """
    Calcule le SVF sur une grille de points.

    Args:
        context: Contexte Helios
        grid_center: Centre de la grille
        grid_size: Taille de la grille
        grid_resolution: Résolution de la grille
        height: Hauteur des points d'évaluation

    Returns:
        DataFrame avec les résultats du SVF
    """
    print(f"🗺️  Calcul du SVF sur une grille {grid_resolution}x{grid_resolution}")

    results = []

    for i in range(grid_resolution):
        for j in range(grid_resolution):
            # Position du point dans la grille
            x = (
                grid_center.x
                - grid_size.x / 2
                + (i + 0.5) * grid_size.x / grid_resolution
            )
            y = (
                grid_center.y
                - grid_size.y / 2
                + (j + 0.5) * grid_size.y / grid_resolution
            )
            z = height

            point = vec3(x, y, z)

            # Calcul du SVF
            svf_value = calculate_svf_simple(context, point)

            results.append({"x": x, "y": y, "z": z, "svf": svf_value})

    return pd.DataFrame(results)


def create_svf_heatmap(df: pd.DataFrame, output_file: str = "svf_heatmap.png") -> None:
    """
    Crée une carte de chaleur du SVF.

    Args:
        df: DataFrame avec les résultats du SVF
        output_file: Nom du fichier de sortie
    """
    print(f"📊 Création de la carte de chaleur: {output_file}")

    # Créer une grille pour la carte de chaleur
    grid_size = int(math.sqrt(len(df)))
    svf_grid = df["svf"].values.reshape(grid_size, grid_size)

    plt.figure(figsize=(10, 8))
    im = plt.imshow(svf_grid, cmap="viridis", origin="lower", vmin=0, vmax=1)

    plt.colorbar(im, label="Sky View Factor")
    plt.title("Sky View Factor - Carte de chaleur")
    plt.xlabel("Position X")
    plt.ylabel("Position Y")

    # # Ajouter les valeurs sur la carte
    # for i in range(grid_size):
    #     for j in range(grid_size):
    #         plt.text(j, i, f'{svf_grid[i, j]:.2f}',
    #                 ha='center', va='center', color='white', fontsize=8)
    #
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.show()


def analyze_svf_results(df: pd.DataFrame) -> None:
    """
    Analyse les résultats du calcul de SVF.

    Args:
        df: DataFrame avec les résultats du SVF
    """
    print("\n📈 Analyse des résultats du SVF:")
    print("=" * 40)

    svf_values = df["svf"].values

    print(f"   Nombre de points: {len(svf_values)}")
    print(f"   SVF moyen: {np.mean(svf_values):.3f}")
    print(f"   SVF médian: {np.median(svf_values):.3f}")
    print(f"   SVF min: {np.min(svf_values):.3f}")
    print(f"   SVF max: {np.max(svf_values):.3f}")
    print(f"   Écart-type: {np.std(svf_values):.3f}")

    # Classification des zones
    very_low = np.sum(svf_values < 0.2)
    low = np.sum((svf_values >= 0.2) & (svf_values < 0.4))
    medium = np.sum((svf_values >= 0.4) & (svf_values < 0.6))
    high = np.sum((svf_values >= 0.6) & (svf_values < 0.8))
    very_high = np.sum(svf_values >= 0.8)

    print(f"\n   Classification des zones:")
    print(
        f"   Très faible (< 0.2): {very_low} points ({very_low/len(svf_values)*100:.1f}%)"
    )
    print(f"   Faible (0.2-0.4): {low} points ({low/len(svf_values)*100:.1f}%)")
    print(f"   Moyen (0.4-0.6): {medium} points ({medium/len(svf_values)*100:.1f}%)")
    print(f"   Élevé (0.6-0.8): {high} points ({high/len(svf_values)*100:.1f}%)")
    print(
        f"   Très élevé (≥ 0.8): {very_high} points ({very_high/len(svf_values)*100:.1f}%)"
    )


def main():
    """
    Démonstration du calculateur simple de SVF.
    """
    print("🌌 Calculateur simple de Sky View Factor")
    print("=" * 50)

    # Créer un contexte de test
    with Context() as context:
        print("🏗️  Création de la scène de test...")

        # Créer un sol
        ground = context.addPatch(
            center=vec3(0, 0, 0), size=vec2(20, 20), color=RGBcolor(0.5, 0.5, 0.5)
        )

        # Créer des obstacles (bâtiments)
        obstacles = []
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:  # Laissez le centre libre
                    continue

                obstacle = context.addPatch(
                    center=vec3(i * 5 - 5, j * 5 - 5, 2),
                    size=vec2(3, 3),
                    color=RGBcolor(0.8, 0.8, 0.8),
                )
                obstacles.append(obstacle)

        print(f"✅ Scène créée: 1 sol, {len(obstacles)} obstacles")

        # Calculer le SVF à différents points
        test_points = [
            vec3(0, 0, 1),  # Centre (devrait avoir un SVF élevé)
            vec3(5, 5, 1),  # Près d'un obstacle
            vec3(-5, -5, 1),  # Coin libre
        ]

        print("\n📍 Calcul du SVF à des points spécifiques:")
        for point in test_points:
            svf = calculate_svf_simple(context, point)
            print(
                f"   Point ({point.x:.1f}, {point.y:.1f}, {point.z:.1f}): SVF = {svf:.3f}"
            )

        # Calcul sur une grille
        print(f"\n🗺️  Calcul du SVF sur une grille...")
        grid_results = calculate_svf_grid_simple(
            context,
            grid_center=vec3(0, 0, 1),
            grid_size=vec2(10, 10),
            grid_resolution=5,
        )

        # Analyser les résultats
        analyze_svf_results(grid_results)

        # Créer une carte de chaleur
        create_svf_heatmap(grid_results)

        # Sauvegarder les résultats
        grid_results.to_csv("svf_results.csv", index=False)
        print("\n💾 Résultats sauvegardés dans svf_results.csv")

        print("\n✅ Calcul du SVF terminé!")


if __name__ == "__main__":
    main()
