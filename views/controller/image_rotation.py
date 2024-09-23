from pathlib import Path
import threading
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from PIL import Image as PILImage
from utils.elevation_manager import start_elevation_download
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from utils.tiffGenerator import add_elevations_to_tiff, generate_tif, get_actual_transform, pixel_to_geo, point_to_square_coordinates

local_dir = Path(__file__).parent.parent
base_dir = Path(__file__).parent.parent.parent
Builder.load_file(str(local_dir / "front" / "image_rotation.kv"))

class ImageRotation(Screen):
    download_button = ObjectProperty(None)
    top_id = ObjectProperty(None)
    bottom_id = ObjectProperty(None)
    left_id = ObjectProperty(None)
    right_id = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_image_path = None
        self.modified_image_path = None
        self.original_image = None
        self.modified_image = None
        self.rotation = 0
        self.resolution = "02107"
        self.crop_pixels = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}  
        self.new_square_coordinates = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.original_image_path = self.manager.image_path  
        self.new_square_coordinates = None

        if self.original_image_path:
            self.modified_image_path = str(base_dir / "tmp" / "modified.png")
            self.load_images()
            self.refresh_image()

    def load_images(self):
        try:
            self.original_image = PILImage.open(self.modified_image_path)
            self.modified_image = PILImage.open(self.modified_image_path)
            self.modified_image.save(self.modified_image_path)
            self.ids.map_image.source = self.modified_image_path
        except IOError:
            print("Error in loading images")

    def rotate_image(self, angle):
        self.rotation = angle
        rotated_image = self.original_image.rotate(angle, expand=True)
        rotated_image.save(self.modified_image_path)
        self.refresh_image()

    def refresh_image(self):
        self.ids.map_image.reload()


    def next_window(self):
        self.manager.rotation = self.rotation
        self.manager.modified_image_path = self.modified_image_path
        if self.new_square_coordinates:
            self.manager.square_coordinates = self.new_square_coordinates
        self.manager.current = "process_image"

   
