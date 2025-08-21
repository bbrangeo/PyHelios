# Development Mode {#MockMode}

PyHelios includes a comprehensive mock mode that enables development and testing without requiring native libraries. This is perfect for development workflows, CI/CD, and cross-platform compatibility.

## What is Mock Mode?

Mock mode provides:
- **Full API compatibility** without native libraries
- **Development and testing** on any platform
- **CI/CD integration** without complex build requirements
- **Cross-platform development** before native library availability

## Enabling Mock Mode

### Environment Variable
```bash
# Enable mock mode globally
export PYHELIOS_DEV_MODE=1

# In Python
import os
os.environ['PYHELIOS_DEV_MODE'] = '1'
```

### Programmatic Control
```python
from pyhelios import dev_utils

# Enable mock mode
dev_utils.enable_mock_mode()

# Check current mode
if dev_utils.is_mock_mode():
    print("Running in mock mode")

# Disable mock mode
dev_utils.disable_mock_mode()
```

## Mock Mode Behavior

### API Compatibility
All PyHelios APIs work in mock mode with realistic return values:

```python
from pyhelios import Context, WeberPennTree, WPTType

# This works in mock mode
context = Context()
wpt = WeberPennTree(context)

# Mock functions return realistic UUIDs
tree_uuid = wpt.build_tree(WPTType.LEMON)
print(f"Mock tree UUID: {tree_uuid}")  # Returns valid UUID

# Mock geometry operations
patch_uuid = context.add_patch(center=(0,0,0), size=(1,1))
area = context.get_primitive_area(patch_uuid)
print(f"Mock area: {area}")  # Returns reasonable value
```

### Fail-Fast Philosophy
Mock mode follows PyHelios's fail-fast philosophy:

```python
from pyhelios import RadiationModel
from pyhelios.exceptions import HeliosMockModeError

try:
    # This will raise an explicit error in mock mode
    with RadiationModel(context) as radiation:
        radiation.run_band("SW")
except HeliosMockModeError as e:
    print(f"Mock mode limitation: {e}")
    # Error includes instructions for using real functionality
```

## Development Workflows

### Local Development
```python
# Development script that works with or without native libraries
import os
from pyhelios import Context

# Automatically use mock mode for development
if not os.path.exists("/path/to/native/libraries"):
    os.environ['PYHELIOS_DEV_MODE'] = '1'

context = Context()
# Your development code here...
```

### Testing Integration
```python
import pytest
from pyhelios import dev_utils

@pytest.fixture
def mock_context():
    """Fixture that provides mock context for testing."""
    dev_utils.enable_mock_mode()
    yield Context()
    dev_utils.disable_mock_mode()

def test_geometry_operations(mock_context):
    """Test that works in mock mode."""
    patch_uuid = mock_context.add_patch(center=(0,0,0), size=(1,1))
    assert patch_uuid is not None
    
    area = mock_context.get_primitive_area(patch_uuid)
    assert area > 0
```

### CI/CD Integration
```yaml
# GitHub Actions example
name: PyHelios Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -e .
          
      - name: Run tests in mock mode
        env:
          PYHELIOS_DEV_MODE: 1
        run: |
          pytest -m cross_platform
```

## Mock Data and Responses

### Realistic Mock Data
Mock mode provides realistic responses:

```python
context = Context()

# Mock geometry with realistic properties
patch_uuid = context.add_patch(center=(1, 2, 3), size=(2, 4))

# Realistic mock responses
center = context.get_primitive_center(patch_uuid)  # Returns (1, 2, 3)
area = context.get_primitive_area(patch_uuid)      # Returns 8.0 (2*4)
normal = context.get_primitive_normal(patch_uuid)  # Returns (0, 0, 1)
```

### Mock Plugin Behavior
```python
from pyhelios.plugins import get_plugin_info

# Mock mode reports no plugins available
info = get_plugin_info()
print(f"Mock plugins: {info['available_plugins']}")  # Returns []

# Plugin availability checks work correctly
if context.is_plugin_available('radiation'):
    print("This won't print in mock mode")
else:
    print("Radiation plugin not available in mock mode")
```

## Error Handling in Mock Mode

### Clear Error Messages
```python
from pyhelios import RadiationModel
from pyhelios.exceptions import HeliosMockModeError

try:
    radiation = RadiationModel(context)
    radiation.run_band("SW")
except HeliosMockModeError as e:
    # Error includes helpful information
    print(f"""
    Mock Mode Error: {e}
    
    To use real radiation modeling:
    1. Build native libraries: build_scripts/build_helios --profile gpu-accelerated
    2. Disable mock mode: unset PYHELIOS_DEV_MODE
    3. Ensure CUDA is available
    """)
```

### Graceful Degradation
```python
from pyhelios import Context, dev_utils

def create_radiation_simulation():
    """Function that works in both mock and real mode."""
    context = Context()
    
    if dev_utils.is_mock_mode():
        print("Running simulation preview in mock mode")
        # Use simplified algorithms for preview
        return run_mock_simulation(context)
    else:
        print("Running full GPU simulation")
        # Use real radiation modeling
        return run_gpu_simulation(context)
```

## Testing Strategies

### Multi-Mode Testing
```python
import pytest
from pyhelios import dev_utils

@pytest.mark.parametrize("mock_mode", [True, False])
def test_context_creation(mock_mode):
    """Test context creation in both modes."""
    if mock_mode:
        dev_utils.enable_mock_mode()
    else:
        dev_utils.disable_mock_mode()
    
    context = Context()
    assert context is not None
    
    # Test basic operations
    patch_uuid = context.add_patch(center=(0,0,0), size=(1,1))
    assert patch_uuid is not None
```

### Mock-Specific Tests
```python
@pytest.mark.mock_mode
def test_mock_specific_behavior():
    """Test behavior specific to mock mode."""
    dev_utils.enable_mock_mode()
    
    context = Context()
    
    # Test that mock mode is detected
    assert dev_utils.is_mock_mode()
    
    # Test that expensive operations are mocked
    with pytest.raises(HeliosMockModeError):
        from pyhelios import RadiationModel
        radiation = RadiationModel(context)
        radiation.run_band("SW")
```

## Development Tools

### Mock Mode Utilities
```python
from pyhelios import dev_utils

# Check current environment
print(f"Mock mode: {dev_utils.is_mock_mode()}")
print(f"Native libraries: {dev_utils.native_libraries_available()}")
print(f"Platform: {dev_utils.get_platform_info()}")

# Generate mock data for testing
mock_data = dev_utils.generate_mock_geometry(num_patches=100)
print(f"Generated {len(mock_data)} mock primitives")

# Mock performance timing
with dev_utils.mock_timer("simulation"):
    # Your simulation code here
    pass
# Prints realistic timing information
```

### Development Helpers
```python
from pyhelios.dev_utils import DevelopmentHelper

helper = DevelopmentHelper()

# Auto-detect best mode for current environment
recommended_mode = helper.recommend_mode()
print(f"Recommended mode: {recommended_mode}")

# Set up development environment
helper.setup_development_environment()

# Generate example data
helper.create_sample_scene("test_scene.json")
```

## Best Practices

### When to Use Mock Mode
- **Development**: Early stages without native libraries
- **Testing**: Unit tests and CI/CD pipelines
- **Prototyping**: Quick API exploration
- **Documentation**: Examples that run anywhere

### When NOT to Use Mock Mode
- **Production**: Real simulations need native libraries
- **Performance testing**: Mock mode doesn't reflect real performance
- **GPU validation**: Testing GPU-specific functionality
- **Final validation**: Before deployment

### Hybrid Approaches
```python
def smart_simulation(use_gpu=None):
    """Automatically choose best available mode."""
    if use_gpu is None:
        # Auto-detect capabilities
        use_gpu = (not dev_utils.is_mock_mode() and 
                  context.is_plugin_available('radiation'))
    
    if use_gpu:
        return run_gpu_simulation()
    else:
        return run_cpu_simulation()
```