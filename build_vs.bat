@echo off
call "D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
cd /d "d:\Windsurf\RubiChessAdvanced\RubiChess"
msbuild RubiChess.sln /p:Configuration=Release /p:Platform=x64
pause
