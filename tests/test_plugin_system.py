"""
Comprehensive tests for the PyHelios plugin system.

This module tests plugin metadata, profiles, dependency resolution,
configuration management, and runtime plugin detection.
"""

import pytest
import os
import tempfile
import platform
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the plugin system components to test
from pyhelios.config.plugin_metadata import (
    PLUGIN_METADATA, get_plugin_metadata, get_all_plugin_names,
    get_plugins_by_tags, get_platform_compatible_plugins, get_gpu_dependent_plugins
)
from pyhelios.config.plugin_profiles import (
    PLUGIN_PROFILES, get_profile, get_all_profile_names, get_profile_plugins,
    filter_profile_by_platform, get_recommended_profile
)
from pyhelios.config.dependency_resolver import (
    PluginDependencyResolver, ResolutionStatus
)
from pyhelios.config.config_manager import ConfigManager, ConfigurationError


class TestPluginMetadata:
    """Test plugin metadata functionality."""
    
    def test_plugin_metadata_structure(self):
        """Test that all plugins have required metadata fields."""
        assert len(PLUGIN_METADATA) > 0, "No plugin metadata found"
        
        for plugin_name, metadata in PLUGIN_METADATA.items():
            # Check required fields
            assert hasattr(metadata, 'name')
            assert hasattr(metadata, 'description')
            assert hasattr(metadata, 'system_dependencies')
            assert hasattr(metadata, 'plugin_dependencies')
            assert hasattr(metadata, 'platforms')
            assert hasattr(metadata, 'gpu_required')
            assert hasattr(metadata, 'optional')
            assert hasattr(metadata, 'profile_tags')
            assert hasattr(metadata, 'test_symbols')
            
            # Check field types
            assert isinstance(metadata.description, str)
            assert isinstance(metadata.system_dependencies, list)
            assert isinstance(metadata.plugin_dependencies, list)
            assert isinstance(metadata.platforms, list)
            assert isinstance(metadata.gpu_required, bool)
            assert isinstance(metadata.optional, bool)
            assert isinstance(metadata.profile_tags, list)
            assert isinstance(metadata.test_symbols, list)
            
            # Check that platforms are valid
            valid_platforms = {'windows', 'linux', 'macos'}
            for platform_name in metadata.platforms:
                assert platform_name in valid_platforms, f"Invalid platform: {platform_name}"
    
    def test_get_plugin_metadata(self):
        """Test getting metadata for specific plugins."""
        # Test existing plugin
        radiation_metadata = get_plugin_metadata('radiation')
        assert radiation_metadata is not None
        assert radiation_metadata.name == 'radiation'
        assert radiation_metadata.gpu_required == True
        
        # Test non-existent plugin
        assert get_plugin_metadata('nonexistent') is None
    
    def test_get_all_plugin_names(self):
        """Test getting all plugin names."""
        plugin_names = get_all_plugin_names()
        assert isinstance(plugin_names, list)
        assert len(plugin_names) > 0
        assert 'radiation' in plugin_names
        assert 'weberpenntree' in plugin_names
    
    def test_get_plugins_by_tags(self):
        """Test filtering plugins by tags."""
        gpu_plugins = get_plugins_by_tags(['gpu'])
        assert isinstance(gpu_plugins, list)
        assert 'radiation' in gpu_plugins
        
        core_plugins = get_plugins_by_tags(['core'])
        assert isinstance(core_plugins, list)
        assert len(core_plugins) > 0
    
    def test_get_platform_compatible_plugins(self):
        """Test getting platform-compatible plugins."""
        compatible = get_platform_compatible_plugins()
        assert isinstance(compatible, list)
        assert len(compatible) > 0
        
        # Should include plugins compatible with current platform
        current_system = platform.system().lower()
        platform_map = {'windows': 'windows', 'linux': 'linux', 'darwin': 'macos'}
        current_platform = platform_map.get(current_system, current_system)
        
        for plugin in compatible:
            metadata = PLUGIN_METADATA[plugin]
            assert current_platform in metadata.platforms
    
    def test_get_gpu_dependent_plugins(self):
        """Test getting GPU-dependent plugins."""
        gpu_plugins = get_gpu_dependent_plugins()
        assert isinstance(gpu_plugins, list)
        assert 'radiation' in gpu_plugins
        
        # All returned plugins should have gpu_required=True
        for plugin in gpu_plugins:
            metadata = PLUGIN_METADATA[plugin]
            assert metadata.gpu_required == True


class TestPluginProfiles:
    """Test plugin profile functionality."""
    
    def test_plugin_profiles_structure(self):
        """Test that all profiles have required structure."""
        assert len(PLUGIN_PROFILES) > 0, "No plugin profiles found"
        
        for profile_name, profile in PLUGIN_PROFILES.items():
            # Check required fields
            assert hasattr(profile, 'name')
            assert hasattr(profile, 'description')
            assert hasattr(profile, 'plugins')
            assert hasattr(profile, 'recommended_for')
            assert hasattr(profile, 'requires_gpu')
            
            # Check field types
            assert isinstance(profile.description, str)
            assert isinstance(profile.plugins, list)
            assert isinstance(profile.recommended_for, str)
            assert isinstance(profile.requires_gpu, bool)
            
            # Check that all plugins in profile exist in metadata
            for plugin in profile.plugins:
                assert plugin in PLUGIN_METADATA, f"Profile {profile_name} references unknown plugin: {plugin}"
    
    def test_get_profile(self):
        """Test getting specific profiles."""
        # Test existing profile
        standard_profile = get_profile('standard')
        assert standard_profile.name == 'standard'
        assert isinstance(standard_profile.plugins, list)
        
        # Test non-existent profile
        with pytest.raises(ValueError, match="Unknown profile"):
            get_profile('nonexistent')
    
    def test_get_all_profile_names(self):
        """Test getting all profile names."""
        profile_names = get_all_profile_names()
        assert isinstance(profile_names, list)
        assert len(profile_names) > 0
        assert 'minimal' in profile_names
        assert 'standard' in profile_names
        assert 'gpu-accelerated' in profile_names
    
    def test_get_profile_plugins(self):
        """Test getting plugin list for profiles."""
        minimal_plugins = get_profile_plugins('minimal')
        assert isinstance(minimal_plugins, list)
        assert len(minimal_plugins) > 0
        
        gpu_plugins = get_profile_plugins('gpu-accelerated')
        assert isinstance(gpu_plugins, list)
        assert 'radiation' in gpu_plugins
    
    def test_filter_profile_by_platform(self):
        """Test platform filtering of profiles."""
        # Test with current platform
        filtered = filter_profile_by_platform('standard')
        assert isinstance(filtered, list)
        
        # All plugins should be platform-compatible
        compatible = get_platform_compatible_plugins()
        for plugin in filtered:
            assert plugin in compatible
    
    def test_get_recommended_profile(self):
        """Test profile recommendations."""
        # Test with GPU
        gpu_rec = get_recommended_profile(has_gpu=True, use_case="general")
        assert gpu_rec in get_all_profile_names()
        
        # Test without GPU
        no_gpu_rec = get_recommended_profile(has_gpu=False, use_case="general")
        assert no_gpu_rec in get_all_profile_names()
        
        # Test specific use cases
        research_rec = get_recommended_profile(has_gpu=True, use_case="research")
        assert research_rec == "research"
        
        dev_rec = get_recommended_profile(has_gpu=False, use_case="development")
        assert dev_rec == "development"


class TestDependencyResolver:
    """Test plugin dependency resolution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.resolver = PluginDependencyResolver()
    
    def test_resolve_dependencies_simple(self):
        """Test simple dependency resolution."""
        resolver = PluginDependencyResolver()
        
        # Test with basic plugins
        result = resolver.resolve_dependencies(['weberpenntree', 'canopygenerator'])
        
        assert result.status in [ResolutionStatus.SUCCESS, ResolutionStatus.WARNING]
        assert isinstance(result.final_plugins, list)
        assert 'weberpenntree' in result.final_plugins
        assert 'canopygenerator' in result.final_plugins
    
    def test_resolve_dependencies_with_gpu(self):
        """Test dependency resolution with GPU plugins."""
        resolver = PluginDependencyResolver()
        
        # Test with radiation plugin (GPU-dependent)
        result = resolver.resolve_dependencies(['radiation'])
        
        assert isinstance(result.final_plugins, list)
        
        # If CUDA is available, radiation should be included
        # If not, it should be removed with warnings
        if result.system_check_results.get('cuda', False):
            assert 'radiation' in result.final_plugins
        else:
            assert 'radiation' not in result.final_plugins
            assert len(result.warnings) > 0
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        resolver = PluginDependencyResolver()
        
        # Test valid configuration
        validation = resolver.validate_configuration(['weberpenntree', 'canopygenerator'])
        
        assert isinstance(validation, dict)
        assert 'valid_plugins' in validation
        assert 'invalid_plugins' in validation
        assert 'platform_compatible' in validation
        assert 'system_dependencies' in validation
        
        # Test invalid plugin
        validation = resolver.validate_configuration(['nonexistent'])
        assert 'nonexistent' in validation['invalid_plugins']
    
    def test_dependency_graph(self):
        """Test dependency graph generation."""
        resolver = PluginDependencyResolver()
        
        plugins = ['weberpenntree', 'radiation']
        graph = resolver.get_dependency_graph(plugins)
        
        assert isinstance(graph, dict)
        assert 'weberpenntree' in graph
        assert isinstance(graph['weberpenntree'], list)


class TestConfigManager:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = ConfigManager()
        
        # Check default values
        assert config.plugin_config.selection_mode == "profile"
        assert config.plugin_config.profile == "standard"
        assert config.build_config.build_type == "Release"
        assert config.logging_config.level == "INFO"
    
    def test_yaml_config_loading(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
plugins:
  selection_mode: "explicit"
  explicit_plugins:
    - weberpenntree
    - canopygenerator
  excluded_plugins:
    - radiation

build:
  build_type: "Debug"
  verbose: true

logging:
  level: "DEBUG"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_filename = f.name
            
        try:
            config = ConfigManager(temp_filename)
            
            # Check parsed values
            assert config.plugin_config.selection_mode == "explicit"
            assert config.plugin_config.explicit_plugins == ["weberpenntree", "canopygenerator"]
            assert config.plugin_config.excluded_plugins == ["radiation"]
            assert config.build_config.build_type == "Debug"
            assert config.build_config.verbose == True
            assert config.logging_config.level == "DEBUG"
            
        finally:
            try:
                os.unlink(temp_filename)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
    
    def test_plugin_resolution(self):
        """Test plugin resolution from configuration."""
        config = ConfigManager()
        
        # Test profile-based resolution
        config.plugin_config.selection_mode = "profile"
        config.plugin_config.profile = "minimal"
        
        plugins = config.resolve_plugin_selection()
        assert isinstance(plugins, list)
        assert len(plugins) > 0
        
        # Test explicit resolution (clear platform-specific config to avoid interference)
        config.plugin_config.selection_mode = "explicit"
        config.plugin_config.explicit_plugins = ["weberpenntree", "canopygenerator"]
        config.plugin_config.platform_specific = {}  # Clear platform-specific config
        
        plugins = config.resolve_plugin_selection()
        assert plugins == ["weberpenntree", "canopygenerator"]
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = ConfigManager()
        
        # Test valid configuration
        validation = config.validate_configuration()
        assert isinstance(validation, dict)
        assert 'valid' in validation
        assert 'issues' in validation
        assert 'warnings' in validation
        
        # Test invalid configuration
        config.plugin_config.selection_mode = "invalid_mode"
        validation = config.validate_configuration()
        assert validation['valid'] == False
        assert len(validation['issues']) > 0
    
    def test_config_save_load(self):
        """Test saving and loading configuration."""
        original_config = ConfigManager()
        original_config.plugin_config.profile = "research"
        original_config.build_config.build_type = "Debug"
        original_config.logging_config.level = "WARNING"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_filename = f.name
            
        try:
            # Save configuration
            original_config.save_config(temp_filename)
            
            # Load configuration
            loaded_config = ConfigManager(temp_filename)
            
            # Verify values match
            assert loaded_config.plugin_config.profile == "research"
            assert loaded_config.build_config.build_type == "Debug"
            assert loaded_config.logging_config.level == "WARNING"
            
        finally:
            try:
                os.unlink(temp_filename)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows


class TestPluginRegistry:
    """Test plugin registry functionality."""
    
    @pytest.fixture
    def mock_plugin_functions(self):
        """Mock plugin detection functions for testing."""
        with patch('pyhelios.plugins.registry.detect_available_plugins') as mock_detect, \
             patch('pyhelios.plugins.registry.get_plugin_capabilities') as mock_capabilities:
            
            mock_detect.return_value = ['weberpenntree', 'canopygenerator']
            mock_capabilities.return_value = {
                'weberpenntree': {
                    'name': 'weberpenntree',
                    'description': 'Tree generation',
                    'available': True,
                    'gpu_required': False,
                    'dependencies': []
                },
                'canopygenerator': {
                    'name': 'canopygenerator',
                    'description': 'Canopy generation',
                    'available': True, 
                    'gpu_required': False,
                    'dependencies': []
                }
            }
            yield mock_detect, mock_capabilities
    
    def test_registry_initialization(self, mock_plugin_functions):
        """Test plugin registry initialization."""
        from pyhelios.plugins.registry import PluginRegistry
        
        registry = PluginRegistry()
        registry.initialize()
        
        assert registry._initialized == True
        available = registry.get_available_plugins()
        assert isinstance(available, list)
        assert 'weberpenntree' in available
    
    def test_plugin_availability_check(self, mock_plugin_functions):
        """Test plugin availability checking."""
        from pyhelios.plugins.registry import PluginRegistry
        
        registry = PluginRegistry()
        registry.initialize()
        
        # Test available plugin
        assert registry.is_plugin_available('weberpenntree') == True
        
        # Test unavailable plugin  
        assert registry.is_plugin_available('nonexistent') == False
    
    def test_plugin_requirements(self, mock_plugin_functions):
        """Test plugin requirement checking."""
        from pyhelios.plugins.registry import PluginRegistry, PluginNotAvailableError
        
        registry = PluginRegistry()
        registry.initialize()
        
        # Test requiring available plugin - should not raise
        registry.require_plugin('weberpenntree')
        
        # Test requiring unavailable plugin - should raise
        with pytest.raises(PluginNotAvailableError):
            registry.require_plugin('nonexistent')


class TestIntegration:
    """Integration tests for the complete plugin system."""
    
    def test_end_to_end_workflow(self):
        """Test complete plugin selection and validation workflow."""
        # Create configuration
        config = ConfigManager()
        config.plugin_config.selection_mode = "profile"
        config.plugin_config.profile = "minimal"
        
        # Resolve plugins
        plugins = config.resolve_plugin_selection()
        assert isinstance(plugins, list)
        assert len(plugins) > 0
        
        # Validate with dependency resolver
        resolver = PluginDependencyResolver()
        result = resolver.resolve_dependencies(plugins)
        
        assert result.status in [ResolutionStatus.SUCCESS, ResolutionStatus.WARNING]
        assert isinstance(result.final_plugins, list)
    
    def test_cross_platform_compatibility(self):
        """Test that the system works across different platforms."""
        # Test all profiles on current platform
        for profile_name in get_all_profile_names():
            try:
                plugins = filter_profile_by_platform(profile_name)
                assert isinstance(plugins, list)
                
                # All plugins should be platform-compatible
                compatible = get_platform_compatible_plugins()
                for plugin in plugins:
                    assert plugin in compatible, f"Plugin {plugin} not compatible with current platform"
                    
            except Exception as e:
                pytest.fail(f"Profile {profile_name} failed on current platform: {e}")
    
    def test_mock_mode_compatibility(self):
        """Test that mock mode works correctly."""
        # Test that plugin metadata works without native libraries
        plugin_names = get_all_plugin_names()
        assert len(plugin_names) > 0
        
        # Test dependency resolution in mock environment
        resolver = PluginDependencyResolver()
        result = resolver.resolve_dependencies(['weberpenntree'])
        
        # Should work even without native libraries
        assert isinstance(result.final_plugins, list)


@pytest.mark.slow
class TestPerformance:
    """Performance tests for plugin system."""
    
    def test_metadata_loading_performance(self):
        """Test that metadata loading is fast."""
        import time
        
        start_time = time.time()
        for _ in range(100):
            get_all_plugin_names()
            get_platform_compatible_plugins()
        end_time = time.time()
        
        # Should complete 100 iterations in under 1 second
        assert (end_time - start_time) < 1.0
    
    def test_dependency_resolution_performance(self):
        """Test that dependency resolution is reasonably fast."""
        import time
        
        resolver = PluginDependencyResolver()
        all_plugins = get_all_plugin_names()
        
        start_time = time.time()
        result = resolver.resolve_dependencies(all_plugins)
        end_time = time.time()
        
        # Should resolve all plugins in under 5 seconds
        assert (end_time - start_time) < 5.0
        assert isinstance(result.final_plugins, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])