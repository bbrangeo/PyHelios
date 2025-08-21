"""
Plugin dependency resolution for PyHelios.

This module handles automatic resolution of plugin dependencies, system requirements
validation, and conflict detection to ensure compatible plugin combinations.
"""

import os
import platform
import shutil
import subprocess
import sys
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .plugin_metadata import PLUGIN_METADATA, PluginMetadata, get_platform_compatible_plugins


class ResolutionStatus(Enum):
    """Status of dependency resolution."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ResolutionResult:
    """Result of plugin dependency resolution."""
    status: ResolutionStatus
    final_plugins: List[str]
    added_plugins: List[str]
    removed_plugins: List[str]
    warnings: List[str]
    errors: List[str]
    system_check_results: Dict[str, bool]


class PluginDependencyResolver:
    """Resolves plugin dependencies and validates system requirements."""
    
    def __init__(self):
        self.platform_plugins = get_platform_compatible_plugins()
    
    def resolve_dependencies(self, requested_plugins: List[str], 
                           include_optional: bool = True,
                           strict_mode: bool = False) -> ResolutionResult:
        """
        Resolve plugin dependencies and conflicts.
        
        Args:
            requested_plugins: List of requested plugin names
            include_optional: Whether to include optional dependencies
            strict_mode: If True, fail on any missing dependencies
        
        Returns:
            ResolutionResult with final plugin list and any issues
        """
        result = ResolutionResult(
            status=ResolutionStatus.SUCCESS,
            final_plugins=[],
            added_plugins=[],
            removed_plugins=[],
            warnings=[],
            errors=[],
            system_check_results={}
        )
        
        # Validate requested plugins exist
        valid_plugins, invalid_plugins = self._validate_plugins(requested_plugins)
        if invalid_plugins:
            result.errors.extend([f"Unknown plugin: {p}" for p in invalid_plugins])
            if strict_mode:
                result.status = ResolutionStatus.ERROR
                return result
        
        # Filter by platform compatibility
        platform_compatible = [p for p in valid_plugins if p in self.platform_plugins]
        platform_incompatible = [p for p in valid_plugins if p not in self.platform_plugins]
        
        if platform_incompatible:
            result.removed_plugins.extend(platform_incompatible)
            result.warnings.extend([
                f"Plugin '{p}' not supported on {platform.system()}" 
                for p in platform_incompatible
            ])
        
        # Add plugin dependencies
        final_plugins = set(platform_compatible)
        for plugin in platform_compatible:
            deps = self._get_plugin_dependencies(plugin)
            new_deps = [d for d in deps if d not in final_plugins]
            final_plugins.update(deps)
            result.added_plugins.extend(new_deps)
        
        # Validate system dependencies
        system_results = self._check_system_dependencies(list(final_plugins))
        result.system_check_results = system_results
        
        # Remove plugins with failed system dependencies
        failed_plugins = []
        for plugin in list(final_plugins):
            plugin_metadata = PLUGIN_METADATA[plugin]
            for sys_dep in plugin_metadata.system_dependencies:
                if not system_results.get(sys_dep, False):
                    failed_plugins.append(plugin)
                    result.warnings.append(
                        f"Plugin '{plugin}' disabled: missing system dependency '{sys_dep}'"
                    )
                    break
        
        final_plugins -= set(failed_plugins)
        result.removed_plugins.extend(failed_plugins)
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(list(final_plugins))
        if circular_deps:
            result.warnings.append(f"Circular dependencies detected: {circular_deps}")
        
        result.final_plugins = sorted(list(final_plugins))
        
        # Set overall status
        if result.errors:
            result.status = ResolutionStatus.ERROR
        elif result.warnings:
            result.status = ResolutionStatus.WARNING
            
        return result
    
    def _validate_plugins(self, plugins: List[str]) -> Tuple[List[str], List[str]]:
        """Separate valid and invalid plugin names."""
        valid = [p for p in plugins if p in PLUGIN_METADATA]
        invalid = [p for p in plugins if p not in PLUGIN_METADATA]
        return valid, invalid
    
    def _get_plugin_dependencies(self, plugin_name: str) -> List[str]:
        """Get all dependencies for a plugin recursively."""
        if plugin_name not in PLUGIN_METADATA:
            return []
        
        metadata = PLUGIN_METADATA[plugin_name]
        dependencies = set(metadata.plugin_dependencies)
        
        # Recursively add dependencies of dependencies
        for dep in metadata.plugin_dependencies:
            if dep in PLUGIN_METADATA:
                sub_deps = self._get_plugin_dependencies(dep)
                dependencies.update(sub_deps)
        
        return list(dependencies)
    
    def _detect_circular_dependencies(self, plugins: List[str]) -> List[str]:
        """Detect circular dependencies in plugin list."""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(plugin: str) -> bool:
            if plugin in rec_stack:
                return True
            if plugin in visited:
                return False
            
            visited.add(plugin)
            rec_stack.add(plugin)
            
            if plugin in PLUGIN_METADATA:
                for dep in PLUGIN_METADATA[plugin].plugin_dependencies:
                    if dep in plugins and has_cycle(dep):
                        return True
            
            rec_stack.remove(plugin)
            return False
        
        circular = []
        for plugin in plugins:
            if plugin not in visited and has_cycle(plugin):
                circular.append(plugin)
        
        return circular
    
    def _check_system_dependencies(self, plugins: List[str]) -> Dict[str, bool]:
        """Check availability of system dependencies."""
        all_deps = set()
        for plugin in plugins:
            if plugin in PLUGIN_METADATA:
                all_deps.update(PLUGIN_METADATA[plugin].system_dependencies)
        
        results = {}
        for dep in all_deps:
            results[dep] = self._check_system_dependency(dep)
        
        return results
    
    def _check_system_dependency(self, dependency: str) -> bool:
        """Check if a specific system dependency is available."""
        checkers = {
            "cuda": self._check_cuda,
            "optix": self._check_optix,
            "opengl": self._check_opengl,
            "glfw": self._check_glfw,
            "glew": self._check_glew,
            "freetype": self._check_freetype,
            "imgui": self._check_imgui,
            "x11": self._check_x11
        }
        
        checker = checkers.get(dependency)
        if checker:
            try:
                return checker()
            except Exception:
                return False
        
        # For unknown dependencies, assume available
        return True
    
    def _check_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            result = subprocess.run(["nvcc", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_optix(self) -> bool:
        """Check if OptiX is available."""
        # OptiX is typically bundled with PyHelios, so check for CUDA instead
        return self._check_cuda()
    
    def _check_opengl(self) -> bool:
        """Check if OpenGL is available."""
        system = platform.system()
        if system == "Windows":
            # OpenGL is typically available on Windows
            return True
        elif system == "Darwin":  # macOS
            # OpenGL is available on macOS
            return True
        else:  # Linux
            # Check for OpenGL libraries
            return (shutil.which("glxinfo") is not None or 
                   any(shutil.which(cmd) for cmd in ["nvidia-smi", "amdgpu-pro-info"]))
    
    def _check_glfw(self) -> bool:
        """Check if GLFW is available."""
        # GLFW is typically built as part of the project
        return True
    
    def _check_glew(self) -> bool:
        """Check if GLEW is available."""
        # GLEW is typically built as part of the project
        return True
    
    def _check_freetype(self) -> bool:
        """Check if FreeType is available."""
        # Check for system FreeType first
        if shutil.which("freetype-config") is not None:
            return True
        
        # Check for bundled FreeType in visualizer plugin
        try:
            import os
            # Try multiple possible locations for the FreeType bundle
            possible_paths = [
                # From dependency_resolver.py location
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "helios-core", "plugins", "visualizer", "lib", "freetype-2.7"),
                # From build script working directory
                os.path.join(os.getcwd(), "helios-core", "plugins", "visualizer", "lib", "freetype-2.7"),
                # From PyHelios project root
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "helios-core", "plugins", "visualizer", "lib", "freetype-2.7")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    return True
            
            return False
        except Exception:
            return False
    
    def _check_imgui(self) -> bool:
        """Check if ImGui is available."""
        # ImGui is typically built as part of the project
        return True
    
    def _check_x11(self) -> bool:
        """Check if X11 is available (Linux only)."""
        if platform.system() != "Linux":
            return True  # Not required on other platforms
        
        x11_paths = ["/usr/lib/x86_64-linux-gnu/libX11.so", 
                    "/usr/lib/libX11.so", 
                    "/usr/local/lib/libX11.so"]
        return any(os.path.exists(path) for path in x11_paths)
    
    def suggest_alternatives(self, failed_plugins: List[str]) -> List[str]:
        """Suggest alternative plugins when some fail to load."""
        suggestions = []
        
        # Alternative suggestions based on failed plugins
        alternatives = {
            "radiation": ["energybalance", "leafoptics"],
            "visualizer": ["syntheticannotation"],
            "aeriallidar": ["lidar"],
            "collisiondetection": ["voxelintersection"],
            "projectbuilder": []
        }
        
        for failed in failed_plugins:
            if failed in alternatives:
                suggestions.extend(alternatives[failed])
        
        # Remove duplicates and already requested plugins
        suggestions = list(set(suggestions))
        return suggestions
    
    def get_dependency_graph(self, plugins: List[str]) -> Dict[str, List[str]]:
        """Build dependency graph for visualization/debugging."""
        graph = {}
        for plugin in plugins:
            if plugin in PLUGIN_METADATA:
                graph[plugin] = PLUGIN_METADATA[plugin].plugin_dependencies
            else:
                graph[plugin] = []
        return graph
    
    def validate_configuration(self, plugins: List[str]) -> Dict[str, any]:
        """Comprehensive validation of plugin configuration."""
        valid, invalid = self._validate_plugins(plugins)
        platform_compatible = [p for p in valid if p in self.platform_plugins]
        system_deps = self._check_system_dependencies(platform_compatible)
        
        return {
            "valid_plugins": valid,
            "invalid_plugins": invalid,
            "platform_compatible": platform_compatible,
            "platform_incompatible": [p for p in valid if p not in platform_compatible],
            "system_dependencies": system_deps,
            "gpu_required": any(PLUGIN_METADATA[p].gpu_required for p in platform_compatible),
            "total_requested": len(plugins),
            "total_valid": len(valid)
        }