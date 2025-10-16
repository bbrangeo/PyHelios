"""
Calcul du Sky View Factor (SVF) avec Helios.

Le Sky View Factor représente la fraction du ciel visible depuis un point donné,
crucial pour l'évaluation de l'exposition au rayonnement solaire et au refroidissement radiatif.

Méthodes implémentées :
1. Méthode de projection hémisphérique
2. Méthode de ray casting
3. Méthode de simulation de rayonnement diffus
"""

import math
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt

from pyhelios import Context, RadiationModel, Visualizer
from pyhelios.types import *


@dataclass
class SVFResult:
    """Résultat du calcul de Sky View Factor."""

    svf_value: float
    sky_visible: float
    obstacles_visible: float
    total_hemisphere: float
    method: str
    point_position: vec3
    resolution: int


class SkyViewFactorCalculator:
    """Calculateur de Sky View Factor pour Helios."""

    def __init__(self, context: Context, resolution: int = 100):
        """
        Initialise le calculateur de SVF.

        Args:
            context: Contexte Helios
            resolution: Résolution angulaire (nombre de directions)
        """
        self.context = context
        self.resolution = resolution
        self.hemisphere_directions = self._generate_hemisphere_directions()

    def _generate_hemisphere_directions(self) -> List[vec3]:
        """
        Génère les directions de l'hémisphère supérieur pour le calcul du SVF.

        Returns:
            Liste des directions normalisées
        """
        directions = []

        # Génération des directions selon une grille sphérique
        for i in range(self.resolution):
            for j in range(self.resolution):
                # Angles sphériques
                theta = (
                    math.pi * i / (self.resolution - 1)
                )  # 0 à π (hémisphère supérieur)
                phi = 2 * math.pi * j / self.resolution  # 0 à 2π (azimut)

                # Conversion en coordonnées cartésiennes
                x = math.sin(theta) * math.cos(phi)
                y = math.sin(theta) * math.sin(phi)
                z = math.cos(theta)  # Composante verticale positive

                directions.append(vec3(x, y, z))

        return directions

    def calculate_svf_ray_casting(
        self, point: vec3, max_distance: float = 1000.0
    ) -> SVFResult:
        """
        Calcule le SVF par ray casting.

        Args:
            point: Position du point d'évaluation
            max_distance: Distance maximale de ray casting

        Returns:
            Résultat du calcul de SVF
        """
        print(
            f"🔍 Calcul du SVF par ray casting au point ({point.x:.2f}, {point.y:.2f}, {point.z:.2f})"
        )

        sky_visible = 0
        obstacles_visible = 0

        for direction in self.hemisphere_directions:
            # Lancer un rayon depuis le point dans la direction
            hit = self._cast_ray(point, direction, max_distance)

            if hit:
                obstacles_visible += 1
            else:
                sky_visible += 1

        total_directions = len(self.hemisphere_directions)
        svf_value = sky_visible / total_directions

        return SVFResult(
            svf_value=svf_value,
            sky_visible=sky_visible,
            obstacles_visible=obstacles_visible,
            total_hemisphere=total_directions,
            method="ray_casting",
            point_position=point,
            resolution=self.resolution,
        )

    def _cast_ray(self, origin: vec3, direction: vec3, max_distance: float) -> bool:
        """
        Lance un rayon et vérifie s'il intersecte un obstacle.

        Args:
            origin: Point d'origine du rayon
            direction: Direction du rayon (normalisée)
            max_distance: Distance maximale

        Returns:
            True si le rayon intersecte un obstacle, False sinon
        """
        # Méthode simplifiée : vérifier si le rayon intersecte la géométrie
        # Dans une implémentation complète, utiliser les fonctions de ray casting d'Helios

        # Pour cette démonstration, on simule une intersection basée sur la géométrie
        # En réalité, utiliser context.rayIntersect() ou équivalent

        # Simulation basique : vérifier si la direction pointe vers le sol
        if direction.z < 0:  # Direction vers le bas
            return True

        # Vérifier les obstacles dans la direction
        # (Cette partie nécessiterait l'API de ray casting d'Helios)
        return False

    def calculate_svf_radiation_method(self, point: vec3) -> SVFResult:
        """
        Calcule le SVF en utilisant la simulation de rayonnement diffus.

        Args:
            point: Position du point d'évaluation

        Returns:
            Résultat du calcul de SVF
        """
        print(
            f"🌞 Calcul du SVF par méthode de rayonnement au point ({point.x:.2f}, {point.y:.2f}, {point.z:.2f})"
        )

        try:
            with RadiationModel(self.context) as rad:
                # Créer une source de rayonnement diffus isotrope
                rad.addRadiationBand("SVF")
                rad.disableEmission("SVF")
                rad.setScatteringDepth("SVF", 0)
                rad.setDiffuseRayCount(
                    "SVF", self.resolution * 10
                )  # Plus de rayons pour précision

                # Créer un patch de test au point d'évaluation
                test_patch = self.context.addPatch(
                    center=point,
                    size=vec2(0.1, 0.1),  # Petit patch
                    color=RGBcolor(1, 0, 0),  # Rouge pour identification
                )

                # Configurer le rayonnement diffus isotrope
                rad.setDiffuseRadiationFlux("SVF", 1000.0)  # Flux unitaire

                # Exécuter la simulation
                rad.updateGeometry()
                rad.runBand("SVF")

                # Récupérer le flux reçu
                flux_received = self.context.getPrimitiveData(
                    test_patch, "radiation_flux_SVF"
                )

                if flux_received is None:
                    flux_received = 0.0

                # Le SVF est proportionnel au flux reçu
                # Flux maximal théorique (ciel complètement dégagé)
                max_flux = 1000.0
                svf_value = min(flux_received / max_flux, 1.0)

                # Nettoyer le patch de test
                # (Dans une implémentation complète, supprimer le patch)

                return SVFResult(
                    svf_value=svf_value,
                    sky_visible=svf_value * self.resolution,
                    obstacles_visible=(1 - svf_value) * self.resolution,
                    total_hemisphere=self.resolution,
                    method="radiation",
                    point_position=point,
                    resolution=self.resolution,
                )

        except Exception as e:
            print(f"❌ Erreur lors du calcul par rayonnement: {e}")
            return SVFResult(
                svf_value=0.0,
                sky_visible=0,
                obstacles_visible=self.resolution,
                total_hemisphere=self.resolution,
                method="radiation",
                point_position=point,
                resolution=self.resolution,
            )

    def calculate_svf_hemispherical_projection(self, point: vec3) -> SVFResult:
        """
        Calcule le SVF par projection hémisphérique.

        Args:
            point: Position du point d'évaluation

        Returns:
            Résultat du calcul de SVF
        """
        print(
            f"📐 Calcul du SVF par projection hémisphérique au point ({point.x:.2f}, {point.y:.2f}, {point.z:.2f})"
        )

        # Créer une grille hémisphérique
        sky_pixels = 0
        obstacle_pixels = 0

        for i in range(self.resolution):
            for j in range(self.resolution):
                # Coordonnées dans l'image hémisphérique
                x = (i - self.resolution // 2) / (self.resolution // 2)
                y = (j - self.resolution // 2) / (self.resolution // 2)

                # Vérifier si le point est dans l'hémisphère
                if x * x + y * y <= 1:
                    # Convertir en direction 3D
                    z = math.sqrt(1 - x * x - y * y)
                    direction = vec3(x, y, z)

                    # Vérifier si cette direction est obstruée
                    if self._is_direction_obstructed(point, direction):
                        obstacle_pixels += 1
                    else:
                        sky_pixels += 1

        total_pixels = sky_pixels + obstacle_pixels
        svf_value = sky_pixels / total_pixels if total_pixels > 0 else 0.0

        return SVFResult(
            svf_value=svf_value,
            sky_visible=sky_pixels,
            obstacles_visible=obstacle_pixels,
            total_hemisphere=total_pixels,
            method="hemispherical_projection",
            point_position=point,
            resolution=self.resolution,
        )

    def _is_direction_obstructed(self, point: vec3, direction: vec3) -> bool:
        """
        Vérifie si une direction est obstruée par la géométrie.

        Args:
            point: Point d'évaluation
            direction: Direction à vérifier

        Returns:
            True si la direction est obstruée, False sinon
        """
        # Implémentation simplifiée
        # En réalité, utiliser les fonctions d'intersection d'Helios

        # Vérifier si la direction pointe vers le sol
        if direction.z < 0:
            return True

        # Vérifier les obstacles dans la direction
        # (Cette partie nécessiterait l'API d'intersection d'Helios)
        return False

    def calculate_svf_comprehensive(self, point: vec3) -> Dict[str, SVFResult]:
        """
        Calcule le SVF avec toutes les méthodes disponibles.

        Args:
            point: Position du point d'évaluation

        Returns:
            Dictionnaire avec les résultats de toutes les méthodes
        """
        print(
            f"🎯 Calcul complet du SVF au point ({point.x:.2f}, {point.y:.2f}, {point.z:.2f})"
        )

        results = {}

        # Méthode 1: Ray casting
        try:
            results["ray_casting"] = self.calculate_svf_ray_casting(point)
        except Exception as e:
            print(f"⚠️  Erreur ray casting: {e}")

        # Méthode 2: Rayonnement
        try:
            results["radiation"] = self.calculate_svf_radiation_method(point)
        except Exception as e:
            print(f"⚠️  Erreur rayonnement: {e}")

        # Méthode 3: Projection hémisphérique
        try:
            results["hemispherical"] = self.calculate_svf_hemispherical_projection(
                point
            )
        except Exception as e:
            print(f"⚠️  Erreur projection hémisphérique: {e}")

        return results


def create_svf_visualization(
    svf_results: Dict[str, SVFResult], output_dir: str = "svf_results"
) -> None:
    """
    Crée des visualisations du Sky View Factor.

    Args:
        svf_results: Résultats du calcul de SVF
        output_dir: Dossier de sortie
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    # Graphique comparatif des méthodes
    methods = list(svf_results.keys())
    svf_values = [svf_results[method].svf_value for method in methods]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, svf_values, color=["skyblue", "lightcoral", "lightgreen"])
    plt.title("Comparaison des méthodes de calcul du Sky View Factor")
    plt.xlabel("Méthode")
    plt.ylabel("Valeur du SVF")
    plt.ylim(0, 1)

    # Ajouter les valeurs sur les barres
    for bar, value in zip(bars, svf_values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{value:.3f}",
            ha="center",
            va="bottom",
        )

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "svf_comparison.png"), dpi=300)
    plt.show()

    # Graphique de répartition ciel/obstacles
    fig, axes = plt.subplots(1, len(methods), figsize=(15, 5))
    if len(methods) == 1:
        axes = [axes]

    for i, (method, result) in enumerate(svf_results.items()):
        labels = ["Ciel visible", "Obstacles"]
        sizes = [result.sky_visible, result.obstacles_visible]
        colors = ["skyblue", "lightcoral"]

        axes[i].pie(
            sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
        )
        axes[i].set_title(f"{method}\nSVF = {result.svf_value:.3f}")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "svf_distribution.png"), dpi=300)
    plt.show()


def calculate_svf_grid(
    context: Context, grid_center: vec3, grid_size: vec2, grid_resolution: int = 10
) -> pd.DataFrame:
    """
    Calcule le SVF sur une grille de points.

    Args:
        context: Contexte Helios
        grid_center: Centre de la grille
        grid_size: Taille de la grille
        grid_resolution: Résolution de la grille

    Returns:
        DataFrame avec les résultats du SVF
    """
    print(f"🗺️  Calcul du SVF sur une grille {grid_resolution}x{grid_resolution}")

    calculator = SkyViewFactorCalculator(context, resolution=50)

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
            z = grid_center.z

            point = vec3(x, y, z)

            # Calcul du SVF
            svf_result = calculator.calculate_svf_ray_casting(point)

            results.append(
                {
                    "x": x,
                    "y": y,
                    "z": z,
                    "svf": svf_result.svf_value,
                    "sky_visible": svf_result.sky_visible,
                    "obstacles_visible": svf_result.obstacles_visible,
                }
            )

    return pd.DataFrame(results)


def main():
    """
    Démonstration du calcul de Sky View Factor avec Helios.
    """
    print("🌌 Calcul du Sky View Factor avec Helios")
    print("=" * 50)

    # Créer un contexte de test
    with Context() as context:
        # Créer une scène de test avec des obstacles
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

        calculator = SkyViewFactorCalculator(context, resolution=100)

        for point in test_points:
            print(f"\n📍 Point de test: ({point.x:.1f}, {point.y:.1f}, {point.z:.1f})")

            # Calcul avec toutes les méthodes
            results = calculator.calculate_svf_comprehensive(point)

            # Afficher les résultats
            for method, result in results.items():
                print(f"  {method}: SVF = {result.svf_value:.3f}")
                print(
                    f"    Ciel visible: {result.sky_visible:.0f}/{result.total_hemisphere}"
                )
                print(
                    f"    Obstacles: {result.obstacles_visible:.0f}/{result.total_hemisphere}"
                )

        # Calcul sur une grille
        print(f"\n🗺️  Calcul du SVF sur une grille...")
        grid_results = calculate_svf_grid(
            context,
            grid_center=vec3(0, 0, 1),
            grid_size=vec2(10, 10),
            grid_resolution=5,
        )

        print("📊 Résultats de la grille:")
        print(grid_results.head())

        # Sauvegarder les résultats
        grid_results.to_csv("svf_grid_results.csv", index=False)
        print("💾 Résultats sauvegardés dans svf_grid_results.csv")

        # Créer des visualisations
        if test_points:
            point_results = calculator.calculate_svf_comprehensive(test_points[0])
            create_svf_visualization(point_results)

        print("\n✅ Calcul du SVF terminé!")


if __name__ == "__main__":
    main()
