# Solar Position Plugin Documentation {#SolarPositionDoc}

## Overview

The Solar Position plugin provides comprehensive solar position calculations and sun angle modeling for PyHelios. This plugin enables accurate solar geometry computations essential for radiation modeling, energy balance calculations, and photosynthesis simulations in plant canopy models.

Key features include:
- Precise solar position calculations based on date, time, and geographic location
- Sun direction vector computations for ray tracing applications
- Solar flux calculations with atmospheric corrections
- Sunrise and sunset time calculations
- Atmospheric parameter calibration from time series data

## System Requirements

- **Platforms**: Windows, Linux, macOS  
- **Dependencies**: None (uses standard mathematical functions)
- **GPU**: Not required
- **Memory**: Minimal memory footprint

## Installation

### Build with Solar Position Plugin

The Solar Position plugin is included in the default PyHelios build. If building explicitly:

```bash
# Using interactive selection
build_scripts/build_helios --interactive

# Explicit selection
build_scripts/build_helios --plugins solarposition

# Check if available
python -c "from pyhelios.plugins.registry import PluginRegistry; print('solarposition available:', PluginRegistry().is_plugin_available('solarposition'))"
```

## Quick Start

```python
from pyhelios import Context, SolarPosition

# Create context and solar position calculator
with Context() as context:
    # Set date and time
    context.setDate(year=2024, month=6, day=21)  # Summer solstice
    context.setTime(hour=12, minute=0, second=0)     # Noon
    
    # Create solar position calculator with coordinates (NYC)
    with SolarPosition(context, utc_offset=-5, latitude=40.7128, longitude=-74.0060) as solar:
        # Get sun elevation angle
        elevation = solar.getSunElevation()
        print(f"Sun elevation: {elevation:.2f} degrees")
        
        # Get sun direction vector
        direction = solar.getSunDirectionVector()
        print(f"Sun direction: ({direction.x:.3f}, {direction.y:.3f}, {direction.z:.3f})")
        
        # Calculate solar flux (standard atmospheric conditions)
        flux = solar.getSolarFlux(pressure_Pa=101325, temperature_K=288.15, 
                                 humidity_rel=0.6, turbidity=0.1)
        print(f"Solar flux: {flux:.2f} W/m²")
```

## Examples

### Daily Solar Path Analysis

```python
from pyhelios import Context, SolarPosition
import numpy as np
import matplotlib.pyplot as plt

with Context() as context:
    context.setDate(year=2024, month=6, day=21)  # Summer solstice
    
    # Create solar position with coordinates (Davis, CA)
    with SolarPosition(context, utc_offset=-8, latitude=38.5382, longitude=-121.7617) as solar:
        # Calculate sun path throughout the day
        hours = np.arange(5, 20, 0.5)  # 5 AM to 8 PM
        elevations = []
        azimuths = []
        
        for hour in hours:
            hour_int = int(hour)
            minute_int = int((hour - hour_int) * 60)
            context.setTime(hour=hour_int, minute=minute_int, second=0)
            
            elevation = solar.getSunElevation()
            azimuth = solar.getSunAzimuth()
            
            if elevation > 0:  # Sun above horizon
                elevations.append(elevation)
                azimuths.append(azimuth)
        
        # Plot solar path
        plt.figure(figsize=(10, 6))
        plt.subplot(1, 2, 1)
        plt.plot(hours[:len(elevations)], elevations)
        plt.xlabel('Hour of Day')
        plt.ylabel('Sun Elevation (degrees)')
        plt.title('Sun Elevation vs Time')
        
        plt.subplot(1, 2, 2)
        plt.plot(azimuths, elevations)
        plt.xlabel('Sun Azimuth (degrees)')
        plt.ylabel('Sun Elevation (degrees)')
        plt.title('Sun Path (Elevation vs Azimuth)')
        plt.show()
```

### Solar Flux Analysis

```python
from pyhelios import Context, SolarPosition

def analyze_solar_flux(latitude, longitude, year, month, day):
    """Analyze solar flux variation throughout a day."""
    
    with Context() as context:
        context.setDate(year=year, month=month, day=day)
        
        # Create solar position with provided coordinates  
        with SolarPosition(context, utc_offset=0, latitude=latitude, longitude=longitude) as solar:
            # Get sunrise/sunset times
            sunrise = solar.getSunriseTime()
            sunset = solar.getSunsetTime()
            
            print(f"Sunrise: {sunrise}")
            print(f"Sunset: {sunset}")
            # Calculate day length in hours
            day_length = (sunset.hour * 3600 + sunset.minute * 60 + sunset.second) - (sunrise.hour * 3600 + sunrise.minute * 60 + sunrise.second)
            print(f"Day length: {day_length / 3600:.2f} hours")
            
            # Calculate solar flux at key times
            key_times = [
                (sunrise.hour, sunrise.minute, 'Sunrise'),
                (12, 0, 'Noon'),
                (sunset.hour, sunset.minute, 'Sunset')
            ]
            
            for hour, minute, label in key_times:
                context.setTime(hour=hour, minute=minute, second=0)
                
                elevation = solar.getSunElevation()
                flux = solar.getSolarFlux(pressure_Pa=101325, temperature_K=288.15,
                                         humidity_rel=0.6, turbidity=0.1)
                
                print(f"{label}: Elevation = {elevation:.1f}°, Flux = {flux:.0f} W/m²")

# Example usage
analyze_solar_flux(40.7128, -74.0060, 2024, 6, 21)  # NYC summer solstice
analyze_solar_flux(40.7128, -74.0060, 2024, 12, 21) # NYC winter solstice
```

### Error Handling

```python
from pyhelios import Context, SolarPosition, SolarPositionError

with Context() as context:
    try:
        # This will fail if coordinates not provided
        context.setDate(year=2024, month=7, day=15)
        context.setTime(hour=12, minute=0, second=0)
        with SolarPosition(context) as solar:
            elevation = solar.getSunElevation()
            
    except SolarPositionError as e:
        print(f"Solar position error: {e}")
        # Error messages include specific requirements
        
        # Retry with coordinates
        with SolarPosition(context, utc_offset=-8, latitude=40.0, longitude=-120.0) as solar:
            elevation = solar.getSunElevation()
            print(f"Sun elevation: {elevation:.2f}°")
```

## Algorithm Details

The Solar Position plugin implements standard solar geometry algorithms:

- **Solar declination**: Based on day of year using standard astronomical formulas
- **Hour angle**: Calculated from local solar time and longitude
- **Solar elevation/azimuth**: Standard spherical trigonometry calculations
- **Atmospheric corrections**: Air mass calculations for solar flux attenuation
- **Time calculations**: Sunrise/sunset based on solar elevation = 0° with refraction correction

These implementations follow established solar engineering practices and produce results accurate to within 0.1° for typical applications.