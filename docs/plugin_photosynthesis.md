# Photosynthesis Plugin Documentation {#PhotosynthesisDoc}

The Photosynthesis plugin provides comprehensive photosynthesis modeling capabilities for PyHelios, enabling simulation of plant carbon assimilation using both empirical and mechanistic models.

## Overview

The Photosynthesis plugin implements:
- **Empirical photosynthesis models** based on light response curves
- **Farquhar-von Caemmerer-Berry (FvCB) model** for mechanistic C3 photosynthesis simulation
- **Built-in species library** with parameters for 21+ plant species
- **Temperature response modeling** for photosynthetic parameters
- **Environmental factor integration** including CO₂, temperature, PAR, and conductance effects

## Key Features

### Multi-Model Support
- **Empirical Model**: Simple light response curve with saturation kinetics
- **FvCB Model**: Mechanistic model accounting for biochemical limitations of photosynthesis

### Species Library
The plugin includes a comprehensive species library with validated parameters:

**Tree Species**: ALMOND, APPLE, AVOCADO, CITRUS, LEMON, OLIVE, PEACH, WALNUT
**Crops**: BEAN, CORN, COTTON, SOYBEAN, TOMATO, WHEAT
**Other Plants**: GRAPE, LETTUCE, ROSE, STRAWBERRY, SUNFLOWER, CANOLA

Species names are case-insensitive and support aliases (e.g., "apple" → "APPLE").

### Environmental Integration
- Air temperature effects with Q10 temperature response
- CO₂ concentration effects (50-2000 ppm range)
- O₂ concentration effects (5-50% range)
- PAR (Photosynthetically Active Radiation) integration
- Stomatal conductance coupling

## Installation and Setup

### Building with Photosynthesis Plugin

```bash
# Build PyHelios with photosynthesis plugin
build_scripts/build_helios --plugins photosynthesis

# Or build with multiple plugins
build_scripts/build_helios --plugins radiation,photosynthesis,visualizer

# Check plugin availability
python -c "from pyhelios.plugins import get_plugin_info; print(get_plugin_info())"
```

### Import and Basic Usage

```python
from pyhelios import Context, PhotosynthesisModel
from pyhelios.types import PhotosyntheticTemperatureResponseParameters

# Create context and photosynthesis model
context = Context()
with PhotosynthesisModel(context) as photosynthesis:
    # Configure species
    photosynthesis.setSpecies("APPLE")
    
    # Set environmental conditions
    photosynthesis.setTemperature(25.0)      # °C
    photosynthesis.setCO2Concentration(400.0) # ppm
    photosynthesis.setPARFlux(1000.0)        # μmol m⁻² s⁻¹
    
    # Calculate photosynthesis
    rate = photosynthesis.calculatePhotosynthesis()
    print(f"Photosynthetic rate: {rate:.2f} μmol m⁻² s⁻¹")
```

## Usage Examples

### Example 1: Empirical Model

```python
from pyhelios import Context, PhotosynthesisModel
from pyhelios.types import EmpiricalModelCoefficients

context = Context()
with PhotosynthesisModel(context) as photosynthesis:
    # Configure empirical model
    coefficients = EmpiricalModelCoefficients(
        light_saturation_point=1000.0,    # μmol m⁻² s⁻¹
        light_compensation_point=50.0,    # μmol m⁻² s⁻¹
        quantum_efficiency=0.08,          # dimensionless
        maximum_rate=25.0                 # μmol m⁻² s⁻¹
    )
    
    photosynthesis.setEmpiricalModelCoefficients(coefficients)
    photosynthesis.setSpecies("APPLE")
    photosynthesis.setTemperature(25.0)
    photosynthesis.setCO2Concentration(400.0)
    photosynthesis.setPARFlux(800.0)
    
    # Calculate photosynthesis
    rate = photosynthesis.calculatePhotosynthesis()
    print(f"Empirical model rate: {rate:.2f} μmol m⁻² s⁻¹")
```

### Example 2: Farquhar Model

```python
from pyhelios import Context, PhotosynthesisModel
from pyhelios.types import FarquharModelCoefficients

context = Context()
with PhotosynthesisModel(context) as photosynthesis:
    # Configure Farquhar-von Caemmerer-Berry model
    coefficients = FarquharModelCoefficients(
        vcmax=100.0,                # μmol m⁻² s⁻¹
        jmax=180.0,                 # μmol m⁻² s⁻¹  
        tpu=10.0,                   # μmol m⁻² s⁻¹
        quantum_efficiency_II=0.85,  # dimensionless
        dark_respiration=2.0        # μmol m⁻² s⁻¹
    )
    
    photosynthesis.setFarquharModelCoefficients(coefficients)
    photosynthesis.setSpecies("SOYBEAN")
    photosynthesis.setTemperature(25.0)
    photosynthesis.setCO2Concentration(400.0)
    photosynthesis.setO2Concentration(21.0)
    photosynthesis.setPARFlux(1200.0)
    
    # Calculate photosynthesis
    rate = photosynthesis.calculatePhotosynthesis()
    conductance = photosynthesis.calculateStomatalConductance()
    transpiration = photosynthesis.calculateTranspiration()
    
    print(f"FvCB model rate: {rate:.2f} μmol m⁻² s⁻¹")
    print(f"Stomatal conductance: {conductance:.3f} mol m⁻² s⁻¹")
    print(f"Transpiration: {transpiration:.3f} mol m⁻² s⁻¹")
```

### Example 3: Temperature Response

```python
from pyhelios import Context, PhotosynthesisModel
from pyhelios.types import PhotosyntheticTemperatureResponseParameters

context = Context()
with PhotosynthesisModel(context) as photosynthesis:
    # Configure temperature response
    temp_params = PhotosyntheticTemperatureResponseParameters(
        optimal_temperature=25.0,         # °C
        maximum_temperature=45.0,         # °C
        minimum_temperature=5.0,          # °C
        temperature_coefficient_q10=2.0   # dimensionless
    )
    
    photosynthesis.setTemperatureResponseParameters(temp_params)
    photosynthesis.setSpecies("WHEAT")
    photosynthesis.setCO2Concentration(400.0)
    photosynthesis.setPARFlux(1000.0)
    
    # Test temperature response
    temperatures = [15.0, 20.0, 25.0, 30.0, 35.0]
    for temp in temperatures:
        photosynthesis.setTemperature(temp)
        rate = photosynthesis.calculatePhotosynthesis()
        print(f"Temperature {temp:4.1f}°C: {rate:6.2f} μmol m⁻² s⁻¹")
```

### Example 4: Primitive-Specific Calculations

```python
from pyhelios import Context, PhotosynthesisModel
from pyhelios.types import vec3, vec2, RGBcolor

# Create geometry
context = Context()
center = vec3(0, 0, 0)
size = vec2(1, 1)
color = RGBcolor(0.5, 0.8, 0.3)

# Add leaves as patches
leaf1_id = context.addPatch(center=center, size=size, color=color)
leaf2_id = context.addPatch(center=vec3(1, 1, 1), size=size, color=color)

with PhotosynthesisModel(context) as photosynthesis:
    # Configure model
    photosynthesis.setSpecies("APPLE")
    photosynthesis.setTemperature(25.0)
    photosynthesis.setCO2Concentration(400.0)
    photosynthesis.setPARFlux(1000.0)
    photosynthesis.setStomatalConductance(0.5)
    
    # Calculate for specific primitives
    rate1 = photosynthesis.calculatePhotosynthesisForPrimitives(leaf1_id)
    rates_multiple = photosynthesis.calculatePhotosynthesisForPrimitives([leaf1_id, leaf2_id])
    
    print(f"Leaf 1 rate: {rate1:.2f} μmol m⁻² s⁻¹")
    print(f"Multiple rates: {rates_multiple}")
    
    # Get stored rates
    stored_rate = photosynthesis.getPhotosynthesisRateForPrimitive(leaf1_id)
    stored_rates = photosynthesis.getPhotosynthesisRateForPrimitives([leaf1_id, leaf2_id])
    
    print(f"Stored rate: {stored_rate:.2f} μmol m⁻² s⁻¹")
    print(f"Stored rates: {stored_rates}")
```

### Parameter Structures

#### PhotosyntheticTemperatureResponseParameters
```python
@dataclass
class PhotosyntheticTemperatureResponseParameters:
    optimal_temperature: float      # °C, temperature for optimal photosynthesis
    maximum_temperature: float      # °C, upper temperature limit
    minimum_temperature: float      # °C, lower temperature limit 
    temperature_coefficient_q10: float  # Q10 temperature coefficient
```

#### EmpiricalModelCoefficients
```python
@dataclass
class EmpiricalModelCoefficients:
    light_saturation_point: float      # μmol m⁻² s⁻¹, PAR at saturation
    light_compensation_point: float    # μmol m⁻² s⁻¹, PAR at zero net photosynthesis
    quantum_efficiency: float          # dimensionless (0-1), initial slope
    maximum_rate: float                # μmol m⁻² s⁻¹, maximum photosynthetic rate
```

#### FarquharModelCoefficients  
```python
@dataclass
class FarquharModelCoefficients:
    vcmax: float                    # μmol m⁻² s⁻¹, maximum carboxylation rate
    jmax: float                     # μmol m⁻² s⁻¹, maximum electron transport rate
    tpu: float                      # μmol m⁻² s⁻¹, triose phosphate utilization
    quantum_efficiency_II: float    # dimensionless (0-1), PSII quantum efficiency
    dark_respiration: float         # μmol m⁻² s⁻¹, dark respiration rate
```

## Parameter Validation

The plugin includes comprehensive parameter validation:

### Temperature Validation
- **Range**: -50°C to +70°C
- **Rationale**: Covers physiological temperature range for plant life

### CO₂ Concentration Validation
- **Range**: 50-2000 ppm
- **Rationale**: From very low to extremely elevated atmospheric CO₂

### PAR Flux Validation
- **Range**: 0-3000 μmol m⁻² s⁻¹
- **Rationale**: From darkness to extreme high light conditions

### Conductance Validation
- **Range**: 0-2 mol m⁻² s⁻¹
- **Rationale**: From closed stomata to maximum conductance values

### Model Coefficient Validation
- **Vcmax**: 1-500 μmol m⁻² s⁻¹
- **Jmax**: Must be ≥ 1.2 × Vcmax (biochemical constraint)
- **Quantum Efficiency**: 0-1 (physical constraint)
- **Respiration**: 0-50 μmol m⁻² s⁻¹

## Error Handling

### Common Exceptions

```python
from pyhelios import PhotosynthesisModel, PhotosynthesisModelError
from pyhelios.validation.exceptions import ValidationError

try:
    photosynthesis = PhotosynthesisModel(context)
except PhotosynthesisModelError as e:
    if "plugin is not available" in str(e):
        print("Rebuild PyHelios with: build_scripts/build_helios --plugins photosynthesis")
    elif "mock mode" in str(e):
        print("Native libraries required - currently in mock mode")

try:
    photosynthesis.setSpecies("INVALID_SPECIES")
except ValidationError as e:
    print(f"Invalid species: {e}")
    available = photosynthesis.getAvailableSpecies()
    print(f"Available: {available}")
```

### Plugin Availability Check

```python
from pyhelios import PhotosynthesisModel

# Check if photosynthesis plugin is available
if PhotosynthesisModel is None:
    print("Photosynthesis plugin not available")
    print("Build with: build_scripts/build_helios --plugins photosynthesis")
else:
    print("Photosynthesis plugin available")
    print("Available species:", PhotosynthesisModel.get_available_species())
```

## Integration with Other Plugins

### With RadiationModel
```python
from pyhelios import Context, RadiationModel, PhotosynthesisModel

context = Context()
# Add geometry...

with RadiationModel(context) as radiation:
    # Configure radiation simulation
    radiation.add_radiation_band("PAR")
    radiation.add_collimated_radiation_source()
    radiation.run_band("PAR")
    
    # Get PAR flux results
    par_flux = radiation.get_flux_data("PAR")

with PhotosynthesisModel(context) as photosynthesis:
    # Use radiation results for photosynthesis
    for i, flux in enumerate(par_flux):
        photosynthesis.setPARFlux(flux)
        rate = photosynthesis.calculatePhotosynthesis()
        print(f"Primitive {i}: PAR={flux:.1f}, Rate={rate:.2f}")
```

### With EnergyBalanceModel
```python
from pyhelios import Context, EnergyBalanceModel, PhotosynthesisModel

context = Context()
# Add geometry...

with EnergyBalanceModel(context) as energy:
    energy.enableAirEnergyBalance()
    # Configure energy balance...

with PhotosynthesisModel(context) as photosynthesis:
    # Use temperature from energy balance
    leaf_temperature = energy.getLeafTemperature()
    photosynthesis.setTemperature(leaf_temperature)
    
    # Calculate photosynthesis with realistic leaf temperature
    rate = photosynthesis.calculatePhotosynthesis()
```

## Performance Considerations

### Batch Calculations
For multiple primitives, use batch methods:
```python
# Efficient for multiple primitives
rates = photosynthesis.calculatePhotosynthesisForPrimitives([uuid1, uuid2, uuid3])

# Less efficient
rate1 = photosynthesis.calculatePhotosynthesisForPrimitives(uuid1)
rate2 = photosynthesis.calculatePhotosynthesisForPrimitives(uuid2)  
rate3 = photosynthesis.calculatePhotosynthesisForPrimitives(uuid3)
```

### Model Configuration
Configure model parameters once when possible:
```python
# Configure once
photosynthesis.setSpecies("APPLE")
photosynthesis.setCO2Concentration(400.0)

# Then vary conditions efficiently
for temperature in temperature_range:
    photosynthesis.setTemperature(temperature)
    rate = photosynthesis.calculatePhotosynthesis()
```

## Troubleshooting

### Plugin Not Available
**Error**: "Photosynthesis plugin is not available"
**Solution**: 
```bash
build_scripts/build_helios --clean --plugins photosynthesis
```

### Mock Mode Operation
**Error**: "Currently running in mock mode"
**Solution**: Native libraries required. Build with:
```bash
build_scripts/build_helios --plugins photosynthesis
```

### Invalid Species
**Error**: ValidationError with species name
**Solution**: Check available species:
```python
available = PhotosynthesisModel.get_available_species()
aliases = PhotosynthesisModel.get_species_aliases()
```

### Parameter Out of Range
**Error**: ValidationError with parameter value
**Solution**: Check parameter ranges in API reference above

### Model Not Ready
**Error**: "Model is not ready for calculations"
**Solution**: Ensure required parameters are set:
```python
# Minimum required for calculations
photosynthesis.setSpecies("APPLE")
photosynthesis.setTemperature(25.0)
photosynthesis.setCO2Concentration(400.0)

# Check readiness
if photosynthesis.isModelReady():
    rate = photosynthesis.calculatePhotosynthesis()
```

## Scientific Background

### Empirical Model
The empirical model uses a rectangular hyperbola:
```
A = (α × I × Amax) / (α × I + Amax) - Rd
```
Where:
- A = Net photosynthesis
- α = Quantum efficiency (initial slope)
- I = Incident PAR
- Amax = Maximum photosynthetic rate
- Rd = Dark respiration

### Farquhar-von Caemmerer-Berry Model
The FvCB model calculates photosynthesis as the minimum of three rates:
- **Rubisco-limited**: Ac = (Vcmax × (Ci - Γ*)) / (Ci + Kc(1 + Oi/Ko))
- **RuBP-limited**: Aj = (J × (Ci - Γ*)) / (4Ci + 8Γ*)
- **TPU-limited**: Ap = 3 × TPU

Where Ci is intercellular CO₂, Γ* is CO₂ compensation point, and Kc, Ko are kinetic parameters.

### Temperature Response
Parameters follow Q10 temperature dependence:
```
Parameter(T) = Parameter(T_ref) × Q10^((T - T_ref)/10)
```

## References

1. Farquhar, G.D., von Caemmerer, S., Berry, J.A. (1980). A biochemical model of photosynthetic CO₂ assimilation in leaves of C3 species. Planta 149: 78-90.

2. von Caemmerer, S. (2000). Biochemical Models of Leaf Photosynthesis. CSIRO Publishing.

3. Medlyn, B.E., et al. (2002). Temperature response of parameters of a biochemically based model of photosynthesis. Plant, Cell & Environment 25: 1205-1216.