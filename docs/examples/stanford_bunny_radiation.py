#!/usr/bin/env python3
"""
Stanford Bunny Radiation Model Example

This example demonstrates PyHelios radiation modeling capabilities by replicating
the Stanford Bunny sample from the Helios C++ samples. It loads the Stanford Bunny
PLY file, sets up a radiation model with shortwave radiation, and visualizes the
radiation flux distribution using the native PyHelios visualizer plugin.

HARDWARE REQUIREMENTS:
- NVIDIA GPU with CUDA compute capability (for radiation simulation)
- CUDA Toolkit installed and configured
- OptiX ray tracing SDK installed
- OpenGL-compatible graphics system (for visualization)

SOFTWARE REQUIREMENTS:
- PyHelios with radiation and visualizer plugins enabled in native library
- Stanford Bunny PLY file (included in helios-core)

NOTE: This example demonstrates the full PyHelios workflow including native 3D visualization.
The radiation plugin requires GPU ray tracing hardware for full functionality.

This is the PyHelios equivalent of helios-core/samples/radiation_StanfordBunny/main.cpp
"""

import sys
import os
import numpy as np

# Add pyhelios to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pyhelios import Context, RadiationModel, Visualizer
from pyhelios.types import *


def main():
    """Main function demonstrating Stanford Bunny radiation simulation"""
    print("PyHelios Stanford Bunny Radiation Model Example")
    print("=" * 50)
    
    # Initialize context
    print("Creating PyHelios context...")
    with Context() as context:
        
        # Load Stanford Bunny PLY file  
        ply_path = os.path.join(os.path.dirname(__file__), '..', '..', 'helios-core', 'PLY', 'StanfordBunny.ply')
        
        print(f"Loading Stanford Bunny from: {ply_path}")
        
        if not os.path.exists(ply_path):
            print(f"ERROR: Stanford Bunny PLY file not found at {ply_path}")
            print("Please ensure the helios-core submodule is properly initialized.")
            return 1
            
        try:
            # Load bunny with scaling factor of 4 (same as C++ sample)
            bunny_uuids = context.loadPLY(ply_path, 
                                        origin=vec3(0, 0, 0), 
                                        height=4.0, 
                                        upaxis="YUP")
            
            print(f"Loaded Stanford Bunny with {len(bunny_uuids)} triangles")
            
        except Exception as e:
            print(f"Failed to load Stanford Bunny PLY file: {e}")
            print("This might be because native Helios libraries are not available.")
            print("The radiation model requires native library support.")
            return 1
        
        # Add ground patches (similar to C++ sample)
        print("Adding ground patches...")
        
        # Ground parameters (matching C++ sample)
        D = 10  # Ground size
        size = int2(5, 5)  # Number of ground segments
        subsize = int2(50, 50)  # Subdivisions per segment
        dx = vec2(D / (size.x * subsize.x), D / (size.y * subsize.y))
        
        ground_uuids = []
        for j in range(size.y):
            for i in range(size.x):
                
                for jj in range(subsize.y):
                    for ii in range(subsize.x):
                        center = vec3(
                            -0.5 * D + (i * subsize.x + ii) * dx.x,
                            -0.5 * D + (j * subsize.y + jj) * dx.y,
                            0
                        )
                        
                        if (j * size.x + i) % 2 == 0:
                            # Silver patches with low reflectivity
                            color = RGBcolor(0.75, 0.75, 0.75)
                            patch_uuid = context.addPatch(center=center, size=dx, color=color)
                            context.setPrimitiveData(patch_uuid, "reflectivity_SW", 0.0)
                        else:
                            # White patches with higher reflectivity  
                            color = RGBcolor(1.0, 1.0, 1.0)
                            patch_uuid = context.addPatch(center=center, size=dx, color=color)
                            context.setPrimitiveData(patch_uuid, "reflectivity_SW", 0.6)

                        ground_uuids.append(patch_uuid)
        
        print(f"Added {len(ground_uuids)} ground patches")

        # Initialize radiation model
        
        try:
            print("Creating RadiationModel...")
            radiation_model = RadiationModel(context)
            print("✓ RadiationModel created successfully")
            
            # Add shortwave radiation band
            radiation_model.addRadiationBand("SW")
            
            radiation_model.disableEmission("SW")
            radiation_model.setDirectRayCount("SW", 100)
            radiation_model.setDiffuseRayCount("SW", 300)

            sun_direction = vec3(0.4, -0.4, 0.6)
            sun_source = radiation_model.addCollimatedRadiationSource(sun_direction)

            radiation_model.setSourceFlux(sun_source, "SW", 800.0)
            radiation_model.setDiffuseRadiationFlux("SW", 200.0)
            radiation_model.setScatteringDepth("SW", 3)
            
            print("Running radiation simulation...")
            
            # Update geometry and run simulation
            print("Updating geometry for radiation model...")
            radiation_model.updateGeometry()
            
            print("Running radiation band simulation...")
            radiation_model.runBand("SW")
            print("✓ Radiation simulation completed")

            # Verify radiation data was created
            print("Checking radiation flux data after simulation...")
            # Use a better sampling strategy - sample from multiple regions
            sample_size = min(20, len(bunny_uuids))
            sample_uuids = []
            
            # Sample from different regions to find flux data
            for i in range(0, len(bunny_uuids), len(bunny_uuids) // sample_size):
                if len(sample_uuids) < sample_size:
                    sample_uuids.append(bunny_uuids[i])
            
            # Add some from the optimal range we found (900-1000)
            optimal_start = 900
            if optimal_start < len(bunny_uuids):
                sample_uuids.extend(bunny_uuids[optimal_start:optimal_start+10])
            
            sample_uuids = sample_uuids[:20]  # Limit to 20 samples
            flux_values = []
            
            for uuid in sample_uuids:
                try:
                    flux = context.getPrimitiveData(uuid, "radiation_flux_SW")
                    flux_values.append(flux)
                    print(f"  UUID {uuid}: flux = {flux}")
                except Exception as e:
                    print(f"  UUID {uuid}: error reading flux - {e}")
                    flux_values.append(0.0)
            
            max_flux = max(flux_values) if flux_values else 0.0
            nonzero_count = sum(1 for f in flux_values if f > 0.0)
            avg_flux = sum(flux_values) / len(flux_values) if flux_values else 0.0
            print(f"  Found {nonzero_count}/{len(flux_values)} primitives with non-zero flux, max = {max_flux:.3f}")
            print(f"  Average flux: {avg_flux:.3f} W/m²")

            if nonzero_count == 0:
                raise RuntimeError(
                    "❌ RadiationModel simulation failed: No radiation flux values were computed.\\n"
                    "   \\n" 
                    "   This indicates the radiation plugin is not functional on this system.\\n"
                    "   The most likely cause is missing CUDA/OptiX GPU ray tracing support.\\n"
                    "   \\n"
                    "   REQUIREMENTS: Helios radiation simulation requires:\\n"
                    "   - NVIDIA GPU with CUDA compute capability\\n"
                    "   - CUDA Toolkit properly installed\\n"
                    "   - OptiX ray tracing SDK\\n"
                    "   - Native library built with radiation plugin enabled\\n"
                    "   \\n"
                    "   Run this example on a CUDA-enabled Linux system."
                )
            
            # Success! We have flux data - radiation simulation is working
            print(f"\\n✅ SUCCESS: GPU radiation simulation is functional!")
            
            print(f"   ⚡ Processed {len(bunny_uuids):,} triangles with GPU")
            print(f"   🔬 Average flux computed: {avg_flux:.1f} W/m²")
            print(f"   🔥 Max flux found: {max_flux:.1f} W/m²")
            print(f"   📊 Non-zero flux: {nonzero_count}/{len(flux_values)} sampled primitives")
            
        except Exception as e:
            print(f"❌ Radiation model simulation failed: {e}")
            print("   ")
            print("   This Stanford Bunny example requires functional radiation simulation.")
            print("   Cannot proceed without radiation flux data - visualization would be misleading.")
            print("   ")
            print("   Please run this example on a system with:")
            print("   - NVIDIA GPU with CUDA support")
            print("   - Native PyHelios library with radiation plugin enabled")
            return 1
        
        # Apply native Helios pseudocolor mapping to all primitives
        print("\\n🎨 Applying native Helios pseudocolor mapping...")
        all_uuids = context.getAllUUIDs()
        context.colorPrimitiveByDataPseudocolor(
            uuids=all_uuids,
            primitive_data="radiation_flux_SW", 
            colormap="hot", 
            ncolors=256
        )
        print(f"   Applied pseudocolor mapping to {len(all_uuids)} primitives using 'hot' colormap")
        
        # Visualize results using native PyHelios visualizer
        print("\\n🎮 Launching native PyHelios 3D visualizer...")
        visualize_with_native_visualizer(context)
    
    print("Stanford Bunny radiation example completed!")
    return 0


def visualize_with_native_visualizer(context):
    """Visualize the Stanford Bunny using PyHelios native 3D visualizer"""
    
    print("Initializing PyHelios native 3D visualizer...")
    
    # Create visualizer instance with appropriate window size
    with Visualizer(width=1024, height=768) as visualizer:
        print("✓ Visualizer initialized successfully")
        
        # Load geometry from context into visualizer
        print("Building context geometry in visualizer...")
        visualizer.buildContextGeometry(context)
        print("✓ Context geometry loaded")
        
        # Set up camera for good Stanford Bunny view
        print("Setting up optimal camera view...")
        
        # Position camera for Stanford Bunny view (bunny is ~4 units tall)
        camera_position = [6.0, -6.0, 4.0]  # Elevated view
        lookat_point = [0.0, 0.0, 1.5]      # Look at bunny center
        
        visualizer.setCameraPosition(camera_position, lookat_point)
        
        print(f"   Camera position: ({camera_position[0]}, {camera_position[1]}, {camera_position[2]})")
        print(f"   Looking at: ({lookat_point[0]}, {lookat_point[1]}, {lookat_point[2]})")
        
        # Add lighting for better visualization
        print("Setting up lighting...")
        sun_direction = [0.4, -0.4, -0.6]
        light_direction = [-sun_direction[0], -sun_direction[1], -sun_direction[2]]
        visualizer.setLightDirection(light_direction)
        visualizer.setLightingModel("none")
        
        # Set background color to black for better contrast
        visualizer.setBackgroundColor([0.0, 0.0, 0.0])
        
        # Start the interactive visualization
        print("🎮 Starting interactive 3D visualization...")
        print("   Controls:")
        print("   - Mouse: Rotate view (left click + drag)")
        print("   - Mouse wheel: Zoom in/out")
        print("   - Right click + drag: Pan view")
        print("   - The bunny and ground patches show radiation flux via color mapping")
        print("   - Hot colors (red/yellow) = high flux, cool colors (blue/black) = low flux")
        print()
        print("   Starting visualization window... (may take a moment)")
        
        # Start the visualization loop - this will open a window and run until user exits
        visualizer.plotInteractive()  # Blocking call - runs until user closes window
        print("✓ Visualization session completed")


if __name__ == "__main__":
    sys.exit(main())