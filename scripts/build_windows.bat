@echo off
echo --- Building VibeHub for Windows ---

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

:: Install dependencies
echo [1/3] Installing dependencies...
pip install customtkinter pillow PyInstaller requests

:: Build EXE
echo [2/3] Building Standalone EXE...
python -m PyInstaller --noconfirm --onefile --windowed --name "VibeHub_Win" ^
                       --icon "NONE" ^
                       --clean ^
                       app_gui.py

echo [3/3] Build Complete!
echo You can find VibeHub_Win.exe in the 'dist' folder.
echo Note: Ensure 'media_library' and 'set_wallpaper.py' are in the same environment.
pause
