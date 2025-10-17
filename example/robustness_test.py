#!/usr/bin/env python3
"""
Test de robustesse pour la fonction calculate_sky_view_factor_from_uuids.

Ce script teste la fonction avec un très grand nombre de primitives
pour démontrer sa robustesse.
"""

import sys
import os
import time

# Add the pyhelios directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pyhelios import Context, SkyViewFactorModel
from pyhelios.wrappers.DataTypes import vec3


def create_large_scene(context, num_obstacles=200):
    """Create a large scene with many obstacles for testing."""
    print(f"Creating scene with {num_obstacles} obstacles...")

    uuids = []

    # Create a grid of obstacles
    import math

    grid_size = int(math.sqrt(num_obstacles))

    for i in range(grid_size):
        for j in range(grid_size):
            if len(uuids) >= num_obstacles:
                break

            # Create a small triangle obstacle
            x = (i - grid_size / 2) * 2.0
            y = (j - grid_size / 2) * 2.0

            uuid = context.addTriangle(
                vec3(x - 0.1, y - 0.1, 0.0),
                vec3(x + 0.1, y - 0.1, 0.0),
                vec3(x, y + 0.1, 0.0),
            )
            uuids.append(uuid)

    return uuids


def test_robustness():
    """Test the robustness of calculate_sky_view_factor_from_uuids."""
    print("Test de robustesse - calculate_sky_view_factor_from_uuids")
    print("=" * 60)

    # Create a single context and model to reuse
    print("Création du contexte et du modèle...")
    context = Context()

    # Create SkyViewFactor model once
    svf_model = SkyViewFactorModel(context)
    svf_model.set_ray_count(50)  # Use fewer rays for speed
    svf_model.set_max_ray_length(20.0)
    svf_model.set_message_flag(False)  # Disable console output

    # Test with different numbers of obstacles
    test_sizes = [5000, 10000]

    for num_obstacles in test_sizes:
        print(f"\n--- Test avec {num_obstacles} obstacles ---")

        try:
            # Clear previous scene and create new one
            context = Context()  # Create fresh context
            uuids = create_large_scene(context, num_obstacles)

            print(f"Scène créée avec {len(uuids)} primitives")

            # Recreate model for new context
            svf_model = SkyViewFactorModel(context)
            svf_model.set_ray_count(50)
            svf_model.set_max_ray_length(20.0)
            svf_model.set_message_flag(False)

            # Test with different batch sizes
            batch_sizes = [10, 25]

            for batch_size in batch_sizes:
                print(f"  Test avec batch_size={batch_size}...")

                start_time = time.time()

                try:
                    svf_results = svf_model.calculate_sky_view_factor_from_uuids(
                        uuids, batch_size=batch_size
                    )

                    end_time = time.time()
                    duration = end_time - start_time

                    print(
                        f"    ✓ Succès: {len(svf_results)} résultats en {duration:.2f}s"
                    )
                    print(f"    ✓ Vitesse: {len(svf_results)/duration:.1f} points/s")

                    # Verify results
                    if len(svf_results) == len(uuids):
                        print(f"    ✓ Tous les {len(uuids)} UUIDs ont été traités")
                    else:
                        print(
                            f"    ⚠ Seuls {len(svf_results)}/{len(uuids)} UUIDs traités"
                        )

                    # Check for valid results
                    valid_results = [svf for svf in svf_results if svf > 0]
                    print(f"    ✓ {len(valid_results)} résultats valides (SVF > 0)")

                except Exception as e:
                    print(f"    ✗ Échec: {e}")
                    break

                print()

        except Exception as e:
            print(f"✗ Erreur lors de la création de la scène: {e}")
            continue

    print("\nTest de robustesse terminé!")


if __name__ == "__main__":
    test_robustness()
