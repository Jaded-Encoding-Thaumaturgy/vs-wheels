# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "dumb-pypi>=1.15.0",
#     "niquests>=3.18.7",
#     "rich>=15.0.0",
# ]
# ///
"""
Generate a PEP 503 Simple Repository API index from GitHub Releases.
"""

import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, NotRequired, Required, TypedDict

import niquests
import rich.console
import rich.logging
from dumb_pypi.main import main as dumb_pypi_main  # type: ignore[import-untyped]

PACKAGES_URL_PLACEHOLDER = "https://__PACKAGES_PLACEHOLDER__"
OUTPUT_DIR = Path("_site")
LOGO_WIDTH = 100


class AssetInfo(TypedDict, total=False):
    url: Required[str]
    hash: Required[str]
    upload_timestamp: Required[int]
    core_metadata: NotRequired[str]
    requires_python: NotRequired[str]
    yanked_reason: NotRequired[str]


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


def github_api_get(url: str, token: str | None) -> list[dict[str, Any]]:
    logger.debug(f"Fetching {url}...")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with niquests.get(url, headers=headers) as resp:
        return resp.raise_for_status().json()


def fetch_releases(repo: str, token: str | None = None) -> list[dict[str, Any]]:
    logger.debug(f"Fetching releases for {repo}...")
    releases = list[dict[str, Any]]()
    page = 1
    while True:
        batch = github_api_get(f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}", token)
        if not batch:
            break
        releases.extend(batch)
        page += 1

    logger.info(f"Found {len(releases)} releases.")
    return releases


def fetch_hf_files(bucket_id: str) -> dict[str, str]:
    """Fetch the list of files in the Hugging Face bucket and map them to their download URLs."""
    url = f"https://huggingface.co/api/buckets/{bucket_id}/tree"
    logger.info("Fetching HuggingFace files list from %s...", url)
    try:
        with niquests.get(url) as resp:
            files = resp.raise_for_status().json()
            return {
                item["path"]: f"https://huggingface.co/buckets/{bucket_id}/resolve/{item['path']}"
                for item in files
                if item.get("type") == "file"
            }
    except Exception as e:
        logger.warning("Failed to fetch HuggingFace files: %s", e)
        logger.debug("", exc_info=e)
        return {}


def fetch_requires_python(asset: dict[str, Any], token: str | None) -> str | None:
    """Fetch and parse the Requires-Python header from the metadata asset."""
    headers = dict[str, str]()
    if token:
        headers["Authorization"] = f"Bearer {token}"
        url = asset["url"]
        headers["Accept"] = "application/octet-stream"
    else:
        url = asset["browser_download_url"]

    try:
        logger.debug(f"Fetching metadata file from: {url}")
        with niquests.get(url, headers=headers) as resp:
            resp.raise_for_status()
            assert resp.text is not None
            for line in resp.text.splitlines():
                if line.lower().startswith("requires-python:"):
                    return line.split(":", 1)[1].strip()
    except Exception as e:
        logger.warning(f"Failed to fetch or parse metadata from {url}: {e}")
        logger.debug("", exc_info=e)
    return None


def collect_assets(releases: list[dict[str, Any]], token: str | None = None) -> dict[str, AssetInfo]:
    """
    Return a {filename: AssetInfo} mapping for all dist assets.
    """
    assets: dict[str, AssetInfo] = {}

    for release in releases:
        release_assets = {a["name"]: a for a in release.get("assets", [])}
        for name, release_asset in release_assets.items():
            if not name.endswith((".whl", ".tar.gz")):
                continue

            url = release_asset["browser_download_url"]
            digest = release_asset.get("digest", "")
            updated_at = release_asset["updated_at"]

            if not digest.startswith("sha256:"):
                logger.warning(f"No SHA256 digest found for {name} in API response. Skipping.")
                continue

            assets[name] = AssetInfo(
                url=url,
                hash=digest.split(":", 1)[1],
                upload_timestamp=int(datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ").astimezone().timestamp()),
            )

            # Check if a .metadata file exists in the release assets
            if meta_asset := release_assets.get(name + ".metadata"):
                meta_digest = meta_asset.get("digest", "")
                if meta_digest.startswith("sha256:"):
                    assets[name]["core_metadata"] = f"sha256={meta_digest.split(':', 1)[1]}"
                else:
                    assets[name]["core_metadata"] = "true"

                # Download and parse Requires-Python from metadata file
                if requires_python := fetch_requires_python(meta_asset, token):
                    assets[name]["requires_python"] = requires_python
                    logger.debug(f"Found Requires-Python: {requires_python} for {name}")

            # Check if the release has been yanked
            release_body = release.get("body", "") or ""
            release_name = release.get("name", "") or ""
            is_yanked = "[yanked]" in release_body.lower() or "[yanked]" in release_name.lower()
            if is_yanked:
                assets[name]["yanked_reason"] = "Yanked via release description"

    return assets


def run_dumb_pypi(assets: dict[str, AssetInfo], title: str) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        package_list = Path(tmpdir) / "packages.json"

        # Write one JSON object per line (dumb-pypi --package-list-json format)
        with package_list.open("w", encoding="utf-8") as f:
            for filename in sorted(assets):
                asset = assets[filename]
                entry = {
                    "filename": filename,
                    "hash": f"sha256={asset['hash']}",
                    "upload_timestamp": asset["upload_timestamp"],
                    "uploaded_by": "Jaded-Encoding-Thaumaturgy",
                }
                if "core_metadata" in asset:
                    entry["core_metadata"] = asset["core_metadata"]
                if "requires_python" in asset:
                    entry["requires_python"] = asset["requires_python"]
                if "yanked_reason" in asset:
                    entry["yanked_reason"] = asset["yanked_reason"]
                json.dump(entry, f)
                f.write("\n")

        args = [
            "--package-list-json",
            str(package_list),
            "--packages-url",
            PACKAGES_URL_PLACEHOLDER,
            "--output-dir",
            str(OUTPUT_DIR),
            "--title",
            title,
            "--logo",
            "https://avatars.githubusercontent.com/u/137835541",
            "--logo-width",
            str(LOGO_WIDTH),
        ]
        dumb_pypi_main(args)
    _fixup_urls(assets)


def _fixup_urls(assets: dict[str, AssetInfo]) -> None:
    extra_style = (
        f"\n<style>.title h1 {{ "
        f"background-size: contain; "
        f"background-position: left center; "
        f"padding-left: {LOGO_WIDTH + 10}px !important; "
        f"}}</style>\n"
    )

    for path in OUTPUT_DIR.rglob("*"):
        if path.is_file() and path.suffix in (".html", ".json"):
            content = path.read_text(encoding="utf-8")
            original = content

            if extra_style and path.suffix == ".html" and "</head>" in content:
                content = content.replace("</head>", f"{extra_style}</head>")

            for filename, data in assets.items():
                placeholder_url = f"{PACKAGES_URL_PLACEHOLDER}/{filename}"
                content = content.replace(placeholder_url, data["url"])

            if content != original:
                path.write_text(content, encoding="utf-8")


def main() -> None:
    repo = os.environ.get("GITHUB_REPOSITORY", "Jaded-Encoding-Thaumaturgy/vs-wheels")
    token = os.environ.get("GITHUB_TOKEN")
    title = os.environ.get("INDEX_TITLE", "JET Package Index")
    bucket_id = os.environ.get("HF_BUCKET", "Ichunjo/wheel-storage")

    logger.info("Generating index for %s -> %s", repo, OUTPUT_DIR)

    releases = fetch_releases(repo, token)
    assets = collect_assets(releases, token)

    hf_files = fetch_hf_files(bucket_id)

    for name, asset in assets.items():
        if name in hf_files:
            logger.info("Using HuggingFace URL for %s", name)
            asset["url"] = hf_files[name]
        else:
            logger.info("Using GitHub URL for %s (not found in HF bucket)", name)

    logger.info("Found %s distribution file(s) across %s release(s)", len(assets), len(releases))

    if not assets:
        logger.warning("No distribution assets found in any release.")
    else:
        run_dumb_pypi(assets, title)

    logger.info("Done.")


if __name__ == "__main__":
    main()
