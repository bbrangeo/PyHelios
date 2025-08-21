# Plugin System {#Plugins}

PyHelios currently provides 3 major plugins accessible through Python bindings, with additional functionality integrated into the core Context class.

## Currently Implemented Plugins

These plugins are fully implemented and documented:

- **[Radiation Model](RadiationDoc.html)** - GPU-accelerated radiation modeling and ray tracing
- **[Visualizer](VisualizerDoc.html)** - OpenGL-based 3D visualization and rendering
- **[Weber-Penn Tree](WeberPennTreeDoc.html)** - Procedural tree generation using Weber-Penn algorithms

## Plugin Architecture

PyHelios uses a flexible plugin-based architecture that automatically detects available functionality:

```python
from pyhelios import Context

# Context automatically reports available plugins
context = Context()
# Output: "PyHelios Context created with 5 available plugins: weberpenntree, canopygenerator, visualizer..."

# Check specific plugin availability
if context.is_plugin_available('radiation'):
    print("GPU radiation modeling available")
else:
    print("Radiation plugin requires --profile gpu-accelerated build")
```

## Plugin Categories

### Core Functionality (Always Available)
- **weberpenntree**: Procedural tree generation
- **canopygenerator**: Plant canopy generation  
- **solarposition**: Solar calculations

### Visualization and Analysis
- **visualizer**: OpenGL 3D visualization
- **radiation**: OptiX-accelerated ray tracing (requires GPU)

### Future Plugins

The following 16 plugins from the Helios ecosystem will be added to PyHelios in future releases:

**Physics Modeling:**
- energybalance: Plant energy balance calculations
- photosynthesis: Photosynthesis modeling
- leafoptics: Leaf optical properties (PROSPECT model)
- stomatalconductance: Stomatal conductance modeling
- boundarylayerconductance: Boundary layer conductance
- planthydraulics: Plant hydraulic modeling

**Analysis and Simulation:**
- lidar: LiDAR simulation and point cloud processing
- aeriallidar: Aerial LiDAR simulation with GPU acceleration
- plantarchitecture: Advanced plant structure modeling
- voxelintersection: Voxel intersection operations
- syntheticannotation: Synthetic data annotation
- parameteroptimization: Parameter optimization algorithms
- collisiondetection: Collision detection with GPU support

**Tools and Utilities:**
- projectbuilder: GUI project builder with ImGui

## Plugin Discovery

```bash
# Check plugin status and availability
python -m pyhelios.plugins status

# Discover optimal configuration for your system
python -m pyhelios.plugins discover

# Get information about specific plugins
python -m pyhelios.plugins info radiation

# Validate plugin configuration
python -m pyhelios.plugins validate --plugins radiation,visualizer
```

## Build Configuration

Control which plugins are built using the flexible build system:

```bash
# Use predefined profiles
build_scripts/build_helios --profile standard

# Custom plugin selection
build_scripts/build_helios --plugins weberpenntree,canopygenerator,visualizer

# Interactive selection
build_scripts/build_helios --interactive
```

For detailed build instructions, see the [Plugin System](PluginSystem.html) documentation.
