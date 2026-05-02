# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "dumb-pypi>=1.15.0",
#     "niquests>=3.18.7",
# ]
# ///
"""
Generate a PEP 503 Simple Repository API index from GitHub Releases.
"""

import asyncio
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import niquests
from dumb_pypi.main import main as dumb_pypi_main  # type: ignore[import-untyped]

PACKAGES_URL_PLACEHOLDER = "https://__PACKAGES_PLACEHOLDER__"
OUTPUT_DIR = Path("_site")
LOGO_WIDTH = 100


def github_api_get(url: str, token: str | None) -> list[dict[str, Any]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with niquests.get(url, headers=headers) as resp:
        return resp.raise_for_status().json()


def fetch_releases(repo: str, token: str | None = None) -> list[dict[str, Any]]:
    releases = list[dict[str, Any]]()
    page = 1
    while True:
        batch = github_api_get(f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}", token)
        if not batch:
            break
        releases.extend(batch)
        page += 1
    return releases


async def collect_assets(releases: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Return a {filename: {url, hash}} mapping for all dist assets."""
    assets = dict[str, dict[str, str]]()
    asset_info = list[tuple[str, str]]()
    cache = load_cache()

    for release in releases:
        for asset in release.get("assets", []):
            name = asset["name"]
            if name.endswith(".whl") or name.endswith(".tar.gz"):
                url = asset["browser_download_url"]
                file_hash = cache.get(name)

                if file_hash:
                    assets[name] = {"url": url, "hash": file_hash}
                else:
                    asset_info.append((name, url))

    semaphore = asyncio.Semaphore(5)
    tasks = dict[str, tuple[str, asyncio.Task[str]]]()

    if not asset_info:
        return assets

    async with niquests.AsyncSession() as session:
        async with asyncio.TaskGroup() as tg:
            for name, url in asset_info:
                print(f"Hashing new asset (async): {name}...", file=sys.stderr)
                task = tg.create_task(calculate_sha256(session, url, semaphore))
                tasks[name] = (url, task)

        for name, (url, task) in tasks.items():
            assets[name] = {"url": url, "hash": task.result()}

    return assets


async def calculate_sha256(session: niquests.AsyncSession, url: str, semaphore: asyncio.Semaphore) -> str:
    async with semaphore:
        resp = await session.get(url, stream=True)
        resp.raise_for_status()

        sha256 = hashlib.sha256()
        async for chunk in await resp.iter_content():
            sha256.update(chunk)

        return sha256.hexdigest()


def load_cache() -> dict[str, str]:
    cache_path = OUTPUT_DIR / "packages.json"
    if not cache_path.exists():
        return {}

    cache = dict[str, str]()
    with cache_path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if "filename" in data and "hash" in data:
                # hash is stored as sha256=hex
                cache[data["filename"]] = data["hash"].split("=", 1)[-1]
    return cache


def run_dumb_pypi(assets: dict[str, dict[str, str]], title: str) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        package_list = Path(tmpdir) / "packages.json"

        # Write one JSON object per line (dumb-pypi --package-list-json format)
        with package_list.open("w", encoding="utf-8") as f:
            for filename in sorted(assets):
                entry = {"filename": filename, "hash": f"sha256={assets[filename]['hash']}"}
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
            "--no-generate-timestamp",
            "--logo",
            "https://avatars.githubusercontent.com/u/137835541",
            "--logo-width",
            str(LOGO_WIDTH),
        ]
        dumb_pypi_main(args)
    _fixup_urls(assets)


def _fixup_urls(assets: dict[str, dict[str, str]]) -> None:
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


async def main() -> None:
    repo = os.environ.get("GITHUB_REPOSITORY", "Jaded-Encoding-Thaumaturgy/vs-wheels")
    token = os.environ.get("GITHUB_TOKEN")
    title = os.environ.get("INDEX_TITLE", "JET Package Index")

    print(f"Generating index for {repo} -> {OUTPUT_DIR}", file=sys.stderr)

    releases = fetch_releases(repo, token)
    assets = await collect_assets(releases)

    print(f"Found {len(assets)} distribution file(s) across {len(releases)} release(s)", file=sys.stderr)

    if not assets:
        print("WARNING: No distribution assets found in any release.", file=sys.stderr)
    else:
        run_dumb_pypi(assets, title)

    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
