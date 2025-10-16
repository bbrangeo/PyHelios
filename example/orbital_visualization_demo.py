"""
Démonstration du mouvement orbital dans PyHelios Visualizer.

Ce script montre comment utiliser les nouvelles fonctionnalités de mouvement orbital
ajoutées au Visualizer PyHelios.
"""

import math
import time
from typing import List, Tuple, Optional

from pyhelios import Context, Visualizer, WeberPennTree, WPTType
from pyhelios.types import vec3, RGBcolor, make_vec3


def create_simple_scene(context: Context) -> Tuple[Optional[int], List[str]]:
    """
    Crée une scène simple pour la démonstration orbitale.

    Args:
        context: Contexte PyHelios

    Returns:
        Tuple contenant l'ID de l'arbre et la liste des UUIDs
    """
    print("🌳 Création d'une scène simple...")

    # Créer un arbre simple
    try:
        with WeberPennTree(context) as wpt:
            wpt.setBranchRecursionLevel(2)
            wpt.setTrunkSegmentResolution(8)
            wpt.setBranchSegmentResolution(8)
            wpt.setLeafSubdivisions(1, 1)

            tree_origin = vec3(0, 0, 0)
            tree_id = wpt.buildTree(WPTType.APPLE, origin=tree_origin)

            # Récupérer les UUIDs
            trunk_uuids = wpt.getTrunkUUIDs(tree_id)
            branch_uuids = wpt.getBranchUUIDs(tree_id)
            leaf_uuids = wpt.getLeafUUIDs(tree_id)

            # Configurer les propriétés
            all_uuids = trunk_uuids + branch_uuids + leaf_uuids

            for trunk_uuid in trunk_uuids:
                context.setPrimitiveDataFloat(trunk_uuid, "reflectivity_SW", 0.6)
                context.setPrimitiveDataString(trunk_uuid, "plant_part", "trunk")

            for branch_uuid in branch_uuids:
                context.setPrimitiveDataFloat(branch_uuid, "reflectivity_SW", 0.6)
                context.setPrimitiveDataString(branch_uuid, "plant_part", "branch")

            for leaf_uuid in leaf_uuids:
                context.setPrimitiveDataFloat(leaf_uuid, "reflectivity_SW", 0.2)
                context.setPrimitiveDataString(leaf_uuid, "plant_part", "leaf")

            print(f"✅ Scène créée avec {len(all_uuids)} primitives")
            return tree_id, all_uuids

    except Exception as e:
        print(f"❌ Erreur lors de la création de la scène: {e}")
        return None, []


def orbital_animation_demo(visualizer: Visualizer, center_point: vec3) -> None:
    """
    Démonstration de différentes animations orbitales.

    Args:
        visualizer: Objet Visualizer PyHelios
        center_point: Point central pour l'orbite
    """
    print("🎬 Démonstration des animations orbitales")
    print("=" * 50)

    # Configuration 1: Orbite lente et fluide
    print("\n1️⃣ Animation lente et fluide...")
    create_orbital_camera_animation(
        visualizer=visualizer,
        center_point=center_point,
        radius=15.0,
        duration=10.0,
        elevation_range=(0.3, 1.0),
        num_frames=60,
    )

    time.sleep(1)  # Pause entre les animations

    # Configuration 2: Orbite rapide et dynamique
    print("\n2️⃣ Animation rapide et dynamique...")
    create_orbital_camera_animation(
        visualizer=visualizer,
        center_point=center_point,
        radius=20.0,
        duration=5.0,
        elevation_range=(0.1, 1.2),
        num_frames=30,
    )

    time.sleep(1)

    # Configuration 3: Orbite serrée et détaillée
    print("\n3️⃣ Animation serrée et détaillée...")
    create_orbital_camera_animation(
        visualizer=visualizer,
        center_point=center_point,
        radius=8.0,
        duration=8.0,
        elevation_range=(0.4, 0.9),
        num_frames=40,
    )


def create_orbital_camera_animation(
    visualizer: Visualizer,
    center_point: vec3,
    radius: float = 15.0,
    duration: float = 10.0,
    elevation_range: Tuple[float, float] = (0.2, 1.2),
    num_frames: int = 60,
) -> None:
    """
    Crée une animation orbitale de la caméra autour d'un point central.

    Args:
        visualizer: Objet Visualizer PyHelios
        center_point: Point central autour duquel la caméra va orbiter
        radius: Rayon de l'orbite
        duration: Durée de l'animation en secondes
        elevation_range: Plage d'élévation (theta min, theta max) en radians
        num_frames: Nombre de frames pour l'animation
    """
    print(f"🎬 Animation orbitale - Rayon: {radius:.1f}, Durée: {duration:.1f}s")

    # Calcul des paramètres d'animation
    frame_duration = duration / num_frames
    theta_min, theta_max = elevation_range

    for frame in range(num_frames):
        # Calcul de l'angle azimutal (phi) - rotation complète
        phi = 2 * math.pi * frame / num_frames

        # Calcul de l'angle d'élévation (theta) - oscillation entre min et max
        theta = theta_min + (theta_max - theta_min) * (
            0.5 + 0.5 * math.sin(2 * math.pi * frame / num_frames)
        )

        # Conversion des coordonnées sphériques en cartésiennes
        x = center_point.x + radius * math.sin(theta) * math.cos(phi)
        y = center_point.y + radius * math.sin(theta) * math.sin(phi)
        z = center_point.z + radius * math.cos(theta)

        # Position de la caméra
        camera_position = vec3(x, y, z)

        # La caméra regarde toujours vers le centre
        look_at = center_point

        # Mise à jour de la position de la caméra
        visualizer.setCameraPosition(camera_position, look_at)

        # Mise à jour de l'affichage
        visualizer.plotUpdate()

        # Pause pour l'animation
        time.sleep(frame_duration)

        # Affichage du progrès
        if frame % 10 == 0:
            progress = (frame / num_frames) * 100
            print(
                f"   Progrès: {progress:.0f}% - Position: ({x:.1f}, {y:.1f}, {z:.1f})"
            )

    print("✅ Animation terminée!")


def main():
    """
    Fonction principale de démonstration.
    """
    print("🚀 Démonstration du mouvement orbital PyHelios")
    print("=" * 60)

    # Créer le contexte
    with Context() as context:
        # Créer une scène simple
        tree_id, all_uuids = create_simple_scene(context)

        if tree_id is None:
            print("❌ Impossible de créer la scène")
            return

        # Créer le visualizer
        with Visualizer(800, 600, headless=False) as visualizer:
            # Charger la géométrie
            visualizer.buildContextGeometry(context)

            # Configurer la scène
            visualizer.setBackgroundColor(RGBcolor(0.1, 0.1, 0.15))
            visualizer.setLightDirection(vec3(1, 1, 1))
            visualizer.setLightingModel("phong_shadowed")

            # Point central pour l'orbite
            orbit_center = vec3(0, 0, 2)

            # Position initiale de la caméra
            initial_radius = 15.0
            initial_theta = 0.6
            initial_phi = 0.0

            x = orbit_center.x + initial_radius * math.sin(initial_theta) * math.cos(
                initial_phi
            )
            y = orbit_center.y + initial_radius * math.sin(initial_theta) * math.sin(
                initial_phi
            )
            z = orbit_center.z + initial_radius * math.cos(initial_theta)

            visualizer.setCameraPosition(vec3(x, y, z), orbit_center)

            print("\n🎮 Contrôles disponibles:")
            print("  - Souris: Navigation manuelle")
            print("  - Fermer la fenêtre pour quitter")

            # Démarrer les animations orbitales
            try:
                orbital_animation_demo(visualizer, orbit_center)
            except KeyboardInterrupt:
                print("\n⏹️ Démonstration interrompue")
            except Exception as e:
                print(f"\n❌ Erreur: {e}")

            print("\n🎮 Mode interactif - vous pouvez maintenant naviguer manuellement")
            visualizer.plotInteractive()


if __name__ == "__main__":
    main()
