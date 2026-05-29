import math
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from example.improved_radiation_calculation import (
    SURFACE_PROPERTIES,
    SurfaceType,
    apply_surface_properties,
)
from example.pyhelios_radiation_pure import compute_MRT
import example.pyhelios_svf_radiation_tmrt as tmrt_base
from example.pyhelios_svf_radiation_tmrt import (
    create_ground_patch,
    create_sample_tree,
    getAmbientLongwaveFlux,
    get_ramped_value,
)
from pyhelios import (
    BoundaryLayerConductanceModel,
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
TREE_BUILD_PARAMETERS: Optional[Dict[str, float]] = None
TREE_MODEL_LABEL: str = "olive"

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
        leaf_props = SURFACE_PROPERTIES[SurfaceType.LEAF]
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

            for age in growth_stages_days:
                print(f"\nGrowth stage export: +{age} days")
                plant_architecture.advanceTime(age)

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
        soil_albedo = SURFACE_PROPERTIES[SurfaceType.SOIL].albedo_sw

        # Capteurs MRT à z=1.5m (hauteur piéton, petits, juste pour mesurer)
        center_sensors = vec3(0, 0, 1.5)
        sensor_uuids, sensor_patches = create_ground_patch(
            context, center_sensors, size_total, dx, dy
        )
        # Capteurs transparents : ne perturbent pas le bilan radiatif
        for uuid in sensor_uuids:
            context.setPrimitiveDataFloat(uuid, "reflectivity_SW", 0.0)
            context.setPrimitiveDataFloat(uuid, "reflectivity_PAR", 0.0)
            context.setPrimitiveDataFloat(uuid, "reflectivity_NIR", 0.0)
            context.setPrimitiveDataFloat(uuid, "emissivity_LW", 0.97)  # corps humain
            context.setPrimitiveDataFloat(uuid, "temperature", 25.0 + 273.15)
            context.setPrimitiveDataUInt(uuid, "twosided_flag", 1)  # reçoit de toutes les directions
            context.setPrimitiveDataString(uuid, "surface_type", "sensor")


        bat_uuids = context.loadOBJ("example/models/MAISON_EP_1.obj")
        vertical_walls = apply_building_surface_properties(context, bat_uuids)

        reference_ground_uuid = context.addPatch(
            center=vec3(-100, -100, 1.5),
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

                plant_uuids = configure_plant_primitives(
                    context, plant_architecture, loaded_plants
                )

                canopy_leaf_uuids = filter_uuids_by_plant_part(
                    context, plant_uuids, "leaf"
                )
                if not canopy_leaf_uuids:
                    canopy_leaf_uuids = plant_uuids
                leaf_uuids = canopy_leaf_uuids
                stomatal_species = stomatal_species_for_tree_label(TREE_MODEL_LABEL)

                # print("Computing sky view factors for ground patches...")
                # compute_ground_sky_view_factors(context, ground_uuids, ray_count=400, max_ray_length=400.0, num_threads=36)
                simulation_uuids = context.getAllUUIDs()

                stomatal_model = StomatalConductanceModel(context)
                stomatal_model.setBMFCoefficientsFromLibrary(stomatal_species, uuids=leaf_uuids)

                energy_balance_model = EnergyBalanceModel(context)
                energy_balance_model.addRadiationBand("LW")
                energy_balance_model.addRadiationBand("PAR")
                energy_balance_model.addRadiationBand("NIR")
                energy_balance_model.enableAirEnergyBalance()

                for i, hour in enumerate(hours):
                    print(f"\nHOUR: {hour}")
                    context.setTime(hour=hour)

                    air_temperature_k = 288.15 + 10 * math.sin(math.pi * (hour - 6) / 12)
                    air_humidity = 0.6 - 0.2 * math.sin(math.pi * (hour - 6) / 12)
                    wind_speed = get_ramped_value(0.9, 1.0, hour, 6, 19)

                    with SolarPosition(context, utc_offset, latitude, longitude) as solar_position:
                        solar_position.setAtmosphericConditions(
                            pressure_pa, air_temperature_k, air_humidity, turbidity
                        )
                        sun_dir = solar_position.getSunDirectionVector()
                        solar_position.enablePragueSkyModel()
                        solar_position.updatePragueSkyModel(ground_albedo=soil_albedo)

                        with RadiationModel(context) as radiation:
                            sun_source = radiation.addCollimatedRadiationSource(sun_dir)

                            radiation.addRadiationBand("LW")
                            radiation.setDirectRayCount("LW", 100)
                            radiation.setDiffuseRayCount("LW", 1000)
                            radiation.setScatteringDepth("LW", 3)  # same as SW/PAR/NIR; or 1–5

                            radiation.addRadiationBand("NIR")
                            radiation.disableEmission("NIR")
                            radiation.setScatteringDepth("NIR", 3)
                            radiation.setDirectRayCount("NIR", 100)
                            radiation.setDiffuseRayCount("NIR", 1000)

                            radiation.addRadiationBand("SW")
                            radiation.disableEmission("SW")
                            radiation.setScatteringDepth("SW", 3)
                            radiation.setDirectRayCount("SW", 100)
                            radiation.setDiffuseRayCount("SW", 1000)

                            radiation.addRadiationBand("PAR")
                            radiation.disableEmission("PAR")
                            radiation.setScatteringDepth("PAR", 3)
                            radiation.setDirectRayCount("PAR", 100)
                            radiation.setDiffuseRayCount("PAR", 1000)

                            lw_flux = getAmbientLongwaveFlux(
                                temperature_K=air_temperature_k,
                                humidity_rel=air_humidity,
                            )
                            par_flux = solar_position.getSolarFluxPAR(
                                pressure_Pa=pressure_pa,
                                temperature_K=air_temperature_k,
                                humidity_rel=air_humidity,
                                turbidity=turbidity,
                            )
                            nir_flux = solar_position.getSolarFluxNIR(
                                pressure_Pa=pressure_pa,
                                temperature_K=air_temperature_k,
                                humidity_rel=air_humidity,
                                turbidity=turbidity,
                            )
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

                            with BoundaryLayerConductanceModel(
                                context
                            ) as boundary_layer_model:
                                boundary_layer_model.setBoundaryLayerModel(
                                    "Ground", ground_uuids
                                )
                                boundary_layer_model.setBoundaryLayerModel(
                                    "Pohlhausen", leaf_uuids
                                )
                                boundary_layer_model.run()

                            radiation.runBand(["SW", "PAR", "NIR", "LW"])

                            stomatal_model.run(leaf_uuids)

                            # Passe 1 : surfaces puis couche limite atmospherique (T_ABL).
                            energy_balance_model.run()
                            energy_balance_model.evaluateAirEnergyBalance(
                                dt_sec=30.0, time_advance_sec=3600.0
                            )

                            # Mise a jour LW avec les nouvelles temperatures de surface
                            radiation.runBand("LW")                             # ré-émission LW avec T mises à jour
                            stomatal_model.run(leaf_uuids)                      # stomates réagissent à la nouvelle T

                            # Passe 2 : convergence surface + air
                            energy_balance_model.run()
                            energy_balance_model.evaluateAirEnergyBalance(
                                dt_sec=30.0, time_advance_sec=3600.0
                            )

                            photosynthesis_model = PhotosynthesisModel(context)
                            photosynthesis_model.setFarquharModelCoefficients(
                                FarquharModelCoefficients()
                            )
                            photosynthesis_model.setModelTypeFarquhar()
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

                            WUE_canopy = A_canopy / E_canopy  # umol CO2/mmol H2O
                            print(f"WUE of the canopy = {WUE_canopy} umol CO2/mmol H2O")

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

                            df_tmrt = compute_MRT(
                                context, sensor_patches, output_dir, sigma=5.67e-8
                            )
                            figure_path = os.path.join(
                                output_dir,
                                f"tmrt_growth_{age:02d}days_{hour:02d}h.png"
                            )
                            plt.figure(figsize=(7, 5))
                            plt.imshow(df_tmrt.values, cmap="inferno", origin="lower", vmin=20, vmax=70)
                            plt.colorbar(label="TMRT (degC)")
                            plt.title(f"TMRT growth={age}days hour={hour:02d}h")
                            plt.tight_layout()
                            
                            plt.savefig(figure_path, dpi=180)
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


if __name__ == "__main__":
    # growth_stages = [10, 20, 30, 40, 50]  # jours
    # growth_stages = [1 * 365, 2 * 365, 4 * 365, 6 * 365, 8 * 365, 10 * 365]
    growth_stages = [10 * 365]

    save_growth_stage_canopies(growth_stages_days=growth_stages)

    run_growth_tmrt_example(
        longitude=-1.15,
        latitude=46.166672,
        utc_offset=1,
        pressure_pa=101300.0,
        turbidity=0.05,
        hours=[10, 12, 14],
        growth_steps_days=growth_stages,
        output_dir="resultats_ombres_growth",
    )
