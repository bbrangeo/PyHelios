# Radiation Model Plugin {#RadiationDoc}

The Radiation Model plugin provides GPU-accelerated ray tracing for radiation simulation using OptiX. This documentation is based on the actual implementation.

## Overview

The \ref pyhelios.RadiationModel.RadiationModel "RadiationModel class" provides advanced radiation modeling and ray tracing capabilities for realistic light interaction simulations in plant canopies and scenes.

## Requirements

The radiation plugin requires:
- NVIDIA GPU with CUDA support
- CUDA Toolkit installed
- OptiX runtime (bundled with PyHelios)

## Basic Usage

```python
from pyhelios import Context, RadiationModel
from pyhelios.types import *

# Create context with geometry
context = Context()
patch_uuid = context.addPatch(
    center=vec3(0, 0, 0),
    size=vec2(2, 2),
    color=RGBcolor(0.3, 0.7, 0.2)
)

# Use RadiationModel with context manager (recommended)
with RadiationModel(context) as radiation:
    # Add radiation band
    radiation.addRadiationBand("PAR")
    
    # Add radiation source
    source_id = radiation.addCollimatedRadiationSource()
    radiation.setSourceFlux(source_id, "PAR", 1000.0)
    
    # Configure ray counts
    radiation.setDirectRayCount("PAR", 100)
    radiation.setDiffuseRayCount("PAR", 300)
    
    # Run simulation
    radiation.runBand("PAR")
    
    # Get results
    results = radiation.getTotalAbsorbedFlux()
    print(f"Total absorbed flux: {sum(results)} W")
```

## Radiation Bands

### Basic Band Management

```python
# Add radiation bands (verified methods)
radiation.addRadiationBand("PAR")
radiation.addRadiationBand("NIR")
radiation.addRadiationBand("SW")

# Add band with wavelength bounds
radiation.addRadiationBand("custom", wavelength_min=400.0, wavelength_max=700.0)

# Copy existing band
radiation.copyRadiationBand("PAR", "PAR_copy")
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
    radiation.addRadiationBand(band)
    print(f"Added {band}: {description}")
```

## Radiation Sources

### Collimated Sources

```python
# Default collimated source (verified methods)
source_id = radiation.addCollimatedRadiationSource()

# Source with specific direction vector
source_id = radiation.addCollimatedRadiationSource(
    direction=(0.3, 0.3, -0.9)  # Sun angle
)

# Set source flux
radiation.setSourceFlux(source_id, "PAR", 1200.0)  # W/m²
```

### Spherical Sources

```python
# Spherical radiation source
source_id = radiation.addSphereRadiationSource(
    position=(0, 0, 10),  # x, y, z position
    radius=0.5            # Source radius
)

# Set flux for spherical source
radiation.setSourceFlux(source_id, "PAR", 800.0)
```

### Sun Sources

```python
# Realistic sun modeling
sun_id = radiation.addSunSphereRadiationSource(
    radius=0.5,           # Sun disc radius
    zenith=45.0,          # Sun zenith angle (degrees)
    azimuth=180.0,        # Sun azimuth angle (degrees)
    position_scaling=1.0, # Position scaling factor
    angular_width=0.53,   # Sun angular width (degrees)
    flux_scaling=1.0      # Flux scaling factor
)

# Set solar flux
radiation.setSourceFlux(sun_id, "PAR", 1200.0)
```

## Flux Configuration

### Source Flux Management

```python
# Single source flux
radiation.setSourceFlux(source_id, "PAR", 1000.0)

# Multiple sources with same flux
source_ids = [source1, source2, source3]
radiation.setSourceFlux(source_ids, "PAR", 800.0)

# Get current source flux
current_flux = radiation.getSourceFlux(source_id, "PAR")
print(f"Source flux: {current_flux} W/m²")

# Diffuse radiation flux
radiation.setDiffuseRadiationFlux("PAR", 200.0)
```

## Ray Configuration

### Ray Count Settings

```python
# Configure ray counts for accuracy vs. performance
radiation.setDirectRayCount("PAR", 1000)    # Direct rays
radiation.setDiffuseRayCount("PAR", 3000)   # Diffuse rays

# Higher ray counts for better accuracy
radiation.setDirectRayCount("PAR", 5000)
radiation.setDiffuseRayCount("PAR", 10000)
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
radiation.setDirectRayCount("PAR", config["direct"])
radiation.setDiffuseRayCount("PAR", config["diffuse"])
```

## Advanced Configuration

### Scattering Control

```python
# Set scattering depth (number of bounces)
radiation.setScatteringDepth("PAR", 3)

# Set minimum scatter energy threshold
radiation.setMinScatterEnergy("PAR", 0.01)
```

### Emission Control

```python
# Enable/disable emission for thermal radiation
radiation.enableEmission("thermal")
radiation.disableEmission("PAR")  # PAR typically doesn't emit
```

## Simulation Execution

### Geometry Updates

```python
# Update all geometry before simulation
radiation.updateGeometry()

# Update specific geometry UUIDs
radiation.updateGeometry([patch_uuid, triangle_uuid])
```

### Running Simulations

**CRITICAL PERFORMANCE NOTE**: When simulating multiple radiation bands, **ALWAYS** run all bands in a single `runBand()` call rather than sequential single-band calls. This provides **significant computational efficiency gains** (often 2-5x faster) because:

- GPU ray tracing setup is performed once for all bands
- Scene geometry acceleration structures are reused across bands
- OptiX kernel launches are batched together
- Memory transfers between CPU/GPU are minimized
- Ray traversal computations are shared between spectral bands

```python
# ✅ EFFICIENT - Single call for multiple bands (RECOMMENDED)
radiation.runBand(["PAR", "NIR", "SW"])

# ❌ INEFFICIENT - Sequential single-band calls (AVOID)
radiation.runBand("PAR")    # Full GPU setup overhead
radiation.runBand("NIR")    # Full GPU setup overhead again  
radiation.runBand("SW")     # Full GPU setup overhead again

# Single band execution (when only one band needed)
radiation.runBand("PAR")
```

### Performance Comparison

```python
import time

# Method 1: Sequential calls (SLOW)
start_time = time.time()
radiation.runBand("PAR")
radiation.runBand("NIR") 
radiation.runBand("SW")
sequential_time = time.time() - start_time

# Method 2: Multi-band call (FAST)
start_time = time.time()
radiation.runBand(["PAR", "NIR", "SW"])
multiband_time = time.time() - start_time

print(f"Sequential: {sequential_time:.2f}s")
print(f"Multi-band: {multiband_time:.2f}s") 
print(f"Speedup: {sequential_time/multiband_time:.1f}x faster")
```

## Results and Analysis

### Flux Results

```python
# Get total absorbed flux for all primitives
results = radiation.getTotalAbsorbedFlux()
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
radiation_data = radiation.getTotalAbsorbedFlux()

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
from pyhelios import Context, WeberPennTree, WPTType, RadiationModel
from pyhelios.types import *

# Create scene
context = Context()

# Add ground plane
ground_uuid = context.addPatch(
    center=vec3(0, 0, 0),
    size=vec2(10, 10),
    color=RGBcolor(0.3, 0.2, 0.1)
)

# Generate tree
wpt = WeberPennTree(context)
tree_id = wpt.buildTree(WPTType.LEMON)

# Run radiation simulation
try:
    with RadiationModel(context) as radiation:
        # Configure multiple radiation bands for comprehensive analysis
        radiation.addRadiationBand("PAR")  # Photosynthetically Active Radiation
        radiation.addRadiationBand("NIR")  # Near Infrared
        radiation.addRadiationBand("SW")   # Total Shortwave
        
        # Add sun
        sun_id = radiation.addSunSphereRadiationSource(
            radius=0.5,
            zenith=30.0,    # Morning sun
            azimuth=135.0   # Southeast
        )
        
        # Configure sources for all bands
        radiation.setSourceFlux(sun_id, "PAR", 600.0)  # W/m² PAR
        radiation.setSourceFlux(sun_id, "NIR", 500.0)  # W/m² NIR  
        radiation.setSourceFlux(sun_id, "SW", 1200.0)  # W/m² Total SW
        
        # Add diffuse sky radiation for all bands
        radiation.setDiffuseRadiationFlux("PAR", 100.0)
        radiation.setDiffuseRadiationFlux("NIR", 80.0)
        radiation.setDiffuseRadiationFlux("SW", 200.0)
        
        # Configure simulation quality for all bands
        for band in ["PAR", "NIR", "SW"]:
            radiation.setDirectRayCount(band, 2000)
            radiation.setDiffuseRayCount(band, 6000)
            radiation.setScatteringDepth(band, 2)
        
        # Run simulation - EFFICIENT multi-band execution
        radiation.updateGeometry()
        radiation.runBand(["PAR", "NIR", "SW"])  # Single call for all bands!
        
        # Analyze results
        results = radiation.getTotalAbsorbedFlux()
        
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
        
        # Access band-specific data stored by radiation model
        for band in ["PAR", "NIR", "SW"]:
            print(f"Band {band} results available in primitive data: radiation_flux_{band}")

```

### Data Storage

```python
# Store radiation results as primitive data
results = radiation.getTotalAbsorbedFlux()
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

## Camera and Image Functions (v1.3.47)

The RadiationModel now includes advanced camera functionality for generating synthetic images, object detection training data, and auto-calibrated imagery.

### Camera Image Generation

```python
# Basic camera image writing (returns output filename)
filename = radiation.write_camera_image(
    camera="overhead_camera",
    bands=["Red", "Green", "Blue"],
    imagefile_base="scene_rgb",
    image_path="./images",
    frame=-1  # All frames
)
print(f"Camera image saved to: {filename}")

# Normalized camera images  
filename = radiation.write_norm_camera_image(
    camera="side_camera",
    bands=["NIR", "Red"], 
    imagefile_base="false_color",
    image_path="./output"
)

# Camera image data in ASCII format
radiation.write_camera_image_data(
    camera="overhead_camera",
    band="RGB",
    imagefile_base="raw_data",
    image_path="./data"
)
```

### Object Detection Training Data

Generate YOLO-format bounding boxes for machine learning training:

```python
# Single primitive data label
radiation.write_image_bounding_boxes(
    camera_label="training_camera",
    primitive_data_labels="leaf_type",
    object_class_ids=1,  # Class ID for "leaf"
    image_file="training_001.jpg",
    classes_txt_file="plant_classes.txt",
    image_path="./annotations"
)

# Multiple primitive data labels for multi-class detection
radiation.write_image_bounding_boxes(
    camera_label="training_camera", 
    primitive_data_labels=["leaves", "stems", "fruits"],
    object_class_ids=[0, 1, 2],  # Different class IDs
    image_file="training_002.jpg",
    classes_txt_file="classes.txt"
)

# Object-based bounding boxes (entire objects)
radiation.write_image_bounding_boxes(
    camera_label="training_camera",
    object_data_labels=["tree_1", "tree_2", "shrub_1"], 
    object_class_ids=[10, 10, 20],  # Tree class=10, Shrub class=20
    image_file="training_003.jpg"
)
```

### Segmentation Masks for Instance Segmentation

Generate COCO-format JSON files for semantic/instance segmentation:

```python
# Single primitive segmentation
radiation.write_image_segmentation_masks(
    camera_label="segmentation_camera",
    primitive_data_labels="plant_part",
    object_class_ids=1,
    json_filename="segmentation_001.json",
    image_file="seg_image_001.jpg",
    append_file=False
)

# Multiple primitive classes in one image
radiation.write_image_segmentation_masks(
    camera_label="segmentation_camera",
    primitive_data_labels=["leaf", "bark", "soil"],
    object_class_ids=[1, 2, 3],
    json_filename="multi_class_seg.json", 
    image_file="scene_segmentation.jpg",
    append_file=True  # Add to existing annotations
)

# Object-level segmentation
radiation.write_image_segmentation_masks(
    camera_label="segmentation_camera",
    object_data_labels=["individual_plant_1", "individual_plant_2"],
    object_class_ids=[100, 101],  # Unique instance IDs
    json_filename="instance_segmentation.json",
    image_file="plant_instances.jpg"
)
```

### Auto-Calibrated Camera Images

Automatic color correction for realistic imagery:

```python
# Basic auto-calibration with default settings
filename = radiation.auto_calibrate_camera_image(
    camera_label="rgb_camera",
    red_band_label="Red",
    green_band_label="Green", 
    blue_band_label="Blue",
    output_file_path="auto_calibrated_image.jpg"
)

# Advanced auto-calibration with quality report
filename = radiation.auto_calibrate_camera_image(
    camera_label="multispectral_camera",
    red_band_label="Band_670nm",
    green_band_label="Band_550nm",
    blue_band_label="Band_450nm", 
    output_file_path="calibrated_multispectral.jpg",
    print_quality_report=True,
    algorithm="MATRIX_3X3_AUTO",  # or "DIAGONAL_ONLY", "MATRIX_3X3_FORCE"
    ccm_export_file_path="color_correction_matrix.txt"
)
print(f"Calibrated image saved to: {filename}")
```

### Color Correction Algorithms

Choose the appropriate algorithm based on your needs:

```python
algorithms = {
    "DIAGONAL_ONLY": "Simple white balance correction (fastest)",
    "MATRIX_3X3_AUTO": "Full 3x3 matrix with stability fallback (recommended)",
    "MATRIX_3X3_FORCE": "Force 3x3 matrix even if potentially unstable"
}

# Test different algorithms
for algorithm, description in algorithms.items():
    filename = radiation.auto_calibrate_camera_image(
        camera_label="test_camera",
        red_band_label="R", green_band_label="G", blue_band_label="B",
        output_file_path=f"calibrated_{algorithm.lower()}.jpg",
        algorithm=algorithm
    )
    print(f"{algorithm}: {description} -> {filename}")
```

### Complete Camera Pipeline Example

```python
from pyhelios import Context, WeberPennTree, WPTType, RadiationModel
from pyhelios.types import *

# Create scene with labeled geometry
context = Context()

# Generate tree with data labels
wpt = WeberPennTree(context)
tree_id = wpt.buildTree(WPTType.APPLE)

# Label tree components for ML training
leaf_uuids = wpt.getLeafUUIDs(tree_id)
branch_uuids = wpt.getBranchUUIDs(tree_id)

for uuid in leaf_uuids:
    context.setPrimitiveDataString(uuid, "plant_part", "leaf")
    context.setPrimitiveDataString(uuid, "species", "apple")
    
for uuid in branch_uuids:
    context.setPrimitiveDataString(uuid, "plant_part", "branch") 
    context.setPrimitiveDataString(uuid, "species", "apple")

# Add ground with labels
ground = context.addPatch(center=vec3(0,0,0), size=vec2(10,10))
context.setPrimitiveDataString(ground, "plant_part", "soil")

# Run radiation simulation with cameras
try:
    with RadiationModel(context) as radiation:
        # Set up radiation bands
        radiation.addRadiationBand("Red")
        radiation.addRadiationBand("Green") 
        radiation.addRadiationBand("Blue")
        radiation.addRadiationBand("NIR")
        
        # Add sun source
        sun_id = radiation.addSunSphereRadiationSource(
            radius=0.5, zenith=45.0, azimuth=180.0)
        
        # Configure realistic solar spectrum
        radiation.setSourceFlux(sun_id, "Red", 250.0)
        radiation.setSourceFlux(sun_id, "Green", 350.0)
        radiation.setSourceFlux(sun_id, "Blue", 200.0)
        radiation.setSourceFlux(sun_id, "NIR", 400.0)
        
        # Run simulation
        radiation.updateGeometry()
        radiation.runBand(["Red", "Green", "Blue", "NIR"])
        
        # Generate camera images
        rgb_filename = radiation.write_camera_image(
            camera="overhead_rgb",
            bands=["Red", "Green", "Blue"],
            imagefile_base="apple_tree_rgb"
        )
        
        nir_filename = radiation.write_camera_image(
            camera="side_view", 
            bands=["NIR"],
            imagefile_base="apple_tree_nir"
        )
        
        # Generate training data for object detection
        radiation.write_image_bounding_boxes(
            camera_label="overhead_rgb",
            primitive_data_labels=["leaf", "branch", "soil"],
            object_class_ids=[0, 1, 2],  # leaf=0, branch=1, soil=2
            image_file=rgb_filename,
            classes_txt_file="plant_classes.txt"
        )
        
        # Generate segmentation masks 
        radiation.write_image_segmentation_masks(
            camera_label="overhead_rgb",
            primitive_data_labels=["leaf", "branch", "soil"],
            object_class_ids=[0, 1, 2],
            json_filename="apple_tree_segmentation.json",
            image_file=rgb_filename
        )
        
        # Create auto-calibrated realistic image
        calibrated_filename = radiation.auto_calibrate_camera_image(
            camera_label="overhead_rgb",
            red_band_label="Red",
            green_band_label="Green", 
            blue_band_label="Blue",
            output_file_path="apple_tree_calibrated.jpg",
            print_quality_report=True
        )
        
        print("Camera pipeline completed:")
        print(f"  RGB Image: {rgb_filename}")
        print(f"  NIR Image: {nir_filename}") 
        print(f"  Calibrated: {calibrated_filename}")
        print(f"  Training data: plant_classes.txt + YOLO format labels")
        print(f"  Segmentation: apple_tree_segmentation.json")
        
except RadiationModelError as e:
    print(f"Camera processing failed: {e}")
```

### Camera Function Error Handling

```python
try:
    # Camera functions with comprehensive error handling
    filename = radiation.write_camera_image(
        camera="test_camera",
        bands=["R", "G", "B"],
        imagefile_base="test"
    )
    
except TypeError as e:
    print(f"Parameter error: {e}")
    # Handle invalid parameter types
    
except ValueError as e:
    print(f"Value error: {e}")  
    # Handle invalid parameter values (e.g., both primitive and object labels)
    
except RuntimeError as e:
    print(f"Camera operation failed: {e}")
    # Handle camera or image generation failures
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

## Build Requirements

```bash
# Build with radiation plugin
build_scripts/build_helios --plugins radiation

# Or use GPU profile
build_scripts/build_helios --plugins radiation

# Check if radiation is available
python -c "from pyhelios.plugins import get_plugin_registry; print(get_plugin_registry().is_plugin_available('radiation'))"
```

This documentation covers the actual RadiationModel implementation in PyHelios, verified against the wrapper code and high-level interface.