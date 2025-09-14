#!/usr/bin/env python3
"""
Wheel content validation script for PyHelios CI.
Validates that wheels contain both Python modules and native libraries.
"""

import zipfile
import sys
import os
from pathlib import Path

def validate_wheel(wheel_path):
    """Validate wheel contents."""
    print(f"Validating: {Path(wheel_path).name}")
    
    try:
        with zipfile.ZipFile(wheel_path, 'r') as zf:
            files = zf.namelist()
            
            # Check for Python plugins module
            py_files = [f for f in files if 'plugins/__init__.py' in f]
            native_files = [f for f in files if any(f.endswith(ext) for ext in ['.dll', '.so', '.dylib']) and 'plugins/' in f]
            
            print(f'  Python files: {len(py_files)} (needed: 1+)')
            print(f'  Native libraries: {len(native_files)} (needed: 1+)')
            
            if not py_files:
                print('  [ERROR] No Python plugins module found in wheel')
                return False
            if not native_files:
                print('  [ERROR] No native libraries found in wheel (pure Python wheel)')
                print('  This means prepare_wheel.py failed to copy native libraries')
                return False
            
            print('  [OK] Wheel contains both Python modules and native libraries')
            print(f'  Total files: {len(files)}')
            return True
            
    except Exception as e:
        print(f'  [ERROR] Cannot validate wheel: {e}')
        return False

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: validate_wheel.py <wheel_file>")
        sys.exit(1)
    
    wheel_path = sys.argv[1]
    if not validate_wheel(wheel_path):
        sys.exit(1)

if __name__ == '__main__':
    main()