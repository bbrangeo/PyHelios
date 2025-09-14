# CMake patch for zlib compatibility in manylinux containers
# Addresses z_size_t and va_list type definition issues

# Add compiler definitions for compatibility
add_compile_definitions(_GNU_SOURCE)
add_compile_definitions(_LARGEFILE64_SOURCE=1)

# Ensure proper include directories
include_directories(/usr/include)

# Define z_size_t if not already defined (addresses issue #772)
check_type_size(z_size_t Z_SIZE_T)
if(NOT HAVE_Z_SIZE_T)
    add_compile_definitions(z_size_t=size_t)
endif()

# Ensure va_list is available
check_include_file(stdarg.h HAVE_STDARG_H)
if(HAVE_STDARG_H)
    add_compile_definitions(HAVE_STDARG_H)
endif()

# Additional type safety for manylinux
add_compile_definitions(ZLIB_CONST)

# Set appropriate C/C++ standards
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Enable position independent code for shared libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Compatibility flags for manylinux2014
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D_GNU_SOURCE")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GNU_SOURCE -D_GLIBCXX_USE_CXX11_ABI=0")
endif()