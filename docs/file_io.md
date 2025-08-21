# File I/O {#IO}

Comprehensive guide to loading and saving data in PyHelios, including geometry files, simulation data, and configuration.

## Supported File Formats

### Geometry Files
- **PLY**: Stanford Triangle Format (preferred for 3D meshes)
- **OBJ**: Wavefront OBJ format
- **XML**: Helios XML format for complex scenes

### Data Files
- **CSV**: Comma-separated values for tabular data
- **TXT**: Plain text data files
- **JSON**: Configuration and metadata

## Loading Geometry

### PLY Files
```python
from pyhelios import Context

context = Context()

# Load PLY file
uuids = context.loadPLY("models/plant.ply")
print(f"Loaded {len(uuids)} primitives from PLY file")

# Load with transformations
origin = DataTypes.vec3(5, 0, 0)
rotation = DataTypes.SphericalCoord(1.0, 0, 1.57)  # 90 degrees
color = DataTypes.RGBcolor(0.3, 0.7, 0.3)

uuids = context.loadPLY(
    "leaf.ply",
    origin=origin,
    rotation=rotation,
    color=color
)
```

### OBJ Files
```python
# Load OBJ file
uuids = context.loadOBJ("models/tree.obj")

# OBJ files support material loading
uuids = context.loadOBJ(
    "textured_plant.obj",
    silent=True
)
```

### XML Scene Files
```python
# Load complex Helios XML scenes
context.load_xml("scenes/canopy_scene.xml")

# XML files can contain multiple objects, lighting, and configuration
```

## Saving Geometry

### Export to PLY
```python
# Export all geometry
context.export_ply("output/simulation.ply")

# Export specific primitives
leaf_uuids = context.get_patches()
context.export_ply("output/leaves.ply", leaf_uuids)

# Export with associated data
context.export_ply(
    "output/with_data.ply",
    include_data=True,
    data_fields=["temperature", "radiation_flux"]
)
```

### Export to OBJ
```python
# Export with materials
context.export_obj(
    "output/scene.obj", 
    include_materials=True
)

# Export specific object collections
tree_uuids = context.get_object_primitives("tree_001")
context.export_obj("output/tree.obj", tree_uuids)
```

## Data I/O Operations

### Primitive Data
```python
# Save primitive data to CSV
all_uuids = context.get_all_uuids()
data_fields = ["temperature", "area", "radiation_flux"]

context.export_primitive_data(
    "output/simulation_data.csv",
    all_uuids,
    data_fields
)

# Load data from CSV
context.load_primitive_data(
    "input/measured_data.csv",
    uuid_column="primitive_id",
    data_columns=["measured_temp", "leaf_area"]
)
```

### Global Data
```python
# Save simulation parameters
global_data = {
    "simulation_time": 3600,
    "ambient_temperature": 25.0,
    "wind_speed": 2.5,
    "solar_elevation": 45.0
}

context.save_global_data("output/parameters.json", global_data)

# Load global parameters
loaded_data = context.load_global_data("input/parameters.json")
for key, value in loaded_data.items():
    context.set_global_data(key, value)
```

## Advanced I/O Operations

### Batch Loading
```python
import glob

# Load multiple files
ply_files = glob.glob("models/leaves/*.ply")
all_uuids = []

for i, file in enumerate(ply_files):
    # Position each leaf differently
    position = DataTypes.vec3(i * 2, 0, 0)
    uuids = context.loadPLY(file, origin=position)
    all_uuids.extend(uuids)

print(f"Loaded {len(all_uuids)} primitives from {len(ply_files)} files")
```

### Streaming Large Datasets
```python
# For very large datasets, load sequentially
# Note: PyHelios doesn't have streaming - process files individually
for i, large_file in enumerate(large_ply_files):
    uuids = context.loadPLY(large_file, origin=DataTypes.vec3(i * 10, 0, 0))
    # Process loaded geometry
    for uuid in uuids:
            # Add data or perform operations
            context.set_primitive_data(uuid, "processed", True)
```

### Memory-Efficient Export
```python
# Export large datasets in chunks
all_uuids = context.get_all_uuids()
chunk_size = 10000

for i in range(0, len(all_uuids), chunk_size):
    chunk_uuids = all_uuids[i:i+chunk_size]
    chunk_file = f"output/chunk_{i//chunk_size:04d}.ply"
    context.export_ply(chunk_file, chunk_uuids)
```

## File Format Details

### PLY Format
PLY files store:
- Vertex positions (x, y, z)
- Face connectivity (vertex indices)
- Vertex colors (red, green, blue)
- Custom properties and data

### Helios XML Format
XML files can contain:
- Multiple geometric objects
- Material definitions
- Lighting configurations
- Simulation parameters
- Plugin configurations

## Error Handling

```python
from pyhelios.exceptions import HeliosFileIOError

try:
    uuids = context.load_ply("nonexistent.ply")
except HeliosFileIOError as e:
    print(f"Failed to load file: {e}")
    # Handle missing file

try:
    context.export_ply("output/data.ply")
except HeliosFileIOError as e:
    print(f"Failed to save file: {e}")
    # Handle write permissions or disk space issues
```

## Performance Tips

### Large File Loading
```python
# Use binary format when available
uuids = context.load_ply("large_file.ply", binary=True)

# Load only geometry, skip materials for faster loading
uuids = context.load_obj("complex.obj", load_materials=False)
```

### Export Optimization
```python
# Use binary PLY for faster writes
context.export_ply("output.ply", binary=True)

# Compress output files
context.export_ply("output.ply", compression=True)
```

### Memory Management
```python
# Clear unused data before large operations
context.clear_primitive_data(["temporary_field"])

# Monitor memory usage
print(f"Memory usage: {context.get_memory_usage_mb()} MB")
```
