import time
import argparse
from wallpaper_manager import update_wallpaper

def main():
    parser = argparse.ArgumentParser(description="Anime Wallpaper App")
    parser.add_argument("--interval", type=int, default=60, help="Interval in minutes to change wallpaper (default: 60)")
    parser.add_argument("--once", action="store_true", help="Change wallpaper once and exit")
    
    args = parser.parse_args()
    
    if args.once:
        update_wallpaper()
    else:
        print(f"Starting Anime Wallpaper daemon. Updating every {args.interval} minutes.")
        while True:
            update_wallpaper()
            print(f"Waiting for {args.interval} minutes...")
            time.sleep(args.interval * 60)

if __name__ == "__main__":
    main()
