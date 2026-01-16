import os
import platform
import requests
from typing import List, Optional

from api_client import get_anime_image
from set_wallpaper import set_macos_wallpaper

CACHE_DIR = os.path.expanduser("~/Pictures/AnimeWallpapers")


def ensure_cache_dir() -> None:
    """Create the cache directory if it does not exist."""
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)


def detect_os() -> str:
    """Return a string identifier for the current operating system."""
    return platform.system().lower()


def get_screen_resolution() -> tuple:
    """Return the screen width and height in pixels.
    Currently implemented for macOS using pyobjc; falls back to (1920, 1080)."""
    try:
        if detect_os() == "darwin":
            from AppKit import NSScreen
            screen = NSScreen.mainScreen()
            frame = screen.frame()
            width = int(frame.size.width)
            height = int(frame.size.height)
            return width, height
    except Exception:
        pass
    # Default fallback resolution
    return 1920, 1080


def download_image(url: str) -> Optional[str]:
    """Download an image to the cache directory and return the local path."""
    ensure_cache_dir()
    filename = url.split('/')[-1]
    save_path = os.path.join(CACHE_DIR, filename)
    try:
        resp = requests.get(url, stream=True, timeout=15)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return save_path
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


def choose_image(options: List[str]) -> str:
    """Present three image URLs to the user and let them pick one."""
    print("Please choose one of the following wallpapers:")
    for idx, opt in enumerate(options, start=1):
        print(f"[{idx}] {opt}")
    while True:
        choice = input("Enter the number of your choice (1-3): ").strip()
        if choice in {"1", "2", "3"}:
            return options[int(choice) - 1]
        print("Invalid choice, please enter 1, 2, or 3.")


def update_wallpaper() -> bool:
    """Main workflow: detect OS, fetch three images matching resolution, let user pick, download and set wallpaper."""
    current_os = detect_os()
    if current_os != "darwin":
        print(f"Unsupported OS for this script: {current_os}. Only macOS is supported at the moment.")
        return False

    width, height = get_screen_resolution()
    print(f"Detected screen resolution: {width}x{height}")

    # Fetch three candidate images (the API client can accept width/height parameters)
    candidates = []
    for _ in range(3):
        img_url = get_anime_image(width=width, height=height)
        if img_url:
            candidates.append(img_url)
    if not candidates:
        print("Failed to retrieve any image URLs.")
        return False

    selected_url = choose_image(candidates)
    print(f"Downloading selected image: {selected_url}")
    local_path = download_image(selected_url)
    if not local_path:
        return False
    print("Setting wallpaper...")
    return set_macos_wallpaper(local_path)


if __name__ == "__main__":
    update_wallpaper()
