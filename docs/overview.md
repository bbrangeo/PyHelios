# Introduction {#Overview}

Welcome to the PyHelios User's Guide. This section introduces the core concepts and architecture of the Helios 3D plant simulation library as accessed through PyHelios.

## What is Helios?

Helios is a powerful C++ library for 3D physical simulation of plant and environmental systems. It provides:

- **3D Geometry Management**: Sophisticated handling of complex plant architectures
- **Physical Modeling**: Advanced simulation of light, energy, and mass transport
- **Plugin Architecture**: Extensible system for specialized modeling capabilities
- **High Performance**: Optimized C++ core with optional GPU acceleration

## PyHelios Integration

PyHelios provides seamless Python access to Helios functionality:

```python
from pyhelios import Context, DataTypes

# Access the full Helios simulation environment
context = Context()

# Use Helios data types naturally in Python
position = DataTypes.vec3(x=1.0, y=2.0, z=3.0)
size = DataTypes.vec2(width=5.0, height=3.0)
color = DataTypes.RGBcolor(r=0.2, g=0.8, b=0.3)

# Create geometry using Helios core functions
patch_uuid = context.addPatch(center=position, size=size, color=color)
```

## Core Architecture

### Context - The Simulation Environment
The `Context` is the central hub of any Helios simulation:

- **Geometry Management**: Stores and organizes all 3D primitives
- **Coordinate Systems**: Manages spatial reference frames
- **Data Association**: Links data to geometric elements
- **State Tracking**: Maintains simulation state and history

### Primitives - Basic Geometric Elements
Helios uses several primitive types:

- **Patches**: Rectangular surface elements (most common)
- **Triangles**: Triangular surface elements for complex shapes
- **Disks**: Circular/elliptical surface elements
- **Voxels**: 3D volumetric elements
- **Tiles**: Specialized surface elements

### Objects - Complex Structures
Objects group primitives into meaningful structures:
- **Compound Objects**: User-defined collections
- **Tree Objects**: Hierarchical plant structures
- **Canopy Objects**: Large-scale vegetation assemblies

### Coordinate Systems
Helios supports flexible coordinate systems:
- **Global Coordinates**: World reference frame
- **Local Coordinates**: Object-relative coordinates
- **Transformations**: Translation, rotation, scaling operations

## Data Management

### Primitive Data
Associate data with geometric elements:

```python
# Add scalar data to primitives
context.setPrimitiveDataFloat(patch_uuid, "temperature", 25.5)
context.setPrimitiveDataFloat(patch_uuid, "moisture", 0.65)

# Add vector data
context.setPrimitiveDataVec3(patch_uuid, "energy_flux", 0.1, 0.2, 0.3)

# Retrieve data (auto-detects type)
temperature = context.getPrimitiveData(patch_uuid, "temperature")
# Or with explicit type (optional)
temperature = context.getPrimitiveDataFloat(patch_uuid, "temperature")
```

### Global Data
Store simulation-wide information:

```python
# Global data methods are not currently exposed in PyHelios Context
# Use primitive data for simulation-wide information:
all_uuids = context.getAllUUIDs()
for uuid in all_uuids:
    context.setPrimitiveDataFloat(uuid, "ambient_temperature", 20.0)
```

## UUID-Based Object Tracking

Helios uses UUIDs (Universally Unique Identifiers) for robust object tracking:

```python
# All geometry operations return UUIDs
patch_uuid = context.addPatch(
    center=DataTypes.vec3(0, 0, 0),
    size=DataTypes.vec2(1, 1),
    color=DataTypes.RGBcolor(0.3, 0.7, 0.2)
)
triangle_uuid = context.addTriangle(
    vertex0=DataTypes.vec3(0, 0, 0),
    vertex1=DataTypes.vec3(1, 0, 0), 
    vertex2=DataTypes.vec3(0.5, 1, 0)
)

# UUIDs remain valid throughout simulation
area = context.getPrimitiveArea(patch_uuid)
normal = context.getPrimitiveNormal(patch_uuid)

# Collect and manipulate UUIDs
all_uuids = context.getAllUUIDs()
primitive_count = context.getPrimitiveCount()
```

## Physical Units and Conventions

Helios uses consistent SI units:
- **Length**: meters (m)
- **Area**: square meters (m²)
- **Angles**: radians
- **Temperature**: Celsius (°C)
- **Energy**: Joules (J)
- **Power**: Watts (W)

### Coordinate System Conventions
- **X-axis**: East (positive) / West (negative)
- **Y-axis**: North (positive) / South (negative)  
- **Z-axis**: Up (positive) / Down (negative)

## Error Handling

PyHelios provides comprehensive error handling:

```python
from pyhelios.exceptions import (
    HeliosError, HeliosRuntimeError, 
    HeliosUUIDNotFoundError, HeliosFileIOError
)

try:
    context = Context()
    patch_uuid = context.addPatch(
        center=DataTypes.vec3(0, 0, 0),
        size=DataTypes.vec2(1, 1),
        color=DataTypes.RGBcolor(0.3, 0.7, 0.2)
    )
    area = context.getPrimitiveArea(patch_uuid)
except HeliosUUIDNotFoundError:
    print("Primitive not found")
except HeliosRuntimeError as e:
    print(f"Runtime error: {e}")
except HeliosError as e:
    print(f"General Helios error: {e}")
```

## Memory Management

PyHelios handles memory management automatically:

```python
# Context managers ensure proper cleanup
with Context() as context:
    # Your simulation code here
    pass  # Automatic cleanup when done

# Manual resource management if needed
context = Context()
try:
    # Simulation code
    pass
finally:
    context.cleanup()  # Explicit cleanup
```

## Performance Considerations

### Efficient Geometry Creation
```python
# Individual operations (batch operations not available in current API)
centers = [DataTypes.vec3(i, 0, 0) for i in range(100)]
sizes = [DataTypes.vec2(1, 1) for _ in range(100)]
colors = [DataTypes.RGBcolor(0.3, 0.7, 0.2) for _ in range(100)]

# Create patches individually
uuids = []
for center, size, color in zip(centers, sizes, colors):
    uuid = context.addPatch(center=center, size=size, color=color)
    uuids.append(uuid)
```

### Memory Usage
```python
# Monitor geometry usage (memory monitoring not available in current API)
primitive_count = context.getPrimitiveCount()
object_count = context.getObjectCount()
print(f"Managing {primitive_count} primitives in {object_count} objects")
```

## Integration with Helios Documentation

This PyHelios documentation complements the complete Helios documentation:

- **Core Concepts**: Detailed in Helios C++ documentation
- **Plugin Details**: Each plugin has comprehensive documentation
- **Advanced Features**: Full coverage in native Helios docs
- **Performance Optimization**: Detailed optimization guides

Visit [https://baileylab.ucdavis.edu/software/helios](https://baileylab.ucdavis.edu/software/helios) for complete documentation.

## Next Steps

- **[User/API Guide](API.html)** - Detailed API reference
- **[File I/O](IO.html)** - Data loading and saving
- **[Plugin System](PluginSystem.html)** - Extended functionality
- **[Examples](Examples.html)** - Practical examples and tutorials