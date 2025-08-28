# Changelog

# [v0.0.6] 2025-08-27

🚨++ New Plug-in Integrated ++ 🚨
- Solar Position plug-in integrated with PyHelios

## Bug Fixes
- Fixed CMake build system to only compile wrapper sources for selected plugins
- Fixed plugin registry detection for selective builds (`--plugins visualizer`)
- Fixed SolarPosition plugin metadata to correctly reflect optional status
- Fixed WeberPennTree constructor to properly handle unavailable plugin scenarios
- Updated error messages for plugin availability to match build configurations

## Testing
- Enhanced cross-platform tests for selective plugin builds
- Fixed test failures when building with limited plugin sets
- Improved error handling validation in plugin availability tests

# [v0.0.5] 2025-08-27

- Helios native C++ had several bugs that was causing errors in the last version. Merged in patched version of 1.3.46.

## Visualizer
- Fixed some issues that could cause the visualizer tests to crash in headless mode.

# [v0.0.4] 2025-08-25

🚨++ New Plug-in Integrated ++ 🚨
- Energy Balance plug-in integrated with PyHelios

- Updated Helios native C++ library to v1.3.46

## Visualizer
- Added `Visualizer.colorContextPrimitivesByData()`
- Fixed a number of issues where visualizer methods were using lists instead of Helios data types (e.g., vec2, vec3, etc.)

# [v0.0.3] 2025-08-23

## Context
- Added comprehensive file loading support with `Context.loadPLY()`, `Context.loadOBJ()`, and `Context.loadXML()` methods
- Enhanced `Context.loadPLY()` with 5 overloads supporting origin, height, rotation, color, and upaxis transformations
- Enhanced `Context.loadOBJ()` with 4 overloads including scale transformations and upaxis specification
- Added complete `Context.loadXML()` implementation for Helios XML geometry files
- Extended native C++ wrapper with 9 new file loading functions and proper error handling
- Added comprehensive parameter validation and security path checking
- Implemented `Context.addTriangleTextured()`
- Implemented `Context.addTrianglesFromArraysTextured()`

## Examples
- Added example geometry files: `suzanne.ply`, `suzanne.obj`, `suzanne.mtl`, and `leaf_cube.xml`
- Updated `external_geometry_sample.py` and `stanford_bunny_radiation.py` for demonstration

## Documentation
- Major README.md restructuring with simplified installation and quick start guide
- Streamlined documentation structure with consolidated user guide sections
- Updated Doxygen configuration for cleaner documentation generation
- Removed redundant documentation files and consolidated content

## Testing
- Enhanced existing tests with file loading functionality validation
- Added cross-platform API tests that work with and without native library

# [v0.0.2] 2025-08-22

## Context
- Added compound geometry support with `addTile()`, `addSphere()`, `addTube()`, `addBox()`, and `addCone()` methods (with color variants)
- Enhanced native C++ wrapper with thread-safe static vector management
- Fixed memory management issues with proper context cleanup to prevent segmentation faults
- Added comprehensive test coverage for compound geometry functionality

## Examples
- Added `primitive_data_array_example.py` demonstrating numpy array integration
- Enhanced `stanford_bunny_radiation.py` with improved visualization workflow
- Removed deprecated `simple_radiation_test.py`

## Documentation
- Updated plugin integration guide with memory management best practices
- Enhanced README.md with simplified installation instructions

# [v0.0.1] 2025-08-21

## Helios native C++
Fix helios-core submodule to point to correct remote commit  
- Reset submodule to match actual remote state (228a3d389)  
- Remove local divergent commits that don't exist on remote 
- This fixes the git history display showing non-existent commits

## Context
- Add primitive data operations for all types (float, int, string, vec2/3/4, int2/3/4)
- Add primitive data query functions (exists, type, size)
- Add auto-detection getter and pseudo-color visualization support
- Extend Context.py with comprehensive primitive data methods
- Add robust error handling and cross-platform ctypes wrappers
- Include comprehensive test coverage for all primitive data operations
- Added Context::getPrimitiveDataArray() to return a numpy array of primitive data

# [v0.0.0] 2025-08-20

🎉 Initial version! 🎉

## Currently implemented plug-ins
- `visualizer`
- `radiation`
- `weber-penn tree`