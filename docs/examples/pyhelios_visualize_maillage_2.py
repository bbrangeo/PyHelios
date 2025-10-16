import math
import os

import imageio
import numpy as np
import pandas as pd

# https://drajmarsh.bitbucket.io/tree3d.html
from pyhelios import (
    Context,
    RadiationModel,
    SolarPosition,
    Visualizer,
    WeberPennTree,
    WPTType,
)

from pyhelios.types import *


def create_sample_tree(context):
    """Create a sample tree using WeberPennTree."""
    print("Creating sample tree...")

    try:
        with WeberPennTree(context) as wpt:
            # Set tree parameters for a nice-looking tree
            wpt.setBranchRecursionLevel(3)
            wpt.setTrunkSegmentResolution(12)
            wpt.setBranchSegmentResolution(8)
            wpt.setLeafSubdivisions(4, 4)

            # Build a lemon tree at a specific location
            tree_origin = vec3(10, 0, 0)
            tree_id = wpt.buildTree(WPTType.APPLE, origin=tree_origin)

            # Get tree UUIDs for potential future use
            trunk_uuids = wpt.getTrunkUUIDs(tree_id)
            branch_uuids = wpt.getBranchUUIDs(tree_id)
            leaf_uuids = wpt.getLeafUUIDs(tree_id)

            print(
                f"Created tree with {len(trunk_uuids)} trunk, {len(branch_uuids)} branch, and {len(leaf_uuids)} leaf primitives"
            )
            return tree_id, trunk_uuids + branch_uuids + leaf_uuids

    except Exception as e:
        print(
            f"Note: Tree creation failed (WeberPennTree plugin may not be available): {e}"
        )
        return None, []


latitude = -1.15
longitude = 46
UTC = 7

# Paramètres du sol
# center = vec3(0, 50, 0)
center = vec3(0, 0, 0)
# size_total = vec2(450, 150)     # taille globale du sol (m)
size_total = vec2(50, 50)  # taille globale du sol (m)
nx, ny = 100, 100  # nombre de subdivisions

dx = size_total.x / nx
dy = size_total.y / ny

# Paramètres
D = 50  # Dimension totale (en m)
size = vec2(10, 10)  # Nombre de patches en X et Y
subsize = vec2(50, 50)  # Subdivision des patches

# Calcul des espacements
dx_ = vec2(D / (size.x * subsize.x), D / (size.y * subsize.y))

output_dir = "resultats_ombres"
os.makedirs(output_dir, exist_ok=True)

with Context() as context:
    # tree_id, tree_uuids = create_sample_tree(context)

    # uuids = context.loadOBJ("models/LABINTECH.obj")
    uuids = context.loadOBJ("models/MAISON_EP_1.obj")

    UUID = None
    rho = 0.0  # Réflectivité par défaut

    # Boucle sur les "patches" principaux
    for j in range(int(size.y)):
        for i in range(int(size.x)):
            # Rotation des patches (seulement dans un cas particulier)
            rot = ((j * int(size.x) + i) % 3) * math.pi * 0.5

            # Boucle sur les sous-éléments (patches secondaires)
            for jj in range(int(subsize.y)):
                for ii in range(int(subsize.x)):
                    # Calcul des coordonnées
                    x = -0.5 * D + (i * subsize.x + ii) * dx_.x
                    y = -0.5 * D + (j * subsize.y + jj) * dx_.y

                    # Définition de la couleur et réflectivité
                    if (j * int(size.x) + i) % 2 == 0:
                        color = RGBcolor(0.75, 0.75, 0.75)  # Silver
                        rho = 0.0  # Réflectivité pour silver
                    else:
                        color = RGBcolor(1.0, 1.0, 1.0)  # White
                        rho = 0.6  # Réflectivité pour white

                    # Création du patch
                    UUID = context.addPatch(
                        center=vec3(x, y, 0),
                        size=dx_,  # Taille de chaque patch
                        rotation=SphericalCoord(0.01, rot),  # Rotation
                        color=color,
                    )

                    # Application de la donnée de réflectivité
                    context.setPrimitiveDataFloat(UUID, "reflectivity_SW", rho)

    ombres_par_heure = {}  # dict {hour: DataFrame}

    for hour in range(6, 19):
        context.setDate(2025, 6, 10)
        context.setTime(hour=hour)
        solar_position = SolarPosition(context, UTC, latitude, longitude)
        sun_dir = solar_position.getSunDirectionVector()
        try:
            with RadiationModel(context) as rad:
                sun_source = rad.addCollimatedRadiationSource(sun_dir)

                rad.addRadiationBand("SW")
                rad.setDirectRayCount("SW", 1000)  # plus de rayons = plus de précision
                rad.disableEmission("SW")
                rad.setDiffuseRayCount("SW", 300)
                rad.setSourceFlux(sun_source, "SW", 800)
                rad.setDiffuseRadiationFlux("SW", 200)
                rad.setScatteringDepth("SW", 3)

                rad.updateGeometry()
                rad.runBand("SW")

        except Exception as e:
            print(f"Radiation modeling not available: {e}")

    # Create visualizer (smaller window for demo)
    with Visualizer(800, 600, headless=False) as visualizer:
        # Load all geometry into visualizer
        visualizer.buildContextGeometry(context)

        # Configure scene
        bg_color = RGBcolor(0.1, 0.1, 0.15)  # Dark blue background
        visualizer.setBackgroundColor(bg_color)
        light_dir = vec3(1, 1, 1)  # Directional lighting
        visualizer.setLightDirection(light_dir)
        # visualizer.setLightingModel("phong_shadowed")    # Nice lighting with shadows
        visualizer.setLightingModel(
            visualizer.LIGHTING_NONE
        )  # Nice lighting with shadows
        visualizer.buildContextGeometry(context)

        visualizer.colorContextPrimitivesByData("radiation_flux_SW")

        visualizer.enableColorbar()
        visualizer.setColorbarRange(200, 1000)
        visualizer.setColorbarTitle("Radiation Flux")

        # Set a good camera position to view the scene
        camera_pos = vec3(8, 8, 6)  # Camera position
        look_at = vec3(1.5, 4.5, 3.5)  # Look at center of geometry
        visualizer.setCameraPosition(camera_pos, look_at)

        print("Opening interactive visualization window...")
        print("Controls:")
        print("  - Mouse scroll: Zoom in/out")
        print("  - Left mouse + drag: Rotate camera")
        print("  - Right mouse + drag: Pan camera")
        print("  - Arrow keys: Camera movement")
        print("  - Close window to continue")

        # Show interactive visualization
        visualizer.plotInteractive()

# === ANIMATION JOURNALIÈRE ===
images = []
for hour in range(6, 19):
    png_path = os.path.join(output_dir, f"ombre_{hour:02d}h.png")
    if os.path.exists(png_path):
        images.append(imageio.imread(png_path))
if images:
    gif_path = os.path.join(output_dir, "animation_ombres.gif")
    imageio.mimsave(gif_path, images, fps=2)
    print(f"\n✅ Animation créée : {gif_path}")
