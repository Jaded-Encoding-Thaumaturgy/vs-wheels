# macOS-specific OpenVINO cache variables.

set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "")

# Use Homebrew's TBB instead of building from source.
# The subproject build produces dylibs with malformed __LINKEDIT segments
# that Xcode's install_name_tool can't process, breaking wheel delocating.
set(ENABLE_SYSTEM_TBB ON CACHE BOOL "")
set(ENABLE_INTEL_GPU OFF CACHE BOOL "")
set(ENABLE_ONEDNN_FOR_GPU OFF CACHE BOOL "")
set(ENABLE_INTEL_NPU OFF CACHE BOOL "")
