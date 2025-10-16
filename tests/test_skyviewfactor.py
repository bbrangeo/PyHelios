"""
Unit tests for SkyViewFactor plugin.

This module contains comprehensive tests for the SkyViewFactorModel and SkyViewFactorCamera classes.
"""

import unittest
import numpy as np
import tempfile
import os
from pathlib import Path

from pyhelios import Context, SkyViewFactorModel, SkyViewFactorCamera, SkyViewFactorModelError


class TestSkyViewFactorModel(unittest.TestCase):
    """Test cases for SkyViewFactorModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = Context()
        self.model = SkyViewFactorModel(self.context)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'context'):
            del self.context
    
    def test_model_creation(self):
        """Test that SkyViewFactorModel can be created."""
        self.assertIsNotNone(self.model)
        self.assertTrue(self.model._is_initialized)
    
    def test_ray_count_configuration(self):
        """Test ray count configuration."""
        # Test setting ray count
        self.model.set_ray_count(500)
        self.assertEqual(self.model.get_ray_count(), 500)
        
        # Test invalid ray count
        with self.assertRaises(ValueError):
            self.model.set_ray_count(0)
        
        with self.assertRaises(ValueError):
            self.model.set_ray_count(-1)
    
    def test_max_ray_length_configuration(self):
        """Test max ray length configuration."""
        # Test setting max ray length
        self.model.set_max_ray_length(500.0)
        self.assertEqual(self.model.get_max_ray_length(), 500.0)
        
        # Test invalid max ray length
        with self.assertRaises(ValueError):
            self.model.set_max_ray_length(0.0)
        
        with self.assertRaises(ValueError):
            self.model.set_max_ray_length(-1.0)
    
    def test_message_flag_configuration(self):
        """Test message flag configuration."""
        # Test setting message flag
        self.model.set_message_flag(False)
        self.assertFalse(self.model._message_flag)
        
        self.model.set_message_flag(True)
        self.assertTrue(self.model._message_flag)
    
    def test_single_point_calculation(self):
        """Test sky view factor calculation for a single point."""
        # Test with no obstacles (should be close to 1.0)
        svf = self.model.calculate_sky_view_factor(0.0, 0.0, 0.0)
        self.assertIsInstance(svf, float)
        self.assertGreaterEqual(svf, 0.0)
        self.assertLessEqual(svf, 1.0)
        
        # Test with obstacles
        self.context.addTriangle(
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (0.0, 1.0, 1.0)
        )
        
        svf_with_obstacle = self.model.calculate_sky_view_factor(0.0, 0.0, 0.0)
        self.assertIsInstance(svf_with_obstacle, float)
        self.assertGreaterEqual(svf_with_obstacle, 0.0)
        self.assertLessEqual(svf_with_obstacle, 1.0)
        
        # SVF should be lower with obstacles
        self.assertLess(svf_with_obstacle, svf)
    
    def test_single_point_calculation_cpu(self):
        """Test CPU-based sky view factor calculation for a single point."""
        # Test with no obstacles (should be close to 1.0)
        svf = self.model.calculate_sky_view_factor_cpu(0.0, 0.0, 0.0)
        self.assertIsInstance(svf, float)
        self.assertGreaterEqual(svf, 0.0)
        self.assertLessEqual(svf, 1.0)
        
        # Test with obstacles
        self.context.addTriangle(
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (0.0, 1.0, 1.0)
        )
        
        svf_with_obstacle = self.model.calculate_sky_view_factor_cpu(0.0, 0.0, 0.0)
        self.assertIsInstance(svf_with_obstacle, float)
        self.assertGreaterEqual(svf_with_obstacle, 0.0)
        self.assertLessEqual(svf_with_obstacle, 1.0)
        
        # SVF should be lower with obstacles
        self.assertLess(svf_with_obstacle, svf)
    
    def test_multiple_points_calculation(self):
        """Test sky view factor calculation for multiple points."""
        points = [
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0)
        ]
        
        svfs = self.model.calculate_sky_view_factors(points)
        
        self.assertEqual(len(svfs), len(points))
        for svf in svfs:
            self.assertIsInstance(svf, float)
            self.assertGreaterEqual(svf, 0.0)
            self.assertLessEqual(svf, 1.0)
    
    def test_empty_points_list(self):
        """Test calculation with empty points list."""
        svfs = self.model.calculate_sky_view_factors([])
        self.assertEqual(svfs, [])
    
    def test_primitive_centers_calculation(self):
        """Test sky view factor calculation for primitive centers."""
        # Add some primitives
        self.context.addTriangle(
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.5, 1.0, 0.0)
        )
        self.context.addTriangle(
            (2.0, 0.0, 0.0),
            (3.0, 0.0, 0.0),
            (2.5, 1.0, 0.0)
        )
        
        svfs = self.model.calculate_sky_view_factors_for_primitives()
        
        self.assertEqual(len(svfs), 2)
        for svf in svfs:
            self.assertIsInstance(svf, float)
            self.assertGreaterEqual(svf, 0.0)
            self.assertLessEqual(svf, 1.0)
    
    def test_export_import_functionality(self):
        """Test export and import functionality."""
        # Calculate some SVFs
        points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]
        svfs = self.model.calculate_sky_view_factors(points)
        
        # Test export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_filename = f.name
        
        try:
            success = self.model.export_sky_view_factors(temp_filename)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(temp_filename))
            
            # Test import
            success = self.model.load_sky_view_factors(temp_filename)
            self.assertTrue(success)
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_get_sky_view_factors(self):
        """Test getting calculated sky view factors."""
        # Initially should be empty
        svfs = self.model.get_sky_view_factors()
        self.assertEqual(svfs, [])
        
        # After calculation, should contain results
        points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]
        self.model.calculate_sky_view_factors(points)
        
        svfs = self.model.get_sky_view_factors()
        self.assertEqual(len(svfs), 2)
    
    def test_statistics(self):
        """Test statistics functionality."""
        stats = self.model.get_statistics()
        self.assertIsInstance(stats, str)
        self.assertGreater(len(stats), 0)
    
    def test_cuda_optix_availability(self):
        """Test CUDA/OptiX availability checks."""
        cuda_available = self.model.is_cuda_available()
        optix_available = self.model.is_optix_available()
        
        self.assertIsInstance(cuda_available, bool)
        self.assertIsInstance(optix_available, bool)
    
    def test_reset_functionality(self):
        """Test reset functionality."""
        # Calculate some SVFs
        points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]
        self.model.calculate_sky_view_factors(points)
        
        # Verify data exists
        self.assertGreater(len(self.model.get_sky_view_factors()), 0)
        
        # Reset
        self.model.reset()
        
        # Verify data is cleared
        self.assertEqual(len(self.model.get_sky_view_factors()), 0)


class TestSkyViewFactorCamera(unittest.TestCase):
    """Test cases for SkyViewFactorCamera class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = Context()
        self.camera = SkyViewFactorCamera(self.context)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'camera'):
            del self.camera
        if hasattr(self, 'context'):
            del self.context
    
    def test_camera_creation(self):
        """Test that SkyViewFactorCamera can be created."""
        self.assertIsNotNone(self.camera)
        self.assertIsNotNone(self.camera._camera_ptr)
    
    def test_camera_position_configuration(self):
        """Test camera position configuration."""
        self.camera.set_position(1.0, 2.0, 3.0)
        self.assertEqual(self.camera._position, (1.0, 2.0, 3.0))
    
    def test_camera_target_configuration(self):
        """Test camera target configuration."""
        self.camera.set_target(0.0, 0.0, 0.0)
        self.assertEqual(self.camera._target, (0.0, 0.0, 0.0))
    
    def test_camera_up_configuration(self):
        """Test camera up vector configuration."""
        self.camera.set_up(0.0, 1.0, 0.0)
        self.assertEqual(self.camera._up, (0.0, 1.0, 0.0))
    
    def test_camera_field_of_view_configuration(self):
        """Test camera field of view configuration."""
        self.camera.set_field_of_view(45.0)
        self.assertEqual(self.camera._field_of_view, 45.0)
        
        # Test invalid field of view
        with self.assertRaises(ValueError):
            self.camera.set_field_of_view(0.0)
        
        with self.assertRaises(ValueError):
            self.camera.set_field_of_view(180.0)
    
    def test_camera_resolution_configuration(self):
        """Test camera resolution configuration."""
        self.camera.set_resolution(256, 256)
        self.assertEqual(self.camera._resolution, (256, 256))
        
        # Test invalid resolution
        with self.assertRaises(ValueError):
            self.camera.set_resolution(0, 256)
        
        with self.assertRaises(ValueError):
            self.camera.set_resolution(256, 0)
    
    def test_camera_ray_count_configuration(self):
        """Test camera ray count configuration."""
        self.camera.set_ray_count(50)
        self.assertEqual(self.camera._ray_count, 50)
        
        # Test invalid ray count
        with self.assertRaises(ValueError):
            self.camera.set_ray_count(0)
    
    def test_camera_max_ray_length_configuration(self):
        """Test camera max ray length configuration."""
        self.camera.set_max_ray_length(500.0)
        self.assertEqual(self.camera._max_ray_length, 500.0)
        
        # Test invalid max ray length
        with self.assertRaises(ValueError):
            self.camera.set_max_ray_length(0.0)
    
    def test_camera_rendering(self):
        """Test camera rendering."""
        # Add some obstacles
        self.context.addTriangle(
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (0.0, 1.0, 1.0)
        )
        
        # Configure camera
        self.camera.set_resolution(64, 64)
        self.camera.set_ray_count(10)  # Low ray count for fast testing
        
        # Render
        success = self.camera.render()
        self.assertTrue(success)
        self.assertTrue(self.camera._is_rendered)
    
    def test_camera_image_data(self):
        """Test camera image data retrieval."""
        # Add obstacles and render
        self.context.addTriangle(
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (0.0, 1.0, 1.0)
        )
        
        self.camera.set_resolution(32, 32)
        self.camera.set_ray_count(5)
        self.camera.render()
        
        # Get image data
        image_data = self.camera.get_image()
        self.assertIsInstance(image_data, list)
        self.assertEqual(len(image_data), 32 * 32)
        
        for pixel_value in image_data:
            self.assertIsInstance(pixel_value, float)
            self.assertGreaterEqual(pixel_value, 0.0)
            self.assertLessEqual(pixel_value, 1.0)
    
    def test_camera_pixel_value(self):
        """Test camera pixel value retrieval."""
        # Add obstacles and render
        self.context.addTriangle(
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (0.0, 1.0, 1.0)
        )
        
        self.camera.set_resolution(16, 16)
        self.camera.set_ray_count(5)
        self.camera.render()
        
        # Get pixel value
        pixel_value = self.camera.get_pixel_value(8, 8)
        self.assertIsInstance(pixel_value, float)
        self.assertGreaterEqual(pixel_value, 0.0)
        self.assertLessEqual(pixel_value, 1.0)
        
        # Test invalid pixel coordinates
        with self.assertRaises(ValueError):
            self.camera.get_pixel_value(16, 8)  # x out of bounds
        
        with self.assertRaises(ValueError):
            self.camera.get_pixel_value(8, 16)  # y out of bounds
    
    def test_camera_export(self):
        """Test camera image export."""
        # Add obstacles and render
        self.context.addTriangle(
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (0.0, 1.0, 1.0)
        )
        
        self.camera.set_resolution(16, 16)
        self.camera.set_ray_count(5)
        self.camera.render()
        
        # Export image
        with tempfile.NamedTemporaryFile(suffix='.ppm', delete=False) as f:
            temp_filename = f.name
        
        try:
            success = self.camera.export_image(temp_filename)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(temp_filename))
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_camera_statistics(self):
        """Test camera statistics."""
        stats = self.camera.get_statistics()
        self.assertIsInstance(stats, str)
    
    def test_camera_reset(self):
        """Test camera reset functionality."""
        # Add obstacles and render
        self.context.addTriangle(
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (0.0, 1.0, 1.0)
        )
        
        self.camera.set_resolution(16, 16)
        self.camera.set_ray_count(5)
        self.camera.render()
        
        # Verify data exists
        self.assertTrue(self.camera._is_rendered)
        self.assertGreater(len(self.camera._image_data), 0)
        
        # Reset
        self.camera.reset()
        
        # Verify data is cleared
        self.assertFalse(self.camera._is_rendered)
        self.assertEqual(len(self.camera._image_data), 0)


class TestSkyViewFactorIntegration(unittest.TestCase):
    """Integration tests for SkyViewFactor plugin."""
    
    def test_model_camera_integration(self):
        """Test integration between model and camera."""
        context = Context()
        
        # Add obstacles
        context.addTriangle(
            (-2.0, -2.0, 0.0),
            (2.0, -2.0, 0.0),
            (0.0, 2.0, 0.0)
        )
        
        # Create model and camera
        model = SkyViewFactorModel(context)
        camera = model.create_camera()
        
        # Configure both
        model.set_ray_count(100)
        camera.set_resolution(32, 32)
        camera.set_ray_count(10)
        
        # Calculate SVFs
        points = [(0.0, 0.0, 0.5), (1.0, 0.0, 0.5)]
        svfs = model.calculate_sky_view_factors(points)
        
        # Render camera
        success = camera.render()
        
        # Verify both work
        self.assertEqual(len(svfs), 2)
        self.assertTrue(success)
        
        # Clean up
        del model
        del camera


if __name__ == '__main__':
    unittest.main()
