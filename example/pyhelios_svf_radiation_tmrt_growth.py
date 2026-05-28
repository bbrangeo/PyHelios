import math
import os
import platform
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
TREE_MODEL_LABEL = "soybean"


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
            print("\ncreate_canopy\n")
            # create_canopy(plant_architecture)
            apple_ring_ids = create_apple_ring_around_building(
                context=context,
                plant_architecture=plant_architecture,
                building_uuids=bat_uuids,
                tree_model_label=TREE_MODEL_LABEL,
                count_per_side=TREE_RING_COUNT_PER_SIDE,
                spacing=TREE_RING_SPACING,
                offset=TREE_RING_OFFSET,
                age=TREE_AGE,
                build_parameters=TREE_BUILD_PARAMETERS,
                
            )
            print(f"Arbres apple ajoutes autour du batiment: {len(apple_ring_ids)}")
            all_uuids = context.getAllUUIDs()

            for growth_step in growth_steps_days:
                plant_architecture.advanceTime(growth_step * 365)
                print(f"\n===== Growth step: +{growth_step} years =====")

                if platform.system() == "Darwin":
                    with Visualizer(800, 600, headless=False) as visualizer:
                        visualizer.buildContextGeometry(context)
                        bg_color = RGBcolor(0.1, 0.1, 0.15)
                        visualizer.setBackgroundColor(bg_color)
                        light_dir = vec3(1, 1, 1)
                        visualizer.setLightDirection(light_dir)
                        visualizer.setLightingModel("phong_shadowed")
                        visualizer.setBackgroundSkyTexture()

                        radius = 15
                        theta = 0.35
                        phi = 0.4 * math.pi
                        x = radius * math.sin(theta) * math.cos(phi)
                        y = radius * math.sin(theta) * math.sin(phi)
                        z = radius * math.cos(theta)
                        camera_position = vec3(x, y, z)
                        look_at = vec3(0, 0, 2)
                        visualizer.setCameraPosition(camera_position, look_at)
                        visualizer.buildContextGeometry(context)

                        print("Opening interactive visualization window...")
                        print("Controls:")
                        print("  - Mouse scroll: Zoom in/out")
                        print("  - Left mouse + drag: Rotate camera")
                        print("  - Right mouse + drag: Pan camera")
                        print("  - Arrow keys: Camera movement")
                        print("  - Close window to continue")
                        visualizer.plotInteractive()

                for hour in hours:
                    print(f"\nHOUR: {hour}")
                    context.setTime(hour=hour)

                    air_temperature_k = 288.15 + 10 * math.sin(math.pi * (hour - 6) / 12)
                    air_humidity = 0.6 - 0.2 * math.sin(math.pi * (hour - 6) / 12)
                    wind_speed = get_ramped_value(0.9, 1.0, hour, 6, 19)

                    for uuid in all_uuids:
                        context.setPrimitiveDataFloat(uuid, "air_temperature", air_temperature_k)
                        context.setPrimitiveDataFloat(uuid, "air_humidity", air_humidity)
                        context.setPrimitiveDataFloat(uuid, "wind_speed", wind_speed)

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
                                f"tmrt_growth_{growth_step:02d}y_{hour:02d}h.png",
                            )
                            plt.figure(figsize=(7, 5))
                            plt.imshow(df_tmrt.values, cmap="inferno", origin="lower")
                            plt.colorbar(label="TMRT (degC)")
                            plt.title(f"TMRT growth={growth_step}y hour={hour:02d}h")
                            plt.tight_layout()
                            plt.savefig(figure_path, dpi=180)
                            plt.close()

                            irradiance_reference = context.getPrimitiveData(
                                reference_ground_uuid, "radiation_flux_SW"
                            )
                            print(
                                "Growth step / hour / SW reference:",
                                growth_step,
                                hour,
                                irradiance_reference,
                            )


if __name__ == "__main__":
    run_growth_tmrt_example(
        longitude=-1.15,
        latitude=46.166672,
        utc_offset=1,
        pressure_pa=101300.0,
        turbidity=0.05,
        hours=[10, 12, 14],
        growth_steps_days=[5, 10, 15, 20],
        output_dir="resultats_ombres_growth",
    )
