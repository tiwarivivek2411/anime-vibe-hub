import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app_gui import get_anime_folders, get_images_for_anime

def test_anime_folder_detection(tmp_path):
    # Setup mock anime_images directory
    anime_dir = tmp_path / "anime_images"
    anime_dir.mkdir()
    (anime_dir / "Naruto").mkdir()
    (anime_dir / "One Piece").mkdir()
    (anime_dir / "README.txt").write_text("not a dir")

    # Override BASE_DIR in app_gui for testing
    import app_gui
    original_base = app_gui.BASE_DIR
    app_gui.BASE_DIR = anime_dir
    
    try:
        folders = get_anime_folders()
        assert "Naruto" in folders
        assert "One Piece" in folders
        assert "README.txt" not in folders
        assert len(folders) == 2
    finally:
        app_gui.BASE_DIR = original_base

def test_image_fetching_recursive(tmp_path):
    anime_dir = tmp_path / "anime_images"
    naruto_dir = anime_dir / "Naruto"
    naruto_dir.mkdir(parents=True)
    
    # Root image
    (naruto_dir / "img1.jpg").write_text("fake data")
    # Character subfolder image
    sasuke_dir = naruto_dir / "Sasuke"
    sasuke_dir.mkdir()
    (sasuke_dir / "img2.png").write_text("fake data")
    
    import app_gui
    original_base = app_gui.BASE_DIR
    app_gui.BASE_DIR = anime_dir
    
    try:
        images = get_images_for_anime("Naruto")
        assert any("img1.jpg" in str(p) for p in images)
        assert any("img2.png" in str(p) for p in images)
        assert len(images) == 2
    finally:
        app_gui.BASE_DIR = original_base
