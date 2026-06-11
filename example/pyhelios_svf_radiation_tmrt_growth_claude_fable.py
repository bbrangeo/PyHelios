"""
Version refactorisée du cœur de simulation TMRT / croissance.

Changements (tous validés contre l'API réelle de PlantSimulationLab/PyHelios) :

  [PERF-1]  Un seul RadiationModel par stade de croissance (géométrie fixe entre
            les heures) au lieu d'un RadiationModel neuf à chaque heure.
            => BVH OptiX/Vulkan construite UNE fois par stade.
            La source solaire est mise à jour via setSourcePosition() — il n'existe
            PAS de clearRadiationSources() dans PyHelios.

  [PERF-2]  Bandes / ray counts / scattering / disableEmission / caméras configurés
            une seule fois. runBand groupé (la doc PyHelios déconseille les appels
            mono-bande répétés).

  [BUG-1]   L'air n'est avancé qu'UNE fois par heure (time_advance_sec=3600).
            L'ancien code appelait evaluateAirEnergyBalance() deux fois avec
            time_advance_sec=3600 -> +2 h d'air par heure simulée (dérive).

  [BUG-2]   LAI = aire foliaire TOTALE / aire de sol, et non l'aire d'une feuille.

  [ROBUST]  getPrimitiveData lève si le label manque -> on retire les gardes
            "if temperature:" trompeurs et on lit directement (les données
            existent toujours après runBand/EB). np.nan pour les vrais manquants.

  [MRT]     POINT DE DÉCISION laissé explicite : MRT au sol (z=0) vs hauteur piéton
            (z=1.5). Voir le paramètre `mrt_patches` plus bas.

Ce fichier remplace `run_growth_tmrt_example` ; les helpers du fichier d'origine
(create_ground_patch, compute_MRT, apply_*_surface_properties, etc.) sont réutilisés
tels quels.
"""

import math
import os
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from example.improved_radiation_calculation import SURFACE_PROPERTIES_2, SurfaceType
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
    Context,
    EnergyBalanceModel,
    PhotosynthesisModel,
    PlantArchitecture,
    RadiationModel,
    SolarPosition,
    StomatalConductanceModel,
)
from pyhelios.types import vec2, vec3

# Réutilise les constantes/fonctions du module d'origine.
from pyhelios_svf_radiation_tmrt_growth import (  # adapte le nom si besoin
    TREE_MODEL_LABEL,
    CAMERA_EXPORT_HOUR,
    add_growth_radiation_bands,
    apply_building_surface_properties,
    apply_energy_balance_inputs,
    apply_ground_surface_properties,
    apply_wpt_sample_tree_surface_properties,
    configure_plant_primitives,
    export_growth_camera_outputs,
    filter_uuids_by_plant_part,
    setup_camera_ml_labels,
    setup_radiation_cameras,
    stomatal_species_for_tree_label,
)


# --------------------------------------------------------------------------- #
# [BUG-2] LAI correct : aire foliaire totale / aire de référence
# --------------------------------------------------------------------------- #
def compute_canopy_lai(
    context: Context,
    plant_architecture: PlantArchitecture,
    plant_ids: List[int],
    ground_area_m2: float,
) -> float:
    """LAI = somme(leaf_area) / aire de sol de référence (m²/m²).

    Note : `ground_area_m2` doit être l'emprise pertinente. Diviser par tout le
    domaine (50x50) donne un LAI *moyenné sur le domaine*, très sous-estimé ;
    pour le LAI réel des oliviers, utilise l'emprise projetée de l'anneau.
    """
    total_leaf_area = 0.0
    for plant_id in plant_ids:
        for uuid in plant_architecture.getAllPlantUUIDs(plant_id):
            if context.doesPrimitiveDataExist(uuid, "leaf_area"):
                total_leaf_area += context.getPrimitiveData(uuid, "leaf_area")
    if ground_area_m2 <= 0:
        return float("nan")
    return total_leaf_area / ground_area_m2


def run_growth_tmrt_example(
    longitude: float,
    latitude: float,
    utc_offset: int,
    pressure_pa: float,
    turbidity: float,
    hours: List[int],
    growth_steps_days: List[int],
    output_dir: str,
    *,
    mrt_at_pedestrian_height: bool = True,  # [MRT] True -> z=1.5m ; False -> sol z=0
) -> None:
    """Simulation TMRT avec croissance de canopée sur plusieurs stades."""
    center = vec3(0, 0, 0)
    size_total = vec2(50, 50)
    nx, ny = 100, 100
    dx = size_total.x / nx
    dy = size_total.y / ny
    domain_area = size_total.x * size_total.y
    os.makedirs(output_dir, exist_ok=True)
    tmrt_base.nx = nx
    tmrt_base.ny = ny

    with Context() as context:
        context.setDate(2026, 6, 10)

        _tree_id, wpt_all_uuids, wpt_leaf_uuids = create_sample_tree(context=context)
        apply_wpt_sample_tree_surface_properties(context, wpt_all_uuids, wpt_leaf_uuids)
        wpt_trunk_uuids = [u for u in wpt_all_uuids if u not in set(wpt_leaf_uuids)]

        # Sol (z=0) — support de la carte de température et MRT au sol.
        ground_uuids, ground_patches = create_ground_patch(context, center, size_total, dx, dy)
        apply_ground_surface_properties(context, ground_uuids)
        soil_albedo = SURFACE_PROPERTIES_2[SurfaceType.SOIL].albedo_sw

        # Capteurs MRT à hauteur piéton (z=1.5, ISO 7726).
        center_sensors = vec3(0, 0, 1.5)
        sensor_uuids, sensor_patches = create_ground_patch(context, center_sensors, size_total, dx, dy)
        for uuid in sensor_uuids:
            for band in ("SW", "PAR", "NIR"):
                context.setPrimitiveDataFloat(uuid, f"reflectivity_{band}", 0.0)
                context.setPrimitiveDataFloat(uuid, f"transmissivity_{band}", 0.0)
            context.setPrimitiveDataFloat(uuid, "reflectivity_LW", 0.0)
            context.setPrimitiveDataFloat(uuid, "transmissivity_LW", 0.0)
            context.setPrimitiveDataFloat(uuid, "emissivity", 0.97)
            context.setPrimitiveDataFloat(uuid, "emissivity_LW", 0.97)
            context.setPrimitiveDataUInt(uuid, "twosided_flag", 1)
            context.setPrimitiveDataUInt(uuid, "energy_balance_flag", 0)
            context.setPrimitiveDataString(uuid, "surface_type", "sensor")

        bat_uuids = context.loadOBJ("example/models/MAISON_EP_1.obj")
        vertical_walls = apply_building_surface_properties(context, bat_uuids)

        reference_ground_uuid = context.addPatch(center=vec3(-30, -30, 1.5), size=vec2(dx, dy))
        apply_ground_surface_properties(context, [reference_ground_uuid])

        # [MRT] choix de la grille évaluée pour la TMRT
        mrt_patches = sensor_patches if mrt_at_pedestrian_height else ground_patches

        with PlantArchitecture(context) as plant_architecture:
            loaded_plants: List[int] = []

            for age in growth_steps_days:
                # Remplacer la canopée du stade précédent.
                for pid in loaded_plants:
                    plant_architecture.deletePlantInstance(pid)
                loaded_plants = []

                print(f"\n===== Growth step: +{age} jours =====")
                plant_architecture.loadPlantModelFromLibrary(TREE_MODEL_LABEL)

                canopy_dir = Path(f"{TREE_MODEL_LABEL}_canopy_{age}days")
                for filepath in sorted(canopy_dir.glob("plant_*.xml")):
                    loaded_plants.extend(
                        plant_architecture.readPlantStructureXML(str(filepath), quiet=True)
                    )
                print(f"Loaded {len(loaded_plants)} plants from canopy")

                # [BUG-2] LAI correct.
                lai = compute_canopy_lai(context, plant_architecture, loaded_plants, domain_area)
                print(f"LAI (domaine) = {lai:.3f} m2/m2")

                plant_uuids = configure_plant_primitives(context, plant_architecture, loaded_plants)
                canopy_leaf_uuids = filter_uuids_by_plant_part(context, plant_uuids, "leaf") or plant_uuids
                leaf_uuids = canopy_leaf_uuids
                all_leaf_uuids = list(set(leaf_uuids) | set(wpt_leaf_uuids))

                setup_camera_ml_labels(
                    context,
                    leaf_uuids=all_leaf_uuids,
                    trunk_uuids=wpt_trunk_uuids,
                    ground_uuids=ground_uuids,
                )

                simulation_uuids = (
                    wpt_all_uuids
                    + ground_uuids
                    + bat_uuids
                    + plant_uuids
                    + [reference_ground_uuid]
                )

                # Reset thermique de l'aube (une fois par stade).
                T_DAWN = 288.15
                context.setPrimitiveDataFloat(simulation_uuids, "temperature", T_DAWN)
                context.setPrimitiveDataFloat(simulation_uuids, "air_temperature", T_DAWN)
                context.setPrimitiveDataFloat(simulation_uuids, "air_humidity", 0.6)
                context.setPrimitiveDataFloat(simulation_uuids, "wind_speed", 0.9)
                context.setPrimitiveDataFloat(simulation_uuids, "air_pressure", pressure_pa)

                stomatal_species = stomatal_species_for_tree_label(TREE_MODEL_LABEL)
                stomatal_model = StomatalConductanceModel(context)
                stomatal_model.setBMFCoefficientsFromLibrary(stomatal_species, uuids=leaf_uuids)

                energy_balance_model = EnergyBalanceModel(context)
                # SW = PAR + NIR spectralement : on ajoute PAR+NIR (pas SW) pour ne pas
                # doubler le courtonde, + LW. (Choix correct, conservé.)
                energy_balance_model.addRadiationBand(["LW", "PAR", "NIR"])
                energy_balance_model.enableAirEnergyBalance()

                photosynthesis_model = PhotosynthesisModel(context)
                photosynthesis_model.setFarquharCoefficientsFromLibrary("Olive", uuids=leaf_uuids)

                # ----------------------------------------------------------- #
                # [PERF-1/2] UN SEUL RadiationModel pour tout le stade.
                # ----------------------------------------------------------- #
                with RadiationModel(context) as radiation:
                    add_growth_radiation_bands(radiation)  # LW, PAR, NIR, SW

                    for band in ("LW", "NIR", "SW", "PAR"):
                        radiation.setScatteringDepth(band, 3)
                        radiation.setDirectRayCount(band, 100)
                        radiation.setDiffuseRayCount(band, 1000)
                    for band in ("NIR", "SW", "PAR"):
                        radiation.disableEmission(band)  # courtonde : pas d'émission thermique

                    # Caméras ajoutées AVANT updateGeometry (rendu seulement à midi).
                    setup_radiation_cameras(radiation, scene_center=center)

                    # Source solaire créée une fois ; direction/flux mis à jour par heure.
                    sun_source = radiation.addCollimatedRadiationSource(vec3(0, 0, -1))

                    radiation.updateGeometry()  # BVH construite UNE fois pour le stade

                    for i, hour in enumerate(hours):
                        print(f"\n----- HOUR {hour:02d} -----")
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

                            par_flux = solar_position.getSolarFluxPAR(
                                pressure_Pa=pressure_pa, temperature_K=air_temperature_k,
                                humidity_rel=air_humidity, turbidity=turbidity,
                            )
                            nir_flux = solar_position.getSolarFluxNIR(
                                pressure_Pa=pressure_pa, temperature_K=air_temperature_k,
                                humidity_rel=air_humidity, turbidity=turbidity,
                            )
                            diffuse_fraction = solar_position.getDiffuseFraction(
                                pressure_Pa=pressure_pa, temperature_K=air_temperature_k,
                                humidity_rel=air_humidity, turbidity=turbidity,
                            )
                            lw_flux = _getAmbientLongwaveFlux(air_temperature_k, air_humidity)
                            sw_flux = par_flux + nir_flux

                        # [PERF-1] mise à jour de la source en place (pas de rebuild).
                        radiation.setSourcePosition(sun_source, sun_dir)
                        for band, flux in (("SW", sw_flux), ("PAR", par_flux), ("NIR", nir_flux)):
                            radiation.setSourceFlux(sun_source, band, flux * (1.0 - diffuse_fraction))
                            radiation.setDiffuseRadiationFlux(band, flux * diffuse_fraction)
                        radiation.setDiffuseRadiationFlux("LW", lw_flux)

                        # Entrées atmosphériques (Ta par primitive, init T_ABL au 1er pas).
                        apply_energy_balance_inputs(
                            context, simulation_uuids, air_temperature_k, air_humidity,
                            wind_speed, pressure_pa, reset_surface_temperature=(i == 0),
                        )
                        for label, val in (
                            ("air_temperature", air_temperature_k), ("air_humidity", air_humidity),
                            ("wind_speed", wind_speed), ("air_pressure", pressure_pa),
                            ("temperature", air_temperature_k),
                        ):
                            context.setPrimitiveDataFloat(sensor_uuids, label, val)

                        with BoundaryLayerConductanceModel(context) as blc:
                            blc.setBoundaryLayerModel("Ground", ground_uuids)
                            context.setPrimitiveDataFloat(leaf_uuids, "object_length", 0.05)
                            blc.setBoundaryLayerModel("Pohlhausen", leaf_uuids)
                            context.setPrimitiveDataFloat(wpt_leaf_uuids, "object_length", 0.05)
                            blc.setBoundaryLayerModel("Pohlhausen", wpt_leaf_uuids)
                            blc.setBoundaryLayerModel("InclinedPlate", bat_uuids)
                            blc.run()

                            # Radiation initiale (toutes bandes groupées).
                            radiation.runBand(["SW", "PAR", "NIR", "LW"])

                            if hour == CAMERA_EXPORT_HOUR:
                                export_growth_camera_outputs(radiation, output_dir, age, hour)

                            # Contrôle SW ≈ PAR + NIR.
                            sw = context.getPrimitiveData(reference_ground_uuid, "radiation_flux_SW")
                            par = context.getPrimitiveData(reference_ground_uuid, "radiation_flux_PAR")
                            nir = context.getPrimitiveData(reference_ground_uuid, "radiation_flux_NIR")
                            print(f"SW={sw:.1f}  PAR+NIR={par+nir:.1f}  écart={abs(sw-(par+nir)):.1f} W/m2")

                            # --- Couplage surface <-> radiation à temps figé ---
                            stomatal_model.run(leaf_uuids)
                            for _ in range(2):
                                energy_balance_model.run(dt=600.0)     # relaxation T de surface
                                radiation.runBand("LW")                # ré-émission LW (T à jour)
                                stomatal_model.run(leaf_uuids)

                        # [BUG-1] l'air n'avance qu'UNE fois pour cette heure.
                        energy_balance_model.evaluateAirEnergyBalance(
                            dt_sec=60.0, time_advance_sec=3600.0
                        )

                        photosynthesis_model.runForPrimitives(leaf_uuids)

                        # --- WUE canopée ---
                        A_canopy = E_canopy = 0.0
                        for uuid in leaf_uuids:
                            E = context.getPrimitiveData(uuid, "latent_flux")
                            A = context.getPrimitiveData(uuid, "net_photosynthesis")
                            E_mmol = E / 44000.0 * 1000.0   # W/m2 -> mmol H2O/m2/s (lambda~44 kJ/mol)
                            E_canopy += E_mmol
                            A_canopy += A
                            context.setPrimitiveDataFloat(
                                uuid, "WUE", A / E_mmol if abs(E_mmol) > 1e-10 else 0.0
                            )
                        WUE_canopy = A_canopy / E_canopy if abs(E_canopy) > 1e-10 else 0.0
                        print(f"WUE canopée = {WUE_canopy:.3f} umol CO2/mmol H2O")

                        # --- Diagnostics (accès direct : données garanties présentes) ---
                        if leaf_uuids:
                            par_vals = [context.getPrimitiveData(u, "radiation_flux_PAR")
                                        for u in leaf_uuids[:10]]
                            temps = [context.getPrimitiveData(u, "temperature") - 273.15
                                     for u in leaf_uuids[:10]]
                            print(f"PAR feuilles (W/m2): min={min(par_vals):.1f} max={max(par_vals):.1f}")
                            print(f"T feuilles (°C): min={min(temps):.1f} max={max(temps):.1f}")

                        wall_flux_total = sum(
                            context.getPrimitiveData(w, "radiation_flux_SW") for w in vertical_walls
                        )
                        print(f"Flux murs = {wall_flux_total:.1f} W/m2")

                        # Carte de température sol (matrice ny x nx).
                        ground_temp_matrix = np.empty((ny, nx))
                        for j in range(ny):
                            for k in range(nx):
                                t = context.getPrimitiveData(ground_patches[j][k], "temperature")
                                ground_temp_matrix[j, k] = t - 273.15

                        df_tmrt = compute_MRT(context, mrt_patches, output_dir, sigma=5.67e-8)

                        # --- Figures ---
                        plt.figure(figsize=(7, 5))
                        plt.imshow(df_tmrt.values, cmap="inferno", origin="lower", vmin=20, vmax=70)
                        plt.colorbar(label="TMRT (°C)")
                        plt.title(f"TMRT {age}j {hour:02d}h "
                                  f"({'piéton 1.5m' if mrt_at_pedestrian_height else 'sol'})")
                        plt.tight_layout()
                        plt.savefig(os.path.join(output_dir, f"tmrt_growth_{age:02d}days_{hour:02d}h.png"), dpi=180)
                        plt.close()

                        plt.figure(figsize=(7, 5))
                        plt.imshow(ground_temp_matrix, cmap="inferno", origin="lower", vmin=20, vmax=70,
                                   extent=[-size_total.x/2, size_total.x/2, -size_total.y/2, size_total.y/2])
                        plt.colorbar(label="T sol (°C)")
                        plt.xlabel("X (m)"); plt.ylabel("Y (m)")
                        plt.title(f"T ground {age}j {hour:02d}h")
                        plt.tight_layout()
                        plt.savefig(os.path.join(output_dir, f"temperature_ground_{age:02d}days_{hour:02d}h.png"), dpi=180)
                        plt.close()

                        irr_ref = context.getPrimitiveData(reference_ground_uuid, "radiation_flux_SW")
                        print(f"Stade {age}j / {hour:02d}h / SW référence = {irr_ref:.1f} W/m2")

                context.writeOBJ(f"{output_dir}/scene_growth_{age:02d}days.obj")


if __name__ == "__main__":
    growth_stages = [365, 730, 1095, 1460, 1825]
    run_growth_tmrt_example(
        longitude=-1.15,
        latitude=46.166672,
        utc_offset=1,
        pressure_pa=101300.0,
        turbidity=0.05,
        hours=[12],
        growth_steps_days=growth_stages,
        output_dir="resultats_ombres_growth",
        mrt_at_pedestrian_height=True,   # [MRT] z=1.5m (ISO 7726). False = sol.
    )