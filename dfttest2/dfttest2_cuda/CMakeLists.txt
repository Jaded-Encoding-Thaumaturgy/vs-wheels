cmake_minimum_required(VERSION 3.22)
project(DFTTEST2_CUDA_Package)

# === Apply patches ===
include("${CMAKE_CURRENT_SOURCE_DIR}/ApplyPatch.cmake")

set(SRC_DFTTEST2_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vs-dfttest2")
set(BIN_DFTTEST2_DIR "${CMAKE_CURRENT_BINARY_DIR}/vs-dfttest2")

add_patched_source(
  PATCHED_WIN32
  "${SRC_DFTTEST2_DIR}/cuda_source/win32.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/patches/nvidia-wheel-paths.patch"
)

# === C++ Standard & Options ===
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(VS_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

if(SKBUILD_PROJECT_VERSION)
  set(VCS_TAG "v${SKBUILD_PROJECT_VERSION}" CACHE STRING "Version from scikit-build-core")
  set(CMAKE_DISABLE_FIND_PACKAGE_Git ON)
endif()

set(ENABLE_CUDA ON CACHE BOOL "" FORCE)
set(USE_NVRTC_STATIC ON CACHE BOOL "" FORCE)
set(ENABLE_CPU OFF CACHE BOOL "" FORCE)
set(ENABLE_GCC OFF CACHE BOOL "" FORCE)
set(ENABLE_HIP OFF CACHE BOOL "" FORCE)

# === Dependencies ===
find_package(CUDAToolkit REQUIRED)

# === Target Definition & Configuration ===
add_library(dfttest2_cuda MODULE vs-dfttest2/cuda_source/source.cpp "${PATCHED_WIN32}")

target_include_directories(
  dfttest2_cuda
  PRIVATE "${VS_INCLUDE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}" "${SRC_DFTTEST2_DIR}"
)

configure_file(vs-dfttest2/common/config.h.in config.h)

target_link_libraries(dfttest2_cuda PRIVATE CUDA::cuda_driver CUDA::cufft)

if(MSVC)
  target_link_options(dfttest2_cuda PRIVATE "delayimp.lib" "/DELAYLOAD:cufft64_12.dll")
  target_link_libraries(dfttest2_cuda PRIVATE Ws2_32 ntdll)
endif()

# Hide static and internal symbols to avoid conflicts with dynamically loaded CUDA libraries
if(UNIX)
  set_target_properties(dfttest2_cuda PROPERTIES CXX_VISIBILITY_PRESET hidden VISIBILITY_INLINES_HIDDEN ON)
  set_target_properties(dfttest2_cuda PROPERTIES INSTALL_RPATH "$ORIGIN;$ORIGIN/../../../nvidia/cu13/lib")
endif()

add_custom_target(build_cuda ALL DEPENDS dfttest2_cuda)

# === Link Libraries Setup ===
# Post-process the target to fix Linux driver initialization
if(UNIX)
  execute_process(
    COMMAND
      ${CMAKE_COMMAND} -E create_symlink "${CUDAToolkit_LIBRARY_DIR}/stubs/libcuda.so"
      "${CMAKE_CURRENT_BINARY_DIR}/libcuda.so.1"
  )

  target_link_directories(dfttest2_cuda PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
  target_link_libraries(dfttest2_cuda PRIVATE :libcuda.so.1)
  target_link_options(dfttest2_cuda PRIVATE "-Wl,--exclude-libs,ALL")
endif()

# Link nvJitLink_static for CUDA 12+ (needed when USE_NVRTC_STATIC is ON)
target_link_directories(dfttest2_cuda PRIVATE "${CUDAToolkit_LIBRARY_DIR}")
target_link_libraries(
  dfttest2_cuda
  PRIVATE nvrtc_static nvrtc-builtins_static nvptxcompiler_static nvJitLink_static nvptxcompiler_static
)

# === Packaging & Installation ===
install(TARGETS dfttest2_cuda LIBRARY DESTINATION .)

if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\ndfttest2_cuda\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibdfttest2_cuda\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
