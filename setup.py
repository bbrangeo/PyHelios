from setuptools import setup, find_packages
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
        library_files.extend(glob.glob(os.path.join(plugins_dir, pattern)))
    
    # Return relative paths for package_data
    return [os.path.basename(f) for f in library_files]

def get_long_description():
    """Read long description from README."""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Python bindings for Helios 3D plant simulation library'

# Get platform-appropriate library files
library_files = get_platform_libraries()
if library_files:
    package_data = {'pyhelios': [f'plugins/{f}' for f in library_files]}
else:
    # Fallback - include common library extensions
    package_data = {'pyhelios': ['plugins/*.dll', 'plugins/*.so', 'plugins/*.dylib']}

setup(
    name='pyhelios',
    use_scm_version=True,
    description='Cross-platform Python bindings for Helios 3D plant simulation',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Pranav Ghate',
    author_email='pghate@ucdavis.edu',
    url='https://github.com/PlantSimulationLab/PyHelios',
    packages=find_packages(exclude=('tests', 'docs', 'build_scripts')),
    package_data=package_data,
    include_package_data=True,
    
    # Platform support
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux', 
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
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
    
    python_requires='>=3.7',
    
    # Additional metadata
    keywords='helios, plant simulation, 3d modeling, ray tracing, photosynthesis, plant architecture',
    project_urls={
        'Documentation': 'https://baileylab.ucdavis.edu/software/helios',
        'Source': 'https://github.com/PlantSimulationLab/PyHelios',
        'Tracker': 'https://github.com/PlantSimulationLab/PyHelios/issues',
        'Helios Core': 'https://github.com/PlantSimulationLab/Helios',
    },
)