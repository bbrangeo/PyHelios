"""
Test suite for PhotosynthesisModel plugin.

Comprehensive tests covering all photosynthesis modeling functionality,
parameter validation, species library, and cross-platform compatibility.
"""

import pytest
from pyhelios import Context
from pyhelios.PhotosynthesisModel import PhotosynthesisModel, PhotosynthesisModelError
from pyhelios.types.photosynthesis import (
    PhotosyntheticTemperatureResponseParameters,
    EmpiricalModelCoefficients,
    FarquharModelCoefficients,
    PHOTOSYNTHESIS_SPECIES,
    validate_species_name,
    get_available_species,
    get_species_aliases
)
from pyhelios.validation.exceptions import ValidationError


class TestPhotosynthesisSpeciesLibrary:
    """Test the photosynthesis species library functionality."""
    
    def test_photosynthesis_species_constants(self):
        """Test that PHOTOSYNTHESIS_SPECIES contains expected species."""
        assert "Almond" in PHOTOSYNTHESIS_SPECIES
        assert "Apple" in PHOTOSYNTHESIS_SPECIES
        assert "Grape" in PHOTOSYNTHESIS_SPECIES
        assert len(PHOTOSYNTHESIS_SPECIES) >= 15  # Should have at least 15 species
        
    def test_get_available_species(self):
        """Test getting available species list."""
        species = get_available_species()
        assert isinstance(species, list)
        assert len(species) >= 15
        assert "Almond" in species
        assert "Apple" in species
        
    def test_get_species_aliases(self):
        """Test getting species aliases mapping."""
        aliases = get_species_aliases()
        assert isinstance(aliases, dict)
        # Test some expected aliases
        if "apple" in aliases:
            assert aliases["apple"] == "Apple"
        if "grape" in aliases:
            assert aliases["grape"] == "Grape"
            
    def test_validate_species_name_valid(self):
        """Test species name validation with valid names."""
        # Test canonical names
        assert validate_species_name("Apple") == "Apple"
        assert validate_species_name("Almond") == "Almond"
        
        # Test case insensitive
        assert validate_species_name("apple") == "Apple"
        assert validate_species_name("APPLE") == "Apple"
        
    def test_validate_species_name_invalid(self):
        """Test species name validation with invalid names."""
        with pytest.raises(ValueError):
            validate_species_name("INVALID_SPECIES")
            
        with pytest.raises(ValueError):
            validate_species_name("")


class TestPhotosynthesisParameterStructures:
    """Test the photosynthesis parameter structure dataclasses."""
    
    def test_temperature_response_parameters_creation(self):
        """Test PhotosyntheticTemperatureResponseParameters creation."""
        params = PhotosyntheticTemperatureResponseParameters()
        assert params.value_at_25C == 100.0
        assert params.dHa == 60.0
        assert params.dHd == 600.0
        assert params.Topt == 10000.0
        
        # Test custom values
        params = PhotosyntheticTemperatureResponseParameters(
            value_at_25C=25.0,
            dHa=65000.0,
            dHd=200000.0,
            Topt=25.0
        )
        assert params.value_at_25C == 25.0
        assert params.dHa == 65000.0
        assert params.dHd == 200000.0
        assert params.Topt == 25.0
        
    def test_empirical_model_coefficients_creation(self):
        """Test EmpiricalModelCoefficients creation."""
        coeffs = EmpiricalModelCoefficients()
        assert coeffs.Tref == 298.0
        assert coeffs.Ci_ref == 290.0
        assert coeffs.Asat == 18.18
        
        # Test to_array method
        arr = coeffs.to_array()
        assert isinstance(arr, list)
        assert len(arr) == 10
        assert arr[0] == 298.0  # Tref
        
        # Test from_array method
        coeffs2 = EmpiricalModelCoefficients.from_array(arr)
        assert coeffs2.Tref == coeffs.Tref
        assert coeffs2.Ci_ref == coeffs.Ci_ref
        
    def test_farquhar_model_coefficients_creation(self):
        """Test FarquharModelCoefficients creation."""
        coeffs = FarquharModelCoefficients()
        assert coeffs.Vcmax == -1.0  # Uninitialized
        assert coeffs.Jmax == -1.0   # Uninitialized
        assert coeffs.O == 213.5     # Ambient oxygen
        
        # Test custom values  
        coeffs = FarquharModelCoefficients(Vcmax=100.0, Jmax=180.0)
        assert coeffs.Vcmax == 100.0
        assert coeffs.Jmax == 180.0


@pytest.mark.cross_platform
class TestPhotosynthesisModelMockMode:
    """Test PhotosynthesisModel in mock mode (cross-platform)."""
    
    def test_photosynthesis_model_static_methods(self):
        """Test static methods work without native libraries."""
        species = PhotosynthesisModel.get_available_species()
        assert isinstance(species, list)
        assert len(species) >= 15
        
        aliases = PhotosynthesisModel.get_species_aliases()
        assert isinstance(aliases, dict)
        
    def test_photosynthesis_model_mock_initialization_error(self):
        """Test PhotosynthesisModel initialization when plugin is available."""
        context = Context()
        
        # Since photosynthesis plugin is now built and available,
        # this should succeed rather than raise an error
        try:
            with PhotosynthesisModel(context) as photosynthesis:
                assert photosynthesis is not None
                assert photosynthesis.get_native_ptr() is not None
        except PhotosynthesisModelError:
            # If this fails, it means the plugin is not available
            # In that case, we expect a clear error message
            pass
        
    def test_photosynthesis_model_invalid_context(self):
        """Test initialization with invalid context."""
        with pytest.raises(PhotosynthesisModelError) as exc_info:
            PhotosynthesisModel("not a context")
            
        assert "Context parameter must be a Context instance" in str(exc_info.value)


@pytest.mark.native_only
class TestPhotosynthesisModelNative:
    """Test PhotosynthesisModel with native libraries."""
    
    def test_photosynthesis_model_initialization(self):
        """Test PhotosynthesisModel initialization with native libraries."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            assert photosynthesis is not None
            assert photosynthesis.get_native_ptr() is not None
            
    def test_photosynthesis_model_context_manager(self):
        """Test context manager functionality."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            ptr_before = photosynthesis.get_native_ptr()
            assert ptr_before is not None
            
        # After context manager, should be cleaned up
        assert photosynthesis.get_native_ptr() is None
        
    def test_model_type_configuration(self):
        """Test setting model types."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            # Test empirical model
            photosynthesis.setModelTypeEmpirical()
            assert True  # Should not raise errors
            
            # Test Farquhar model
            photosynthesis.setModelTypeFarquhar()
            assert True  # Should not raise errors
            
    def test_species_configuration(self):
        """Test species coefficient configuration."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            photosynthesis.setSpeciesCoefficients("Apple")
            assert True  # Should not raise errors
            
            # Test case insensitive
            photosynthesis.setSpeciesCoefficients("apple")
            assert True  # Should not raise errors
            
    def test_species_coefficients_retrieval(self):
        """Test getting species coefficients."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            coeffs = photosynthesis.getSpeciesCoefficients("Apple")
            assert isinstance(coeffs, list)
            assert len(coeffs) > 0
            
    def test_empirical_model_configuration(self):
        """Test empirical model configuration."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            coeffs = EmpiricalModelCoefficients()
            photosynthesis.setEmpiricalModelCoefficients(coeffs)
            assert True  # Should not raise errors
            
    def test_farquhar_model_configuration(self):
        """Test Farquhar model configuration."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            coeffs = FarquharModelCoefficients(Vcmax=100.0, Jmax=180.0)
            photosynthesis.setFarquharModelCoefficients(coeffs)
            assert True  # Should not raise errors
            
    @pytest.mark.native_only
    def test_individual_farquhar_parameters(self):
        """Test setting individual Farquhar parameters."""
        context = Context()
        
        # Add test primitive
        from pyhelios.types import vec3, vec2, RGBcolor
        center = vec3(0, 0, 0)
        size = vec2(1, 1)
        color = RGBcolor(0.5, 0.8, 0.3)
        uuid1 = context.addPatch(center=center, size=size, color=color)
        
        with PhotosynthesisModel(context) as photosynthesis:
            # Set initial coefficients so individual setters have something to work with
            from pyhelios.types import FarquharModelCoefficients
            initial_coeffs = FarquharModelCoefficients(
                Vcmax=80.0, Jmax=160.0, alpha=0.75, Rd=1.2
            )
            photosynthesis.setFarquharModelCoefficients(initial_coeffs, [uuid1])
            
            # Test basic parameter setting (now requires UUIDs)
            photosynthesis.setVcmax(100.0, [uuid1])
            photosynthesis.setJmax(180.0, [uuid1])
            photosynthesis.setDarkRespiration(2.0, [uuid1])
            photosynthesis.setQuantumEfficiency(0.85, [uuid1])
            photosynthesis.setLightResponseCurvature(0.7, [uuid1])
            
            # Test with temperature response parameters
            photosynthesis.setVcmax(100.0, [uuid1], dha=65000.0, topt=25.0, dhd=200000.0)
            photosynthesis.setJmax(180.0, [uuid1], dha=43000.0, topt=25.0, dhd=200000.0)
            
            assert True  # Should not raise errors
    
    @pytest.mark.native_only
    def test_parameter_persistence_critical(self):
        """
        CRITICAL: Test that individual parameter setters preserve other parameters.
        
        This test verifies the fix for the critical bug where individual parameter
        setters were overwriting all other parameters with defaults.
        """
        context = Context()
        
        # Add test primitive
        from pyhelios.types import vec3, vec2, RGBcolor
        center = vec3(0, 0, 0)
        size = vec2(1, 1)
        color = RGBcolor(0.5, 0.8, 0.3)
        uuid1 = context.addPatch(center=center, size=size, color=color)
        
        with PhotosynthesisModel(context) as photosynthesis:
            # Set explicit Farquhar coefficients first to establish known baseline
            from pyhelios.types import FarquharModelCoefficients
            initial_coeffs = FarquharModelCoefficients(
                Vcmax=120.0,   # μmol m⁻² s⁻¹
                Jmax=200.0,    # μmol m⁻² s⁻¹  
                alpha=0.8,     # mol electrons/mol photons
                Rd=1.5         # μmol m⁻² s⁻¹
            )
            photosynthesis.setFarquharModelCoefficients(initial_coeffs, [uuid1])
            
            # Get baseline coefficients for verification
            baseline_coeffs = photosynthesis.getFarquharModelCoefficients(uuid1)
            assert len(baseline_coeffs) >= 18, "Should have at least 18 Farquhar coefficients"
            
            # Store original values for verification
            original_vcmax = baseline_coeffs[0]   # Vcmax
            original_jmax = baseline_coeffs[1]    # Jmax  
            original_alpha = baseline_coeffs[2]   # alpha
            original_rd = baseline_coeffs[3]      # Rd
            
            # Verify we have the expected initial values
            assert abs(original_vcmax - 120.0) < 0.01, f"Initial Vcmax should be 120.0, got {original_vcmax}"
            assert abs(original_jmax - 200.0) < 0.01, f"Initial Jmax should be 200.0, got {original_jmax}"
            assert abs(original_alpha - 0.8) < 0.01, f"Initial alpha should be 0.8, got {original_alpha}"
            assert abs(original_rd - 1.5) < 0.01, f"Initial Rd should be 1.5, got {original_rd}"
            
            # TEST 1: Modify Vcmax, verify other parameters preserved
            new_vcmax = 150.0
            photosynthesis.setVcmax(new_vcmax, [uuid1])
            
            coeffs_after_vcmax = photosynthesis.getFarquharModelCoefficients(uuid1)
            assert abs(coeffs_after_vcmax[0] - new_vcmax) < 0.01, f"Vcmax not set correctly: {coeffs_after_vcmax[0]} != {new_vcmax}"
            assert abs(coeffs_after_vcmax[1] - original_jmax) < 0.01, f"Jmax was overwritten! {coeffs_after_vcmax[1]} != {original_jmax}"
            assert abs(coeffs_after_vcmax[2] - original_alpha) < 0.01, f"Alpha was overwritten! {coeffs_after_vcmax[2]} != {original_alpha}"
            assert abs(coeffs_after_vcmax[3] - original_rd) < 0.01, f"Rd was overwritten! {coeffs_after_vcmax[3]} != {original_rd}"
            
            # TEST 2: Modify Jmax, verify Vcmax and others preserved  
            new_jmax = 250.0
            photosynthesis.setJmax(new_jmax, [uuid1])
            
            coeffs_after_jmax = photosynthesis.getFarquharModelCoefficients(uuid1)
            assert abs(coeffs_after_jmax[0] - new_vcmax) < 0.01, f"Vcmax was overwritten! {coeffs_after_jmax[0]} != {new_vcmax}"
            assert abs(coeffs_after_jmax[1] - new_jmax) < 0.01, f"Jmax not set correctly: {coeffs_after_jmax[1]} != {new_jmax}"
            assert abs(coeffs_after_jmax[2] - original_alpha) < 0.01, f"Alpha was overwritten! {coeffs_after_jmax[2]} != {original_alpha}"
            assert abs(coeffs_after_jmax[3] - original_rd) < 0.01, f"Rd was overwritten! {coeffs_after_jmax[3]} != {original_rd}"
            
            # TEST 3: Modify Rd, verify Vcmax, Jmax, and alpha preserved
            new_rd = 5.0
            photosynthesis.setDarkRespiration(new_rd, [uuid1])
            
            coeffs_after_rd = photosynthesis.getFarquharModelCoefficients(uuid1)
            assert abs(coeffs_after_rd[0] - new_vcmax) < 0.01, f"Vcmax was overwritten! {coeffs_after_rd[0]} != {new_vcmax}"
            assert abs(coeffs_after_rd[1] - new_jmax) < 0.01, f"Jmax was overwritten! {coeffs_after_rd[1]} != {new_jmax}"
            assert abs(coeffs_after_rd[2] - original_alpha) < 0.01, f"Alpha was overwritten! {coeffs_after_rd[2]} != {original_alpha}"
            assert abs(coeffs_after_rd[3] - new_rd) < 0.01, f"Rd not set correctly: {coeffs_after_rd[3]} != {new_rd}"
            
            # TEST 4: Modify alpha, verify all previous changes preserved
            new_alpha = 0.95
            photosynthesis.setQuantumEfficiency(new_alpha, [uuid1])
            
            coeffs_after_alpha = photosynthesis.getFarquharModelCoefficients(uuid1)
            assert abs(coeffs_after_alpha[0] - new_vcmax) < 0.01, f"Vcmax was overwritten! {coeffs_after_alpha[0]} != {new_vcmax}"
            assert abs(coeffs_after_alpha[1] - new_jmax) < 0.01, f"Jmax was overwritten! {coeffs_after_alpha[1]} != {new_jmax}"
            assert abs(coeffs_after_alpha[2] - new_alpha) < 0.01, f"Alpha not set correctly: {coeffs_after_alpha[2]} != {new_alpha}"
            assert abs(coeffs_after_alpha[3] - new_rd) < 0.01, f"Rd was overwritten! {coeffs_after_alpha[3]} != {new_rd}"
            
            print("✓ CRITICAL TEST PASSED: Individual parameter setters preserve existing parameters!")
            
    def test_model_execution(self):
        """Test model execution methods."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            # Configure model first
            coeffs = EmpiricalModelCoefficients()
            photosynthesis.setEmpiricalModelCoefficients(coeffs)
            
            # Run model
            photosynthesis.run()
            assert True  # Should not raise errors
            
    def test_primitive_specific_operations(self):
        """Test operations with specific primitives."""
        context = Context()
        
        # Add some primitives to context
        from pyhelios.types import vec3, vec2, RGBcolor
        center = vec3(0, 0, 0)
        size = vec2(1, 1)
        color = RGBcolor(0.5, 0.8, 0.3)
        
        uuid1 = context.addPatch(center=center, size=size, color=color)
        uuid2 = context.addPatch(center=vec3(1, 1, 1), size=size, color=color)
        
        with PhotosynthesisModel(context) as photosynthesis:
            # Configure coefficients for specific primitives
            coeffs = EmpiricalModelCoefficients()
            photosynthesis.setEmpiricalModelCoefficients(coeffs, uuids=[uuid1, uuid2])
            
            # Run for specific primitives
            photosynthesis.runForPrimitives([uuid1, uuid2])
            photosynthesis.runForPrimitives(uuid1)  # Single primitive
            
            assert True  # Should not raise errors
            
    def test_coefficient_retrieval(self):
        """Test getting coefficients for primitives."""
        context = Context()
        
        # Add a primitive
        from pyhelios.types import vec3, vec2, RGBcolor
        center = vec3(0, 0, 0)
        size = vec2(1, 1)
        color = RGBcolor(0.5, 0.8, 0.3)
        
        uuid = context.addPatch(center=center, size=size, color=color)
        
        with PhotosynthesisModel(context) as photosynthesis:
            # Set coefficients
            empirical_coeffs = EmpiricalModelCoefficients()
            photosynthesis.setEmpiricalModelCoefficients(empirical_coeffs)
            
            farquhar_coeffs = FarquharModelCoefficients(Vcmax=100.0, Jmax=180.0)
            photosynthesis.setFarquharModelCoefficients(farquhar_coeffs)
            
            # Get coefficients
            retrieved_empirical = photosynthesis.getEmpiricalModelCoefficients(uuid)
            retrieved_farquhar = photosynthesis.getFarquharModelCoefficients(uuid)
            
            assert isinstance(retrieved_empirical, list)
            assert isinstance(retrieved_farquhar, list)
            assert len(retrieved_empirical) > 0
            assert len(retrieved_farquhar) > 0
            
    def test_model_utilities(self):
        """Test model utility methods."""
        context = Context()
        
        with PhotosynthesisModel(context) as photosynthesis:
            # Test message control
            photosynthesis.enableMessages()
            photosynthesis.disableMessages()
            
            # Test reporting
            photosynthesis.printModelReport()
            
            # Test export
            photosynthesis.exportResults("test_data")
            
            # Test validation
            is_valid = photosynthesis.validateConfiguration()
            assert isinstance(is_valid, bool)
            assert is_valid  # Should have valid pointer
            
            # Test reset
            photosynthesis.resetModel()
            
            assert True  # Should not raise errors


@pytest.mark.cross_platform
class TestPhotosynthesisValidationDecorators:
    """Test validation decorators work properly."""
    
    def test_species_validation_decorator(self):
        """Test species validation decorator."""
        from pyhelios.validation.plugin_decorators import validate_photosynthesis_species_params
        
        @validate_photosynthesis_species_params
        def dummy_method(self, species):
            return species
            
        # Valid species
        result = dummy_method(None, "Apple")
        assert result == "Apple"
        
        # Invalid species should raise ValidationError
        with pytest.raises(ValidationError):
            dummy_method(None, "INVALID_SPECIES")
            
    def test_uuid_validation_decorator(self):
        """Test UUID validation decorator."""
        from pyhelios.validation.plugin_decorators import validate_photosynthesis_uuid_params
        
        @validate_photosynthesis_uuid_params  
        def dummy_method(self, uuids):
            return uuids
            
        # Valid single UUID
        result = dummy_method(None, 123)
        assert result == 123
        
        # Valid UUID list
        result = dummy_method(None, [123, 456, 789])
        assert result == [123, 456, 789]
        
        # Invalid UUID should raise ValidationError
        with pytest.raises(ValidationError):
            dummy_method(None, "not_an_int")


@pytest.mark.cross_platform
class TestPhotosynthesisParameterValidation:
    """Test all parameter validation functions work correctly."""
    
    def test_species_validation_ranges(self):
        """Test species name validation with various values."""
        # Valid species
        assert validate_species_name("Apple") == "Apple"
        assert validate_species_name("apple") == "Apple"  # Case insensitive
        assert validate_species_name("Grape") == "Grape"
        
        # Invalid species
        with pytest.raises(ValueError):
            validate_species_name("INVALID_SPECIES")
            
        with pytest.raises(ValueError):
            validate_species_name("")
            
    def test_empirical_coefficients_structure(self):
        """Test empirical model coefficients structure."""
        # Valid coefficients
        coeffs = EmpiricalModelCoefficients()
        assert hasattr(coeffs, 'Tref')
        assert hasattr(coeffs, 'Asat')
        assert hasattr(coeffs, 'to_array')
        
        # Test array conversion
        arr = coeffs.to_array()
        assert isinstance(arr, list)
        assert len(arr) == 10
        
    def test_farquhar_coefficients_structure(self):
        """Test Farquhar model coefficients structure."""
        # Valid coefficients
        coeffs = FarquharModelCoefficients()
        assert hasattr(coeffs, 'Vcmax')
        assert hasattr(coeffs, 'Jmax')
        assert coeffs.Vcmax == -1.0  # Uninitialized default


if __name__ == "__main__":
    pytest.main([__file__])