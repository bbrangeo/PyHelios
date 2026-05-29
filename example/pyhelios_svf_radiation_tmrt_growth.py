import math
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt

from example.pyhelios_radiation_pure import compute_MRT
import example.pyhelios_svf_radiation_tmrt as tmrt_base
from example.pyhelios_svf_radiation_tmrt import (
    create_canopy,
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

# Configuration globale des arbres apple autour du bâtiment
TREE_RING_COUNT_PER_SIDE = 2
TREE_RING_SPACING = 3.5
TREE_RING_OFFSET = 2.5
TREE_AGE = 365.0
TREE_BUILD_PARAMETERS: Optional[Dict[str, float]] = None
TREE_MODEL_LABEL: str = "peach"


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


def get_plant_primitive_uuids(
    plant_architecture: PlantArchitecture, plant_ids: List[int]
) -> List[int]:
    """Retourne tous les UUID de primitives associes a des plants."""
    plant_uuids: List[int] = []
    for plant_id in plant_ids:
        plant_uuids.extend(plant_architecture.getAllPlantUUIDs(plant_id))
    return plant_uuids


def configure_soybean_plant_primitives(
    context: Context,
    plant_architecture: PlantArchitecture,
    plant_ids: List[int],
) -> List[int]:
    """Configure les proprietes optiques et thermiques des plants soybean."""
    plant_uuids = get_plant_primitive_uuids(plant_architecture, plant_ids)
    if not plant_uuids:
        return plant_uuids

    context.setPrimitiveDataFloat(plant_uuids, "reflectivity_SW", 0.20)
    context.setPrimitiveDataFloat(plant_uuids, "reflectivity_PAR", 0.10)
    context.setPrimitiveDataFloat(plant_uuids, "reflectivity_NIR", 0.45)
    context.setPrimitiveDataFloat(plant_uuids, "transmissivity_PAR", 0.45)
    context.setPrimitiveDataFloat(plant_uuids, "transmissivity_NIR", 0.40)
    context.setPrimitiveDataFloat(plant_uuids, "emissivity", 0.95)
    context.setPrimitiveDataFloat(plant_uuids, "emissivity_LW", 0.95)
    context.setPrimitiveDataFloat(plant_uuids, "emissivity_PAR", 0.95)
    context.setPrimitiveDataFloat(plant_uuids, "emissivity_NIR", 0.95)
    return plant_uuids


def apply_energy_balance_inputs(
    context: Context,
    uuids: List[int],
    air_temperature_k: float,
    air_humidity: float,
    wind_speed: float,
    pressure_pa: float,
) -> None:
    """Applique les donnees primitives requises par EnergyBalanceModel."""
    if not uuids:
        return

    context.setPrimitiveDataFloat(uuids, "air_temperature", air_temperature_k)
    context.setPrimitiveDataFloat(uuids, "air_humidity", air_humidity)
    context.setPrimitiveDataFloat(uuids, "wind_speed", wind_speed)
    context.setPrimitiveDataFloat(uuids, "air_pressure", pressure_pa)
    context.setPrimitiveDataFloat(uuids, "temperature", air_temperature_k)
    context.setPrimitiveDataFloat(uuids, "emissivity_LW", 0.95)
    context.setPrimitiveDataFloat(uuids, "emissivity_PAR", 0.95)
    context.setPrimitiveDataFloat(uuids, "emissivity_NIR", 0.95)


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
    nx, ny = 30, 30
    dx = size_total.x / nx
    dy = size_total.y / ny
    os.makedirs(output_dir, exist_ok=True)
    tmrt_base.nx = nx
    tmrt_base.ny = ny

    with Context() as context:
        context.setDate(2026, 6, 10)
        _tree_id, _tree_uuids, leaf_uuids = create_sample_tree(context=context)
        ground_uuids, ground_patches = create_ground_patch(
            context, center, size_total, dx, dy
        )
        bat_uuids = context.loadOBJ("example/models/MAISON_EP_1.obj")
        for bat_uuid in bat_uuids:
            context.setPrimitiveDataFloat(bat_uuid, "reflectivity_SW", 0.35)
            context.setPrimitiveDataFloat(bat_uuid, "reflectivity_PAR", 0.20)
            context.setPrimitiveDataFloat(bat_uuid, "reflectivity_NIR", 0.30)
            context.setPrimitiveDataFloat(bat_uuid, "emissivity", 0.90)
            context.setPrimitiveDataFloat(bat_uuid, "temperature", 25.0)

        reference_ground_uuid = context.addPatch(
            center=vec3(-100, -100, 0),
            size=vec2(dx, dy),
        )
        context.setPrimitiveDataString(reference_ground_uuid, "surface_type", "soil")
        context.setPrimitiveDataFloat(reference_ground_uuid, "reflectivity_SW", 0.3)
        context.setPrimitiveDataFloat(reference_ground_uuid, "emissivity", 0.90)
        context.setPrimitiveDataUInt(reference_ground_uuid, "twosided_flag", 0)

        with PlantArchitecture(context) as plant_architecture:
            for age in growth_steps_days:
                #plant_architecture.advanceTime(age)
                print(f"\n===== Growth step: +{age} =====")

                plant_architecture.loadPlantModelFromLibrary(TREE_MODEL_LABEL)
 
                loaded_plants = []
                for i in range(8):  # 3x3 = 9 plants
                    filename = Path(f"soybean_canopy_{age}days/plant_{i}.xml")
                    plant_ids = plant_architecture.readPlantStructureXML(str(filename), quiet=True)
                    loaded_plants.extend(plant_ids)
        
                print(f"Loaded {len(loaded_plants)} plants from canopy")

                plant_uuids = configure_soybean_plant_primitives(
                    context, plant_architecture, loaded_plants
                )
                leaf_uuids = plant_uuids

                print("Computing sky view factors for ground patches...")
                compute_ground_sky_view_factors(context, ground_uuids)

                for hour in hours:
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
                        solar_position.updatePragueSkyModel(ground_albedo=0.3)

                        with RadiationModel(context) as radiation:
                            sun_source = radiation.addCollimatedRadiationSource(sun_dir)

                            radiation.addRadiationBand("LW")
                            radiation.setDirectRayCount("LW", 100)
                            radiation.setDiffuseRayCount("LW", 1000)

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

                            simulation_uuids = context.getAllUUIDs()
                            apply_energy_balance_inputs(
                                context,
                                simulation_uuids,
                                air_temperature_k,
                                air_humidity,
                                wind_speed,
                                pressure_pa,
                            )
                            context.setPrimitiveDataFloat(
                                bat_uuids, "emissivity_LW", 0.90
                            )
                            context.setPrimitiveDataFloat(
                                bat_uuids, "emissivity_PAR", 0.90
                            )
                            context.setPrimitiveDataFloat(
                                bat_uuids, "emissivity_NIR", 0.90
                            )
                            context.setPrimitiveDataFloat(ground_uuids, "emissivity_LW", 0.90)
                            context.setPrimitiveDataFloat(ground_uuids, "emissivity_PAR", 0.90)
                            context.setPrimitiveDataFloat(ground_uuids, "emissivity_NIR", 0.90)

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

                            stomatal_model = StomatalConductanceModel(context)
                            stomatal_model.setBMFCoefficientsFromLibrary(
                                "Apple", uuids=leaf_uuids
                            )
                            stomatal_model.run(leaf_uuids)

                            energy_balance_model = EnergyBalanceModel(context)
                            energy_balance_model.addRadiationBand("LW")
                            energy_balance_model.addRadiationBand("PAR")
                            energy_balance_model.addRadiationBand("NIR")
                            energy_balance_model.run()

                            radiation.runBand("LW")
                            stomatal_model.run(leaf_uuids)
                            energy_balance_model.run()

                            photosynthesis_model = PhotosynthesisModel(context)
                            photosynthesis_model.setFarquharModelCoefficients(
                                FarquharModelCoefficients()
                            )
                            photosynthesis_model.setModelTypeFarquhar()
                            photosynthesis_model.runForPrimitives(leaf_uuids)

                            df_tmrt = compute_MRT(
                                context, ground_patches, output_dir, sigma=5.67e-8
                            )
                            figure_path = os.path.join(
                                output_dir,
                                f"tmrt_growth_{age:02d}days_{hour:02d}h.png",
                            )
                            plt.figure(figsize=(7, 5))
                            plt.imshow(df_tmrt.values, cmap="inferno", origin="lower")
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
    # Save plants at multiple growth stages
    # growth_stages = [10, 20, 30, 40, 50]  # days
    growth_stages = [1*365, 2*365, 4*365, 6*365, 8*365, 10*365]  # days

    with Context() as context:
        bat_uuids = context.loadOBJ("example/models/MAISON_EP_1.obj")
        with PlantArchitecture(context) as plantarch:
            plantarch.loadPlantModelFromLibrary(TREE_MODEL_LABEL)
             # Fast (for rapid prototyping or large-scale simulations)
            plantarch.setSoftCollisionAvoidanceParameters(
                view_half_angle_deg=60.0,
                look_ahead_distance=0.08,
                sample_count=128,
                inertia_weight=0.5
            )
            # Configure which organs participate in collision detection
            plantarch.setCollisionRelevantOrgans(
                include_internodes=True,   # Include stems
                include_leaves=True,       # Include leaf blades
                include_petioles=False,    # Exclude petioles (performance)
                include_flowers=False,     # Exclude flowers
                include_fruit=False        # Exclude fruit
            )
            
            # Enable collision detection
            #plant_architecture.enableSoftCollisionAvoidance()
            # Disable collision detection
            plantarch.disableCollisionDetection()
            
            plant_ids = create_apple_ring_around_building(
                    context=context,
                    plant_architecture=plantarch,
                    building_uuids=bat_uuids,
                    tree_model_label=TREE_MODEL_LABEL,
                    count_per_side=TREE_RING_COUNT_PER_SIDE,
                    spacing=TREE_RING_SPACING,
                    offset=TREE_RING_OFFSET,
                    age=0.0,
                    build_parameters=TREE_BUILD_PARAMETERS,
                    
            )

            for age in growth_stages:
                print("\ncreate_canopy\n")
                # Grow canopy
                plantarch.advanceTime(age)
        
                # Save each plant
                canopy_dir = Path(f"{TREE_MODEL_LABEL}_canopy_{age}days")
                canopy_dir.mkdir(exist_ok=True)
        
                for i, plant_id in enumerate(plant_ids):
                    filename = canopy_dir / f"plant_{i}.xml"
                    plantarch.writePlantStructureXML(plant_id, str(filename))
 
                    print(f"Saved {len(plant_ids)} plants to {canopy_dir}")
    
    print(f"\nCreated library with {len(growth_stages)} growth stages")
    print(f"Library location: {library_dir.absolute()}")

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
