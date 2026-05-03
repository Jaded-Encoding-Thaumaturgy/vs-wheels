cmake_minimum_required(VERSION 3.20)
project(BM3DCUDA_Package)

# Define the include path relative to this wrapper
set(
  VAPOURSYNTH_INCLUDE_DIRECTORY
  "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include"
  CACHE PATH
  "Path to VapourSynth headers"
)

# Add the submodule
add_subdirectory(VapourSynth-BM3DCUDA)
