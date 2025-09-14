from setuptools import setup, find_packages, Extension
import os
import platform
import glob

# Read development requirements
def read_dev_requirements():
    try:
        with open('requirements-dev.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

def get_platform_libraries():
    """Get platform-specific library files for packaging."""
    plugins_dir = os.path.join('pyhelios', 'plugins')
    if not os.path.exists(plugins_dir):
        return []
    
    system = platform.system()
    if system == 'Windows':
        patterns = ['*.dll']
    elif system == 'Darwin':  # macOS
        patterns = ['*.dylib'] 
    elif system == 'Linux':
        patterns = ['*.so', '*.so.*']
    else:
        # Include all possible library types
        patterns = ['*.dll', '*.dylib', '*.so', '*.so.*']
    
    library_files = []
    for pattern in patterns:
        found_files = glob.glob(os.path.join(plugins_dir, pattern))
        # Only include files that exist and have non-zero size
        for f in found_files:
            if os.path.exists(f) and os.path.getsize(f) > 0:
                library_files.append(f)
    
    # Return relative paths for package_data
    return [os.path.basename(f) for f in library_files]

def get_asset_files():
    """Get asset files for packaging in wheels."""
    # Look for build directory with assets
    build_dirs = [
        'pyhelios_build/build',
        'pyhelios/assets/build',  # For pip packaging
        'build'  # Alternative location
    ]
    
    asset_patterns = []
    
    for build_dir in build_dirs:
        if os.path.exists(build_dir):
            # Core assets
            core_images = os.path.join(build_dir, 'lib', 'images')
            if os.path.exists(core_images):
                asset_patterns.extend([
                    'assets/build/lib/images/*'
                ])
            
            # Plugin assets - comprehensive patterns matching prepare_wheel.py
            plugins_dir = os.path.join(build_dir, 'plugins')
            if os.path.exists(plugins_dir):
                asset_patterns.extend([
                    # Shader files - all graphics shader types
                    'assets/build/plugins/*/shaders/*.glsl',
                    'assets/build/plugins/*/shaders/*.vert',
                    'assets/build/plugins/*/shaders/*.frag',
                    'assets/build/plugins/*/shaders/*.geom', 
                    'assets/build/plugins/*/shaders/*.comp',
                    # Font files - all font formats
                    'assets/build/plugins/*/fonts/*.ttf',
                    'assets/build/plugins/*/fonts/*.otf',
                    'assets/build/plugins/*/fonts/*.woff',
                    'assets/build/plugins/*/fonts/*.woff2',
                    # Texture files - all image formats
                    'assets/build/plugins/*/textures/*.png',
                    'assets/build/plugins/*/textures/*.jpg',
                    'assets/build/plugins/*/textures/*.jpeg',
                    'assets/build/plugins/*/textures/*.tiff',
                    'assets/build/plugins/*/textures/*.bmp',
                    # WeberPennTree assets - leaves and wood
                    'assets/build/plugins/*/leaves/*.xml',
                    'assets/build/plugins/*/leaves/*.obj',
                    'assets/build/plugins/*/leaves/*.ply',
                    'assets/build/plugins/*/wood/*.xml',
                    'assets/build/plugins/*/wood/*.obj',
                    'assets/build/plugins/*/wood/*.ply',
                    # XML configuration files
                    'assets/build/plugins/*/xml/*.xml',
                    # Spectral data - all data formats
                    'assets/build/plugins/*/spectral_data/*.csv',
                    'assets/build/plugins/*/spectral_data/*.txt',
                    'assets/build/plugins/*/spectral_data/*.dat',
                    # Generic data files
                    'assets/build/plugins/*/data/*.csv',
                    'assets/build/plugins/*/data/*.txt',
                    'assets/build/plugins/*/data/*.dat',
                    'assets/build/plugins/*/data/*.json',
                    # Camera and light models
                    'assets/build/plugins/*/camera_light_models/*.xml',
                    'assets/build/plugins/*/camera_light_models/*.json',
                    # Subdirectories recursively for complex asset structures
                    'assets/build/plugins/*/shaders/**/*',
                    'assets/build/plugins/*/fonts/**/*',
                    'assets/build/plugins/*/textures/**/*',
                    'assets/build/plugins/*/spectral_data/**/*',
                    'assets/build/plugins/*/data/**/*',
                ])
            break  # Use first found build directory
    
    return asset_patterns

def get_long_description():
    """Read long description from README."""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Python bindings for Helios 3D plant simulation library'

def get_extensions():
    """
    Create a stub extension to force setuptools to create platform-specific wheels.
    
    This is necessary because setuptools only creates platform-specific wheels when
    it detects compiled extensions. Since PyHelios includes pre-built native libraries
    via package_data, we need this stub to signal that the wheel is platform-specific.
    """
    # Check if we have actual binary libraries to justify platform wheel
    plugins_dir = os.path.join('pyhelios', 'plugins')
    has_binaries = False
    
    if os.path.exists(plugins_dir):
        system = platform.system()
        if system == 'Windows':
            has_binaries = bool(glob.glob(os.path.join(plugins_dir, '*.dll')))
        elif system == 'Darwin':
            has_binaries = bool(glob.glob(os.path.join(plugins_dir, '*.dylib')))
        else:  # Linux
            has_binaries = bool(glob.glob(os.path.join(plugins_dir, '*.so*')))
    
    if has_binaries:
        # Create a minimal stub extension that signals binary content
        stub_extension = Extension(
            name='pyhelios._stub',
            sources=['pyhelios/_stub.c'],  # Minimal C extension
            optional=True,  # Won't fail build if compilation fails
        )
        return [stub_extension]
    else:
        # No binaries found - allow pure Python wheel
        return []

# Get platform-appropriate library files and assets
library_files = get_platform_libraries()
asset_files = get_asset_files()

if library_files:
    package_data = {'pyhelios': [f'plugins/{f}' for f in library_files] + asset_files}
else:
    # Fallback - include common library extensions and assets
    package_data = {'pyhelios': ['plugins/*.dll', 'plugins/*.so', 'plugins/*.dylib'] + asset_files}

setup(
    name='pyhelios3d',
    use_scm_version=True,
    description='Cross-platform Python bindings for Helios 3D plant simulation',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Pranav Ghate',
    author_email='pghate@ucdavis.edu',
    url='https://github.com/PlantSimulationLab/PyHelios',
    packages=find_packages(exclude=('tests', 'docs', 'build_scripts', '*.build*', 'pyhelios_build*', '*.assets.build*')),
    package_data=package_data,
    include_package_data=True,
    ext_modules=get_extensions(),  # Force platform-specific wheels
    
    # Platform support
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux', 
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    
    # Dependencies
    install_requires=[
        'numpy>=1.19.0',  # Core dependency for PyHelios data structures
        'pyyaml>=5.0.0',  # Configuration file parsing for plugin system
    ],
    setup_requires=[
        'setuptools-scm',
    ],
    extras_require={
        'dev': read_dev_requirements(),
        'test': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.10.0',
            'pytest-xdist>=3.0.0',
            'pytest-timeout>=2.1.0',
        ],
        'build': [
            'cmake',
        ],
    },
    
    # Entry points for build utilities
    entry_points={
        'console_scripts': [
            'pyhelios-build=build_scripts.build_helios:main',
        ],
    },
    
    python_requires='>=3.8',
    
    # Additional metadata
    keywords='helios, plant simulation, 3d modeling, ray tracing, photosynthesis, plant architecture',
    project_urls={
        'Documentation': 'https://baileylab.ucdavis.edu/software/helios',
        'Source': 'https://github.com/PlantSimulationLab/PyHelios',
        'Tracker': 'https://github.com/PlantSimulationLab/PyHelios/issues',
        'Helios Core': 'https://github.com/PlantSimulationLab/Helios',
    },
)