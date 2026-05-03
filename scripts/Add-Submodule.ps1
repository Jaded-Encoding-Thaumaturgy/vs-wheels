<#
.SYNOPSIS
    Adds a submodule, checks out a specific tag, and stages the changes.
.PARAMETER $GitUrl
    The URL of the git to clone as submodule
.PARAMETER $Path
    The URL of the git to clone as submodule
.PARAMETER $Tag
    The URL of the git to clone as submodule
#>

param (
    [Parameter(Mandatory = $true)]
    [string]$GitUrl,
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [string]$Tag = ""
)

git submodule add $GitUrl $Path
if (-not [string]::IsNullOrWhiteSpace($Tag)) {
    git -C $Path checkout $Tag
}
git add $Path
