# Development

## Build Shell

Windows builds require the Visual Studio x64 developer environment. Start a configured shell from the repository root:

```powershell
just dev-shell
```

## Submodules

This repository vendors various dependencies as Git submodules.

Use these commands from the repository root:

```powershell
# Initialize or reset submodules to the commits tracked by this repo.
git submodule update --init --recursive

# Show each submodule's current commit and local status.
just substatus

# Native Git status output.
git submodule status

# Update every submodule to the remote branch configured in .gitmodules.
git submodule update --remote --recursive

# Update one submodule.
git submodule update --remote bm3dcuda/bm3dcpu/vapoursynth

# List tags for one submodule.
git -C bm3dcuda/bm3dcpu/vapoursynth tag
```

To pin a submodule to a tag:

```powershell
git -C bm3dcuda/bm3dcpu/vapoursynth fetch --tags
git -C bm3dcuda/bm3dcpu/vapoursynth tag
git -C bm3dcuda/bm3dcpu/vapoursynth checkout R57

git add bm3dcuda/bm3dcpu/vapoursynth
git commit -m "chore: update vapoursynth submodule to R57"
```
