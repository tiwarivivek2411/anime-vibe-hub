import os
import requests
from pathlib import Path
import time
import random

ROOT_DIR = Path(__file__).resolve().parents[1]
LIB_DIR = ROOT_DIR / "remote_assets"
WALLHAVEN_API = "https://wallhaven.cc/api/v1/search"

# MASSIVE CATALOG EXPANSION
COLLECTIONS = {
    "Anime": {
        "Jujutsu Kaisen": ["jujutsu kaisen"],
        "Naruto": ["naruto shippuden"],
        "Demon Slayer": ["kimetsu no yaiba"],
        "Attack on Titan": ["shingeki no kyojin"],
        "One Piece": ["one piece anime"],
        "Death Note": ["death note wallpaper"],
        "My Hero Academia": ["boku no hero academia"],
        "Fullmetal Alchemist": ["fullmetal alchemist brotherhood"],
        "Hunter x Hunter": ["hunter x hunter 2011"],
        "Steins;Gate": ["steins gate"],
        "Sword Art Online": ["sword art online"],
        "Tokyo Ghoul": ["tokyo ghoul"],
        "One Punch Man": ["one punch man"],
        "Evangelion": ["neon genesis evangelion"],
        "Cyberpunk Edgerunners": ["cyberpunk edgerunners"],
        "Arcane": ["arcane league of legends"],
        "Bleach": ["bleach tybw"],
        "Dragon Ball Z": ["dragon ball super"],
        "Sailor Moon": ["sailor moon aesthetic"],
        "Vinland Saga": ["vinland saga"],
        "Berserk": ["berserk guts"],
        "Code Geass": ["code geass lelouch"]
    },
    "Shows": {
        "Game of Thrones": ["game of thrones"],
        "Stranger Things": ["stranger things"],
        "The Witcher": ["the witcher series"],
        "Breaking Bad": ["breaking bad"],
        "The Boys": ["the boys homelander"],
        "Peaky Blinders": ["peaky blinders"],
        "The Last of Us": ["the last of us hbo"],
        "Better Call Saul": ["better call saul"],
        "Dark": ["dark netflix"],
        "The Crown": ["the crown netflix"],
        "Severance": ["severance apple tv"],
        "Ted Lasso": ["ted lasso"],
        "The Bear": ["the bear tv show"],
        "Westworld": ["westworld"],
        "Black Mirror": ["black mirror netflix"]
    },
    "Movies": {
        "Marvel MCU": ["avengers endgame", "iron man"],
        "Star Wars": ["star wars", "mandalorian"],
        "The Dark Knight": ["batman joker"],
        "Lord of the Rings": ["lord of the rings"],
        "Interstellar": ["interstellar movie"],
        "Inception": ["inception movie"],
        "Dune": ["dune paul atreides"],
        "The Matrix": ["the matrix neo"],
        "Spider-Verse": ["spider-man across the spider-verse"],
        "John Wick": ["john wick"],
        "Top Gun": ["top gun maverick"],
        "Avatar": ["avatar way of water"],
        "Gladiator": ["gladiator movie"],
        "Fight Club": ["fight club tyler durden"]
    }
}

def get_high_res_urls(query, count=20):
    """Fetch direct high-res image URLs from Wallhaven."""
    params = {
        "q": query,
        "categories": "111", 
        "purity": "100",     
        "sorting": "toplist", 
        "atleast": "1920x1080"
    }
    try:
        resp = requests.get(WALLHAVEN_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [item["path"] for item in data.get("data", [])[:count]]
    except Exception as e:
        print(f"  [!] API error for '{query}': {e}")
        return []

def download_image(topic, collection, url, index):
    dest_dir = LIB_DIR / topic / collection
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    ext = os.path.splitext(url)[1] or ".jpg"
    dest_path = dest_dir / f"vibe_{index}{ext}"
    
    if dest_path.exists():
        return
    
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        
        # New: Resolution Guard Check
        from resolution_guard import is_suitable_for_wallpaper
        suitable, reason = is_suitable_for_wallpaper(dest_path)
        if not suitable:
            print(f"    [-] Rejected {collection} image: {reason}")
            dest_path.unlink()
            return

        print(f"    [+] {topic}/{collection} > {dest_path.name}")
    except Exception as e:
        print(f"    [!] Error: {e}")

if __name__ == "__main__":
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    print("--- VIBEHUB MASSIVE SEEDING INITIATED ---")
    
    all_tasks = []
    for topic, collections in COLLECTIONS.items():
        for collection, queries in collections.items():
            all_tasks.append((topic, collection, queries))
    
    # Shuffle tasks to make it look "running wild"
    random.shuffle(all_tasks)
    
    for topic, collection, queries in all_tasks:
        print(f"[*] Processing: {topic} -> {collection}")
        urls = get_high_res_urls(queries[0], count=40)
        for i, url in enumerate(urls):
            download_image(topic, collection, url, i+1)
            time.sleep(0.3)
            
    print("\n--- Universe Fully Populated ---")
