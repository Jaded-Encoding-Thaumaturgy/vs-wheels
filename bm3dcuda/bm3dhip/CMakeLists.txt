cmake_minimum_required(VERSION 3.20)
project(BM3DCUDA_Package)

# === C++ Standard & Options ===
set(
  VAPOURSYNTH_INCLUDE_DIRECTORY
  "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include"
  CACHE PATH
  "Path to VapourSynth headers"
)

# === Target Definition & Configuration ===
# Add the submodule
add_subdirectory(VapourSynth-BM3DCUDA)

# === Packaging & Installation ===
if(WIN32)
  file(TO_CMAKE_PATH "$ENV{HIP_PATH}" HIP_ROOT_DIR)
  if(NOT HIP_ROOT_DIR)
    file(TO_CMAKE_PATH "$ENV{ROCM_PATH}" HIP_ROOT_DIR)
  endif()

  if(HIP_ROOT_DIR)
    set(HIP_BIN_DIR "${HIP_ROOT_DIR}/bin")
    file(GLOB _DLLS "${HIP_BIN_DIR}/amdhip64_*.dll")
    file(GLOB _DLLS "${HIP_BIN_DIR}/rocm_kpack.dll")

    if(_DLLS)
      install(FILES ${_DLLS} DESTINATION .)
    else()
      message(WARNING "Could not find HIP DLLs in ${HIP_BIN_DIR}")
    endif()
  endif()
endif()

# Write VapourSynth Manifest
if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nbm3dhip\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibbm3dhip\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
