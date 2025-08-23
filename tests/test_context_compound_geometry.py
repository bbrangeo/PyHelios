"""
Tests for PyHelios Context compound geometry methods.

These tests verify the compound geometry creation methods including tiles,
spheres, tubes, and boxes that return lists of primitive UUIDs.
"""

import pytest
from unittest.mock import Mock, patch
import platform
import numpy as np
from typing import List, Union

import pyhelios
from pyhelios import Context
from pyhelios.types import *  # Import all vector types for convenience
from tests.conftest import assert_vec3_equal, assert_vec2_equal, assert_color_equal
from tests.test_utils import GeometryValidator, PlatformHelper


def is_compound_geometry_available():
    """Check if compound geometry functions are available in the current build."""
    try:
        with Context() as context:
            context.addTile()
        return True
    except NotImplementedError:
        return False
    except Exception:
        # Any other exception means the functions exist but failed for other reasons
        return True


compound_geometry_available = pytest.mark.skipif(
    not is_compound_geometry_available(),
    reason="Compound geometry functions not available in current Helios library build"
)


class TestCompoundGeometryValidation:
    """Test validation helpers for compound geometry methods."""
    
    @staticmethod
    def validate_uuid_list(uuids: List[int], expected_min_count: int = 1) -> bool:
        """Validate that a UUID list meets basic requirements."""
        assert isinstance(uuids, list), f"Expected list, got {type(uuids)}"
        assert len(uuids) >= expected_min_count, f"Expected at least {expected_min_count} UUIDs, got {len(uuids)}"
        assert all(isinstance(uuid, int) for uuid in uuids), "All UUIDs must be integers"
        assert all(uuid >= 0 for uuid in uuids), "All UUIDs must be non-negative"
        assert len(set(uuids)) == len(uuids), "All UUIDs must be unique"
        return True
    
    @staticmethod
    def validate_primitive_list(context, uuids: List[int], expected_primitive_type=None):
        """Validate that all UUIDs correspond to valid primitives of expected type."""
        for uuid in uuids:
            # Check UUID exists in context
            assert uuid in context.getAllUUIDs(), f"UUID {uuid} not found in context"
            
            # Check primitive type if specified
            if expected_primitive_type is not None:
                actual_type = context.getPrimitiveType(uuid)
                assert actual_type == expected_primitive_type, \
                    f"Expected {expected_primitive_type}, got {actual_type} for UUID {uuid}"
        return True
    
    @staticmethod
    def calculate_expected_tile_count(subdiv: int2) -> int:
        """Calculate expected number of patches in a tile."""
        return subdiv.x * subdiv.y
    
    @staticmethod
    def calculate_expected_sphere_triangles(ndivs: int) -> int:
        """Calculate expected number of triangles in a sphere."""
        # Sphere tessellation formula: approximately 2 * ndivs^2 triangles
        # This is an approximation - exact formula depends on tessellation algorithm
        return 2 * ndivs * ndivs
    
    @staticmethod
    def calculate_expected_tube_triangles(nodes_count: int, ndivs: int) -> int:
        """Calculate expected number of triangles in a tube."""
        # Tube has ndivs triangles per segment, 2 triangles per radial division
        segments = nodes_count - 1
        return segments * ndivs * 2
    
    @staticmethod
    def calculate_expected_box_patches(subdiv: int3) -> int:
        """Calculate expected number of patches on a box."""
        # Box has 6 faces, each subdivided according to subdiv
        return 2 * (subdiv.x * subdiv.y + subdiv.x * subdiv.z + subdiv.y * subdiv.z)


@pytest.mark.native_only
@compound_geometry_available
class TestTileCreation:
    """Test Context.addTile() method."""
    
    def test_addTile_basic(self, basic_context):
        """Test basic tile creation with default parameters."""
        tile_uuids = basic_context.addTile()
        
        TestCompoundGeometryValidation.validate_uuid_list(tile_uuids, 1)
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, tile_uuids, PrimitiveType.Patch
        )
        
        # Default subdiv is (1, 1), so should create 1 patch
        expected_count = TestCompoundGeometryValidation.calculate_expected_tile_count(int2(1, 1))
        assert len(tile_uuids) == expected_count
        
        # Verify context state
        assert basic_context.getPrimitiveCount() == len(tile_uuids)
    
    def test_addTile_with_parameters(self, basic_context):
        """Test tile creation with specified parameters."""
        center = vec3(2, 3, 4)
        size = vec2(3, 2)
        rotation = SphericalCoord(0.5, 0.3, 0)
        subdiv = int2(2, 3)
        color = RGBcolor(0.8, 0.2, 0.1)
        
        tile_uuids = basic_context.addTile(
            center=center, size=size, rotation=rotation, 
            subdiv=subdiv, color=color
        )
        
        TestCompoundGeometryValidation.validate_uuid_list(tile_uuids)
        
        # Should create subdiv.x * subdiv.y patches
        expected_count = TestCompoundGeometryValidation.calculate_expected_tile_count(subdiv)
        assert len(tile_uuids) == expected_count
        
        # Verify all patches have the specified color
        for uuid in tile_uuids:
            actual_color = basic_context.getPrimitiveColor(uuid)
            assert_color_equal(actual_color, color)
    
    def test_addTile_subdivisions(self, basic_context):
        """Test tile creation with various subdivision levels."""
        test_cases = [
            (int2(1, 1), 1),
            (int2(2, 2), 4),
            (int2(3, 4), 12),
            (int2(5, 1), 5),
        ]
        
        for subdiv, expected_count in test_cases:
            # Use the context directly, not as a context manager in a loop
            tile_uuids = basic_context.addTile(subdiv=subdiv)
            
            assert len(tile_uuids) == expected_count, \
                f"Subdivision {subdiv} should create {expected_count} patches, got {len(tile_uuids)}"
            TestCompoundGeometryValidation.validate_uuid_list(tile_uuids, expected_count)
    
    def test_addTile_multiple_tiles(self, basic_context):
        """Test creating multiple tiles in the same context."""
        # Create first tile
        tile1_uuids = basic_context.addTile(
            center=vec3(-2, 0, 0), subdiv=int2(2, 2), color=RGBcolor(1, 0, 0)
        )
        
        # Create second tile
        tile2_uuids = basic_context.addTile(
            center=vec3(2, 0, 0), subdiv=int2(3, 1), color=RGBcolor(0, 1, 0)
        )
        
        # Verify both tiles
        assert len(tile1_uuids) == 4
        assert len(tile2_uuids) == 3
        
        # No overlap in UUIDs
        assert set(tile1_uuids).isdisjoint(set(tile2_uuids))
        
        # Total primitive count should be sum
        assert basic_context.getPrimitiveCount() == len(tile1_uuids) + len(tile2_uuids)
        
        # Verify colors are maintained
        for uuid in tile1_uuids:
            color = basic_context.getPrimitiveColor(uuid)
            assert_color_equal(color, RGBcolor(1, 0, 0))
        
        for uuid in tile2_uuids:
            color = basic_context.getPrimitiveColor(uuid)
            assert_color_equal(color, RGBcolor(0, 1, 0))
    
    def test_addTile_parameter_validation(self, basic_context):
        """Test parameter validation for addTile."""
        # Test invalid subdivision values
        with pytest.raises(ValueError):
            basic_context.addTile(subdiv=int2(0, 1))  # Zero subdivision
        
        with pytest.raises(ValueError):
            basic_context.addTile(subdiv=int2(1, -1))  # Negative subdivision
        
        # Test invalid size values
        with pytest.raises(ValueError):
            basic_context.addTile(size=vec2(0, 1))  # Zero size
        
        with pytest.raises(ValueError):
            basic_context.addTile(size=vec2(1, -1))  # Negative size


@pytest.mark.native_only
@compound_geometry_available
class TestSphereCreation:
    """Test Context.addSphere() method."""
    
    def test_addSphere_basic(self, basic_context):
        """Test basic sphere creation with default parameters."""
        sphere_uuids = basic_context.addSphere()
        
        TestCompoundGeometryValidation.validate_uuid_list(sphere_uuids, 1)
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, sphere_uuids, PrimitiveType.Triangle
        )
        
        # Sphere should create multiple triangles
        assert len(sphere_uuids) > 10  # At least some reasonable number of triangles
        
        # Verify context state
        assert basic_context.getPrimitiveCount() == len(sphere_uuids)
    
    def test_addSphere_with_parameters(self, basic_context):
        """Test sphere creation with specified parameters."""
        center = vec3(1, 2, 3)
        radius = 2.5
        ndivs = 15
        color = RGBcolor(0.1, 0.9, 0.3)
        
        sphere_uuids = basic_context.addSphere(
            center=center, radius=radius, ndivs=ndivs, color=color
        )
        
        TestCompoundGeometryValidation.validate_uuid_list(sphere_uuids)
        
        # Verify all triangles have the specified color
        for uuid in sphere_uuids:
            actual_color = basic_context.getPrimitiveColor(uuid)
            assert_color_equal(actual_color, color)
        
        # Verify sphere is roughly the right size by checking vertex distances
        sample_uuid = sphere_uuids[0]
        vertices = basic_context.getPrimitiveVertices(sample_uuid)
        
        # All vertices should be approximately radius distance from center
        for vertex in vertices:
            distance = ((vertex.x - center.x)**2 + 
                       (vertex.y - center.y)**2 + 
                       (vertex.z - center.z)**2)**0.5
            assert distance == pytest.approx(radius, rel=0.1)
    
    def test_addSphere_divisions_scaling(self, basic_context):
        """Test that higher divisions create more triangles."""
        sphere_low = basic_context.addSphere(ndivs=5)
        basic_context.__exit__(None, None, None)  # Reset context
        
        with Context() as new_context:
            sphere_high = new_context.addSphere(ndivs=15)
            
            # Higher divisions should create more triangles
            assert len(sphere_high) > len(sphere_low)
    
    def test_addSphere_parameter_validation(self, basic_context):
        """Test parameter validation for addSphere."""
        # Test invalid radius
        with pytest.raises(ValueError, match="radius must be positive"):
            basic_context.addSphere(radius=0)
        
        with pytest.raises(ValueError, match="radius must be positive"):
            basic_context.addSphere(radius=-1.5)
        
        # Test invalid divisions
        with pytest.raises(ValueError, match="divisions must be at least 3"):
            basic_context.addSphere(ndivs=2)
        
        with pytest.raises(ValueError, match="divisions must be at least 3"):
            basic_context.addSphere(ndivs=0)


@pytest.mark.native_only
@compound_geometry_available
class TestTubeCreation:
    """Test Context.addTube() method."""
    
    def test_addTube_basic(self, basic_context):
        """Test basic tube creation with minimal parameters."""
        nodes = [vec3(0, 0, 0), vec3(1, 0, 0)]
        radius = 0.5
        
        tube_uuids = basic_context.addTube(nodes, radius)
        
        TestCompoundGeometryValidation.validate_uuid_list(tube_uuids, 1)
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, tube_uuids, PrimitiveType.Triangle
        )
        
        # Tube should create multiple triangles
        assert len(tube_uuids) > 6  # At least some reasonable number for a simple tube
        
        # Verify context state
        assert basic_context.getPrimitiveCount() == len(tube_uuids)
    
    def test_addTube_single_radius(self, basic_context):
        """Test tube creation with single radius for all nodes."""
        nodes = [
            vec3(0, 0, 0),
            vec3(1, 0, 0), 
            vec3(2, 1, 0),
            vec3(3, 1, 1)
        ]
        radius = 0.3
        ndivs = 8
        color = RGBcolor(0.7, 0.2, 0.9)
        
        tube_uuids = basic_context.addTube(nodes, radius, ndivs, color)
        
        TestCompoundGeometryValidation.validate_uuid_list(tube_uuids)
        
        # Verify all triangles have the specified color
        for uuid in tube_uuids:
            actual_color = basic_context.getPrimitiveColor(uuid)
            assert_color_equal(actual_color, color)
    
    def test_addTube_variable_radii(self, basic_context):
        """Test tube creation with different radius at each node."""
        nodes = [
            vec3(0, 0, 0),
            vec3(1, 0, 0),
            vec3(2, 1, 0)
        ]
        radii = [0.1, 0.5, 0.2]  # Variable radii
        
        tube_uuids = basic_context.addTube(nodes, radii)
        
        TestCompoundGeometryValidation.validate_uuid_list(tube_uuids)
        
        # More complex validation could check that the tube actually varies in radius
        # For now, just verify it completes successfully
        assert len(tube_uuids) > 10
    
    def test_addTube_variable_colors(self, basic_context):
        """Test tube creation with different colors at each node."""
        nodes = [
            vec3(0, 0, 0),
            vec3(1, 0, 0),
            vec3(1, 1, 0)
        ]
        radii = 0.2
        colors = [
            RGBcolor(1, 0, 0),  # Red
            RGBcolor(0, 1, 0),  # Green  
            RGBcolor(0, 0, 1)   # Blue
        ]
        
        tube_uuids = basic_context.addTube(nodes, radii, colors=colors)
        
        TestCompoundGeometryValidation.validate_uuid_list(tube_uuids)
        
        # Colors should be interpolated along the tube
        # Exact color verification depends on interpolation implementation
        for uuid in tube_uuids:
            color = basic_context.getPrimitiveColor(uuid)
            assert isinstance(color, RGBcolor)
    
    def test_addTube_single_color_for_all(self, basic_context):
        """Test tube creation with single color applied to all nodes."""
        nodes = [vec3(0, 0, 0), vec3(1, 1, 1), vec3(0, 2, 0)]
        radii = [0.1, 0.2, 0.1]
        color = RGBcolor(0.5, 0.5, 0.5)  # Single color
        
        tube_uuids = basic_context.addTube(nodes, radii, colors=color)
        
        TestCompoundGeometryValidation.validate_uuid_list(tube_uuids)
        
        # All triangles should have the same color (or close to it due to interpolation)
        sample_color = basic_context.getPrimitiveColor(tube_uuids[0])
        assert_color_equal(sample_color, color, tolerance=0.1)
    
    def test_addTube_parameter_validation(self, basic_context):
        """Test parameter validation for addTube."""
        # Test insufficient nodes
        with pytest.raises(ValueError, match="at least 2 nodes"):
            basic_context.addTube([vec3(0, 0, 0)], 0.5)
        
        with pytest.raises(ValueError, match="at least 2 nodes"):
            basic_context.addTube([], 0.5)
        
        # Test invalid divisions
        with pytest.raises(ValueError, match="radial divisions must be at least 3"):
            basic_context.addTube([vec3(0, 0, 0), vec3(1, 0, 0)], 0.5, ndivs=2)
        
        # Test mismatched radii count
        nodes = [vec3(0, 0, 0), vec3(1, 0, 0), vec3(2, 0, 0)]
        radii = [0.1, 0.2]  # Too few radii
        with pytest.raises(ValueError, match="Number of radii.*must match number of nodes"):
            basic_context.addTube(nodes, radii)
        
        # Test mismatched colors count
        colors = [RGBcolor(1, 0, 0), RGBcolor(0, 1, 0)]  # Too few colors
        with pytest.raises(ValueError, match="Number of colors.*must match number of nodes"):
            basic_context.addTube(nodes, 0.5, colors=colors)
        
        # Test invalid radii (negative/zero)
        with pytest.raises(ValueError, match="All radii must be positive"):
            basic_context.addTube([vec3(0, 0, 0), vec3(1, 0, 0)], [0.5, 0])
        
        with pytest.raises(ValueError, match="All radii must be positive"):
            basic_context.addTube([vec3(0, 0, 0), vec3(1, 0, 0)], [-0.1, 0.5])


@pytest.mark.native_only
@compound_geometry_available
class TestBoxCreation:
    """Test Context.addBox() method."""
    
    def test_addBox_basic(self, basic_context):
        """Test basic box creation with default parameters."""
        box_uuids = basic_context.addBox()
        
        TestCompoundGeometryValidation.validate_uuid_list(box_uuids, 6)  # At least 6 faces
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, box_uuids, PrimitiveType.Patch
        )
        
        # Default subdiv is (1, 1, 1), so should create 6 patches (one per face)
        expected_count = TestCompoundGeometryValidation.calculate_expected_box_patches(int3(1, 1, 1))
        assert len(box_uuids) == expected_count
        
        # Verify context state
        assert basic_context.getPrimitiveCount() == len(box_uuids)
    
    def test_addBox_with_parameters(self, basic_context):
        """Test box creation with specified parameters."""
        center = vec3(1, 2, 3)
        size = vec3(2, 1, 3)
        subdiv = int3(2, 1, 2)
        color = RGBcolor(0.3, 0.7, 0.1)
        
        box_uuids = basic_context.addBox(
            center=center, size=size, subdiv=subdiv, color=color
        )
        
        TestCompoundGeometryValidation.validate_uuid_list(box_uuids)
        
        # Calculate expected number of patches
        expected_count = TestCompoundGeometryValidation.calculate_expected_box_patches(subdiv)
        assert len(box_uuids) == expected_count
        
        # Verify all patches have the specified color
        for uuid in box_uuids:
            actual_color = basic_context.getPrimitiveColor(uuid)
            assert_color_equal(actual_color, color)
    
    def test_addBox_subdivisions(self, basic_context):
        """Test box creation with various subdivision levels."""
        test_cases = [
            (int3(1, 1, 1), 6),   # Basic cube: 6 faces
            (int3(2, 2, 2), 24),  # 2*2 patches per face * 6 faces = 24
            (int3(1, 2, 3), 22),  # Mixed subdivisions
        ]
        
        for subdiv, expected_count in test_cases:
            with Context() as ctx:  # Fresh context for each test
                box_uuids = ctx.addBox(subdiv=subdiv)
                
                calculated_count = TestCompoundGeometryValidation.calculate_expected_box_patches(subdiv)
                assert calculated_count == expected_count, \
                    f"Test case calculation error for {subdiv}"
                
                assert len(box_uuids) == expected_count, \
                    f"Subdivision {subdiv} should create {expected_count} patches, got {len(box_uuids)}"
    
    def test_addBox_parameter_validation(self, basic_context):
        """Test parameter validation for addBox."""
        # Test invalid size values
        with pytest.raises(ValueError, match="All box dimensions must be positive"):
            basic_context.addBox(size=vec3(0, 1, 1))
        
        with pytest.raises(ValueError, match="All box dimensions must be positive"):
            basic_context.addBox(size=vec3(1, -1, 1))
        
        # Test invalid subdivision values
        with pytest.raises(ValueError, match="All subdivision counts must be at least 1"):
            basic_context.addBox(subdiv=int3(0, 1, 1))
        
        with pytest.raises(ValueError, match="All subdivision counts must be at least 1"):
            basic_context.addBox(subdiv=int3(1, 1, -1))


@pytest.mark.cross_platform  
class TestCompoundGeometryMockMode:
    """Test compound geometry methods in mock mode."""
    
    def test_addTile_mock_mode(self):
        """Test addTile behavior in mock mode or when functions not available."""
        if PlatformHelper.is_native_library_available():
            # If native libraries are available but compound geometry is not
            if not is_compound_geometry_available():
                context = Context()
                # Should raise NotImplementedError indicating functions not available
                with pytest.raises(NotImplementedError) as exc_info:
                    context.addTile()
                
                error_msg = str(exc_info.value)
                assert "Compound geometry functions not available" in error_msg
            else:
                pytest.skip("Compound geometry functions are available - cannot test unavailable scenario")
        else:
            context = Context()
            # Should raise RuntimeError indicating mock mode
            with pytest.raises(RuntimeError) as exc_info:
                context.addTile()
            
            # Error message should indicate mock mode
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in 
                      ["mock", "native", "library", "unavailable", "development"])
    
    def test_addSphere_mock_mode(self):
        """Test addSphere behavior in mock mode or when functions not available."""
        if PlatformHelper.is_native_library_available():
            # If native libraries are available but compound geometry is not
            if not is_compound_geometry_available():
                context = Context()
                # Should raise NotImplementedError indicating functions not available
                with pytest.raises(NotImplementedError) as exc_info:
                    context.addSphere()
                
                error_msg = str(exc_info.value)
                assert "Compound geometry functions not available" in error_msg
            else:
                pytest.skip("Compound geometry functions are available - cannot test unavailable scenario")
        else:
            context = Context()
            # Should raise RuntimeError indicating mock mode
            with pytest.raises(RuntimeError) as exc_info:
                context.addSphere()
            
            # Error message should indicate mock mode
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in 
                      ["mock", "native", "library", "unavailable", "development"])
    
    def test_addTube_mock_mode(self):
        """Test addTube behavior in mock mode or when functions not available."""
        if PlatformHelper.is_native_library_available():
            # If native libraries are available but compound geometry is not
            if not is_compound_geometry_available():
                context = Context()
                # Should raise NotImplementedError indicating functions not available
                with pytest.raises(NotImplementedError) as exc_info:
                    context.addTube([vec3(0, 0, 0), vec3(1, 0, 0)], 0.5)
                
                error_msg = str(exc_info.value)
                assert "Compound geometry functions not available" in error_msg
            else:
                pytest.skip("Compound geometry functions are available - cannot test unavailable scenario")
        else:
            context = Context()
            # Should raise RuntimeError indicating mock mode
            with pytest.raises(RuntimeError) as exc_info:
                context.addTube([vec3(0, 0, 0), vec3(1, 0, 0)], 0.5)
            
            # Error message should indicate mock mode
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in 
                      ["mock", "native", "library", "unavailable", "development"])
    
    def test_addBox_mock_mode(self):
        """Test addBox behavior in mock mode or when functions not available."""
        if PlatformHelper.is_native_library_available():
            # If native libraries are available but compound geometry is not
            if not is_compound_geometry_available():
                context = Context()
                # Should raise NotImplementedError indicating functions not available
                with pytest.raises(NotImplementedError) as exc_info:
                    context.addBox()
                
                error_msg = str(exc_info.value)
                assert "Compound geometry functions not available" in error_msg
            else:
                pytest.skip("Compound geometry functions are available - cannot test unavailable scenario")
        else:
            context = Context()
            # Should raise RuntimeError indicating mock mode
            with pytest.raises(RuntimeError) as exc_info:
                context.addBox()
            
            # Error message should indicate mock mode
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in 
                      ["mock", "native", "library", "unavailable", "development"])


@pytest.mark.native_only
@compound_geometry_available
class TestCompoundGeometryIntegration:
    """Test integration of compound geometry methods with existing Context functionality."""
    
    def test_mixed_geometry_creation(self, basic_context):
        """Test creating various compound geometries in the same context."""
        # Create a tile
        tile_uuids = basic_context.addTile(
            center=vec3(-2, 0, 0), subdiv=int2(2, 2), color=RGBcolor(1, 0, 0)
        )
        
        # Create a sphere
        sphere_uuids = basic_context.addSphere(
            center=vec3(0, 0, 0), radius=0.5, ndivs=8, color=RGBcolor(0, 1, 0)
        )
        
        # Create a tube
        tube_nodes = [vec3(2, 0, 0), vec3(2, 1, 0), vec3(2, 1, 1)]
        tube_uuids = basic_context.addTube(
            tube_nodes, 0.1, colors=RGBcolor(0, 0, 1)
        )
        
        # Create a box
        box_uuids = basic_context.addBox(
            center=vec3(0, 2, 0), size=vec3(1, 1, 1), color=RGBcolor(1, 1, 0)
        )
        
        # Verify all geometries are distinct
        all_uuids = tile_uuids + sphere_uuids + tube_uuids + box_uuids
        assert len(set(all_uuids)) == len(all_uuids), "All UUIDs should be unique"
        
        # Verify total count
        expected_total = len(tile_uuids) + len(sphere_uuids) + len(tube_uuids) + len(box_uuids)
        assert basic_context.getPrimitiveCount() == expected_total
        
        # Verify all UUIDs are in context
        context_uuids = basic_context.getAllUUIDs()
        for uuid in all_uuids:
            assert uuid in context_uuids
    
    def test_primitive_data_on_compound_geometry(self, basic_context):
        """Test setting primitive data on compound geometry primitives."""
        # Create a tile
        tile_uuids = basic_context.addTile(subdiv=int2(2, 2))
        
        # Set primitive data on all tile patches
        for i, uuid in enumerate(tile_uuids):
            basic_context.setPrimitiveDataInt(uuid, "tile_index", i)
            basic_context.setPrimitiveDataString(uuid, "geometry_type", "tile_patch")
        
        # Verify data was set correctly
        for i, uuid in enumerate(tile_uuids):
            assert basic_context.getPrimitiveData(uuid, "tile_index", int) == i
            assert basic_context.getPrimitiveData(uuid, "geometry_type", str) == "tile_patch"
        
        # Test bulk data retrieval
        indices_array = basic_context.getPrimitiveDataArray(tile_uuids, "tile_index")
        assert len(indices_array) == len(tile_uuids)
        assert list(indices_array) == list(range(len(tile_uuids)))
    
    def test_compound_geometry_with_existing_primitives(self, basic_context):
        """Test compound geometry creation alongside regular primitives."""
        # Add some regular primitives first
        patch_uuid = basic_context.addPatch(center=vec3(5, 5, 5), color=RGBcolor(0.5, 0.5, 0.5))
        triangle_uuid = basic_context.addTriangle(
            vec3(6, 0, 0), vec3(7, 0, 0), vec3(6.5, 1, 0), RGBcolor(0.8, 0.8, 0.8)
        )
        
        initial_count = basic_context.getPrimitiveCount()
        initial_uuids = set(basic_context.getAllUUIDs())
        
        # Add compound geometry
        sphere_uuids = basic_context.addSphere(center=vec3(10, 10, 10), ndivs=6)
        
        # Verify compound geometry doesn't interfere with existing primitives
        final_count = basic_context.getPrimitiveCount()
        final_uuids = set(basic_context.getAllUUIDs())
        
        assert final_count == initial_count + len(sphere_uuids)
        assert initial_uuids.issubset(final_uuids)
        
        # Verify original primitives still exist and have correct properties
        assert basic_context.getPrimitiveType(patch_uuid) == PrimitiveType.Patch
        assert basic_context.getPrimitiveType(triangle_uuid) == PrimitiveType.Triangle


@pytest.mark.native_only
@pytest.mark.slow
@compound_geometry_available
class TestCompoundGeometryPerformance:
    """Test performance characteristics of compound geometry methods."""
    
    def test_large_tile_creation(self, basic_context):
        """Test performance with large tile subdivisions."""
        # Create a large tile
        large_subdiv = int2(20, 20)  # 400 patches
        
        tile_uuids = basic_context.addTile(subdiv=large_subdiv)
        
        expected_count = TestCompoundGeometryValidation.calculate_expected_tile_count(large_subdiv)
        assert len(tile_uuids) == expected_count
        
        # Verify all patches exist and are valid
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, tile_uuids, PrimitiveType.Patch
        )
    
    def test_high_resolution_sphere(self, basic_context):
        """Test performance with high-resolution sphere."""
        # Create a high-resolution sphere
        high_ndivs = 25  # Creates many triangles
        
        sphere_uuids = basic_context.addSphere(ndivs=high_ndivs)
        
        # Should create a substantial number of triangles
        assert len(sphere_uuids) > 100
        
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, sphere_uuids, PrimitiveType.Triangle
        )
    
    def test_complex_tube_creation(self, basic_context):
        """Test performance with complex tube geometry."""
        # Create a complex tube with many nodes
        nodes = []
        for i in range(20):  # 20 nodes = 19 segments
            angle = i * 0.3
            x = np.cos(angle) * 2
            y = np.sin(angle) * 2  
            z = i * 0.1
            nodes.append(vec3(x, y, z))
        
        # Variable radii
        radii = [0.1 + 0.05 * np.sin(i * 0.5) for i in range(len(nodes))]
        
        tube_uuids = basic_context.addTube(nodes, radii, ndivs=8)
        
        # Should create substantial geometry
        assert len(tube_uuids) > 50
        
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, tube_uuids, PrimitiveType.Triangle
        )
    
    def test_highly_subdivided_box(self, basic_context):
        """Test performance with highly subdivided box."""
        # Create a highly subdivided box
        high_subdiv = int3(10, 8, 6)
        
        box_uuids = basic_context.addBox(subdiv=high_subdiv)
        
        expected_count = TestCompoundGeometryValidation.calculate_expected_box_patches(high_subdiv)
        assert len(box_uuids) == expected_count
        
        TestCompoundGeometryValidation.validate_primitive_list(
            basic_context, box_uuids, PrimitiveType.Patch
        )


@pytest.mark.cross_platform
class TestCompoundGeometryEdgeCases:
    """Test edge cases and error conditions for compound geometry methods."""
    
    @compound_geometry_available
    def test_extreme_parameter_values(self, basic_context):
        """Test compound geometry methods with extreme but valid parameter values."""
        if not PlatformHelper.is_native_library_available():
            pytest.skip("Requires native library for extreme parameter testing")
        
        # Very large coordinates
        large_center = vec3(1e6, 1e6, 1e6)
        
        # Should not crash with large coordinates
        tile_uuids = basic_context.addTile(center=large_center)
        assert len(tile_uuids) > 0
        
        basic_context.__exit__(None, None, None)
        
        # Very small but positive values
        with Context() as small_context:
            small_radius = 1e-6
            sphere_uuids = small_context.addSphere(radius=small_radius)
            assert len(sphere_uuids) > 0
    
    @compound_geometry_available
    def test_boundary_subdivision_values(self, basic_context):
        """Test compound geometry with boundary subdivision values."""
        # Minimum valid subdivisions
        min_tile = basic_context.addTile(subdiv=int2(1, 1))
        assert len(min_tile) == 1
        
        basic_context.__exit__(None, None, None)
        
        with Context() as new_context:
            min_box = new_context.addBox(subdiv=int3(1, 1, 1))
            assert len(min_box) == 6
    
    @compound_geometry_available
    def test_minimal_geometry_requirements(self, basic_context):
        """Test compound geometry with minimal valid parameters."""
        # Minimal sphere
        min_sphere = basic_context.addSphere(ndivs=3)  # Minimum allowed divisions
        assert len(min_sphere) > 0
        
        basic_context.__exit__(None, None, None)
        
        # Minimal tube
        with Context() as new_context:
            minimal_nodes = [vec3(0, 0, 0), vec3(1, 0, 0)]  # Minimum 2 nodes
            min_tube = new_context.addTube(minimal_nodes, 0.1, ndivs=3)  # Minimum divisions
            assert len(min_tube) > 0


@pytest.mark.cross_platform
class TestCompoundGeometryReturnValues:
    """Test return value formats and types for compound geometry methods."""
    
    @compound_geometry_available
    def test_return_value_types(self):
        """Test that all compound geometry methods return List[int]."""
        if not PlatformHelper.is_native_library_available():
            pytest.skip("Requires native library for return value testing")
        
        with Context() as context:
            # Test addTile return type
            tile_result = context.addTile()
            assert isinstance(tile_result, list)
            assert all(isinstance(uuid, int) for uuid in tile_result)
            
            # Test addSphere return type  
            sphere_result = context.addSphere()
            assert isinstance(sphere_result, list)
            assert all(isinstance(uuid, int) for uuid in sphere_result)
            
            # Test addTube return type
            nodes = [vec3(0, 0, 0), vec3(1, 0, 0)]
            tube_result = context.addTube(nodes, 0.5)
            assert isinstance(tube_result, list)
            assert all(isinstance(uuid, int) for uuid in tube_result)
            
            # Test addBox return type
            box_result = context.addBox()
            assert isinstance(box_result, list)
            assert all(isinstance(uuid, int) for uuid in box_result)
    
    @compound_geometry_available
    def test_uuid_uniqueness_across_methods(self):
        """Test that UUIDs are unique across different compound geometry methods."""
        if not PlatformHelper.is_native_library_available():
            pytest.skip("Requires native library for UUID uniqueness testing")
        
        with Context() as context:
            # Create geometry with different methods
            tile_uuids = context.addTile(subdiv=int2(2, 2))
            sphere_uuids = context.addSphere(ndivs=8)
            tube_uuids = context.addTube([vec3(0, 0, 0), vec3(1, 0, 0)], 0.1)
            box_uuids = context.addBox(subdiv=int3(2, 1, 1))
            
            # Collect all UUIDs
            all_compound_uuids = tile_uuids + sphere_uuids + tube_uuids + box_uuids
            
            # Verify all UUIDs are unique
            assert len(set(all_compound_uuids)) == len(all_compound_uuids)
            
            # Verify they match context's UUID list
            context_uuids = context.getAllUUIDs()
            assert set(all_compound_uuids) == set(context_uuids)
    
    @compound_geometry_available
    def test_empty_geometry_handling(self):
        """Test handling of cases that might produce empty geometry.""" 
        if not PlatformHelper.is_native_library_available():
            pytest.skip("Requires native library for empty geometry testing")
        
        with Context() as context:
            # All valid compound geometry methods should produce at least some primitives
            # This test ensures no method returns an empty list for valid parameters
            
            tile_uuids = context.addTile(subdiv=int2(1, 1))
            assert len(tile_uuids) > 0
            
            sphere_uuids = context.addSphere(ndivs=3)  # Minimum divisions
            assert len(sphere_uuids) > 0
            
            tube_uuids = context.addTube([vec3(0, 0, 0), vec3(0.1, 0, 0)], 0.01, ndivs=3)
            assert len(tube_uuids) > 0
            
            box_uuids = context.addBox(subdiv=int3(1, 1, 1))
            assert len(box_uuids) > 0