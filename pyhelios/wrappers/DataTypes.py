import ctypes
from typing import Any, List
from enum import IntEnum


class PrimitiveType(IntEnum):
    """Helios primitive type enumeration."""
    Patch = 0
    Triangle = 1
    Disk = 2
    Tile = 3
    Sphere = 4
    Tube = 5
    Box = 6
    Cone = 7
    Polymesh = 8

class int2(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int32), ('y', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'int2({self.x}, {self.y})'
    
    def __str__(self) -> str:
        return f'int2({self.x}, {self.y})'
    
    def __init__(self, x:int=0, y:int=0):
        self.x = x
        self.y = y

    def from_list(self, input_list:List[int]):
        self.x = input_list[0]
        self.y = input_list[1]

    def to_list(self) -> List[int]:
        return [self.x, self.y]

    
    
class int3(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int32), ('y', ctypes.c_int32), ('z', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'int3({self.x}, {self.y}, {self.z})'
    
    def __str__(self) -> str:
        return f'int3({self.x}, {self.y}, {self.z})'
    
    def __init__(self, x:int=0, y:int=0, z:int=0):
        self.x = x
        self.y = y
        self.z = z

    def from_list(self, input_list:List[int]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]

    def to_list(self) -> List[int]:
        return [self.x, self.y, self.z]
    
    
    
class int4(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int32), ('y', ctypes.c_int32), ('z', ctypes.c_int32), ('w', ctypes.c_int32)]

    def __repr__(self) -> str:
        return f'int4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __str__(self) -> str:
        return f'int4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __init__(self, x:int=0, y:int=0, z:int=0, w:int=0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def from_list(self, input_list:List[int]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]
        self.w = input_list[3]

    def to_list(self) -> List[int]:
        return [self.x, self.y, self.z, self.w]
    
   
    
class vec2(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'vec2({self.x}, {self.y})'
    
    def __str__(self) -> str:
        return f'vec2({self.x}, {self.y})'
    
    def __init__(self, x:float=0, y:float=0):
        self.x = x
        self.y = y

    def from_list(self, input_list:List[float]):
        self.x = input_list[0]
        self.y = input_list[1]

    def to_list(self) -> List[float]:
        return [self.x, self.y]
    
class vec3(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float), ('z', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'vec3({self.x}, {self.y}, {self.z})'
    
    def __str__(self) -> str:
        return f'vec3({self.x}, {self.y}, {self.z})'
    
    def __init__(self, x:float=0, y:float=0, z:float=0):
        self.x = x
        self.y = y
        self.z = z

    def from_list(self, input_list:List[float]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]
    
    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z)
    
    
class vec4(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float), ('z', ctypes.c_float), ('w', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'vec4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __str__(self) -> str:
        return f'vec4({self.x}, {self.y}, {self.z}, {self.w})'
    
    def __init__(self, x:float=0, y:float=0, z:float=0, w:float=0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def from_list(self, input_list:List[float]):
        self.x = input_list[0]
        self.y = input_list[1]
        self.z = input_list[2]
        self.w = input_list[3]

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z, self.w]
    
    
    
class RGBcolor(ctypes.Structure):
    _fields_ = [('r', ctypes.c_float), ('g', ctypes.c_float), ('b', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'RGBcolor({self.r}, {self.g}, {self.b})'
    
    def __str__(self) -> str:
        return f'RGBcolor({self.r}, {self.g}, {self.b})'
    
    def __init__(self, r:float=0, g:float=0, b:float=0):
        self.r = r
        self.g = g
        self.b = b

    def from_list(self, input_list:List[float]):
        self.r = input_list[0]
        self.g = input_list[1]
        self.b = input_list[2]

    def to_list(self) -> List[float]:
        return [self.r, self.g, self.b]

    
    
    
class RGBAcolor(ctypes.Structure):
    _fields_ = [('r', ctypes.c_float), ('g', ctypes.c_float), ('b', ctypes.c_float), ('a', ctypes.c_float)]

    def __repr__(self) -> str:
        return f'RGBAcolor({self.r}, {self.g}, {self.b}, {self.a})'
    
    def __str__(self) -> str:
        return f'RGBAcolor({self.r}, {self.g}, {self.b}, {self.a})'
    
    def __init__(self, r:float=0, g:float=0, b:float=0, a:float=0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def from_list(self, input_list:List[float]):
        self.r = input_list[0]
        self.g = input_list[1]
        self.b = input_list[2]
        self.a = input_list[3]
    
    
    
class SphericalCoord(ctypes.Structure):
    _fields_ = [
        ('radius', ctypes.c_float),
        ('elevation', ctypes.c_float),
        ('zenith', ctypes.c_float),
        ('azimuth', ctypes.c_float)
    ]

    def __repr__(self) -> str:
        return f'SphericalCoord({self.radius}, {self.elevation}, {self.zenith}, {self.azimuth})'
    
    def __str__(self) -> str:
        return f'SphericalCoord({self.radius}, {self.elevation}, {self.zenith}, {self.azimuth})'
    
    def __init__(self, radius:float=1, elevation:float=0, azimuth:float=0):
        """
        Initialize SphericalCoord matching C++ constructor.
        
        Args:
            radius: Radius (default: 1)
            elevation: Elevation angle in radians (default: 0)  
            azimuth: Azimuthal angle in radians (default: 0)
            
        Note: zenith is automatically computed as (π/2 - elevation) to match C++ behavior
        """
        import math
        self.radius = radius
        self.elevation = elevation
        self.zenith = 0.5 * math.pi - elevation  # zenith = π/2 - elevation (matches C++)
        self.azimuth = azimuth

    def from_list(self, input_list:List[float]):
        self.radius = input_list[0]
        self.elevation = input_list[1]
        self.zenith = input_list[2]
        self.azimuth = input_list[3]

    def to_list(self) -> List[float]:
        return [self.radius, self.elevation, self.zenith, self.azimuth]
    

# Factory functions to match C++ API
def make_int2(x: int, y: int) -> int2:
    """Make an int2 from two integers"""
    return int2(x, y)

def make_SphericalCoord(elevation_radians: float, azimuth_radians: float) -> SphericalCoord:
    """
    Make a SphericalCoord by specifying elevation and azimuth (C++ API compatibility).
    
    Args:
        elevation_radians: Elevation angle in radians
        azimuth_radians: Azimuthal angle in radians
        
    Returns:
        SphericalCoord with radius=1, and automatically computed zenith
    """
    return SphericalCoord(radius=1, elevation=elevation_radians, azimuth=azimuth_radians)

def make_int3(x: int, y: int, z: int) -> int3:
    """Make an int3 from three integers"""
    return int3(x, y, z)

def make_int4(x: int, y: int, z: int, w: int) -> int4:
    """Make an int4 from four integers"""  
    return int4(x, y, z, w)

def make_vec2(x: float, y: float) -> vec2:
    """Make a vec2 from two floats"""
    return vec2(x, y)

def make_vec3(x: float, y: float, z: float) -> vec3:
    """Make a vec3 from three floats"""
    return vec3(x, y, z)

def make_vec4(x: float, y: float, z: float, w: float) -> vec4:
    """Make a vec4 from four floats"""
    return vec4(x, y, z, w)

def make_RGBcolor(r: float, g: float, b: float) -> RGBcolor:
    """Make an RGBcolor from three floats"""
    return RGBcolor(r, g, b)

def make_RGBAcolor(r: float, g: float, b: float, a: float) -> RGBAcolor:
    """Make an RGBAcolor from four floats"""
    return RGBAcolor(r, g, b, a)

# Removed duplicate make_SphericalCoord function - keeping only the 2-parameter version above
