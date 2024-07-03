from pathlib import Path
import threading
from kivy.uix.screenmanager import Screen
import cv2
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from PIL import Image
from utils.elevation_manager import start_elevation_download
from kivy.uix.popup import Popup
from kivy.uix.label import Label


from utils.tiffGenerator import add_elevations_to_tiff

local_dir = Path(__file__).parent.parent
base_dir = Path(__file__).parent.parent.parent
Builder.load_file(str(local_dir / "front" / "image_transformation.kv" ))

class ImageTransformation(Screen):
    project_name_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_image_path = None
        self.modified_image_path = None
        self.original_image = None
        self.modified_image = None
        self.rotation = 0
        self.resolution = "02107"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.original_image_path = self.manager.image_path  

        if self.original_image_path:
            self.modified_image_path = str(base_dir / "tmp" / "modified.png" )
            self.load_images()
            self.refresh_image()

    def load_images(self):
        try:
            self.original_image = Image.open(self.original_image_path)
            self.modified_image = Image.open(self.original_image_path)
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

    def download_elevation(self):
        download_thread = threading.Thread(target=self.download_thread)
        download_thread.start()
    
    def download_thread(self):
        process_image.ids.generate_button.disabled = True 
        elevation_path = start_elevation_download(self.manager.square_coordinates, self.resolution)
        add_elevations_to_tiff(elevation_path, 0)
        process_image = self.manager.get_screen('process_image')  
        process_image.ids.generate_button.disabled = False 

    def next_window(self):
        self.manager.rotation = self.rotation
        self.manager.modified_image_path = self.modified_image_path
        self.manager.current = "process_image"

    def start_slice(self):
        self.show_error("Slice not implemented yet")

    def select_resolution(self, resolution):
        if resolution == 2:
            self.resolution = "MDT02"
        if resolution == 5:
            self.resolution = "MDT05"
        if resolution == 25:
            self.resolution = "02107"

    def show_error(self, message):

        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()
