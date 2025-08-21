# User/API Guide {#API}

Complete API reference for PyHelios core functionality, based on the actual implementation and wrappers.

## Context Class

The `Context` class is the central simulation environment in PyHelios. All methods documented here are verified from the actual implementation.

### Basic Usage
```python
from pyhelios import Context
from pyhelios.types import *  # Import all vector types directly

# Create a new simulation context
context = Context()

# Context manager usage (recommended)
with Context() as context:
    # Your simulation code here
    pass  # Automatic cleanup
```

### Actual Data Types

PyHelios provides these verified data types:

```python
from pyhelios.types import *  # Import all vector types directly

# Vector types (lowercase)
position = vec3(x=1.0, y=2.0, z=3.0)
size = vec2(x=5.0, y=3.0)
direction = vec4(x=1.0, y=2.0, z=3.0, w=1.0)

# Integer vectors
grid_size = int2(x=100, y=50)
voxel_index = int3(x=10, y=20, z=5)
tensor_dims = int4(x=100, y=50, z=25, w=10)

# Colors (0.0 to 1.0 range)
green = RGBcolor(r=0.2, g=0.8, b=0.2)
transparent_blue = RGBAcolor(r=0.2, g=0.2, b=0.8, a=0.5)

# Spherical coordinates
spherical = SphericalCoord(
    radius=10.0,
    elevation=0.5,  # radians from horizontal
    azimuth=1.57    # radians from north
)

# Alternative: Explicit DataTypes module (if preferred)
# from pyhelios import DataTypes
# position = DataTypes.vec3(1.0, 2.0, 3.0)
```

### Actual Geometry Creation Methods

These methods are verified from the Context.py implementation:

#### Patches (Rectangular Surfaces)
```python
# Basic patch (default position and size)
patch_uuid = context.addPatch()

# Patch with center and size
patch_uuid = context.addPatch(
    center=vec3(0, 0, 0),
    size=vec2(1.0, 2.0)
)

# Patch with center, size, rotation and color
patch_uuid = context.addPatch(
    center=vec3(0, 0, 0),
    size=vec2(1.0, 2.0), 
    rotation=SphericalCoord(radius=1, elevation=0, azimuth=0),
    color=RGBcolor(0.3, 0.7, 0.2)
)
```

#### Triangles
```python
# Triangle with three vertices
triangle_uuid = context.addTriangle(
    vertex0=vec3(0, 0, 0),
    vertex1=vec3(1, 0, 0),
    vertex2=vec3(0.5, 1, 0)
)

# Triangle with color
triangle_uuid = context.addTriangle(
    vertex0=vec3(0, 0, 0),
    vertex1=vec3(1, 0, 0),
    vertex2=vec3(0.5, 1, 0),
    color=RGBcolor(0.8, 0.2, 0.2)
)
```

### Actual Geometry Query Methods

These methods are verified from the actual wrapper implementation:

```python
# Basic properties
area = context.getPrimitiveArea(uuid)
primitive_type = context.getPrimitiveType(uuid)  # Returns PrimitiveType enum
normal = context.getPrimitiveNormal(uuid)
vertices = context.getPrimitiveVertices(uuid)
color = context.getPrimitiveColor(uuid)

# Collections
all_uuids = context.getAllUUIDs()
primitive_count = context.getPrimitiveCount()
object_count = context.getObjectCount()
all_object_ids = context.getAllObjectIDs()

# Object queries
object_primitives_info = context.getPrimitivesInfoForObject(object_id)
```

### Primitive Data API

PyHelios provides a comprehensive primitive data system for storing user-defined metadata:

#### Setting Primitive Data
```python
# Set primitive data (auto-detects type from Python value)
context.setPrimitiveData(uuid, "temperature", 25.5)        # float
context.setPrimitiveData(uuid, "leaf_count", 100)          # int  
context.setPrimitiveData(uuid, "species", "oak")           # string
context.setPrimitiveData(uuid, "position", vec3(1, 2, 3))  # vec3
context.setPrimitiveData(uuid, "size", vec2(1.0, 2.0))     # vec2
context.setPrimitiveData(uuid, "is_flowering", True)       # bool

# Extended data types
context.setPrimitiveData(uuid, "precise_value", 3.14159)   # double (high precision)
context.setPrimitiveData(uuid, "large_id", 3000000000)     # uint (large numbers)
context.setPrimitiveData(uuid, "grid_pos", int2(10, 20))   # int2
context.setPrimitiveData(uuid, "voxel_index", int3(5, 10, 15))     # int3
context.setPrimitiveData(uuid, "tensor_dims", int4(100, 50, 25, 10)) # int4
context.setPrimitiveData(uuid, "color_data", vec4(1.0, 0.5, 0.2, 0.8)) # vec4

# Lists/tuples automatically converted to appropriate vector types
context.setPrimitiveData(uuid, "velocity", [0.1, 0.2, 0.3])  # Becomes vec3
context.setPrimitiveData(uuid, "uv_coord", [0.5, 0.7])       # Becomes vec2
context.setPrimitiveData(uuid, "rgba", [1.0, 0.5, 0.2, 0.8]) # Becomes vec4
```

#### Getting Primitive Data (Auto-Detection - Recommended)
```python
# New simplified API - automatically detects and returns correct type
temperature = context.getPrimitiveData(uuid, "temperature")    # Returns: float
leaf_count = context.getPrimitiveData(uuid, "leaf_count")      # Returns: int
species = context.getPrimitiveData(uuid, "species")            # Returns: str
position = context.getPrimitiveData(uuid, "position")          # Returns: vec3
is_flowering = context.getPrimitiveData(uuid, "is_flowering")  # Returns: bool

# Extended types
precise_value = context.getPrimitiveData(uuid, "precise_value")  # Returns: float (double)
large_id = context.getPrimitiveData(uuid, "large_id")           # Returns: int (uint) 
grid_pos = context.getPrimitiveData(uuid, "grid_pos")           # Returns: int2
voxel_index = context.getPrimitiveData(uuid, "voxel_index")     # Returns: int3
color_data = context.getPrimitiveData(uuid, "color_data")       # Returns: vec4

print(f"Temperature: {temperature} (type: {type(temperature).__name__})")
print(f"Position: {position} (type: {type(position).__name__})")
```

#### Getting Primitive Data (Explicit Types - Optional)
```python
# Backward compatibility: you can still specify types explicitly if needed
temperature = context.getPrimitiveData(uuid, "temperature", float)
leaf_count = context.getPrimitiveData(uuid, "leaf_count", int)
species = context.getPrimitiveData(uuid, "species", str)
position = context.getPrimitiveData(uuid, "position", vec3)
velocity = context.getPrimitiveData(uuid, "velocity", list)  # Returns as list

# Special cases requiring explicit types
large_id = context.getPrimitiveData(uuid, "large_id", "uint")     # Unsigned int
precise = context.getPrimitiveData(uuid, "precise_value", "double") # Double precision
grid_list = context.getPrimitiveData(uuid, "grid_pos", "list_int2") # As list [x, y]
```

#### Data Utility Functions
```python
# Check data existence and properties
has_data = context.doesPrimitiveDataExist(uuid, "temperature")
data_type = context.getPrimitiveDataType(uuid, "temperature")  # Returns HeliosDataType enum
data_size = context.getPrimitiveDataSize(uuid, "temperature")  # Returns size in elements

# Type introspection
type_names = {
    0: "HELIOS_TYPE_INT", 1: "HELIOS_TYPE_UINT", 2: "HELIOS_TYPE_FLOAT",
    3: "HELIOS_TYPE_DOUBLE", 4: "HELIOS_TYPE_VEC2", 5: "HELIOS_TYPE_VEC3",
    6: "HELIOS_TYPE_VEC4", 7: "HELIOS_TYPE_INT2", 8: "HELIOS_TYPE_INT3",
    9: "HELIOS_TYPE_INT4", 10: "HELIOS_TYPE_STRING", 11: "HELIOS_TYPE_BOOL"
}
print(f"Data type: {type_names.get(data_type, 'UNKNOWN')}")
```

#### Advanced Type-Specific Methods (For Specialized Use)
```python
# These type-specific methods are still available for specialized use cases
context.setPrimitiveDataFloat(uuid, "temperature", 25.5)
context.setPrimitiveDataInt(uuid, "leaf_count", 100)
context.setPrimitiveDataString(uuid, "species", "oak")
context.setPrimitiveDataVec3(uuid, "velocity", 0.1, 0.2, 0.3)
context.setPrimitiveDataUInt(uuid, "large_id", 3000000000)  # Required for values > 2^31

# Type-specific getters (return specific types)
temperature = context.getPrimitiveDataFloat(uuid, "temperature")
leaf_count = context.getPrimitiveDataInt(uuid, "leaf_count")
species = context.getPrimitiveDataString(uuid, "species")
velocity_list = context.getPrimitiveDataVec3(uuid, "velocity")  # Returns [x, y, z]
```

### Actual File Operations

These methods are verified from the wrapper implementation:

```python
# Load PLY files - single method with optional parameters
uuids = context.loadPLY("models/plant.ply")
uuids = context.loadPLY("models/plant.ply", silent=True)

# Load PLY with transformations - all via single method
uuids = context.loadPLY(
    "leaf.ply", 
    origin=vec3(5.0, 0.0, 0.0), 
    height=2.0,
    upaxis="YUP",
    silent=False
)

uuids = context.loadPLY(
    "tree.ply",
    origin=vec3(0.0, 0.0, 0.0),
    height=5.0,
    rotation=SphericalCoord(1.0, 0.0, 1.57),  # 90 degrees
    upaxis="YUP"
)

uuids = context.loadPLY(
    "leaves.ply",
    origin=vec3(2.0, 3.0, 0.0),
    height=1.0,
    color=RGBcolor(0.3, 0.7, 0.2),
    upaxis="YUP"
)

# Load OBJ files
uuids = context.loadOBJ("models/tree.obj")
uuids = context.loadOBJ("models/tree.obj", silent=True)

# Load XML files
uuids = context.loadXML("scenes/canopy.xml")
uuids = context.loadXML("scenes/canopy.xml", quiet=True)
```

### Actual Visualization Methods

These methods are verified from the wrapper implementation:

```python
# Pseudocolor mapping
all_uuids = context.getAllUUIDs()
context.colorPrimitiveByDataPseudocolor(
    uuids=all_uuids,
    primitive_data="temperature",
    colormap="hot", 
    ncolors=256
)

# With specified value range (same method, optional parameters)
context.colorPrimitiveByDataPseudocolor(
    uuids=all_uuids,
    primitive_data="radiation_flux",
    colormap="hot",
    ncolors=256,
    max_val=100.0,
    min_val=0.0
)
```

### Actual Geometry State Management

```python
# Check if geometry needs updates
is_dirty = context.isGeometryDirty()

# Mark geometry state
context.markGeometryDirty()
context.markGeometryClean()
```

## WeberPennTree Class

The WeberPennTree class provides procedural tree generation with these actual methods:

### Basic Usage
```python
from pyhelios import Context, WeberPennTree, WPTType

context = Context()
wpt = WeberPennTree(context)

# Available tree types (from actual enum)
tree_types = [
    WPTType.ALMOND,
    WPTType.APPLE, 
    WPTType.AVOCADO,
    WPTType.LEMON,
    WPTType.OLIVE,
    WPTType.ORANGE,
    WPTType.PEACH,
    WPTType.PISTACHIO,
    WPTType.WALNUT
]

# Build tree with default parameters
tree_id = wpt.buildTree(WPTType.LEMON)

# Build tree with position and scale
tree_id = wpt.buildTree(
    wpt_type=WPTType.APPLE,
    origin=vec3(5, 10, 0),
    scale=1.5
)
```

### Actual Tree Query Methods
```python
# Get UUIDs for different tree components
trunk_uuids = wpt.getTrunkUUIDs(tree_id)
branch_uuids = wpt.getBranchUUIDs(tree_id)
leaf_uuids = wpt.getLeafUUIDs(tree_id)
all_tree_uuids = wpt.getAllUUIDs(tree_id)
```

### Actual Customization Methods
```python
# Set generation parameters
wpt.setBranchRecursionLevel(4)  # Levels of branching
wpt.setTrunkSegmentResolution(8)  # Trunk smoothness  
wpt.setBranchSegmentResolution(6)  # Branch smoothness
wpt.setLeafSubdivisions(3, 3)  # Leaf detail (x, y subdivisions)
```

## RadiationModel Class

The RadiationModel provides GPU-accelerated radiation simulation:

### Basic Usage
```python
from pyhelios import Context, RadiationModel, RadiationModelError

context = Context()

try:
    with RadiationModel(context) as radiation:
        # Add radiation band
        radiation.add_radiation_band("PAR")
        
        # Configure sources
        source_id = radiation.add_collimated_radiation_source()
        radiation.set_source_flux(source_id, "PAR", 1000.0)
        
        # Set ray counts
        radiation.set_direct_ray_count("PAR", 100)
        radiation.set_diffuse_ray_count("PAR", 300)
        
        # Run simulation
        radiation.run_band("PAR")
        
        # Get results
        results = radiation.get_total_absorbed_flux()
        
except RadiationModelError as e:
    print(f"Radiation modeling not available: {e}")
```

### Actual Radiation Methods
```python
# Band management
radiation.add_radiation_band("SW")
radiation.add_radiation_band_with_wavelengths("custom", 400.0, 700.0)
radiation.copy_radiation_band("PAR", "PAR_copy")

# Source management
source_id = radiation.add_collimated_radiation_source()
source_id = radiation.add_collimated_radiation_source(direction=(0.3, 0.3, -0.9))
sphere_id = radiation.add_sphere_radiation_source(position=(0, 0, 10), radius=0.5)
sun_id = radiation.add_sun_sphere_radiation_source(
    radius=0.5, zenith=45.0, azimuth=180.0
)

# Flux configuration
radiation.set_diffuse_radiation_flux("PAR", 200.0)
radiation.set_source_flux(source_id, "PAR", 1000.0)
flux = radiation.get_source_flux(source_id, "PAR")

# Simulation control
radiation.update_geometry()  # Update all geometry
radiation.update_geometry([uuid1, uuid2])  # Update specific UUIDs
radiation.run_band("PAR")
radiation.run_bands(["PAR", "NIR"])

# Advanced configuration
radiation.set_scattering_depth("PAR", 3)
radiation.set_min_scatter_energy("PAR", 0.01)
radiation.disable_emission("PAR")
radiation.enable_emission("PAR")
```

## Visualizer Class

The Visualizer provides OpenGL-based 3D visualization:

### Basic Usage
```python
from pyhelios import Context, Visualizer, VisualizerError

context = Context()
# Add some geometry first
patch_uuid = context.addPatch(
    center=vec3(0, 0, 0),
    size=vec2(2, 2),
    color=RGBcolor(0.3, 0.7, 0.2)
)

try:
    visualizer = Visualizer(
        width=1024, 
        height=768, 
        antialiasing_samples=4,
        headless=False
    )
    # Visualizer methods would be documented based on actual implementation
    
except VisualizerError as e:
    print(f"Visualization not available: {e}")
```

## Error Handling

PyHelios provides comprehensive error handling:

```python
from pyhelios.exceptions import (
    HeliosError,
    HeliosRuntimeError,
    HeliosInvalidArgumentError,
    HeliosUUIDNotFoundError,
    HeliosFileIOError,
    HeliosMemoryAllocationError,
    HeliosGPUInitializationError,
    HeliosPluginNotAvailableError,
    HeliosUnknownError
)

try:
    context = Context()
    patch_uuid = context.addPatch()
    area = context.getPrimitiveArea(patch_uuid)
except HeliosUUIDNotFoundError:
    print("Primitive not found")
except HeliosFileIOError as e:
    print(f"File operation failed: {e}")
except HeliosRuntimeError as e:
    print(f"Runtime error: {e}")
except HeliosError as e:
    print(f"General Helios error: {e}")
```

## Example Workflows

### Complete Basic Example
```python
from pyhelios import Context, WeberPennTree, WPTType
from pyhelios.types import *

# Create simulation
context = Context()

# Add basic geometry
patch_uuid = context.addPatch(
    center=vec3(0, 0, 0),
    size=vec2(5, 5),
    color=RGBcolor(0.5, 0.5, 0.5)
)

# Generate tree
wpt = WeberPennTree(context)
tree_id = wpt.buildTree(WPTType.LEMON)

# Query results
print(f"Patch UUID: {patch_uuid}")
print(f"Patch area: {context.getPrimitiveArea(patch_uuid)}")
print(f"Tree ID: {tree_id}")
print(f"Tree leaf count: {len(wpt.getLeafUUIDs(tree_id))}")
print(f"Total primitives: {context.getPrimitiveCount()}")
```

This documentation is based entirely on the actual PyHelios implementation and verified wrapper functions.