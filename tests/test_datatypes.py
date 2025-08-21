"""
Tests for PyHelios DataTypes module.

These tests verify the ctypes-based data structures used for Helios interop.
"""

import pytest
import math
from pyhelios import DataTypes
from tests.conftest import assert_vec3_equal, assert_vec2_equal, assert_color_equal
from tests.test_utils import generate_test_vectors


class TestVec2:
    """Test Vec2 data type."""
    
    def test_vec2_creation_default(self):
        """Test Vec2 creation with default values."""
        v = DataTypes.vec2()
        assert v.x == 0.0
        assert v.y == 0.0
    
    def test_vec2_creation_with_values(self):
        """Test Vec2 creation with specific values."""
        v = DataTypes.vec2(3.14, 2.71)
        assert v.x == pytest.approx(3.14)
        assert v.y == pytest.approx(2.71)
    
    def test_vec2_to_list(self):
        """Test Vec2 to_list conversion."""
        v = DataTypes.vec2(1.5, -2.5)
        result = v.to_list()
        assert result == [1.5, -2.5]
        assert isinstance(result, list)
    
    def test_vec2_from_list(self):
        """Test Vec2 from_list method."""
        v = DataTypes.vec2()
        v.from_list([4.0, 5.0])
        assert v.x == 4.0
        assert v.y == 5.0
    
    def test_vec2_string_representation(self):
        """Test Vec2 string representations."""
        v = DataTypes.vec2(1, 2)
        assert str(v) == "vec2(1.0, 2.0)"
        assert repr(v) == "vec2(1.0, 2.0)"
    
    @pytest.mark.parametrize("x,y", [
        (0, 0),
        (1, 1),
        (-1, -1),
        (3.14159, 2.71828),
        (float('inf'), float('-inf')),
    ])
    def test_vec2_various_values(self, x, y):
        """Test Vec2 with various values."""
        v = DataTypes.vec2(x, y)
        if math.isfinite(x):
            assert v.x == pytest.approx(x, rel=1e-6)
        else:
            assert v.x == x
        if math.isfinite(y):
            assert v.y == pytest.approx(y, rel=1e-6)
        else:
            assert v.y == y


class TestVec3:
    """Test Vec3 data type."""
    
    def test_vec3_creation_default(self):
        """Test Vec3 creation with default values."""
        v = DataTypes.vec3()
        assert v.x == 0.0
        assert v.y == 0.0
        assert v.z == 0.0
    
    def test_vec3_creation_with_values(self):
        """Test Vec3 creation with specific values."""
        v = DataTypes.vec3(1.0, 2.0, 3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0
    
    def test_vec3_to_list(self):
        """Test Vec3 to_list conversion."""
        v = DataTypes.vec3(1.5, -2.5, 3.5)
        result = v.to_list()
        assert result == [1.5, -2.5, 3.5]
        assert isinstance(result, list)
    
    def test_vec3_to_tuple(self):
        """Test Vec3 to_tuple conversion."""
        v = DataTypes.vec3(1.5, -2.5, 3.5)
        result = v.to_tuple()
        assert result == (1.5, -2.5, 3.5)
        assert isinstance(result, tuple)
    
    def test_vec3_from_list(self):
        """Test Vec3 from_list method."""
        v = DataTypes.vec3()
        v.from_list([4.0, 5.0, 6.0])
        assert v.x == 4.0
        assert v.y == 5.0
        assert v.z == 6.0
    
    def test_vec3_string_representation(self):
        """Test Vec3 string representations."""
        v = DataTypes.vec3(1, 2, 3)
        assert str(v) == "vec3(1.0, 2.0, 3.0)"
        assert repr(v) == "vec3(1.0, 2.0, 3.0)"


class TestVec4:
    """Test Vec4 data type."""
    
    def test_vec4_creation_default(self):
        """Test Vec4 creation with default values."""
        v = DataTypes.vec4()
        assert v.x == 0.0
        assert v.y == 0.0
        assert v.z == 0.0
        assert v.w == 0.0
    
    def test_vec4_creation_with_values(self):
        """Test Vec4 creation with specific values."""
        v = DataTypes.vec4(1.0, 2.0, 3.0, 4.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0
        assert v.w == 4.0
    
    def test_vec4_to_list(self):
        """Test Vec4 to_list conversion."""
        v = DataTypes.vec4(1.5, -2.5, 3.5, -4.5)
        result = v.to_list()
        assert result == [1.5, -2.5, 3.5, -4.5]
        assert isinstance(result, list)


class TestRGBcolor:
    """Test RGBcolor data type."""
    
    def test_rgb_creation_default(self):
        """Test RGBcolor creation with default values."""
        c = DataTypes.RGBcolor()
        assert c.r == 0.0
        assert c.g == 0.0
        assert c.b == 0.0
    
    def test_rgb_creation_with_values(self):
        """Test RGBcolor creation with specific values."""
        c = DataTypes.RGBcolor(0.5, 0.7, 0.2)
        assert c.r == pytest.approx(0.5)
        assert c.g == pytest.approx(0.7)
        assert c.b == pytest.approx(0.2)
    
    def test_rgb_to_list(self):
        """Test RGBcolor to_list conversion."""
        c = DataTypes.RGBcolor(0.1, 0.5, 0.9)
        result = c.to_list()
        assert result == pytest.approx([0.1, 0.5, 0.9], rel=1e-6)
        assert isinstance(result, list)
    
    def test_rgb_from_list(self):
        """Test RGBcolor from_list method."""
        c = DataTypes.RGBcolor()
        c.from_list([0.3, 0.6, 0.9])
        assert c.r == pytest.approx(0.3)
        assert c.g == pytest.approx(0.6)
        assert c.b == pytest.approx(0.9)
    
    def test_rgb_string_representation(self):
        """Test RGBcolor string representations."""
        c = DataTypes.RGBcolor(1, 0.5, 0)
        assert str(c) == "RGBcolor(1.0, 0.5, 0.0)"
        assert repr(c) == "RGBcolor(1.0, 0.5, 0.0)"
    
    @pytest.mark.parametrize("r,g,b", [
        (0, 0, 0),      # Black
        (1, 1, 1),      # White
        (1, 0, 0),      # Red
        (0, 1, 0),      # Green
        (0, 0, 1),      # Blue
        (0.5, 0.5, 0.5), # Gray
    ])
    def test_rgb_common_colors(self, r, g, b):
        """Test RGBcolor with common color values."""
        c = DataTypes.RGBcolor(r, g, b)
        assert c.r == r
        assert c.g == g
        assert c.b == b


class TestRGBAcolor:
    """Test RGBAcolor data type."""
    
    def test_rgba_creation_default(self):
        """Test RGBAcolor creation with default values."""
        c = DataTypes.RGBAcolor()
        assert c.r == 0.0
        assert c.g == 0.0
        assert c.b == 0.0
        assert c.a == 0.0
    
    def test_rgba_creation_with_values(self):
        """Test RGBAcolor creation with specific values."""
        c = DataTypes.RGBAcolor(0.5, 0.7, 0.2, 0.8)
        assert c.r == pytest.approx(0.5)
        assert c.g == pytest.approx(0.7)
        assert c.b == pytest.approx(0.2)
        assert c.a == pytest.approx(0.8)
    
    def test_rgba_from_list(self):
        """Test RGBAcolor from_list method."""
        c = DataTypes.RGBAcolor()
        c.from_list([0.3, 0.6, 0.9, 0.7])
        assert c.r == pytest.approx(0.3)
        assert c.g == pytest.approx(0.6)
        assert c.b == pytest.approx(0.9)
        assert c.a == pytest.approx(0.7)


class TestSphericalCoord:
    """Test SphericalCoord data type."""
    
    def test_spherical_creation_default(self):
        """Test SphericalCoord creation with default values."""
        s = DataTypes.SphericalCoord()
        assert s.radius == 1.0  # Default radius is 1.0, not 0.0
        assert s.elevation == 0.0
        assert pytest.approx(s.zenith) == pytest.approx(1.5707963705062866)  # π/2
        assert s.azimuth == 0.0
    
    def test_spherical_creation_with_values(self):
        """Test SphericalCoord creation with specific values."""
        s = DataTypes.SphericalCoord(5.0, 30.0, 45.0)
        assert s.radius == 5.0
        assert s.elevation == 30.0
        # zenith is computed as π/2 - elevation = π/2 - 30.0 ≈ 0.5708 radians
        import math
        expected_zenith = 0.5 * math.pi - 30.0
        assert abs(s.zenith - expected_zenith) < 0.01
        assert s.azimuth == 45.0
    
    def test_spherical_to_list(self):
        """Test SphericalCoord to_list conversion."""
        s = DataTypes.SphericalCoord(1.0, 2.0, 3.0)
        result = s.to_list()
        # Result should be [radius, elevation, zenith, azimuth]
        # zenith = π/2 - elevation = π/2 - 2.0
        import math
        expected_zenith = 0.5 * math.pi - 2.0
        expected_result = [1.0, 2.0, expected_zenith, 3.0]
        assert len(result) == 4
        assert result[0] == 1.0  # radius
        assert result[1] == 2.0  # elevation
        assert abs(result[2] - expected_zenith) < 0.01  # zenith
        assert result[3] == 3.0  # azimuth
        assert isinstance(result, list)
    
    def test_spherical_from_list(self):
        """Test SphericalCoord from_list method."""
        s = DataTypes.SphericalCoord()
        s.from_list([10.0, 45.0, 30.0, 180.0])
        assert s.radius == 10.0
        assert s.elevation == 45.0
        assert s.zenith == 30.0
        assert s.azimuth == 180.0
    
    def test_spherical_string_representation(self):
        """Test SphericalCoord string representations."""
        s = DataTypes.SphericalCoord(1, 2, 3)  # radius, elevation, azimuth
        # Just test that the string representation contains the expected values, 
        # but don't do exact floating point comparison
        str_repr = str(s)
        assert str_repr.startswith("SphericalCoord(")
        assert "1.0" in str_repr
        assert "2.0" in str_repr
        assert "3.0" in str_repr
        
        repr_str = repr(s)
        assert repr_str.startswith("SphericalCoord(")
        assert "1.0" in repr_str
        assert "2.0" in repr_str
        assert "3.0" in repr_str


class TestIntegerTypes:
    """Test integer vector types (Int2, Int3, Int4)."""
    
    def test_int2_creation(self):
        """Test Int2 creation and methods."""
        i = DataTypes.int2(5, 10)
        assert i.x == 5
        assert i.y == 10
        assert i.to_list() == [5, 10]
    
    def test_int3_creation(self):
        """Test Int3 creation and methods."""
        i = DataTypes.int3(1, 2, 3)
        assert i.x == 1
        assert i.y == 2
        assert i.z == 3
        assert i.to_list() == [1, 2, 3]
    
    def test_int4_creation(self):
        """Test Int4 creation and methods."""
        i = DataTypes.int4(10, 20, 30, 40)
        assert i.x == 10
        assert i.y == 20
        assert i.z == 30
        assert i.w == 40
        assert i.to_list() == [10, 20, 30, 40]


class TestDataTypeInteroperability:
    """Test interoperability and edge cases for data types."""
    
    def test_vec3_precision(self):
        """Test Vec3 precision with small numbers."""
        v = DataTypes.vec3(1e-10, 1e-10, 1e-10)
        assert v.x == pytest.approx(1e-10)
        assert v.y == pytest.approx(1e-10)
        assert v.z == pytest.approx(1e-10)
    
    def test_color_clamping_behavior(self):
        """Test behavior with out-of-range color values."""
        # Note: This tests current behavior, not necessarily desired behavior
        c = DataTypes.RGBcolor(-0.5, 1.5, 0.5)
        # The values should be stored as-is (no automatic clamping)
        assert c.r == -0.5
        assert c.g == 1.5
        assert c.b == 0.5
    
    @pytest.mark.unit
    def test_list_conversion_roundtrip(self):
        """Test that list conversion is bidirectional."""
        original_vec3 = DataTypes.vec3(1.5, 2.5, 3.5)
        vec_list = original_vec3.to_list()
        
        new_vec3 = DataTypes.vec3()
        new_vec3.from_list(vec_list)
        
        assert_vec3_equal(original_vec3, new_vec3)
    
    def test_zero_vectors(self):
        """Test zero vectors have expected properties."""
        vec2_zero = DataTypes.vec2(0, 0)
        vec3_zero = DataTypes.vec3(0, 0, 0)
        
        assert all(x == 0 for x in vec2_zero.to_list())
        assert all(x == 0 for x in vec3_zero.to_list())