import subprocess
import os

def set_macos_wallpaper(image_path):
    """
    Sets the macOS wallpaper to the image at the given path using AppleScript.
    """
    abs_path = os.path.abspath(image_path)
    script = f'tell application "Finder" to set desktop picture to POSIX file "{abs_path}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        print(f"Wallpaper set to: {abs_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting wallpaper: {e}")
        return False

if __name__ == "__main__":
    # Test with a dummy path or a real image if you have one
    # Note: This will fail if the file doesn't exist.
    pass
