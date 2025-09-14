#!/usr/bin/env python3
"""
Test wheel import functionality in isolation.
Tests that installed wheels work correctly without source code contamination.
"""

import sys
import os

def main():
    """Test wheel import functionality."""
    print('=== Wheel Import Test ===')
    print(f'Python: {sys.executable}')
    print(f'Working directory: {os.getcwd()}')
    print(f'Platform: {sys.platform}')

    try:
        import pyhelios
        print(f'[OK] PyHelios3D {pyhelios.__version__} imported successfully')
        
        # Test native library loading
        from pyhelios.plugins import get_plugin_info
        info = get_plugin_info()
        print(f'[OK] Platform: {info["platform"]}')
        print(f'[OK] Mock mode: {info["is_mock"]}')
        
        if info['is_mock']:
            print('[ERROR] Wheel is in mock mode - native libraries not found!')
            print(f'  Plugin directory: {info.get("plugin_dir", "Not set")}')
            available = info.get("available_files", [])
            print(f'  Available files: {available}')
            if not available:
                print('  No library files found - wheel packaging failed')
            raise RuntimeError('Native libraries not working in installed wheel')
        else:
            lib_path = info.get('library_path', 'Unknown')
            print(f'[SUCCESS] Native library loaded from: {lib_path}')
        
        print('[OK] Wheel functionality test completed successfully')
        
    except Exception as e:
        print(f'[FAILED] {e}')
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)