import math
import os
import platform
from typing import List, Tuple, Optional, Dict, Any

import imageio
import numpy as np
import pandas as pd
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import apply_surface_properties, SurfaceType
from sky_view_factor_calculation import SkyViewFactorCalculator, calculate_svf_grid
from simple_svf_calculator import create_svf_heatmap

"""
Type de Radiation	Plage de longueur d'onde	Application principale	Effet principal
SW (Short Wave)	0.1 µm - 4 µm	Chaleur solaire, photosynthèse, énergies renouvelables.	Chaleur directe reçue par la surface terrestre.
PAR (Photosynthetically Active Radiation)	0.4 µm - 0.7 µm	Photosynthèse, végétation.	Chaleur utile pour la croissance des plantes.
NIR (Near Infrared)	0.7 µm - 1.5 µm	Réflexion par la surface, télédétection.	Réflexion par les surfaces, indicateur d’humidité.
LW (Long Wave)	> 4 µm	Chaleur émise par la surface terrestre.	Chaleur émise par la surface et l’atmosphère.
"""
# https://drajmarsh.bitbucket.io/tree3d.html
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


def compute_sky_view_factor(context, uuids, n_rays=1000):
    """
    Calcule le Sky View Factor pour une liste de primitives (patches).
    """
    svf_dict = {}
    with RadiationModel(context) as rad:
        rad.addRadiationBand("SVF")
        rad.disableEmission("SVF")
        rad.setDiffuseRayCount("SVF", n_rays)
        rad.setScatteringDepth("SVF", 110)
        rad.runBand("SVF")

        for uuid in uuids:
            svf = context.getPrimitiveData(uuid, "radiation_flux_SVF")
            svf_dict[uuid] = svf
            print(svf)

    return svf_dict


def compute_MRT(context, ground_patches, output_dir, sigma=5.67e-8):
    """
    Calcule la Mean Radiant Temperature (MRT) pour chaque patch de sol.

    Args:
        context: objet pyhelios.Context
        ground_patches: liste 2D [[uuid_ij]] des patches du sol
        output_dir: dossier de sortie pour les fichiers CSV
        sigma: constante de Stefan-Boltzmann (W/m²·K⁴)

    Returns:
        df_MRT (DataFrame): température radiante moyenne (°C) pour chaque maille
    """
    ny, nx = len(ground_patches), len(ground_patches[0])
    MRT_matrix = np.zeros((ny, nx))

    for j in range(ny):
        for i in range(nx):
            uuid = ground_patches[j][i]

            # Flux long-onde descendant (atmosphère, W/m²)
            L_down = context.getPrimitiveData(uuid, "LW")
            # Flux émis par le patch (W/m²)
            Tg = context.getPrimitiveData(uuid, "temperature")
            emissivity = context.getPrimitiveData(uuid, "emissivity") or 0.96
            L_up = emissivity * sigma * (Tg**4)

            # Facteur de vue vers le ciel (si disponible)
            fsky = context.getPrimitiveData(uuid, "sky_view_factor") or 0.5

            # Conversion du flux descendant en température équivalente du ciel
            Tsky = (L_down / sigma) ** 0.25 if L_down else 273.15

            # MRT (K)
            Tmrt_K = ((fsky * Tsky**4 + (1 - fsky) * Tg**4)) ** 0.25
            MRT_matrix[j, i] = Tmrt_K - 273.15  # conversion °C

    df_MRT = pd.DataFrame(
        MRT_matrix,
        index=[f"y{j}" for j in range(ny)],
        columns=[f"x{i}" for i in range(nx)],
    )

    csv_path = os.path.join(output_dir, "MRT_map.csv")
    df_MRT.to_csv(csv_path)

    print(f"✅ Fichier MRT exporté : {csv_path}")
    print(f"MRT moyenne : {np.nanmean(MRT_matrix):.1f} °C")

    return df_MRT


# Fonction pour appliquer une rampe de variation
def get_ramped_value(
    min_value: float,
    max_value: float,
    current_hour: float,
    start_hour: float,
    end_hour: float,
) -> float:
    """
    Cette fonction génère une valeur variant linéairement entre min_value et max_value
    en fonction de l'heure actuelle, sur une période de start_hour à end_hour.

    Args:
        min_value: Valeur minimale de la rampe
        max_value: Valeur maximale de la rampe
        current_hour: Heure actuelle
        start_hour: Heure de début de la rampe
        end_hour: Heure de fin de la rampe

    Returns:
        Valeur interpolée entre min_value et max_value
    """
    # Calcul de la fraction de l'heure écoulée par rapport à la période définie
    fraction = (current_hour - start_hour) / (end_hour - start_hour)

    # Calcul de la valeur rampée
    return min_value + (max_value - min_value) * fraction


def getAmbientLongwaveFlux(temperature_K: float, humidity_rel: float) -> float:
    """
    Calcule le flux radiatif atmosphérique de grande longueur d’onde (W/m²)
    selon le modèle de Prata (1996).

    Paramètres
    ----------
    temperature_K : float
        Température de l’air en Kelvin.
    humidity_rel : float
        Humidité relative (entre 0 et 1).

    Retour
    ------
    float
        Flux de rayonnement long incident (W/m²)
    """
    # Constante de saturation de la vapeur d’eau (Pa)
    e0 = (
        611.0
        * math.exp(17.502 * (temperature_K - 273.0) / ((temperature_K - 273.0) + 240.9))
        * humidity_rel
    )

    # Coefficient de Prata (cm·K/Pa)
    K = 0.465

    # Variable intermédiaire
    xi = e0 / temperature_K * K

    # Émissivité atmosphérique selon Prata
    eps = 1.0 - (1.0 + xi) * math.exp(-math.sqrt(1.2 + 3.0 * xi))

    # Constante de Stefan-Boltzmann (W/m²·K⁴)
    sigma = 5.67e-8

    # Flux de rayonnement long (W/m²)
    return eps * sigma * (temperature_K**4)


def create_sample_tree(
    context: Context,
    species: WPTType = WPTType.APPLE,
    recursion_depth: int = 3,
    trunk_subdivisions: int = 12,
    branch_subdivisions: int = 12,
    leaf_subdivisions: Tuple[int, int] = (1, 1),
) -> Tuple[Optional[int], List[str], List[str]]:
    """
    Create a sample tree using WeberPennTree.

    Args:
        context: PyHelios context object
        species: Type of tree species to create
        recursion_depth: Depth of branch recursion
        trunk_subdivisions: Number of trunk subdivisions
        branch_subdivisions: Number of branch subdivisions
        leaf_subdivisions: Tuple of (x, y) leaf subdivisions

    Returns:
        Tuple containing:
            - tree_id: ID of the created tree (None if failed)
            - all_uuids: List of all primitive UUIDs
            - leaf_uuids: List of leaf primitive UUIDs
    """
    print("Creating sample tree...")

    try:
        with WeberPennTree(context) as wpt:
            # Set tree parameters for a nice-looking tree
            wpt.setBranchRecursionLevel(recursion_depth)
            wpt.setTrunkSegmentResolution(trunk_subdivisions)
            wpt.setBranchSegmentResolution(branch_subdivisions)
            wpt.setLeafSubdivisions(*leaf_subdivisions)

            # Build a lemon tree at a specific location
            tree_origin = vec3(10, 0, 0)

            tree_id = wpt.buildTree(
                species,
                origin=tree_origin,
            )

            # Get tree UUIDs for potential future use
            trunk_uuids = wpt.getTrunkUUIDs(tree_id)
            branch_uuids = wpt.getBranchUUIDs(tree_id)
            leaf_uuids = wpt.getLeafUUIDs(tree_id)

            # apply_surface_properties(
            #     context=context, uuids=trunk_uuids, surface_type=SurfaceType.TRUNK
            # )

            # Associer l'albédo à l'objet entier (plutôt qu'à des primitives)
            for trunk_uuid in trunk_uuids:
                context.setPrimitiveDataString(trunk_uuid, "plant_part", "trunk")
                context.setPrimitiveDataString(trunk_uuid, "species", str(species))

            # apply_surface_properties(
            #     context=context, uuids=branch_uuids, surface_type=SurfaceType.BRANCH
            # )

            # Associer l'albédo à l'objet entier (plutôt qu'à des primitives)
            for branch_uuid in branch_uuids:
                context.setPrimitiveDataString(branch_uuid, "plant_part", "branch")
                context.setPrimitiveDataString(branch_uuid, "species", str(species))

            # apply_surface_properties(
            #     context=context, uuids=leaf_uuids, surface_type=SurfaceType.LEAF
            # )

            # Associer l'albédo à l'objet entier (plutôt qu'à des primitives)
            for leaf_uuid in leaf_uuids:
                # context.setPrimitiveDataFloat(leaf_uuid, "transmissivity_PAR", 0.45)
                # context.setPrimitiveDataFloat(leaf_uuid, "transmissivity_NIR", 0.4)
                context.setPrimitiveDataString(leaf_uuid, "plant_part", "leaf")
                context.setPrimitiveDataString(leaf_uuid, "species", str(species))

            print(
                f"Created tree with {len(trunk_uuids)} trunk, {len(branch_uuids)} branch, and {len(leaf_uuids)} leaf primitives"
            )
            return tree_id, trunk_uuids + branch_uuids + leaf_uuids, leaf_uuids

    except Exception as e:
        print(
            f"Note: Tree creation failed (WeberPennTree plugin may not be available): {e}"
        )
        return None, [], []


def create_canopy(plantarch: PlantArchitecture) -> None:
    """
    Create a plant canopy using the PlantArchitecture model.

    Args:
        plantarch: PlantArchitecture object for canopy creation
    """
    # Simulate growth over time
    plantarch.loadPlantModelFromLibrary("apple")
    plant_uuids = plantarch.buildPlantCanopyFromLibrary(
        canopy_center=vec3(20, 0, 0),
        plant_spacing=vec2(1.5, 1.5),
        plant_count=int2(10, 10),
        age=365.0,
    )


def create_ground_patch(
    context: Context, center: vec3, size_total: vec2, dx: float, dy: float
) -> Tuple[List[str], List[List[str]]]:
    """
    Create a ground patch mesh with specified parameters.

    Args:
        context: PyHelios context object
        center: Center position of the ground patch
        size_total: Total size of the ground patch
        dx: Grid spacing in x direction
        dy: Grid spacing in y direction

    Returns:
        Tuple containing:
            - ground_uuids: List of all ground patch UUIDs
            - ground_patches: 2D list of ground patch UUIDs organized by row
    """
    # === Création du maillage de sol ===
    ground_patches = []
    ground_uuids = []
    x0 = center.x - size_total.x / 2 + dx / 2
    y0 = center.y - size_total.y / 2 + dy / 2

    for j in range(ny):
        row_patches = []
        for i in range(nx):
            cx = x0 + i * dx
            cy = y0 + j * dy
            color = (
                RGBcolor(0.5, 0.5, 0.5) if (i + j) % 2 == 0 else RGBcolor(0.0, 1.0, 1.0)
            )
            # color=RGBcolor(0.4, 0.3, 0.2),  # Brown soil
            ground_uuid = context.addPatch(
                center=vec3(cx, cy, 0), size=vec2(dx, dy), color=color
            )
            context.setPrimitiveDataString(ground_uuid, "plant_part", "soil")
            context.setPrimitiveDataString(ground_uuid, "surface_type", "soil")

            context.setPrimitiveDataFloat(ground_uuid, "temperature", 25.5)
            # Make sure that the ground is only able to intercept radiation from the top
            context.setPrimitiveDataUInt(ground_uuid, "twosided_flag", 0)

            row_patches.append(ground_uuid)
            ground_uuids.append(ground_uuid)
        ground_patches.append(row_patches)
    return ground_uuids, ground_patches


def main():
    with Context() as context:

        tree_id, tree_uuids, leaf_uuids = create_sample_tree(context=context)

        ground_uuids, ground_patches = create_ground_patch(
            context, center, size_total, dx, dy
        )

        apply_surface_properties(
            context=context, uuids=ground_uuids, surface_type=SurfaceType.SOIL
        )

        # uuids = context.loadOBJ("models/LABINTECH.obj")
        bat_uuids = context.loadOBJ(
            "models/MAISON_EP_1.obj",
            origin=vec3(0, 0, 0),  # position du modèle
            scale=vec3(1, 1, 1),  # pas de mise à l’échelle
            rotation=make_SphericalCoord(0, 0),  # pas de rotation
            color=RGBcolor(0.55, 0.36, 0.23),  # marron moyen
            upaxis="ZUP",  # axe vertical
            silent=False,
        )

        # bat_uuids = context.loadOBJ(
        #     "models/Mesh_Buildings.obj",
        #     origin=vec3(0, 0, 0),  # position du modèle
        #     scale=vec3(1, 1, 1),  # pas de mise à l’échelle
        #     rotation=make_SphericalCoord(0, 0),  # pas de rotation
        #     color=RGBcolor(0.55, 0.36, 0.23),  # marron moyen
        #     upaxis="ZUP",  # axe vertical
        #     silent=False,
        # )
        # pedestrian_uuids = context.loadOBJ(
        #     "models/Mesh_Pedestrian.obj",
        #     origin=vec3(0, 0, 0.2),  # position du modèle
        #     scale=vec3(1, 1, 1),  # pas de mise à l’échelle
        #     rotation=make_SphericalCoord(0, 0),  # pas de rotation
        #     color=RGBcolor(0.25, 0.25, 1),
        #     upaxis="ZUP",  # axe vertical
        #     silent=False,
        # )

        # for pedestrian_uuid in pedestrian_uuids:
        #     context.setPrimitiveDataString(pedestrian_uuid, "surface_type", "pedestrian")
        #     context.setPrimitiveDataString(pedestrian_uuid, "material", "soil_pedestrian")
        #     # Propriétés optiques
        #     context.setPrimitiveDataFloat(pedestrian_uuid, "reflectivity_SW", 0.25)
        #     context.setPrimitiveDataFloat(pedestrian_uuid, "reflectivity_PAR", 0.10)
        #     context.setPrimitiveDataFloat(pedestrian_uuid, "reflectivity_NIR", 0.35)

        # terrain_uuids = context.loadOBJ(
        #     "models/Mesh_Terrain.obj",
        #     origin=vec3(0, 0, 0.5),  # position du modèle
        #     scale=vec3(1, 1, 1),  # pas de mise à l’échelle
        #     rotation=make_SphericalCoord(0, 0),  # pas de rotation
        #     color=RGBcolor(0.25, 0.25, 0.25),
        #     upaxis="ZUP",  # axe vertical
        #     silent=False,
        # )
        #
        # for terrain_uuid in terrain_uuids:
        #     # Propriétés optiques de l'herbe
        #     context.setPrimitiveDataFloat(terrain_uuid, "reflectivity_SW", 0.25)
        #     context.setPrimitiveDataFloat(terrain_uuid, "reflectivity_PAR", 0.10)
        #     context.setPrimitiveDataFloat(terrain_uuid, "reflectivity_NIR", 0.50)
        #     context.setPrimitiveDataFloat(terrain_uuid, "transmissivity_PAR", 0.05)
        #     context.setPrimitiveDataFloat(terrain_uuid, "transmissivity_NIR", 0.10)
        #     context.setPrimitiveDataFloat(
        #         terrain_uuid, "reflectivity_LW", 0.03
        #     )  # faible réflexion IR lointain
        #     context.setPrimitiveDataString(terrain_uuid, "surface_type", "grass")
        #
        # water_uuids = context.loadOBJ(
        #     "models/Mesh_Water.obj",
        #     origin=vec3(0, 0, 0),  # position du modèle
        #     scale=vec3(1, 1, 1),  # pas de mise à l’échelle
        #     rotation=make_SphericalCoord(0, 0),  # pas de rotation
        #     color=RGBcolor(
        #         0.25, 0.55, 0.75
        #     ),  # bleu plus terne, tirant légèrement sur le vert
        #     upaxis="ZUP",  # axe vertical
        #     silent=False,
        # )
        #
        # for water_uuid in water_uuids:
        #     context.setPrimitiveDataFloat(water_uuid, "reflectivity_SW", 0.07)
        #     context.setPrimitiveDataFloat(water_uuid, "reflectivity_PAR", 0.06)
        #     context.setPrimitiveDataFloat(water_uuid, "reflectivity_NIR", 0.02)
        #     context.setPrimitiveDataFloat(water_uuid, "reflectivity_LW", 0.03)
        #     context.setPrimitiveDataString(water_uuid, "surface_type", "water")

        vertical_walls = []  # Liste pour stocker les UUID des parois verticales

        for bat_uuid in bat_uuids:
            context.setPrimitiveDataFloat(bat_uuid, "reflectivity_SW", 0.35)

            # Récupère la normale de la primitive
            normal = context.getPrimitiveNormal(bat_uuid)

            # On vérifie si la normale est proche de (0, 0, 1) ou (0, 0, -1), donc une paroi verticale
            if (
                np.isclose(normal.x, 0)
                and np.isclose(normal.y, 0)
                and (np.isclose(normal.z, 1) or np.isclose(normal.z, -1))
            ):
                vertical_walls.append(bat_uuid)

        # Affichage des UUID des parois verticales identifiées
        print(f"Parois verticales identifiées : {vertical_walls}")
        all_uuids = context.getAllUUIDs()

        compute_sky_view_factor(context, all_uuids)
        # context.writeOBJ("models/scene.obj")

        # === Patch de référence ===
        ref_ground_uuid = context.addPatch(
            center=vec3(-100, -100, 0), size=vec2(dx, dy), color=RGBcolor(0.2, 0.7, 0.2)
        )

        if platform.system() == "Darwin":
            # Create visualizer (smaller window for demo)
            with Visualizer(800, 600, headless=False) as visualizer:
                # Load all geometry into visualizer
                visualizer.buildContextGeometry(context)

                # Configure scene
                bg_color = RGBcolor(0.1, 0.1, 0.15)  # Dark blue background
                visualizer.setBackgroundColor(bg_color)
                light_dir = vec3(1, 1, 1)  # Directional lighting
                visualizer.setLightDirection(light_dir)
                visualizer.setLightingModel(
                    "phong_shadowed"
                )  # Nice lighting with shadows
                # visualizer.setLightingModel(visualizer.LIGHTING_NONE)    # Nice lighting with shadows
                # visualizer.buildContextGeometry(context)

                # visualizer.colorContextPrimitivesByData("radiation_flux_SW")
                #
                # visualizer.enableColorbar()
                # visualizer.setColorbarRange(200, 1000)
                # visualizer.setColorbarTitle("Radiation Flux")

                # Set a good camera position to view the scene
                camera_pos = vec3(8, 8, 6)  # Camera position
                look_at = vec3(1.5, 4.5, 3.5)  # Look at center of geometry
                visualizer.setCameraPosition(camera_pos, look_at)

                # Paramètres de la caméra
                radius = 15
                theta = 0.35
                phi = 0.4 * math.pi

                # Conversion de SphericalCoord à cartésien
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.sin(theta) * math.sin(phi)
                z = radius * math.cos(theta)

                # Création du vecteur de position de la caméra
                camera_position = vec3(x, y, z)

                # Position de la cible (pod’intérêt) de la caméra
                look_at = vec3(0, 0, 2)

                # Appliquer la position de la caméra dans le Visualizer
                visualizer.setCameraPosition(camera_position, look_at)
                visualizer.buildContextGeometry(context)

                print("Opening interactive visualization window...")
                print("Controls:")
                print("  - Mouse scroll: Zoom in/out")
                print("  - Left mouse + drag: Rotate camera")
                print("  - Right mouse + drag: Pan camera")
                print("  - Arrow keys: Camera movement")
                print("  - Close window to continue")

                # Show interactive visualization
                visualizer.plotInteractive()

        # print(context.getAllPrimitiveInfo())
        #
        # grid_results = calculate_svf_grid(
        #     context,
        #     grid_center=center,
        #     grid_size=size_total,
        #     grid_resolution=100,
        # )
        #
        # print("📊 Résultats de la grille:")
        # print(grid_results.head())
        #
        # # Sauvegarder les résultats
        # grid_results.to_csv("svf_grid_results.csv", index=False)
        # print("💾 Résultats sauvegardés dans svf_grid_results.csv")
        #
        # create_svf_heatmap(grid_results)

        exit()
        # === Simulation horaire ===
        ombres_par_heure = {}  # dict {hour: DataFrame}
        all_UUIDs = context.getAllUUIDs()

        context.setDate(2025, 6, 10)

        # Paramètres pour la rampe
        min_temperature_C = 25.0  # Température min en °C
        max_temperature_C = 40.0  # Température max en °C
        min_humidity = 0.4  # Humidité min
        max_humidity = 0.6  # Humidité max
        min_wind_speed = 0.9  # Vitesse du vent min en m/s
        max_wind_speed = 1.0  # Vitesse du vent max en m/s

        for i, hour in enumerate(hours):
            # for hour in range(12, 13):
            print(f"\n\nHOUR : {hour}\n\n")
            context.setTime(hour=hour)
            air_temperature_K = 288.15 + 10 * math.sin(math.pi * (hour - 6) / 12)  # K
            air_humidity = 0.6 - 0.2 * math.sin(math.pi * (hour - 6) / 12)  # 0-1

            # Vitesse du vent (de 0.3 m/s à 2.0 m/s entre 6h et 19h)
            wind_speed = get_ramped_value(min_wind_speed, max_wind_speed, hour, 6, 19)

            # Affichage des valeurs
            print(f"Température (K) : {air_temperature_K:.2f} K")
            print(f"Humidité relative : {air_humidity:.2f}")
            print(f"Vitesse du vent : {wind_speed:.2f} m/s\n")

            for uuid in all_UUIDs:
                context.setPrimitiveDataFloat(
                    uuid, "air_temperature", air_temperature_K
                )
                context.setPrimitiveDataFloat(uuid, "air_humidity", air_humidity)
                context.setPrimitiveDataFloat(uuid, "wind_speed", wind_speed)

            with SolarPosition(context, UTC, latitude, longitude) as solar_position:
                sun_dir = solar_position.getSunDirectionVector()
                # solar_position.enableCloudCalibration("cloud_cover")

                try:
                    with RadiationModel(context) as rad:
                        sun_source = rad.addCollimatedRadiationSource(sun_dir)

                        # Configure longwave radiation band
                        rad.addRadiationBand("LW")
                        rad.disableEmission("LW")
                        rad.setDirectRayCount(
                            "LW", 100
                        )  # plus de rayons = plus de précision
                        rad.setDiffuseRayCount("LW", 1000)

                        rad.addRadiationBand("NIR")
                        rad.disableEmission("NIR")
                        rad.setScatteringDepth("NIR", 3)

                        # Configure shortwave radiation band
                        rad.addRadiationBand("SW")
                        rad.disableEmission("SW")
                        rad.setScatteringDepth("SW", 3)
                        rad.setDirectRayCount(
                            "SW", 100
                        )  # plus de rayons = plus de précision
                        rad.setDiffuseRayCount("SW", 1000)

                        rad.addRadiationBand("PAR")
                        rad.disableEmission("PAR")
                        rad.setScatteringDepth("PAR", 3)

                        LW = getAmbientLongwaveFlux(
                            temperature_K=air_temperature_K, humidity_rel=air_humidity
                        )
                        print(
                            f"LW : flux radiatif atmosphérique de grande longueur d’onde (W/m²): {LW:.1f} W/m²"
                        )

                        PAR = solar_position.getSolarFluxPAR(
                            pressure_Pa=pressure,
                            temperature_K=air_temperature_K,
                            humidity_rel=air_humidity,
                            turbidity=turbidity,
                        )
                        print(
                            f"PAR (Photosynthetically Active Radiation) solar flux: {PAR:.1f} W/m²"
                        )

                        NIR = solar_position.getSolarFluxNIR(
                            pressure_Pa=pressure,
                            temperature_K=air_temperature_K,
                            humidity_rel=air_humidity,
                            turbidity=turbidity,
                        )
                        print(f"NIR (Near-Infrared) solar flux: {NIR:.1f} W/m²")

                        diffuse_fraction = solar_position.getDiffuseFraction(
                            pressure_Pa=pressure,
                            temperature_K=air_temperature_K,
                            humidity_rel=air_humidity,
                            turbidity=turbidity,
                        )
                        print(
                            f"Diffuse fraction of solar radiation : {diffuse_fraction:.3f} ({diffuse_fraction*100:.1f}%)"
                        )

                        rad.setSourceFlux(sun_source, "SW", 800)
                        rad.setDiffuseRadiationFlux("SW", 200)

                        rad.setSourceFlux(
                            sun_source, "NIR", NIR * (1.0 - diffuse_fraction)
                        )
                        rad.setDiffuseRadiationFlux("NIR", NIR * diffuse_fraction)

                        rad.setSourceFlux(
                            sun_source, "PAR", PAR * (1.0 - diffuse_fraction)
                        )
                        rad.setDiffuseRadiationFlux("PAR", PAR * diffuse_fraction)

                        rad.setDiffuseRadiationFlux("LW", LW)

                        rad.updateGeometry()

                        with BoundaryLayerConductanceModel(
                            context
                        ) as boundarylayerconductance:
                            boundarylayerconductance.setBoundaryLayerModel(
                                "Ground", ground_uuids
                            )
                            boundarylayerconductance.setBoundaryLayerModel(
                                "Pohlhausen", leaf_uuids
                            )
                            boundarylayerconductance.run()

                        rad.runBand(["SW", "PAR", "NIR", "LW"])

                        # Step 7: Setting Up the Stomatal Conductance Model
                        stomatalconductance = StomatalConductanceModel(context)
                        # Set model coefficients using species library
                        stomatalconductance.setBMFCoefficientsFromLibrary(
                            "Apple", uuids=leaf_uuids
                        )
                        # Run steady-state calculation
                        stomatalconductance.run(leaf_uuids)
                        # Or run dynamic simulation with timestep
                        # stomatal.run(dt=60.0)  # 60 second timestep
                        # # Set custom BMF coefficients for specific leaves
                        # bmf_coeffs = BMFCoefficients(Em=258.25, i0=38.65, k=232916.82, b=609.67)
                        # stomatal.setBMFCoefficients(bmf_coeffs, uuids=[leaf_uuid])

                        energybalance = EnergyBalanceModel(context)
                        energybalance.addRadiationBand("LW")
                        energybalance.addRadiationBand("PAR")
                        energybalance.addRadiationBand("NIR")
                        # energybalance.enableAirEnergyBalance()

                        energybalance.run()
                        # energybalance.evaluateAirEnergyBalance(
                        #     dt_sec=30.0, time_advance_sec=3600.0
                        # )

                        # Run the longwave band, stomatal conductance plugin, and energy balance plugin again to update primitive temperature values
                        rad.runBand("LW")

                        stomatalconductance.run(leaf_uuids)
                        energybalance.run()
                        # energybalance.evaluateAirEnergyBalance(
                        #     dt_sec=30.0, time_advance_sec=3600.0
                        # )

                        photosynthesis = PhotosynthesisModel(context)

                        photoparams = FarquharModelCoefficients()
                        photosynthesis.setFarquharModelCoefficients(photoparams)
                        photosynthesis.setModelTypeFarquhar()

                        photosynthesis.runForPrimitives(leaf_uuids)

                        # df_MRT = compute_MRT(context, ground_patches, output_dir)
                        # plt.imshow(df_MRT.values, cmap="inferno", origin="lower")
                        # plt.colorbar(label="MRT (°C)")
                        # plt.title("Mean Radiant Temperature")
                        # plt.savefig("MRT.png")

                        A_canopy = 0.0
                        E_canopy = 0.0
                        for UUID in leaf_uuids:
                            E = context.getPrimitiveData(UUID, "latent_flux")
                            A = context.getPrimitiveData(UUID, "net_photosynthesis")
                            E_canopy += E / 44000 * 1000
                            # mmol H2O / m^2 / sec
                            A_canopy += A  # umol CO2 / m^2 / sec

                            WUE = A / (E / 44000 * 1000)  # umol CO2/mmol H2O
                            context.setPrimitiveDataFloat(UUID, "WUE", WUE)

                        WUE_canopy = A_canopy / E_canopy  # umol CO2/mmol H2O
                        print(f"WUE of the canopy = {WUE_canopy} umol CO2/mmol H2O")

                        # Apply Helios pseudocolor mapping to all primitives
                        # all_uuids = context.getAllUUIDs()
                        # context.colorPrimitiveByDataPseudocolor(
                        #     uuids=all_uuids,
                        #     primitive_data="radiation_flux_SW",
                        #     colormap="hot",
                        #     ncolors=256,
                        # )

                        # flux de référence
                        irr_ref = context.getPrimitiveData(
                            ref_ground_uuid, "radiation_flux_SW"
                        )
                        if not irr_ref or irr_ref <= 0:
                            irr_ref = 1e-6  # éviter la division par zéro

                        # Calcul du flux sur chaque paroi verticale
                        wall_fluxes = []
                        for wall_uuid in vertical_walls:
                            flux = context.getPrimitiveData(
                                wall_uuid, "radiation_flux_SW"
                            )
                            if flux:
                                wall_fluxes.append(flux)
                            else:
                                wall_fluxes.append(0.0)

                        # Matrice des flux par heure
                        df_flux = pd.DataFrame(
                            wall_fluxes,
                            index=[f"Wall {i}" for i in range(len(wall_fluxes))],
                            columns=[f"hour_{hour}"],
                        )
                        ombres_par_heure[hour] = df_flux

                        print(
                            f"Heure {hour:02d}h : Flux sur murs = {np.sum(wall_fluxes):.1f} W/m²"
                        )

                        # Matrice numpy pour stocker les fractions
                        ombre_matrix = np.zeros((ny, nx))
                        temperature_matrix = np.zeros((ny, nx))

                        for j in range(ny):
                            for i in range(nx):
                                irr_sol = context.getPrimitiveData(
                                    ground_patches[j][i], "radiation_flux_SW"
                                )
                                temperature = context.getPrimitiveData(
                                    ground_patches[j][i], "temperature"
                                )
                                # print(f"temperature : {temperature-273.15}")
                                temperature_matrix[j, i] = temperature - 273.15

                                if irr_sol:
                                    ombre_matrix[j, i] = max(0, 1 - irr_sol / irr_ref)
                                else:
                                    ombre_matrix[j, i] = np.nan  # aucune donnée

                        # Convertir en DataFrame avec index spatiaux
                        df_ombre = pd.DataFrame(
                            ombre_matrix,
                            index=[f"y{j}" for j in range(ny)],
                            columns=[f"x{i}" for i in range(nx)],
                        )

                        df_temperature = pd.DataFrame(
                            temperature_matrix,
                            index=[f"y{j}" for j in range(ny)],
                            columns=[f"x{i}" for i in range(nx)],
                        )
                        ombres_par_heure[hour] = df_ombre
                        print(
                            f"Heure {hour:02d}h : ombre moyenne = {np.nanmean(ombre_matrix)*100:.1f}%"
                        )

                        import matplotlib.pyplot as plt

                        # --- Export CSV + Heatmap PNG ---
                        csv_path_ombre = os.path.join(
                            output_dir, f"ombre_{hour:02d}h.csv"
                        )
                        csv_path_temperature = os.path.join(
                            output_dir, f"temperature_{hour:02d}h.csv"
                        )

                        png_path_ombre = os.path.join(
                            output_dir, f"ombre_{hour:02d}h.png"
                        )
                        png_path_temperature = os.path.join(
                            output_dir, f"temperature_{hour:02d}h.png"
                        )

                        df_ombre.to_csv(csv_path_ombre)
                        df_temperature.to_csv(csv_path_temperature)

                        plt.figure(figsize=(6, 4))
                        plt.imshow(
                            df_ombre.values,
                            cmap="gray_r",
                            origin="lower",
                            extent=[0, nx, 0, ny],
                            vmin=0,
                            vmax=1,
                        )
                        plt.title(f"Fraction d’ombre à {hour}h")
                        plt.xlabel("X")
                        plt.ylabel("Y")
                        plt.colorbar(label="Fraction d’ombre")
                        plt.tight_layout()
                        plt.savefig(png_path_ombre, dpi=200)
                        plt.close()

                        plt.figure(figsize=(6, 4))
                        plt.imshow(
                            df_temperature.values,
                            cmap="magma",
                            origin="lower",
                            extent=[0, nx, 0, ny],
                            vmin=20,
                            vmax=50,
                        )
                        plt.title(f"Temperature (°C) à {hour}h")
                        plt.xlabel("X")
                        plt.ylabel("Y")
                        plt.colorbar(label="Temperature")
                        plt.tight_layout()
                        plt.savefig(png_path_temperature, dpi=200)
                        plt.close()

                except Exception as e:
                    print(f"Radiation modeling not available: {e}")
                    exit()


def animation():

    # === ANIMATION JOURNALIÈRE ===
    images_ombre = []
    images_temperature = []
    for i, hour in enumerate(hours):
        png_path_ombre = os.path.join(output_dir, f"ombre_{hour:02d}h.png")
        png_path_temperature = os.path.join(output_dir, f"temperature_{hour:02d}h.png")
        if os.path.exists(png_path_ombre):
            images_ombre.append(imageio.v3.imread(png_path_ombre))
        if os.path.exists(png_path_temperature):
            images_temperature.append(imageio.v3.imread(png_path_temperature))

    if images_ombre:
        gif_path = os.path.join(output_dir, "animation_ombres.gif")
        imageio.mimsave(gif_path, images_ombre, fps=2)
        print(f"\n✅ Animation créée : {gif_path}")

    if images_temperature:
        gif_path = os.path.join(output_dir, "animation_temperature.gif")
        imageio.mimsave(gif_path, images_temperature, fps=2)
        print(f"\n✅ Animation créée : {gif_path}")


if __name__ == "__main__":
    latitude = -1.15
    longitude = 46.166672
    UTC = 1

    pressure = 101300
    turbidity = 0.05

    # Paramètres du sol
    # center = vec3(0, 50, 0)
    center = vec3(0, 0, 0)
    # size_total = vec2(450, 150)     # taille globale du sol (m)
    size_total = vec2(50, 50)  # taille globale du sol (m)
    nx, ny = 200, 200  # nombre de subdivisions

    dx = size_total.x / nx
    dy = size_total.y / ny

    output_dir = "resultats_ombres"
    os.makedirs(output_dir, exist_ok=True)

    hours = [6, 10, 12, 14, 18]  # Days to advance
    main()
