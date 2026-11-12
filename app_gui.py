import os
import sys
import threading
import time
import random
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
try:
    import pystray
    from pystray import MenuItem as item
except ImportError:
    pystray = None
from set_wallpaper import set_wallpaper

# Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Constants
ROOT_DIR = Path(__file__).resolve().parent
MEDIA_DIRS = [ROOT_DIR / "media_library", ROOT_DIR / "anime_images"]
CONFIG_FILE = ROOT_DIR / "config.json"
WALLHAVEN_API = "https://wallhaven.cc/api/v1/search"
SERVER_URL = "http://localhost:5001"
CACHE_DIR = ROOT_DIR / "vibe_cache"
CACHE_DIR.mkdir(exist_ok=True)

def find_media_paths():
    library = {}
    
    # Local Files
    for base in MEDIA_DIRS:
        if not base.exists(): continue
        if base.name == "anime_images":
            cat = "Anime"
            if cat not in library: library[cat] = {}
            for col in base.iterdir():
                if col.is_dir():
                    imgs = [{"name": p.name, "local_path": str(p), "is_remote": False} 
                            for p in col.glob("**/*") if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')]
                    if imgs: library[cat][col.name] = imgs
        elif base.name == "media_library":
            for cat_folder in base.iterdir():
                if cat_folder.is_dir():
                    cat_name = cat_folder.name
                    if cat_name not in library: library[cat_name] = {}
                    for col in cat_folder.iterdir():
                        if col.is_dir():
                            imgs = [{"name": p.name, "local_path": str(p), "is_remote": False} 
                                    for p in col.glob("**/*") if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')]
                            if imgs: library[cat_name][col.name] = imgs
                            
    # Remote Server
    try:
        resp = requests.get(f"{SERVER_URL}/manifest", timeout=2)
        if resp.status_code == 200:
            remote_manifest = resp.json()
            for cat, collections in remote_manifest.items():
                if cat not in library: library[cat] = {}
                for col, assets in collections.items():
                    if col not in library[cat]: library[cat][col] = []
                    for asset in assets:
                        # Don't add if already exists locally
                            library[cat][col].append({
                                "name": asset["name"],
                                "url": f"{SERVER_URL}{asset['presigned_url']}",
                                "thumb_url": f"{SERVER_URL}{asset['thumb_url']}",
                                "is_remote": True
                            })
    except:
        pass
        
    return library

class VibeHubApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VibeHub Multiverse Pro v2.0")
        self.geometry("1300x900")

        # Load Config & State
        self.config = self.load_config()
        self.favorites = self.config.get("favorites", [])
        
        # Data
        library = find_media_paths()
        if self.favorites:
            library["★ Favorites"] = {"My Vibes": self.favorites}
        self.library = library
        self.categories = sorted(list(self.library.keys()))
        self.current_cat = tk.StringVar(value=self.config.get("category", self.categories[0] if self.categories else ""))
        self.current_col = tk.StringVar(value=self.config.get("collection", ""))
        self.search_query = tk.StringVar()
        self.discover_query = tk.StringVar()
        self.pinned_collections = self.config.get("pinned_collections", [])
        self.selected_img_meta = None
        self.auto_on = tk.BooleanVar(value=self.config.get("auto_change", False))
        self.interval = tk.IntVar(value=self.config.get("interval", 1))
        self.engine_thread = None

        self.setup_ui()
        self.refresh_collections()
        
        if self.current_col.get():
            self.load_collection(self.current_col.get())
        if self.auto_on.get():
            self.toggle_engine(initial=True)
            
        # Tray Management
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        if pystray:
            threading.Thread(target=self.setup_tray, daemon=True).start()

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except: pass
        return {}

    def save_config(self):
        data = {
            "category": self.current_cat.get(),
            "collection": self.current_col.get() if hasattr(self, 'current_col') else "",
            "auto_change": self.auto_on.get(),
            "interval": self.interval.get(),
            "favorites": self.favorites,
            "pinned_collections": self.pinned_collections
        }
        with open(CONFIG_FILE, "w") as f: json.dump(data, f)

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="VIBEHUB", font=ctk.CTkFont(size=36, weight="bold", family="Inter"))
        self.logo.pack(pady=(40, 20))

        # Tab Selection (Library vs Discovery)
        self.tab_view = ctk.CTkTabview(self.sidebar, height=600)
        self.tab_view.pack(padx=15, pady=10, fill="both", expand=True)
        
        self.lib_tab = self.tab_view.add("Library")
        self.disc_tab = self.tab_view.add("Discover")

        # --- Library Tab Layout ---
        self.cat_menu = ctk.CTkOptionMenu(self.lib_tab, variable=self.current_cat, values=self.categories, command=lambda _: self.refresh_collections())
        self.cat_menu.pack(padx=10, pady=10, fill="x")
        
        self.lib_search = ctk.CTkEntry(self.lib_tab, placeholder_text="Filter locally...", textvariable=self.search_query)
        self.lib_search.pack(padx=10, pady=5, fill="x")
        self.search_query.trace_add("write", lambda *args: self.refresh_collections())

        self.col_scroll = ctk.CTkScrollableFrame(self.lib_tab, fg_color="transparent")
        self.col_scroll.pack(padx=5, pady=5, fill="both", expand=True)

        # --- Discovery Tab Layout ---
        ctk.CTkLabel(self.disc_tab, text="Search Multiverse:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.disc_entry = ctk.CTkEntry(self.disc_tab, placeholder_text="Enter Anime/Show/Movie...", textvariable=self.discover_query)
        self.disc_entry.pack(padx=10, pady=5, fill="x")
        self.disc_btn = ctk.CTkButton(self.disc_tab, text="SEARCH & SYNC", command=self.perform_discovery)
        self.disc_btn.pack(padx=10, pady=10, fill="x")
        
        self.disc_status = ctk.CTkLabel(self.disc_tab, text="Ready to scan...", font=ctk.CTkFont(size=11))
        self.disc_status.pack(pady=5)

        # Automation Footer
        self.auto_frame = ctk.CTkFrame(self.sidebar, fg_color="#111111", corner_radius=15)
        self.auto_frame.pack(padx=20, pady=20, fill="x")
        
        # VibeEngine Title with Info
        engine_header = ctk.CTkFrame(self.auto_frame, fg_color="transparent")
        engine_header.pack(fill="x", padx=10, pady=(10, 0))
        
        self.auto_switch = ctk.CTkSwitch(engine_header, text="VibeEngine", font=ctk.CTkFont(weight="bold"), 
                                         variable=self.auto_on, command=self.toggle_engine)
        self.auto_switch.pack(side="left")
        
        self.engine_info = ctk.CTkLabel(engine_header, text="?", font=ctk.CTkFont(size=12, weight="bold"), 
                                        width=20, height=20, fg_color="#333333", corner_radius=10, cursor="question_arrow")
        self.engine_info.pack(side="right")
        self.add_tooltip(self.engine_info, "VibeEngine: Automatically cycles your wallpaper.\nIt pulls from your 'Pinned' topics if any are set.")

        # Interval Slider with Info
        slider_header = ctk.CTkFrame(self.auto_frame, fg_color="transparent")
        slider_header.pack(fill="x", padx=10, pady=(15, 0))
        
        ctk.CTkLabel(slider_header, text="Cycle Interval", font=ctk.CTkFont(size=11)).pack(side="left")
        
        self.slider_info = ctk.CTkLabel(slider_header, text="?", font=ctk.CTkFont(size=12, weight="bold"), 
                                        width=20, height=20, fg_color="#333333", corner_radius=10, cursor="question_arrow")
        self.slider_info.pack(side="right")
        self.add_tooltip(self.slider_info, "Interval: Set how often (in minutes) the\nwallpaper changes. Min: 1m, Max: 120m.")

        self.interval_slider = ctk.CTkSlider(self.auto_frame, from_=1, to=120, variable=self.interval)
        self.interval_slider.pack(padx=15, pady=(5, 15))

        # --- Main Gallery ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(self.main_area, text="Multiverse Explorer", font=ctk.CTkFont(size=28, weight="bold"))
        self.header.grid(row=0, column=0, sticky="w", pady=(0, 20))

        self.gallery = ctk.CTkScrollableFrame(self.main_area, label_text="Visual Stream")
        self.gallery.grid(row=1, column=0, sticky="nsew")
        self.gallery.grid_columnconfigure((0,1,2,3), weight=1)

        # --- Bottom Action Bar ---
        self.bar = ctk.CTkFrame(self, height=90, corner_radius=0)
        self.bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.apply_btn = ctk.CTkButton(self.bar, text="EQUIP VISUAL", height=50, width=160, 
                                       font=ctk.CTkFont(size=16, weight="bold"), command=self.apply)
        self.apply_btn.pack(side="right", padx=15, pady=20)

        self.like_btn = ctk.CTkButton(self.bar, text="LIKE ♥", height=50, width=100, fg_color="#27AE60",
                                      hover_color="#219150", font=ctk.CTkFont(size=14, weight="bold"), 
                                      command=lambda: self.toggle_favorite(self.selected_img_meta) if self.selected_img_meta else None)
        self.like_btn.pack(side="right", padx=10, pady=20)
        
        self.random_btn = ctk.CTkButton(self.bar, text="EXPLORE RANDOM", height=50, width=160,
                                        fg_color="#2B5B2B", font=ctk.CTkFont(weight="bold"), command=self.quick_random)
        self.random_btn.pack(side="right", padx=10, pady=20)
        
        self.refresh_btn = ctk.CTkButton(self.bar, text="Sync Library", width=120, fg_color="#333333", command=self.reload_library)
        self.refresh_btn.pack(side="left", padx=(40, 10))

        self.scrub_btn = ctk.CTkButton(self.bar, text="Optimize Library", width=140, fg_color="#443333", command=self.run_scrub)
        self.scrub_btn.pack(side="left", padx=10)

        self.system_status = ctk.CTkLabel(self.bar, text="SYSTEM STATUS: NOMINAL", font=ctk.CTkFont(family="Courier", size=12))
        self.system_status.pack(side="left")

    def reload_library(self):
        self.library = find_media_paths()
        self.categories = sorted(list(self.library.keys()))
        self.cat_menu.configure(values=self.categories)
        self.refresh_collections()
        self.system_status.configure(text="LIBRARY SYNCED")

    def refresh_collections(self):
        for w in self.col_scroll.winfo_children(): w.destroy()
        cat = self.current_cat.get()
        query = self.search_query.get().lower()
        cols = sorted(list(self.library.get(cat, {}).keys()))
        for c in cols:
            if query and query not in c.lower(): continue
            
            frame = ctk.CTkFrame(self.col_scroll, fg_color="transparent")
            frame.pack(fill="x", pady=1)
            
            is_pinned = f"{cat}:{c}" in self.pinned_collections
            pin_color = "#1E90FF" if is_pinned else "gray"
            pin_text = "★" if is_pinned else "☆"

            pin_btn = ctk.CTkButton(frame, text=pin_text, width=30, fg_color=pin_color, 
                                    command=lambda cat=cat, col=c: self.toggle_pin(cat, col))
            pin_btn.pack(side="left", padx=5)

            btn = ctk.CTkButton(frame, text=c, anchor="w", fg_color="transparent", 
                                hover_color="#222222", corner_radius=0, 
                                command=lambda n=c: self.load_collection(n))
            btn.pack(side="left", fill="x", expand=True)
        self.save_config()

    def toggle_pin(self, cat, col):
        id = f"{cat}:{col}"
        if id in self.pinned_collections:
            self.pinned_collections.remove(id)
        else:
            if len(self.pinned_collections) >= 5:
                messagebox.showwarning("Limit Reached", "You can only pin up to 5 collections for the VibeEngine cycle.")
                return
            self.pinned_collections.append(id)
        self.refresh_collections()
        self.save_config()
        self.system_status.configure(text=f"PINNED: {len(self.pinned_collections)} TOPICS")

    def load_collection(self, name):
        self.current_col.set(name)
        self.header.configure(text=f"{self.current_cat.get()} > {name}")
        self.render_gallery()
        self.save_config()

    def render_gallery(self):
        for w in self.gallery.winfo_children(): w.destroy()
        imgs = self.library.get(self.current_cat.get(), {}).get(self.current_col.get(), [])
        self.img_refs = []
        for i, meta in enumerate(imgs):
            try:
                if meta["is_remote"]:
                    # Fetch thumbnail from server
                    resp = requests.get(meta["thumb_url"], timeout=5)
                    from io import BytesIO
                    img = Image.open(BytesIO(resp.content))
                else:
                    img = Image.open(meta["local_path"])
                
                img.thumbnail((300, 200))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 160))
                btn = ctk.CTkButton(self.gallery, text="", image=ctk_img, fg_color="#1A1A1A", 
                                    hover_color="#252525", corner_radius=10, command=lambda m=meta: self.preview(m))
                btn.grid(row=i//4, column=i%4, padx=12, pady=12)
                
                # Bindings for double-click and right-click
                btn.bind("<Double-Button-1>", lambda e, m=meta: self.open_hd_preview(m))
                btn.bind("<Button-2>" if sys.platform == "darwin" else "<Button-3>", lambda e, m=meta: self.toggle_favorite(m))
                
                self.img_refs.append(ctk_img)
            except Exception as e:
                print(f"Error rendering {meta.get('name')}: {e}")

    def toggle_favorite(self, meta):
        path = meta.get("local_path") or meta.get("url")
        if path in self.favorites:
            self.favorites.remove(path)
            self.system_status.configure(text="REMOVED FROM FAVORITES")
        else:
            self.favorites.append(path)
            self.system_status.configure(text="ADDED TO FAVORITES ★")
        self.save_config()
        if self.current_cat.get() == "★ Favorites":
            self.reload_library()

    def get_local_path(self, meta):
        if not meta["is_remote"]:
            return meta["local_path"]
        
        cache_path = CACHE_DIR / meta["name"]
        if cache_path.exists():
            return str(cache_path)
        
        self.system_status.configure(text=f"FETCHING {meta['name']} (SECURE)...")
        self.update_idletasks()
        try:
            resp = requests.get(meta["url"], timeout=30)
            if resp.status_code == 403:
                # Token might be expired, try refreshing manifest and retrying once
                self.system_status.configure(text="TOKEN EXPIRED, REFRESHING...")
                self.library = find_media_paths()
                # Find the new meta for the same image
                cat, col = self.current_cat.get(), self.current_col.get()
                new_meta = next((m for m in self.library.get(cat, {}).get(col, []) if m["name"] == meta["name"]), None)
                if new_meta:
                    resp = requests.get(new_meta["url"], timeout=30)
            
            if resp.status_code == 200:
                with open(cache_path, "wb") as f:
                    f.write(resp.content)
                return str(cache_path)
            else:
                print(f"Download failed with status: {resp.status_code}")
                return None
        except Exception as e:
            print(f"Download failed: {e}")
            return None

    def open_hd_preview(self, meta):
        path = self.get_local_path(meta)
        if not path: return
        
        top = ctk.CTkToplevel(self)
        top.title(f"HD PREVIEW - {meta['name']}")
        top.geometry("1000x700")
        top.attributes("-topmost", True)
        
        raw = Image.open(path)
        w, h = raw.size
        ratio = min(1000/w, 600/h)
        new_size = (int(w*ratio), int(h*ratio))
        
        ctk_img = ctk.CTkImage(light_image=raw, dark_image=raw, size=new_size)
        lbl = ctk.CTkLabel(top, text="", image=ctk_img)
        lbl.pack(expand=True, fill="both", padx=20, pady=20)
        
        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=20)
        
        ctk.CTkButton(btn_frame, text="SET AS WALLPAPER", command=lambda: [self.preview(meta), self.apply(), top.destroy()]).pack(side="right", padx=20)
        ctk.CTkButton(btn_frame, text="CLOSE", fg_color="gray", command=top.destroy).pack(side="right", padx=20)
        top.img_ref = ctk_img

    def preview(self, meta):
        self.selected_img_meta = meta
        self.system_status.configure(text=f"TARGET: {meta['name']}")

    def apply(self):
        if not hasattr(self, 'selected_img_meta'): return
        path = self.get_local_path(self.selected_img_meta)
        if path and set_wallpaper(path):
            self.system_status.configure(text="VISUAL EQUIPPED")
            os.system(f"osascript -e 'display notification \"Wallpaper Synchronized\" with title \"VibeHub Pro\"'")
        self.save_config()

    def perform_discovery(self):
        query = self.discover_query.get().strip()
        if not query: return
        
        self.disc_status.configure(text="Searching Wallhaven...", text_color="yellow")
        self.disc_btn.configure(state="disabled")
        
        threading.Thread(target=self.discovery_worker, args=(query,), daemon=True).start()

    def discovery_worker(self, query):
        try:
            params = {"q": query, "categories": "111", "purity": "100", "sorting": "relevance", "atleast": "1920x1080"}
            resp = requests.get(WALLHAVEN_API, params=params, timeout=15)
            data = resp.json().get("data", [])
            
            if not data:
                self.after(0, lambda: self.finish_discovery("No results found.", "red"))
                return
            
            # Use "Discoveries" as a special category
            target_dir = ROOT_DIR / "media_library" / "Discoveries" / query
            target_dir.mkdir(parents=True, exist_ok=True)
            
            self.after(0, lambda: self.disc_status.configure(text=f"Syncing {len(data[:10])} visuals..."))
            
            for i, item in enumerate(data[:10]):
                img_url = item["path"]
                ext = os.path.splitext(img_url)[1] or ".jpg"
                dest = target_dir / f"disc_{i+1}{ext}"
                if not dest.exists():
                    img_data = requests.get(img_url, timeout=20).content
                    with open(dest, "wb") as f: f.write(img_data)
                    
                    # New: Resolution Guard Check
                    from scripts.resolution_guard import is_suitable_for_wallpaper
                    suitable, reason = is_suitable_for_wallpaper(dest)
                    if not suitable:
                        print(f"[Discovery] Rejected {query} image: {reason}")
                        dest.unlink()
            
            self.after(0, lambda: self.finish_discovery(f"Synced '{query}' to Discoveries!", "green"))
            self.after(0, self.reload_library)
            
        except Exception as e:
            self.after(0, lambda: self.finish_discovery(f"Search failed: {str(e)}", "red"))

    def run_scrub(self):
        self.system_status.configure(text="CLEANING LIBRARY...", text_color="orange")
        from scripts.resolution_guard import scrub_library
        def work():
            removed = scrub_library(ROOT_DIR / "media_library")
            removed += scrub_library(ROOT_DIR / "anime_images")
            self.after(0, lambda: self.reload_library())
            self.after(0, lambda: self.system_status.configure(text=f"CLEANED: {removed} REMOVED", text_color="white"))
            self.after(0, lambda: messagebox.showinfo("Optimization Complete", f"Successfully removed {removed} unsuitable images from your multiverse."))
        threading.Thread(target=work, daemon=True).start()

    def finish_discovery(self, msg, color):
        self.disc_status.configure(text=msg, text_color=color)
        self.disc_btn.configure(state="normal")

    def quick_random(self):
        """Pick a random image from the current collection and set it."""
        imgs = self.library.get(self.current_cat.get(), {}).get(self.current_col.get(), [])
        if imgs:
            target = random.choice(imgs)
            self.selected_img_meta = target
            self.apply()
            self.system_status.configure(text=f"RANDOMIZED: {target['name']}")
        else:
            messagebox.showinfo("Wait", "Please select a collection first!")

    def toggle_engine(self, initial=False):
        if self.auto_on.get():
            if self.engine_thread and self.engine_thread.is_alive():
                return
            self.engine_thread = threading.Thread(target=self.engine_loop, daemon=True)
            self.engine_thread.start()
            if not initial: self.system_status.configure(text="VIBE-ENGINE: ONLINE")
        self.save_config()

    def engine_loop(self):
        while self.auto_on.get():
            pool = []
            if self.pinned_collections:
                # Use ONLY pinned collections if any exist
                for pin in self.pinned_collections:
                    try:
                        cat, col = pin.split(":", 1)
                        items = self.library.get(cat, {}).get(col, [])
                        pool.extend(items)
                    except Exception as e:
                        print(f"Error loading pinned {pin}: {e}")
            else:
                # Fallback to current selection or whole library
                active_cat = self.current_cat.get()
                active_col = self.current_col.get()
                pool = self.library.get(active_cat, {}).get(active_col, [])
                if not pool:
                    # Absolute fallback: Everything
                    for cat_data in self.library.values():
                        for col_data in cat_data.values():
                            pool.extend(col_data)

            if pool:
                target = random.choice(pool)
                print(f"[VIBE-ENGINE] Triggering change: {target['name']}", flush=True)
                self.system_status.configure(text=f"ENGINE: EQUIPPING {target['name']}")
                self.selected_img_meta = target # Mark as selected so 'LIKE' works
                path = self.get_local_path(target)
                if path: set_wallpaper(path)
            
            # Responsive sleep loop with countdown
            wait_seconds = int(self.interval.get() * 60)
            for s in range(wait_seconds, 0, -1):
                if not self.auto_on.get(): 
                    self.system_status.configure(text="ENGINE: STOPPED")
                    return
                # Show countdown every 10 seconds or last 5 seconds
                if s % 10 == 0 or s <= 5:
                    self.system_status.configure(text=f"NEXT VIBE IN {s}s...")
                time.sleep(1)

    def hide_window(self):
        self.withdraw()
        if not pystray:
            self.quit() # Fallback if no pystray

    def show_window(self):
        self.deiconify()
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)

    def setup_tray(self):
        try:
            # Try to find any image for the icon
            icon_path = next((ROOT_DIR / "media_library").glob("**/*.jpg"), None)
            if icon_path:
                img = Image.open(icon_path)
            else:
                img = Image.new('RGB', (64, 64), color=(73, 109, 137))
        except:
            img = Image.new('RGB', (64, 64), color=(73, 109, 137))
            
        menu = (
            item('Show VibeHub', self.show_window),
            item('Cycle Wallpaper', self.quick_random),
            item('Exit Universe', self.quit_all)
        )
        self.tray = pystray.Icon("VibeHub", img, "VibeHub Pro", menu)
        self.tray.run()

    def add_tooltip(self, widget, text):
        widget.bind("<Enter>", lambda e: self.show_tooltip(e, text))
        widget.bind("<Leave>", lambda e: self.hide_tooltip())

    def show_tooltip(self, event, text):
        if hasattr(self, "tooltip_window") and self.tooltip_window:
            return
            
        bbox = event.widget.bbox("insert")
        x_off, y_off = (bbox[0], bbox[1]) if bbox else (0, 0)
        x += event.widget.winfo_rootx() + x_off + 25
        y += event.widget.winfo_rooty() + y_off + 20
        
        self.tooltip_window = tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=text, justify="left", background="#2b2b2b", 
                         foreground="white", relief="solid", borderwidth=1,
                         font=("Inter", "10"))
        label.pack(ipadx=5, ipady=2)
        
    def hide_tooltip(self):
        if hasattr(self, "tooltip_window") and self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def quit_all(self):
        if hasattr(self, 'tray'):
            self.tray.stop()
        self.auto_on.set(False)
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = VibeHubApp()
    app.mainloop()
