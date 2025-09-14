#!/usr/bin/env python3
"""
Helper script to prepare PyHelios for wheel building.
This script builds native libraries and copies them to the correct location for packaging.
"""

import sys
import platform
import shutil
import glob
import os
from pathlib import Path
import subprocess
import ctypes

def validate_library(lib_path: Path) -> bool:
    """
    Validate that library is a proper PyHelios library that can be loaded.
    
    Args:
        lib_path: Path to the library file
        
    Returns:
        bool: True if library is valid and loadable, False otherwise
    """
    try:
        # Check file exists and has reasonable size
        if not lib_path.exists():
            print(f"Library file does not exist: {lib_path}")
            return False
            
        file_size = lib_path.stat().st_size
        if file_size < 1024:  # Less than 1KB is suspicious
            print(f"Library file suspiciously small ({file_size} bytes): {lib_path}")
            return False
            
        # Try to load the library
        system = platform.system()
        if system == 'Windows':
            lib = ctypes.WinDLL(str(lib_path))
        else:
            lib = ctypes.CDLL(str(lib_path))
            
        # Basic library loading is sufficient validation - don't check internal symbols
        # which may not be consistently exported across all PyHelios plugins
        print(f"[OK] Library validated: {lib_path.name}")
        return True
            
    except OSError as e:
        print(f"[ERROR] Cannot load library {lib_path.name}: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error validating library {lib_path.name}: {e}")
        return False

def copy_assets_for_packaging(project_root: Path) -> None:
    """
    Copy Helios assets to pyhelios/assets/build for packaging in wheels.
    
    Args:
        project_root: Path to project root directory
    """
    print("\nCopying assets for packaging...")
    
    # Source directories
    build_dir = project_root / 'pyhelios_build' / 'build'
    helios_core = project_root / 'helios-core'
    
    # Destination: pyhelios/assets/build
    dest_assets_dir = project_root / 'pyhelios' / 'assets' / 'build'
    dest_assets_dir.mkdir(parents=True, exist_ok=True)
    
    total_copied = 0
    
    # 1. Copy core lib/images directory from build
    core_images_src = build_dir / 'lib' / 'images'
    if core_images_src.exists():
        core_images_dest = dest_assets_dir / 'lib' / 'images'
        if core_images_dest.exists():
            shutil.rmtree(core_images_dest)
        shutil.copytree(core_images_src, core_images_dest)
        image_count = len(list(core_images_dest.glob('*')))
        print(f"[OK] Copied {image_count} core images to lib/images/")
        total_copied += image_count
    else:
        print(f"Warning: No core images found at {core_images_src}")
    
    # 2. Copy plugin assets from helios-core source
    if not helios_core.exists():
        print(f"Warning: helios-core directory not found at {helios_core}")
        return
    
    plugins_src_dir = helios_core / 'plugins'
    plugins_dest_dir = dest_assets_dir / 'plugins'
    
    if plugins_dest_dir.exists():
        shutil.rmtree(plugins_dest_dir)
    plugins_dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Asset types to look for in each plugin
    asset_patterns = {
        'shaders': ['*.glsl', '*.vert', '*.frag', '*.geom', '*.comp'],
        'textures': ['*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp'],
        'fonts': ['*.ttf', '*.otf', '*.woff', '*.woff2'],
        'leaves': ['*.xml', '*.obj', '*.ply'],
        'wood': ['*.xml', '*.obj', '*.ply'],
        'xml': ['*.xml'],
        'spectral_data': ['*.csv', '*.txt', '*.dat'],
        'data': ['*.csv', '*.txt', '*.dat', '*.json'],
        'camera_light_models': ['*.xml', '*.json']
    }
    
    # Plugin-specific asset directory mappings (actual directory names in helios-core)
    # Only include plugins that are integrated with PyHelios
    plugin_asset_dirs = {
        'weberpenntree': ['leaves', 'wood', 'xml'],
        'visualizer': ['textures', 'shaders'],
        'radiation': ['spectral_data'] if Path(plugins_src_dir / 'radiation' / 'spectral_data').exists() else []
        # NOTE: plantarchitecture and canopygenerator are not integrated with PyHelios - assets not needed
    }
    
    # Process each plugin directory
    for plugin_dir in plugins_src_dir.iterdir():
        if not plugin_dir.is_dir():
            continue
            
        plugin_name = plugin_dir.name
        plugin_assets_copied = 0
        
        # Get asset directories for this plugin
        asset_dirs = plugin_asset_dirs.get(plugin_name, [])
        if not asset_dirs:
            continue
            
        plugin_dest = plugins_dest_dir / plugin_name
        plugin_dest.mkdir(exist_ok=True)
        
        # Copy assets from each specified directory
        for asset_dir_path in asset_dirs:
            asset_src = plugin_dir / asset_dir_path
            if not asset_src.exists():
                continue
                
            # Use just the final directory name for destination
            asset_dir_name = asset_dir_path.split('/')[-1]
            asset_dest = plugin_dest / asset_dir_name
            
            if asset_dest.exists():
                shutil.rmtree(asset_dest)
            shutil.copytree(asset_src, asset_dest)
            
            # Count files copied
            files_copied = sum(1 for _ in asset_dest.rglob('*') if _.is_file())
            plugin_assets_copied += files_copied
        
        if plugin_assets_copied > 0:
            print(f"[OK] Copied {plugin_assets_copied} assets from {plugin_name} plugin")
            total_copied += plugin_assets_copied
    
    if total_copied > 0:
        print(f"[OK] Successfully copied {total_copied} total assets for packaging")
    else:
        print("Warning: No assets found to copy")
    
    print(f"[OK] Assets packaged in {dest_assets_dir}")

def build_and_prepare(build_args):
    """Build native libraries and copy them to pyhelios/plugins for packaging."""
    print("Building native libraries for wheel...")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Validate environment
    print(f"Script directory: {script_dir}")
    print(f"Project root: {project_root}")
    print(f"Platform: {platform.system()}")
    print(f"Python executable: {sys.executable}")
    
    # Check required files exist
    build_script = script_dir / 'build_helios.py'
    if not build_script.exists():
        print(f"ERROR: build_helios.py not found at {build_script}")
        sys.exit(1)
    
    helios_core = project_root / 'helios-core'
    if not helios_core.exists():
        print(f"ERROR: helios-core submodule not found at {helios_core}")
        print("Available directories:")
        for item in project_root.iterdir():
            if item.is_dir():
                print(f"  {item.name}/")
        sys.exit(1)
    
    # Build native libraries
    build_cmd = [sys.executable, str(build_script)] + build_args
    print(f"Running build command: {' '.join(build_cmd)}")
    
    try:
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True, cwd=project_root)
        print("Native libraries built successfully")
        if result.stdout:
            print("Build stdout:", result.stdout[-500:])  # Last 500 chars
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Build stdout: {e.stdout}")
        if e.stderr:
            print(f"Build stderr: {e.stderr}")
        sys.exit(1)
    
    # Copy built libraries to packaging location
    build_lib_dir = project_root / 'pyhelios_build' / 'build' / 'lib'
    plugins_dir = project_root / 'pyhelios' / 'plugins'
    
    if not build_lib_dir.exists():
        print(f"Warning: Build directory {build_lib_dir} does not exist")
        return
        
    # Verify source plugins directory exists (should contain Python files)
    if not plugins_dir.exists():
        print(f"ERROR: Source plugins directory not found: {plugins_dir}")
        print("The pyhelios/plugins/ directory with Python source files must exist")
        sys.exit(1)
        
    # Verify it has the required Python files
    py_files = list(plugins_dir.glob('*.py'))
    if not py_files:
        print(f"ERROR: No Python files found in plugins directory: {plugins_dir}")
        print("The plugins directory must contain __init__.py and other Python source files")
        sys.exit(1)
        
    print(f"Found {len(py_files)} Python source files in plugins directory")
    
    # Remove any existing binary libraries from the source directory
    # (These should not be there, but clean up just in case)
    system = platform.system()
    if system == 'Windows':
        old_libs = list(plugins_dir.glob('*.dll'))
    elif system == 'Darwin':
        old_libs = list(plugins_dir.glob('*.dylib'))
    else:
        old_libs = list(plugins_dir.glob('*.so*'))
        
    for old_lib in old_libs:
        print(f"Removing old library: {old_lib.name}")
        old_lib.unlink()
    
    # Platform-specific library extensions
    system = platform.system()
    if system == 'Windows':
        patterns = ['*.dll']
    elif system == 'Darwin':  # macOS
        patterns = ['*.dylib']
    else:  # Linux and others
        patterns = ['*.so', '*.so.*']
    
    # Find and validate libraries
    found_libraries = []
    for pattern in patterns:
        for lib_file in build_lib_dir.glob(pattern):
            found_libraries.append(lib_file)
    
    if not found_libraries:
        print(f"ERROR: No libraries found matching patterns {patterns} in {build_lib_dir}")
        print("Available files in build directory:")
        try:
            for item in build_lib_dir.iterdir():
                print(f"  - {item.name}")
        except:
            print("  (cannot list directory contents)")
        sys.exit(1)
    
    # Copy and validate libraries
    copied_count = 0
    failed_count = 0
    
    for lib_file in found_libraries:
        print(f"\nProcessing library: {lib_file.name}")
        
        # Validate library before copying
        if not validate_library(lib_file):
            print(f"[WARNING] Skipping invalid library: {lib_file.name}")
            failed_count += 1
            continue
            
        # Copy library
        dest_file = plugins_dir / lib_file.name
        try:
            shutil.copy2(lib_file, dest_file)
            print(f"[OK] Copied: {lib_file.name} -> {dest_file}")
            
            # Verify copied file
            if not dest_file.exists() or dest_file.stat().st_size != lib_file.stat().st_size:
                print(f"[ERROR] Copy verification failed for {lib_file.name}")
                failed_count += 1
                continue
                
            copied_count += 1
            
        except (OSError, PermissionError) as e:
            print(f"[ERROR] Failed to copy {lib_file.name}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\n=== Library Copy Summary ===")
    print(f"Found: {len(found_libraries)} libraries")
    print(f"Copied: {copied_count} libraries")
    print(f"Failed: {failed_count} libraries")
    
    if copied_count == 0:
        print("ERROR: No libraries were successfully copied!")
        sys.exit(1)
    elif failed_count > 0:
        print(f"WARNING: {failed_count} libraries could not be copied")
        # Continue anyway - some failures might be acceptable
    
    print(f"[OK] Successfully prepared {copied_count} libraries for packaging")
    
    # Copy assets for packaging
    copy_assets_for_packaging(project_root)

def main():
    """Main entry point."""
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("prepare_wheel.py - Build PyHelios native libraries and prepare for wheel packaging")
        print()
        print("Usage: python prepare_wheel.py <build_args...>")
        print("Example: python prepare_wheel.py --buildmode release --exclude radiation,aeriallidar --verbose")
        print()
        print("This script:")
        print("  1. Calls build_scripts/build_helios.py with the provided arguments")
        print("  2. Copies built libraries to pyhelios/plugins/ for wheel packaging")
        print("  3. Validates libraries can be loaded properly")
        print()
        print("For build argument options, run:")
        print("  python build_scripts/build_helios.py --help")
        sys.exit(0 if '--help' in sys.argv or '-h' in sys.argv else 1)
    
    build_args = sys.argv[1:]
    build_and_prepare(build_args)

if __name__ == '__main__':
    main()