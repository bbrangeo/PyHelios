# Quick Start {#QuickStart}

Get up and running with PyHelios in minutes! This guide walks you through your first simulation.

## Your First PyHelios Script

Let's create a simple simulation with a patch and a tree:

```python
from pyhelios import Context, WeberPennTree, WPTType
from pyhelios.types import *  # Import all vector types

# Create a simulation context
context = Context()

# Add a simple patch
center = vec3(0, 0, 0)
size = vec2(2, 2)
color = RGBcolor(0.3, 0.7, 0.3)  # Green

patch_uuid = context.addPatch(center=center, size=size, color=color)
print(f"Created patch with UUID: {patch_uuid}")

# Add a lemon tree
wpt = WeberPennTree(context)
tree_uuid = wpt.buildTree(WPTType.LEMON)
print(f"Created tree with UUID: {tree_uuid}")

# Check what we've created
print(f"Total primitives: {context.getPrimitiveCount()}")
print(f"All UUIDs: {context.getAllUUIDs()}")
```

## Basic Concepts

### Context
The `Context` is your simulation environment. It manages all 3D geometry:

```python
from pyhelios import Context

context = Context()
# Context automatically detects available plugins
# and reports what's available for use
```

### Data Types
PyHelios provides geometric data types for 3D operations:

```python
from pyhelios.types import *  # Import all vector types directly

# 3D vectors
position = vec3(1.0, 2.0, 3.0)
direction = vec3(0, 0, 1)  # Up vector

# 2D vectors for sizes
size = vec2(10.0, 5.0)  # width, height

# Colors
green = RGBcolor(0.2, 0.8, 0.2)
transparent_blue = RGBAcolor(0.2, 0.2, 0.8, 0.5)
```

### Convenient Vector Type Imports

PyHelios provides two ways to use vector types:

**Option 1: Explicit DataTypes module (verbose)**
```python
from pyhelios import DataTypes
position = DataTypes.vec3(1, 2, 3)
color = DataTypes.RGBcolor(0.5, 0.5, 0.5)
```

**Option 2: Direct imports (recommended)**
```python
from pyhelios.types import *  # Import all types
position = vec3(1, 2, 3)
color = RGBcolor(0.5, 0.5, 0.5)
```

The star import brings in all vector types: `vec2`, `vec3`, `vec4`, `int2`, `int3`, `int4`, `RGBcolor`, `RGBAcolor`, `SphericalCoord`, and factory functions like `make_vec3`

### Tree Generation
Create procedural trees with the WeberPennTree plugin:

```python
from pyhelios import WeberPennTree, WPTType

wpt = WeberPennTree(context)

# Available tree types
tree_types = [
    WPTType.ALMOND, WPTType.APPLE, WPTType.AVOCADO,
    WPTType.LEMON, WPTType.OLIVE, WPTType.ORANGE,
    WPTType.PEACH, WPTType.PISTACHIO, WPTType.WALNUT
]

# Create different trees
for tree_type in tree_types[:3]:  # First 3 types
    tree_uuid = wpt.buildTree(tree_type)
    print(f"Created {tree_type} tree: {tree_uuid}")
```

## Working with Geometry

### Adding Primitives

```python
# Add patches (rectangular surfaces)
patch_uuid = context.addPatch(
    center=vec3(0, 0, 0),
    size=vec2(1, 1),
    color=RGBcolor(0.5, 0.5, 0.5)
)

# Add triangles
vertices = [
    vec3(0, 0, 0),
    vec3(1, 0, 0), 
    vec3(0.5, 1, 0)
]
triangle_uuid = context.add_triangle(vertices[0], vertices[1], vertices[2])

# Add disks (circular surfaces) 
disk_uuid = context.add_disk(
    center=vec3(2, 0, 0),
    size=vec2(0.5, 0.5),  # radii
    color=RGBcolor(1, 0, 0)  # Red
)
```

### Querying Geometry

```python
# Get information about primitives
primitive_count = context.getPrimitiveCount()
all_uuids = context.getAllUUIDs()

# Get specific primitive properties
patch_center = context.get_primitive_center(patch_uuid)
patch_area = context.get_primitive_area(patch_uuid)
patch_normal = context.get_primitive_normal(patch_uuid)

print(f"Patch center: {patch_center}")
print(f"Patch area: {patch_area}")
```

## Plugin-Aware Usage

PyHelios automatically detects available plugins:

```python
# Check what plugins are available
available_plugins = context.get_available_plugins()
print(f"Available plugins: {available_plugins}")

# Check specific plugin
if context.is_plugin_available('radiation'):
    print("GPU radiation modeling available!")
    # Use radiation plugin...
else:
    print("Radiation plugin not available")
    print("Build with: build_scripts/build_helios --profile gpu-accelerated")
```

## Next Steps

- **[Cross-Platform Usage](CrossPlatform.html)** - Platform-specific features
- **[Plugin System](PluginSystem.html)** - Understanding available plugins  
- **[Examples](Examples.html)** - More detailed examples
- **[User's Guide](UserGuide.html)** - Complete API documentation

## Common Patterns

### Context Manager Usage
```python
# Both Context and plugins support context managers
with Context() as context:
    # Your simulation code here
    pass
# Automatic cleanup when done
```

### Error Handling
```python
from pyhelios.exceptions import HeliosError

try:
    context = Context()
    # ... simulation code ...
except HeliosError as e:
    print(f"PyHelios error: {e}")
    # Handle error appropriately
```

### Development Mode
```python
# For development without native libraries
import os
os.environ['PYHELIOS_DEV_MODE'] = '1'

from pyhelios import Context
# Will use mock mode - great for development and testing
```