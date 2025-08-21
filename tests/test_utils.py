"""
Utility functions and helpers for PyHelios tests.
"""

import os
import platform
from typing import Dict, Any, List
import pyhelios
from pyhelios import DataTypes


class DataManager:
    """Manager for test data files and expected outputs."""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.test_data_path = os.path.join(base_path, 'test_data')
        self.expected_outputs_path = os.path.join(base_path, 'expected_outputs')
    
    def get_test_data_file(self, filename: str) -> str:
        """Get path to a test data file."""
        return os.path.join(self.test_data_path, filename)
    
    def get_expected_output_file(self, filename: str) -> str:
        """Get path to an expected output file."""
        return os.path.join(self.expected_outputs_path, filename)
    
    def save_expected_output(self, filename: str, data: Any) -> None:
        """Save expected output data for regression testing."""
        os.makedirs(self.expected_outputs_path, exist_ok=True)
        filepath = self.get_expected_output_file(filename)
        # Implementation depends on data type - could be JSON, pickle, etc.
        # For now, just create a placeholder
        with open(filepath, 'w') as f:
            f.write(str(data))


class GeometryValidator:
    """Validator for geometric operations and results."""
    
    @staticmethod
    def validate_patch_properties(context, patch_uuid: int, expected_center: DataTypes.vec3, 
                                expected_size: DataTypes.vec2, expected_color: DataTypes.RGBcolor,
                                tolerance: float = 1e-6) -> bool:
        """Validate that a patch has expected properties."""
        try:
            # Check primitive type  
            from pyhelios.wrappers.DataTypes import PrimitiveType
            assert context.getPrimitiveType(patch_uuid) == PrimitiveType.Patch
            
            # Check color
            actual_color = context.getPrimitiveColor(patch_uuid)
            assert abs(actual_color.r - expected_color.r) < tolerance
            assert abs(actual_color.g - expected_color.g) < tolerance
            assert abs(actual_color.b - expected_color.b) < tolerance
            
            # Check area (for unit size patch, area should be size.x * size.y)
            expected_area = expected_size.x * expected_size.y
            actual_area = context.getPrimitiveArea(patch_uuid)
            assert abs(actual_area - expected_area) < tolerance
            
            # Check vertices count (patch should have 4 vertices)
            vertices = context.getPrimitiveVertices(patch_uuid)
            assert len(vertices) == 4
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def validate_tree_structure(wpt, tree_id: int) -> Dict[str, Any]:
        """Validate basic tree structure and return statistics."""
        stats = {}
        
        try:
            stats['trunk_uuids'] = wpt.getTrunkUUIDs(tree_id)
            stats['branch_uuids'] = wpt.getBranchUUIDs(tree_id)
            stats['leaf_uuids'] = wpt.getLeafUUIDs(tree_id)
            stats['all_uuids'] = wpt.getAllUUIDs(tree_id)
            
            stats['trunk_count'] = len(stats['trunk_uuids'])
            stats['branch_count'] = len(stats['branch_uuids'])
            stats['leaf_count'] = len(stats['leaf_uuids'])
            stats['total_count'] = len(stats['all_uuids'])
            
            # Basic validation
            assert stats['trunk_count'] > 0, "Tree should have at least one trunk segment"
            assert stats['total_count'] == (stats['trunk_count'] + stats['branch_count'] + stats['leaf_count']), \
                "Total UUID count should equal sum of components"
            
            # Check for UUID overlaps
            all_component_uuids = set(stats['trunk_uuids'] + stats['branch_uuids'] + stats['leaf_uuids'])
            assert len(all_component_uuids) == stats['total_count'], "UUIDs should not overlap between components"
            
            stats['valid'] = True
            
        except Exception as e:
            stats['valid'] = False
            stats['error'] = str(e)
        
        return stats


class PerformanceMeasure:
    """Helper for measuring test performance and detecting regressions."""
    
    def __init__(self):
        self.measurements = {}
    
    def measure_operation(self, name: str, operation_func, *args, **kwargs):
        """Measure execution time of an operation."""
        import time
        
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.measurements[name] = execution_time
        
        return result, execution_time
    
    def get_measurements(self) -> Dict[str, float]:
        """Get all performance measurements."""
        return self.measurements.copy()


class PlatformHelper:
    """Helper for platform-specific test operations."""
    
    @staticmethod
    def get_platform_name() -> str:
        """Get current platform name."""
        return platform.system()
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == 'Windows'
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system() == 'Darwin'
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == 'Linux'
    
    @staticmethod
    def is_native_library_available() -> bool:
        """Check if native Helios library is available."""
        try:
            from pyhelios.plugins import is_native_library_available
            return is_native_library_available()
        except:
            return False
    
    @staticmethod
    def is_dll_available() -> bool:
        """Check if native Helios library is available (legacy alias)."""
        return PlatformHelper.is_native_library_available()
    
    @staticmethod
    def skip_if_no_native_library():
        """Decorator to skip tests if native library is not available."""
        import pytest
        return pytest.mark.skipif(
            not PlatformHelper.is_native_library_available(),
            reason="Native Helios library not available"
        )
    
    @staticmethod
    def skip_if_not_windows():
        """Decorator to skip tests if not on Windows."""
        import pytest
        return pytest.mark.skipif(
            not PlatformHelper.is_windows(),
            reason="Test requires Windows platform"
        )
    
    @staticmethod
    def skip_if_not_macos():
        """Decorator to skip tests if not on macOS."""
        import pytest
        return pytest.mark.skipif(
            not PlatformHelper.is_macos(),
            reason="Test requires macOS platform"
        )
    
    @staticmethod
    def skip_if_not_linux():
        """Decorator to skip tests if not on Linux."""
        import pytest
        return pytest.mark.skipif(
            not PlatformHelper.is_linux(),
            reason="Test requires Linux platform"
        )
    
    @staticmethod
    def requires_native():
        """Decorator to mark tests that require native library."""
        import pytest
        return pytest.mark.native_only
    
    @staticmethod
    def cross_platform():
        """Decorator to mark tests that work on all platforms."""
        import pytest
        return pytest.mark.cross_platform


# Common test data generators
def generate_test_vectors():
    """Generate common test vectors for DataTypes testing."""
    return {
        'vec2_samples': [
            DataTypes.vec2(0, 0),
            DataTypes.vec2(1, 1),
            DataTypes.vec2(-1, -1),
            DataTypes.vec2(3.14, 2.71),
        ],
        'vec3_samples': [
            DataTypes.vec3(0, 0, 0),
            DataTypes.vec3(1, 1, 1),
            DataTypes.vec3(-1, -1, -1),
            DataTypes.vec3(1, 2, 3),
            DataTypes.vec3(3.14, 2.71, 1.41),
        ],
        'color_samples': [
            DataTypes.RGBcolor(0, 0, 0),
            DataTypes.RGBcolor(1, 1, 1),
            DataTypes.RGBcolor(1, 0, 0),
            DataTypes.RGBcolor(0, 1, 0),
            DataTypes.RGBcolor(0, 0, 1),
            DataTypes.RGBcolor(0.5, 0.5, 0.5),
        ],
    }


def generate_patch_test_cases():
    """Generate test cases for patch creation."""
    return [
        {
            'name': 'default_patch',
            'center': DataTypes.vec3(0, 0, 0),
            'size': DataTypes.vec2(1, 1),
            'color': DataTypes.RGBcolor(1, 1, 1),
        },
        {
            'name': 'colored_patch',
            'center': DataTypes.vec3(2, 3, 4),
            'size': DataTypes.vec2(2, 3),
            'color': DataTypes.RGBcolor(0.5, 0.7, 0.2),
        },
        {
            'name': 'small_patch',
            'center': DataTypes.vec3(0, 0, 1),
            'size': DataTypes.vec2(0.1, 0.1),
            'color': DataTypes.RGBcolor(0, 0, 1),
        },
    ]