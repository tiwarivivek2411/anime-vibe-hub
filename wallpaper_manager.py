import os
import requests
from api_client import get_anime_image
from set_wallpaper import set_macos_wallpaper

CACHE_DIR = os.path.expanduser("~/Pictures/AnimeWallpapers")

def download_image(url):
    """
    Downloads the image from the URL and saves it to the cache directory.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    
    filename = url.split("/")[-1]
    save_path = os.path.join(CACHE_DIR, filename)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return save_path
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def update_wallpaper():
    """
    Fetches a new image URL, downloads it, and sets it as the macOS wallpaper.
    """
    print("Fetching new anime image...")
    img_url = get_anime_image()
    if not img_url:
        print("Failed to get image URL.")
        return False
    
    print(f"Downloading image from: {img_url}")
    save_path = download_image(img_url)
    if not save_path:
        print("Failed to download image.")
        return False
    
    print("Setting wallpaper...")
    return set_macos_wallpaper(save_path)

if __name__ == "__main__":
    update_wallpaper()
