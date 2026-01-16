import requests
import random

def get_anime_image(category="sfw", type="waifu"):
    """
    Fetches a random anime image URL from waifu.pics API.
    Categories: sfw, nsfw (defaulting to sfw for safety)
    Types: waifu, neko, shinobu, megumin, bully, cuddle, cry, hug, awoo, kiss, lick, pat, smug, bonk, yeet, blush, smile, wave, highfive, handhold, nom, bite, slap, kill, kick, happy, wink, poke, dance, cringe
    """
    url = f"https://api.waifu.pics/{category}/{type}"
    try:
        response = requests.get(url)
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
