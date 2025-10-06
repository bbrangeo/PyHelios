"""
Tests for BoundaryLayerConductance integration
"""

import pytest
from pyhelios import Context
from pyhelios.plugins.registry import get_plugin_registry
# Import HeliosError from pyhelios main module to ensure consistency
from pyhelios import HeliosError
from pyhelios.types import vec3

class TestBoundaryLayerConductanceMetadata:
    """Test plugin metadata and registration"""

    @pytest.mark.cross_platform
    def test_plugin_metadata_exists(self):
        """Test that plugin metadata is correctly defined"""
        from pyhelios.config.plugin_metadata import get_plugin_metadata

        metadata = get_plugin_metadata('boundarylayerconductance')
        assert metadata is not None
        assert metadata.name == 'boundarylayerconductance'
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
        assert 'boundarylayerconductance' in PLUGIN_METADATA

        # Should not require GPU
        metadata = PLUGIN_METADATA['boundarylayerconductance']
        assert not metadata.gpu_required

        # Should have no system dependencies
        assert metadata.system_dependencies == []


class TestBoundaryLayerConductanceAvailability:
    """Test plugin availability detection"""

    @pytest.mark.cross_platform
    def test_plugin_registry_awareness(self):
        """Test that plugin registry knows about BoundaryLayerConductance"""
        registry = get_plugin_registry()

        # Plugin should be known (even if not available)
        all_plugins = registry.get_available_plugins()
        # Note: boundarylayerconductance will be in all_plugins only if actually built and available

    @pytest.mark.cross_platform
    def test_graceful_unavailable_handling(self):
        """Test graceful handling when plugin unavailable"""
        registry = get_plugin_registry()

        with Context() as context:
            if not registry.is_plugin_available('boundarylayerconductance'):
                # Should raise informative error
                try:
                    from pyhelios import BoundaryLayerConductanceModel
                    if BoundaryLayerConductanceModel is not None:
                        with pytest.raises(Exception) as exc_info:
                            BoundaryLayerConductanceModel(context)

                        error_msg = str(exc_info.value).lower()
                        # Error should mention rebuilding or plugin unavailability
                        expected_keywords = ['rebuild', 'build', 'enable', 'compile', 'plugin', 'not available', 'unavailable']
                        found_keywords = [k for k in expected_keywords if k in error_msg]
                        assert len(found_keywords) > 0, f"Error message missing expected keywords. Got: '{str(exc_info.value)}'"
                except ImportError:
                    # BoundaryLayerConductanceModel not imported when plugin unavailable
                    pass
            else:
                # Plugin is available - nothing to test for graceful unavailable handling
                pass


class TestBoundaryLayerConductanceInterface:
    """Test plugin interface without requiring native library"""

    @pytest.mark.cross_platform
    def test_plugin_class_structure(self):
        """Test that plugin class has expected structure"""
        try:
            from pyhelios import (
                BoundaryLayerConductanceModel,
                BoundaryLayerConductanceModelError
            )

            # Test class attributes and methods exist
            assert hasattr(BoundaryLayerConductanceModel, '__init__')
            assert hasattr(BoundaryLayerConductanceModel, '__enter__')
            assert hasattr(BoundaryLayerConductanceModel, '__exit__')
            assert hasattr(BoundaryLayerConductanceModel, 'enableMessages')
            assert hasattr(BoundaryLayerConductanceModel, 'disableMessages')
            assert hasattr(BoundaryLayerConductanceModel, 'setBoundaryLayerModel')
            assert hasattr(BoundaryLayerConductanceModel, 'run')
            assert hasattr(BoundaryLayerConductanceModel, 'is_available')

        except ImportError:
            # Expected when plugin not built
            pass

    @pytest.mark.cross_platform
    def test_error_types_available(self):
        """Test that error types are properly defined"""
        try:
            from pyhelios import BoundaryLayerConductanceModelError
            assert issubclass(BoundaryLayerConductanceModelError, HeliosError)
        except ImportError:
            # Expected when plugin not built
            pass


@pytest.mark.native_only
class TestBoundaryLayerConductanceFunctionality:
    """Test actual plugin functionality with native library"""

    def test_plugin_creation(self, basic_context):
        """Test plugin can be created and destroyed"""
        from pyhelios import BoundaryLayerConductanceModel

        bl_model = BoundaryLayerConductanceModel(basic_context)
        assert bl_model is not None
        assert isinstance(bl_model, BoundaryLayerConductanceModel)

        # Test cleanup
        bl_model.__exit__(None, None, None)

    def test_plugin_context_manager(self, basic_context):
        """Test plugin works as context manager"""
        from pyhelios import BoundaryLayerConductanceModel

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            assert bl_model is not None

    def test_set_model_pohlhausen(self, basic_context):
        """Test setting Pohlhausen model"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add a patch
        uuid = basic_context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Set Pohlhausen model (default)
            bl_model.setBoundaryLayerModel("Pohlhausen")

            # Run calculation
            bl_model.run()

    def test_set_model_inclined_plate(self, basic_context):
        """Test setting InclinedPlate model"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add a patch
        uuid = basic_context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Set InclinedPlate model
            bl_model.setBoundaryLayerModel("InclinedPlate")

            # Run calculation
            bl_model.run()

    def test_set_model_sphere(self, basic_context):
        """Test setting Sphere model"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add a patch
        uuid = basic_context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Set Sphere model
            bl_model.setBoundaryLayerModel("Sphere")

            # Run calculation
            bl_model.run()

    def test_set_model_ground(self, basic_context):
        """Test setting Ground model"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add a patch
        uuid = basic_context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Set Ground model
            bl_model.setBoundaryLayerModel("Ground")

            # Run calculation
            bl_model.run()

    def test_set_model_invalid_name(self, basic_context):
        """Test that invalid model name raises error"""
        from pyhelios import BoundaryLayerConductanceModel

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Should raise ValueError for invalid model name
            with pytest.raises(ValueError, match="Invalid boundary layer model"):
                bl_model.setBoundaryLayerModel("InvalidModel")

    def test_set_model_for_uuid(self, basic_context):
        """Test setting model for specific UUID"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add two patches
        uuid1 = basic_context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])
        uuid2 = basic_context.addPatch(center=vec3(0, 0, 2), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Set different models for different patches
            bl_model.setBoundaryLayerModel("Pohlhausen", uuids=[uuid1])
            bl_model.setBoundaryLayerModel("Sphere", uuids=[uuid2])

            # Run for all
            bl_model.run()

    def test_set_model_for_uuids(self, basic_context):
        """Test setting model for multiple UUIDs"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add multiple patches
        uuids = []
        for i in range(5):
            uuid = basic_context.addPatch(center=vec3(i, 0, 1), size=[0.1, 0.1])
            uuids.append(uuid)

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Set InclinedPlate for first 3
            bl_model.setBoundaryLayerModel("InclinedPlate", uuids=uuids[:3])

            # Set Sphere for last 2
            bl_model.setBoundaryLayerModel("Sphere", uuids=uuids[3:])

            # Run for all
            bl_model.run()

    def test_run_for_all_primitives(self, basic_context):
        """Test running for all primitives"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add multiple patches
        for i in range(3):
            basic_context.addPatch(center=vec3(i, 0, 1), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            bl_model.setBoundaryLayerModel("Pohlhausen")

            # Run for all
            bl_model.run()

    def test_run_for_specific_uuids(self, basic_context):
        """Test running for specific UUIDs"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add patches
        uuid1 = basic_context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])
        uuid2 = basic_context.addPatch(center=vec3(1, 0, 1), size=[0.1, 0.1])
        uuid3 = basic_context.addPatch(center=vec3(2, 0, 1), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            bl_model.setBoundaryLayerModel("InclinedPlate")

            # Run for specific UUIDs only
            bl_model.run(uuids=[uuid1, uuid3])

    def test_message_enable_disable(self, basic_context):
        """Test message control"""
        from pyhelios import BoundaryLayerConductanceModel

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Enable messages
            bl_model.enableMessages()

            # Disable messages
            bl_model.disableMessages()

    def test_is_available_static_method(self):
        """Test is_available static method"""
        from pyhelios import BoundaryLayerConductanceModel

        # Should return True since we're in native_only tests
        assert BoundaryLayerConductanceModel.is_available() is True


@pytest.mark.native_only
class TestBoundaryLayerConductanceIntegration:
    """Test plugin integration with other PyHelios components"""

    def test_context_integration(self, basic_context):
        """Test plugin works with Context geometry"""
        from pyhelios import BoundaryLayerConductanceModel

        # Add various geometry
        patch_uuid = basic_context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])
        triangle_uuid = basic_context.addTriangle(vec3(0, 0, 0), vec3(1, 0, 0), vec3(0, 1, 0))

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Set model and run
            bl_model.setBoundaryLayerModel("Pohlhausen")
            bl_model.run()

    def test_different_models_different_primitives(self, basic_context):
        """Test using different models for different primitive types"""
        from pyhelios import BoundaryLayerConductanceModel

        # Create leaf patches
        leaf_uuids = []
        for i in range(3):
            uuid = basic_context.addPatch(center=vec3(i, 0, 1), size=[0.05, 0.05])
            leaf_uuids.append(uuid)

        # Create fruit patches (spheres approximated as patches)
        fruit_uuids = []
        for i in range(2):
            uuid = basic_context.addPatch(center=vec3(i, 1, 1), size=[0.02, 0.02])
            fruit_uuids.append(uuid)

        # Create ground patches
        ground_uuids = []
        for i in range(2):
            uuid = basic_context.addPatch(center=vec3(i, 0, 0), size=[1.0, 1.0])
            ground_uuids.append(uuid)

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Use different models for different types
            bl_model.setBoundaryLayerModel("InclinedPlate", uuids=leaf_uuids)
            bl_model.setBoundaryLayerModel("Sphere", uuids=fruit_uuids)
            bl_model.setBoundaryLayerModel("Ground", uuids=ground_uuids)

            # Run for all
            bl_model.run()

    def test_error_handling_integration(self, basic_context):
        """Test that errors are properly raised"""
        from pyhelios import BoundaryLayerConductanceModel, BoundaryLayerConductanceModelError

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            # Test invalid model name
            with pytest.raises(ValueError):
                bl_model.setBoundaryLayerModel("NotAModel")


@pytest.mark.slow
class TestBoundaryLayerConductancePerformance:
    """Performance tests for plugin operations"""

    @pytest.mark.native_only
    def test_computation_performance(self, basic_context):
        """Test computation performance doesn't regress"""
        import time
        from pyhelios import BoundaryLayerConductanceModel

        # Add many patches
        for i in range(100):
            basic_context.addPatch(center=vec3(i % 10, i // 10, 1), size=[0.1, 0.1])

        with BoundaryLayerConductanceModel(basic_context) as bl_model:
            bl_model.setBoundaryLayerModel("Pohlhausen")

            # Time computation
            start_time = time.time()
            bl_model.run()
            elapsed = time.time() - start_time

            # Should be fast (adjust threshold based on expected performance)
            assert elapsed < 2.0, f"Computation too slow: {elapsed:.3f}s"
