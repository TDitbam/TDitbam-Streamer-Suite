param(
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
Set-Location -LiteralPath $projectRoot

function Remove-ProjectOutput {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $target = [IO.Path]::GetFullPath((Join-Path $projectRoot $RelativePath))
    $rootPrefix = [IO.Path]::GetFullPath($projectRoot) + [IO.Path]::DirectorySeparatorChar
    if (-not $target.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the project: $target"
    }
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
}

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }

Remove-ProjectOutput "build"
Remove-ProjectOutput "dist"
Remove-ProjectOutput "installer"

Write-Host "[1/2] Building the separated application folder..."
& $python -m PyInstaller --clean --noconfirm "build_exe.spec"
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

$appExe = Join-Path $projectRoot "dist\StreamerSuite\StreamerSuite.exe"
if (-not (Test-Path -LiteralPath $appExe)) {
    throw "Expected application executable was not created: $appExe"
}

Copy-Item -LiteralPath (Join-Path $projectRoot "CREDITS.md") -Destination (Join-Path $projectRoot "dist\StreamerSuite\CREDITS.md") -Force

$supportFiles = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot "dist\StreamerSuite\parts") -Recurse -File)
$appHash = (Get-FileHash -LiteralPath $appExe -Algorithm SHA256).Hash
@(
    "TDitbam Streamer Suite v3.6.0 separated application build",
    "Main executable: StreamerSuite.exe",
    "Support directory: parts\ ($($supportFiles.Count) files)",
    "Keep StreamerSuite.exe and the parts directory together.",
    "SHA256 StreamerSuite.exe: $appHash"
) | Set-Content -LiteralPath (Join-Path $projectRoot "dist\StreamerSuite\APP-PARTS.txt") -Encoding utf8

if ($SkipInstaller) {
    Write-Host "Application build complete: $appExe"
    exit 0
}

$isccCandidates = @(
    (Get-Command "ISCC.exe" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    (Join-Path $projectRoot ".tools\Inno Setup 6\ISCC.exe"),
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique

$iscc = $isccCandidates | Select-Object -First 1
if (-not $iscc) {
    throw "Inno Setup 6 compiler (ISCC.exe) was not found. The app EXE was built successfully; install Inno Setup 6 and run this script again."
}

Write-Host "[2/2] Building the split installer parts..."
& $iscc "installer_script.iss"
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup build failed with exit code $LASTEXITCODE"
}

$installerFiles = Get-ChildItem -LiteralPath (Join-Path $projectRoot "installer") -File |
    Sort-Object Name
if (-not $installerFiles) {
    throw "Inno Setup completed without producing installer files."
}

$manifestLines = @(
    "TDitbam Streamer Suite v3.6.0 installer parts",
    "Keep the Setup EXE and every BIN part in the same directory.",
    ""
)
foreach ($file in $installerFiles) {
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    $manifestLines += "{0}`t{1} bytes`tSHA256 {2}" -f $file.Name, $file.Length, $hash
}
$manifestLines | Set-Content -LiteralPath (Join-Path $projectRoot "installer\PARTS.txt") -Encoding utf8

Write-Host "Release build complete."
$installerFiles | ForEach-Object { Write-Host " - $($_.FullName)" }
