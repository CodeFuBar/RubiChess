@echo off
echo Building Sapphire_1.1_dev_20250911_001 with Phase 1 optimizations...

:: Set up Visual Studio environment
call "D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

:: Create output directory
if not exist "Release-modified" mkdir "Release-modified"

:: Download neural network if needed
for /f "tokens=3" %%A in ('findstr "NNUEDEFAULT " RubiChess.h') do (
    if not exist %%A (
        echo Downloading neural network %%A...
        curl -skL "https://github.com/Matthies/NN/raw/main/%%A" -o %%A
    )
    if not exist "Release-modified\%%A" copy %%A "Release-modified\"
)

:: Build zlib
echo Building zlib...
cd zlib
cl /c /O2 /DNDEBUG /MD *.c
lib /OUT:zlib.lib *.obj
cd ..

:: Compile Sapphire with optimizations (neural network will be loaded externally)
echo Compiling Sapphire with Phase 1 endgame optimizations...
cl /EHsc /O2 /Oi /Ot /GL /DNDEBUG /MD /DIS_64BIT /DUSE_AVX2 /DUSE_BMI1 /DUSE_POPCNT /DUSE_SSSE3 /DUSE_SSE2 /DUSE_ZLIB ^
   /arch:AVX2 /fp:fast ^
   /Izlib ^
   /Fe:"Release-modified\Sapphire_1.1_dev_20250911_001_x86-64-avx2.exe" ^
   *.cpp ^
   zlib\zlib.lib ^
   advapi32.lib ^
   /link /LTCG /OPT:REF /OPT:ICF

if %ERRORLEVEL% == 0 (
    echo.
    echo ===================================================
    echo BUILD SUCCESSFUL!
    echo ===================================================
    echo Engine: Sapphire_1.1_dev_20250911_001_x86-64-avx2.exe
    echo Location: Release-modified\
    echo Author: Andreas Matthies (RubiChess), modified by Martin van der Hoek and CodeFuBar
    echo.
    echo Phase 1 Modifications Applied:
    echo - Enhanced rook mobility evaluation
    echo - Improved rook positioning bonuses
    echo - Better king centralization in endgames
    echo - Increased king activity scoring
    echo.
    echo Ready for testing against positions 135-142!
    echo ===================================================
) else (
    echo BUILD FAILED! Error code: %ERRORLEVEL%
)

pause
