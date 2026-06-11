import math
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from example.improved_radiation_calculation import (
    SURFACE_PROPERTIES_2,
    SurfaceType,
    apply_surface_properties,
)
from example.pyhelios_radiation_pure import compute_MRT
import example.pyhelios_svf_radiation_tmrt as tmrt_base
from example.pyhelios_svf_radiation_tmrt import (
    create_ground_patch,
    create_sample_tree,
    _getAmbientLongwaveFlux,
    get_ramped_value,
)
from pyhelios import (
    BoundaryLayerConductanceModel,
    CameraProperties,
    Context,
    EnergyBalanceModel,
    PhotosynthesisModel,
    PlantArchitecture,
    RadiationModel,
    SkyViewFactorModel,
    SolarPosition,
    StomatalConductanceModel,
    Visualizer,
)
from pyhelios.types import FarquharModelCoefficients, RGBcolor, vec2, vec3

# RadiationModel — données primitives d'entrée : voir example/helios_radiation_primitive_data_docs.py

# Configuration globale des arbres apple autour du bâtiment
TREE_RING_COUNT_PER_SIDE = 2
TREE_RING_SPACING = 3.5
TREE_RING_OFFSET = 2.5
TREE_AGE = 365.0

# Paramètres disponibles pour les arbres
TREE_BUILD_PARAMETERS = {
    "trunk_height":   0.6,   # hauteur tronc en m (défaut 0.6–1.0)
    "num_scaffolds":  3.0,   # nb branches charpentières (défaut 4, max 8)
    "scaffold_angle": 45.0,  # angle branches en degrés (défaut 40–50)
}
TREE_MODEL_LABEL: str = "olive"

# Heure de la journee simulee pour l'export camera (une fois par etape de croissance).
CAMERA_EXPORT_HOUR = 12

# Bornes spectrales (nm) requises pour cameras + modele de ciel de Prague.
RADIATION_BAND_WAVELENGTHS_NM: Dict[str, Tuple[int, int]] = {
    "PAR": (400, 700),
    "NIR": (701, 2500),
    "SW": (400, 2500),
}

# Correspondance libellé PlantArchitecture → espèce bibliothèque stomatique Helios.
STOMATAL_SPECIES_BY_TREE_LABEL: Dict[str, str] = {
    "olive": "Olive",
    "apple": "Apple",
    "almond": "Almond",
    "lemon": "Lemon",
    "grape": "Grape",
    "walnut": "Walnut",
}


def get_xy_bounds_from_uuids(context: Context, uuids: List[str]) -> Tuple[float, float, float, float]:
    """Calcule l'emprise XY d'une liste de primitives."""
    if not uuids:
        raise ValueError("La liste des UUID du bâtiment est vide.")

    xs: List[float] = []
    ys: List[float] = []
    for uuid in uuids:
        vertices = context.getPrimitiveVertices(uuid)
        xs.extend(vertex.x for vertex in vertices)
        ys.extend(vertex.y for vertex in vertices)

    if not xs or not ys:
        raise ValueError("Impossible de calculer l'emprise XY du bâtiment.")

    return min(xs), max(xs), min(ys), max(ys)


def reduce_shoot_parameters(plant_architecture: PlantArchitecture, shoot_types: list) -> None:
    """Réduit la densité des tiges pour limiter le nombre de primitives."""
    for shoot_type in shoot_types:
        try:
            # Récupérer les paramètres actuels — retourne un dict
            params = plant_architecture.getCurrentShootParameters(shoot_type)

            # Modifier directement les clés du dictionnaire
            params["max_nodes"]["parameters"] = [10.0, 14.0]
            params["max_nodes_per_season"]["parameters"] = [5.0, 7.0]
            params["internode_length_max"]["parameters"] = [0.08]
            params["vegetative_bud_break_probability_min"]["parameters"] = [0.015]

            # Réappliquer via defineShootType (pas updateCurrentShootParameters)
            plant_architecture.defineShootType(shoot_type, params)
            print(f"  ✓ Paramètres réduits pour: {shoot_type}")

        except Exception as e:
            print(f"  ✗ shoot type '{shoot_type}' ignoré: {e}")

def create_apple_ring_around_building(
    context: Context,
    plant_architecture: PlantArchitecture,
    building_uuids: List[str],
    tree_model_label: str = TREE_MODEL_LABEL,
    count_per_side: int = TREE_RING_COUNT_PER_SIDE,
    spacing: float = TREE_RING_SPACING,
    offset: float = TREE_RING_OFFSET,
    age: float = TREE_AGE,
    build_parameters: Optional[Dict[str, float]] = TREE_BUILD_PARAMETERS,
) -> List[int]:
    """Cree un anneau d'arbres apple autour de l'emprise du batiment."""
    if count_per_side < 1:
        raise ValueError("count_per_side doit etre >= 1.")
    if spacing <= 0:
        raise ValueError("spacing doit etre strictement positif.")
    if offset < 0:
        raise ValueError("offset doit etre >= 0.")
    if age < 0:
        raise ValueError("age doit etre >= 0.")

    x_min, x_max, y_min, y_max = get_xy_bounds_from_uuids(context, building_uuids)
    x_min -= offset
    x_max += offset
    y_min -= offset
    y_max += offset

    x_start = (x_min + x_max) / 2.0 - ((count_per_side - 1) * spacing) / 2.0
    y_start = (y_min + y_max) / 2.0 - ((count_per_side - 1) * spacing) / 2.0

    positions = []
    for idx in range(count_per_side):
        x = x_start + idx * spacing
        y = y_start + idx * spacing
        positions.extend(
            [
                (x, y_min),  # Sud
                (x, y_max),  # Nord
                (x_min, y),  # Ouest
                (x_max, y),  # Est
            ]
        )

    # Retire les doublons possibles aux coins
    unique_positions = list(dict.fromkeys(positions))

    if not tree_model_label.strip():
        raise ValueError("tree_model_label doit etre une chaine non vide.")

    plant_architecture.loadPlantModelFromLibrary(tree_model_label)


    plant_ids: List[int] = []
    for x, y in unique_positions:
        plant_id = plant_architecture.buildPlantInstanceFromLibrary(
            base_position=vec3(x, y, 0.0),
            age=age,
            build_parameters=build_parameters,
        )
        plant_ids.append(plant_id)

    return plant_ids


def compute_ground_sky_view_factors(
    context: Context,
    ground_uuids: List[int],
    ray_count: int = 400,
    max_ray_length: float = 400.0,
    num_threads: int = 8,
) -> None:
    """Calcule et enregistre sky_view_factor sur les patches de sol."""
    svf_model = SkyViewFactorModel(context)
    svf_model.set_ray_count(ray_count)
    svf_model.set_max_ray_length(max_ray_length)
    svf_model.set_message_flag(True)
    svf_model.calculate_sky_view_factors_for_primitives(
        uuids=ground_uuids, num_threads=num_threads
    )


def stomatal_species_for_tree_label(tree_model_label: str) -> str:
    """Retourne le nom d'espèce stomatique Helios associé au libellé de plante."""
    return STOMATAL_SPECIES_BY_TREE_LABEL.get(tree_model_label.strip().lower(), "Apple")


def filter_uuids_by_plant_part(
    context: Context, uuids: List[int], plant_part: str
) -> List[int]:
    """Filtre les UUID dont plant_part correspond (ex. « leaf »)."""
    matched: List[int] = []
    for uuid in uuids:
        if context.doesPrimitiveDataExist(uuid, "plant_part"):
            if context.getPrimitiveData(uuid, "plant_part") == plant_part:
                matched.append(uuid)
    return matched


def apply_wpt_sample_tree_surface_properties(
    context: Context,
    all_tree_uuids: List[int],
    wpt_leaf_uuids: List[int],
) -> None:
    """Applique SURFACE_PROPERTIES au WeberPennTree (tronc, branches, feuilles)."""
    if not all_tree_uuids:
        return
    leaf_set = set(wpt_leaf_uuids)
    trunk_branch_uuids = [u for u in all_tree_uuids if u not in leaf_set]
    if trunk_branch_uuids:
        apply_surface_properties(context, trunk_branch_uuids, SurfaceType.TRUNK)
        for uuid in trunk_branch_uuids:
            context.setPrimitiveDataString(uuid, "plant_part", "trunk")
    if wpt_leaf_uuids:
        apply_surface_properties(context, wpt_leaf_uuids, SurfaceType.LEAF)
        leaf_props = SURFACE_PROPERTIES_2[SurfaceType.LEAF]
        context.setPrimitiveDataFloat(wpt_leaf_uuids, "transmissivity_PAR", 0.45)
        context.setPrimitiveDataFloat(wpt_leaf_uuids, "transmissivity_NIR", 0.40)
        for uuid in wpt_leaf_uuids:
            context.setPrimitiveDataString(uuid, "plant_part", "leaf")


def get_plant_primitive_uuids(
    plant_architecture: PlantArchitecture, plant_ids: List[int]
) -> List[int]:
    """Retourne tous les UUID de primitives associes a des plants."""
    plant_uuids: List[int] = []
    for plant_id in plant_ids:
        plant_uuids.extend(plant_architecture.getAllPlantUUIDs(plant_id))
    return plant_uuids


def configure_plant_primitives(
    context: Context,
    plant_architecture: PlantArchitecture,
    plant_ids: List[int],
) -> List[int]:
    """Applique les proprietes optiques feuille (SURFACE_PROPERTIES) aux plants."""
    plant_uuids = get_plant_primitive_uuids(plant_architecture, plant_ids)
    if not plant_uuids:
        return plant_uuids

    apply_surface_properties(context, plant_uuids, SurfaceType.LEAF)
    # transmissivity_* — canopy : valeurs complementaires non presentes dans SurfaceProperties.
    context.setPrimitiveDataFloat(plant_uuids, "transmissivity_PAR", 0.45)
    context.setPrimitiveDataFloat(plant_uuids, "transmissivity_NIR", 0.40)
    for plant_uuid in plant_uuids:
        context.setPrimitiveDataString(plant_uuid, "plant_part", "leaf")
    return plant_uuids


def add_growth_radiation_bands(radiation: RadiationModel) -> None:
    """Ajoute les bandes SW/PAR/NIR/LW avec bornes spectrales pour les cameras."""
    radiation.addRadiationBand("LW")
    for band_label, (wavelength_min, wavelength_max) in RADIATION_BAND_WAVELENGTHS_NM.items():
        radiation.addRadiationBand(band_label, wavelength_min, wavelength_max)


def setup_radiation_cameras(
    radiation: RadiationModel,
    scene_center: vec3 = vec3(0, 0, 0),
) -> None:
    """Enregistre les cameras de ray-tracing avant updateGeometry et runBand."""
    overhead_props = CameraProperties(camera_resolution=(1024, 1024), HFOV=60.0)
    radiation.addRadiationCamera(
        camera_label="overhead_rgb",
        band_labels=["PAR", "NIR", "SW"],
        position=vec3(scene_center.x, scene_center.y, 35.0),
        lookat_or_direction=vec3(scene_center.x, scene_center.y, 0.0),
        camera_properties=overhead_props,
        antialiasing_samples=50,
    )
    radiation.addRadiationCamera(
        camera_label="side_view",
        band_labels=["NIR"],
        position=vec3(30.0, 0.0, 5.0),
        lookat_or_direction=vec3(0.0, 0.0, 1.5),
        camera_properties=CameraProperties(camera_resolution=(1024, 512), HFOV=45.0),
        antialiasing_samples=50,
    )


def setup_camera_ml_labels(
    context: Context,
    leaf_uuids: List[int],
    trunk_uuids: List[int],
    ground_uuids: List[int],
) -> None:
    """Assigne des champs UINT pour les APIs camera ML (bounding boxes, segmentation)."""
    if leaf_uuids:
        context.setPrimitiveDataUInt(leaf_uuids, "cam_leaf", 1)
    if trunk_uuids:
        context.setPrimitiveDataUInt(trunk_uuids, "cam_trunk", 1)
    if ground_uuids:
        context.setPrimitiveDataUInt(ground_uuids, "cam_soil", 1)


def export_growth_camera_outputs(
    radiation: RadiationModel,
    output_dir: str,
    age: float,
    hour: int,
) -> None:
    """Exporte images camera, labels YOLO et masques de segmentation.

    autoCalibrateCameraImage est exclu : il exige une mire (DGK/Calibrite/Spyder)
    visible par la camera, absente de cette scene agricole.
    """
    rgb_filename = radiation.writeCameraImage(
        camera="overhead_rgb",
        bands=["PAR", "NIR", "SW"],
        imagefile_base=f"canopy_rgb_{int(age)}days_{hour:02d}h",
        image_path=output_dir,
    )
    if not rgb_filename:
        raise RuntimeError("Camera image export failed for overhead_rgb")

    nir_filename = radiation.writeCameraImage(
        camera="side_view",
        bands=["NIR"],
        imagefile_base=f"canopy_nir_{int(age)}days_{hour:02d}h",
        image_path=output_dir,
    )

    radiation.writeImageBoundingBoxes(
        camera_label="overhead_rgb",
        primitive_data_labels=["cam_leaf", "cam_trunk", "cam_soil"],
        object_class_ids=[0, 1, 2],
        image_file=rgb_filename,
        classes_txt_file="plant_classes.txt",
        image_path=output_dir,
    )

    radiation.writeImageSegmentationMasks(
        camera_label="overhead_rgb",
        primitive_data_labels=["cam_leaf", "cam_trunk", "cam_soil"],
        object_class_ids=[0, 1, 2],
        json_filename=os.path.join(output_dir, f"segmentation_{int(age)}days_{hour:02d}h.json"),
        image_file=rgb_filename,
    )

    print("Camera pipeline completed:")
    print(f"  RGB Image: {rgb_filename}")
    print(f"  NIR Image: {nir_filename}")
    print("  Training data: plant_classes.txt + YOLO format labels")
    print(f"  Segmentation: segmentation_{int(age)}days_{hour:02d}h.json")


def apply_ground_surface_properties(
    context: Context,
    ground_uuids: List[int],
    initial_temperature_k: float = 25.5 + 273.15,
) -> None:
    """Applique SOIL (SURFACE_PROPERTIES) et options sol unilateral."""
    if not ground_uuids:
        return
    apply_surface_properties(context, ground_uuids, SurfaceType.SOIL)
    for ground_uuid in ground_uuids:
        context.setPrimitiveDataFloat(ground_uuid, "temperature", initial_temperature_k)
        context.setPrimitiveDataUInt(ground_uuid, "twosided_flag", 0)
        context.setPrimitiveDataString(ground_uuid, "plant_part", "soil")
        context.setPrimitiveDataFloat(ground_uuid, "emissivity", 0.95)



def apply_building_surface_properties(
    context: Context,
    bat_uuids: List[int],
    initial_temperature_k: float = 25.0 + 273.15,
) -> List[int]:
    """Applique CONCRETE aux primitives du batiment ; retourne les parois verticales."""
    vertical_walls: List[int] = []
    if not bat_uuids:
        return vertical_walls

    apply_surface_properties(context, bat_uuids, SurfaceType.CONCRETE)
    for bat_uuid in bat_uuids:
        context.setPrimitiveDataFloat(bat_uuid, "temperature", initial_temperature_k)
        normal = context.getPrimitiveNormal(bat_uuid)
        if np.isclose(normal.z, 0, atol=0.1):
            vertical_walls.append(bat_uuid)
    return vertical_walls


def apply_energy_balance_inputs(
    context: Context,
    uuids: List[int],
    air_temperature_k: float,
    air_humidity: float,
    wind_speed: float,
    pressure_pa: float,
    reset_surface_temperature: bool = False,
) -> None:
    """Applique les entrees atmosphériques requises par EnergyBalanceModel sur toutes les primitives.

    Doit etre appele avant le premier ``energy_balance_model.run()`` de l'heure :
    ``air_temperature`` sert de Ta par primitive et initialise T_ABL via la moyenne
    de canopée au premier pas de ``evaluateAirEnergyBalance``.
    """
    if not uuids:
        return

    # Toujours a jour pour l'heure courante (Ta dans run(), condition initiale T_ABL).
    context.setPrimitiveDataFloat(uuids, "air_temperature", air_temperature_k)
    context.setPrimitiveDataFloat(uuids, "air_humidity", air_humidity)
    context.setPrimitiveDataFloat(uuids, "wind_speed", wind_speed)
    context.setPrimitiveDataFloat(uuids, "air_pressure", pressure_pa)

    # T de surface : ne pas ecraser les resultats EB entre les passes horaires.
    if reset_surface_temperature:
        context.setPrimitiveDataFloat(uuids, "temperature", air_temperature_k)


def save_growth_stage_canopies(
    growth_stages_days: List[int],
    building_obj_path: str = "example/models/MAISON_EP_1.obj",
    tree_model_label: str = TREE_MODEL_LABEL,
    count_per_side: int = TREE_RING_COUNT_PER_SIDE,
    spacing: float = TREE_RING_SPACING,
    offset: float = TREE_RING_OFFSET,
    build_parameters: Optional[Dict[str, float]] = TREE_BUILD_PARAMETERS,
    initial_age_days: float = 0.0,
    enable_collision_detection: bool = False,
) -> List[Path]:
    """Cree un anneau d'arbres autour du batiment et exporte les structures XML par stade de croissance."""
    if not growth_stages_days:
        raise ValueError("growth_stages_days ne doit pas etre vide.")

    canopy_dirs: List[Path] = []

    with Context() as context:
        bat_uuids = context.loadOBJ(building_obj_path)
        with PlantArchitecture(context) as plant_architecture:
            plant_architecture.loadPlantModelFromLibrary(tree_model_label)
            plant_architecture.setSoftCollisionAvoidanceParameters(
                view_half_angle_deg=60.0,
                look_ahead_distance=0.08,
                sample_count=128,
                inertia_weight=0.5,
            )
            plant_architecture.setCollisionRelevantOrgans(
                include_internodes=True,
                include_leaves=True,
                include_petioles=False,
                include_flowers=False,
                include_fruit=False,
            )
            if enable_collision_detection:
                plant_architecture.enableSoftCollisionAvoidance()
            else:
                plant_architecture.disableCollisionDetection()

            # Réduire la densité avant de construire
            reduce_shoot_parameters(plant_architecture, ["trunk", "scaffold", "proleptic"])

            plant_ids = create_apple_ring_around_building(
                context=context,
                plant_architecture=plant_architecture,
                building_uuids=bat_uuids,
                tree_model_label=tree_model_label,
                count_per_side=count_per_side,
                spacing=spacing,
                offset=offset,
                age=initial_age_days,
                build_parameters=build_parameters,
            )

            previous_age = 0
            for age in growth_stages_days:
                dt = age - previous_age
                print(f"\nGrowth stage export: avance de {dt} jours (âge cible = {age} jours)")
                plant_architecture.advanceTime(dt)
                previous_age = age
                
                canopy_dir = Path(f"{tree_model_label}_canopy_{age}days")
                canopy_dir.mkdir(exist_ok=True)

                for plant_index, plant_id in enumerate(plant_ids):
                    filename = canopy_dir / f"plant_{plant_index}.xml"
                    plant_architecture.writePlantStructureXML(plant_id, str(filename))

                canopy_dirs.append(canopy_dir)
                print(f"Saved {len(plant_ids)} plants to {canopy_dir}")

    print(f"\nCreated library with {len(growth_stages_days)} growth stages")
    return canopy_dirs


def run_growth_tmrt_example(
    longitude: float,
    latitude: float,
    utc_offset: int,
    pressure_pa: float,
    turbidity: float,
    hours: List[int],
    growth_steps_days: List[int],
    output_dir: str,
) -> None:
    """Execute une simulation TMRT avec croissance de canopee sur plusieurs etapes."""
    center = vec3(0, 0, 0)
    size_total = vec2(50, 50)
    nx, ny = 100, 100
    dx = size_total.x / nx
    dy = size_total.y / ny
    os.makedirs(output_dir, exist_ok=True)
    tmrt_base.nx = nx
    tmrt_base.ny = ny

    with Context() as context:
        context.setDate(2026, 6, 10)
        _tree_id, wpt_all_uuids, wpt_leaf_uuids = create_sample_tree(context=context)
        apply_wpt_sample_tree_surface_properties(context, wpt_all_uuids, wpt_leaf_uuids)
        
        ground_uuids, ground_patches = create_ground_patch(
            context, center, size_total, dx, dy
        )
        apply_ground_surface_properties(context, ground_uuids)
        soil_albedo = SURFACE_PROPERTIES_2[SurfaceType.SOIL].albedo_sw

        # Capteurs MRT à z=1.5m (hauteur piéton, petits, juste pour mesurer)
        center_sensors = vec3(0, 0, 1.5)
        sensor_uuids, sensor_patches = create_ground_patch(
            context, center_sensors, size_total, dx, dy
        )
        # Capteurs doivent être absorbants (perturbent pas le bilan radiatifas transparents) pour mesurer les flux — reviens à la configuration absorbante discutée plus tôt : sensor_uuids:
        for uuid in sensor_uuids:
            for band in ("SW", "PAR", "NIR"):
                context.setPrimitiveDataFloat(uuid, f"reflectivity_{band}", 0.0)
                context.setPrimitiveDataFloat(uuid, f"transmissivity_{band}", 0.0)  # ← absorbant
            context.setPrimitiveDataFloat(uuid, "reflectivity_LW",  0.0)
            context.setPrimitiveDataFloat(uuid, "transmissivity_LW", 0.0)
            context.setPrimitiveDataFloat(uuid, "emissivity",    0.97)
            context.setPrimitiveDataFloat(uuid, "emissivity_LW", 0.97)
            context.setPrimitiveDataFloat(uuid, "emissivity_PAR", 0.0)
            context.setPrimitiveDataFloat(uuid, "emissivity_NIR", 0.0)
            context.setPrimitiveDataFloat(uuid, "emissivity_SW",  0.0)
            context.setPrimitiveDataFloat(uuid, "temperature",      298.15)
            context.setPrimitiveDataFloat(uuid, "air_temperature",  298.15)
            context.setPrimitiveDataFloat(uuid, "air_humidity",     0.5)
            context.setPrimitiveDataFloat(uuid, "wind_speed",       1.0)
            context.setPrimitiveDataFloat(uuid, "air_pressure",     101300.0)
            context.setPrimitiveDataUInt(uuid,  "twosided_flag", 1)
            context.setPrimitiveDataString(uuid, "surface_type", "sensor")


        bat_uuids = context.loadOBJ("example/models/MAISON_EP_1.obj")
        vertical_walls = apply_building_surface_properties(context, bat_uuids)

        reference_ground_uuid = context.addPatch(
            center=vec3(-30, -30, 1.5),  # plus proche, hors du domaine mais pas trop loin
            size=vec2(dx, dy),
        )
        apply_ground_surface_properties(context, [reference_ground_uuid])

        with PlantArchitecture(context) as plant_architecture:
            loaded_plants = []

            for age in growth_steps_days:
                # Supprimer les plantes de l'étape précédente
                if loaded_plants:
                    for pid in loaded_plants:
                        plant_architecture.deletePlantInstance(pid)
                
                # Charger les nouvelles
                loaded_plants = []

                #plant_architecture.advanceTime(age)
                print(f"\n===== Growth step: +{age} =====")

                plant_architecture.loadPlantModelFromLibrary(TREE_MODEL_LABEL)
 
                canopy_dir = Path(f"{TREE_MODEL_LABEL}_canopy_{age}days")
                plant_files = sorted(canopy_dir.glob("plant_*.xml"))
                
                for filepath in plant_files:
                    plant_ids = plant_architecture.readPlantStructureXML(str(filepath), quiet=True)
                    loaded_plants.extend(plant_ids)
        
                print(f"Loaded {len(loaded_plants)} plants from canopy")
                # Récupérer l'aire foliaire totale de la canopée après croissance
                for plant_id in loaded_plants:
                    uuids = plant_architecture.getAllPlantUUIDs(plant_id)
                    for uuid in uuids:
                        if context.doesPrimitiveDataExist(uuid, "leaf_area"):
                            lai = context.getPrimitiveData(uuid, "leaf_area")
                            print(f"LAI of the canopy = {lai} m²/m²")

                plant_uuids = configure_plant_primitives(
                    context, plant_architecture, loaded_plants
                )

                canopy_leaf_uuids = filter_uuids_by_plant_part(
                    context, plant_uuids, "leaf"
                )

                if not canopy_leaf_uuids:
                    canopy_leaf_uuids = plant_uuids
                leaf_uuids = canopy_leaf_uuids

                wpt_trunk_uuids = [u for u in wpt_all_uuids if u not in set(wpt_leaf_uuids)]
                all_leaf_uuids = list(set(leaf_uuids + wpt_leaf_uuids))
                setup_camera_ml_labels(
                    context,
                    leaf_uuids=all_leaf_uuids,
                    trunk_uuids=wpt_trunk_uuids,
                    ground_uuids=ground_uuids,
                )

                stomatal_species = stomatal_species_for_tree_label(TREE_MODEL_LABEL)

                # print("Computing sky view factors for ground patches...")
                # compute_ground_sky_view_factors(context, ground_uuids, ray_count=400, max_ray_length=400.0, num_threads=36)
                #simulation_uuids = context.getAllUUIDs()
                simulation_uuids = (
                    wpt_all_uuids        # ← 253k branches/troncs WPT
                    + ground_uuids
                    + bat_uuids           # 10k murs verticaux
                    + plant_uuids
                    + [reference_ground_uuid]
                )
                
                T_DAWN = 288.15
                context.setPrimitiveDataFloat(simulation_uuids, "temperature",     T_DAWN)
                context.setPrimitiveDataFloat(simulation_uuids, "air_temperature", T_DAWN)
                context.setPrimitiveDataFloat(simulation_uuids, "air_humidity",    0.6)
                context.setPrimitiveDataFloat(simulation_uuids, "wind_speed",      0.9)
                context.setPrimitiveDataFloat(simulation_uuids, "air_pressure",    pressure_pa)

                stomatal_model = StomatalConductanceModel(context)
                stomatal_model.setBMFCoefficientsFromLibrary(stomatal_species, uuids=leaf_uuids)

                energy_balance_model = EnergyBalanceModel(context)
                energy_balance_model.addRadiationBand("LW")
                energy_balance_model.addRadiationBand("PAR")
                energy_balance_model.addRadiationBand("NIR")
                energy_balance_model.enableAirEnergyBalance()

                photosynthesis_model = PhotosynthesisModel(context)
                #photosynthesis_model.setFarquharModelCoefficients(FarquharModelCoefficients())
                #photosynthesis_model.setModelTypeFarquhar()
                photosynthesis_model.setFarquharCoefficientsFromLibrary("Olive", uuids=leaf_uuids)
 

                for i, hour in enumerate(hours):
                    print(f"\nHOUR: {hour}")
                    context.setTime(hour=hour)

                    air_temperature_k = 288.15 + 10 * math.sin(math.pi * (hour - 6) / 12)
                    air_humidity = 0.6 - 0.2 * math.sin(math.pi * (hour - 6) / 12)
                    wind_speed = get_ramped_value(0.9, 1.0, hour, 6, 19)

                    with RadiationModel(context) as radiation:
                        add_growth_radiation_bands(radiation)

                        with SolarPosition(context, utc_offset, latitude, longitude) as solar_position:
                            solar_position.setAtmosphericConditions(
                                pressure_pa, air_temperature_k, air_humidity, turbidity
                            )
                            sun_dir = solar_position.getSunDirectionVector()
                            solar_position.enablePragueSkyModel()
                            solar_position.updatePragueSkyModel(ground_albedo=soil_albedo)
                    
                            sun_source = radiation.addCollimatedRadiationSource(sun_dir)

                            radiation.setDirectRayCount("LW", 100)
                            radiation.setDiffuseRayCount("LW", 1000)
                            radiation.setScatteringDepth("LW", 3)  # same as SW/PAR/NIR; or 1–5

                            radiation.disableEmission("NIR")
                            radiation.setScatteringDepth("NIR", 3)
                            radiation.setDirectRayCount("NIR", 100)
                            radiation.setDiffuseRayCount("NIR", 1000)

                            radiation.disableEmission("SW")
                            radiation.setScatteringDepth("SW", 3)
                            radiation.setDirectRayCount("SW", 100)
                            radiation.setDiffuseRayCount("SW", 1000)

                            radiation.disableEmission("PAR")
                            radiation.setScatteringDepth("PAR", 3)
                            radiation.setDirectRayCount("PAR", 100)
                            radiation.setDiffuseRayCount("PAR", 1000)

                            lw_flux = _getAmbientLongwaveFlux(
                                temperature_K=air_temperature_k,
                                humidity_rel=air_humidity,
                            )

                            # PAR solar flux in W/m² (wavelength range ~400-700 nm)
                            par_flux = solar_position.getSolarFluxPAR(
                                pressure_Pa=pressure_pa,
                                temperature_K=air_temperature_k,
                                humidity_rel=air_humidity,
                                turbidity=turbidity,
                            )
                            # NIR solar flux in W/m² (wavelength range >700 nm)
                            nir_flux = solar_position.getSolarFluxNIR(
                                pressure_Pa=pressure_pa,
                                temperature_K=air_temperature_k,
                                humidity_rel=air_humidity,
                                turbidity=turbidity,
                            )
                            # Diffuse fraction as ratio (0.0-1.0) where:
                            # - 0.0 = all direct radiation
                            # - 1.0 = all diffuse radiation
                            diffuse_fraction = solar_position.getDiffuseFraction(
                                pressure_Pa=pressure_pa,
                                temperature_K=air_temperature_k,
                                humidity_rel=air_humidity,
                                turbidity=turbidity,
                            )
                            
                            sw_flux = par_flux + nir_flux

                            radiation.setSourceFlux(
                                sun_source, "SW", sw_flux * (1.0 - diffuse_fraction)
                            )
                            radiation.setDiffuseRadiationFlux(
                                "SW", sw_flux * diffuse_fraction
                            )
                            radiation.setSourceFlux(
                                sun_source, "PAR", par_flux * (1.0 - diffuse_fraction)
                            )
                            radiation.setDiffuseRadiationFlux(
                                "PAR", par_flux * diffuse_fraction
                            )
                            radiation.setSourceFlux(
                                sun_source, "NIR", nir_flux * (1.0 - diffuse_fraction)
                            )
                            radiation.setDiffuseRadiationFlux(
                                "NIR", nir_flux * diffuse_fraction
                            )
                            radiation.setDiffuseRadiationFlux("LW", lw_flux)

                            if hour == CAMERA_EXPORT_HOUR:
                                setup_radiation_cameras(radiation, scene_center=center)

                            radiation.updateGeometry()

                            # --- Bilan energetique (apres radiation + stomatal) ---
                            # air_temperature sur toutes les primitives AVANT le premier run().
                            apply_energy_balance_inputs(
                                context,
                                simulation_uuids,
                                air_temperature_k,
                                air_humidity,
                                wind_speed,
                                pressure_pa,
                                reset_surface_temperature=(i == 0),
                                )

                            # Après apply_energy_balance_inputs(...) dans la boucle horaire
                            context.setPrimitiveDataFloat(sensor_uuids, "air_temperature", air_temperature_k)
                            context.setPrimitiveDataFloat(sensor_uuids, "air_humidity",    air_humidity)
                            context.setPrimitiveDataFloat(sensor_uuids, "wind_speed",      wind_speed)
                            context.setPrimitiveDataFloat(sensor_uuids, "air_pressure",    pressure_pa)
                            context.setPrimitiveDataFloat(sensor_uuids, "temperature",     air_temperature_k)
                            context.setPrimitiveDataUInt(sensor_uuids,  "energy_balance_flag", 0)

                            with BoundaryLayerConductanceModel(context) as boundary_layer_model:
                                # Sol : modèle empirique dédié (Kustas & Norman)
                                boundary_layer_model.setBoundaryLayerModel("Ground", ground_uuids)

                                # Feuilles oliviers : Pohlhausen (convection forcée laminaire)
                                context.setPrimitiveDataFloat(leaf_uuids, "object_length", 0.05)
                                boundary_layer_model.setBoundaryLayerModel("Pohlhausen", leaf_uuids)

                                # Feuilles WPT : idem
                                context.setPrimitiveDataFloat(wpt_leaf_uuids, "object_length", 0.05)
                                boundary_layer_model.setBoundaryLayerModel("Pohlhausen", wpt_leaf_uuids)

                                # Bâtiment : plaque inclinée (murs verticaux)
                                boundary_layer_model.setBoundaryLayerModel("InclinedPlate", bat_uuids)

                                boundary_layer_model.run()

                                radiation.runBand(["SW", "PAR", "NIR", "LW"])

                                if hour == CAMERA_EXPORT_HOUR:
                                    export_growth_camera_outputs(
                                        radiation,
                                        output_dir=output_dir,
                                        age=age,
                                        hour=hour,
                                    )

                            # Après runBand, vérifier que SW_ref ≈ PAR_ref + NIR_ref
                            sw  = context.getPrimitiveData(reference_ground_uuid, "radiation_flux_SW")
                            par = context.getPrimitiveData(reference_ground_uuid, "radiation_flux_PAR")
                            nir = context.getPrimitiveData(reference_ground_uuid, "radiation_flux_NIR")
                            print(f"SW={sw:.1f}  PAR+NIR={par+nir:.1f}  écart={abs(sw-(par+nir)):.1f} W/m²")
                            # Attendu : écart < 5 W/m² (diffusion numérique du ray-tracing)

                            stomatal_model.run(leaf_uuids)

                            # Passe 1 : surfaces puis couche limite atmospherique (T_ABL).
                            # Pas de temps : 3600s entre heures simulées, mais on fait des sous-pas
                            # Pour Cp=1_200_000 J/m²·°C et gH~0.05 mol/m²/s :
                            # τ = Cp / (cp_air × gH) ≈ 1_200_000 / (29.25 × 0.05) ≈ 820 000 s → très stable
                            # On peut donc utiliser dt=600s (10 minutes) sans risque de divergence

                            dt_seconds = 600.0  # 10 minutes
                            energy_balance_model.run(dt=dt_seconds)
                            energy_balance_model.evaluateAirEnergyBalance(
                                dt_sec=10.0, time_advance_sec=3600.0
                            )

                            # Mise a jour LW avec les nouvelles temperatures de surface
                            radiation.runBand("LW")                             # ré-émission LW avec T mises à jour
                            stomatal_model.run(leaf_uuids)                      # stomates réagissent à la nouvelle T

                            # Passe 2 : convergence surface + air
                            energy_balance_model.run(dt=dt_seconds)
                            energy_balance_model.evaluateAirEnergyBalance(
                                dt_sec=10.0, time_advance_sec=3600.0
                            )

                            photosynthesis_model.runForPrimitives(leaf_uuids)

                            A_canopy = 0.0
                            E_canopy = 0.0
                            for UUID in leaf_uuids:
                                E = context.getPrimitiveData(UUID, "latent_flux")
                                A = context.getPrimitiveData(UUID, "net_photosynthesis")
                                E_canopy += E / 44000 * 1000
                                # mmol H2O / m^2 / sec
                                A_canopy += A  # umol CO2 / m^2 / sec

                                E_mmol = E / 44000 * 1000
                                WUE = A / E_mmol if abs(E_mmol) > 1e-10 else 0.0
                                context.setPrimitiveDataFloat(UUID, "WUE", WUE)

                            WUE_canopy = A_canopy / E_canopy if abs(E_canopy) > 1e-10 else 0.0
                            print(f"WUE of the canopy = {WUE_canopy} umol CO2/mmol H2O")


                            par_vals = [context.getPrimitiveData(u, "radiation_flux_PAR") for u in leaf_uuids[:10]]
                            print(f"PAR feuilles (W/m²): min={min(par_vals):.1f} max={max(par_vals):.1f}")
                            temps = [context.getPrimitiveData(u, "temperature") - 273.15 for u in leaf_uuids[:10]]
                            print(f"T feuilles (°C): min={min(temps):.1f} max={max(temps):.1f}")
                            # Cartographie pseudocouleur Helios sur toutes les primitives
                            # all_uuids = context.getAllUUIDs()
                            # context.colorPrimitiveByDataPseudocolor(
                            #     uuids=all_uuids,
                            #     primitive_data="radiation_flux_SW",
                            #     colormap="hot",
                            #     ncolors=256,
                            # )

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
                            _df_flux = pd.DataFrame(
                                wall_fluxes,
                                index=[f"Wall {i}" for i in range(len(wall_fluxes))],
                                columns=[f"hour_{hour}"],
                            )

                            print(
                                f"Heure {hour:02d}h : Flux sur murs = {np.sum(wall_fluxes):.1f} W/m²"
                            )

                            ground_temperature = []
                            for ground_uuid in ground_uuids:
                                temperature = context.getPrimitiveData(ground_uuid, "temperature")
                                if temperature:
                                    ground_temperature.append(temperature - 273.15)  # ← convertir en °C ici
                                else:
                                    ground_temperature.append(0.0)

                            _df_ground_temperature = pd.DataFrame(
                                ground_temperature,
                                index=[f"Ground {i}" for i in range(len(ground_temperature))],
                                columns=[f"hour_{hour}"],
                            )

                            # Par ce bloc — matrice 2D ny×nx comme ground_patches
                            ground_temp_matrix = np.zeros((ny, nx))
                            for j in range(ny):
                                for i in range(nx):
                                    uuid = ground_patches[j][i]
                                    temperature = context.getPrimitiveData(uuid, "temperature")
                                    ground_temp_matrix[j, i] = (temperature - 273.15) if temperature else 0.0

                            _df_ground_temperature = pd.DataFrame(
                                ground_temp_matrix,
                                index=[f"y{j}" for j in range(ny)],
                                columns=[f"x{i}" for i in range(nx)],
                            )

                            df_tmrt = compute_MRT(
                                context, ground_patches, output_dir, sigma=5.67e-8
                            )

                            figure_path_tmrt = os.path.join(output_dir, f"tmrt_growth_{age:02d}days_{hour:02d}h.png")


                            plt.figure(figsize=(7, 5))
                            plt.imshow(df_tmrt.values, cmap="inferno", origin="lower", vmin=20, vmax=70)
                            plt.colorbar(label="TMRT (degC)")
                            plt.title(f"TMRT growth={age}days hour={hour:02d}h")
                            plt.tight_layout()
                            
                            plt.savefig(figure_path_tmrt, dpi=180)
                            plt.close()

                            figure_path_tground = os.path.join(output_dir, f"temperature_ground_{age:02d}days_{hour:02d}h.png")

                            plt.figure(figsize=(7, 5))
                            plt.imshow(
                                _df_ground_temperature.values,
                                cmap="inferno", origin="lower",
                                vmin=20, vmax=70,
                                extent=[-size_total.x/2, size_total.x/2, -size_total.y/2, size_total.y/2]
                            )
                            plt.colorbar(label="Temperature sol (°C)")
                            plt.xlabel("X (m)")
                            plt.ylabel("Y (m)")
                            plt.title(f"Temperature ground growth={age}days hour={hour:02d}h")
                            plt.tight_layout()
                            plt.savefig(figure_path_tground, dpi=180)
                            plt.close()

                            irradiance_reference = context.getPrimitiveData(
                                reference_ground_uuid, "radiation_flux_SW"
                            )
                            print(
                                "Growth step / hour / SW reference:",
                                age,
                                hour,
                                irradiance_reference,
                            )


                context.writeOBJ(f"{output_dir}/scene_growth_{age:02d}days.obj")


if __name__ == "__main__":
    growth_stages = [365, 730, 1095, 1460, 1825]  # 1 à 5 ans de croissance (âge réel: 4 à 8 ans) car oliveier commence a 3 ans  voir https://plantsimulationlab.github.io/Helios/_plant_architecture_doc.html
    #growth_stages = [365]
    #save_growth_stage_canopies(growth_stages_days=growth_stages)

    #growth_stages = [1460]

    run_growth_tmrt_example(
        longitude=-1.15,
        latitude=46.166672,
        utc_offset=1,
        pressure_pa=101300.0,
        turbidity=0.05,
        hours=[12],
        growth_steps_days=growth_stages,
        output_dir="resultats_ombres_growth",
    )
