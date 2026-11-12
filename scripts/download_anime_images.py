import os
import sys
import argparse
import requests
from pathlib import Path

# Reuse the existing API client logic (simple GET to waifu.pics)
def fetch_image_url(category="sfw", type="waifu"):
    url = f"https://api.waifu.pics/{category}/{type}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("url")
    except Exception as e:
        print(f"Error fetching image URL: {e}")
        return None

def download_image(url, dest_path):
    try:
        resp = requests.get(url, stream=True, timeout=15)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download a set of anime images into a folder.")
    parser.add_argument("anime", help="Anime name (folder will be created under anime_images)")
    parser.add_argument("count", type=int, help="Number of images to download")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1] / "anime_images" / args.anime
    base_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {args.count} images for {args.anime} into {base_dir}")
    for i in range(1, args.count + 1):
        img_url = fetch_image_url()
        if not img_url:
            continue
        ext = os.path.splitext(img_url)[1] or ".jpg"
        dest_file = base_dir / f"img{i}{ext}"
        if download_image(img_url, dest_file):
            print(f"Saved {dest_file}")
        else:
            print(f"Failed to save image {i}")

if __name__ == "__main__":
    main()
