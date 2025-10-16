#!/usr/bin/env python3
"""
PyHelios RadiationModel Camera Functions Example (v1.3.47)

This example demonstrates the new camera functionality introduced in PyHelios v1.3.47,
including:
- Camera image generation with filename returns
- Object detection bounding box generation (YOLO format)
- Segmentation mask generation (COCO JSON format)
- Auto-calibrated camera images with color correction

Requirements:
- PyHelios with radiation plugin built and enabled
- NVIDIA GPU with CUDA and OptiX support
"""

from pyhelios import (
    Context,
    WeberPennTree,
    WPTType,
    RadiationModel,
    RadiationModelError,
)
from pyhelios.types import *
import os
import traceback


def main():
    """Main example demonstrating camera functions in RadiationModel v1.3.47."""

    print("PyHelios RadiationModel Camera Functions Example (v1.3.47)")
    print("=" * 60)

    # Create output directory for images and data
    output_dir = "./camera_output"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    try:
        # Create 3D scene with labeled geometry for ML training
        print("\n1. Creating 3D scene with data labels...")
        context = Context()

        # Generate a tree with proper labeling for ML training
        wpt = WeberPennTree(context)
        wpt.setBranchRecursionLevel(3)
        wpt.setTrunkSegmentResolution(6)
        wpt.setLeafSubdivisions(4, 4)
        tree_id = wpt.buildTree(WPTType.LEMON)  # Detailed leaves

        # Get tree component UUIDs for labeling
        leaf_uuids = wpt.getLeafUUIDs(tree_id)
        branch_uuids = wpt.getBranchUUIDs(tree_id)
        trunk_uuids = wpt.getTrunkUUIDs(tree_id)

        # Add semantic labels for machine learning training
        for uuid in leaf_uuids:
            context.setPrimitiveDataString(uuid, "plant_part", "leaf")
            context.setPrimitiveDataString(uuid, "species", "citrus")
            context.setPrimitiveDataInt(uuid, "health", 100)  # Healthy leaves

        for uuid in branch_uuids:
            context.setPrimitiveDataString(uuid, "plant_part", "branch")
            context.setPrimitiveDataString(uuid, "species", "citrus")

        for uuid in trunk_uuids:
            context.setPrimitiveDataString(uuid, "plant_part", "trunk")
            context.setPrimitiveDataString(uuid, "species", "citrus")

        # Add ground plane with soil labeling
        ground_uuid = context.addPatch(
            center=vec3(0, 0, -0.5),
            size=vec2(8, 8),
            color=RGBcolor(0.4, 0.3, 0.2),  # Brown soil
        )
        context.setPrimitiveDataString(ground_uuid, "plant_part", "soil")
        context.setPrimitiveDataString(ground_uuid, "surface_type", "agricultural_soil")

        print(
            f"  Tree generated with {len(leaf_uuids)} leaves, {len(branch_uuids)} branches"
        )
        print(f"  Ground plane added with soil labeling")

        # Set up radiation simulation with cameras
        print("\n2. Configuring radiation simulation...")
        with RadiationModel(context) as radiation:
            # Configure radiation bands for realistic imaging
            bands = ["Red", "Green", "Blue", "NIR"]
            for band in bands:
                radiation.addRadiationBand(band)

            # Add realistic sun source
            sun_id = radiation.addSunSphereRadiationSource(
                radius=0.5,
                zenith=35.0,  # Mid-morning sun angle
                azimuth=120.0,  # Southeast direction
                angular_width=0.53,  # Realistic sun angular width
            )

            # Set realistic solar flux values (W/m²)
            solar_flux = {
                "Red": 280.0,  # Peak solar irradiance in red
                "Green": 320.0,  # Peak in green
                "Blue": 180.0,  # Lower blue content
                "NIR": 350.0,  # High NIR content from sun
            }

            for band, flux in solar_flux.items():
                radiation.setSourceFlux(sun_id, band, flux)
                # Add diffuse sky radiation (typically 10-15% of direct)
                radiation.setDiffuseRadiationFlux(band, flux * 0.12)

            # Configure ray tracing quality (higher = better quality, slower)
            quality_settings = {
                "direct_rays": 2000,
                "diffuse_rays": 5000,
                "scattering_depth": 2,
            }

            for band in bands:
                radiation.setDirectRayCount(band, quality_settings["direct_rays"])
                radiation.setDiffuseRayCount(band, quality_settings["diffuse_rays"])
                radiation.setScatteringDepth(band, quality_settings["scattering_depth"])

            print(
                f"  Configured {len(bands)} radiation bands with realistic solar spectrum"
            )
            print(
                f"  Ray tracing quality: {quality_settings['direct_rays']} direct, {quality_settings['diffuse_rays']} diffuse rays"
            )

            # Run radiation simulation
            print("\n3. Running radiation simulation...")
            radiation.updateGeometry()
            radiation.runBand(bands)  # Efficient multi-band execution
            print("  ✅ Radiation simulation completed")

            # Demonstrate new camera functions
            print("\n4. Generating camera images (v1.3.47 features)...")

            # Generate RGB camera image - now returns filename!
            rgb_filename = radiation.writeCameraImage(
                camera="overhead_rgb",
                bands=["Red", "Green", "Blue"],
                imagefile_base="lemon_tree_rgb",
                image_path=output_dir,
                flux_to_pixel_conversion=1.2,
            )
            print(f"  📷 RGB image: {rgb_filename}")

            # Generate NIR false-color image
            nir_filename = radiation.writeNormCameraImage(
                camera="side_view_nir",
                bands=["NIR", "Red"],
                imagefile_base="lemon_tree_false_color",
                image_path=output_dir,
            )
            print(f"  📷 NIR false-color: {nir_filename}")

            # Generate raw ASCII data for analysis
            radiation.writeCameraImage(
                camera="overhead_rgb",
                band="Green",
                imagefile_base="green_channel_data",
                image_path=output_dir,
            )
            print(f"  📊 Raw data: {output_dir}/green_channel_data*")

            print("\n5. Generating ML training data...")

            # Generate YOLO-format bounding boxes for object detection
            radiation.writeImageBoundingBoxes(
                camera_label="overhead_rgb",
                primitive_data_labels=["leaf", "branch", "trunk", "soil"],
                object_class_ids=[0, 1, 2, 3],  # YOLO class indices
                image_file=rgb_filename,
                classes_txt_file=f"{output_dir}/plant_classes.txt",
                image_path=output_dir,
            )
            print(
                f"  🎯 Object detection: {output_dir}/plant_classes.txt + YOLO labels"
            )

            # Generate COCO-format segmentation masks
            radiation.writeImageSegmentationMasks(
                camera_label="overhead_rgb",
                primitive_data_labels=["leaf", "branch", "trunk", "soil"],
                object_class_ids=[10, 11, 12, 13],  # COCO category IDs
                json_filename=f"{output_dir}/lemon_tree_segmentation.json",
                image_file=rgb_filename,
                append_file=False,
            )
            print(f"  🧩 Segmentation masks: {output_dir}/lemon_tree_segmentation.json")

            print("\n6. Auto-calibrating images...")

            # Test different color correction algorithms
            algorithms = [
                ("DIAGONAL_ONLY", "Fast white balance correction"),
                (
                    "MATRIX_3X3_AUTO",
                    "Full matrix with stability fallback (recommended)",
                ),
                ("MATRIX_3X3_FORCE", "Force full matrix calculation"),
            ]

            calibrated_files = []
            for algorithm, description in algorithms:
                try:
                    calibrated_filename = radiation.autoCalibrateCameraImage(
                        camera_label="overhead_rgb",
                        red_band_label="Red",
                        green_band_label="Green",
                        blue_band_label="Blue",
                        output_file_path=f"{output_dir}/calibrated_{algorithm.lower()}.jpg",
                        algorithm=algorithm,
                        print_quality_report=(
                            algorithm == "MATRIX_3X3_AUTO"
                        ),  # Report for recommended algorithm
                        ccm_export_file_path=(
                            f"{output_dir}/ccm_{algorithm.lower()}.txt"
                            if algorithm == "MATRIX_3X3_AUTO"
                            else ""
                        ),
                    )
                    calibrated_files.append((algorithm, calibrated_filename))
                    print(f"  🎨 {algorithm}: {calibrated_filename}")

                except Exception as e:
                    print(f"  ❌ {algorithm} failed: {e}")

            # Final results summary
            print("\n" + "=" * 60)
            print("🎉 Camera Functions Demo Completed Successfully!")
            print("=" * 60)

            print(f"\nGenerated Files in {output_dir}:")
            print(f"📷 Camera Images:")
            print(f"  • {rgb_filename} (RGB composite)")
            print(f"  • {nir_filename} (NIR false-color)")

            print(f"\n🤖 ML Training Data:")
            print(f"  • plant_classes.txt (YOLO class definitions)")
            print(f"  • *.txt files (YOLO bounding box labels)")
            print(f"  • lemon_tree_segmentation.json (COCO segmentation masks)")

            print(f"\n🎨 Auto-Calibrated Images:")
            for algorithm, filename in calibrated_files:
                print(f"  • {filename} ({algorithm})")

            print(f"\n📊 Analysis Data:")
            print(f"  • green_channel_data* (Raw spectral data)")
            print(f"  • ccm_*.txt (Color correction matrices)")

            print(f"\n💡 Usage Tips:")
            print(f"  • Use RGB images for visualization")
            print(f"  • Use YOLO labels for object detection training")
            print(f"  • Use COCO JSON for segmentation training")
            print(f"  • Use calibrated images for realistic rendering")
            print(f"  • Use raw data for spectral analysis")

            print(f"\n🔬 Next Steps:")
            print(f"  • Train YOLO models with generated bounding boxes")
            print(f"  • Train semantic segmentation with COCO masks")
            print(f"  • Analyze spectral signatures from raw data")
            print(f"  • Compare color correction algorithms")

    except RadiationModelError as e:
        print(f"\n❌ RadiationModel Error: {e}")
        print("\n💡 This likely means the radiation plugin is not available.")
        print("   To resolve this:")
        print("   1. Ensure you have an NVIDIA GPU with CUDA support")
        print("   2. Build PyHelios with radiation plugin:")
        print("      build_scripts/build_helios --plugins radiation")
        print("   3. Check plugin status:")
        print(
            '      python -c "from pyhelios.plugins import get_plugin_registry; print(get_plugin_registry().get_available_plugins())"'
        )

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

    finally:
        print(f"\n📁 Check output directory: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()
