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
            "nvidia-cublas>=13.0.0,<14.0.0",  # renovate: datasource=pypi depName=nvidia-cublas
            "nvidia-cuda-runtime>=13.0.0,<14.0.0",  # renovate: datasource=pypi depName=nvidia-cuda-runtime
            "nvidia-cudnn-cu13>=9.0.0,<10.0.0",  # renovate: datasource=pypi depName=nvidia-cudnn-cu13
            "nvidia-cuda-cupti>=13.0.0,<14.0.0",  # renovate: datasource=pypi depName=nvidia-cuda-cupti
            "nvidia-curand>=10.0.0,<11.0.0",  # renovate: datasource=pypi depName=nvidia-curand
        ]
    )
    data["project"].setdefault("optional-dependencies", {})
    data["project"]["optional-dependencies"]["cufft"] = [
        "nvidia-cufft>=12.0.0,<13.0.0",  # renovate: datasource=pypi depName=nvidia-cufft
    ]

    for override in data["tool"]["scikit-build"]["overrides"]:
        if override["if"]["platform-system"] in ["win32", "linux"]:
            override["cmake"]["define"]["ENABLE_CUDA"] = "ON"
        if override["if"]["platform-system"] == "win32":
            override["cmake"]["define"]["CMAKE_MSVC_RUNTIME_LIBRARY"] = "MultiThreadedDLL"

    pyproject.write_text(tomli_w.dumps(data), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
