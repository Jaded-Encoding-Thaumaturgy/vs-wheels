from pathlib import Path
import sys
from typing import Any

from hatchling.bridge.app import Application
from hatchling.metadata.core import ProjectMetadata

src_path = Path(__file__).parent / "."
sys.path.insert(0, str(src_path))

from fmtconv.hatch_build import CustomHook as FMTConvHook  # noqa: E402


class CustomHook(FMTConvHook):
    def __init__(
        self,
        root: str,
        config: dict[str, Any],
        build_config: Any,
        metadata: ProjectMetadata,
        directory: str,
        target_name: str,
        app: Application | None = None,
    ) -> None:
        super().__init__(str(Path(root) / "fmtconv"), config, build_config, metadata, directory, target_name, app)


def get_build_hook() -> type[CustomHook]:
    return CustomHook
