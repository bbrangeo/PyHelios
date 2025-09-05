# StomatalConductance Documentation {#StomatalConductanceDoc}

## Overview

StomatalConductanceModel provides comprehensive stomatal conductance modeling and gas exchange calculations using five validated stomatal response models. This plugin enables accurate simulation of plant-atmosphere interactions and water-carbon coupling in plant physiological studies.

The plugin implements five different stomatal conductance models:

- **BWB (Ball-Woodrow-Berry, 1987)**: Classic stomatal response model with linear CO₂ and humidity dependence
- **BBL (Ball-Berry-Leuning, 1990, 1995)**: Enhanced model including vapor pressure deficit (VPD) response
- **MOPT (Medlyn et al., 2011)**: Optimality-based model derived from water use efficiency principles  
- **BMF (Buckley-Mott-Farquhar)**: Mechanistic model based on leaf energy balance and transpiration
- **BB (Bailey)**: Hydraulic-based model incorporating turgor pressure and water transport

## System Requirements

- **Platforms**: Windows, Linux, macOS
- **Dependencies**: None (pure computational plugin)
- **GPU**: Not required
- **Memory**: Minimal overhead

## Installation

### Build with StomatalConductanceModel

```bash
# Using interactive selection
build_scripts/build_helios --interactive

# Explicit selection
build_scripts/build_helios --plugins stomatalconductance

# With multiple plugins
build_scripts/build_helios --plugins stomatalconductance,energybalance,photosynthesis

# Check if available
python -c "from pyhelios.plugins import print_plugin_status; print_plugin_status()"
```

## Quick Start

```python
from pyhelios import Context, StomatalConductanceModel, BMFCoefficients

# Create context and add leaf geometry
with Context() as context:
    leaf_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
    
    with StomatalConductanceModel(context) as stomatal:
        # Use species library for quick setup
        stomatal.setBMFCoefficientsFromLibrary("Almond")
        
        # Run steady-state calculation
        stomatal.run()
        
        # Run dynamic simulation with timestep
        stomatal.run(dt=60.0)  # 60 second timestep
        
        # Set custom coefficients for specific leaves
        bmf_coeffs = BMFCoefficients(Em=258.25, i0=38.65, k=232916.82, b=609.67)
        stomatal.setBMFCoefficients(bmf_coeffs, uuids=[leaf_uuid])
```

## API Reference

### StomatalConductanceModel Class

#### Constructor

```python
StomatalConductanceModel(context: Context)
```

Initialize StomatalConductanceModel with a Helios context.

**Parameters:**
- `context`: Active Helios Context instance

**Raises:**
- `TypeError`: If context is not a Context instance
- `StomatalConductanceModelError`: If plugin not available
- `RuntimeError`: If initialization fails

#### Core Execution Methods

##### run

```python
run(uuids: Optional[List[int]] = None, dt: Optional[float] = None) -> None
```

Execute stomatal conductance calculations with flexible execution modes.

**Execution Modes:**
- `run()`: Steady state for all primitives
- `run(dt=60.0)`: Dynamic with timestep for all primitives  
- `run(uuids=[1, 2, 3])`: Steady state for specific primitives
- `run(uuids=[1, 2, 3], dt=60.0)`: Dynamic with timestep for specific primitives

**Parameters:**
- `uuids`: Optional list of primitive UUIDs to process
- `dt`: Optional timestep in seconds for dynamic simulation

**Raises:**
- `ValueError`: If parameters are invalid
- `StomatalConductanceModelError`: If calculation fails

### Model Coefficient Methods

#### Ball-Woodrow-Berry (BWB) Model

```python
setBWBCoefficients(coeffs: BWBCoefficients, uuids: Optional[List[int]] = None) -> None
```

Set BWB model coefficients: gs = gs0 + a1 × An × hs / cs

**Parameters:**
- `coeffs.gs0`: Minimum stomatal conductance (mol/m²/s)
- `coeffs.a1`: Sensitivity parameter (dimensionless)
- `uuids`: Optional list of primitive UUIDs

**Example:**
```python
from pyhelios import BWBCoefficients
bwb_coeffs = BWBCoefficients(gs0=0.0733, a1=9.422)
stomatal.setBWBCoefficients(bwb_coeffs)
```

#### Ball-Berry-Leuning (BBL) Model

```python
setBBLCoefficients(coeffs: BBLCoefficients, uuids: Optional[List[int]] = None) -> None
```

Set BBL model coefficients with VPD response: gs = gs0 + a1 × An × hs / (cs × (1 + Ds/D0))

**Parameters:**
- `coeffs.gs0`: Minimum stomatal conductance (mol/m²/s)
- `coeffs.a1`: Sensitivity parameter (dimensionless)
- `coeffs.D0`: VPD response parameter (mmol/mol)
- `uuids`: Optional list of primitive UUIDs

**Example:**
```python
from pyhelios import BBLCoefficients
bbl_coeffs = BBLCoefficients(gs0=0.0743, a1=4.265, D0=14570.0)
stomatal.setBBLCoefficients(bbl_coeffs)
```

#### Medlyn Optimality (MOPT) Model

```python
setMOPTCoefficients(coeffs: MOPTCoefficients, uuids: Optional[List[int]] = None) -> None
```

Set MOPT model coefficients based on marginal water use efficiency: gs = gs0 + (1 + g1/√Ds) × An/cs

**Parameters:**
- `coeffs.gs0`: Minimum stomatal conductance (mol/m²/s)  
- `coeffs.g1`: Marginal water use efficiency parameter ((kPa)^0.5)
- `uuids`: Optional list of primitive UUIDs

**Example:**
```python
from pyhelios import MOPTCoefficients
mopt_coeffs = MOPTCoefficients(gs0=0.0825, g1=2.637)
stomatal.setMOPTCoefficients(mopt_coeffs)
```

#### Buckley-Mott-Farquhar (BMF) Model

```python
setBMFCoefficients(coeffs: BMFCoefficients, uuids: Optional[List[int]] = None) -> None
```

Set BMF model coefficients based on leaf energy balance and transpiration.

**Parameters:**
- `coeffs.Em`: Maximum transpiration rate (mmol/m²/s)
- `coeffs.i0`: Minimum radiation threshold (μmol/m²/s)
- `coeffs.k`: Light response parameter (μmol/m²/s·mmol/mol)
- `coeffs.b`: Humidity response parameter (mmol/mol)
- `uuids`: Optional list of primitive UUIDs

**Example:**
```python
from pyhelios import BMFCoefficients  
bmf_coeffs = BMFCoefficients(Em=258.25, i0=38.65, k=232916.82, b=609.67)
stomatal.setBMFCoefficients(bmf_coeffs)
```

#### Bailey (BB) Model

```python
setBBCoefficients(coeffs: BBCoefficients, uuids: Optional[List[int]] = None) -> None
```

Set BB model coefficients based on hydraulic regulation and turgor pressure.

**Parameters:**
- `coeffs.pi_0`: Turgor pressure at full closure (MPa)
- `coeffs.pi_m`: Turgor pressure at full opening (MPa) 
- `coeffs.theta`: Light saturation parameter (μmol/m²/s)
- `coeffs.sigma`: Shape parameter (dimensionless)
- `coeffs.chi`: Hydraulic conductance parameter (mol/m²/s/MPa)
- `uuids`: Optional list of primitive UUIDs

**Example:**
```python
from pyhelios import BBCoefficients
bb_coeffs = BBCoefficients(pi_0=1.0, pi_m=1.67, theta=211.22, sigma=0.4408, chi=2.076)
stomatal.setBBCoefficients(bb_coeffs)
```

### Species Library Methods

#### setBMFCoefficientsFromLibrary

```python
setBMFCoefficientsFromLibrary(species: str, uuids: Optional[List[int]] = None) -> None
```

Set BMF coefficients using the built-in species library with pre-calibrated values.

**Available Species:**
- **Tree crops**: Almond, Apple, Avocado, Cherry, Lemon, Orange, Peach, Pear, Plum, Walnut
- **Vine crops**: Grape
- **Other**: Olive

**Parameters:**
- `species`: Species name from library
- `uuids`: Optional list of primitive UUIDs

**Example:**
```python
# Use species library for common plants
stomatal.setBMFCoefficientsFromLibrary("Almond")

# Apply to specific leaves only  
stomatal.setBMFCoefficientsFromLibrary("Grape", uuids=[leaf1_uuid, leaf2_uuid])
```

### Dynamic Time Constants

#### setDynamicTimeConstants

```python
setDynamicTimeConstants(tau_open: float, tau_close: float, uuids: Optional[List[int]] = None) -> None
```

Configure time constants for dynamic stomatal opening and closing responses.

**Parameters:**
- `tau_open`: Time constant for stomatal opening (seconds)
- `tau_close`: Time constant for stomatal closing (seconds)  
- `uuids`: Optional list of primitive UUIDs

**Typical Values:**
- Fast response: tau_open = 60s, tau_close = 120s
- Moderate response: tau_open = 120s, tau_close = 240s
- Slow response: tau_open = 300s, tau_close = 600s

**Example:**
```python
# Set time constants for all leaves
stomatal.setDynamicTimeConstants(tau_open=120.0, tau_close=240.0)

# Faster response for sun leaves
stomatal.setDynamicTimeConstants(tau_open=60.0, tau_close=120.0, uuids=sun_leaf_uuids)
```

### Utility Methods

#### optionalOutputPrimitiveData

```python
optionalOutputPrimitiveData(label: str) -> None
```

Add optional output primitive data to the Context for result analysis.

**Common Output Variables:**
- `"gs"`: Stomatal conductance (mol/m²/s)
- `"Ci"`: Intercellular CO₂ concentration (μmol/mol)  
- `"E"`: Transpiration rate (mmol/m²/s)
- `"A"`: Net photosynthesis rate (μmol/m²/s)
- `"WUE"`: Water use efficiency (μmol CO₂/mmol H₂O)

**Example:**
```python
# Output key gas exchange variables
stomatal.optionalOutputPrimitiveData("gs")
stomatal.optionalOutputPrimitiveData("Ci") 
stomatal.optionalOutputPrimitiveData("E")
```

#### printDefaultValueReport

```python
printDefaultValueReport(uuids: Optional[List[int]] = None) -> None
```

Print diagnostic report showing usage of default values for model parameters.

**Example:**
```python
# Report for all primitives
stomatal.printDefaultValueReport()

# Report for specific leaves
stomatal.printDefaultValueReport(uuids=[leaf1_uuid, leaf2_uuid])
```

## Examples

### Basic Stomatal Conductance Calculation

```python
from pyhelios import Context, StomatalConductanceModel

with Context() as context:
    # Create leaf geometry
    leaf_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
    
    with StomatalConductanceModel(context) as stomatal:
        # Use species library for quick setup
        stomatal.setBMFCoefficientsFromLibrary("Almond")
        
        # Add output variables
        stomatal.optionalOutputPrimitiveData("gs")
        stomatal.optionalOutputPrimitiveData("Ci")
        
        # Run steady-state calculation
        stomatal.run()
        
        # Get results
        gs_values = context.getPrimitiveData(leaf_uuid, "gs")
        ci_values = context.getPrimitiveData(leaf_uuid, "Ci")
        
        print(f"Stomatal conductance: {gs_values} mol/m²/s")
        print(f"Intercellular CO2: {ci_values} μmol/mol")
```

### Dynamic Stomatal Response Simulation

```python
from pyhelios import Context, StomatalConductanceModel
from pyhelios.types import SphericalCoord

with Context() as context:
    # Create multiple leaves with different orientations
    leaf_uuids = []
    for angle in [0, 30, 60, 90]:  # degrees
        leaf_uuid = context.addPatch(
            center=[0, 0, 1], 
            size=[0.1, 0.1],
            rotation=SphericalCoord(1, 0, angle)  # radius=1, elevation=0, azimuth=angle
        )
        leaf_uuids.append(leaf_uuid)
    
    with StomatalConductanceModel(context) as stomatal:
        # Set coefficients using species library
        stomatal.setBMFCoefficientsFromLibrary("Grape")
        
        # Configure dynamic response
        stomatal.setDynamicTimeConstants(tau_open=120.0, tau_close=300.0)
        
        # Add output variables
        stomatal.optionalOutputPrimitiveData("gs")
        stomatal.optionalOutputPrimitiveData("E")
        
        # Simulate timesteps
        timestep = 60.0  # 60 seconds
        for t in range(0, 3600, 60):  # 1 hour simulation
            stomatal.run(dt=timestep)
            
            # Get current values
            for i, leaf_uuid in enumerate(leaf_uuids):
                gs = context.getPrimitiveData(leaf_uuid, "gs")
                print(f"Time {t}s, Leaf {i}: gs = {gs} mol/m²/s")
```

### Multi-Model Comparison

```python
from pyhelios import (Context, StomatalConductanceModel, 
                     BWBCoefficients, BBLCoefficients, MOPTCoefficients)

with Context() as context:
    leaf_uuid = context.addPatch(center=[0, 0, 1], size=[0.1, 0.1])
    
    with StomatalConductanceModel(context) as stomatal:
        # Add output variable
        stomatal.optionalOutputPrimitiveData("gs")
        
        models = {
            "BWB": BWBCoefficients(gs0=0.0733, a1=9.422),
            "BBL": BBLCoefficients(gs0=0.0743, a1=4.265, D0=14570.0),
            "MOPT": MOPTCoefficients(gs0=0.0825, g1=2.637)
        }
        
        results = {}
        
        # Test each model
        for model_name, coeffs in models.items():
            if model_name == "BWB":
                stomatal.setBWBCoefficients(coeffs)
            elif model_name == "BBL":
                stomatal.setBBLCoefficients(coeffs)
            elif model_name == "MOPT":
                stomatal.setMOPTCoefficients(coeffs)
            
            stomatal.run()
            gs = context.getPrimitiveData(leaf_uuid, "gs")
            results[model_name] = gs
            
        # Compare results
        for model_name, gs in results.items():
            print(f"{model_name} model: gs = {gs} mol/m²/s")
```

### Integration with Tree Geometry

```python
from pyhelios import Context, WeberPennTree, WPTType, StomatalConductanceModel

with Context() as context:
    # Generate tree geometry
    with WeberPennTree(context) as wpt:
        tree_id = wpt.buildTree(WPTType.ALMOND)
    
    # Get leaf UUIDs (assumes all UUIDs in context are leaves)
    leaf_uuids = context.getAllUUIDs()
    
    with StomatalConductanceModel(context) as stomatal:
        # Set species-appropriate coefficients
        stomatal.setBMFCoefficientsFromLibrary("Almond")
        
        # Configure for tree-scale simulation  
        stomatal.setDynamicTimeConstants(tau_open=180.0, tau_close=360.0)
        
        # Add output variables
        stomatal.optionalOutputPrimitiveData("gs")
        stomatal.optionalOutputPrimitiveData("E")
        stomatal.optionalOutputPrimitiveData("WUE")
        
        # Run for all leaves
        stomatal.run()
        
        # Analyze results by canopy position
        total_transpiration = 0
        for leaf_uuid in leaf_uuids:
            E = context.getPrimitiveData(leaf_uuid, "E")
            total_transpiration += E
            
        print(f"Total tree transpiration: {total_transpiration} mmol/s")
```

## Error Handling

```python
from pyhelios import Context, StomatalConductanceModel, StomatalConductanceModelError

with Context() as context:
    try:
        with StomatalConductanceModel(context) as stomatal:
            # This will show proper error handling
            stomatal.setBMFCoefficientsFromLibrary("NonexistentSpecies")
            
    except StomatalConductanceModelError as e:
        print(f"Plugin error: {e}")
        # Error messages include available species and troubleshooting
        
    except ValueError as e:
        print(f"Parameter error: {e}")
        # Validation errors for invalid coefficients or parameters
```

## Troubleshooting

### Plugin Not Available

If you see "StomatalConductanceModel not available" errors:

1. Check plugin status:
   ```bash
   python -c "from pyhelios.plugins import print_plugin_status; print_plugin_status()"
   ```

2. Rebuild with plugin:
   ```bash
   build_scripts/build_helios --clean --plugins stomatalconductance
   ```

3. Verify no dependencies required (plugin should work on all platforms)

### Model Parameter Issues

**Invalid coefficients:**
- All conductance values (gs0) must be non-negative
- Time constants must be positive
- VPD parameters (D0) must be positive
- Check coefficient units and typical ranges

**Species not found:**
- Use exact species names: "Almond", "Apple", "Grape", etc.
- Case-sensitive species names
- Limited to pre-calibrated species in library

### Runtime Calculation Errors

**NaN or infinite values:**
- Check input environmental conditions (temperature, humidity, radiation)
- Ensure primitive data has required variables (CO2, light, etc.)
- Validate that Context contains proper environmental setup

**Slow convergence:**
- Check dynamic time constants are appropriate for timestep
- Ensure dt << min(tau_open, tau_close) for stability
- Very stiff equations may need smaller timesteps

## Performance Notes

**Computational Efficiency:**
- Stomatal conductance calculations are lightweight compared to radiation models
- Linear scaling with number of primitives
- Dynamic models have minimal overhead over steady-state

**Memory Usage:**
- Minimal memory footprint
- Coefficient storage scales with number of unique primitive coefficient sets
- No GPU memory requirements

**Recommended Usage:**
- Use species library when available for validated coefficients
- Steady-state calculations for instantaneous values
- Dynamic simulations for transient behavior and diurnal cycles
- Combine with energy balance models for coupled heat-water-carbon calculations

## Limitations

**Environmental Requirements:**
- Requires environmental conditions (temperature, humidity, CO₂, radiation) as primitive data
- Some models need specific micrometeorological variables
- Limited to C3 photosynthesis (no C4/CAM plant support)

**Model Scope:**
- Individual leaf/patch scale (not whole-plant hydraulics)
- Empirical models may not extrapolate beyond calibration conditions  
- Species library limited to common temperate tree and vine crops

**Integration Constraints:**
- Works best with energy balance and photosynthesis plugins
- Some models require coupling with radiation calculations
- Dynamic simulations need appropriate timestep selection