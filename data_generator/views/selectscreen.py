from kivy.uix.screenmanager import ScreenManager, Screen
import json
import os
import re
import cv2
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from utils.google_image_download import download_image_less
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from functools import partial
import time
print(os.getcwd())
Builder.load_file('views/selectscreen.kv')
file_dir = os.path.dirname(__file__)
prefs_path = os.path.join(file_dir, "../preferences.json")
default_prefs = {
    "url": "https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    "url2": "https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
    "tile_size": 256,
    "tile_format": "jpg",
    "dir": os.path.join(file_dir, "images"),
    "headers": {
        "cache-control": "max-age=0",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
    },
    "tl": "",
    "br": "",
    "zoom": "",
}



class SelectScreen(Screen):
    coord1_input = ObjectProperty()
    coord2_input = ObjectProperty()
    map_image = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not os.path.isfile(prefs_path):
            with open(prefs_path, "w", encoding="utf-8") as f:
                json.dump(default_prefs, f, indent=2, ensure_ascii=False)
    

    def handle_paste(self, instance, text_input):
        # Access the clipboard content
        clipboard_content = Clipboard.paste()
        # Try to parse two floats separated by a comma
        if self.validate_and_set_coordinates(clipboard_content, text_input):
            pass  # Here you can implement logic to be executed after successful paste
        else:
            self.show_error("Clipboard does not contain valid coordinates.")

    def validate_and_set_coordinates(self, text, text_input):
        # Validate the clipboard content and set to the TextInput if valid
        try:
            # Using regex to find two floats separated by a comma
            floats = re.findall(r"([+-]?[0-9]*[.]?[0-9]+),\s*([+-]?[0-9]*[.]?[0-9]+)", text)
            if floats:
                # Assuming there is only one pair of floats in the clipboard
                coord_pair = floats[0]
                text_input.text = f"{coord_pair[0]}, {coord_pair[1]}"
                return True
            else:
                return False
        except Exception as e:
            self.show_error(f"Error parsing coordinates: {e}")
            return False
        
    def next_window(self, instance):
        self.manager.current = "process_image"

    def reload_image(self, instance):
        # Logic to get and display the map image from the API using the coordinates
        coord1 = self.coord1_input.text
        coord2 = self.coord2_input.text
        lat1, lon1 = re.findall(r"[+-]?\d*\.\d+|d+", coord1)
        lat2, lon2 = re.findall(r"[+-]?\d*\.\d+|d+", coord2)
        img = download_image_less(float(lat1), float(lon1), float(lat2), float(lon2))
        if img is None or not img.size:
            self.show_error("Could not load map image properly")
        else:
            tmp_img_path = f"tmp/tmpImg_{int(time.time())}.png"
            cv2.imwrite(tmp_img_path, img)
            self.map_image.source = tmp_img_path
            self.map_image.reload()
            self.manager.image_path = tmp_img_path

    def show_error(self, message):
        # This function will create a popup with an error message
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()
