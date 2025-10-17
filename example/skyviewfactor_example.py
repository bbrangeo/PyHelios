#!/usr/bin/env python3
"""
Example usage of the SkyViewFactor plugin in PyHelios.

This example demonstrates how to calculate sky view factors for points in a 3D scene
and visualize the results using a camera.
"""

import sys
import os
import numpy as np

# Add the pyhelios directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pyhelios import Context, SkyViewFactorModel, SkyViewFactorCamera
from pyhelios.wrappers.DataTypes import vec3


def main():
    print("Sky View Factor Plugin Example")
    print("==============================")

    # Create HELIOS context
    print("Creating 3D scene...")
    context = Context()

    # Add many obstacles to the scene to test robustness
    print("Adding multiple obstacles to test robustness...")
    
    # Create a grid of obstacles
    obstacle_uuids = []
    for i in range(-5, 6):  # 11x11 grid
        for j in range(-5, 6):
            if (i + j) % 3 == 0:  # Every third position
                # Create a small triangle obstacle
                uuid = context.addTriangle(
                    vec3(i - 0.2, j - 0.2, 0.0),
                    vec3(i + 0.2, j - 0.2, 0.0),
                    vec3(i, j + 0.2, 0.0)
                )
                obstacle_uuids.append(uuid)
    
    # Add some larger obstacles
    uuid1 = context.addTriangle(
        vec3(-2.0, -2.0, 0.0), vec3(2.0, -2.0, 0.0), vec3(0.0, 2.0, 0.0)
    )
    obstacle_uuids.append(uuid1)

    uuid2 = context.addTriangle(
        vec3(5.0, -1.0, 0.0), vec3(7.0, -1.0, 0.0), vec3(6.0, 1.0, 0.0)
    )
    obstacle_uuids.append(uuid2)

    uuid3 = context.addTriangle(
        vec3(3.0, 3.0, 0.0), vec3(4.0, 3.0, 0.0), vec3(3.5, 4.0, 0.0)
    )
    obstacle_uuids.append(uuid3)

    print(f"Scene created with {len(context.getAllUUIDs())} primitives")

    # Create SkyViewFactor model
    print("\nCreating SkyViewFactor model...")
    try:
        svf_model = SkyViewFactorModel(context)
        print("✓ SkyViewFactor model created successfully")
    except Exception as e:
        print(f"✗ Failed to create SkyViewFactor model: {e}")
        return

    # Configure the model
    svf_model.set_ray_count(2000)  # Use 2000 rays for good accuracy
    svf_model.set_max_ray_length(100.0)  # Maximum ray length of 100 units
    svf_model.set_message_flag(True)  # Enable console output

    print(f"Ray count: {svf_model.get_ray_count()}")
    print(f"Max ray length: {svf_model.get_max_ray_length()}")
    print(f"CUDA available: {svf_model.is_cuda_available()}")
    print(f"OptiX available: {svf_model.is_optix_available()}")

    # Define test points
    test_points = [
        (0.0, 0.0, 0.5),  # Point near building 1
        (3.0, 0.0, 0.5),  # Point between buildings
        (6.0, 0.0, 0.5),  # Point near building 2
        (3.5, 3.5, 0.5),  # Point near tree
        (0.0, 5.0, 0.5),  # Point away from obstacles
        (0.0, 0.0, 5.0),  # Point above obstacles
    ]

    print(f"\nCalculating sky view factors for {len(test_points)} points...")

    # Calculate sky view factors
    try:
        svf_model.set_max_ray_length(10.0)
        svf_model.set_message_flag(True)
        svf_model.set_ray_count(10)
        # svfs = svf_model.calculate_sky_view_factors(test_points)
        svfs = svf_model.calculate_sky_view_factors_for_primitives()
        print("✓ Sky view factors calculated successfully")
    except Exception as e:
        print(f"✗ Failed to calculate sky view factors: {e}")
        return

    success = svf_model.export_sky_view_factors("skyviewfactor_results.txt")

    # Test the new UUID-based calculation function
    print("\nTesting UUID-based sky view factor calculation...")
    try:
        # Get some UUIDs from the loaded model
        all_uuids = context.getAllUUIDs()
        if all_uuids:
            # Test with all UUIDs to demonstrate robustness
            print(f"Calculating SVF for {len(all_uuids)} primitives by UUID...")
            print("Using batch processing to handle large datasets robustly...")

            svf_uuids = svf_model.calculate_sky_view_factor_from_uuids(all_uuids, batch_size=25)
            print("✓ UUID-based calculation successful")
            print(f"Processed {len(svf_uuids)} primitives successfully")

            # Display results
            print("\nUUID-based Results:")
            print("==================")
            # Show results for first 10 and last 10 to demonstrate it works for all
            display_uuids = all_uuids[:10] + all_uuids[-10:] if len(all_uuids) > 20 else all_uuids
            display_svfs = svf_uuids[:10] + svf_uuids[-10:] if len(svf_uuids) > 20 else svf_uuids
            
            if len(all_uuids) > 20:
                print(f"(Showing first 10 and last 10 of {len(all_uuids)} results)")
            
            for i, (uuid, svf) in enumerate(zip(display_uuids, display_svfs)):
                # Get position for display by calculating center from vertices
                try:
                    vertices = context.getPrimitiveVertices(uuid)
                    if vertices:
                        center_x = sum(v.x for v in vertices) / len(vertices)
                        center_y = sum(v.y for v in vertices) / len(vertices)
                        center_z = sum(v.z for v in vertices) / len(vertices)
                        pos_str = f"({center_x:.2f}, {center_y:.2f}, {center_z:.2f})"
                    else:
                        pos_str = "Unknown"
                except:
                    pos_str = "Unknown"

                print(f"UUID {i}: {uuid} at {pos_str}: SVF = {svf:.3f}", end="")

                # Interpret the result
                if svf > 0.9:
                    print(" (Very open sky)")
                elif svf > 0.7:
                    print(" (Mostly open sky)")
                elif svf > 0.5:
                    print(" (Partially obstructed)")
                elif svf > 0.3:
                    print(" (Heavily obstructed)")
                else:
                    print(" (Very obstructed)")
        else:
            print("No primitives found in scene for UUID-based calculation")
    except Exception as e:
        print(f"✗ UUID-based calculation failed: {e}")

    # # Display results
    # print("\nResults:")
    # print("========")
    # for i, (point, svf) in enumerate(zip(test_points, svfs)):
    #     print(f"Point {i} at {point}: SVF = {svf:.3f}", end="")
    #
    #     # Interpret the result
    #     if svf > 0.9:
    #         print(" (Very open sky)")
    #     elif svf > 0.7:
    #         print(" (Mostly open sky)")
    #     elif svf > 0.5:
    #         print(" (Partially obstructed)")
    #     elif svf > 0.3:
    #         print(" (Heavily obstructed)")
    #     else:
    #         print(" (Very obstructed)")
    #
    # # Test CPU implementation for comparison
    # print("\nTesting CPU implementation...")
    # try:
    #     # Test a single point with CPU
    #     test_point = test_points[0]
    #     svf_cpu = svf_model.calculate_sky_view_factor_cpu(*test_point)
    #     print(f"CPU SVF at {test_point}: {svf_cpu:.3f}")
    #
    #     # Compare with GPU result
    #     gpu_svf = svfs[0]
    #     print(f"GPU SVF at {test_point}: {gpu_svf:.3f}")
    #     print(f"Difference: {abs(svf_cpu - gpu_svf):.3f}")
    #
    # except Exception as e:
    #     print(f"✗ CPU calculation failed: {e}")
    #
    # # Export results
    # print("\nExporting results...")
    # try:
    #     success = svf_model.export_sky_view_factors("skyviewfactor_results.txt")
    #     if success:
    #         print("✓ Results exported to skyviewfactor_results.txt")
    #     else:
    #         print("✗ Failed to export results")
    # except Exception as e:
    #     print(f"✗ Export failed: {e}")
    #
    # # Create camera for visualization
    # print("\nCreating camera for visualization...")
    # try:
    #     camera = svf_model.create_camera()
    #     print("✓ Camera created successfully")
    # except Exception as e:
    #     print(f"✗ Failed to create camera: {e}")
    #     return
    #
    # # Configure camera
    # camera.set_position(0.0, 0.0, 10.0)
    # camera.set_target(0.0, 0.0, 0.0)
    # camera.set_up(0.0, 1.0, 0.0)
    # camera.set_field_of_view(60.0)
    # camera.set_resolution(256, 256)
    # camera.set_ray_count(100)
    #
    # print(f"Camera position: {camera._position}")
    # print(f"Camera target: {camera._target}")
    # print(f"Resolution: {camera._resolution}")
    # print(f"Ray count per pixel: {camera._ray_count}")

    # # Render the sky view factor image
    # print("\nRendering sky view factor image...")
    # try:
    #     success = camera.render()
    #     if success:
    #         print("✓ Rendering successful")
    #     else:
    #         print("✗ Rendering failed")
    #         return
    # except Exception as e:
    #     print(f"✗ Rendering failed: {e}")
    #     return
    #
    # # Get image data
    # image_data = camera.get_image()
    # print(f"Image contains {len(image_data)} pixels")
    #
    # # Calculate image statistics
    # if image_data:
    #     min_svf = min(image_data)
    #     max_svf = max(image_data)
    #     avg_svf = sum(image_data) / len(image_data)
    #
    #     print(f"Image statistics:")
    #     print(f"  Min SVF: {min_svf:.3f}")
    #     print(f"  Max SVF: {max_svf:.3f}")
    #     print(f"  Avg SVF: {avg_svf:.3f}")
    #
    # # Export the image
    # print("\nExporting image...")
    # try:
    #     success = camera.export_image("skyviewfactor_visualization.ppm")
    #     if success:
    #         print("✓ Image exported to skyviewfactor_visualization.ppm")
    #     else:
    #         print("✗ Failed to export image")
    # except Exception as e:
    #     print(f"✗ Image export failed: {e}")
    #
    # # Display camera statistics
    # print("\nCamera statistics:")
    # print(camera.get_statistics())
    #
    # # Display model statistics
    # print("\nModel statistics:")
    # print(svf_model.get_statistics())
    #
    # # Test primitive centers calculation
    # print("\nCalculating sky view factors for primitive centers...")
    # try:
    #     primitive_svfs = svf_model.calculate_sky_view_factors_for_primitives()
    #     print(f"✓ Calculated SVFs for {len(primitive_svfs)} primitives")
    #
    #     for i, svf in enumerate(primitive_svfs):
    #         print(f"  Primitive {i}: SVF = {svf:.3f}")
    # except Exception as e:
    #     print(f"✗ Failed to calculate primitive SVFs: {e}")
    #
    # print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
