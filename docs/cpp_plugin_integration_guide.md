# C++ Plugin Integration Guide for PyHelios

This guide provides essential information for future agents working on PyHelios to integrate additional C++ plugins and create Python wrappers.

**IMPORTANT**: For a comprehensive step-by-step plugin integration workflow, see the companion [Plugin Integration Guide](plugin_integration_guide.md). This guide focuses on the C++ interface and technical implementation details.

## Overview

PyHelios uses a sophisticated plugin architecture that interfaces with native Helios C++ libraries through ctypes. This system enables cross-platform support while maintaining high performance for computationally intensive operations like ray tracing, plant modeling, and physics simulations.

## 1. Native Code Build Considerations

### CMake Build System Integration

**Location**: `pyhelios_build/CMakeLists.txt` and `pyhelios_build/cmake/PluginSelection.cmake`

**Key Requirements:**
- All C++ plugins must be built as shared libraries (`.dll`, `.dylib`, `.so`)
- Libraries must export C-compatible functions (use `extern "C"` wrapper functions)
- Plugin dependencies must be properly linked and available at runtime
- **NEW**: Plugins must be registered in the flexible plugin selection system

**Plugin Registration:**
Your plugin must be added to the plugin metadata system (`pyhelios/config/plugin_metadata.py`):

```python
"your_plugin": PluginMetadata(
    name="your_plugin",
    description="Description of your plugin functionality",
    system_dependencies=["required_system_libs"],  # e.g., ["cuda", "opengl"]
    plugin_dependencies=["other_plugins"],         # e.g., ["weberpenntree"]
    platforms=["windows", "linux", "macos"],       # Supported platforms
    gpu_required=False,                            # Set True if requires GPU
    optional=True,                                 # Set False for core plugins
    profile_tags=["your_category"],                # e.g., ["physics", "modeling"]
    test_symbols=["test_function_name"]            # Functions to test availability
)
```

**CRITICAL**: The `test_symbols` list should contain function names that will be used to detect plugin availability at runtime. These should be core functions that are guaranteed to exist if the plugin is properly compiled.

**Add to Plugin Profiles:**
Also add your plugin to relevant profiles in `pyhelios/config/plugin_profiles.py`:

```python
# Add to existing profiles or create new ones
"research": PluginProfile(
    plugins=[
        # ... existing plugins ...
        "your_plugin"  # Add here
    ]
),
```

**Critical Build Settings:**
```cmake
# Ensure symbols are exported for ctypes access
set_target_properties(your_plugin PROPERTIES
    CXX_VISIBILITY_PRESET default
    VISIBILITY_INLINES_HIDDEN NO
)

# For Windows DLL export
if(WIN32)
    set_target_properties(your_plugin PROPERTIES
        WINDOWS_EXPORT_ALL_SYMBOLS ON
    )
endif()
```

### Library Linking and Dependencies

**Static vs Dynamic Linking:**
- **External dependencies** (CUDA, OptiX, OpenGL): Should be dynamically linked when possible
- **Internal Helios components**: Can be statically linked into plugin libraries
- **System libraries**: Always dynamic (user's system provides them)

**RPATH Configuration (Linux/macOS):**
```cmake
# Set RPATH so libraries can find each other at runtime
set_target_properties(your_plugin PROPERTIES
    INSTALL_RPATH_USE_LINK_PATH TRUE
    INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib"
)
```

**Dependency Management:**
- Use `find_package()` for external dependencies (CUDA, OptiX, etc.)
- Implement graceful degradation when optional dependencies are missing
- Copy required runtime files (e.g., `.ptx` files for CUDA) to installation directory

**Example from Radiation Plugin:**
```python
def copy_ptx_files(self) -> None:
    """Copy OptiX PTX files to PyHelios installation directory."""
    ptx_source_dir = self.build_dir / 'plugins' / 'radiation'
    if not ptx_source_dir.exists():
        print("No PTX files found - radiation plugin not built with OptiX")
        return
    
    ptx_files = list(ptx_source_dir.glob('*.ptx'))
    pyhelios_root = self.output_dir.parent.parent
    ptx_dest_dir = pyhelios_root / 'plugins' / 'radiation'
    ptx_dest_dir.mkdir(parents=True, exist_ok=True)
    
    for ptx_file in ptx_files:
        dest_file = ptx_dest_dir / ptx_file.name
        shutil.copy2(ptx_file, dest_file)
```

### Cross-Platform Symbol Export

**C++ Header Structure:**
```cpp
// your_plugin.h
#ifdef _WIN32
    #ifdef BUILDING_YOUR_PLUGIN
        #define YOUR_PLUGIN_API __declspec(dllexport)
    #else
        #define YOUR_PLUGIN_API __declspec(dllimport)
    #endif
#else
    #define YOUR_PLUGIN_API __attribute__((visibility("default")))
#endif

extern "C" {
    YOUR_PLUGIN_API void your_function(ContextHandle context, float* params);
    YOUR_PLUGIN_API int your_other_function(uint32_t* uuids, size_t count);
}
```

## 2. C++ Interface Implementation

### Adding Functions to PyHelios C++ Interface

**Location**: `pyhelios_build/pyhelios_interface.cpp`

**CRITICAL STEP**: Before implementing Python wrappers, you must add C-compatible wrapper functions to the PyHelios interface. This step is often overlooked but is essential for new functionality.

**Function Implementation Pattern:**
```cpp
// Add to pyhelios_interface.cpp after existing functions
EXPORT unsigned int addTriangle(helios::Context* context, float* vertex0, float* vertex1, float* vertex2) {
    if (context && vertex0 && vertex1 && vertex2) {
        helios::vec3 v0(vertex0[0], vertex0[1], vertex0[2]);
        helios::vec3 v1(vertex1[0], vertex1[1], vertex1[2]);
        helios::vec3 v2(vertex2[0], vertex2[1], vertex2[2]);
        return context->addTriangle(v0, v1, v2);
    }
    return 0;
}

EXPORT unsigned int addTriangleWithColor(helios::Context* context, float* vertex0, float* vertex1, float* vertex2, float* color) {
    if (context && vertex0 && vertex1 && vertex2 && color) {
        helios::vec3 v0(vertex0[0], vertex0[1], vertex0[2]);
        helios::vec3 v1(vertex1[0], vertex1[1], vertex1[2]);
        helios::vec3 v2(vertex2[0], vertex2[1], vertex2[2]);
        helios::RGBcolor color_rgb(color[0], color[1], color[2]);
        return context->addTriangle(v0, v1, v2, color_rgb);
    }
    return 0;
}
```

**Key Interface Requirements:**
- Use `EXPORT` macro for cross-platform symbol export
- Always validate pointer parameters (check for null)
- Convert between C arrays and C++ objects (vec3, vec2, etc.)
- Return meaningful values (UUIDs, error codes, etc.)
- Handle all function overloads that exist in the C++ API

**Parameter Conversion Patterns:**
```cpp
// vec3 from float array
helios::vec3 position(float_array[0], float_array[1], float_array[2]);

// vec2 from float array  
helios::vec2 size(float_array[0], float_array[1]);

// SphericalCoord from float array
helios::SphericalCoord rotation = helios::make_SphericalCoord(float_array[0], float_array[1]);

// Color from float array
helios::RGBcolor color(float_array[0], float_array[1], float_array[2]);
helios::RGBAcolor color_rgba(float_array[0], float_array[1], float_array[2], float_array[3]);

// String handling
std::string cpp_string(c_string);  // Automatic conversion
```

### Rebuild Requirement

**CRITICAL**: After adding functions to `pyhelios_interface.cpp`, you MUST rebuild PyHelios:

```bash
python3 build_scripts/build_helios.py --verbose
```

The build process will:
1. Recompile the interface with your new functions and exception handling infrastructure
2. Link everything into the shared library  
3. Make the functions available to ctypes
4. Enable the error management system (`_ERROR_MANAGEMENT_AVAILABLE` becomes `True`)

**Verification**: After rebuild, the functions should be available and `_YOUR_FUNCTIONS_AVAILABLE` flags should be `True`. More importantly, `_ERROR_MANAGEMENT_AVAILABLE` should be `True`, enabling proper exception handling.

**Exception Handling Activation**: The comprehensive exception handling system requires the C++ library to be compiled with the new error management infrastructure. Until recompilation:
- Basic PyHelios functionality works normally
- Exception handling tests are automatically skipped
- Some operations may still cause SIGABRT crashes instead of Python exceptions
- After recompilation, all C++ exceptions become proper Python exceptions

## 3. Python Wrapper Implementation

### Wrapper Architecture

**Location**: `pyhelios/wrappers/UYourPluginWrapper.py` or existing wrapper files

**Template Structure:**
```python
import ctypes
from typing import List, Optional
from ..plugins import helios_lib

# Define plugin-specific data structures
class UYourPluginStruct(ctypes.Structure):
    pass

# Declare function prototypes
try:
    helios_lib.your_function.argtypes = [
        ctypes.POINTER(UContext), 
        ctypes.POINTER(ctypes.c_float)
    ]
    helios_lib.your_function.restype = ctypes.c_int
    
    _YOUR_PLUGIN_FUNCTIONS_AVAILABLE = True
except AttributeError:
    _YOUR_PLUGIN_FUNCTIONS_AVAILABLE = False

def your_function_wrapper(context, params: List[float]) -> int:
    """Wrapper for your C++ function"""
    if not _YOUR_PLUGIN_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Your plugin functions not available in current Helios library. "
            "Rebuild with your plugin enabled."
        )
    
    # Convert Python types to ctypes
    param_array = (ctypes.c_float * len(params))(*params)
    
    # Call C++ function
    result = helios_lib.your_function(context, param_array)
    
    # Handle errors
    if result != 0:
        raise RuntimeError(f"Your plugin function failed with error code: {result}")
    
    return result
```

### Critical ctypes Mapping Rules

**Python Type → ctypes Type:**
```python
# Scalars
int → ctypes.c_int, ctypes.c_uint, ctypes.c_size_t
float → ctypes.c_float, ctypes.c_double  
bool → ctypes.c_bool
str → ctypes.c_char_p (encode to UTF-8 first!)

# Arrays
List[int] → (ctypes.c_int * len(list))(*list)
List[float] → (ctypes.c_float * len(list))(*list)

# Pointers (for output parameters)
ctypes.POINTER(ctypes.c_float)  # For returning single float
ctypes.POINTER(ctypes.c_int)    # For returning single int

# Strings (CRITICAL)
my_string.encode('utf-8')  # Always encode Python strings!
```

**Memory Management:**
```python
# For functions that return dynamically allocated arrays
def get_array_wrapper(context, uuid: int) -> List[float]:
    size = ctypes.c_uint()
    ptr = helios_lib.get_array_function(context, uuid, ctypes.byref(size))
    
    # Convert C array to Python list
    result = list(ptr[:size.value])
    
    # Important: Let C++ manage memory - don't call free() from Python
    # unless the C++ API explicitly requires it
    return result
```

### Error Handling Patterns

**CRITICAL: Exception Handling Infrastructure**

PyHelios implements comprehensive exception handling to convert C++ exceptions into proper Python exceptions. When adding new functions, you MUST follow the error handling patterns to maintain PyHelios's fail-fast philosophy.

**UPDATED: New Error Handling Methodology**

PyHelios now uses a simplified, robust error handling system that automatically converts C++ exceptions to Python exceptions through errcheck callbacks.

**C++ Wrapper Exception Handling:**
```cpp
// In your C++ wrapper functions (pyhelios_wrapper.cpp)
#include "pyhelios_wrapper_common.h"  // Includes error management infrastructure

uint32_t your_new_function(helios::Context* context, float* params, uint32_t param_count) {
    try {
        clearError(); // Clear any previous error
        
        // Always validate parameters first
        if (!context) {
            setError(1, "Context pointer is null");
            return 0;
        }
        if (!params) {
            setError(1, "Parameters array is null");
            return 0;
        }
        
        // Your actual C++ API call that might throw exceptions
        return context->your_cpp_method(params, param_count);
        
    } catch (const std::runtime_error& e) {
        // Use error code based on exception type - preserve exact Helios error message
        setError(7, e.what()); // Error code 7 = PYHELIOS_ERROR_RUNTIME
        return 0; // Return default value, error will be checked by Python errcheck
    } catch (const std::exception& e) {
        // Use error code 7 for general runtime errors
        setError(7, std::string("ERROR (YourFunction): ") + e.what());
        return 0;
    } catch (...) {
        // Use error code 99 for unknown errors
        setError(99, "ERROR (YourFunction): Unknown error.");
        return 0;
    }
}

// For functions returning pointers
float* get_array_function(helios::Context* context, uint32_t uuid, uint32_t* size) {
    try {
        clearError(); // Clear any previous error
        
        if (!context || !size) {
            setError(1, "Invalid parameters");
            if (size) *size = 0;
            return nullptr;
        }
        
        std::vector<float> result = context->get_array_method(uuid);
        // Convert vector to C array and return
        static std::vector<float> static_result;
        static_result = result;
        *size = static_result.size();
        return static_result.data();
        
    } catch (const std::runtime_error& e) {
        setError(2, e.what()); // Error code 2 = UUID_NOT_FOUND for typical cases
        if (size) *size = 0;
        return nullptr;
    } catch (const std::exception& e) {
        setError(7, e.what());
        if (size) *size = 0;
        return nullptr;
    } catch (...) {
        setError(99, "ERROR (GetArrayFunction): Unknown error.");
        if (size) *size = 0;
        return nullptr;
    }
}
```

**Python Wrapper Exception Handling:**
```python
# Import exception checking infrastructure
from ..exceptions import check_helios_error

# Error management function prototypes
helios_lib.getLastErrorCode.restype = ctypes.c_int
helios_lib.getLastErrorMessage.restype = ctypes.c_char_p
helios_lib.clearError.argtypes = []

# Automatic error checking callback
def _check_error(result, func, args):
    """
    Errcheck callback that automatically checks for Helios errors after each function call.
    This ensures that C++ exceptions are properly converted to Python exceptions.
    """
    check_helios_error(helios_lib.getLastErrorCode, helios_lib.getLastErrorMessage)
    return result

# Function prototype with automatic error checking
try:
    helios_lib.your_function.argtypes = [ctypes.POINTER(UContext), ctypes.POINTER(ctypes.c_float), ctypes.c_uint]
    helios_lib.your_function.restype = ctypes.c_uint
    helios_lib.your_function.errcheck = _check_error  # CRITICAL: This enables automatic error checking
    _YOUR_FUNCTION_AVAILABLE = True
except AttributeError:
    _YOUR_FUNCTION_AVAILABLE = False

# Simplified function wrapper - errcheck handles all error checking
def your_function_wrapper(context, params: List[float]) -> int:
    if not _YOUR_FUNCTION_AVAILABLE:
        raise NotImplementedError(
            "Your plugin functions not available in current Helios library. "
            "Rebuild with your plugin enabled."
        )
    
    # Convert Python types to ctypes
    param_array = (ctypes.c_float * len(params))(*params)
    
    # Call C++ function - errcheck automatically handles error checking
    result = helios_lib.your_function(context, param_array, len(params))
    
    # No manual error checking needed - errcheck handles everything automatically
    return result
```

**Function Availability Checking:**
```python
try:
    helios_lib.your_new_function.argtypes = [...]
    _NEW_FUNCTION_AVAILABLE = True
except AttributeError:
    _NEW_FUNCTION_AVAILABLE = False

def wrapper_function(...):
    if not _NEW_FUNCTION_AVAILABLE:
        raise NotImplementedError(
            "Function requires newer Helios library version. "
            "Rebuild PyHelios with updated helios-core."
        )
```

**Robust Parameter Validation:**
```python
def your_wrapper(uuids: List[int], data: str, threshold: float):
    # Validate inputs before C++ call
    if not uuids:
        raise ValueError("UUID list cannot be empty")
    if not data:
        raise ValueError("Data label cannot be empty")
    if threshold < 0:
        raise ValueError("Threshold must be non-negative")
    
    # Convert and validate types
    try:
        uuid_array = (ctypes.c_uint * len(uuids))(*uuids)
        data_encoded = data.encode('utf-8')
        threshold_c = ctypes.c_float(threshold)
    except (TypeError, ValueError, UnicodeEncodeError) as e:
        raise ValueError(f"Parameter conversion failed: {e}")
```

**NEVER Do Silent Fallbacks:**
```python
# ❌ WRONG - Silent fallback (violates fail-fast philosophy)
def bad_wrapper(context, uuid: int):
    try:
        return helios_lib.some_function(context, uuid)
    except:
        return 0  # Silent failure - user doesn't know what went wrong

# ✅ CORRECT - Fail-fast with clear error messages  
def good_wrapper(context, uuid: int):
    result = helios_lib.some_function(context, uuid)
    _check_for_helios_error()  # Will raise appropriate exception
    return result
```

**Available Exception Types:**

PyHelios provides a hierarchy of exception types that map to specific C++ error categories:

```python
from pyhelios.exceptions import (
    HeliosError,                    # Base exception for all PyHelios errors
    HeliosRuntimeError,             # C++ std::runtime_error (most common)
    HeliosInvalidArgumentError,     # Invalid parameters, null pointers
    HeliosUUIDNotFoundError,        # Accessing non-existent primitives
    HeliosFileIOError,              # File loading/saving errors
    HeliosMemoryAllocationError,    # Memory allocation failures
    HeliosGPUInitializationError,   # GPU/OptiX initialization failures
    HeliosPluginNotAvailableError,  # Plugin not compiled/available
    HeliosUnknownError             # Unexpected C++ exceptions
)

# Exception mapping is automatic - C++ error codes are converted to appropriate Python exceptions
# You don't need to manually choose exception types when using _check_for_helios_error()
```

**Error Code Constants (C++ side):**
```cpp
// These are automatically defined in pyhelios_wrapper_common.h
typedef enum {
    PYHELIOS_SUCCESS = 0,
    PYHELIOS_ERROR_INVALID_PARAMETER = 1,     // → HeliosInvalidArgumentError
    PYHELIOS_ERROR_UUID_NOT_FOUND = 2,        // → HeliosUUIDNotFoundError  
    PYHELIOS_ERROR_FILE_IO = 3,               // → HeliosFileIOError
    PYHELIOS_ERROR_MEMORY_ALLOCATION = 4,     // → HeliosMemoryAllocationError
    PYHELIOS_ERROR_GPU_INITIALIZATION = 5,    // → HeliosGPUInitializationError
    PYHELIOS_ERROR_PLUGIN_NOT_AVAILABLE = 6,  // → HeliosPluginNotAvailableError
    PYHELIOS_ERROR_RUNTIME = 7,               // → HeliosRuntimeError
    PYHELIOS_ERROR_UNKNOWN = 99               // → HeliosUnknownError
} PyHeliosErrorCode;
```

### High-Level Python API Integration

**Location**: `pyhelios/YourPlugin.py`

**Class Structure Pattern:**
```python
from typing import List, Optional, Union
from . import wrappers.UYourPluginWrapper as plugin_wrapper
from .Context import Context

class YourPlugin:
    """High-level interface for your C++ plugin"""
    
    def __init__(self, context: Context):
        self.context = context
        self._plugin_handle = plugin_wrapper.create_your_plugin(context.context)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, '_plugin_handle'):
            plugin_wrapper.destroy_your_plugin(self._plugin_handle)
    
    def your_method(self, param1: float, param2: List[int]) -> List[float]:
        """
        High-level method with clear documentation.
        
        Args:
            param1: Description of parameter
            param2: List of primitive UUIDs
            
        Returns:
            List of computed values
            
        Raises:
            RuntimeError: If computation fails
            ValueError: If parameters are invalid
        """
        return plugin_wrapper.your_function_wrapper(
            self._plugin_handle, param1, param2
        )
```

## 3. Additional Important Considerations

### Platform-Specific Considerations

**Windows:**
- Ensure all DLL dependencies are in PATH or same directory
- Use `ctypes.WinDLL` for stdcall functions, `ctypes.CDLL` for cdecl
- Be aware of Visual Studio runtime requirements

**Linux/macOS:**  
- Set proper RPATH so shared libraries can find dependencies
- Handle different library naming conventions (`.so` vs `.dylib`)
- Consider different compiler ABI compatibility

### Testing Integration

**Mock Mode Support:**
```python
# In your wrapper file
if not _YOUR_PLUGIN_FUNCTIONS_AVAILABLE:
    def mock_your_function(*args, **kwargs):
        raise RuntimeError(
            "Mock mode: Your plugin not available. "
            "This would perform [specific operation] with native library."
        )
    
    # Replace wrapper functions with mocks
    your_function_wrapper = mock_your_function
```

**Test Structure:**
```python
# tests/test_your_plugin.py
import pytest
from pyhelios import Context, YourPlugin
from pyhelios.exceptions import HeliosError, HeliosInvalidArgumentError

@pytest.mark.native_only
def test_your_plugin_basic():
    """Test requiring actual native library"""
    with Context() as context:
        with YourPlugin(context) as plugin:
            result = plugin.your_method(1.0, [1, 2, 3])
            assert len(result) == 3

@pytest.mark.cross_platform  
def test_your_plugin_mock():
    """Test that works in mock mode"""
    with Context() as context:
        # This should work in mock mode for API validation
        plugin = YourPlugin(context)  # Don't call actual methods

@pytest.mark.cross_platform
def test_your_plugin_exception_handling():
    """Test that proper exceptions are raised for invalid inputs"""
    with Context() as context:
        with YourPlugin(context) as plugin:
            # Test parameter validation
            with pytest.raises(ValueError):
                plugin.your_method(-1.0, [])  # Invalid parameters
            
            # Test that C++ exceptions become Python exceptions
            with pytest.raises(HeliosError):
                plugin.your_method_that_might_fail(invalid_uuid=99999)

@pytest.mark.native_only  
def test_your_plugin_error_messages():
    """Test that error messages are informative"""
    with Context() as context:
        with YourPlugin(context) as plugin:
            try:
                plugin.problematic_method()
                assert False, "Should have raised an exception"
            except HeliosError as e:
                # Verify error message is helpful
                error_msg = str(e).lower()
                assert any(keyword in error_msg for keyword in 
                          ["invalid", "not found", "failed", "error"])
```

### Memory and Performance

**Large Data Handling:**
- Use `numpy` arrays for large numerical datasets
- Consider memory mapping for very large files
- Implement progress callbacks for long-running operations

**Resource Cleanup:**
- Always implement context managers (`__enter__`/`__exit__`)
- Use weak references for callback registration
- Ensure C++ objects are destroyed when Python objects are deleted

### Documentation Requirements

**Function Documentation Pattern:**
```python
def your_function(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of what the function does.
    
    This function interfaces with the native Helios [PluginName] plugin to
    perform [specific operation]. The computation is performed using [method]
    and returns [description of results].
    
    Args:
        param1: Detailed description including units, ranges, constraints
        param2: Detailed description with examples if complex
        
    Returns:
        Detailed description of return value, including units and format
        
    Raises:
        RuntimeError: When [specific condition causes failure]
        ValueError: When [parameter validation fails]
        NotImplementedError: When plugin not available in current build
        
    Example:
        >>> with Context() as context:
        ...     plugin = YourPlugin(context)
        ...     result = plugin.your_function(1.5, [1, 2, 3])
        ...     print(f"Computed values: {result}")
        
    Note:
        This function requires the native Helios library built with 
        [PluginName] plugin support. In development mode, this will
        raise NotImplementedError with instructions for building.
    """
```

### Build System Integration

**Plugin Selection Integration:**
The new flexible plugin system automatically handles plugin compilation based on user selection. Your plugin will be built when:

1. **User explicitly selects it**: `--plugins your_plugin`
2. **Included in a profile**: Add to relevant profiles in `pyhelios/config/plugin_profiles.py`
3. **Required as dependency**: Another plugin lists it in `plugin_dependencies`

**Dynamic Plugin Configuration:**
The CMake system now uses `cmake/PluginSelection.cmake` to dynamically configure plugins:

```cmake
# Your plugin is automatically configured when selected
# No need to manually modify CMakeLists.txt for basic plugins

# For complex plugins requiring special configuration:
if("your_plugin" IN_LIST PLUGINS)
    # Add plugin-specific CMake configuration here
    find_package(YourDependency REQUIRED)
    target_link_libraries(your_plugin YourDependency::YourDependency)
endif()
```

**Runtime Plugin Detection:**
Your plugin functions will be automatically detected at runtime using the `test_symbols` you specified in the metadata. The plugin registry will:

1. Check if your test functions are available in the loaded library
2. Mark the plugin as available/unavailable for Python code
3. Provide graceful error messages when unavailable
4. Enable automatic fallback behaviors

**User Experience Integration:**
With the new system, users can easily discover and use your plugin:

```bash
# Your plugin appears in discovery
python -m pyhelios.plugins discover

# Users can get detailed information
python -m pyhelios.plugins info your_plugin

# Users can build specifically with your plugin
build_scripts/build_helios --plugins your_plugin

# Your plugin can be included in profiles
build_scripts/build_helios --plugins your_plugin1,your_plugin2
```

**Testing Integration:**
Add your plugin to the comprehensive test suite:

```python
# tests/test_your_plugin.py
@pytest.mark.cross_platform
def test_your_plugin_metadata():
    """Test plugin metadata is correctly defined"""
    from pyhelios.config.plugin_metadata import get_plugin_metadata
    metadata = get_plugin_metadata('your_plugin')
    assert metadata is not None
    assert metadata.description
    assert metadata.test_symbols

@pytest.mark.native_only  
def test_your_plugin_functionality():
    """Test actual plugin functionality with native library"""
    with Context() as context:
        with YourPlugin(context) as plugin:
            result = plugin.your_method()
            assert result is not None

@pytest.mark.cross_platform
def test_your_plugin_graceful_handling():
    """Test graceful handling when plugin unavailable"""
    # Test that appropriate errors are raised with helpful messages
    registry = get_plugin_registry()
    if not registry.is_plugin_available('your_plugin'):
        with pytest.raises(PluginNotAvailableError, match="your_plugin"):
            YourPlugin(context)
```

## 4. Critical Lessons Learned from Visualizer Integration

### Asset Management for Runtime Dependencies

**CRITICAL DISCOVERY**: Many C++ plugins require runtime assets (shaders, textures, fonts) that must be copied to specific locations where the C++ code expects to find them.

**Problem Pattern:**
C++ code often uses hardcoded relative paths to find assets:
```cpp
// In C++ plugin code
primaryShader.initialize("plugins/visualizer/shaders/primaryShader.vert", 
                        "plugins/visualizer/shaders/primaryShader.frag", this);
```

**Solution Pattern:**
The build system must copy these assets to the expected location relative to the PyHelios working directory.

**Implementation in build_helios.py:**
```python
def _copy_visualizer_assets(self) -> None:
    """
    Copy all visualizer assets (shaders, textures, fonts) to the expected location.
    
    The C++ Visualizer code expects assets at "plugins/visualizer/" relative to the
    working directory. This method copies all assets from the build directory to
    the PyHelios directory structure where they can be found at runtime.
    """
    # Base paths
    build_visualizer_dir = self.build_dir / 'plugins' / 'visualizer'
    target_base_dir = self.output_dir.parent / 'plugins' / 'visualizer'
    
    if not build_visualizer_dir.exists():
        print(f"ℹ️  Visualizer assets directory not found: {build_visualizer_dir}")
        return
    
    total_files_copied = 0
    
    # Copy shader files
    build_shader_dir = build_visualizer_dir / 'shaders'
    if build_shader_dir.exists():
        target_shader_dir = target_base_dir / 'shaders'
        target_shader_dir.mkdir(parents=True, exist_ok=True)
        
        for shader_file in build_shader_dir.glob('*'):
            if shader_file.is_file():
                dest_file = target_shader_dir / shader_file.name
                shutil.copy2(shader_file, dest_file)
                total_files_copied += 1
                print(f"Copied shader: {shader_file.name}")
    
    # Copy texture files - preserve directory structure
    build_texture_dir = build_visualizer_dir / 'textures'
    if build_texture_dir.exists():
        target_texture_dir = target_base_dir / 'textures'
        target_texture_dir.mkdir(parents=True, exist_ok=True)
        
        for texture_file in build_texture_dir.rglob('*'):
            if texture_file.is_file():
                rel_path = texture_file.relative_to(build_texture_dir)
                dest_file = target_texture_dir / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(texture_file, dest_file)
                total_files_copied += 1
    
    # Copy font files - preserve directory structure
    build_font_dir = build_visualizer_dir / 'fonts'
    if build_font_dir.exists():
        target_font_dir = target_base_dir / 'fonts'
        target_font_dir.mkdir(parents=True, exist_ok=True)
        
        for font_file in build_font_dir.rglob('*'):
            if font_file.is_file():
                rel_path = font_file.relative_to(build_font_dir)
                dest_file = target_font_dir / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(font_file, dest_file)
                total_files_copied += 1
    
    if total_files_copied > 0:
        print(f"🎨 Successfully copied {total_files_copied} visualizer assets to {target_base_dir}")
```

**Integration into copy_to_output method:**
```python
def copy_to_output(self, library_path: Path) -> None:
    # ... existing library copying code ...
    
    # Copy shader files and other assets for visualizer plugin
    self._copy_visualizer_assets()
    
    # ... rest of method ...
```

**Key Insights:**
1. **Check CMakeLists.txt for asset copying**: Look for `file(COPY ...)` and `add_custom_command` that copy assets during build
2. **Assets may include**: Shaders (.vert, .frag), textures (.png, .jpg), fonts (.ttf), configuration files
3. **Preserve directory structure**: Some plugins expect assets in specific subdirectories
4. **Build-time vs Runtime paths**: Assets are copied during build to one location, but must be accessible at runtime from working directory

### Constructor Parameter Mapping Issues

**CRITICAL DISCOVERY**: C++ function signatures must be precisely mapped to Python parameters, especially for constructor overloads.

**Problem Pattern:**
The C++ Visualizer constructor signature was:
```cpp
Visualizer(width, height, antialiasing_samples, window_decorations, headless)
```

But the C interface was incorrectly mapping parameters:
```cpp
// WRONG - semantically incorrect parameter mapping
Visualizer* createVisualizer(unsigned int width, unsigned int height, bool window_decorations) {
    return new Visualizer(width, height, 4, window_decorations, false); // headless hardcoded as false
}
```

This caused `headless=False` (Python default) to be passed as `window_decorations=false`, disabling window decorations.

**Solution Pattern:**
```cpp
// CORRECT - proper semantic mapping
Visualizer* createVisualizer(unsigned int width, unsigned int height, bool headless) {
    // Enable window decorations by default (true), headless parameter controls window visibility
    return new Visualizer(width, height, 4, true, headless); // decorations=true, headless passed correctly
}
```

**Key Insights:**
1. **Always check the actual C++ constructor signature**: Don't assume parameter order or meaning
2. **Semantic mapping matters**: Parameter names should reflect their actual purpose
3. **Default values in C interface**: Choose sensible defaults for optional C++ parameters
4. **Test different parameter combinations**: Verify that parameter mapping produces expected behavior

### Library Linking and Symbol Resolution

**CRITICAL DISCOVERY**: Static libraries require special handling on macOS to ensure all symbols are included in the shared library.

**Problem Pattern:**
When converting static libraries to shared libraries, some plugin symbols were missing due to dead code elimination.

**Solution Pattern:**
```bash
# macOS: Use -Wl,-force_load to include all symbols from static libraries
cmd = [
    'clang++', '-dynamiclib', '-o', str(output_path),
    '-Wl,-force_load', str(cleaned_libs['main']),  # Force load main library
    # ... other libraries ...
]

# Include cleaned plugin libraries with force_load
for lib_path in cleaned_libs['plugins']:
    cmd.extend(['-Wl,-force_load', str(lib_path)])
    print(f"Including cleaned plugin library: {lib_path.name}")
```

**Key Insights:**
1. **Static library symbol inclusion**: Use appropriate linker flags to ensure all symbols are included
2. **Cross-platform differences**: Linux uses different flags than macOS for similar functionality
3. **Plugin dependencies**: Some plugins depend on other plugins and need proper linking order
4. **Symbol visibility**: Ensure C interface functions are exported with proper visibility

### Plugin Function Availability Detection

**CRITICAL DISCOVERY**: Plugin functionality must be properly detected at runtime to provide graceful fallbacks.

**Problem Pattern:**
Code assumed plugin functions were available without checking, leading to AttributeError crashes.

**Solution Pattern:**
```python
# Proper availability detection in wrappers
try:
    helios_lib.createVisualizer.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_bool]
    helios_lib.createVisualizer.restype = ctypes.POINTER(UVisualizer)
    # ... other function prototypes ...
    _VISUALIZER_FUNCTIONS_AVAILABLE = True
except AttributeError:
    _VISUALIZER_FUNCTIONS_AVAILABLE = False

# Graceful error handling
def create_visualizer(width: int, height: int, headless: bool = False):
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    # ... actual function implementation ...
```

**Key Insights:**
1. **Always check function availability**: Use try/except around ctypes function prototype declarations
2. **Provide actionable error messages**: Tell users exactly how to fix the problem
3. **Mock mode fallbacks**: Consider providing mock implementations for development
4. **Plugin interdependencies**: Some plugins may depend on others being available

### Build System Integration Best Practices

**CRITICAL DISCOVERY**: The build system must handle plugin assets, dependencies, and cross-platform differences automatically.

**Key Requirements:**
1. **Asset copying must be automatic**: No manual user intervention should be required
2. **Cross-platform compatibility**: Handle different file extensions and paths on different platforms
3. **Dependency management**: Automatically handle plugin-specific dependencies (OpenGL, CUDA, etc.)
4. **Library validation**: Test that built libraries can actually be loaded by ctypes

**Implementation Pattern:**
```python
def copy_to_output(self, library_path: Path) -> None:
    # 1. Copy main library
    # 2. Validate library is loadable by ctypes (fail-fast)
    self._validate_library_loadable(output_path)
    
    # 3. Copy plugin-specific assets
    self._copy_plugin_assets()  # New requirement
    
    # 4. Handle platform-specific files
    if self.platform_name == 'Windows':
        # Copy PDB files, etc.
```

### Error Manifestation Patterns

**CRITICAL INSIGHTS**: Different types of integration problems manifest as different error patterns:

1. **Missing C Interface Functions**: `AttributeError` when setting ctypes prototypes
   - **Solution**: Add functions to `pyhelios_interface.cpp` and rebuild

2. **Asset Loading Failures**: Runtime crashes with OpenGL/shader errors
   - **Solution**: Implement asset copying in build system

3. **Parameter Mapping Issues**: Unexpected behavior (wrong window decorations, etc.)
   - **Solution**: Carefully check C++ function signatures and map parameters correctly

4. **Library Loading Failures**: `OSError` when ctypes tries to load library
   - **Solution**: Check library dependencies and linking

5. **Symbol Resolution Failures**: Functions appear available but crash when called
   - **Solution**: Use proper linker flags (`-Wl,-force_load` on macOS)

This guide provides the foundation for integrating additional C++ plugins with PyHelios's new flexible plugin system. The new architecture provides automatic plugin discovery, user-friendly configuration, and comprehensive error handling while maintaining consistency across the codebase.

## Complete Integration Workflow

For the complete step-by-step plugin integration process, including:
- Plugin metadata registration
- Build system integration  
- Python wrapper creation
- Testing and documentation
- Asset management

**See the comprehensive [Plugin Integration Guide](plugin_integration_guide.md)**

## Key Lessons from Plugin Integration Experience

**The radiation, visualizer, and WeberPennTree integration experiences revealed that plugin integration requires attention to:**

1. **Runtime asset management** - copying shaders, textures, fonts to expected locations
2. **Precise parameter mapping** - matching C++ constructor signatures exactly  
3. **Library symbol inclusion** - ensuring all plugin symbols are properly linked
4. **Graceful availability detection** - providing clear error messages when plugins are missing
5. **Automated build system integration** - handling all dependencies and assets automatically
6. **Exception handling patterns** - proper C++ to Python exception translation
7. **Cross-platform compatibility** - different linking and symbol export requirements
8. **Plugin interdependencies** - managing complex dependency relationships

## Integration Phases Overview

The complete plugin integration process involves **8 distinct phases**:

1. **Plugin Metadata Registration** - Add to registry and profiles
2. **Build System Integration** - CMake and dependency management
3. **C++ Interface Implementation** - Add wrapper functions (this guide's focus)
4. **ctypes Wrapper Creation** - Python-to-C++ interface layer
5. **High-Level Python API** - User-friendly classes with error handling
6. **Asset Management** - Runtime asset copying and discovery
7. **Testing Integration** - Cross-platform test coverage  
8. **Documentation** - API docs and usage examples

This guide focuses on **Phase 3** (C++ Interface Implementation). For complete coverage of all phases, see the [Plugin Integration Guide](plugin_integration_guide.md).

These lessons and structured approach will significantly accelerate future plugin integration efforts while maintaining PyHelios's high standards for cross-platform compatibility and user experience.