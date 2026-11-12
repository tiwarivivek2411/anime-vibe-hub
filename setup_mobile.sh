#!/bin/bash
echo "--- VibeHub Mobile Setup (Android APK) ---"

# This script prepares the environment for Android development using Buildozer.
# Note: Developing APKs usually requires Linux or macOS with Android SDK/NDK.

echo "1. Installing Kivy for local preview..."
python3 -m pip install kivy

echo "2. Installing Buildozer (The APK Packager)..."
python3 -m pip install buildozer

echo "--- HOW TO BUILD YOUR APK ---"
echo "To convert 'mobile_vibe.py' into an Android App:"
echo "1. Ensure you have Docker or a Linux environment (Ubuntu recommended)."
echo "2. Run: 'buildozer -v android debug'"
echo "3. The .apk file will be in the 'bin/' directory."
echo ""
echo "Note: The first build will take 15-20 minutes as it downloads the Android SDK."
echo ""
echo "To test locally on Mac:"
echo "Run: 'python3 mobile_vibe.py'"
