# Installation {#Installation}

This guide covers installing PyHelios on all supported platforms.

## Quick Install

For most users, the standard installation is:

```bash
git clone --recursive https://github.com/PlantSimulationLab/PyHelios.git
cd PyHelios/
pip install -e .
```

## Platform-Specific Installation

### Windows

**Prerequisites:**
- Visual Studio 2019+ or Build Tools for Visual Studio
- Python 3.7+

```bash
# Clone repository
git clone --recursive https://github.com/PlantSimulationLab/PyHelios.git
cd PyHelios/

# Build native libraries (optional - pre-built binaries included)
build_scripts/build_helios --profile standard

# Install PyHelios
pip install -e .
```

### macOS

**Prerequisites:**
- Xcode command line tools
- Python 3.7+

```bash
# Install Xcode command line tools
xcode-select --install

# Clone repository
git clone --recursive https://github.com/PlantSimulationLab/PyHelios.git
cd PyHelios/

# Build native libraries
build_scripts/build_helios --profile standard

# Install PyHelios
pip install -e .
```

### Linux (Ubuntu/Debian)

**Prerequisites:**
- Build essentials
- CMake
- Python 3.7+

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install build-essential cmake python3-dev

# Clone repository
git clone --recursive https://github.com/PlantSimulationLab/PyHelios.git
cd PyHelios/

# Build native libraries
build_scripts/build_helios --profile standard

# Install PyHelios
pip install -e .
```

## Development Installation

For development work:

```bash
# Install with development dependencies
pip install -e .[dev]

# Verify installation
pytest
```

## GPU Support

For GPU-accelerated radiation modeling:

```bash
# Install CUDA toolkit (varies by platform)
# Then build with GPU support
build_scripts/build_helios --profile gpu-accelerated
```

## Verification

Test your installation:

```python
from pyhelios import Context, DataTypes

# Create a basic context
context = Context()
print("PyHelios installed successfully!")

# Check available plugins
context.print_plugin_status()
```

## Troubleshooting

### Common Issues

**Import Error**: 
- Verify Python version: `python --version`
- Check installation: `pip list | grep pyhelios`

**Missing Native Libraries**:
- Build libraries: `build_scripts/build_helios`
- Check library path (Linux/macOS): `source pyhelios/setup_env.sh`

**Build Failures**:
- Windows: Ensure Visual Studio is installed
- macOS: Run `xcode-select --install`
- Linux: Install `build-essential cmake`

### Getting Help

- Check the [Troubleshooting](../README.md#troubleshooting) section
- Report issues on [GitHub](https://github.com/PlantSimulationLab/PyHelios/issues)