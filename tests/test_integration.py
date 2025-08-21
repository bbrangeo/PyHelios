"""
Integration tests for PyHelios.

These tests verify end-to-end workflows and integration between PyHelios components
and the underlying Helios C++ library.
"""

import pytest
import time
from pyhelios import Context, WeberPennTree, WPTType, DataTypes
from pyhelios.wrappers.DataTypes import PrimitiveType
from tests.test_utils import GeometryValidator, PerformanceMeasure, PlatformHelper


@pytest.mark.integration
@pytest.mark.native_only
class TestBasicWorkflows:
    """Test basic PyHelios workflows."""
    
    def test_context_patch_workflow(self, basic_context):
        """Test complete patch creation and query workflow."""
        # Create multiple patches with different properties
        patch_data = [
            {
                'center': DataTypes.vec3(0, 0, 0),
                'size': DataTypes.vec2(1, 1),
                'color': DataTypes.RGBcolor(1, 0, 0)  # Red
            },
            {
                'center': DataTypes.vec3(5, 0, 0),
                'size': DataTypes.vec2(2, 1),
                'color': DataTypes.RGBcolor(0, 1, 0)  # Green
            },
            {
                'center': DataTypes.vec3(0, 5, 0),
                'size': DataTypes.vec2(1, 2),
                'color': DataTypes.RGBcolor(0, 0, 1)  # Blue
            }
        ]
        
        patch_uuids = []
        for patch in patch_data:
            uuid = basic_context.addPatch(
                center=patch['center'],
                size=patch['size'],
                color=patch['color']
            )
            patch_uuids.append(uuid)
        
        # Verify all patches were created
        assert basic_context.getPrimitiveCount() == len(patch_data)
        assert len(basic_context.getAllUUIDs()) == len(patch_data)
        
        # Verify each patch has correct properties
        for i, (uuid, expected) in enumerate(zip(patch_uuids, patch_data)):
            # Check type
            assert basic_context.getPrimitiveType(uuid) == PrimitiveType.Patch
            
            # Check color
            actual_color = basic_context.getPrimitiveColor(uuid)
            assert abs(actual_color.r - expected['color'].r) < 1e-6
            assert abs(actual_color.g - expected['color'].g) < 1e-6
            assert abs(actual_color.b - expected['color'].b) < 1e-6
            
            # Check area
            expected_area = expected['size'].x * expected['size'].y
            actual_area = basic_context.getPrimitiveArea(uuid)
            assert abs(actual_area - expected_area) < 1e-6
            
            # Check vertices
            vertices = basic_context.getPrimitiveVertices(uuid)
            assert len(vertices) == 4
    
    def test_tree_generation_workflow(self, basic_context):
        """Test complete tree generation workflow."""
        with WeberPennTree(basic_context) as wpt:
            # Configure tree parameters
            wpt.setBranchRecursionLevel(3)
            wpt.setTrunkSegmentResolution(4)
            wpt.setBranchSegmentResolution(2)
            wpt.setLeafSubdivisions(2, 2)
            
            # Generate different tree types
            tree_types = [WPTType.LEMON, WPTType.APPLE, WPTType.OLIVE]
            tree_data = []
            
            for i, tree_type in enumerate(tree_types):
                origin = DataTypes.vec3(i * 20, 0, 0)  # Space trees apart
                tree_id = wpt.buildTree(tree_type, origin=origin)
                
                # Get tree structure
                trunk_uuids = wpt.getTrunkUUIDs(tree_id)
                branch_uuids = wpt.getBranchUUIDs(tree_id)
                leaf_uuids = wpt.getLeafUUIDs(tree_id)
                all_uuids = wpt.getAllUUIDs(tree_id)
                
                tree_info = {
                    'tree_id': tree_id,
                    'type': tree_type,
                    'origin': origin,
                    'trunk_count': len(trunk_uuids),
                    'branch_count': len(branch_uuids),
                    'leaf_count': len(leaf_uuids),
                    'total_count': len(all_uuids)
                }
                tree_data.append(tree_info)
                
                # Validate tree structure
                stats = GeometryValidator.validate_tree_structure(wpt, tree_id)
                assert stats['valid'], f"Tree validation failed for {tree_type}: {stats.get('error')}"
            
            # Verify all trees are different
            tree_ids = [t['tree_id'] for t in tree_data]
            assert len(set(tree_ids)) == len(tree_types), "Tree IDs should be unique"
            
            # Verify trees have reasonable structure
            for tree in tree_data:
                assert tree['trunk_count'] > 0, f"Tree {tree['type']} should have trunk segments"
                assert tree['leaf_count'] > 0, f"Tree {tree['type']} should have leaves"
                assert tree['total_count'] > tree['trunk_count'], f"Tree {tree['type']} should have more than just trunk"
        
        # Context should now contain all tree primitives
        total_expected_primitives = sum(t['total_count'] for t in tree_data)
        assert basic_context.getPrimitiveCount() == total_expected_primitives
    
    def test_mixed_geometry_workflow(self, basic_context):
        """Test workflow combining patches and trees."""
        # First add some patches
        patch_uuids = []
        for i in range(3):
            center = DataTypes.vec3(i * 2, 0, 0)
            size = DataTypes.vec2(0.5, 0.5)
            color = DataTypes.RGBcolor(0.5, 0.5, 0.5)
            uuid = basic_context.addPatch(center=center, size=size, color=color)
            patch_uuids.append(uuid)
        
        initial_primitive_count = basic_context.getPrimitiveCount()
        assert initial_primitive_count == 3
        
        # Then add trees
        with WeberPennTree(basic_context) as wpt:
            wpt.setBranchRecursionLevel(2)
            
            tree_id1 = wpt.buildTree(WPTType.LEMON, origin=DataTypes.vec3(10, 0, 0))
            tree_id2 = wpt.buildTree(WPTType.APPLE, origin=DataTypes.vec3(30, 0, 0))
            
            tree1_uuids = wpt.getAllUUIDs(tree_id1)
            tree2_uuids = wpt.getAllUUIDs(tree_id2)
        
        # Verify final state
        final_primitive_count = basic_context.getPrimitiveCount()
        expected_count = initial_primitive_count + len(tree1_uuids) + len(tree2_uuids)
        assert final_primitive_count == expected_count
        
        # Verify all UUIDs are accounted for and unique
        all_context_uuids = basic_context.getAllUUIDs()
        assert len(all_context_uuids) == expected_count
        assert len(set(all_context_uuids)) == expected_count  # All unique


@pytest.mark.integration
@pytest.mark.native_only
class TestContextIntegration:
    """Test Context integration with Helios core library."""
    
    def test_context_primitive_consistency(self, basic_context):
        """Test that Context primitive operations are consistent."""
        # Add a variety of primitives
        primitives = []
        
        # Different patch sizes
        for size_x, size_y in [(1, 1), (2, 1), (1, 2), (3, 3)]:
            center = DataTypes.vec3(size_x * 3, size_y * 3, 0)
            size = DataTypes.vec2(size_x, size_y)
            color = DataTypes.RGBcolor(size_x/3.0, size_y/3.0, 0.5)
            
            uuid = basic_context.addPatch(center=center, size=size, color=color)
            primitives.append({
                'uuid': uuid,
                'center': center,
                'size': size,
                'color': color,
                'expected_area': size_x * size_y
            })
        
        # Verify consistency across all operations
        assert basic_context.getPrimitiveCount() == len(primitives)
        
        context_uuids = basic_context.getAllUUIDs()
        primitive_uuids = [p['uuid'] for p in primitives]
        
        assert set(context_uuids) == set(primitive_uuids)
        
        # Verify each primitive individually
        for prim in primitives:
            uuid = prim['uuid']
            
            # Type should be patch
            assert basic_context.getPrimitiveType(uuid) == PrimitiveType.Patch
            
            # Area should match expectation
            actual_area = basic_context.getPrimitiveArea(uuid)
            assert abs(actual_area - prim['expected_area']) < 1e-6
            
            # Color should match
            actual_color = basic_context.getPrimitiveColor(uuid)
            expected_color = prim['color']
            assert abs(actual_color.r - expected_color.r) < 1e-6
            assert abs(actual_color.g - expected_color.g) < 1e-6
            assert abs(actual_color.b - expected_color.b) < 1e-6
            
            # Should have 4 vertices (rectangular patch)
            vertices = basic_context.getPrimitiveVertices(uuid)
            assert len(vertices) == 4
            
            # Normal should be unit length
            normal = basic_context.getPrimitiveNormal(uuid)
            length = (normal.x**2 + normal.y**2 + normal.z**2)**0.5
            assert abs(length - 1.0) < 1e-6
    
    def test_geometry_state_integration(self, basic_context):
        """Test geometry state management integration."""
        # Initially clean
        assert not basic_context.isGeometryDirty()
        
        # Adding primitives might make geometry dirty (implementation dependent)
        basic_context.addPatch()
        
        # Manual state management should work
        basic_context.markGeometryDirty()
        assert basic_context.isGeometryDirty()
        
        basic_context.markGeometryClean()
        assert not basic_context.isGeometryDirty()


@pytest.mark.integration
@pytest.mark.native_only
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance aspects of PyHelios integration."""
    
    def test_patch_creation_performance(self, basic_context):
        """Test performance of patch creation."""
        perf = PerformanceMeasure()
        
        num_patches = 1000
        
        def create_patches():
            patch_uuids = []
            for i in range(num_patches):
                center = DataTypes.vec3(i % 100, i // 100, 0)
                size = DataTypes.vec2(1, 1)
                color = DataTypes.RGBcolor(0.5, 0.5, 0.5)
                uuid = basic_context.addPatch(center=center, size=size, color=color)
                patch_uuids.append(uuid)
            return patch_uuids
        
        patch_uuids, creation_time = perf.measure_operation("patch_creation", create_patches)
        
        assert len(patch_uuids) == num_patches
        assert basic_context.getPrimitiveCount() == num_patches
        
        # Performance should be reasonable (less than 10 seconds for 1000 patches)
        assert creation_time < 10.0, f"Patch creation took too long: {creation_time:.2f}s"
        
        if creation_time > 0:
            print(f"Created {num_patches} patches in {creation_time:.3f}s ({num_patches/creation_time:.1f} patches/s)")
        else:
            print(f"Created {num_patches} patches in <0.001s (very fast)")
    
    def test_tree_generation_performance(self, basic_context):
        """Test performance of tree generation."""
        if not PlatformHelper.is_dll_available():
            pytest.skip("Requires DLL for performance testing")
        
        perf = PerformanceMeasure()
        
        with WeberPennTree(basic_context) as wpt:
            # Configure for moderate complexity
            wpt.setBranchRecursionLevel(3)
            wpt.setTrunkSegmentResolution(3)
            wpt.setBranchSegmentResolution(2)
            wpt.setLeafSubdivisions(2, 2)
            
            def generate_trees():
                tree_ids = []
                tree_types = [WPTType.LEMON, WPTType.APPLE, WPTType.OLIVE, WPTType.ALMOND, WPTType.PEACH]
                
                for i, tree_type in enumerate(tree_types):
                    origin = DataTypes.vec3(i * 25, 0, 0)
                    tree_id = wpt.buildTree(tree_type, origin=origin)
                    tree_ids.append(tree_id)
                
                return tree_ids
            
            tree_ids, generation_time = perf.measure_operation("tree_generation", generate_trees)
            
            assert len(tree_ids) == 5
            
            # Verify trees were created properly
            total_primitives = 0
            for tree_id in tree_ids:
                stats = GeometryValidator.validate_tree_structure(wpt, tree_id)
                assert stats['valid']
                total_primitives += stats['total_count']
            
            assert total_primitives > 0
            
            # Performance should be reasonable
            assert generation_time < 30.0, f"Tree generation took too long: {generation_time:.2f}s"
            
            print(f"Generated 5 trees with {total_primitives} total primitives in {generation_time:.3f}s")


@pytest.mark.integration
@pytest.mark.native_only
class TestErrorHandlingIntegration:
    """Test error handling in integrated scenarios."""
    
    def test_context_recovery_after_errors(self, basic_context):
        """Test that Context can recover after errors."""
        # Add some valid primitives first
        uuid1 = basic_context.addPatch(center=DataTypes.vec3(0, 0, 0))
        assert basic_context.getPrimitiveCount() == 1
        
        # Try to query invalid UUID (should handle gracefully)
        try:
            basic_context.getPrimitiveType(99999)
        except Exception:
            pass  # Expected for invalid UUID
        
        # Context should still be functional
        uuid2 = basic_context.addPatch(center=DataTypes.vec3(1, 1, 1))
        assert basic_context.getPrimitiveCount() == 2
        
        # Valid queries should still work
        assert basic_context.getPrimitiveType(uuid1) == PrimitiveType.Patch
        assert basic_context.getPrimitiveType(uuid2) == PrimitiveType.Patch
    
    def test_wpt_recovery_after_errors(self, basic_context):
        """Test that WeberPennTree can recover after errors."""
        with WeberPennTree(basic_context) as wpt:
            # Generate valid tree first
            tree_id1 = wpt.buildTree(WPTType.LEMON)
            stats1 = GeometryValidator.validate_tree_structure(wpt, tree_id1)
            assert stats1['valid']
            
            # Try to query invalid tree ID
            try:
                invalid_uuids = wpt.get_all_uuids(99999)
                # Should return empty list or handle gracefully
                assert isinstance(invalid_uuids, list)
            except Exception:
                pass  # Some implementations might raise exceptions
            
            # WeberPennTree should still be functional
            tree_id2 = wpt.buildTree(WPTType.APPLE, origin=DataTypes.vec3(10, 0, 0))
            stats2 = GeometryValidator.validate_tree_structure(wpt, tree_id2)
            assert stats2['valid']
    
    def test_resource_cleanup_on_errors(self):
        """Test proper resource cleanup when errors occur."""
        if not PlatformHelper.is_dll_available():
            pytest.skip("Requires DLL for resource testing")
        
        # This test ensures that even if exceptions occur,
        # context managers properly clean up resources
        
        context_created = False
        wpt_created = False
        
        try:
            with Context() as ctx:
                context_created = True
                ctx.addPatch()  # Should work
                
                with WeberPennTree(ctx) as wpt:
                    wpt_created = True
                    wpt.buildTree(WPTType.LEMON)  # Should work
                    
                    # Force an error condition
                    raise ValueError("Simulated error")
                    
        except ValueError:
            # Expected error
            pass
        
        # Resources should have been cleaned up properly
        # (This is hard to test directly, but at least verify the code path executed)
        assert context_created
        assert wpt_created