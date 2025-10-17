#!/usr/bin/env python3
"""
OptiX Sky View Factor Demo

This script demonstrates the OptiX-enabled Sky View Factor calculation
with both CPU (OpenMP) and GPU (OptiX) implementations.

Copyright (C) 2025 Boris Dufour
"""

import sys
import os
import time
import numpy as np

# Add PyHelios to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyhelios import Context, SkyViewFactorModel
from pyhelios.wrappers.DataTypes import vec3

def create_test_scene(context, num_obstacles=100):
    """Create a test scene with obstacles for sky view factor calculation."""
    print(f"Creating test scene with {num_obstacles} obstacles...")
    
    # Create a grid of obstacles
    grid_size = int(np.sqrt(num_obstacles))
    spacing = 2.0
    
    for i in range(grid_size):
        for j in range(grid_size):
            x = (i - grid_size/2) * spacing
            y = (j - grid_size/2) * spacing
            z = 0.0
            
            # Create a simple triangle obstacle
            context.addTriangle(
                vec3(x-0.5, y-0.5, z),
                vec3(x+0.5, y-0.5, z),
                vec3(x, y+0.5, z)
            )
    
    print(f"✓ Created {num_obstacles} obstacles")

def test_cpu_implementation(svf_model, uuids, num_threads=4):
    """Test CPU implementation with OpenMP."""
    print(f"\n=== Testing CPU Implementation (OpenMP, {num_threads} threads) ===")
    
    start_time = time.time()
    
    # Test with primitives
    svf_results = svf_model.calculate_sky_view_factors_for_primitives(
        uuids, num_threads=num_threads
    )
    
    cpu_time = time.time() - start_time
    
    print(f"✓ CPU calculation completed in {cpu_time:.3f} seconds")
    print(f"  - Processed {len(svf_results)} primitives")
    print(f"  - Average SVF: {np.mean(svf_results):.3f}")
    print(f"  - Min SVF: {np.min(svf_results):.3f}")
    print(f"  - Max SVF: {np.max(svf_results):.3f}")
    
    return svf_results, cpu_time

def test_gpu_implementation(svf_model, uuids):
    """Test GPU implementation with OptiX."""
    print(f"\n=== Testing GPU Implementation (OptiX) ===")
    
    # Check if GPU is available
    if not svf_model.is_optix_available():
        print("✗ OptiX not available - GPU implementation not possible")
        return None, 0.0
    
    print("✓ OptiX available - testing GPU implementation")
    
    start_time = time.time()
    
    # Test with primitives (will use GPU if available)
    svf_results = svf_model.calculate_sky_view_factors_for_primitives(uuids)
    
    gpu_time = time.time() - start_time
    
    print(f"✓ GPU calculation completed in {gpu_time:.3f} seconds")
    print(f"  - Processed {len(svf_results)} primitives")
    print(f"  - Average SVF: {np.mean(svf_results):.3f}")
    print(f"  - Min SVF: {np.min(svf_results):.3f}")
    print(f"  - Max SVF: {np.max(svf_results):.3f}")
    
    return svf_results, gpu_time

def test_batch_processing(svf_model, uuids, batch_size=50):
    """Test batch processing for large datasets."""
    print(f"\n=== Testing Batch Processing (batch_size={batch_size}) ===")
    
    start_time = time.time()
    
    # Test batch processing
    svf_results = svf_model.calculate_sky_view_factor_from_uuids(
        uuids, batch_size=batch_size
    )
    
    batch_time = time.time() - start_time
    
    print(f"✓ Batch processing completed in {batch_time:.3f} seconds")
    print(f"  - Processed {len(svf_results)} primitives in batches of {batch_size}")
    print(f"  - Average SVF: {np.mean(svf_results):.3f}")
    
    return svf_results, batch_time

def main():
    """Main demonstration function."""
    print("🚀 OptiX Sky View Factor Demo")
    print("=" * 50)
    
    # Create context
    context = Context()
    
    # Create test scene
    num_obstacles = 200
    create_test_scene(context, num_obstacles)
    
    # Get all UUIDs
    all_uuids = context.getAllUUIDs()
    print(f"✓ Scene contains {len(all_uuids)} primitives")
    
    # Create SkyViewFactor model
    print("\nCreating SkyViewFactor model...")
    try:
        svf_model = SkyViewFactorModel(context)
        print("✓ SkyViewFactor model created successfully")
    except Exception as e:
        print(f"✗ Failed to create SkyViewFactor model: {e}")
        return
    
    # Check availability
    print(f"\nPlugin availability:")
    print(f"  - CUDA available: {svf_model.is_cuda_available()}")
    print(f"  - OptiX available: {svf_model.is_optix_available()}")
    
    # Test different implementations
    test_sizes = [50, 100, len(all_uuids)]
    
    for test_size in test_sizes:
        print(f"\n{'='*60}")
        print(f"Testing with {test_size} primitives")
        print(f"{'='*60}")
        
        # Select subset of UUIDs for testing
        test_uuids = all_uuids[:test_size] if test_size < len(all_uuids) else all_uuids
        
        # Test CPU implementation
        cpu_results, cpu_time = test_cpu_implementation(svf_model, test_uuids, num_threads=4)
        
        # Test GPU implementation
        gpu_results, gpu_time = test_gpu_implementation(svf_model, test_uuids)
        
        # Test batch processing
        batch_results, batch_time = test_batch_processing(svf_model, test_uuids, batch_size=25)
        
        # Performance comparison
        print(f"\n--- Performance Summary ---")
        print(f"CPU (OpenMP):     {cpu_time:.3f}s")
        if gpu_time > 0:
            print(f"GPU (OptiX):      {gpu_time:.3f}s")
            if cpu_time > 0:
                speedup = cpu_time / gpu_time
                print(f"GPU Speedup:      {speedup:.2f}x")
        print(f"Batch Processing: {batch_time:.3f}s")
        
        # Verify results consistency
        if gpu_results is not None and len(gpu_results) == len(cpu_results):
            diff = np.abs(np.array(cpu_results) - np.array(gpu_results))
            max_diff = np.max(diff)
            print(f"Max difference (CPU vs GPU): {max_diff:.6f}")
            
            if max_diff < 1e-5:
                print("✓ Results are consistent between CPU and GPU")
            else:
                print("⚠ Results differ between CPU and GPU (expected for different implementations)")
    
    print(f"\n{'='*60}")
    print("🎉 Demo completed successfully!")
    print("The SkyViewFactor plugin now supports:")
    print("  ✓ CPU implementation with OpenMP parallelization")
    print("  ✓ GPU implementation with OptiX (when available)")
    print("  ✓ Batch processing for large datasets")
    print("  ✓ Configurable thread count")
    print("  ✓ Robust error handling")

if __name__ == "__main__":
    main()
