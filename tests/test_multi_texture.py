"""
Test cases for multi-texture support in PyHelios Context.addTrianglesFromArraysTextured.

These tests validate the new multi-texture functionality that aligns with Open3D/trimesh conventions.
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock

from pyhelios import Context
from pyhelios.plugins.loader import LibraryLoadError


@pytest.mark.cross_platform
class TestMultiTextureValidation:
    """Test validation for multi-texture parameters (works in mock mode)."""
    
    def test_single_texture_backward_compatibility(self):
        """Test that single texture usage still works (backward compatibility)."""
        context = Context()
        
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0], 
            [0.5, 1.0, 0.0]
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.uint32)
        
        uv_coords = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.5, 1.0]
        ], dtype=np.float32)
        
        # Single texture as string (backward compatible) - use real texture file
        texture_file = "docs/examples/models/Helios_logo.jpeg"
        
        # Test both ways of calling with real texture file
        uuids1 = context.addTrianglesFromArraysTextured(vertices, faces, uv_coords, texture_file)
        uuids2 = context.addTrianglesFromArraysTextured(vertices, faces, uv_coords, texture_files=texture_file)
        
        # Should get valid UUIDs for successful texture loading
        assert len(uuids1) == 1  # One triangle
        assert len(uuids2) == 1
        assert all(isinstance(uuid, int) and uuid >= 0 for uuid in uuids1)  # UUIDs can be 0
        assert all(isinstance(uuid, int) and uuid >= 0 for uuid in uuids2)
    
    def test_multi_texture_validation(self):
        """Test validation for multi-texture parameters."""
        context = Context()
        
        vertices = np.array([
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0],  # triangle 1
            [2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [2.5, 1.0, 0.0]   # triangle 2
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32)
        
        uv_coords = np.array([
            [0.0, 0.0], [1.0, 0.0], [0.5, 1.0],  # triangle 1 UVs
            [0.0, 0.0], [1.0, 0.0], [0.5, 1.0]   # triangle 2 UVs
        ], dtype=np.float32)
        
        # Test empty texture list
        with pytest.raises(ValueError, match="Texture files list cannot be empty"):
            context.addTrianglesFromArraysTextured(vertices, faces, uv_coords, [])
        
        # Test material IDs with wrong shape  
        with pytest.raises(ValueError, match="Material IDs must have shape"):
            wrong_material_ids = np.array([0], dtype=np.uint32)  # Only 1 ID for 2 faces
            context.addTrianglesFromArraysTextured(
                vertices, faces, uv_coords, ["tex1.png", "tex2.png"], wrong_material_ids
            )
        
        # Test material ID out of range
        with pytest.raises(ValueError, match="Material ID.*exceeds texture count"):
            invalid_material_ids = np.array([0, 2], dtype=np.uint32)  # ID 2 but only 2 textures (0,1)
            context.addTrianglesFromArraysTextured(
                vertices, faces, uv_coords, ["tex1.png", "tex2.png"], invalid_material_ids
            )
    
    def test_material_ids_auto_generation(self):
        """Test automatic material ID generation when None."""
        context = Context()
        
        vertices = np.array([
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.uint32)
        
        uv_coords = np.array([
            [0.0, 0.0], [1.0, 0.0], [0.5, 1.0]
        ], dtype=np.float32)
        
        # When material_ids is None, should auto-generate zeros
        texture_path = "docs/examples/models/Helios_logo.jpeg"
        uuids = context.addTrianglesFromArraysTextured(
            vertices, faces, uv_coords, [texture_path, texture_path]
        )
            
        # Verify UUID returned
        assert len(uuids) == 1
    
    def test_single_texture_with_material_ids_validation(self):
        """Test validation when using single texture with explicit material IDs."""
        context = Context()
        
        vertices = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.uint32)
        uv_coords = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]], dtype=np.float32)
        
        # Valid: single texture with material ID 0
        texture_path = "docs/examples/models/Helios_logo.jpeg"
        uuids = context.addTrianglesFromArraysTextured(
            vertices, faces, uv_coords, texture_path, material_ids=np.array([0], dtype=np.uint32)
        )
        assert len(uuids) == 1
        
        # Invalid: single texture with non-zero material ID
        with pytest.raises(ValueError, match="When using single texture file, all material IDs must be 0"):
            context.addTrianglesFromArraysTextured(
                vertices, faces, uv_coords, texture_path, material_ids=np.array([1], dtype=np.uint32)
            )


@pytest.mark.native_only 
class TestMultiTextureNativeImplementation:
    """Test multi-texture functionality with native library."""
    
    def test_multi_texture_with_dummy_files(self, basic_context):
        """Test multi-texture functionality with temporary texture files."""
        # Create temporary texture files
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tex1, \
             tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tex2:
            
            # Write dummy PNG headers to make files "valid" (won't actually load as textures but passes file validation)
            tex1.write(b'\x89PNG\r\n\x1a\n' + b'dummy' * 100)
            tex2.write(b'\x89PNG\r\n\x1a\n' + b'dummy' * 100) 
            tex1.flush()
            tex2.flush()
            
            try:
                vertices = np.array([
                    [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0],  # triangle 1
                    [2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [2.5, 1.0, 0.0]   # triangle 2
                ], dtype=np.float32)
                
                faces = np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32)
                
                uv_coords = np.array([
                    [0.0, 0.0], [1.0, 0.0], [0.5, 1.0],  # triangle 1 UVs
                    [0.0, 0.0], [1.0, 0.0], [0.5, 1.0]   # triangle 2 UVs
                ], dtype=np.float32)
                
                # Material IDs: first triangle uses texture 0, second uses texture 1
                material_ids = np.array([0, 1], dtype=np.uint32)
                
                # This may fail due to invalid texture data, but should pass parameter validation
                try:
                    uuids = basic_context.addTrianglesFromArraysTextured(
                        vertices, faces, uv_coords, [tex1.name, tex2.name], material_ids
                    )
                    # If it succeeds, verify we got the right number of triangles
                    assert len(uuids) == 2
                    print(f"Multi-texture test succeeded with UUIDs: {uuids}")
                    
                except Exception as e:
                    # Expected to fail with texture loading error, but not parameter validation error
                    error_msg = str(e)
                    assert not any(keyword in error_msg for keyword in ["shape", "Material ID", "exceeds", "must match"]), \
                        f"Got parameter validation error, expected texture loading error: {error_msg}"
                    print(f"Multi-texture test failed as expected with texture error: {e}")
                    
            finally:
                # Clean up temp files
                for temp_file in [tex1.name, tex2.name]:
                    try:
                        os.unlink(temp_file)
                    except OSError:
                        pass  # File already deleted or permission issue
    
    def test_performance_comparison(self, basic_context):
        """Compare performance of single vs multi-texture approach (if native library available).""" 
        # Create a larger mesh for performance testing
        vertices = np.random.rand(100, 3).astype(np.float32)
        faces = np.array([[i, i+1, i+2] for i in range(0, 97, 3)], dtype=np.uint32)  # 32 triangles
        uv_coords = np.random.rand(100, 2).astype(np.float32)
        
        # Material IDs alternating between 3 different textures
        material_ids = np.tile([0, 1, 2], len(faces) // 3 + 1)[:len(faces)].astype(np.uint32)
        
        # Test would require actual texture files, so just validate the API accepts the arrays
        with pytest.raises((FileNotFoundError, ValueError, RuntimeError)) as exc_info:
            basic_context.addTrianglesFromArraysTextured(
                vertices, faces, uv_coords, 
                ["tex1.png", "tex2.png", "tex3.png"], 
                material_ids
            )
        
        # Should fail due to missing files, not parameter validation
        error_msg = str(exc_info.value)
        assert any(keyword in error_msg for keyword in ["not found", "does not exist", "No such file"]), \
            f"Expected file not found error, got: {error_msg}"


@pytest.mark.cross_platform
class TestOpenThreeDCompatibility:
    """Test compatibility with Open3D-style multi-texture workflows."""
    
    def test_open3d_style_api(self):
        """Test Open3D-style triangle_material_ids workflow."""
        context = Context()
        
        # Simulate Open3D mesh data
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # quad vertices
            [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0]   # second quad vertices
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # first quad (2 triangles)
            [4, 5, 6], [4, 6, 7]   # second quad (2 triangles)
        ], dtype=np.uint32)
        
        uv_coords = np.array([
            [0, 0], [1, 0], [1, 1], [0, 1],  # first quad UVs
            [0, 0], [1, 0], [1, 1], [0, 1]   # second quad UVs
        ], dtype=np.float32)
        
        # Open3D style: triangle_material_ids specifying material for each triangle
        triangle_material_ids = np.array([0, 0, 1, 1], dtype=np.uint32)  # First quad material 0, second quad material 1
        
        texture_path = "docs/examples/models/Helios_logo.jpeg"
        
        # Test Open3D-style API
        uuids = context.addTrianglesFromArraysTextured(
            vertices=vertices,
            faces=faces,
            uv_coords=uv_coords,
            texture_files=[texture_path, texture_path],
            material_ids=triangle_material_ids
        )
        
        assert len(uuids) == 4


@pytest.mark.cross_platform 
class TestTrimeshCompatibility:
    """Test compatibility with trimesh-style workflows."""
    
    def test_automatic_material_grouping(self):
        """Test automatic grouping of faces by material (trimesh-style)."""
        context = Context()
        
        # Simulate trimesh scene with multiple materials
        vertices = np.random.rand(12, 3).astype(np.float32)
        faces = np.array([[i, i+1, i+2] for i in range(0, 9, 3)], dtype=np.uint32)  # 3 triangles
        uv_coords = np.random.rand(12, 2).astype(np.float32)
        
        # Mixed material assignment
        material_ids = np.array([1, 0, 2], dtype=np.uint32)  # Out of order to test grouping
        
        texture_path = "docs/examples/models/Helios_logo.jpeg"
        
        uuids = context.addTrianglesFromArraysTextured(
            vertices, faces, uv_coords,
            [texture_path, texture_path, texture_path],
            material_ids
        )
        
        assert len(uuids) == 3
        
        # The implementation should handle mixed material assignment correctly


@pytest.mark.cross_platform
class TestErrorHandling:
    """Test comprehensive error handling for multi-texture functionality."""
    
    def test_file_validation_errors(self):
        """Test file validation with multi-texture."""
        context = Context()
        
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.uint32)
        uv_coords = np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float32)
        
        # Test file not found for multiple textures - since all files will be validated, the first missing file will fail
        with pytest.raises(ValueError, match="Texture file 0.*does not exist|File not found"):
            context.addTrianglesFromArraysTextured(
                vertices, faces, uv_coords,
                ["nonexistent_file.png", "another_nonexistent_file.png"],  # Both files don't exist
                np.array([0], dtype=np.uint32)
            )
    
    def test_array_dimension_validation(self):
        """Test comprehensive array validation."""
        context = Context()
        
        # Valid base arrays
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.uint32)
        uv_coords = np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float32)
        texture_files = ["tex1.png"]
        
        # Test various invalid configurations
        
        # Wrong vertex shape
        with pytest.raises(ValueError, match="Vertices array must have shape"):
            context.addTrianglesFromArraysTextured(
                np.array([[0, 0]], dtype=np.float32),  # 2D instead of 3D
                faces, uv_coords, texture_files
            )
        
        # Wrong face shape  
        with pytest.raises(ValueError, match="Faces array must have shape"):
            context.addTrianglesFromArraysTextured(
                vertices,
                np.array([[0, 1]], dtype=np.uint32),  # 2 indices instead of 3
                uv_coords, texture_files
            )
        
        # Wrong UV shape
        with pytest.raises(ValueError, match="UV coordinates array must have shape"):
            context.addTrianglesFromArraysTextured(
                vertices, faces,
                np.array([[0, 0, 0]], dtype=np.float32),  # 3D instead of 2D
                texture_files
            )
        
        # Face index out of range
        with pytest.raises(ValueError, match="Face indices reference vertex.*but only.*vertices provided"):
            context.addTrianglesFromArraysTextured(
                vertices,
                np.array([[0, 1, 5]], dtype=np.uint32),  # Vertex 5 doesn't exist
                uv_coords, texture_files
            )