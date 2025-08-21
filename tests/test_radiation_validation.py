#!/usr/bin/env python3
"""
Radiation validation tests - exact replicas of C++ selfTest.cpp cases
These tests validate that PyHelios radiation results match Helios C++ expected values
"""

import pytest
import numpy as np
from pyhelios import Context, RadiationModel, DataTypes


@pytest.mark.native_only
class TestRadiationValidation:
    """Tests that replicate exact C++ test cases to validate PyHelios radiation accuracy"""

    def test_90_degree_common_edge_patches(self):
        """
        Replicates: DOCTEST_TEST_CASE("RadiationModel 90 Degree Common-Edge Squares")
        from helios-core/plugins/radiation/tests/selfTest.cpp lines 13-96
        
        Tests two perpendicular patches at 90 degrees to validate:
        - Patch geometry handling
        - Shortwave radiation (collimated source)
        - Longwave radiation (thermal emission) 
        - Reflectance properties
        """
        error_threshold = 0.005
        Nensemble = 500
        
        Ndiffuse_1 = 100000
        Ndirect_1 = 5000
        
        Qs = 1000.0
        sigma = 5.6703744e-8
        
        # Expected values from C++ test
        shortwave_exact_0 = 0.7 * Qs        # 700.0 W/m² 
        shortwave_exact_1 = 0.3 * 0.2 * Qs  # 60.0 W/m²
        longwave_exact_0 = 0.0
        longwave_exact_1 = sigma * (300.0 ** 4) * 0.2  # ~91.9 W/m² (corrected)
        
        print(f"\\nExpected results:")
        print(f"  Shortwave patch 0: {shortwave_exact_0:.1f} W/m²")
        print(f"  Shortwave patch 1: {shortwave_exact_1:.1f} W/m²") 
        print(f"  Longwave patch 0: {longwave_exact_0:.1f} W/m²")
        print(f"  Longwave patch 1: {longwave_exact_1:.1f} W/m²")
        
        # Use context manager like Stanford Bunny example for proper resource management
        with Context() as context:
            # STEP 1: Add geometry FIRST (proper order)
            # Patch 0: Horizontal patch at z=0 (1x1 square from -0.5 to 0.5 in x,y)
            UUID0 = context.addPatch(center=DataTypes.vec3(0, 0, 0), size=DataTypes.vec2(1, 1))
            
            # Patch 1: FIXED SphericalCoord bug - C++ interface now uses rotation[1] and rotation[3]
            # C++ uses: make_SphericalCoord(0.5 * M_PI, -0.5 * M_PI) = (elevation, azimuth)
            print(f"\\nUsing FIXED SphericalCoord with correct elevation[1] and azimuth[3]...")
            UUID1 = context.addPatch(center=DataTypes.vec3(0.5, 0, 0.5), size=DataTypes.vec2(1, 1),
                                    rotation=DataTypes.SphericalCoord(1.0, 0.5 * np.pi, -0.5 * np.pi))
        
            # STEP 2: Set properties using EXPLICIT DATA TYPES
            ts_flag = 0
            # CRITICAL: Use setPrimitiveDataUInt for twosided_flag (must be uint in C++)
            context.setPrimitiveDataUInt(UUID0, "twosided_flag", ts_flag)
            context.setPrimitiveDataUInt(UUID1, "twosided_flag", ts_flag)
            
            # Use explicit float data types
            context.setPrimitiveDataFloat(UUID0, "temperature", 300.0)
            context.setPrimitiveDataFloat(UUID1, "temperature", 0.0)
            
            shortwave_rho = 0.3
            context.setPrimitiveDataFloat(UUID0, "reflectivity_SW", shortwave_rho)
            
            # Try setting emissivity for longwave (default might be 0)
            context.setPrimitiveDataFloat(UUID0, "emissivity_LW", 1.0)  # Perfect emitter
            context.setPrimitiveDataFloat(UUID1, "emissivity_LW", 1.0)  # Perfect absorber
            
            # STEP 3: Create RadiationModel AFTER geometry exists (proper order)
            radiationmodel = RadiationModel(context)
        
            # Longwave band
            radiationmodel.addRadiationBand("LW")
            radiationmodel.setDirectRayCount("LW", Ndiffuse_1)
            radiationmodel.setDiffuseRayCount("LW", Ndiffuse_1)
            radiationmodel.setScatteringDepth("LW", 0)
            
            # Shortwave band
            SunSource = radiationmodel.addCollimatedRadiationSource(DataTypes.vec3(0, 0, 1))
            radiationmodel.addRadiationBand("SW")
            radiationmodel.disableEmission("SW")
            radiationmodel.setDirectRayCount("SW", Ndirect_1)
            radiationmodel.setDiffuseRayCount("SW", Ndirect_1)
            radiationmodel.setScatteringDepth("SW", 1)
            radiationmodel.setSourceFlux(SunSource, "SW", Qs)
            
            radiationmodel.updateGeometry()
            
            # Run ensemble simulation exactly as in C++
            longwave_model_0 = 0.0
            longwave_model_1 = 0.0
            shortwave_model_0 = 0.0
            shortwave_model_1 = 0.0
            
            print(f"\\nRunning {Nensemble} ensemble simulations...")
            for r in range(Nensemble):
                # C++ line 70: radiationmodel_1.runBand(bands) where bands = {"LW", "SW"}
                radiationmodel.runBand(["LW", "SW"])
                
                # Collect results using UUIDs
                R = context.getPrimitiveData(UUID0, "radiation_flux_LW")
                longwave_model_0 += R / float(Nensemble)
                
                R = context.getPrimitiveData(UUID1, "radiation_flux_LW")
                longwave_model_1 += R / float(Nensemble)
                
                R = context.getPrimitiveData(UUID0, "radiation_flux_SW")
                shortwave_model_0 += R / float(Nensemble)
                
                R = context.getPrimitiveData(UUID1, "radiation_flux_SW")
                shortwave_model_1 += R / float(Nensemble)
                
                # Debug: Print first iteration values
                if r == 0:
                    print(f"\\nPatch geometry verification:")
                    vertices0 = context.getPrimitiveVertices(UUID0)
                    vertices1 = context.getPrimitiveVertices(UUID1)
                    print(f"  UUID0 vertices: {' '.join(str(v) for v in vertices0)}")
                    print(f"  UUID1 vertices: {' '.join(str(v) for v in vertices1)}")
                    
                    print(f"\\nFirst iteration flux values:")
                    print(f"  UUID0 LW: {context.getPrimitiveData(UUID0, 'radiation_flux_LW'):.2f}")
                    print(f"  UUID1 LW: {context.getPrimitiveData(UUID1, 'radiation_flux_LW'):.2f}")
                    print(f"  UUID0 SW: {context.getPrimitiveData(UUID0, 'radiation_flux_SW'):.2f}")
                    print(f"  UUID1 SW: {context.getPrimitiveData(UUID1, 'radiation_flux_SW'):.2f}")
            
            print(f"\\nPyHelios results:")
            print(f"  Shortwave patch 0: {shortwave_model_0:.1f} W/m²")
            print(f"  Shortwave patch 1: {shortwave_model_1:.1f} W/m²")
            print(f"  Longwave patch 0: {longwave_model_0:.1f} W/m²")
            print(f"  Longwave patch 1: {longwave_model_1:.1f} W/m²")
            
            # Calculate errors exactly as in C++
            shortwave_error_0 = abs(shortwave_model_0 - shortwave_exact_0) / abs(shortwave_exact_0)
            shortwave_error_1 = abs(shortwave_model_1 - shortwave_exact_1) / abs(shortwave_exact_1) 
            longwave_error_1 = abs(longwave_model_1 - longwave_exact_1) / abs(longwave_exact_1)
            
            print(f"\\nErrors (threshold = {error_threshold}):")
            print(f"  Shortwave patch 0 error: {shortwave_error_0:.4f}")
            print(f"  Shortwave patch 1 error: {shortwave_error_1:.4f}")
            print(f"  Longwave patch 0: {longwave_model_0:.1f} (exact: {longwave_exact_0:.1f})")
            print(f"  Longwave patch 1 error: {longwave_error_1:.4f}")
            
            # Assertions exactly as in C++
            assert shortwave_error_0 <= error_threshold, f"Shortwave patch 0 error {shortwave_error_0:.4f} > {error_threshold}"
            assert shortwave_error_1 <= error_threshold, f"Shortwave patch 1 error {shortwave_error_1:.4f} > {error_threshold}"
            assert longwave_model_0 == longwave_exact_0, f"Longwave patch 0: {longwave_model_0} != {longwave_exact_0}"
            assert longwave_error_1 <= error_threshold, f"Longwave patch 1 error {longwave_error_1:.4f} > {error_threshold}"

    def test_90_degree_common_edge_triangles(self):
        """
        Replicates: DOCTEST_TEST_CASE("RadiationModel 90 Degree Common-Edge Sub-Triangles")  
        from helios-core/plugins/radiation/tests/selfTest.cpp lines 287-386
        
        Tests four triangles forming two perpendicular squares to validate:
        - Triangle geometry handling (this is key for Stanford Bunny issue!)
        - Same physics as patches but with triangular primitives
        """
        # Check if triangle functions are available
        from pyhelios.wrappers.UContextWrapper import _TRIANGLE_FUNCTIONS_AVAILABLE
        if not _TRIANGLE_FUNCTIONS_AVAILABLE:
            pytest.skip("Triangle functions not available in current Helios library")
            
        error_threshold = 0.005
        Nensemble = 500
        sigma = 5.6703744e-8
        
        Qs = 1000.0
        
        Ndiffuse_5 = 100000
        Ndirect_5 = 5000
        
        # Expected values from C++ (same as patch test since same geometry)
        shortwave_exact_0 = 0.7 * Qs        # 700.0 W/m²
        shortwave_exact_1 = 0.3 * 0.2 * Qs  # 60.0 W/m²
        longwave_exact_0 = 0.0
        longwave_exact_1 = sigma * (300.0 ** 4) * 0.2  # ~91.9 W/m²
        
        print(f"\\nExpected results (triangles):")
        print(f"  Shortwave square 0: {shortwave_exact_0:.1f} W/m²")
        print(f"  Shortwave square 1: {shortwave_exact_1:.1f} W/m²")
        print(f"  Longwave square 0: {longwave_exact_0:.1f} W/m²")
        print(f"  Longwave square 1: {longwave_exact_1:.1f} W/m²")
        
        with Context() as context:
            # Create four triangles exactly as in C++ selfTest.cpp lines 304-308
            print("\\nCreating triangle geometry exactly as in C++ test...")
            
            # First square (horizontal, z=0): two triangles
            triangle_0 = context.addTriangle(
                DataTypes.vec3(-0.5, -0.5, 0),
                DataTypes.vec3(0.5, -0.5, 0),
                DataTypes.vec3(0.5, 0.5, 0)
            )
            triangle_1 = context.addTriangle(
                DataTypes.vec3(-0.5, -0.5, 0),
                DataTypes.vec3(0.5, 0.5, 0),
                DataTypes.vec3(-0.5, 0.5, 0)
            )
            
            # Second square (vertical, x=0.5): two triangles  
            triangle_2 = context.addTriangle(
                DataTypes.vec3(0.5, 0.5, 0),
                DataTypes.vec3(0.5, -0.5, 0),
                DataTypes.vec3(0.5, -0.5, 1)
            )
            triangle_3 = context.addTriangle(
                DataTypes.vec3(0.5, 0.5, 0),
                DataTypes.vec3(0.5, -0.5, 1),
                DataTypes.vec3(0.5, 0.5, 1)
            )
            
            print(f"Created 4 triangles: {[triangle_0, triangle_1, triangle_2, triangle_3]}")
            
            # Set primitive properties exactly as in C++ lines 310-323
            context.setPrimitiveDataFloat(triangle_0, "temperature", 300.0)
            context.setPrimitiveDataFloat(triangle_1, "temperature", 300.0)
            context.setPrimitiveDataFloat(triangle_2, "temperature", 0.0)
            context.setPrimitiveDataFloat(triangle_3, "temperature", 0.0)
            
            shortwave_rho = 0.3
            context.setPrimitiveDataFloat(triangle_0, "reflectivity_SW", shortwave_rho)
            context.setPrimitiveDataFloat(triangle_1, "reflectivity_SW", shortwave_rho)
            
            # CRITICAL: Use setPrimitiveDataUInt for twosided_flag (must be uint in C++)
            flag = 0
            context.setPrimitiveDataUInt(triangle_0, "twosided_flag", flag)
            context.setPrimitiveDataUInt(triangle_1, "twosided_flag", flag)
            context.setPrimitiveDataUInt(triangle_2, "twosided_flag", flag)
            context.setPrimitiveDataUInt(triangle_3, "twosided_flag", flag)
            
            # Set up radiation model exactly as in C++ lines 325-343
            radiationmodel = RadiationModel(context)
            
            # Longwave band
            radiationmodel.addRadiationBand("LW")
            radiationmodel.setDirectRayCount("LW", Ndiffuse_5)
            radiationmodel.setDiffuseRayCount("LW", Ndiffuse_5)
            radiationmodel.setScatteringDepth("LW", 0)
            
            # Shortwave band
            SunSource = radiationmodel.addCollimatedRadiationSource(DataTypes.vec3(0, 0, 1))
            radiationmodel.addRadiationBand("SW")
            radiationmodel.disableEmission("SW")
            radiationmodel.setDirectRayCount("SW", Ndirect_5)
            radiationmodel.setDiffuseRayCount("SW", Ndirect_5)
            radiationmodel.setScatteringDepth("SW", 1)
            radiationmodel.setSourceFlux(SunSource, "SW", Qs)
            
            radiationmodel.updateGeometry()
            
            # Run ensemble simulation exactly as in C++ lines 351-376
            longwave_model_0 = 0.0
            longwave_model_1 = 0.0
            shortwave_model_0 = 0.0
            shortwave_model_1 = 0.0
            
            print(f"\\nRunning {Nensemble} ensemble simulations...")
            for i in range(Nensemble):
                # C++ line 353: radiationmodel_5.runBand(bands) where bands = {"SW", "LW"}
                radiationmodel.runBand(["SW", "LW"])
                
                # Collect results exactly as in C++ - average pairs of triangles
                # patch 0 emission (triangles 0,1)
                R = context.getPrimitiveData(triangle_0, "radiation_flux_LW")
                longwave_model_0 += 0.5 * R / float(Nensemble)
                R = context.getPrimitiveData(triangle_1, "radiation_flux_LW")
                longwave_model_0 += 0.5 * R / float(Nensemble)
                
                # patch 1 emission (triangles 2,3)
                R = context.getPrimitiveData(triangle_2, "radiation_flux_LW")
                longwave_model_1 += 0.5 * R / float(Nensemble)
                R = context.getPrimitiveData(triangle_3, "radiation_flux_LW")
                longwave_model_1 += 0.5 * R / float(Nensemble)
                
                # patch 0 shortwave (triangles 0,1)
                R = context.getPrimitiveData(triangle_0, "radiation_flux_SW")
                shortwave_model_0 += 0.5 * R / float(Nensemble)
                R = context.getPrimitiveData(triangle_1, "radiation_flux_SW")
                shortwave_model_0 += 0.5 * R / float(Nensemble)
                
                # patch 1 shortwave (triangles 2,3)
                R = context.getPrimitiveData(triangle_2, "radiation_flux_SW")
                shortwave_model_1 += 0.5 * R / float(Nensemble)
                R = context.getPrimitiveData(triangle_3, "radiation_flux_SW")
                shortwave_model_1 += 0.5 * R / float(Nensemble)
                
                # Debug: Print first iteration values
                if i == 0:
                    print(f"\\nFirst iteration triangle flux values:")
                    print(f"  Triangle 0 SW: {context.getPrimitiveData(triangle_0, 'radiation_flux_SW'):.2f}")
                    print(f"  Triangle 1 SW: {context.getPrimitiveData(triangle_1, 'radiation_flux_SW'):.2f}")
                    print(f"  Triangle 2 SW: {context.getPrimitiveData(triangle_2, 'radiation_flux_SW'):.2f}")
                    print(f"  Triangle 3 SW: {context.getPrimitiveData(triangle_3, 'radiation_flux_SW'):.2f}")
                    print(f"  Triangle 0 LW: {context.getPrimitiveData(triangle_0, 'radiation_flux_LW'):.2f}")
                    print(f"  Triangle 1 LW: {context.getPrimitiveData(triangle_1, 'radiation_flux_LW'):.2f}")
                    print(f"  Triangle 2 LW: {context.getPrimitiveData(triangle_2, 'radiation_flux_LW'):.2f}")
                    print(f"  Triangle 3 LW: {context.getPrimitiveData(triangle_3, 'radiation_flux_LW'):.2f}")
            
            print(f"\\nPyHelios triangle results:")
            print(f"  Shortwave square 0: {shortwave_model_0:.1f} W/m²")
            print(f"  Shortwave square 1: {shortwave_model_1:.1f} W/m²")
            print(f"  Longwave square 0: {longwave_model_0:.1f} W/m²")
            print(f"  Longwave square 1: {longwave_model_1:.1f} W/m²")
            
            # Calculate errors exactly as in C++ lines 378-380
            shortwave_error_0 = abs(shortwave_model_0 - shortwave_exact_0) / abs(shortwave_exact_0)
            shortwave_error_1 = abs(shortwave_model_1 - shortwave_exact_1) / abs(shortwave_exact_1)
            longwave_error_1 = abs(longwave_model_1 - longwave_exact_1) / abs(longwave_exact_1)
            
            print(f"\\nTriangle errors (threshold = {error_threshold}):")
            print(f"  Shortwave square 0 error: {shortwave_error_0:.4f}")
            print(f"  Shortwave square 1 error: {shortwave_error_1:.4f}")
            print(f"  Longwave square 0: {longwave_model_0:.1f} (exact: {longwave_exact_0:.1f})")
            print(f"  Longwave square 1 error: {longwave_error_1:.4f}")
            
            # Assertions exactly as in C++ lines 382-386
            assert shortwave_error_0 <= error_threshold, f"Triangle shortwave square 0 error {shortwave_error_0:.4f} > {error_threshold}"
            assert shortwave_error_1 <= error_threshold, f"Triangle shortwave square 1 error {shortwave_error_1:.4f} > {error_threshold}"
            assert longwave_model_0 == longwave_exact_0, f"Triangle longwave square 0: {longwave_model_0} != {longwave_exact_0}"
            assert longwave_error_1 <= error_threshold, f"Triangle longwave square 1 error {longwave_error_1:.4f} > {error_threshold}"
            
            print("✓ Triangle validation passed!")


if __name__ == "__main__":
    # Allow running tests directly without pytest
    import sys
    import os
    
    # Add the PyHelios project root to the Python path
    project_root = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, project_root)
    
    test_instance = TestRadiationValidation()
    
    try:
        print("Running patch radiation validation test...")
        test_instance.test_90_degree_common_edge_patches()
        print("✓ Patch test passed!")
        
        print("\nRunning triangle radiation validation test...")
        test_instance.test_90_degree_common_edge_triangles()
        print("✓ Triangle test passed!")
        
        print("\n✓ All radiation validation tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)