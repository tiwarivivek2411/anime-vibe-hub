import os
from PIL import Image
from pathlib import Path
import platform

def get_screen_resolution():
    """Get the current screen resolution."""
    system = platform.system()
    if system == "Darwin":
        try:
            import objc
            from AppKit import NSScreen
            main_screen = NSScreen.mainScreen()
            frame = main_screen.frame()
            # frame is a CGRect, we want the width and height
            return int(frame.size.width), int(frame.size.height)
        except Exception as e:
            print(f"Error getting macOS resolution: {e}")
            return 1920, 1080 # Fallback
    elif system == "Windows":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        except:
            return 1920, 1080
    return 1920, 1080

def is_suitable_for_wallpaper(image_path, min_width=1280, min_height=800, max_aspect_ratio_diff=0.5):
    """
    Check if an image is suitable for a desktop wallpaper.
    - Must be landscape (width > height).
    - Must meet minimum resolution.
    - Aspect ratio should be somewhat reasonable for a desktop.
    """
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            if w < h: # Portrait
                return False, f"Portrait orientation ({w}x{h})"
            if w < min_width or h < min_height:
                return False, f"Low resolution ({w}x{h})"
            
            # Simple aspect ratio check: wide images only
            aspect_ratio = w / h
            if aspect_ratio < 1.2: # Too close to square or portrait
                return False, f"Unsuitable aspect ratio ({aspect_ratio:.2f})"
                
            return True, "Success"
    except Exception as e:
        return False, f"Error checking image: {e}"

def scrub_library(root_dir):
    """Scan the library and remove unsuitable images."""
    root = Path(root_dir)
    removed_count = 0
    total_checked = 0
    
    # We'll use the current screen resolution as a baseline if possible
    sw, sh = get_screen_resolution()
    # MacBook screens are high density, but we'll stick to 1920x1080 as a safe logic minimum for wide
    
    print(f"[*] Starting Library Scrub (Baseline: {sw}x{sh})...")
    
    for p in root.glob("**/*"):
        if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            total_checked += 1
            suitable, reason = is_suitable_for_wallpaper(p)
            if not suitable:
                print(f"  [-] Removing {p.relative_to(root)}: {reason}")
                p.unlink()
                removed_count += 1
                
    print(f"\n[✓] Scrub Complete. Removed {removed_count} out of {total_checked} images.")
    return removed_count

if __name__ == "__main__":
    # Test script
    scrub_library("media_library")
    scrub_library("anime_images")
