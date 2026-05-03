cmake_minimum_required(VERSION 3.20)
project(BM3DCPU_Distribution VERSION 2.6 LANGUAGES CXX)

set(VAPOURSYNTH_INCLUDE_DIRECTORY "vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

option(BM3D_MULTI_TARGET "Build multiple optimized binaries for distribution" OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(SOURCE_FILE "VapourSynth-BM3DCUDA/cpu_source/source.cpp")
set(SOURCE_DIR "VapourSynth-BM3DCUDA/cpu_source")

include("${CMAKE_CURRENT_SOURCE_DIR}/Common.cmake")

if(BM3D_MULTI_TARGET)
  file(READ "arch_configs.json" JSON_DATA)
  string(JSON CONFIG_COUNT LENGTH "${JSON_DATA}")
  math(EXPR CONFIG_MAX "${CONFIG_COUNT} - 1")

  foreach(I RANGE ${CONFIG_MAX})
    string(JSON CONFIG GET "${JSON_DATA}" ${I})
    string(JSON SUFFIX GET "${CONFIG}" "suffix")
    string(JSON MTUNE GET "${CONFIG}" "mtune")
    string(JSON EXTRA_FLAGS GET "${CONFIG}" "extra_flags")

    set(TARGET_NAME "bm3dcpu_${SUFFIX}")
    add_library(${TARGET_NAME} SHARED ${SOURCE_FILE})
    target_include_directories(${TARGET_NAME} PRIVATE ${VAPOURSYNTH_INCLUDE_DIRECTORY})

    apply_bm3d_compile_options(${TARGET_NAME} "${MTUNE}" "${EXTRA_FLAGS}")

    set_target_properties(${TARGET_NAME} PROPERTIES OUTPUT_NAME "bm3dcpu${SUFFIX}")

    install(TARGETS ${TARGET_NAME} DESTINATION .)
  endforeach()

  install(FILES "manifest.vs" DESTINATION .)

else()
  add_library(bm3dcpu SHARED ${SOURCE_FILE})
  target_include_directories(bm3dcpu PRIVATE ${VAPOURSYNTH_INCLUDE_DIRECTORY})

  apply_bm3d_compile_options(bm3dcpu "native" "")

  install(TARGETS bm3dcpu DESTINATION .)
endif()
