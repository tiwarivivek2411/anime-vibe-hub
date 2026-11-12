#!/bin/bash

# Setup and Run script for Anime-Vibe

echo "--- Initializing Anime-Vibe Desktop ---"

# Check for python
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install it."
    exit
fi

# Install dependencies
echo "[1/3] Installing dependencies..."
python3 -m pip install -r requirements.txt
python3 -m pip install customtkinter pillow

# Bootstrap library
if [ ! -d "anime_images" ]; then
    echo "[2/3] Bootstrapping image library (this may take a minute)..."
    python3 scripts/bootstrap_library.py
else
    echo "[2/3] Library folder already exists."
fi

# Run App
echo "[3/3] Launching App..."
python3 app_gui.py
