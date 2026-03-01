param(
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceRoot = Join-Path $repoRoot ".claude\skills"
$targets = @(
    $repoRoot
)

$skillDirs = @(
    "clean-code-workflow-manager",
    "clean-code-principles-architect",
    "clean-code-change-safety-reviewer",
    "clean-code-testability-optimizer",
    "clean-code-_shared"
)

if (-not (Test-Path $sourceRoot)) {
    throw "Source skill root not found: $sourceRoot"
}

Write-Host "Source: $sourceRoot"
Write-Host "Targets:"
foreach ($target in $targets) {
    Write-Host " - $target"
}

foreach ($targetRoot in $targets) {
    if (-not (Test-Path $targetRoot)) {
        throw "Target root not found: $targetRoot"
    }

    foreach ($skillName in $skillDirs) {
        $src = Join-Path $sourceRoot $skillName
        $dst = Join-Path $targetRoot $skillName

        if (-not (Test-Path $src)) {
            throw "Missing source skill directory: $src"
        }

        if ($Apply) {
            if (Test-Path $dst) {
                Remove-Item $dst -Recurse -Force
            }
            Copy-Item $src $dst -Recurse
            Write-Host "[APPLY] Synced $skillName -> $dst"
        } else {
            Write-Host "[DRY-RUN] Would sync $skillName -> $dst"
        }
    }
}

if (-not $Apply) {
    Write-Host ""
    Write-Host "Dry run complete. Re-run with -Apply to perform sync."
}
