from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import requests

WALLHAVEN_API = "https://wallhaven.cc/api/v1/search"

class MobileVibeHub(App):
    def build(self):
        self.title = "VibeHub Mobile"
        
        # Root Layout
        self.root = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=0.1, padding=10)
        header.add_widget(Label(text="VIBEHUB MULTIVERSE", font_size='20sp', bold=True))
        self.root.add_widget(header)
        
        # Search Box
        search_area = BoxLayout(size_hint_y=0.1, padding=5)
        self.search_input = TextInput(text="Naruto", multiline=False, size_hint_x=0.8)
        search_area.add_widget(self.search_input)
        search_btn = Button(text="GO", size_hint_x=0.2)
        search_btn.bind(on_press=self.search_images)
        search_area.add_widget(search_btn)
        self.root.add_widget(search_area)
        
        # Discovery Area
        self.scroll = ScrollView(size_hint_y=0.7)
        self.gallery = GridLayout(cols=2, size_hint_y=None, spacing=10, padding=10)
        self.gallery.bind(minimum_height=self.gallery.setter('height'))
        self.scroll.add_widget(self.gallery)
        self.root.add_widget(self.scroll)
        
        # Footer
        footer = BoxLayout(size_hint_y=0.1, padding=10)
        footer.add_widget(Label(text="Select image to equip", font_size='12sp'))
        self.root.add_widget(footer)
        
        # Initial search
        self.search_images()
        
        return self.root

    def search_images(self, *args):
        query = self.search_input.text
        self.gallery.clear_widgets()
        
        try:
            params = {"q": query, "categories": "111", "purity": "100", "atleast": "1080x1920"} # Phone resolution
            resp = requests.get(WALLHAVEN_API, params=params, timeout=10)
            data = resp.json().get("data", [])
            
            for item in data[:10]:
                thumb = item["thumbs"]["small"]
                full = item["path"]
                
                # Image button
                img_box = BoxLayout(orientation='vertical', size_hint_y=None, height=400)
                img = AsyncImage(source=thumb, allow_stretch=True)
                btn = Button(text="SET WALLPAPER", size_hint_y=0.3)
                btn.bind(on_press=lambda inst, url=full: self.set_mobile_wallpaper(url))
                
                img_box.add_widget(img)
                img_box.add_widget(btn)
                self.gallery.add_widget(img_box)
        except Exception as e:
            self.gallery.add_widget(Label(text=f"Connection Error: {e}"))

    def set_mobile_wallpaper(self, url):
        print(f"Syncing Wallpaper from: {url}")
        # Real Android logic using pyjnius
        try:
            from jnius import autoclass
            # ... Android-specific API calls ...
        except ImportError:
            print("Pyjnius not found. Use real Android device for this action.")

if __name__ == '__main__':
    MobileVibeHub().run()
