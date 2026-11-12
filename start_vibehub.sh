#!/bin/bash

# Setup and Run script for Anime-Vibe

echo "--- Initializing VibeHub Pro v3.0 ---"

# Determine python command
PYTHON_BIN="/opt/homebrew/bin/python3.13"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "Using $PYTHON_BIN"

# Set up Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_BIN -m venv venv
fi

source venv/bin/activate
PYTHON="python"

# Install dependencies
echo "[1/3] Installing dependencies..."
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r requirements.txt
$PYTHON -m pip install customtkinter pillow flask

# Bootstrap library
if [ ! -d "anime_images" ]; then
    echo "[2/3] Bootstrapping image library (this may take a minute)..."
    $PYTHON scripts/bootstrap_library.py
else
    echo "[2/3] Library folder already exists."
fi

# Startup Flask Server in background
echo "[3/4] Launching VibeServer..."
mkdir -p remote_assets
$PYTHON vibe_server.py &
SERVER_PID=$!

# Run App
echo "[4/4] Launching App..."
$PYTHON app_gui.py

# Cleanup
kill $SERVER_PID
