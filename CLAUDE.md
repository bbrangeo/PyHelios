# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MANDATORY WORKFLOW - FOLLOW EVERY SESSION

### 1. Start Every Session
- **TodoWrite**: Create todo list for complex/multi-step tasks (3+ steps or non-trivial tasks)
- **Memory Check**: Search memory for relevant prior knowledge using `mcp__memory__search_nodes`
- **Sub-Agent Selection**: Choose appropriate sub-agent(s) based on task type (see Sub-Agents section)

### 2. During Work
- **TodoWrite**: Update progress frequently - mark tasks in_progress and completed immediately
- **Memory Capture**: For any technical discoveries, solutions, or architectural insights, IMMEDIATELY document in memory using MCP tools

### 3. End Every Session
- **Memory Documentation**: MANDATORY - Create memory entities for:
  - Technical issues discovered and their solutions
  - Design decisions made or conventions established
  - Architectural insights about PyHelios systems
  - Integration patterns or debugging approaches
- **TodoWrite**: Mark final tasks as completed, clean up stale items
- **Verification**: Confirm all memory writes were successful

### 4. Memory Guidelines
**When to write memory (REQUIRED):**
- New technical problems discovered and solved
- Plugin integration insights or patterns
- Testing architecture discoveries (like ctypes contamination)
- Build system or configuration changes
- Performance insights or optimization approaches

**How to write memory:**
- Use `mcp__memory__create_entities` with specific entityType (technical_issue, solution, architecture, etc.)
- Create meaningful relations with `mcp__memory__create_relations`
- Write detailed observations that future sessions can reference

## Sub-Agents

- Make sure to familiarize yourself with the available sub-agents (@.claude/agents/) and use them efficiently:
  - context-gatherer: Expert code archaeologist and information synthesizer specializing in rapidly discovering, analyzing, and summarizing relevant context for development tasks.
  - research-specialist: Expert technical web researcher specializing in finding and evaluating open source codebases, scientific literature, and algorithmic implementation.
  - helios-cpp-expert: Specialist with deep knowledge of the Helios plant simulation software's native C++ codebase.
  - code-architect: Analyzes existing codebases holistically and create comprehensive implementation plans that consider architectural integrity, maintainability, and scalability.
  - debug-specialist: Expert software debugging specialist with deep C++ and cmake expertise.
  - code-reviewer: Code reviewer with deep knowledge of software engineering best practices, security principles, and maintainable code design.
  - test-coverage-maximizer: Writes tests that achieve maximum code coverage while ensuring robust functional testing that catches real bugs and edge cases.

## Virtual Environment

For development, create a virtual environment using your preferred method (venv, conda, etc.):

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or venv\Scripts\activate  # On Windows

# Using conda
conda create -n pyhelios python=3.9
conda activate pyhelios
```

## Project Overview

PyHelios provides cross-platform Python bindings for the Helios plant simulation software, offering a high-level interface for 3D plant modeling and simulation. The library uses ctypes with dynamic platform detection to interface with native C++ libraries and plugins.

**Cross-Platform Support**: 
- **Windows**: Full native support with pre-built DLLs
- **macOS/Linux**: Native support via build-from-source
- **Development Mode**: Mock mode for development on any platform without native libraries

## Development Commands

### Installation
```bash
pip install -e .
```

### Building Native Libraries

PyHelios now supports flexible plugin selection for customized builds based on your hardware and use case requirements.

#### Clean Helios-Style Project Structure

Following standard Helios C++ project conventions with strict separation of source and generated files:
- **pyhelios_build/** - Build source files (CMakeLists.txt, main.cpp, etc.)
- **pyhelios_build/build/** - ALL generated build artifacts (libraries, assets, CMake cache)
- **pyhelios/** - Python source code ONLY (no generated files)

**CRITICAL BUILD ARTIFACT POLICY:**
- ALL generated files (libraries, compiled assets, build outputs) MUST remain in `pyhelios_build/`
- NEVER copy generated files into the source tree (`pyhelios/`)
- Wheel packaging uses custom build commands to copy from `pyhelios_build/` to temporary build directories
- This prevents accidental deletion of source files and maintains clean git status

#### Plugin Selection Options

```bash
# Clean build from fresh state (recommended for troubleshooting)
build_scripts/build_helios --clean --plugins visualizer

# Basic builds
build_scripts/build_helios                           # Default build (non-GPU, non-vis plugins)
build_scripts/build_helios --nogpu                   # Exclude GPU plugins
build_scripts/build_helios --novis                   # Exclude visualization plugins

# Explicit plugin selection
build_scripts/build_helios --plugins weberpenntree,canopygenerator,visualizer

# Interactive selection
build_scripts/build_helios --interactive

# Exclude specific plugins
build_scripts/build_helios --exclude radiation

# Build with custom options
build_scripts/build_helios --cmake-args -DCMAKE_BUILD_TYPE=Debug --verbose

# Debug builds
build_scripts/build_helios --clean --plugins visualizer --buildmode debug
```

#### Plugin Discovery and Status

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

#### Configuration File Support

Create `pyhelios_config.yaml` to specify default plugin selection:

```yaml
plugins:
  explicit_plugins:
    - weberpenntree
    - visualizer
  excluded_plugins:
    - radiation  # Exclude if no GPU available

build:
  build_type: "Release"
  verbose: false
```

### Running Examples
```bash
python docs/examples/context_sample.py
python docs/examples/wpt_sample.py
python docs/examples/visualization_sample.py
```

### Platform Status
```bash
# Check current platform and library status
python -c "from pyhelios.plugins import print_plugin_status; print_plugin_status()"
```

## Style
- Don't add comments that are specific to a given debugging session. For example: "We don't need this anymore, reverting back to old behavior", "Remove Phase 2 code for Phase 3", etc. These types of comments don't make sense outside of a given session.

## Architecture Overview

### Core Components

- **Context** (`pyhelios/Context.py`): Central simulation environment that manages 3D primitives (patches, triangles, voxels). Provides methods for adding geometry, querying properties, and managing object collections.

- **WeberPennTree** (`pyhelios/WeberPennTree.py`): Plant modeling plugin for generating procedural trees. Supports multiple tree types (ALMOND, APPLE, AVOCADO, LEMON, OLIVE, etc.) with configurable parameters for branch recursion, segment resolution, and leaf subdivisions.

- **DataTypes** (`pyhelios/wrappers/DataTypes.py`): Core geometric data structures using ctypes for C++ interop:
  - vec2/vec3/vec4: Vector types for positions, sizes, directions
  - RGBcolor/RGBAcolor: Color representations  
  - SphericalCoord: Spherical coordinate system
  - int2/int3/int4: Integer vector types

### Flexible Plugin System

PyHelios uses a sophisticated plugin-based architecture supporting **21 available plugins** with flexible selection and runtime detection:

#### Plugin Categories

**Core Plugins (Always Available):**
- **weberpenntree**: Procedural tree generation using Weber-Penn algorithms
- **canopygenerator**: Plant canopy generation for various species  
- **solarposition**: Solar position calculations and sun angle modeling

**GPU-Accelerated Plugins (Require CUDA):**
- **radiation**: OptiX-accelerated ray tracing and radiation modeling
- **aeriallidar**: Aerial LiDAR simulation with GPU acceleration
- **collisiondetection**: Collision detection with optional GPU acceleration

**Physics Modeling Plugins:**
- **energybalance**: Plant energy balance calculations and thermal modeling
- **photosynthesis**: Photosynthesis modeling and carbon assimilation
- **leafoptics**: Leaf optical properties modeling (PROSPECT model)
- **stomatalconductance**: Stomatal conductance modeling and gas exchange
- **boundarylayerconductance**: Boundary layer conductance for heat/mass transfer
- **planthydraulics**: Plant hydraulic modeling and water transport

**Analysis and Simulation Plugins:**
- **lidar**: LiDAR simulation and point cloud processing
- **plantarchitecture**: Advanced plant structure and architecture modeling
- **voxelintersection**: Voxel intersection operations and spatial analysis
- **syntheticannotation**: Synthetic data annotation for machine learning
- **parameteroptimization**: Parameter optimization algorithms for model calibration

**Visualization and Tools:**
- **visualizer**: OpenGL-based 3D visualization and rendering
- **projectbuilder**: GUI project builder with ImGui interface

### Cross-Platform Library Loading

PyHelios includes a sophisticated cross-platform library loader (`pyhelios/plugins/loader.py`):

**Platform Support:**
- **Windows**: Uses `ctypes.WinDLL` with `.dll` files
- **macOS**: Uses `ctypes.CDLL` with `.dylib` files  
- **Linux**: Uses `ctypes.CDLL` with `.so` files

**Dynamic Loading Features:**
- Automatic platform detection and appropriate ctypes loader selection
- Fallback to mock mode when native libraries are unavailable
- Comprehensive error handling and informative error messages
- Library validation to ensure core functions are available
- **Runtime plugin detection**: Automatically detects which plugins are compiled into the library
- **Plugin capability discovery**: Provides detailed information about available plugin features
- Dependency checking for optional components (e.g., OptiX for GPU acceleration)
- **Graceful degradation**: Clear error messages when plugins are unavailable with actionable solutions

**Mock Mode:**
- Provides full API compatibility without requiring native libraries
- Enables development and testing on any platform
- Raises informative `RuntimeError` with clear instructions when mock functions are called
- Seamlessly integrates with the testing framework

### High-Level Plugin-Aware Classes

PyHelios provides high-level classes with automatic plugin detection and graceful error handling:

- **Context** (`pyhelios/Context.py`): Enhanced with plugin status reporting and availability checking
- **WeberPennTree** (`pyhelios/WeberPennTree.py`): Automatically detects weberpenntree plugin availability  
- **RadiationModel** (`pyhelios/RadiationModel.py`): High-level interface for radiation modeling with comprehensive error handling and alternative suggestions

### Plugin Registry and Management

- **PluginRegistry** (`pyhelios/plugins/registry.py`): Centralized plugin management with decorators for graceful fallbacks
- **Plugin Detection** (`pyhelios/plugins/loader.py`): Runtime detection of available plugin capabilities
- **Configuration Management** (`pyhelios/config/config_manager.py`): YAML-based configuration with validation

### Wrapper Layer

The `pyhelios/wrappers/` directory contains ctypes wrappers that interface with native plugins:
- `UContextWrapper`: Context operations
- `UWeberPennTreeWrapper`: Tree generation  
- `URadiationModelWrapper`: Radiation modeling (with availability detection)
- `UGlobalWrapper`: Global configuration
- `ULoggerWrapper`: Logging functionality

## Key Usage Patterns

### Basic Geometry Creation
```python
from pyhelios import Context
from pyhelios.types import *  # Convenient import for all vector types

context = Context()
center = vec3(2, 3, 4)
size = vec2(1, 1)
color = RGBcolor(0.25, 0.25, 0.25)
patch_uuid = context.addPatch(center=center, size=size, color=color)
```

### Vector Type Import Options

PyHelios provides two ways to import vector types:

**Option 1: Direct imports (recommended)**
```python
from pyhelios.types import *  # All vector types: vec3, RGBcolor, etc.
position = vec3(1, 2, 3)
color = RGBcolor(0.5, 0.5, 0.5)
```

**Option 2: Explicit DataTypes module**
```python
from pyhelios import DataTypes
position = DataTypes.vec3(1, 2, 3)
color = DataTypes.RGBcolor(0.5, 0.5, 0.5)
```

The star import (`from pyhelios.types import *`) includes all vector types: `vec2`, `vec3`, `vec4`, `int2`, `int3`, `int4`, `RGBcolor`, `RGBAcolor`, `SphericalCoord`, and factory functions like `make_vec3`.

### Tree Generation
```python
from pyhelios import Context, WeberPennTree, WPTType

context = Context()
wpt = WeberPennTree(context)
tree_id = wpt.buildTree(WPTType.LEMON)
```

#### Radiation Modeling with Graceful Handling
```python
from pyhelios import Context, RadiationModel

context = Context()

# RadiationModel automatically checks plugin availability
with RadiationModel(context) as radiation:
    radiation.add_radiation_band("SW")
    radiation.add_collimated_radiation_source()
    radiation.run_band("SW")
    results = radiation.get_total_absorbed_flux()
```

#### Plugin System Discovery
```python
from pyhelios.plugins.registry import get_plugin_registry

registry = get_plugin_registry()

# Get plugin capabilities
capabilities = registry.get_plugin_capabilities()
for plugin, info in capabilities.items():
    print(f"{plugin}: {info['description']}")
    if info['gpu_required']:
        print("  Requires GPU support")

# Check for missing plugins
missing = registry.get_missing_plugins(['radiation', 'visualizer'])
if missing:
    print(f"Missing plugins: {missing}")
```

### Context Managers
Both Context and WeberPennTree support context manager protocol for proper resource cleanup.

## Helios Core Integration

PyHelios interfaces with the main Helios C++ library located in `helios-core/`. The core Helios library provides:

### Core Architecture (`helios-core/core/`)
- **Context.h/cpp**: Central 3D simulation environment with primitive management
- **Global.h/cpp**: Global configuration and utility functions  
- **Vector types**: Comprehensive 3D vector math operations

### Plugin System (`helios-core/plugins/`)
Key plugins that PyHelios may interface with:
- **weberpenntree/**: Procedural tree generation using Weber-Penn algorithms
- **canopygenerator/**: Plant canopy generation for various species  
- **radiation/**: OptiX-accelerated ray tracing for radiation modeling
- **plantarchitecture/**: Advanced plant structure modeling
- **visualizer/**: OpenGL-based 3D visualization
- **lidar/**: LiDAR simulation and point cloud processing
- **energybalance/**: Plant energy balance calculations
- **photosynthesis/**: Photosynthesis modeling

### Accessing Helios Documentation
- Complete documentation: `helios-core/doc/html/index.html` 
- Also available online: https://baileylab.ucdavis.edu/software/helios
- Plugin-specific documentation in each `plugins/*/doc/` directory

### C++/Python Interface Notes
- PyHelios uses ctypes to interface with Helios C++ DLLs
- The `pyhelios/wrappers/` directory contains ctypes wrapper functions
- Native pointers accessible via `get_native_ptr()` for direct Helios API calls
- Helios uses UUID-based object tracking system

## Testing Framework

PyHelios uses pytest for comprehensive testing with support for both unit and integration tests.

### Running Tests

```bash
# Install development dependencies  
pip install -e .[dev]

# Run all tests (works on all platforms - automatically handles mock mode)
pytest

# Run specific test categories
pytest -m unit             # Unit tests (work with mocks)
pytest -m integration      # Integration tests (require native libraries)
pytest -m cross_platform   # Tests that work on all platforms
pytest -m native_only      # Tests requiring native libraries only
pytest -m mock_mode        # Tests specifically for mock mode functionality  
pytest -m slow            # Long-running tests

# Run platform-specific tests
pytest -m windows_only     # Windows-specific tests
pytest -m macos_only       # macOS-specific tests  
pytest -m linux_only       # Linux-specific tests

# Run with coverage (if pytest-cov installed)
pytest --cov=pyhelios --cov-report=html

# Run specific test files
pytest tests/test_datatypes.py
pytest tests/test_cross_platform.py
pytest tests/test_context.py -v
```

### Test Structure

- **Unit Tests**: Test individual components without DLL dependencies (using mocks)
- **Integration Tests**: Test PyHelios + Helios C++ library interaction 
- **Cross-Platform Tests**: Tests that work on all platforms using mock mode when needed
- **Native-Only Tests**: Tests requiring actual native Helios libraries
- **Mock Mode Tests**: Tests specifically for mock mode functionality
- **Performance Tests**: Regression testing for performance-critical operations

### Test Markers

**Core Test Categories:**
- `@pytest.mark.unit`: Pure unit tests (work with mocks)
- `@pytest.mark.integration`: Integration tests with Helios core
- `@pytest.mark.cross_platform`: Tests that work on all platforms
- `@pytest.mark.native_only`: Tests requiring native Helios library
- `@pytest.mark.mock_mode`: Tests specifically for mock mode functionality


**Performance:**
- `@pytest.mark.slow`: Long-running tests

**Platform-Specific:**
- `@pytest.mark.windows_only`: Windows-specific tests
- `@pytest.mark.macos_only`: macOS-specific tests  
- `@pytest.mark.linux_only`: Linux-specific tests

### Key Test Files

- `test_datatypes.py`: DataTypes module (Vec2, Vec3, RGBcolor, etc.) with floating-point precision handling
- `test_context.py`: Context class and primitive management
- `test_weberpenntree.py`: WeberPennTree functionality and tree generation
- `test_cross_platform.py`: Cross-platform functionality, mock mode, and library loading
- `test_integration.py`: End-to-end workflows and complex scenarios
- `conftest.py`: Shared fixtures, platform detection, and test configuration
- `test_utils.py`: Testing utilities, validators, and helper classes

### Test Development Guidelines

**Cross-Platform Testing:**
- **Cross-platform tests** work on all platforms using mock mode when needed
- **Native tests** require platform-specific native libraries 
- Use `@pytest.mark.cross_platform` for tests that work everywhere
- Use `@pytest.mark.native_only` for tests requiring native functionality
- All tests gracefully handle missing libraries with informative skip messages

**Mock Mode Development:**
- Mock mode tests validate API compatibility without requiring native libraries
- Mock mode allows development and testing on any platform without building native libraries
- Tests automatically skip when native libraries are unavailable with informative messages

**Test Configuration:**
- `pytest.ini` configures test markers and excludes `helios-core/` from test collection
- `conftest.py` provides shared fixtures and platform detection utilities
- Floating-point comparisons use `pytest.approx()` for cross-platform reliability

**Test Execution:**
- All tests run successfully on any platform - failing tests are automatically fixed
- Tests provide clear output showing passed/skipped/failed counts  
- Zero warnings and errors in final test execution

**CRITICAL: Mandatory Full Verification Protocol**
For ANY changes to C++ interface files (native/src/*, native/include/*, pyhelios_build/*), ctypes wrappers, or core functionality, you MUST complete this verification sequence:

1. **Full Native Rebuild**: Run `build_scripts/build_helios --clean` to rebuild from scratch
2. **Complete Test Suite**: Run `pytest` (uses subprocess isolation for robust testing) to verify ALL tests pass
3. **Zero Tolerance**: Any failing tests must be fixed before declaring success
4. **No Shortcuts**: Never skip the full test suite even if "individual tests pass"

This protocol is NON-NEGOTIABLE and must be completed regardless of time constraints or apparent simplicity of changes.

**Note**: PyHelios uses pytest-forked for subprocess isolation, preventing ctypes contamination and ensuring reliable test results across all test execution patterns.

**GitHub CI/CD Integration:**
- Comprehensive CI/CD workflows test PyHelios across all platforms
- Quick tests (`test-quick.yml`) for fast development feedback
- Matrix tests (`test-matrix.yml`) for comprehensive cross-platform validation
- Native library tests (`test-native.yml`) attempt to build and test with actual Helios libraries
- All workflows handle mock mode gracefully and provide meaningful test results

## Development Notes

**Cross-Platform Development:**
- **Full platform support**: PyHelios works seamlessly on Windows, macOS, and Linux
- **Mock mode**: Enables development and testing without native libraries on any platform  
- **Native libraries**: Build using `python build_scripts/build_helios.py` for full functionality
- **Platform detection**: Use `from pyhelios.plugins import get_plugin_info` to check current status and library availability

**Testing and Development Workflow:**
- **Comprehensive test suite**: 477 passing tests, 70 properly skipped, zero failures/errors/warnings
- **Subprocess isolation**: pytest-forked prevents ctypes contamination and state interference between tests
- **Cross-platform testing**: Run `pytest` on any platform - tests automatically adapt to available libraries
- **Mock mode development**: Develop and test PyHelios functionality without requiring native library compilation
- **Test categories**: Use `pytest -m cross_platform` for platform-independent tests, `pytest -m native_only` for native library tests
- **Robust test execution**: Tests pass consistently whether run individually or as part of full suite

**MANDATORY: Final Verification Checklist**
Before declaring ANY task complete involving C++/Python interface changes:
□ Built native libraries from scratch using `build_scripts/build_helios --clean`
□ Ran complete `pytest` suite (automatically uses subprocess isolation)
□ All tests pass with zero failures
□ No regressions introduced in any module  
□ Test session shows "plugins: forked-X.X.X" confirming subprocess isolation is active
□ Changes committed to git if task involves file modifications

Failure to complete this checklist constitutes incomplete task execution.

**Architecture and Integration:**
- **UUID-based tracking**: All geometric operations return UUIDs for object tracking
- **Context state management**: The Context manages geometry state with dirty/clean marking
- **Tree generation**: Allows customization of branch recursion levels, segment resolution, and leaf subdivisions
- **Native pointer access**: Available via `get_native_ptr()` methods for advanced operations
- **Helios core integration**: When debugging PyHelios issues, check corresponding C++ implementation in `helios-core/`

**Build and Configuration:**
- **Dynamic library loading**: Automatic platform detection and library loading with fallback to mock mode
- **Build system**: Use build scripts in `build_scripts/` to compile native libraries for your platform
- **Test configuration**: `pytest.ini` and `conftest.py` provide comprehensive test configuration
- **Error handling**: Informative error messages guide users when native libraries are unavailable

**Continuous Integration:**
- **GitHub Actions**: Comprehensive CI/CD workflows in `.github/workflows/`
- **Multi-platform testing**: Automated testing on Ubuntu, Windows, and macOS
- **Python version matrix**: Tests across Python 3.8-3.12
- **Mock mode validation**: All platforms test PyHelios functionality without native dependencies
- **Native library testing**: Best-effort compilation and testing with actual Helios libraries
- **Quick feedback**: Fast workflows for development branches provide rapid feedback

## Error Handling and Fallback Policy

**CRITICAL: PyHelios follows a fail-fast philosophy - never implement silent fallbacks that hide issues from users.** NEVER return fake values (0.0, empty lists, fake IDs), silently catch and ignore exceptions, or continue with misleading fallback functionality when core features fail. Instead, always raise explicit `RuntimeError` or `NotImplementedError` exceptions with clear, actionable error messages that explain what failed, why it failed, and how to fix it. The only acceptable fallbacks are explicit opt-in development modes, documented graceful degradation where users are informed, and safe no-ops like cleaning up `None` resources. **The Golden Rule: If something doesn't work, make it obvious** - users should never wonder why they got unexpected results, but should immediately see clear error messages with specific system requirements and actionable solutions.

## Plugin Integration Guidelines

### When Working on Plugin Integration

PyHelios has successfully integrated 3 major Helios C++ plugins (radiation, visualizer, WeberPennTree) through a sophisticated 8-phase integration process. When working on plugin integration tasks:

#### Use the Right Sub-Agent

- **For complete plugin integration projects**: Use `context-gatherer` to understand existing patterns, then `code-architect` for planning the integration
- **For C++ interface and build issues**: Use `helios-cpp-expert` for deep Helios core knowledge and CMake expertise  
- **For Python wrapper creation**: Use `code-reviewer` to ensure ctypes patterns follow best practices
- **For comprehensive testing**: Use `test-coverage-maximizer` to create robust cross-platform tests
- **For debugging integration issues**: Use `debug-specialist` for systematic troubleshooting

#### Critical Integration Requirements

**ALWAYS follow the 8-phase integration process:**

1. **Plugin Metadata Registration** - Add to `pyhelios/config/plugin_metadata.py`
2. **Build System Integration** - CMake and flexible plugin selection system
3. **C++ Interface Implementation** - Add wrapper functions to `pyhelios_build/pyhelios_interface.cpp`
4. **ctypes Wrapper Creation** - Python-to-C++ interface in `pyhelios/wrappers/`
5. **High-Level Python API** - User-friendly classes with context managers and error handling
6. **Asset Management** - Copy runtime assets (shaders, textures, configs) to expected locations
7. **Testing Integration** - Cross-platform tests with proper pytest markers
8. **Documentation** - API docs and usage examples

#### Essential Integration Patterns

**Asset Management (Critical)**:
Many plugins require runtime assets that must be copied to specific locations where C++ code expects them. ALWAYS check for and implement asset copying in the build system.

**Exception Handling (Mandatory)**:
- All C++ interface functions MUST use try/catch blocks with proper error codes
- Use errcheck callbacks for automatic exception translation
- Never allow C++ exceptions to cross into Python

**Plugin Availability Detection**:
- Check function availability using try/except around ctypes prototypes
- Provide actionable error messages with rebuild instructions
- Implement mock mode for development when plugins unavailable

**Parameter Mapping Precision**:
- Check actual C++ constructor signatures - don't assume parameter order or meaning
- Map parameters semantically, not just positionally
- Test different parameter combinations

**Git Control**:
- Be sure to add any files to git control that will be needed in the repository.

#### Documentation Requirements

For plugin integration tasks, ALWAYS:
- Reference the comprehensive [Plugin Integration Guide](docs/plugin_integration_guide.md) for step-by-step workflow
- Use the [C++ Plugin Integration Guide](docs/cpp_plugin_integration_guide.md) for technical C++ interface details
- Document all new plugin APIs with examples and error handling guidance
- Include troubleshooting sections for common integration issues

#### Testing Requirements

All plugin integrations MUST include:
- **Cross-platform tests** (`@pytest.mark.cross_platform`) that work with mock mode
- **Native-only tests** (`@pytest.mark.native_only`) that require actual plugin functionality
- **Plugin metadata tests** to verify registration
- **Error handling tests** to verify proper exception translation
- **Asset management tests** to verify runtime dependencies are available

#### Build System Requirements

When integrating plugins:
- Use the flexible plugin selection system - no manual CMake modifications needed for basic plugins
- Implement asset copying for runtime dependencies (shaders, textures, fonts, configs)
- Test build system with `--clean` builds and different plugin combinations
- Verify cross-platform symbol export and library loading
- Validate that built libraries can be loaded by ctypes on all platforms

#### Quality Standards

Maintain PyHelios's high standards:
- **Fail-fast error handling** - never silent fallbacks or fake return values
- **Cross-platform compatibility** - test on Windows, macOS, and Linux
- **Comprehensive documentation** - include examples, error scenarios, and troubleshooting
- **Robust testing** - cover both mock mode and native library scenarios
- **Performance considerations** - document any performance characteristics or limitations

#### Critical Lessons from Compound Geometry Integration

**Memory Management**: Always implement safe context cleanup to prevent segmentation faults:
```python
def __exit__(self, exc_type, exc_value, traceback):
    if self.context is not None:
        context_wrapper.destroyContext(self.context)
        self.context = None  # Prevent double deletion - CRITICAL
```

**ctypes Type Equality**: Never rely on `==` for ctypes structures - use field comparison:
```python
# WRONG: color != RGBcolor(1, 1, 1) may fail even when values are equal
# RIGHT: field-based comparison  
if color and not (color.r == 1.0 and color.g == 1.0 and color.b == 1.0):
```

**Parameter Array Mapping**: Check actual array sizes returned by ctypes structures:
```python
# SphericalCoord.to_list() returns 4 elements [radius, elevation, zenith, azimuth]
# But C++ interface expects 3 elements [radius, elevation, azimuth] 
rotation_list = [rotation.radius, rotation.elevation, rotation.azimuth]
```

**Vector Pre-allocation**: Always pre-allocate vectors in C++ for efficiency:
```cpp
std::vector<helios::vec3> nodes_vec;
nodes_vec.reserve(node_count);  // Pre-allocate - CRITICAL for performance
```

**Thread-Local Static Vectors**: Use thread_local for static return vectors:
```cpp
static thread_local std::vector<unsigned int> static_result;  // Not just static
```

## MCP: Knowledge-graph memory policy

- Server alias: `memory` (added via `claude mcp add memory npx:@modelcontextprotocol/server-memory`).
- Purpose: persist structured facts and relationships about this repo, projects, and collaborators using the knowledge-graph memory tools.
- Safety: summarize what you plan to store before writing; do not store secrets or API keys.

### **CRITICAL: How MCP Search Actually Works**

MCP memory uses **simple case-insensitive substring matching** - NOT semantic search or AI understanding. It searches for your query string within entity names, types, and observations using basic `toLowerCase().includes()`.

**Key Implications:**
- Query "test crash" searches for the EXACT phrase "test crash" as a substring
- Query "boundary-layer conductance test failure" WON'T match unless that exact phrase exists
- NO fuzzy matching, NO synonyms, NO semantic understanding
- Case-insensitive: "Test" finds "test", "TEST", "testing"
- Substring matching: "conduct" finds "conductance", "conductor", "semiconductor"

### Search Strategy (MANDATORY)

**✅ GOOD Query Patterns:**
```python
# Single keyword queries work best
mcp__memory__search_nodes(query="radiation")
mcp__memory__search_nodes(query="conductance")
mcp__memory__search_nodes(query="pytest")

# Short phrases that appear verbatim
mcp__memory__search_nodes(query="energy balance")
mcp__memory__search_nodes(query="ctypes wrapper")

# Word stems for broader matching
mcp__memory__search_nodes(query="visual")  # finds "visualizer", "visualization"
mcp__memory__search_nodes(query="test")    # finds "test", "testing", "pytest"
```

**❌ BAD Query Patterns:**
```python
# Complex multi-term queries (searches for EXACT phrase)
mcp__memory__search_nodes(query="boundary-layer conductance test failure exit crash")

# Natural language questions (no semantic understanding)
mcp__memory__search_nodes(query="what causes the radiation plugin to crash?")

# Multiple disconnected concepts (won't match unless exact phrase exists)
mcp__memory__search_nodes(query="CMake plugin shader visualization error")
```

**Query Refinement Strategy:**
1. **Start broad, then narrow**: "test" → "pytest" → "pytest crash" → "pytest contamination"
2. **Use word stems**: "visual" instead of "visualizing", "optim" instead of "optimization"
3. **Multiple simple searches** over one complex search: Do 3 searches with ["radiation", "crash", "GPU"] instead of one "radiation plugin GPU crash"
4. **Search by entity type** if you know it: "technical_issue", "solution", "pattern"

### When to write memory
Trigger a write when any of the following occur:
1. A new project, module, or dataset is introduced.
2. A design decision or convention is finalized.
3. A collaborator's role, preference, or responsibility is clarified.
4. A technical issue is discovered and solved.
5. An integration pattern or architectural insight is learned.

### How to write memory

**Entity Naming Standards (MANDATORY):**
- Use underscores for multi-word names: `RadiationModel_Plugin`, `pytest_forked_fix`
- Be specific but concise (3-5 words max): `boundary_layer_conductance_integration`
- Include dates for time-sensitive items: `shader_fix_2025_10_06`
- Use consistent casing: Choose `snake_case` or `CamelCase` and stick with it
- Make names searchable: Include keywords you'd search for

**Atomic Observation Principle:**
One observation = one fact. Break compound statements into separate observations.

✅ **GOOD Observations:**
```python
observations = [
    "Requires OptiX 7.3 or higher",
    "GPU acceleration optional via --enable-gpu flag",
    "Shader files must be copied to build/shaders/",
    "Fixed in commit 7833202 on 2025-09-25",
    "Located in pyhelios/RadiationModel.py"
]
```

❌ **BAD Observations:**
```python
observations = [
    "Requires OptiX 7.3 or higher and GPU acceleration is optional via --enable-gpu flag, also shader files must be copied to build/shaders/ directory"
]
```

**Recommended Entity Types for PyHelios:**
- **Components**: `plugin`, `module`, `tool`, `library`
- **Knowledge**: `technical_issue`, `solution`, `pattern`, `architecture`
- **Process**: `workflow`, `convention`, `guideline`
- **Project**: `project`, `feature`, `dataset`

**Creating Entities and Relations:**
```python
# 1. Create entities with atomic observations
mcp__memory__create_entities(entities=[
    {
        "name": "pytest_forked_plugin",
        "entityType": "tool",
        "observations": [
            "Prevents ctypes contamination between tests",
            "Runs each test in subprocess for isolation",
            "Required for PyHelios test suite reliability"
        ]
    }
])

# 2. Create meaningful relations
mcp__memory__create_relations(relations=[
    {
        "from": "pytest_forked_plugin",
        "to": "ctypes_contamination_issue",
        "relationType": "solves"
    }
])

# 3. Update existing entities (use add_observations, NOT append_observations)
mcp__memory__add_observations(observations=[
    {
        "entityName": "pytest_forked_plugin",
        "contents": ["Added to PyHelios in version 0.1.4"]
    }
])
```

### When to read memory

**ALWAYS search before creating** to avoid duplicates:
```python
# Before creating new entity, search for existing
results = mcp__memory__search_nodes(query="radiation")
# If found, use add_observations to update
# If not found, create new entity
```

**Search at session start** to gather context:
```python
# Use 2-3 keyword searches
results1 = mcp__memory__search_nodes(query="plugin integration")
results2 = mcp__memory__search_nodes(query="boundary conductance")
results3 = mcp__memory__search_nodes(query="pytest")
```

**Use open_nodes when you know exact names:**
```python
entities = mcp__memory__open_nodes(names=[
    "PyHelios_Plugin_Integration_Process",
    "ctypes_wrapper_error_handling_pattern"
])
```

### Common Pitfalls and Solutions

**Pitfall 1: Overly specific queries return nothing**
- Problem: `search_nodes(query="the test fails with segmentation fault in boundary layer module")`
- Solution: Break into separate searches: `search_nodes(query="segmentation")`, `search_nodes(query="boundary")`

**Pitfall 2: Duplicate entities**
- Problem: Creating `Radiation_Model`, `RadiationModel_Plugin`, `radiation_plugin` separately
- Solution: ALWAYS search before creating: `search_nodes(query="radiation")`

**Pitfall 3: Generic entity names**
- Problem: Entity named "test_issue" is impossible to find
- Solution: Include distinctive identifiers: `pytest_forked_contamination_fix_2025_10`

**Pitfall 4: Compound observations**
- Problem: "Fixed shader compilation and asset copying and CMake configuration"
- Solution: Break into atomic facts: ["Fixed shader compilation issue", "Implemented automatic asset copying", "Updated CMake configuration"]

### PyHelios-Specific Memory Structure

**Core Categories:**
```python
# Plugins (main focus)
"RadiationModel_Plugin", "Visualizer_Plugin", "BoundaryLayerConductance_Plugin"

# Technical challenges
"ctypes_contamination_issue", "pytest_forked_requirement", "cmake_asset_copying_pattern"

# Solutions and patterns
"pytest_forked_solution", "cmake_custom_asset_copy", "errcheck_callback_pattern"

# Architecture
"8_phase_plugin_integration_process", "fail_fast_error_philosophy", "cross_platform_library_loading"
```

**Relation Types to Use:**
- `solves`, `fixes` (solution → problem)
- `depends_on`, `requires` (component → dependency)
- `implements`, `provides` (implementation → interface)
- `part_of`, `contains` (child → parent)
- `follows`, `precedes` (sequence relationships)

### Quick Reference

**Search Commands:**
```python
mcp__memory__search_nodes(query="keyword")           # Discovery search
mcp__memory__open_nodes(names=["Entity_Name"])       # Specific retrieval
mcp__memory__read_graph()                            # Export full graph
```

**When Search Returns Nothing:**
1. Try shorter query (use word stem: "visual" not "visualization")
2. Try related keywords ("GPU" if "OptiX" fails)
3. Search entity types: `search_nodes(query="technical_issue")`
4. Use `read_graph()` to see all entities 