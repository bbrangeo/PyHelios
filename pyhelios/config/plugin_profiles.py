"""
Plugin profile definitions for PyHelios.

This module defines predefined plugin combinations for common use cases,
making it easy for users to select appropriate plugins based on their needs.
"""

from typing import Dict, List
from dataclasses import dataclass

from .plugin_metadata import PLUGIN_METADATA, get_platform_compatible_plugins, get_core_plugins


@dataclass
class PluginProfile:
    """Definition of a plugin profile."""
    name: str
    description: str
    plugins: List[str]
    recommended_for: str
    requires_gpu: bool = False
    platform_specific: Dict[str, List[str]] = None


# Predefined plugin profiles for common use cases
PLUGIN_PROFILES: Dict[str, PluginProfile] = {
    "minimal": PluginProfile(
        name="minimal",
        description="Core functionality only - basic plant modeling without advanced features",
        plugins=["weberpenntree", "canopygenerator", "solarposition"],
        recommended_for="Basic plant modeling, testing, development on any platform",
        requires_gpu=False
    ),
    
    "standard": PluginProfile(
        name="standard",
        description="Standard features for most users - includes visualization and common modeling tools",
        plugins=[
            "weberpenntree", "canopygenerator", "solarposition", "visualizer",
            "energybalance", "photosynthesis", "leafoptics", "voxelintersection"
        ],
        recommended_for="General plant modeling, research, and visualization",
        requires_gpu=False
    ),
    
    "gpu-accelerated": PluginProfile(
        name="gpu-accelerated",
        description="GPU-enabled features for high-performance computing",
        plugins=[
            "weberpenntree", "canopygenerator", "solarposition", "radiation", 
            "visualizer", "energybalance", "photosynthesis", "lidar"
        ],
        recommended_for="High-performance ray tracing, radiation modeling, advanced simulations",
        requires_gpu=True
    ),
    
    "research": PluginProfile(
        name="research",
        description="Comprehensive research suite with full scientific capabilities",
        plugins=[
            "weberpenntree", "canopygenerator", "solarposition", "radiation", 
            "visualizer", "lidar", "energybalance", "photosynthesis", "leafoptics",
            "stomatalconductance", "boundarylayerconductance", "plantarchitecture",
            "planthydraulics", "voxelintersection", "syntheticannotation", 
            "parameteroptimization"
        ],
        recommended_for="Academic research, comprehensive plant modeling, full-featured analysis",
        requires_gpu=True
    ),
    
    "production": PluginProfile(
        name="production",
        description="Production-ready features with reliable performance",
        plugins=[
            "weberpenntree", "canopygenerator", "solarposition", "plantarchitecture",
            "energybalance", "photosynthesis", "leafoptics", "voxelintersection",
            "parameteroptimization"
        ],
        recommended_for="Agricultural applications, reliable performance, production systems",
        requires_gpu=False
    ),
    
    "visualization": PluginProfile(
        name="visualization",
        description="Focus on visualization and rendering capabilities",
        plugins=[
            "weberpenntree", "canopygenerator", "solarposition", "visualizer",
            "voxelintersection", "syntheticannotation"
        ],
        recommended_for="3D visualization, rendering, presentation, educational use",
        requires_gpu=False
    ),
    
    "sensing": PluginProfile(
        name="sensing",
        description="Remote sensing and LiDAR simulation capabilities",
        plugins=[
            "weberpenntree", "canopygenerator", "solarposition", "lidar",
            "syntheticannotation", "voxelintersection", "visualizer"
        ],
        recommended_for="LiDAR simulation, remote sensing research, point cloud analysis",
        requires_gpu=False
    ),
    
    "physics": PluginProfile(
        name="physics",
        description="Comprehensive physics modeling and simulation",
        plugins=[
            "weberpenntree", "canopygenerator", "solarposition", "energybalance",
            "photosynthesis", "leafoptics", "stomatalconductance", 
            "boundarylayerconductance", "planthydraulics", "radiation"
        ],
        recommended_for="Detailed physics modeling, energy balance, thermal analysis",
        requires_gpu=True
    ),
    
    "development": PluginProfile(
        name="development",
        description="Minimal set for PyHelios development and testing",
        plugins=["weberpenntree", "solarposition"],
        recommended_for="PyHelios development, testing, CI/CD, mock mode validation",
        requires_gpu=False
    )
}


def get_profile(profile_name: str) -> PluginProfile:
    """Get a specific plugin profile."""
    if profile_name not in PLUGIN_PROFILES:
        raise ValueError(f"Unknown profile '{profile_name}'. Available profiles: {list(PLUGIN_PROFILES.keys())}")
    return PLUGIN_PROFILES[profile_name]


def get_all_profile_names() -> List[str]:
    """Get list of all available profile names."""
    return list(PLUGIN_PROFILES.keys())


def get_profile_plugins(profile_name: str) -> List[str]:
    """Get the plugin list for a specific profile."""
    return get_profile(profile_name).plugins


def get_gpu_profiles() -> List[str]:
    """Get profiles that require GPU support."""
    return [name for name, profile in PLUGIN_PROFILES.items() if profile.requires_gpu]


def get_non_gpu_profiles() -> List[str]:
    """Get profiles that don't require GPU support."""
    return [name for name, profile in PLUGIN_PROFILES.items() if not profile.requires_gpu]


def filter_profile_by_platform(profile_name: str, platform: str = None) -> List[str]:
    """
    Filter a profile's plugins to only include those compatible with the current platform.
    
    Args:
        profile_name: Name of the profile
        platform: Target platform (auto-detected if None)
    
    Returns:
        List of platform-compatible plugins from the profile
    """
    profile = get_profile(profile_name)
    compatible_plugins = get_platform_compatible_plugins()
    
    # Filter profile plugins to only include platform-compatible ones
    filtered_plugins = [plugin for plugin in profile.plugins if plugin in compatible_plugins]
    
    return filtered_plugins


def get_recommended_profile(has_gpu: bool = False, use_case: str = "general") -> str:
    """
    Get a recommended profile based on system capabilities and use case.
    
    Args:
        has_gpu: Whether GPU acceleration is available
        use_case: Use case category ("general", "research", "visualization", "production")
    
    Returns:
        Recommended profile name
    """
    if use_case == "development":
        return "development"
    elif use_case == "research":
        return "research" if has_gpu else "standard"
    elif use_case == "visualization":
        return "visualization"
    elif use_case == "production":
        return "production"
    elif use_case == "sensing":
        return "sensing"
    elif use_case == "physics":
        return "physics" if has_gpu else "standard"
    else:  # general
        if has_gpu:
            return "gpu-accelerated"
        else:
            return "standard"


def validate_profile_plugins(profile_name: str) -> Dict[str, List[str]]:
    """
    Validate that all plugins in a profile exist and return any issues.
    
    Returns:
        Dictionary with 'valid', 'invalid', and 'missing_deps' plugin lists
    """
    profile = get_profile(profile_name)
    valid_plugins = []
    invalid_plugins = []
    
    for plugin in profile.plugins:
        if plugin in PLUGIN_METADATA:
            valid_plugins.append(plugin)
        else:
            invalid_plugins.append(plugin)
    
    return {
        "valid": valid_plugins,
        "invalid": invalid_plugins,
        "total": len(profile.plugins)
    }