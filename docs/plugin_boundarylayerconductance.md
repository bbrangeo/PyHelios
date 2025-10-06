# Boundary Layer Conductance Documentation {#BoundaryLayerConductanceDoc}

## Overview

BoundaryLayerConductanceModel provides boundary layer conductance calculations for heat and mass transfer across primitive boundaries. This plugin enables accurate modeling of convective transport in plant-atmosphere interactions and surface energy balance studies.

The plugin implements four different boundary-layer conductance models:

- **Pohlhausen**: Laminar flat plate, forced convection (default)
- **InclinedPlate**: Mixed free-forced convection for inclined surfaces
- **Sphere**: Laminar flow around spherical objects
- **Ground**: Convective transfer over bare ground surfaces

## System Requirements

- **Platforms**: Windows, Linux, macOS
- **Dependencies**: None (pure computational plugin)
- **GPU**: Not required
- **Memory**: Minimal overhead

## Input Primitive Data

The boundary layer conductance calculation uses the following primitive data:

| Primitive Data | Units | Type | Description | Default Value |
|----------------|-------|------|-------------|---------------|
| wind_speed | m/s | float | Air wind speed outside boundary layer | 1.0 m/s |
| object_length | m | float | Characteristic dimension of object | sqrt(area) |
| air_temperature | K | float | Ambient air temperature | 290 K |
| surface_temperature | K | float | Surface temperature | 300 K |
| twosided_flag | - | uint | Number of faces (1 or 2) | 2 |

Set input data using:
```python
context.setPrimitiveData(uuid, "wind_speed", 2.5)
context.setPrimitiveData(uuid, "air_temperature", 298.0)
```

## Output Primitive Data

Results are stored as primitive data:

| Primitive Data | Units | Type | Description |
|----------------|-------|------|-------------|
| boundarylayer_conductance | mol air/m²/s | float | Calculated boundary-layer conductance |

Access results using:
```python
gH = context.getPrimitiveData(uuid, "boundarylayer_conductance")
```

## Quick Start

```python
from pyhelios import Context, BoundaryLayerConductanceModel
from pyhelios.types import *

# Create context and add leaf geometry
with Context() as context:
    leaf_uuid = context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])

    with BoundaryLayerConductanceModel(context) as bl_model:
        # Set model for all primitives (default is Pohlhausen)
        bl_model.setBoundaryLayerModel("InclinedPlate")

        # Run calculation
        bl_model.run()

        # Results stored in primitive data "boundarylayer_conductance"
        # Units: mol air/m²/s
```

## Boundary Layer Models

### 1. Pohlhausen (Laminar Flat Plate)

Classical solution for laminar forced convection over a flat plate parallel to flow direction.

**Use Cases:**
- Flat leaves in steady wind
- Laminar boundary layers
- Forced convection dominant

**Formula:**
```
gH = 0.135 * ns * sqrt(U / L)
```

where:
- `gH` = boundary-layer conductance (mol air/m²/s)
- `ns` = number of primitive sides (1 or 2)
- `U` = wind speed (m/s)
- `L` = characteristic length (m)

**Example:**
```python
bl_model.setBoundaryLayerModel("Pohlhausen")
bl_model.run()
```

### 2. InclinedPlate (Mixed Convection)

Correlation for plates inclined to flow direction, accounting for both forced and free convection.

**Use Cases:**
- Angled leaves
- Mixed convection scenarios
- Temperature-dependent buoyancy effects

**Formula (simplified):**
```
gH = f(Re, Gr, θ)
```

Based on Chen et al. (1986) correlation incorporating:
- Reynolds number (Re)
- Grashof number (Gr)
- Plate inclination angle (θ)

**Example:**
```python
# Ideal for angled leaves
bl_model.setBoundaryLayerModel("InclinedPlate", uuids=leaf_uuids)
bl_model.run()
```

### 3. Sphere (Laminar Sphere)

Correlation for forced convection around a sphere.

**Use Cases:**
- Fruits (apples, oranges, grapes)
- Spherical objects
- Low Reynolds number flow

**Formula:**
```
gH = 0.00164/D + 0.110*sqrt(U/D)
```

where:
- `D` = sphere diameter (m)
- `U` = wind speed (m/s)

**Example:**
```python
# Ideal for fruit modeling
bl_model.setBoundaryLayerModel("Sphere", uuids=fruit_uuids)
bl_model.run()
```

### 4. Ground (Bare Soil Surface)

Simplified relationship for convective transfer over flat, bare ground.

**Use Cases:**
- Soil surfaces
- Ground patches
- Horizontal surfaces

**Formula:**
```
gH = 0.166 + 0.5*U
```

where:
- `U` = wind speed at reference height (m/s)

**Example:**
```python
# Ideal for ground/soil patches
bl_model.setBoundaryLayerModel("Ground", uuids=ground_uuids)
bl_model.run()
```

## Examples

### Basic Usage

```python
from pyhelios import Context, BoundaryLayerConductanceModel
from pyhelios.types import *

with Context() as context:
    # Add a leaf patch
    leaf = context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])

    with BoundaryLayerConductanceModel(context) as bl_model:
        # Use default Pohlhausen model
        bl_model.run()

        # Access results
        # Results are stored in primitive data "boundarylayer_conductance"
```

### Setting Different Models

```python
from pyhelios import Context, BoundaryLayerConductanceModel
from pyhelios.types import *

with Context() as context:
    # Add various geometry
    leaves = []
    for i in range(5):
        uuid = context.addPatch(center=vec3(i*0.2, 0, 1), size=[0.05, 0.05])
        leaves.append(uuid)

    with BoundaryLayerConductanceModel(context) as bl_model:
        # Test all four models
        bl_model.setBoundaryLayerModel("Pohlhausen", uuids=[leaves[0]])
        bl_model.setBoundaryLayerModel("InclinedPlate", uuids=[leaves[1]])
        bl_model.setBoundaryLayerModel("Sphere", uuids=[leaves[2]])
        bl_model.setBoundaryLayerModel("Ground", uuids=[leaves[3]])

        # Run for all
        bl_model.run()
```

### Application-Specific Models

```python
from pyhelios import Context, BoundaryLayerConductanceModel
from pyhelios.types import *

with Context() as context:
    # Create different surface types

    # Leaves (inclined plates)
    leaf_uuids = []
    for i in range(10):
        uuid = context.addPatch(center=vec3(i*0.1, 0, 1.5), size=[0.05, 0.05])
        leaf_uuids.append(uuid)

    # Fruits (spheres)
    fruit_uuids = []
    for i in range(3):
        uuid = context.addPatch(center=vec3(i*0.3, 0.5, 1.5), size=[0.08, 0.08])
        fruit_uuids.append(uuid)

    # Soil surface (ground)
    ground_uuids = []
    for i in range(5):
        uuid = context.addPatch(center=vec3(i*0.5, 0, 0), size=[0.5, 0.5])
        ground_uuids.append(uuid)

    with BoundaryLayerConductanceModel(context) as bl_model:
        # Apply appropriate models
        bl_model.setBoundaryLayerModel("InclinedPlate", uuids=leaf_uuids)
        bl_model.setBoundaryLayerModel("Sphere", uuids=fruit_uuids)
        bl_model.setBoundaryLayerModel("Ground", uuids=ground_uuids)

        # Calculate for all surfaces
        bl_model.run()
```

### Selective Calculation

```python
from pyhelios import Context, BoundaryLayerConductanceModel
from pyhelios.types import *

with Context() as context:
    # Add many patches
    all_uuids = []
    for i in range(20):
        uuid = context.addPatch(center=vec3(i*0.1, 0, 1), size=[0.05, 0.05])
        all_uuids.append(uuid)

    with BoundaryLayerConductanceModel(context) as bl_model:
        bl_model.setBoundaryLayerModel("InclinedPlate")

        # Only calculate for subset of primitives
        subset = all_uuids[5:15]
        bl_model.run(uuids=subset)
```

### Error Handling

```python
from pyhelios import Context, BoundaryLayerConductanceModel, BoundaryLayerConductanceModelError

with Context() as context:
    leaf_uuid = context.addPatch(center=vec3(0, 0, 1), size=[0.1, 0.1])

    try:
        with BoundaryLayerConductanceModel(context) as bl_model:
            # This will raise ValueError (invalid model name)
            bl_model.setBoundaryLayerModel("InvalidModel")

    except ValueError as e:
        print(f"Invalid model name: {e}")

    except BoundaryLayerConductanceModelError as e:
        print(f"Plugin error: {e}")
        # Error messages include rebuild instructions
```

## Message Control

Control console output:

```python
with BoundaryLayerConductanceModel(context) as bl_model:
    # Enable detailed output
    bl_model.enableMessages()

    # ... perform calculations ...

    # Disable output
    bl_model.disableMessages()
```
