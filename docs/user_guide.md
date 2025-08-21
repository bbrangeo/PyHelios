# User's Guide {#UserGuide}

This guide covers the core Helios library functionality accessible through PyHelios, providing detailed information about the underlying 3D simulation environment.

## Core Concepts

### Simulation Environment
The Helios core provides a comprehensive 3D simulation environment for plant and environmental modeling. PyHelios exposes this functionality through a clean Python interface while maintaining the power and flexibility of the underlying C++ implementation.

### Key Components
- **Context**: Central simulation environment managing all 3D geometry
- **Primitives**: Basic geometric elements (patches, triangles, disks, voxels)
- **Objects**: Collections of primitives forming complex structures
- **Data**: Primitive-associated information and metadata
- **Coordinate Systems**: 3D spatial reference frameworks

### Navigation
- **[Introduction](Overview.html)** - Overview of core concepts
- **[User/API Guide](API.html)** - Detailed API documentation
- **[File I/O](IO.html)** - Loading and saving data

## Architecture Overview

PyHelios provides Python bindings to the Helios C++ library while maintaining:
- **Performance**: Direct access to optimized C++ implementations
- **Flexibility**: Full access to underlying Helios functionality  
- **Ease of Use**: Pythonic interfaces and error handling
- **Cross-Platform**: Consistent behavior across Windows, macOS, and Linux

The architecture consists of:
1. **Python Interface Layer**: High-level classes and functions
2. **ctypes Wrapper Layer**: Low-level C++ library bindings
3. **Native Library Layer**: Compiled Helios C++ library
4. **Plugin System**: Modular extensions for specialized functionality

## Getting Started with Core Functionality

### Vector Type Imports

PyHelios provides two convenient ways to work with vector types:

**Option 1: Explicit DataTypes module (verbose)**
```python
from pyhelios import Context, DataTypes

# Create simulation environment
context = Context()

# Basic 3D data types
position = DataTypes.vec3(1.0, 2.0, 3.0)
size = DataTypes.vec2(10.0, 5.0)
color = DataTypes.RGBcolor(0.3, 0.7, 0.2)
```

**Option 2: Direct import (recommended)**
```python
from pyhelios import Context
from pyhelios.types import *  # Import all vector types

# Create simulation environment
context = Context()

# Basic 3D data types - no DataTypes prefix needed
position = vec3(1.0, 2.0, 3.0)
size = vec2(10.0, 5.0)
color = RGBcolor(0.3, 0.7, 0.2)
```

The star import `from pyhelios.types import *` brings in all commonly used types:
- **Vector types**: `vec2`, `vec3`, `vec4`
- **Integer vectors**: `int2`, `int3`, `int4`
- **Colors**: `RGBcolor`, `RGBAcolor`
- **Coordinates**: `SphericalCoord`
- **Factory functions**: `make_vec3`, `make_RGBcolor`, etc.

### Basic Usage Example

```python
from pyhelios import Context
from pyhelios.types import *

# Create simulation environment
context = Context()

# Basic 3D data types
position = vec3(1.0, 2.0, 3.0)
size = vec2(10.0, 5.0)
color = RGBcolor(0.3, 0.7, 0.2)

# Add geometry to simulation
patch_uuid = context.addPatch(center=position, size=size, color=color)

# Query geometry properties
area = context.getPrimitiveArea(patch_uuid)
center = context.getPrimitiveCenter(patch_uuid)
normal = context.getPrimitiveNormal(patch_uuid)

print(f"Created patch with area {area} at {center}")
```

## Integration with Helios Ecosystem

PyHelios seamlessly integrates with the broader Helios ecosystem:

- **Native Helios**: Access to full C++ API through ctypes
- **Helios Plugins**: Support for all 21+ available plugins
- **Helios Data Formats**: Compatible file I/O operations
- **Helios Documentation**: Consistent with native documentation

For complete documentation of the underlying Helios library, visit:
[https://baileylab.ucdavis.edu/software/helios](https://baileylab.ucdavis.edu/software/helios)