# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "tomli-w>=1.2.0",
# ]
# ///

import sys
import tomllib
from pathlib import Path

import tomli_w


def main(pyproject: Path) -> None:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    data["project"]["name"] += "-cuda"
    data["project"]["description"] += " with CUDA support"
    data["tool"]["scikit-build"]["wheel"]["install-dir"] += "-cuda"
    data["project"]["dependencies"].extend(
        [
            # TODO: Keep in sync with .github/workflows/pkg-ort-cuda.yml and current CUDA Toolkit release notes
            # CUDA 13.0 is currently the maximum supported by ONNX Runtime
            # https://docs.nvidia.com/cuda/archive/13.0.3/cuda-toolkit-release-notes/index.html
            "nvidia-cublas~=13.1.1",
            "nvidia-cuda-runtime~=13.0.96",
            "nvidia-cudnn-cu13~=9.23.1",  # renovate: datasource=pypi depName=nvidia-cudnn-cu13
            "nvidia-cufft~=12.0.0",
            "nvidia-cuda-cupti~=13.0.85",
            "nvidia-cuda-nvrtc~=13.0.88",
            "nvidia-nvjitlink~=13.0.88",
            "nvidia-curand~=10.4.0.35",
        ]
    )

    for override in data["tool"]["scikit-build"]["overrides"]:
        if override["if"]["platform-system"] in ["win32", "linux"]:
            override["cmake"]["define"]["ENABLE_CUDA"] = "ON"

    pyproject.write_text(tomli_w.dumps(data), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
