#!/usr/bin/env python3
"""
PyHelios Visualizer Demo

This example demonstrates the core functionality of the PyHelios Visualizer
plugin for 3D visualization of plant models and simulation results.

The example shows:
1. Basic Context and geometry creation
2. Tree generation using WeberPennTree
3. Interactive 3D visualization
4. Camera and lighting control
5. Image export capabilities

Requirements:
- PyHelios built with visualizer plugin
- OpenGL-capable graphics system
"""
import csv
import sys
import os

# Add PyHelios to path if running from examples directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from pyhelios import (
        Context,
        Visualizer,
        WeberPennTree,
        WPTType,
        RadiationModel,
        SolarPosition,
    )
    from pyhelios.types import *

    if hasattr(Visualizer, "VisualizerError"):
        from pyhelios.Visualizer import VisualizerError
    else:
        VisualizerError = Exception
except ImportError as e:
    print(f"Error importing PyHelios: {e}")
    print("Make sure PyHelios is installed and built with visualizer plugin.")
    sys.exit(1)


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
            tree_origin = vec3(0, 0, 0)
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


def demonstrate_basic_visualization():
    """Demonstrate basic visualization functionality."""
    print("\n=== Basic Visualization Demo ===")

    # Paramètres du sol
    center = vec3(0, 0, 0)
    size_total = vec2(8, 8)  # taille globale du sol (m)
    nx, ny = 4, 4  # nombre de subdivisions

    dx = size_total.x / nx
    dy = size_total.y / ny

    try:
        with Context() as context:
            context.setDate(2025, 10, 10)
            latitude = -1.15
            longitude = 46
            UTC = 7

            # Create geometry
            ground_uuid = context.addPatch(
                center=vec3(0, 0, 0), size=vec2(50, 50), color=RGBcolor(0.4, 0.3, 0.2)
            )

            # Patch de référence (plein soleil, décalé de 50 m)
            ref_ground_uuid = context.addPatch(
                center=vec3(10, 0, 0), size=vec2(10, 10), color=RGBcolor(0.2, 0.7, 0.2)
            )

            print(ground_uuid)

            # tree_id, tree_uuids = create_sample_tree(context)
            bat_uuids = context.loadOBJ("models/MAISON_EP_1.obj")

            # Set initial conditions
            all_uuids = context.getAllUUIDs()
            for uuid in bat_uuids:
                context.setPrimitiveDataFloat(uuid, "temperature", 20.0)

            # Fichier CSV de sortie
            with open("ombres.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["heure", "flux_sol", "flux_ref", "fraction_ombre"])

                for hour in range(6, 19):
                    context.setTime(hour=hour)
                    solar_position = SolarPosition(context, UTC, latitude, longitude)
                    sun_dir = solar_position.getSunDirectionVector()

                    # Gtheta = 0
                    # area_total = 0
                    # for uuid in [ground_uuid] :
                    #     print(uuid)
                    #     normal = context.getPrimitiveNormal(uuid)
                    #     area = context.getPrimitiveArea(uuid)
                    #     print("normal : ",normal)
                    #     print("area : ",area)
                    #     dot = sun_dir.x * normal.x + sun_dir.y * normal.y + sun_dir.z * normal.z
                    #     Gtheta += abs(dot) * area  # ajoute la contribution pondérée par l'aire
                    #     print("Gtheta : ",Gtheta)
                    #     # area_total += area
                    #
                    # print(f"Gtheta: {Gtheta}")
                    # print(f"Area: {area_total}")

                    # Run radiation simulation if available
                    try:
                        with RadiationModel(context) as rad:
                            sun_source = rad.addCollimatedRadiationSource(sun_dir)

                            rad.addRadiationBand("SW")
                            rad.setDirectRayCount(
                                "SW", 20000
                            )  # plus de rayons = plus de précision
                            rad.disableEmission("SW")
                            rad.setDiffuseRayCount("SW", 300)
                            rad.setSourceFlux(sun_source, "SW", 800)
                            rad.setDiffuseRadiationFlux("SW", 200)
                            rad.setScatteringDepth("SW", 3)

                            rad.updateGeometry()
                            rad.runBand("SW")

                            # Lire le flux reçu sur le sol
                            irr = context.getPrimitiveData(
                                ground_uuid, "radiation_flux_SW"
                            )
                            # Pour un cas clair, on peut estimer le flux incident "théorique"
                            # comme l’irradiance directe horizontale sous soleil perpendiculaire
                            cosZ = max(0, sun_dir.z)  # projection sur plan horizontal
                            flux_incident = (
                                1000 * cosZ
                            )  # W/m² arbitrairement (1 kW/m² max)

                            # Calcul de la fraction ombrée (si flux reçu << flux incident)
                            if flux_incident > 0:
                                frac_ombre = max(0, 1 - irr / flux_incident)
                            else:
                                frac_ombre = 0.0

                            # Lire les flux radiatifs
                            irr_sol = context.getPrimitiveData(
                                ground_uuid, "radiation_flux_SW"
                            )
                            irr_ref = context.getPrimitiveData(
                                ref_ground_uuid, "radiation_flux_SW"
                            )

                            if irr_ref and irr_ref > 0:
                                frac_ombre = max(0, 1 - irr_sol / irr_ref)
                            else:
                                frac_ombre = 0.0

                            writer.writerow(
                                [
                                    hour,
                                    f"{irr_sol:.2f}",
                                    f"{irr_ref:.2f}",
                                    f"{frac_ombre:.3f}",
                                ]
                            )
                            print(
                                f"{hour:02d}h : sol = {irr_sol:.1f} W/m², ref = {irr_ref:.1f} W/m² → ombre = {frac_ombre*100:.1f}%"
                            )
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
                    visualizer.setLightingModel(
                        "phong_shadowed"
                    )  # Nice lighting with shadows
                    # visualizer.setLightingModel(visualizer.LIGHTING_NONE)    # Nice lighting with shadows
                    visualizer.buildContextGeometry(context)

                    # visualizer.colorContextPrimitivesByData("radiation_flux_SW")
                    #
                    # visualizer.enableColorbar()
                    # visualizer.setColorbarRange(200, 1000)
                    # visualizer.setColorbarTitle("Radiation Flux")

                    # Set a good camera position to view the scene
                    camera_pos = vec3(8, 8, 6)  # Camera position
                    look_at = vec3(1.5, 1.5, 0.5)  # Look at center of geometry
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

    except VisualizerError as e:
        print(f"Visualization error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

    return True


def demonstrate_lighting_comparison():
    """Demonstrate different lighting models."""
    print("\n=== Lighting Model Comparison ===")

    try:
        with Context() as context:
            # Create a simple scene for lighting comparison
            center = vec3(0, 0, 0)
            size = vec2(2, 2)
            color = RGBcolor(0.7, 0.5, 0.3)
            context.addPatch(center=center, size=size, color=color)

            # Add a second patch at an angle for better lighting visualization
            center2 = vec3(1, 0, 1)
            rotation = SphericalCoord(
                1.0, 0.5, 0.3
            )  # Some rotation (radius, elevation, azimuth)
            context.addPatch(center=center2, size=size, rotation=rotation, color=color)

            with Visualizer(600, 400, headless=True) as visualizer:
                visualizer.buildContextGeometry(context)
                bg_color = RGBcolor(0.1, 0.1, 0.1)
                visualizer.setBackgroundColor(bg_color)
                light_dir = vec3(1, 1, -0.5)
                visualizer.setLightDirection(light_dir)

                # Camera position for good lighting view
                camera_pos = vec3(3, 3, 2)
                look_at = vec3(0.5, 0, 0.5)
                visualizer.setCameraPosition(camera_pos, look_at)

                # Test different lighting models
                lighting_modes = [
                    (Visualizer.LIGHTING_NONE, "lighting_none.jpg"),
                    (Visualizer.LIGHTING_PHONG, "lighting_phong.jpg"),
                    (Visualizer.LIGHTING_PHONG_SHADOWED, "lighting_shadowed.jpg"),
                ]

                print("Comparing lighting models...")
                for mode, filename in lighting_modes:
                    visualizer.setLightingModel(mode)
                    visualizer.plotUpdate()

                    output_path = os.path.join(os.path.dirname(__file__), filename)
                    visualizer.printWindow(output_path)

                    mode_names = {0: "None", 1: "Phong", 2: "Phong with Shadows"}
                    print(f"  Saved {mode_names[mode]}: {filename}")

    except VisualizerError as e:
        print(f"Lighting comparison error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

    return True


def main():
    """Run the PyHelios Visualizer demo."""
    print("PyHelios Visualizer Demo")
    print("========================")

    # Check if we can create a visualizer
    try:
        # Quick test with small headless visualizer
        test_viz = Visualizer(100, 100, headless=True)
        test_viz.__exit__(None, None, None)  # Clean up
        print("✓ Visualizer plugin is available")
    except VisualizerError as e:
        print("✗ Visualizer plugin is not available")
        print(f"Error: {e}")
        print("\nTo enable visualization, build PyHelios with:")
        print("  build_scripts/build_helios --plugins visualizer")
        return 1

    success_count = 0
    total_demos = 3

    # Run demonstrations
    if demonstrate_basic_visualization():
        success_count += 1

    # if demonstrate_lighting_comparison():
    #     success_count += 1

    print(f"\n=== Demo Summary ===")
    print(f"Completed {success_count}/{total_demos} demonstrations successfully")

    if success_count == total_demos:
        print("✓ All demonstrations completed successfully!")
        print("\nGenerated image files:")
        image_files = [
            "view_perspective.jpg",
            "view_side.jpg",
            "view_front.jpg",
            "view_top.jpg",
            "lighting_none.jpg",
            "lighting_phong.jpg",
            "lighting_shadowed.jpg",
        ]
        for img in image_files:
            img_path = os.path.join(os.path.dirname(__file__), img)
            if os.path.exists(img_path):
                print(f"  - {img}")

        return 0
    else:
        print("⚠ Some demonstrations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
