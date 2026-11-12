#!/bin/bash

# Build script for Anime-Vibe macOS App

echo "--- Building Anime-Vibe macOS App ---"

# 1. Install/Update requirements
python3 -m pip install customtkinter pillow pyinstaller requests pyobjc

# 2. Run PyInstaller
# --windowed: No console window
# --onefile: Single executable (though for macOS .app is better)
# --noconfirm: overwrite existing
# --name: App Name
# --add-data: Include scripts if needed (but we'll keep images external so user can add more)

python3 -m PyInstaller --noconfirm --windowed --name "VibeHub" \
            --clean \
            app_gui.py

echo "--- VibeHub Build Complete ---"
echo "The app is in dist/VibeHub.app"
echo "Note: Library is at 'media_library/' in the root."
