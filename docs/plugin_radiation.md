# Radiation Model Plugin {#RadiationDoc}

The Radiation Model plugin provides GPU-accelerated ray tracing for radiation simulation using OptiX. This documentation is based on the actual implementation.

## Overview

The RadiationModel class provides advanced radiation modeling and ray tracing capabilities for realistic light interaction simulations in plant canopies and scenes.

## Requirements

The radiation plugin requires:
- NVIDIA GPU with CUDA support
- CUDA Toolkit installed
- OptiX runtime (bundled with PyHelios)

## Basic Usage

```python
from pyhelios import Context, RadiationModel, RadiationModelError
from pyhelios import DataTypes

# Create context with geometry
context = Context()
patch_uuid = context.addPatch(
    center=DataTypes.vec3(0, 0, 0),
    size=DataTypes.vec2(2, 2),
    color=DataTypes.RGBcolor(0.3, 0.7, 0.2)
)

# Use RadiationModel with context manager (recommended)
with RadiationModel(context) as radiation:
    # Add radiation band
    radiation.add_radiation_band("PAR")
    
    # Add radiation source
    source_id = radiation.add_collimated_radiation_source()
    radiation.set_source_flux(source_id, "PAR", 1000.0)
    
    # Configure ray counts
    radiation.set_direct_ray_count("PAR", 100)
    radiation.set_diffuse_ray_count("PAR", 300)
    
    # Run simulation
    radiation.run_band("PAR")
    
    # Get results
    results = radiation.get_total_absorbed_flux()
    print(f"Total absorbed flux: {sum(results)} W")
```

## Radiation Bands

### Basic Band Management

```python
# Add radiation bands (verified methods)
radiation.add_radiation_band("PAR")
radiation.add_radiation_band("NIR")
radiation.add_radiation_band("SW")

# Add band with wavelength bounds
radiation.add_radiation_band_with_wavelengths("custom", 400.0, 700.0)

# Copy existing band
radiation.copy_radiation_band("PAR", "PAR_copy")
```

### Common Radiation Bands

```python
# Standard radiation bands for plant modeling
bands = {
    "PAR": "Photosynthetically Active Radiation (400-700 nm)",
    "NIR": "Near Infrared (700-1100 nm)", 
    "SW": "Shortwave (300-3000 nm)",
    "UV": "Ultraviolet (280-400 nm)",
    "VIS": "Visible (380-750 nm)"
}

for band, description in bands.items():
    radiation.add_radiation_band(band)
    print(f"Added {band}: {description}")
```

## Radiation Sources

### Collimated Sources

```python
# Default collimated source (verified methods)
source_id = radiation.add_collimated_radiation_source()

# Source with specific direction vector
source_id = radiation.add_collimated_radiation_source(
    direction=(0.3, 0.3, -0.9)  # Sun angle
)

# Set source flux
radiation.set_source_flux(source_id, "PAR", 1200.0)  # W/m²
```

### Spherical Sources

```python
# Spherical radiation source
source_id = radiation.add_sphere_radiation_source(
    position=(0, 0, 10),  # x, y, z position
    radius=0.5            # Source radius
)

# Set flux for spherical source
radiation.set_source_flux(source_id, "PAR", 800.0)
```

### Sun Sources

```python
# Realistic sun modeling
sun_id = radiation.add_sun_sphere_radiation_source(
    radius=0.5,           # Sun disc radius
    zenith=45.0,          # Sun zenith angle (degrees)
    azimuth=180.0,        # Sun azimuth angle (degrees)
    position_scaling=1.0, # Position scaling factor
    angular_width=0.53,   # Sun angular width (degrees)
    flux_scaling=1.0      # Flux scaling factor
)

# Set solar flux
radiation.set_source_flux(sun_id, "PAR", 1200.0)
```

## Flux Configuration

### Source Flux Management

```python
# Single source flux
radiation.set_source_flux(source_id, "PAR", 1000.0)

# Multiple sources with same flux
source_ids = [source1, source2, source3]
radiation.set_source_flux_multiple(source_ids, "PAR", 800.0)

# Get current source flux
current_flux = radiation.get_source_flux(source_id, "PAR")
print(f"Source flux: {current_flux} W/m²")

# Diffuse radiation flux
radiation.set_diffuse_radiation_flux("PAR", 200.0)
```

## Ray Configuration

### Ray Count Settings

```python
# Configure ray counts for accuracy vs. performance
radiation.set_direct_ray_count("PAR", 1000)    # Direct rays
radiation.set_diffuse_ray_count("PAR", 3000)   # Diffuse rays

# Higher ray counts for better accuracy
radiation.set_direct_ray_count("PAR", 5000)
radiation.set_diffuse_ray_count("PAR", 10000)
```

### Ray Count Guidelines

```python
# Performance vs accuracy trade-offs
ray_configs = {
    "fast": {"direct": 100, "diffuse": 300},
    "standard": {"direct": 1000, "diffuse": 3000}, 
    "high_quality": {"direct": 5000, "diffuse": 15000},
    "research": {"direct": 10000, "diffuse": 30000}
}

# Apply configuration
config = ray_configs["standard"]
radiation.set_direct_ray_count("PAR", config["direct"])
radiation.set_diffuse_ray_count("PAR", config["diffuse"])
```

## Advanced Configuration

### Scattering Control

```python
# Set scattering depth (number of bounces)
radiation.set_scattering_depth("PAR", 3)

# Set minimum scatter energy threshold
radiation.set_min_scatter_energy("PAR", 0.01)
```

### Emission Control

```python
# Enable/disable emission for thermal radiation
radiation.enable_emission("thermal")
radiation.disable_emission("PAR")  # PAR typically doesn't emit
```

## Simulation Execution

### Geometry Updates

```python
# Update all geometry before simulation
radiation.update_geometry()

# Update specific geometry UUIDs
radiation.update_geometry([patch_uuid, triangle_uuid])
```

### Running Simulations

```python
# Run single band
radiation.run_band("PAR")

# Run multiple bands
radiation.run_bands(["PAR", "NIR", "SW"])
```

## Results and Analysis

### Flux Results

```python
# Get total absorbed flux for all primitives
results = radiation.get_total_absorbed_flux()
total_absorption = sum(results)
print(f"Total absorbed flux: {total_absorption:.2f} W")

# Analyze results per primitive
all_uuids = context.getAllUUIDs()
for i, uuid in enumerate(all_uuids):
    if i < len(results):
        flux = results[i]
        area = context.getPrimitiveArea(uuid)
        flux_density = flux / area if area > 0 else 0
        print(f"Primitive {uuid}: {flux:.2f} W ({flux_density:.2f} W/m²)")
```

### Radiation Analysis

```python
# Calculate radiation statistics
radiation_data = radiation.get_total_absorbed_flux()

import statistics
mean_flux = statistics.mean(radiation_data)
max_flux = max(radiation_data)
min_flux = min(radiation_data)
std_flux = statistics.stdev(radiation_data)

print(f"Radiation statistics:")
print(f"  Mean: {mean_flux:.2f} W")
print(f"  Max: {max_flux:.2f} W") 
print(f"  Min: {min_flux:.2f} W")
print(f"  Std Dev: {std_flux:.2f} W")
```

## Complete Workflow Example

```python
from pyhelios import Context, WeberPennTree, WPTType, RadiationModel, DataTypes

# Create scene
context = Context()

# Add ground plane
ground_uuid = context.addPatch(
    center=DataTypes.vec3(0, 0, 0),
    size=DataTypes.vec2(10, 10),
    color=DataTypes.RGBcolor(0.3, 0.2, 0.1)
)

# Generate tree
wpt = WeberPennTree(context)
tree_id = wpt.buildTree(WPTType.LEMON)

# Run radiation simulation
try:
    with RadiationModel(context) as radiation:
        # Configure radiation
        radiation.add_radiation_band("PAR")
        
        # Add sun
        sun_id = radiation.add_sun_sphere_radiation_source(
            radius=0.5,
            zenith=30.0,    # Morning sun
            azimuth=135.0   # Southeast
        )
        radiation.set_source_flux(sun_id, "PAR", 1200.0)
        
        # Add diffuse sky radiation
        radiation.set_diffuse_radiation_flux("PAR", 200.0)
        
        # Configure simulation quality
        radiation.set_direct_ray_count("PAR", 2000)
        radiation.set_diffuse_ray_count("PAR", 6000)
        radiation.set_scattering_depth("PAR", 2)
        
        # Run simulation
        radiation.update_geometry()
        radiation.run_band("PAR")
        
        # Analyze results
        results = radiation.get_total_absorbed_flux()
        
        # Get leaf-specific results
        leaf_uuids = wpt.getLeafUUIDs(tree_id)
        leaf_absorption = 0
        
        all_uuids = context.getAllUUIDs()
        for i, uuid in enumerate(all_uuids):
            if uuid in leaf_uuids and i < len(results):
                leaf_absorption += results[i]
        
        print(f"Total scene absorption: {sum(results):.2f} W")
        print(f"Leaf absorption: {leaf_absorption:.2f} W")
        print(f"Ground absorption: {results[all_uuids.index(ground_uuid)]:.2f} W")
        
except RadiationModelError as e:
    print(f"Radiation simulation failed: {e}")
```

## Integration with Other Components

### With WeberPennTree

```python
# Generate tree and analyze radiation interception
tree_id = wpt.buildTree(WPTType.OLIVE)

# Run radiation
radiation.run_band("PAR")
results = radiation.get_total_absorbed_flux()

# Calculate tree radiation budget
leaf_uuids = wpt.getLeafUUIDs(tree_id)
branch_uuids = wpt.getBranchUUIDs(tree_id)

total_leaf_interception = 0
total_branch_interception = 0

all_uuids = context.getAllUUIDs()
for i, uuid in enumerate(all_uuids):
    if i < len(results):
        if uuid in leaf_uuids:
            total_leaf_interception += results[i]
        elif uuid in branch_uuids:
            total_branch_interception += results[i]

print(f"Leaf interception: {total_leaf_interception:.2f} W")
print(f"Branch interception: {total_branch_interception:.2f} W")
```

### Data Storage

```python
# Store radiation results as primitive data
results = radiation.get_total_absorbed_flux()
all_uuids = context.getAllUUIDs()

for i, uuid in enumerate(all_uuids):
    if i < len(results):
        # Store flux data
        context.setPrimitiveDataFloat(uuid, "radiation_flux_PAR", results[i])
        
        # Calculate flux density
        area = context.getPrimitiveArea(uuid)
        flux_density = results[i] / area if area > 0 else 0
        context.setPrimitiveDataFloat(uuid, "flux_density_PAR", flux_density)

# Use for visualization
context.colorPrimitiveByDataPseudocolor(
    all_uuids, "flux_density_PAR", "hot", 256
)
```

## Error Handling

```python
from pyhelios.exceptions import HeliosGPUInitializationError

try:
    radiation = RadiationModel(context)
    
except RadiationModelError as e:
    print(f"RadiationModel initialization failed: {e}")
    
    # Check if GPU is available
    if "NVIDIA GPU" in str(e):
        print("Ensure NVIDIA GPU with CUDA support is available")
    elif "OptiX" in str(e):
        print("OptiX runtime error - check graphics drivers")
        
except HeliosGPUInitializationError as e:
    print(f"GPU initialization failed: {e}")
```

## Performance Optimization

```python
# Optimize for different scenarios
scenarios = {
    "interactive": {
        "direct_rays": 100,
        "diffuse_rays": 300,
        "scattering_depth": 1
    },
    "production": {
        "direct_rays": 2000,
        "diffuse_rays": 6000, 
        "scattering_depth": 2
    },
    "research": {
        "direct_rays": 10000,
        "diffuse_rays": 30000,
        "scattering_depth": 3
    }
}

# Apply scenario
scenario = scenarios["production"]
radiation.set_direct_ray_count("PAR", scenario["direct_rays"])
radiation.set_diffuse_ray_count("PAR", scenario["diffuse_rays"])
radiation.set_scattering_depth("PAR", scenario["scattering_depth"])
```

## Build Requirements

```bash
# Build with radiation plugin
build_scripts/build_helios --plugins radiation

# Or use GPU profile
build_scripts/build_helios --profile gpu-accelerated

# Check if radiation is available
python -c "from pyhelios.plugins import get_plugin_registry; print(get_plugin_registry().is_plugin_available('radiation'))"
```

This documentation covers the actual RadiationModel implementation in PyHelios, verified against the wrapper code and high-level interface.