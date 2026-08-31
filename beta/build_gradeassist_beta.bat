@echo off
setlocal
title GradeAssist Beta Builder

echo.
echo ============================================
echo   GradeAssist Beta - Windows Build
echo ============================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3 from python.org, then run this file again.
    pause
    exit /b 1
)

echo Installing/updating PyInstaller...
py -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo PyInstaller installation failed.
    pause
    exit /b 1
)

echo.
echo Building GradeAssist Beta...
py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "GradeAssist Beta" ^
  "GradeAssist_Teacher_Beta.py"

if errorlevel 1 (
    echo.
    echo Build failed. Copy the error text and send it to ChatGPT.
    pause
    exit /b 1
)

echo.
echo ============================================
echo BUILD COMPLETE
echo ============================================
echo Your app is here:
echo dist\GradeAssist Beta.exe
echo.
echo You can copy that EXE to another Windows PC.
echo.
pause
