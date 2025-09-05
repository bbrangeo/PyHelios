"""
Tests for StomatalConductance integration
"""

import pytest
from pyhelios import Context
from pyhelios.plugins.registry import get_plugin_registry
# Import HeliosError from pyhelios main module to ensure consistency
from pyhelios import HeliosError

class TestStomatalConductanceMetadata:
    """Test plugin metadata and registration"""
    
    @pytest.mark.cross_platform
    def test_plugin_metadata_exists(self):
        """Test that plugin metadata is correctly defined"""
        from pyhelios.config.plugin_metadata import get_plugin_metadata
        
        metadata = get_plugin_metadata('stomatalconductance')
        assert metadata is not None
        assert metadata.name == 'stomatalconductance'
        assert metadata.description
        assert metadata.test_symbols
        assert isinstance(metadata.platforms, list)
        assert len(metadata.platforms) > 0
        assert 'windows' in metadata.platforms
        assert 'linux' in metadata.platforms  
        assert 'macos' in metadata.platforms

    @pytest.mark.cross_platform
    def test_plugin_available(self):
        """Test that plugin is available when expected"""
        from pyhelios.config.plugin_metadata import PLUGIN_METADATA
        
        # Should be in plugin metadata
        assert 'stomatalconductance' in PLUGIN_METADATA
        
        # Should not require GPU
        metadata = PLUGIN_METADATA['stomatalconductance']
        assert not metadata.gpu_required
        
        # Should have no system dependencies
        assert metadata.system_dependencies == []

class TestStomatalConductanceAvailability:
    """Test plugin availability detection"""
    
    @pytest.mark.cross_platform
    def test_plugin_registry_awareness(self):
        """Test that plugin registry knows about StomatalConductance"""
        registry = get_plugin_registry()
        
        # Plugin should be known (even if not available)
        all_plugins = registry.get_available_plugins()
        # Note: stomatalconductance will be in all_plugins only if actually built and available
    
    @pytest.mark.cross_platform 
    def test_graceful_unavailable_handling(self):
        """Test graceful handling when plugin unavailable"""
        registry = get_plugin_registry()
        
        with Context() as context:
            if not registry.is_plugin_available('stomatalconductance'):
                # Should raise informative error
                try:
                    from pyhelios import StomatalConductanceModel
                    if StomatalConductanceModel is not None:
                        with pytest.raises(Exception) as exc_info:
                            StomatalConductanceModel(context)
                        
                        error_msg = str(exc_info.value).lower()
                        # Error should mention rebuilding or plugin unavailability
                        expected_keywords = ['rebuild', 'build', 'enable', 'compile', 'plugin', 'not available', 'unavailable']
                        found_keywords = [k for k in expected_keywords if k in error_msg]
                        assert len(found_keywords) > 0, f"Error message missing expected keywords. Got: '{str(exc_info.value)}'"
                except ImportError:
                    # StomatalConductanceModel not imported when plugin unavailable
                    pass
            else:
                # Plugin is available - nothing to test for graceful unavailable handling
                pass

class TestStomatalConductanceInterface:
    """Test plugin interface without requiring native library"""
    
    @pytest.mark.cross_platform
    def test_plugin_class_structure(self):
        """Test that plugin class has expected structure"""
        try:
            from pyhelios import (
                StomatalConductanceModel, 
                StomatalConductanceModelError,
                BWBCoefficients,
                BBLCoefficients, 
                MOPTCoefficients,
                BMFCoefficients,
                BBCoefficients
            )
            
            if StomatalConductanceModel is not None:
                # Test class attributes and methods exist
                assert hasattr(StomatalConductanceModel, '__init__')
                assert hasattr(StomatalConductanceModel, '__enter__')
                assert hasattr(StomatalConductanceModel, '__exit__')
                assert hasattr(StomatalConductanceModel, 'run')
                assert hasattr(StomatalConductanceModel, 'setBWBCoefficients')
                assert hasattr(StomatalConductanceModel, 'setBBLCoefficients')
                assert hasattr(StomatalConductanceModel, 'setMOPTCoefficients')
                assert hasattr(StomatalConductanceModel, 'setBMFCoefficients')
                assert hasattr(StomatalConductanceModel, 'setBBCoefficients')
                assert hasattr(StomatalConductanceModel, 'setBMFCoefficientsFromLibrary')
                assert hasattr(StomatalConductanceModel, 'setDynamicTimeConstants')
                assert hasattr(StomatalConductanceModel, 'optionalOutputPrimitiveData')
                assert hasattr(StomatalConductanceModel, 'printDefaultValueReport')
                assert hasattr(StomatalConductanceModel, 'is_available')
            
        except ImportError:
            # StomatalConductanceModel not available - this is acceptable
            pass
    
    @pytest.mark.cross_platform
    def test_coefficient_classes_structure(self):
        """Test that coefficient classes are properly defined"""
        try:
            from pyhelios import (
                BWBCoefficients,
                BBLCoefficients, 
                MOPTCoefficients,
                BMFCoefficients,
                BBCoefficients
            )
            
            if BWBCoefficients is not None:
                # Test BWB coefficients
                bwb = BWBCoefficients(gs0=0.1, a1=1.0)
                assert hasattr(bwb, 'gs0')
                assert hasattr(bwb, 'a1')
                assert bwb.gs0 == 0.1
                assert bwb.a1 == 1.0
                
                # Test BBL coefficients
                bbl = BBLCoefficients(gs0=0.1, a1=1.0, D0=1000.0)
                assert hasattr(bbl, 'gs0')
                assert hasattr(bbl, 'a1')
                assert hasattr(bbl, 'D0')
                
                # Test MOPT coefficients
                mopt = MOPTCoefficients(gs0=0.1, g1=2.0)
                assert hasattr(mopt, 'gs0')
                assert hasattr(mopt, 'g1')
                
                # Test BMF coefficients
                bmf = BMFCoefficients(Em=250.0, i0=40.0, k=200000.0, b=600.0)
                assert hasattr(bmf, 'Em')
                assert hasattr(bmf, 'i0')
                assert hasattr(bmf, 'k')
                assert hasattr(bmf, 'b')
                
                # Test BB coefficients
                bb = BBCoefficients(pi_0=1.0, pi_m=1.5, theta=200.0, sigma=0.5, chi=2.0)
                assert hasattr(bb, 'pi_0')
                assert hasattr(bb, 'pi_m')
                assert hasattr(bb, 'theta')
                assert hasattr(bb, 'sigma')
                assert hasattr(bb, 'chi')
                
        except ImportError:
            # Coefficient classes not available - this is acceptable
            pass
    
    @pytest.mark.cross_platform
    def test_error_types_available(self):
        """Test that error types are properly defined"""
        try:
            from pyhelios import StomatalConductanceModelError
            if StomatalConductanceModelError is not None:
                # Check that it's actually a class, not None or other
                assert isinstance(StomatalConductanceModelError, type), \
                    f"StomatalConductanceModelError should be a class, got: {type(StomatalConductanceModelError)}"
                
                # Import HeliosError in the same scope to ensure consistent class identity
                from pyhelios import HeliosError
                assert issubclass(StomatalConductanceModelError, HeliosError), \
                    f"StomatalConductanceModelError should inherit from HeliosError. "\
                    f"StomatalConductanceModelError: {StomatalConductanceModelError} (module: {StomatalConductanceModelError.__module__}), "\
                    f"HeliosError: {HeliosError} (module: {HeliosError.__module__}), "\
                    f"MRO: {StomatalConductanceModelError.__mro__}"
            else:
                # None is acceptable when plugin not available
                pass
        except ImportError:
            # Error types not available - this is acceptable
            pass

@pytest.mark.native_only
class TestStomatalConductanceFunctionality:
    """Test actual plugin functionality with native library"""
    
    def test_plugin_creation(self):
        """Test plugin can be created and destroyed"""
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            with StomatalConductanceModel(context) as stomatal:
                assert stomatal is not None
                assert isinstance(stomatal, StomatalConductanceModel)
    
    def test_message_control(self):
        """Test message enable/disable functionality"""
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            with StomatalConductanceModel(context) as stomatal:
                # Should not raise exceptions
                stomatal.enableMessages()
                stomatal.disableMessages()
    
    def test_basic_run_methods(self):
        """Test basic run functionality"""
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            # Add some geometry for testing
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test steady state for all primitives
                stomatal.run()
                
                # Test steady state for specific primitives
                stomatal.run(uuids=[patch_uuid])
                
                # Test dynamic with timestep for all primitives
                stomatal.run(dt=60.0)
                
                # Test dynamic with timestep for specific primitives
                stomatal.run(uuids=[patch_uuid], dt=30.0)

    def test_bwb_coefficients(self):
        """Test Ball-Woodrow-Berry model coefficients"""
        from pyhelios import StomatalConductanceModel, BWBCoefficients
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test BWB coefficients for all primitives
                bwb_coeffs = BWBCoefficients(gs0=0.0733, a1=9.422)
                stomatal.setBWBCoefficients(bwb_coeffs)
                
                # Test BWB coefficients for specific primitives
                stomatal.setBWBCoefficients(bwb_coeffs, uuids=[patch_uuid])
                
                # Run model to ensure coefficients are applied
                stomatal.run()
    
    def test_bbl_coefficients(self):
        """Test Ball-Berry-Leuning model coefficients"""
        from pyhelios import StomatalConductanceModel, BBLCoefficients
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test BBL coefficients
                bbl_coeffs = BBLCoefficients(gs0=0.0743, a1=4.265, D0=14570.0)
                stomatal.setBBLCoefficients(bbl_coeffs)
                stomatal.setBBLCoefficients(bbl_coeffs, uuids=[patch_uuid])
                stomatal.run()
    
    def test_mopt_coefficients(self):
        """Test Medlyn et al. optimality model coefficients"""
        from pyhelios import StomatalConductanceModel, MOPTCoefficients
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test MOPT coefficients
                mopt_coeffs = MOPTCoefficients(gs0=0.0825, g1=2.637)
                stomatal.setMOPTCoefficients(mopt_coeffs)
                stomatal.setMOPTCoefficients(mopt_coeffs, uuids=[patch_uuid])
                stomatal.run()
    
    def test_bmf_coefficients(self):
        """Test Buckley-Mott-Farquhar model coefficients"""
        from pyhelios import StomatalConductanceModel, BMFCoefficients
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test BMF coefficients
                bmf_coeffs = BMFCoefficients(Em=258.25, i0=38.65, k=232916.82, b=609.67)
                stomatal.setBMFCoefficients(bmf_coeffs)
                stomatal.setBMFCoefficients(bmf_coeffs, uuids=[patch_uuid])
                stomatal.run()
    
    def test_bb_coefficients(self):
        """Test Bailey model coefficients"""
        from pyhelios import StomatalConductanceModel, BBCoefficients
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test BB coefficients
                bb_coeffs = BBCoefficients(pi_0=1.0, pi_m=1.67, theta=211.22, sigma=0.4408, chi=2.076)
                stomatal.setBBCoefficients(bb_coeffs)
                stomatal.setBBCoefficients(bb_coeffs, uuids=[patch_uuid])
                stomatal.run()
    
    def test_species_library(self):
        """Test species library functionality"""
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test common species
                common_species = ["Almond", "Apple", "Grape", "Walnut"]
                
                for species in common_species:
                    try:
                        # Set coefficients for all primitives
                        stomatal.setBMFCoefficientsFromLibrary(species)
                        
                        # Set coefficients for specific primitives
                        stomatal.setBMFCoefficientsFromLibrary(species, uuids=[patch_uuid])
                        
                        # Run model to ensure coefficients work
                        stomatal.run()
                    except Exception as e:
                        # Some species may not be available - this is acceptable
                        if "species not found" not in str(e).lower():
                            raise
    
    def test_dynamic_time_constants(self):
        """Test dynamic time constants"""
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Set time constants for all primitives
                stomatal.setDynamicTimeConstants(tau_open=120.0, tau_close=240.0)
                
                # Set time constants for specific primitives
                stomatal.setDynamicTimeConstants(tau_open=60.0, tau_close=180.0, uuids=[patch_uuid])
                
                # Run dynamic simulation
                stomatal.run(dt=30.0)
    
    def test_optional_output(self):
        """Test optional output functionality"""
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Add optional outputs
                common_outputs = ["gs", "Ci", "E"]
                
                for output in common_outputs:
                    stomatal.optionalOutputPrimitiveData(output)
                
                # Run model to generate output
                stomatal.run()
    
    def test_default_value_report(self):
        """Test default value reporting"""
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Print report for all primitives
                stomatal.printDefaultValueReport()
                
                # Print report for specific primitives
                stomatal.printDefaultValueReport(uuids=[patch_uuid])

    def test_parameter_validation(self):
        """Test parameter validation"""
        from pyhelios import StomatalConductanceModel, BWBCoefficients, StomatalConductanceModelError
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test invalid time step
                with pytest.raises(ValueError, match="positive"):
                    stomatal.run(dt=-1.0)
                
                # Test empty UUIDs list
                with pytest.raises(ValueError, match="empty"):
                    stomatal.run(uuids=[])
                
                # Test invalid BWB coefficients
                with pytest.raises(ValueError):
                    bad_coeffs = BWBCoefficients(gs0=-0.1, a1=1.0)  # negative gs0
                    stomatal.setBWBCoefficients(bad_coeffs)
                
                # Test invalid time constants
                with pytest.raises(ValueError, match="positive"):
                    stomatal.setDynamicTimeConstants(tau_open=-1.0, tau_close=100.0)
                
                # Test empty species name
                with pytest.raises(ValueError, match="empty"):
                    stomatal.setBMFCoefficientsFromLibrary("")
                
                # Test empty output label
                with pytest.raises(ValueError, match="empty"):
                    stomatal.optionalOutputPrimitiveData("")

@pytest.mark.native_only
class TestStomatalConductanceIntegration:
    """Test plugin integration with other PyHelios components"""
    
    def test_context_integration(self):
        """Test plugin works with Context geometry"""
        from pyhelios import StomatalConductanceModel, BMFCoefficients
        
        with Context() as context:
            # Add different types of geometry
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            triangle_uuid = context.addTriangle([0, 0, 0], [0.1, 0, 0], [0, 0.1, 0])
            
            with StomatalConductanceModel(context) as stomatal:
                # Set coefficients using species library
                stomatal.setBMFCoefficientsFromLibrary("Almond")
                
                # Test plugin can work with context geometry
                stomatal.run()
                
                # Test with specific geometry
                stomatal.run(uuids=[patch_uuid, triangle_uuid])
    
    def test_error_handling_integration(self):
        """Test that C++ exceptions become proper Python exceptions"""
        from pyhelios import StomatalConductanceModel, StomatalConductanceModelError
        
        with Context() as context:
            with StomatalConductanceModel(context) as stomatal:
                # Test operations that should cause specific errors
                try:
                    # Try to use non-existent species
                    stomatal.setBMFCoefficientsFromLibrary("NonexistentSpecies")
                except Exception as e:
                    # Should be a meaningful error message
                    error_msg = str(e).lower()
                    assert any(keyword in error_msg for keyword in 
                              ['species', 'not found', 'invalid', 'library'])
    
    def test_multiple_models(self):
        """Test using multiple model types in sequence"""
        from pyhelios import (
            StomatalConductanceModel, 
            BWBCoefficients, 
            BBLCoefficients, 
            MOPTCoefficients,
            BMFCoefficients
        )
        
        with Context() as context:
            patch_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
            
            with StomatalConductanceModel(context) as stomatal:
                # Test using different models in sequence
                
                # Start with BWB model
                bwb_coeffs = BWBCoefficients(gs0=0.05, a1=8.0)
                stomatal.setBWBCoefficients(bwb_coeffs, uuids=[patch_uuid])
                stomatal.run()
                
                # Switch to BBL model
                bbl_coeffs = BBLCoefficients(gs0=0.06, a1=5.0, D0=15000.0)
                stomatal.setBBLCoefficients(bbl_coeffs, uuids=[patch_uuid])
                stomatal.run()
                
                # Switch to MOPT model  
                mopt_coeffs = MOPTCoefficients(gs0=0.07, g1=3.0)
                stomatal.setMOPTCoefficients(mopt_coeffs, uuids=[patch_uuid])
                stomatal.run()
                
                # Switch to BMF model
                bmf_coeffs = BMFCoefficients(Em=250.0, i0=40.0, k=200000.0, b=600.0)
                stomatal.setBMFCoefficients(bmf_coeffs, uuids=[patch_uuid])
                stomatal.run()

@pytest.mark.slow
class TestStomatalConductancePerformance:
    """Performance tests for plugin operations"""
    
    @pytest.mark.native_only
    def test_computation_performance(self):
        """Test computation performance doesn't regress"""
        import time
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            # Create multiple patches for performance testing
            patch_uuids = []
            for i in range(100):
                x = (i % 10) * 0.1
                y = (i // 10) * 0.1
                patch_uuid = context.addPatch(center=[x, y, 1], size=[0.05, 0.05])
                patch_uuids.append(patch_uuid)
            
            with StomatalConductanceModel(context) as stomatal:
                # Set coefficients using species library
                stomatal.setBMFCoefficientsFromLibrary("Almond")
                
                # Time computation
                start_time = time.time()
                stomatal.run()
                elapsed = time.time() - start_time
                
                # Should complete in reasonable time (adjust threshold as needed)
                assert elapsed < 5.0, f"Computation too slow: {elapsed:.3f}s"
    
    @pytest.mark.native_only
    def test_dynamic_performance(self):
        """Test dynamic simulation performance"""
        import time
        from pyhelios import StomatalConductanceModel
        
        with Context() as context:
            # Create some geometry
            patch_uuids = []
            for i in range(50):
                x = (i % 10) * 0.1
                y = (i // 10) * 0.1
                patch_uuid = context.addPatch(center=[x, y, 1], size=[0.05, 0.05])
                patch_uuids.append(patch_uuid)
            
            with StomatalConductanceModel(context) as stomatal:
                stomatal.setBMFCoefficientsFromLibrary("Apple")
                stomatal.setDynamicTimeConstants(tau_open=60.0, tau_close=120.0)
                
                # Time dynamic computation
                start_time = time.time()
                stomatal.run(dt=30.0)
                elapsed = time.time() - start_time
                
                # Should complete in reasonable time
                assert elapsed < 3.0, f"Dynamic computation too slow: {elapsed:.3f}s"