<#
.SYNOPSIS
    RubiChess Optimal Build Script
    Automatically detects CPU features and builds the best version

.DESCRIPTION
    This script:
    1. Detects your CPU features (AVX-512, AVX2, BMI2, etc.)
    2. Determines the optimal build configuration
    3. Compiles RubiChess with maximum optimizations for your CPU

.EXAMPLE
    .\Build-Optimal.ps1
    
.EXAMPLE
    .\Build-Optimal.ps1 -Verbose
#>

[CmdletBinding()]
param(
    [switch]$SkipNetworkDownload,
    [switch]$CleanBuild
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "RubiChess Optimal Build Script" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

#region Find Visual Studio
Write-Host "Step 1: Finding Visual Studio..." -ForegroundColor Yellow

$VSPaths = @(
    "D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat",
    "$env:ProgramFiles\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat",
    "$env:ProgramFiles\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat",
    "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat"
)

$VCVars = $null
foreach ($path in $VSPaths) {
    if (Test-Path $path) {
        $VCVars = $path
        break
    }
}

if (-not $VCVars) {
    Write-Host "ERROR: Visual Studio not found!" -ForegroundColor Red
    Write-Host "Please install Visual Studio 2019 or 2022 with C++ tools." -ForegroundColor Red
    exit 1
}

Write-Host "  Found: $VCVars" -ForegroundColor Green
Write-Host ""
#endregion

#region Initialize VS Environment
Write-Host "Step 2: Initializing Visual Studio environment..." -ForegroundColor Yellow

# Run vcvarsall and capture environment
$envCmd = "`"$VCVars`" x64 && set"
$envOutput = cmd /c $envCmd 2>&1

foreach ($line in $envOutput) {
    if ($line -match "^([^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

Write-Host "  Environment initialized." -ForegroundColor Green
Write-Host ""
#endregion

#region Create output directory
$OutputDir = Join-Path $ScriptDir "Release-optimal"
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

if ($CleanBuild) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item "$OutputDir\*" -Force -ErrorAction SilentlyContinue
    Remove-Item "*.obj" -Force -ErrorAction SilentlyContinue
}
#endregion

#region Build CPU detection tool
Write-Host "Step 3: Building CPU detection tool..." -ForegroundColor Yellow

# Use a simpler CPU detection approach that doesn't require full compilation
$CpuTestCode = @"
#include <iostream>
#include <intrin.h>
int main() {
    int cpuInfo[4];
    __cpuid(cpuInfo, 0);
    __cpuid(cpuInfo, 1);
    bool sse2 = (cpuInfo[3] & (1 << 26)) != 0;
    bool ssse3 = (cpuInfo[2] & (1 << 9)) != 0;
    bool popcnt = (cpuInfo[2] & (1 << 23)) != 0;
    __cpuid(cpuInfo, 7);
    bool avx2 = (cpuInfo[1] & (1 << 5)) != 0;
    bool bmi1 = (cpuInfo[1] & (1 << 3)) != 0;
    bool bmi2 = (cpuInfo[1] & (1 << 8)) != 0;
    bool avx512 = (cpuInfo[1] & (1 << 16)) != 0 && (cpuInfo[1] & (1 << 30)) != 0;
    __cpuid(cpuInfo, 0x80000001);
    bool lzcnt = (cpuInfo[2] & (1 << 5)) != 0;
    if (sse2) std::cout << "sse2 ";
    if (ssse3) std::cout << "ssse3 ";
    if (popcnt) std::cout << "popcnt ";
    if (lzcnt) std::cout << "lzcnt ";
    if (bmi1) std::cout << "bmi1 ";
    if (avx2) std::cout << "avx2 ";
    if (bmi2) std::cout << "bmi2 ";
    if (avx512) std::cout << "avx512 ";
    return 0;
}
"@

$CpuTestCode | Out-File -FilePath "cputest_simple.cpp" -Encoding ASCII

$clOutput = & cl /nologo /EHsc /O2 cputest_simple.cpp /Fe:cputest.exe /link /NODEFAULTLIB:OLDNAMES.lib 2>&1
if ($LASTEXITCODE -ne 0) {
    # Try alternative approach
    $clOutput = & cl /nologo /EHsc /O2 /MT cputest_simple.cpp /Fe:cputest.exe 2>&1
}

if (-not (Test-Path "cputest.exe")) {
    Write-Host "WARNING: Could not build CPU detection tool, using default detection..." -ForegroundColor Yellow
    # Fallback: detect using PowerShell/WMI
    $CpuName = (Get-WmiObject Win32_Processor).Name
    Write-Host "  CPU: $CpuName" -ForegroundColor Cyan
    
    # Assume modern Intel/AMD has at least AVX2
    if ($CpuName -match "i[3579]-[0-9]{4,5}" -or $CpuName -match "Ryzen") {
        $CpuFeatures = "sse2 ssse3 popcnt lzcnt bmi1 avx2 bmi2"
        if ($CpuName -match "i[79]-1[0-9]{4}" -or $CpuName -match "i[79]-[0-9]{5}") {
            $CpuFeatures += " avx512"
        }
    } else {
        $CpuFeatures = "sse2 ssse3 popcnt"
    }
} else {
    Write-Host "  CPU detection tool built." -ForegroundColor Green
}

Remove-Item "cputest_simple.cpp" -Force -ErrorAction SilentlyContinue
Write-Host ""
#endregion

#region Detect CPU features
Write-Host "Step 4: Detecting CPU features..." -ForegroundColor Yellow

if (Test-Path "cputest.exe") {
    $CpuFeatures = & .\cputest.exe
}

if (-not $CpuFeatures) {
    # Fallback detection
    $CpuName = (Get-WmiObject Win32_Processor).Name
    Write-Host "  CPU: $CpuName" -ForegroundColor Cyan
    
    if ($CpuName -match "i[3579]-1[0-9]{4}") {
        # 10th/11th/12th gen Intel - has AVX512
        $CpuFeatures = "sse2 ssse3 popcnt lzcnt bmi1 avx2 bmi2 avx512"
    } elseif ($CpuName -match "i[3579]-[0-9]{4,5}" -or $CpuName -match "Ryzen") {
        $CpuFeatures = "sse2 ssse3 popcnt lzcnt bmi1 avx2 bmi2"
    } else {
        $CpuFeatures = "sse2 ssse3 popcnt"
    }
}

Write-Host "  Detected: $CpuFeatures" -ForegroundColor Cyan
Write-Host ""

# Parse features into array
$Features = $CpuFeatures.ToLower().Split(" ", [StringSplitOptions]::RemoveEmptyEntries)
#endregion

#region Determine optimal configuration
Write-Host "Step 5: Determining optimal build configuration..." -ForegroundColor Yellow

$Defines = @("USE_SSE2", "USE_ZLIB")
$ArchName = "sse2"
$ArchFlag = ""

if ($Features -contains "ssse3") {
    $Defines += "USE_SSSE3"
    $ArchName = "ssse3"
}

if ($Features -contains "popcnt") {
    $Defines += "USE_POPCNT"
    $ArchName = "modern"
}

if ($Features -contains "bmi1") {
    $Defines += "USE_BMI1"
}

if ($Features -contains "lzcnt") {
    $Defines += "USE_LZCNT"
}

if ($Features -contains "avx2") {
    $Defines += "USE_AVX2"
    $ArchName = "avx2"
    $ArchFlag = "/arch:AVX2"
}

if ($Features -contains "bmi2") {
    $Defines += "USE_BMI2"
    $ArchName = "bmi2"
}

if ($Features -contains "avx512") {
    $Defines += "USE_AVX512"
    $ArchName = "avx512"
    $ArchFlag = "/arch:AVX512"
}

Write-Host "  Architecture: $ArchName" -ForegroundColor Cyan
Write-Host "  Defines: $($Defines -join ', ')" -ForegroundColor Cyan
Write-Host ""
#endregion

#region Build zlib
Write-Host "Step 6: Building zlib..." -ForegroundColor Yellow

Push-Location "zlib"
$zlibOutput = & cl /nologo /c /O2 /EHsc *.c 2>&1
if ($LASTEXITCODE -eq 0) {
    $libOutput = & lib /nologo /OUT:zlib.lib *.obj 2>&1
}
Pop-Location

if (-not (Test-Path "zlib\zlib.lib")) {
    Write-Host "ERROR: Failed to build zlib!" -ForegroundColor Red
    exit 1
}

Write-Host "  zlib built successfully." -ForegroundColor Green
Write-Host ""
#endregion

#region Download NNUE network
Write-Host "Step 7: Checking NNUE network..." -ForegroundColor Yellow

$NnueNet = (Select-String -Path "RubiChess.h" -Pattern "NNUEDEFAULT\s+(\S+)" | 
            ForEach-Object { $_.Matches.Groups[1].Value })

Write-Host "  Required network: $NnueNet" -ForegroundColor Cyan

if (-not $SkipNetworkDownload -and -not (Test-Path $NnueNet)) {
    Write-Host "  Downloading network..." -ForegroundColor Yellow
    try {
        $url = "https://github.com/Matthies/NN/raw/main/$NnueNet"
        Invoke-WebRequest -Uri $url -OutFile $NnueNet -UseBasicParsing
        Write-Host "  Network downloaded." -ForegroundColor Green
    }
    catch {
        Write-Host "  WARNING: Could not download network!" -ForegroundColor Yellow
    }
}
elseif (Test-Path $NnueNet) {
    Write-Host "  Network file exists." -ForegroundColor Green
}
Write-Host ""
#endregion

#region Compile RubiChess
Write-Host "Step 8: Compiling RubiChess (optimized for $ArchName)..." -ForegroundColor Yellow

# Clean up any leftover object files first
Remove-Item "*.obj" -Force -ErrorAction SilentlyContinue

$SourceFiles = @(
    "board.cpp", "engine.cpp", "eval.cpp", "main.cpp", "move.cpp",
    "nnue.cpp", "search.cpp", "tbprobe.cpp", "transposition.cpp",
    "utils.cpp", "book.cpp", "learn.cpp", "texel.cpp", "cputest.cpp"
)

$CompilerFlags = @(
    "/nologo", "/EHsc", "/O2", "/Oi", "/Ot", "/GL", "/MT",
    "/favor:INTEL64", "/D_CONSOLE", "/DNDEBUG", "/c"
)

# Note: _M_X64 is automatically defined by MSVC when targeting x64

if ($ArchFlag) {
    $CompilerFlags += $ArchFlag
}

foreach ($def in $Defines) {
    $CompilerFlags += "/D$def"
}

Write-Host "  Compiler flags: $($CompilerFlags -join ' ')" -ForegroundColor Gray

$compileOutput = & cl @CompilerFlags @SourceFiles 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Compilation failed!" -ForegroundColor Red
    Write-Host $compileOutput
    exit 1
}

Write-Host "  Compilation successful." -ForegroundColor Green
Write-Host ""
#endregion

#region Link
Write-Host "Step 9: Linking..." -ForegroundColor Yellow

$ExeName = "RubiChess_$ArchName.exe"
$ExePath = Join-Path $OutputDir $ExeName

# Get list of object files (excluding cputest)
$ObjFiles = Get-ChildItem "*.obj" | Where-Object { $_.Name -ne "cputest.obj" -and $_.Name -ne "cputest_simple.obj" } | ForEach-Object { $_.Name }

$LinkFlags = @(
    "/nologo", "/LTCG", "/OPT:REF", "/OPT:ICF",
    "/NODEFAULTLIB:OLDNAMES.lib",
    "/OUT:$ExePath"
) + $ObjFiles + @("zlib\zlib.lib", "ws2_32.lib", "advapi32.lib")

$linkOutput = & link @LinkFlags 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Linking failed!" -ForegroundColor Red
    Write-Host $linkOutput
    exit 1
}

# Copy network file
if (Test-Path $NnueNet) {
    Copy-Item $NnueNet -Destination $OutputDir -Force
}

Write-Host "  Linking successful." -ForegroundColor Green
Write-Host ""
#endregion

#region Cleanup
Write-Host "Step 10: Cleaning up..." -ForegroundColor Yellow

Remove-Item "*.obj" -Force -ErrorAction SilentlyContinue
Remove-Item "cputest.exe" -Force -ErrorAction SilentlyContinue
Remove-Item "cputest.obj" -Force -ErrorAction SilentlyContinue
Push-Location "zlib"
Remove-Item "*.obj" -Force -ErrorAction SilentlyContinue
Pop-Location

Write-Host "  Cleanup complete." -ForegroundColor Green
Write-Host ""
#endregion

#region Summary
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output:       $ExePath" -ForegroundColor White
Write-Host "Architecture: $ArchName" -ForegroundColor White
Write-Host "CPU Features: $CpuFeatures" -ForegroundColor White
Write-Host ""
Write-Host "To test, run:" -ForegroundColor Yellow
Write-Host "  $ExePath" -ForegroundColor Cyan
Write-Host ""

# Get file size
$FileSize = (Get-Item $ExePath).Length / 1MB
Write-Host "Binary size: $([math]::Round($FileSize, 2)) MB" -ForegroundColor Gray
#endregion
