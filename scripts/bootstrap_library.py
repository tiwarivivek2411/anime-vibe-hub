import os
import requests
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parents[1] / "anime_images"

# Mapping waifu.pics tags to (Anime Name, Character Name)
# Key: API tag, Value: (Folder, Subfolder)
COLLECTIONS = {
    "shinobu": ("Demon Slayer", "Shinobu Kocho"),
    "megumin": ("Konosuba", "Megumin"),
    "bulma": ("Dragon Ball", "Bulma"),
    "zero_two": ("Darling in the Franxx", "Zero Two"),
    "waifu": ("General", "Waifu Collection"),
    "neko": ("General", "Neko Collection"),
}

# Special handling for popular animes using generic high-res tags
EXTRA_ANIMES = {
    "Naruto": "waifu",
    "Jujutsu Kaisen": "waifu",
    "Bleach": "waifu",
    "One Piece": "waifu"
}

def download_image(tag, anime_folder, char_subfolder, count=10):
    target_dir = BASE_DIR / anime_folder / char_subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"--- Downloading {count} images for {anime_folder} > {char_subfolder} (Tag: {tag}) ---")
    
    for i in range(1, count + 1):
        url = f"https://api.waifu.pics/sfw/{tag}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            img_url = resp.json().get("url")
            
            ext = os.path.splitext(img_url)[1] or ".jpg"
            dest = target_dir / f"image_{i}{ext}"
            
            if dest.exists():
                continue
                
            img_data = requests.get(img_url, timeout=15).content
            with open(dest, "wb") as f:
                f.write(img_data)
            print(f"  [+] Saved {dest.name}")
            time.sleep(0.3)
        except Exception as e:
            print(f"  [!] Failed image {i}: {e}")

if __name__ == "__main__":
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Download specific tagged characters
    for tag, (anime, char) in COLLECTIONS.items():
        download_image(tag, anime, char, count=8)
        
    # 2. Download for major series (using generic tag)
    for anime, tag in EXTRA_ANIMES.items():
        download_image(tag, anime, "General Collection", count=12)
        
    print("\n--- Library Bootstrap Complete ---")
