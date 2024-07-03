import os
from pathlib import Path
from kivy.uix.screenmanager import Screen
import cv2
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from PIL import Image
import numpy as np
from utils.elevation_manager import start_elevation_download
from utils.project_manager import save_current_project, save_project_in, exists_project_folder, move_file
from kivy.uix.popup import Popup
from kivy.uix.label import Label


from utils.image_processing import (
    create_mask,
    create_otsu,
    find_and_sort_contours,
    create_image_detection,
    write_files,
)
import time

from utils.tiffGenerator import add_elevations_to_tiff

base_dir = Path(__file__).parent.parent.parent
local_dir = Path(__file__).parent.parent
Builder.load_file(str(local_dir / "front" / "edit_screen.kv" ))

class EditScreen(Screen):
    project_name_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rotated_image_path = None
        self.modified_image_path = None
        self.original_image = None
        self.modified_image = None
        self.hue = 70
        self.saturation = 255
        self.value = 50
        self.active_mask = False
        self.active_detection = False
        self.active_final = False

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        image_path = self.manager.modified_image_path  

        if image_path:
            self.modified_image_path = str(base_dir / "tmp" / "masked.png" )
            self.rotated_image_path = image_path
            self.load_images()
            self.refresh_image()

    def load_images(self):
        try:
            self.original_image = Image.open(self.rotated_image_path)
            self.modified_image = Image.open(self.rotated_image_path)
            self.modified_image.save(self.modified_image_path)
            self.ids.map_image.source = self.modified_image_path
        except IOError:
            print("Error in loading images")

    def apply_processing(self, processing_func, *args):
        if self.original_image:
            img = cv2.imread(self.rotated_image_path)
            processed_img = processing_func(img, *args)
            cv2.imwrite(self.modified_image_path, processed_img)
            self.refresh_image()

    def make_mask(self, img, hue, saturation, value ):
        upperbound = np.array([hue, saturation, value])
        lowerbound = np.array([0, 0, 0])
        lowerbound = lowerbound.astype(np.uint8)
        upperbound = upperbound.astype(np.uint8)
        mask = create_mask(img, lowerbound, upperbound)
        return mask

    def make_detection(self, img, hue, saturation, value):
        mask = self.make_mask(img, hue, saturation, value)
        otsu = create_otsu(mask)
        return otsu
    
    def make_final(self, img, hue, saturation, value):
        otsu = self.make_detection(img, hue, saturation, value)
        contours = find_and_sort_contours(otsu)

        create_image_detection(contours, img, None, False)
        return img

    def refresh_image(self):
        self.ids.map_image.reload()

    def update_hsv(self, hue=None, saturation=None, value=None):
        if hue is not None:
            self.hue = hue
        if saturation is not None:
            self.saturation = saturation
        if value is not None:
            self.value = value
        if self.active_mask or self.active_detection:
            self.apply_feature()

    def toggle_feature(self, feature):
        if feature == "mask":
            self.active_detection = False
            self.active_final = False
            self.active_mask = not self.active_mask
        elif feature == "detection":
            self.active_mask = False
            self.active_final = False
            self.active_detection = not self.active_detection
        elif feature == "final":
            self.active_mask = False
            self.active_detection = False
            self.active_final = not self.active_final
            if self.active_final:
                self.apply_processing(self.make_final, self.hue, self.saturation, self.value)            
        self.apply_feature()
            
    def apply_feature(self):
        if self.active_mask:
            self.apply_processing(self.make_mask, self.hue, self.saturation, self.value)
        elif self.active_detection:
            self.apply_processing(self.make_detection, self.hue, self.saturation, self.value)
        self.refresh_image()


    def generate_files(self):
        write_files(self.modified_image_path, self.hue, self.saturation, self.value, self.manager.rotation)

    def file_merge(self, project_name):
        self.add_elevations()
        move_file(Path(self.rotated_image_path), base_dir / "out", "original_image_" +project_name +".png") 
        write_files(self.modified_image_path, project_name , self.hue, self.saturation, self.value, self.manager.rotation)

        return True
       

    def save_to_project_folder(self):
        if not self.project_name_input.text:
            self.show_error("Select a project name before saving")
        project_name = self.project_name_input.text
        print(project_name)
        if exists_project_folder(project_name):
            self.show_error("The selected project name is already in use")
        elif self.file_merge(project_name):
            save_current_project(project_name)

    def add_elevations(self):
                # threading.Thread(target=start_elevation_download, args=square_coordinates)
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future = executor.submit(start_elevation_download, square_coordinates)
        elevation_path = str(base_dir / "elevations" / "area_elevation.tif")
        if not os.path.exists(base_dir / "elevations" / "area_elevation.tif"):
            elevation_path = start_elevation_download(self.manager.square_coordinates)  
        add_elevations_to_tiff(elevation_path, self.manager.rotation)

    def show_error(self, message):

        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()
