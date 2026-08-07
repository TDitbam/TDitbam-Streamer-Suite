param(
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$AppVersion = "3.6.1"
$InstallerBaseName = "TDitbam-Streamer-Suite-Setup-v$AppVersion"

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-IsAdministrator)) {
    $scriptPath = $MyInvocation.MyCommand.Path
    $elevatedArguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
    if ($SkipInstaller) {
        $elevatedArguments += " -SkipInstaller"
    }

    Write-Host "Administrator permission is required. Opening the UAC prompt..."
    try {
        $elevatedProcess = Start-Process `
            -FilePath "powershell.exe" `
            -ArgumentList $elevatedArguments `
            -WorkingDirectory $projectRoot `
            -Verb RunAs `
            -Wait `
            -PassThru
    } catch {
        throw "Unable to start the release build as Administrator: $($_.Exception.Message)"
    }

    exit $elevatedProcess.ExitCode
}

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

$installerDir = Join-Path $projectRoot "installer"
if (-not $SkipInstaller) {
    if (-not (Test-Path -LiteralPath $installerDir)) {
        New-Item -ItemType Directory -Path $installerDir | Out-Null
    } else {
        Get-ChildItem -LiteralPath $installerDir -File |
            Where-Object { $_.Name -like "$InstallerBaseName*" } |
            ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }
    }
}

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
    "TDitbam Streamer Suite v$AppVersion separated application build",
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

Write-Host "[2/2] Building the single-file installer..."
$installerScript = Join-Path $projectRoot "installer_script.iss"
$versionPattern = '^#define\s+MyAppVersion\s+"' + [Regex]::Escape($AppVersion) + '"$'
if (-not (Select-String -LiteralPath $installerScript -Pattern $versionPattern -Quiet)) {
    throw "installer_script.iss does not declare MyAppVersion $AppVersion. Keep both release versions synchronized."
}

& $iscc $installerScript
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup build failed with exit code $LASTEXITCODE"
}

$installerPath = Join-Path $installerDir "$InstallerBaseName.exe"
if (-not (Test-Path -LiteralPath $installerPath)) {
    throw "Inno Setup completed without producing the expected installer: $installerPath"
}

$installerFile = Get-Item -LiteralPath $installerPath
$installerHash = (Get-FileHash -LiteralPath $installerPath -Algorithm SHA256).Hash
$checksumPath = Join-Path $installerDir "$InstallerBaseName-SHA256.txt"
@(
    "TDitbam Streamer Suite v$AppVersion single-file installer",
    "File: $($installerFile.Name)",
    "Size: $($installerFile.Length) bytes",
    "SHA256: $installerHash"
) | Set-Content -LiteralPath $checksumPath -Encoding utf8

Write-Host "Release build complete."
@(
    $installerPath,
    $checksumPath
) | ForEach-Object {
    Write-Host " - $_"
}
