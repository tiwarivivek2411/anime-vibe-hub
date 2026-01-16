import requests
import random
from typing import Optional


def get_anime_image(category: str = "sfw", type: str = "waifu", width: Optional[int] = None, height: Optional[int] = None) -> Optional[str]:
    """Fetch a random anime image URL from waifu.pics API.

    Parameters
    ----------
    category: str
        "sfw" or "nsfw" (default "sfw").
    type: str
        Type of image, e.g., "waifu", "neko", etc.
    width, height: Optional[int]
        Desired resolution. If provided, the function will attempt to request an image
        that meets or exceeds these dimensions. The waifu.pics API does not support
        explicit size parameters, so we append a query string that many image hosts
        respect (e.g., "?size=WIDTHxHEIGHT"). If the API ignores it, we simply return
        the URL.
    """
    base_url = f"https://api.waifu.pics/{category}/{type}"
    # Some APIs allow size hints via query parameters; we add them if given.
    if width and height:
        url = f"{base_url}?size={width}x{height}"
    else:
        url = base_url
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("url")
    except Exception as e:
        print(f"Error fetching image: {e}")
        return None

if __name__ == "__main__":
    # Quick test
    img_url = get_anime_image()
    if img_url:
        print(f"Fetched image URL: {img_url}")
    else:
        print("Failed to fetch image.")
