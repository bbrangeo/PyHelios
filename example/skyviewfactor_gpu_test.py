#!/usr/bin/env python3
"""
Test SkyViewFactor GPU implementation
"""

import sys
import os
import time
import numpy as np

# Add PyHelios to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyhelios import Context, SkyViewFactorModel
from pyhelios.wrappers.DataTypes import vec3

def create_test_scene():
    """Create a test scene with obstacles"""
    context = Context()
    
    # Add some triangles as obstacles
    for i in range(5):
        for j in range(5):
            x = i * 2.0 - 4.0
            y = j * 2.0 - 4.0
            z = 3.0
            
            context.addTriangle(
                vec3(x, y, z),
                vec3(x + 1.5, y, z),
                vec3(x, y + 1.5, z)
            )
    
    return context

def test_gpu_implementation():
    """Test the GPU implementation"""
    print("🚀 Testing SkyViewFactor GPU implementation...")
    
    # Create context and model
    context = create_test_scene()
    print(f"✓ Created scene with {len(context.getAllUUIDs())} primitives")
    
    # Create SkyViewFactor model
    svf_model = SkyViewFactorModel(context)
    print(f"✓ SkyViewFactor model created")
    print(f"  - CUDA available: {svf_model.is_cuda_available()}")
    print(f"  - OptiX available: {svf_model.is_optix_available()}")
    
    # Test points
    test_points = [
        vec3(0.0, 0.0, 0.0),
        vec3(2.0, 2.0, 0.0),
        vec3(-2.0, -2.0, 0.0),
        vec3(5.0, 5.0, 0.0),
        vec3(-5.0, -5.0, 0.0)
    ]
    
    print(f"\n🎯 Testing {len(test_points)} points...")
    
    results = []
    for i, point in enumerate(test_points):
        print(f"\n📍 Point {i+1}: ({point.x}, {point.y}, {point.z})")
        
        # Calculate sky view factor
        start_time = time.time()
        svf = svf_model.calculate_sky_view_factor(point.x, point.y, point.z)
        end_time = time.time()
        
        results.append(svf)
        print(f"   SVF: {svf:.4f}")
        print(f"   Time: {(end_time - start_time)*1000:.2f} ms")
    
    # Test batch calculation
    print(f"\n🔄 Testing batch calculation...")
    start_time = time.time()
    batch_results = svf_model.calculate_sky_view_factor_from_uuids(
        context.getAllUUIDs()[:10],  # Test with first 10 UUIDs
        batch_size=5,
        num_threads=4
    )
    end_time = time.time()
    
    print(f"✓ Batch calculation completed in {(end_time - start_time)*1000:.2f} ms")
    print(f"   Results: {len(batch_results)} sky view factors")
    print(f"   Average SVF: {np.mean(batch_results):.4f}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_gpu_implementation()
