#!/usr/bin/env python3
"""
Simple PyHelios Radiation Model Test (Works in Mock Mode)

This example demonstrates the RadiationModel API without requiring 
native libraries or PLY file loading.
"""

import sys
import os

# Add pyhelios to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pyhelios import Context, RadiationModel
from pyhelios.types import *


def main():
    """Test RadiationModel functionality in mock mode"""
    print("PyHelios RadiationModel API Test (Mock Mode Compatible)")
    print("=" * 60)
    
    try:
        with Context() as context:
            print("✓ Context created successfully")
            
            # Create simple geometry instead of loading PLY
            print("Creating simple test geometry...")
            patches = []
            for i in range(5):
                for j in range(5):
                    center = vec3(i - 2, j - 2, 0)
                    size = vec2(0.5, 0.5)
                    color = RGBcolor(0.8, 0.8, 0.8)
                    
                    patch_uuid = context.addPatch(center=center, size=size, color=color)
                    patches.append(patch_uuid)
                    
                    # Set primitive data for radiation simulation
                    context.setPrimitiveData(patch_uuid, "reflectivity_SW", 0.3)
                    context.setPrimitiveData(patch_uuid, "radiation_flux_SW", 500.0)
            
            print(f"✓ Created {len(patches)} ground patches")
            
            # Test RadiationModel API
            with RadiationModel(context) as radiation_model:
                print("✓ RadiationModel created successfully")
                
                # Add radiation band
                radiation_model.addRadiationBand("SW")
                print("✓ Added SW radiation band")
                
                # Configure radiation model
                radiation_model.disableEmission("SW")
                radiation_model.setDirectRayCount("SW", 100)
                radiation_model.setDiffuseRayCount("SW", 300)
                print("✓ Configured ray counts and emission")
                
                # Add radiation source
                sun_direction = vec3(0.4, -0.4, 0.6)
                sun_source = radiation_model.addCollimatedRadiationSource(sun_direction)
                print(f"✓ Added collimated sun source (ID: {sun_source})")
                
                # Set fluxes
                radiation_model.setSourceFlux(sun_source, "SW", 800.0)
                radiation_model.setDiffuseRadiationFlux("SW", 200.0)
                radiation_model.setScatteringDepth("SW", 3)
                print("✓ Configured radiation fluxes and scattering")
                
                # Update geometry and run simulation
                radiation_model.updateGeometry()
                print("✓ Updated geometry in radiation model")
                
                radiation_model.runBand("SW")
                print("✓ Radiation simulation completed")
                
                # Get results
                source_count = radiation_model.getRadiationSourceCount()
                band_count = radiation_model.getBandCount()
                absorbed_flux = radiation_model.getTotalAbsorbedFlux()
                
                print(f"✓ Results: {source_count} sources, {band_count} bands")
                print(f"✓ Absorbed flux data: {len(absorbed_flux)} values")
                
                # Test pseudocolor functionality
                try:
                    context.colorPrimitiveByDataPseudocolor(
                        patches[:10], "radiation_flux_SW", "hot", 10)
                    print("✓ Pseudocolor mapping applied successfully")
                except NotImplementedError as e:
                    print(f"ⓘ Pseudocolor not available: {e}")
                
        print("\n" + "=" * 60)
        print("SUCCESS: All RadiationModel API functions work correctly!")
        print("Note: In mock mode, actual radiation calculations are simulated.")
        print("Build native libraries for full functionality.")
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())