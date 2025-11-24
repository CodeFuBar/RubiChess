@echo off
REM ============================================================================
REM RubiChess Optimal Build Script
REM Automatically detects CPU features and builds the best version
REM 
REM Usage:
REM   build_optimal.bat         - Standard optimized build
REM   build_optimal.bat pgo     - Profile-Guided Optimization build (slower but faster result)
REM ============================================================================

setlocal enabledelayedexpansion

REM Check for PGO mode
set "PGO_MODE=0"
if /i "%1"=="pgo" set "PGO_MODE=1"

echo ============================================================================
if "%PGO_MODE%"=="1" (
    echo RubiChess Optimal Build Script - PGO MODE
) else (
    echo RubiChess Optimal Build Script
)
echo ============================================================================
echo.

REM Check for Visual Studio
set "VCVARS="
if exist "D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VCVARS=D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
) else if exist "%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VCVARS=%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
) else if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VCVARS=%ProgramFiles(x86)%\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat"
)

if "%VCVARS%"=="" (
    echo ERROR: Visual Studio not found!
    echo Please install Visual Studio 2019 or 2022 with C++ tools.
    exit /b 1
)

echo Found Visual Studio: %VCVARS%
echo.

REM Initialize Visual Studio environment
echo Initializing Visual Studio environment...
call "%VCVARS%" x64

REM Create output directory
if not exist "Release-optimal" mkdir Release-optimal

REM ============================================================================
REM Step 1: Build CPU detection tool
REM ============================================================================
echo.
echo Step 1: Building CPU detection tool...

cl /nologo /EHsc /O2 /DCPUTEST cputest.cpp /Fe:cputest.exe /link /NODEFAULTLIB:OLDNAMES.lib ws2_32.lib
if errorlevel 1 (
    echo ERROR: Failed to build CPU detection tool!
    exit /b 1
)

REM ============================================================================
REM Step 2: Detect CPU features
REM ============================================================================
echo.
echo Step 2: Detecting CPU features...

for /f "tokens=*" %%a in ('cputest.exe') do set CPUFEATURES=%%a
echo Detected CPU features: %CPUFEATURES%
echo.

REM ============================================================================
REM Step 3: Determine optimal build configuration
REM ============================================================================
echo Step 3: Determining optimal build configuration...

set "DEFINES=USE_SSE2"
set "ARCHNAME=sse2"
set "ARCHFLAG="

REM Check for SSSE3
echo %CPUFEATURES% | findstr /i "ssse3" >nul
if not errorlevel 1 (
    set "DEFINES=!DEFINES! USE_SSSE3"
    set "ARCHNAME=ssse3"
)

REM Check for POPCNT
echo %CPUFEATURES% | findstr /i "popcnt" >nul
if not errorlevel 1 (
    set "DEFINES=!DEFINES! USE_POPCNT"
    set "ARCHNAME=modern"
)

REM Check for BMI1
echo %CPUFEATURES% | findstr /i "bmi1" >nul
if not errorlevel 1 (
    set "DEFINES=!DEFINES! USE_BMI1"
)

REM Check for LZCNT
echo %CPUFEATURES% | findstr /i "lzcnt" >nul
if not errorlevel 1 (
    set "DEFINES=!DEFINES! USE_LZCNT"
)

REM Check for AVX2
echo %CPUFEATURES% | findstr /i "avx2" >nul
if not errorlevel 1 (
    set "DEFINES=!DEFINES! USE_AVX2"
    set "ARCHNAME=avx2"
    set "ARCHFLAG=/arch:AVX2"
)

REM Check for BMI2
echo %CPUFEATURES% | findstr /i "bmi2" >nul
if not errorlevel 1 (
    set "DEFINES=!DEFINES! USE_BMI2"
    set "ARCHNAME=bmi2"
)

REM Check for AVX512
echo %CPUFEATURES% | findstr /i "avx512" >nul
if not errorlevel 1 (
    set "DEFINES=!DEFINES! USE_AVX512"
    set "ARCHNAME=avx512"
    set "ARCHFLAG=/arch:AVX512"
)

REM Add ZLIB support
set "DEFINES=!DEFINES! USE_ZLIB"

echo.
echo Selected architecture: %ARCHNAME%
echo Preprocessor defines: %DEFINES%
echo.

REM ============================================================================
REM Step 4: Build zlib
REM ============================================================================
echo Step 4: Building zlib...

pushd zlib
del /Q *.obj 2>nul
cl /nologo /c /O2 /EHsc *.c
lib /nologo /OUT:zlib.lib *.obj
popd

if not exist "zlib\zlib.lib" (
    echo ERROR: Failed to build zlib!
    exit /b 1
)
echo zlib built successfully.
echo.

REM ============================================================================
REM Step 5: Download NNUE network if needed
REM ============================================================================
echo Step 5: Checking NNUE network...

for /f "tokens=3" %%A in ('findstr "NNUEDEFAULT " RubiChess.h') do set NNUENET=%%A
echo Required network: %NNUENET%

if not exist "%NNUENET%" (
    echo Downloading network...
    curl -skL "https://github.com/Matthies/NN/raw/main/%NNUENET%" -o "%NNUENET%"
)

if exist "%NNUENET%" (
    echo Network file ready.
) else (
    echo WARNING: Could not download network file!
)
echo.

REM ============================================================================
REM Step 6: Compile and Link RubiChess
REM ============================================================================

REM Clean old object files and PGO data
del /Q *.obj 2>nul
del /Q *.pgc 2>nul
del /Q *.pgd 2>nul

REM Build base compiler flags
set "CXXFLAGS=/nologo /EHsc /O2 /Oi /Ot /GL /MT /favor:INTEL64 /D_CONSOLE /DNDEBUG"

REM Add architecture flag
if not "%ARCHFLAG%"=="" set "CXXFLAGS=%CXXFLAGS% %ARCHFLAG%"

REM Add all preprocessor defines
for %%d in (%DEFINES%) do (
    set "CXXFLAGS=!CXXFLAGS! /D%%d"
)

set "SOURCEFILES=board.cpp engine.cpp eval.cpp main.cpp move.cpp nnue.cpp search.cpp tbprobe.cpp transposition.cpp utils.cpp book.cpp learn.cpp texel.cpp cputest.cpp"
set "OBJFILES=board.obj engine.obj eval.obj main.obj move.obj nnue.obj search.obj tbprobe.obj transposition.obj utils.obj book.obj learn.obj texel.obj cputest.obj"
set "LIBS=zlib\zlib.lib ws2_32.lib advapi32.lib"

if not "%PGO_MODE%"=="1" goto standard_build

REM ========================================================================
REM PGO BUILD - Three-phase process
REM ========================================================================
echo.
echo Step 6: PGO Build Phase 1 - Instrumented compilation...
echo.

set "PGDFILE=RubiChess_pgo.pgd"
set "EXENAME_INSTR=RubiChess_pgo_instr.exe"

REM Clean any previous PGO data
del /Q *.pgc 2>nul
del /Q *.pgd 2>nul
del /Q %EXENAME_INSTR% 2>nul

REM Phase 1: Build instrumented version
echo Compiling with instrumentation...
cl %CXXFLAGS% /c %SOURCEFILES%
if errorlevel 1 goto compile_error

echo Linking instrumented executable...
link /nologo /LTCG:PGINSTRUMENT /PGD:%PGDFILE% /NODEFAULTLIB:OLDNAMES.lib /OUT:%EXENAME_INSTR% %OBJFILES% %LIBS%
if errorlevel 1 goto link_error

echo.
echo ========================================================================
echo Step 7: PGO Build Phase 2 - Profiling run
echo ========================================================================
echo.
echo Running profiling workload to collect profile data...
echo This may take 2-5 minutes...
echo.

REM Use Python script for proper engine communication
python pgo_profile.py %EXENAME_INSTR%

REM Wait for file handles to be released
echo.
echo Waiting for profile data to be written...
timeout /t 3 /nobreak >nul 2>&1

REM Force close any remaining handles (suppress all output)
taskkill /F /IM %EXENAME_INSTR% >nul 2>&1
del /Q pgo_in.txt 2>nul
del /Q pgo_output.txt 2>nul

REM Check if profile data was generated
dir /b *.pgc >nul 2>&1
if errorlevel 1 goto no_profile_data

echo Profile data collected successfully.
echo.

echo ========================================================================
echo Step 8: PGO Build Phase 3 - Optimized compilation
echo ========================================================================
echo.

REM Clean object files for rebuild
del /Q *.obj 2>nul

echo Recompiling with profile optimization...
cl %CXXFLAGS% /c %SOURCEFILES%
if errorlevel 1 goto compile_error

echo Linking with profile optimization...
set "EXENAME=RubiChess_%ARCHNAME%_pgo.exe"
link /nologo /LTCG:PGOPTIMIZE /PGD:%PGDFILE% /NODEFAULTLIB:OLDNAMES.lib /OUT:Release-optimal\%EXENAME% %OBJFILES% %LIBS%
if errorlevel 1 goto link_error

REM Cleanup PGO artifacts
del /Q %EXENAME_INSTR% 2>nul
del /Q *.pgc 2>nul
del /Q *.pgd 2>nul
del /Q pgo_output.txt 2>nul

goto build_done

:no_profile_data
echo WARNING: No profile data generated. Falling back to standard build.

:standard_build
REM ========================================================================
REM STANDARD BUILD - Single-phase process
REM ========================================================================
echo Step 6: Compiling RubiChess (optimized for %ARCHNAME%)...
echo.
echo Compiler flags: %CXXFLAGS%
echo.

echo Compiling source files...
cl %CXXFLAGS% /c %SOURCEFILES%
if errorlevel 1 goto compile_error

echo.
echo Step 7: Linking...

set "EXENAME=RubiChess_%ARCHNAME%.exe"
link /nologo /LTCG /OPT:REF /OPT:ICF /NODEFAULTLIB:OLDNAMES.lib /OUT:Release-optimal\%EXENAME% %OBJFILES% %LIBS%
if errorlevel 1 goto link_error

:build_done

REM Copy network file
copy /Y "%NNUENET%" "Release-optimal\%NNUENET%" >nul 2>&1

REM ============================================================================
REM Cleanup
REM ============================================================================
echo.
echo Cleaning up...
del /Q *.obj 2>nul
del /Q cputest.exe 2>nul
pushd zlib
del /Q *.obj 2>nul
popd

REM ============================================================================
REM Done!
REM ============================================================================
echo.
echo ============================================================================
echo BUILD SUCCESSFUL!
echo ============================================================================
echo.
echo Output: Release-optimal\%EXENAME%
echo Architecture: %ARCHNAME%
echo CPU Features: %CPUFEATURES%
if "%PGO_MODE%"=="1" (
    echo Build Type: Profile-Guided Optimization (PGO)
    echo.
    echo PGO builds are typically 5-15%% faster than standard builds.
) else (
    echo Build Type: Standard optimized
    echo.
    echo For even better performance, try: build_optimal.bat pgo
)
echo.
echo To test, run:
echo   Release-optimal\%EXENAME%
echo.
goto end

:compile_error
echo ERROR: Compilation failed!
exit /b 1

:link_error
echo ERROR: Linking failed!
exit /b 1

:end
endlocal
