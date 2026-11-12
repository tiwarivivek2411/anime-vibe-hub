import subprocess
import os
import platform
import ctypes
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont

def extend_and_stylize(image_path, target_res=(2880, 1864)):
    """
    Artistically extends an image to fit target resolution by:
    1. Creating a blurred background from the original.
    2. Placing the original in the center.
    3. Adding vertical 'VIBEHUB PRO' or image name typography on the sides.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        tw, th = target_res
        iw, ih = img.size
        
        # 1. Background: Smooth blurred base
        bg = ImageOps.fit(img, target_res, centering=(0.5, 0.5))
        bg = bg.filter(ImageFilter.GaussianBlur(radius=80))
        
        # 2. Add subtle dark overlay to the background for depth
        overlay = Image.new('RGBA', target_res, (0, 0, 0, 100))
        bg.paste(overlay, (0,0), overlay)

        # 3. Main Image: Fit to height with slight padding
        scale = (th * 0.95) / ih
        nw, nh = int(iw * scale), int(ih * scale)
        fg = img.resize((nw, nh), Image.Resampling.LANCZOS)
        
        # 4. Paste main image in center
        result = bg.copy()
        offset = ((tw - nw) // 2, (th - nh) // 2)
        result.paste(fg, offset)
        
        # 5. Add Stylized Side Typography if there's enough room
        if tw - nw > 300:
            draw = ImageDraw.Draw(result)
            side_text = os.path.basename(image_path).replace("_", " ").split(".")[0].upper()
            
            # Use a default font or try to find a nice one
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
            except:
                font = ImageFont.load_default()
            
            # Left vertical text
            txt_surface = Image.new('RGBA', (600, 100), (0,0,0,0))
            txt_draw = ImageDraw.Draw(txt_surface)
            txt_draw.text((0, 0), "VIBEHUB // DESKTOP", font=font, fill=(255, 255, 255, 120))
            left_txt = txt_surface.rotate(90, expand=True)
            result.paste(left_txt, (50, th//2 - 300), left_txt)
            
            # Right vertical text (Image name)
            txt_surface_r = Image.new('RGBA', (600, 100), (0,0,0,0))
            txt_draw_r = ImageDraw.Draw(txt_surface_r)
            txt_draw_r.text((0, 0), side_text[:20], font=font, fill=(255, 255, 255, 100))
            right_txt = txt_surface_r.rotate(270, expand=True)
            result.paste(right_txt, (tw - 120, th//2 - 300), right_txt)

        temp_path = os.path.expanduser("~/.vibehub_extended_vibe.jpg")
        result.save(temp_path, "JPEG", quality=95)
        return temp_path
    except Exception as e:
        print(f"Enhancement error: {e}")
        return image_path

def set_wallpaper(image_path):
    """
    Sets the wallpaper after extending it artistically.
    """
    system = platform.system()
    
    # Target resolution detection
    target_res = (2880, 1864) # Default
    if system == "Darwin":
        try:
            res_output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"]).decode()
            if "Resolution:" in res_output:
                line = [l for l in res_output.split("\n") if "Resolution:" in l][0]
                parts = line.split(":")[1].split()
                target_res = (int(parts[0]), int(parts[2]))
        except: pass
        
        abs_path = extend_and_stylize(os.path.abspath(image_path), target_res)
        return _set_macos_wallpaper(abs_path)
    
    # Fallback for non-macOS (simple set for now)
    abs_path = os.path.abspath(image_path)
    if system == "Windows":
        return _set_windows_wallpaper(abs_path)
    elif system == "Linux":
        return _set_linux_wallpaper(abs_path)
    return False

def _set_macos_wallpaper(abs_path):
    # Use robust Finder script. Universal compatibility.
    # High-res native images (2880x1800) will fit perfectly by default.
    script = f'tell application "Finder" to set desktop picture to POSIX file "{abs_path}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"macOS error: {e}")
        return False

def _set_windows_wallpaper(abs_path):
    try:
        result = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        return result != 0
    except Exception as e:
        print(f"Windows error: {e}")
        return False

def _set_linux_wallpaper(abs_path):
    desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    try:
        if "gnome" in desktop_env or "unity" in desktop_env:
            args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{abs_path}"]
            subprocess.run(args, check=True)
            return True
        else:
            subprocess.run(["feh", "--bg-fill", abs_path], check=True)
            return True
    except Exception as e:
        print(f"Linux error: {e}")
        return False

if __name__ == "__main__":
    print(f"Detected OS: {platform.system()}")
