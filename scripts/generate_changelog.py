# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anyio>=4.13.0",
#     "cyclopts>=4.17.0",
#     "niquests>=3.19.0",
#     "rich>=15.0.0",
# ]
# ///

import asyncio
import io
import json
import logging
import os
import shutil
import subprocess
import zipfile
from contextlib import suppress
from datetime import UTC, datetime
from functools import cached_property
from pathlib import Path
from typing import Any

import anyio
import cyclopts
import niquests
import rich
import rich.console
import rich.logging

console = rich.console.Console(
    stderr=True,
    force_terminal=True if os.environ.get("GITHUB_ACTIONS") else None,
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[rich.logging.RichHandler(rich_tracebacks=True, console=console, show_path=True)],
    format="%(message)s",
    datefmt="[%X]",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = cyclopts.App(console=console)


class Downloader:
    def __init__(self) -> None:
        self.sema = anyio.Semaphore(8)
        self.session = niquests.AsyncSession(
            base_url="https://api.github.com/repos/Jaded-Encoding-Thaumaturgy/vs-wheels/actions/",
            headers=self.headers,
        )

    @cached_property
    def headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "vs-wheels-updater",
            "Authorization": f"Bearer {get_github_token()}",
        }

    async def all_metadata(self, metadata_dir: anyio.Path) -> None:
        shutil.rmtree(metadata_dir, ignore_errors=True)
        await metadata_dir.mkdir(parents=True, exist_ok=True)

        async with self.session, asyncio.TaskGroup() as tg:
            async for wf in anyio.Path(".github/workflows").glob("pkg-*.yml"):
                tg.create_task(self.workflow_metadata(wf.name, metadata_dir))

    async def workflow_metadata(self, wf: str, metadata_dir: anyio.Path) -> None:
        async with self.sema:
            response = await self.session.get(f"workflows/{wf}/runs", params={"status": "success", "per_page": "10"})
            if response.status_code != 200:
                logger.error("Failed to list runs for %s: HTTP %s - %s", wf, response.status_code, response.text)
                return
            runs = response.json().get("workflow_runs", [])

            if not runs:
                logger.info("No successful runs found for %s", wf)
                return

            for run in runs:
                run_id = run["id"]
                run_date = run["created_at"][:10]
                run_sha = run["head_sha"]

                art_response = await self.session.get(f"runs/{run_id}/artifacts")
                if art_response.status_code != 200:
                    logger.error("Failed to list artifacts for run %s: HTTP %s", run_id, art_response.status_code)
                    continue
                artifacts = art_response.json().get("artifacts", [])
                metadata_artifact = next((art for art in artifacts if art.get("name", "").endswith("-metadata")), None)

                if not metadata_artifact:
                    continue

                if metadata_artifact.get("expired", False):
                    logger.debug("Metadata artifact for run %s has expired", run_id)
                    continue

                download_url = metadata_artifact["archive_download_url"]
                dl_response = await self.session.get(download_url)
                if dl_response.status_code != 200:
                    logger.error("Failed to download artifact for run %s: HTTP %s", run_id, dl_response.status_code)
                    continue
                assert dl_response.content

                wf_dir = metadata_dir / anyio.Path(wf).stem
                await wf_dir.mkdir(parents=True, exist_ok=True)

                try:
                    with zipfile.ZipFile(io.BytesIO(dl_response.content)) as z:
                        z.extractall(wf_dir)
                except zipfile.BadZipFile:
                    logger.error("Downloaded metadata from run %s for %s is not a valid ZIP file", run_id, wf)
                    continue

                async for jf in wf_dir.glob("**/*.json"):
                    data = json.loads(await jf.read_text())
                    data["release_date"] = run_date
                    data["commit"] = run_sha
                    await jf.write_text(json.dumps(data, indent=2))

                logger.info("Successfully downloaded metadata from run %s for %s (Run date: %s)", run_id, wf, run_date)
                return
            logger.info("No metadata found in the last 10 successful runs for %s", wf)


def get_github_token() -> str:
    if token := (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")):
        return token

    with suppress(subprocess.CalledProcessError):
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()

    raise NotImplementedError


def generate_changelog(metadata_dir: os.PathLike[str]) -> None:
    metadata_files = list(Path(metadata_dir).rglob("*.json"))

    if not metadata_files:
        logger.info("No new metadata files found. Generating from existing changelog.")

    db_file = Path("changelog.json")
    db: dict[str, Any] = json.loads(db_file.read_text())

    # Merge new metadata
    for mf in metadata_files:
        data = json.loads(mf.read_text())
        if (pkg := data.get("package")) and (version := data.get("version")):
            db.setdefault(pkg, {}).setdefault(version, {}).update(data)
            db[pkg][version].setdefault("release_date", datetime.now(UTC).strftime("%Y-%m-%d"))

    db_file.write_text(json.dumps(db, indent=2))

    # Generate CHANGELOG.md
    cl_content = "# Plugins Release Changelog\n\n"
    for pkg in sorted(db.keys()):
        cl_content += f"## {pkg}\n\n"

        for version in sorted(db[pkg].keys(), reverse=True):
            data = db[pkg][version]
            date = data["release_date"]
            cl_content += f"### Version {version} ({date})\n\n"

            if "notes" in data:
                cl_content += f"{data['notes']}\n\n"

            for k, v in data.items():
                if k not in ["package", "version", "release_date", "notes", "commit"]:
                    formatted_key = k.replace("_", " ").title()
                    formatted_key = (
                        formatted_key.replace("Macos", "macOS")
                        .replace("Onnxruntime", "ONNX Runtime")
                        .replace("Onnx", "ONNX")
                        .replace("Ncnn", "NCNN")
                        .replace("Cuda", "CUDA")
                        .replace("Hip", "HIP")
                        .replace("Cudnn", "cuDNN")
                        .replace("Openvino", "OpenVINO")
                        .replace("Tensorrt", "TensorRT")
                        .replace("Rtx", "RTX")
                    )
                    cl_content += f"- **{formatted_key}**: {v}\n"

            if "commit" in data:
                commit_sha = data["commit"]
                cl_content += f"- **Commit**: [{commit_sha[:7]}](https://github.com/Jaded-Encoding-Thaumaturgy/vs-wheels/commit/{commit_sha})\n"
        cl_content += "\n"

    Path("CHANGELOG.md").write_text(cl_content)
    logger.info("Changelog generated successfully. Updated %s packages.", len(db))


@app.default
async def main(download: bool = True) -> None:
    """
    Download metadata and generate changelog.

    Args:
        download: Skip downloading metadata from GitHub.
    """
    metadata_dir = anyio.Path("metadata_files")

    if download:
        await Downloader().all_metadata(metadata_dir)

    generate_changelog(metadata_dir)


if __name__ == "__main__":
    app()
