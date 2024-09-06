from pathlib import Path
from kivy.uix.screenmanager import Screen
import json
import os
import re
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from utils.google_image_download import download_image
from utils.project_manager import copy_file
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from utils.tiffGenerator import generate_tif
import time
import cv2

# print(os.getcwd())
local_dir = Path(__file__).parent.parent
base_dir = Path(__file__).parent.parent.parent

Builder.load_file(str(local_dir / "front" / "select_screen.kv"))
prefs_path = os.path.join(base_dir, "preferences.json")
default_prefs = {
    "url": "https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    "url2": "https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
    "url3": "https://api.maptiler.com/maps/satellite/{z}/{x}/{y}@2x.jpg?key=SCfiaKdgX6tLDVBemuVv",
    "tile_size": 256,
    "tile_format": "jpg",
    "dir": os.path.join(base_dir, "images"),
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
    global tmp_img_path
    coord1_input = ObjectProperty()
    coord2_input = ObjectProperty()
    map_image = ObjectProperty()
    # switch = ObjectProperty()
    select_image_button = ObjectProperty()
    maptiler_checkbox = ObjectProperty()
    google_checkbox = ObjectProperty()
    download_image_button = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not os.path.isfile(prefs_path):
            with open(prefs_path, "w", encoding="utf-8") as f:
                json.dump(default_prefs, f, indent=2, ensure_ascii=False)

    def on_pre_enter(self, *args):
        try:
            with open(prefs_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)
                
            google_key = prefs.get("google_api_key", "")
            maptiler_key = prefs.get("maptiler_api_key", "")
            self.maptiler_checkbox.active = True
            if google_key != "":
                self.google_checkbox.disabled = False
            if maptiler_key != "":
                self.maptiler_checkbox.disabled = False

            if not self.google_checkbox.disabled:
                self.google_checkbox.active = True
            elif not self.maptiler_checkbox.disabled:
                self.maptiler_checkbox.active = True
            else:
                self.download_image_button.disabled = True
        except FileNotFoundError:
            print("preferences.json file not found")
        except json.JSONDecodeError:
            print("Error decoding preferences.json")



    def handle_paste(self, instance, text_input):
        self.map_image.reload()

        clipboard_content = Clipboard.paste()
        if self.validate_and_set_coordinates(clipboard_content, text_input):
            pass
        else:
            self.show_error("Clipboard does not contain valid coordinates.")

    def validate_and_set_coordinates(self, text, text_input):
        try:
            floats = re.findall(
                r"([+-]?[0-9]*[.]?[0-9]+),\s*([+-]?[0-9]*[.]?[0-9]+)", text
            )
            if floats:
                coord_pair = floats[0]
                text_input.text = f"{coord_pair[0]}, {coord_pair[1]}"
                return True
            else:
                return False
        except Exception as e:
            self.show_error("Error parsing coordinates")
            return False

    def next_window(self, instance):
        tmp_img_path = self.manager.image_path 
        lat1, lon1, lat2, lon2 = self.get_coordinates()
        if not lat1 or not lon1 or not lat2 or not lon2:
            return
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
        generate_tif(tmp_img_path, lat1, lon1, lat2, lon2)
        self.manager.square_coordinates = ((lon1, lat1), (lon2, lat1), (lon2, lat2), (lon1, lat2))
        # add_elevations_to_tiff(str(base_dir / "utils" / "spain.tif"))
        self.manager.current = "image_transformation"

    # def get_CNIG_elevations():
    #     coordinates = [lat1, lon1], [lat2, lon1], [lat2, lon2], [lat1, lon2]
    #     if getIndex(coordinates):
    #         for tif_code in get_tif_list():
    #             download_elevation(tif_code)

    def reload_image(self, instance):
        # download_thread = threading.Thread(target=self.download_image)
        # download_thread.start()
        # download_thread.join()
        self.download_image()
        self.map_image.reload()

    def download_image(self):
        lat1, lon1, lat2, lon2 = self.get_coordinates()
        if not lat1 or not lon1 or not lat2 or not lon2:
            return
        
        search_motor = [self.google_checkbox.active, self.maptiler_checkbox.active]
        img = download_image(
            float(lat1), float(lon1), float(lat2), float(lon2), search_motor
        )
        if img is None or not img.size:
            self.show_error("Could not load map image properly")
        else:
            tmp_img_path = str(base_dir / "tmp" / f"tmpImg_{int(time.time())}.png")
            self.manager.image_path = tmp_img_path

            cv2.imwrite(tmp_img_path, img)
            print(tmp_img_path)
            self.update_image(tmp_img_path)

    def get_coordinates(self):    
        coord1 = self.coord1_input.text
        coord2 = self.coord2_input.text
        print(coord1)
        print(coord2)
        if coord1 == "" or coord2 == "":
            self.show_error("Please input both coordinates")
            return None, None, None, None
        try:
            lat1, lon1 = [float(x) for x in re.findall(r"[+-]?\d*\.\d+|d+", coord1)]
            lat2, lon2 = [float(x) for x in re.findall(r"[+-]?\d*\.\d+|d+", coord2)]
        except ValueError:
            self.show_error("Invalid coordinates format")
            return None, None, None, None
        return lat1, lon1, lat2, lon2


    def update_image(self, img_path):
        self.map_image.source = img_path
        self.map_image.reload()
        self.manager.image_path = img_path
        self.select_image_button.disabled = False

    def load_image(self, instance):
        self.open_filechooser()

    def open_map(self):
        os.startfile(base_dir / "mapa.html")

    def open_filechooser(self):
        filechooser = FileChooserListView(dirselect=False, path=str(base_dir))
        filechooser.bind(on_submit=self.on_file_select)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)

        # Select button
        select_button = Button(text='Select', size_hint=(1, 0.1))
        select_button.bind(on_press=lambda x: self.on_file_select(filechooser, filechooser.selection, popup))

        layout.add_widget(select_button)

        popup = Popup(title="Select custom image", content=layout,
                      size_hint=(0.9, 0.9), size=(400, 400))
        popup.open()

    def on_file_select(self, instance, selection, popup):
        if selection:
            path = Path(selection[0])
            new_name = f"tmpImg_{int(time.time())}.png" 
            if copy_file(path, base_dir / "tmp", new_name):
                self.update_image(str(base_dir / "tmp" / new_name))
        popup.dismiss()

    def show_error(self, message):

        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()
