# Linux-specific ONNX Runtime cache variables.

set(CMAKE_POSITION_INDEPENDENT_CODE ON CACHE BOOL "")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-error=unused-variable" CACHE STRING "" FORCE)
