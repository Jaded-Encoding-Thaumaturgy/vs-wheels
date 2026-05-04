cmake_minimum_required(VERSION 3.22)
project(DFTTEST2_NVRTC_Package)

# Define the include path relative to this wrapper
set(VS_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

# Fix version detection
if(SKBUILD_PROJECT_VERSION)
  set(VCS_TAG "v${SKBUILD_PROJECT_VERSION}" CACHE STRING "Version from scikit-build-core")
  set(CMAKE_DISABLE_FIND_PACKAGE_Git ON)
endif()

set(ENABLE_CUDA ON CACHE BOOL "" FORCE)
set(USE_NVRTC_STATIC ON CACHE BOOL "" FORCE)
set(ENABLE_CPU OFF CACHE BOOL "" FORCE)
set(ENABLE_GCC OFF CACHE BOOL "" FORCE)
set(ENABLE_HIP OFF CACHE BOOL "" FORCE)

# Add the submodule but skip its internal install rules
add_subdirectory(vs-dfttest2 EXCLUDE_FROM_ALL)

add_custom_target(build_nvrtc ALL DEPENDS dfttest2_nvrtc)

install(TARGETS dfttest2_nvrtc LIBRARY DESTINATION .)
