"""
Generate PEP 658 metadata files (.metadata) for all distribution files in dist/.
"""

import glob
import sys
import tarfile
import zipfile
from collections.abc import Callable
from functools import wraps


def generate_metadata() -> None:
    # Generate metadata for wheels
    for whl in glob.glob("dist/*.whl"):
        generate_metadata_wheel(whl)

    # Generate metadata for sdists
    for sdist in glob.glob("dist/*.tar.gz"):
        generate_metadata_sdist(sdist)


def catch_exception(func: Callable[[str], None]) -> Callable[[str], None]:
    @wraps(func)
    def wrapper(arg: str) -> None:
        try:
            func(arg)
        except Exception as e:  # noqa: BLE001
            print(f"Failed to {func.__name__} for {arg}: {e}", file=sys.stderr)

    return wrapper


@catch_exception
def generate_metadata_wheel(whl: str) -> None:
    with zipfile.ZipFile(whl) as z:
        for name in z.namelist():
            if not name.endswith(".dist-info/METADATA"):
                continue

            with open(whl + ".metadata", "wb") as f:
                f.write(z.read(name))
            print(f"Extracted metadata for {whl}", file=sys.stderr)
            break


@catch_exception
def generate_metadata_sdist(sdist: str) -> None:
    with tarfile.open(sdist, "r:gz") as t:
        for member in t.getmembers():
            if member.name.endswith("/PKG-INFO") or member.name == "PKG-INFO":
                f = t.extractfile(member)
                if f:
                    with open(sdist + ".metadata", "wb") as out:
                        out.write(f.read())
                    print(f"Extracted metadata for {sdist}", file=sys.stderr)
                break


if __name__ == "__main__":
    generate_metadata()
