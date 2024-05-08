from pathlib import Path
from kivy.uix.screenmanager import Screen
import cv2
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from PIL import Image
import numpy as np
from utils.image_transformations import (
    create_mask,
    create_otsu,
    find_and_sort_contours,
    create_image_detection,
    write_files,
)
import time

base_dir = Path(__file__).parent.parent
Builder.load_file(str(base_dir / "views" / "edit_screen.kv" ))

class EditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_image_path = None
        self.modified_image_path = None
        self.original_image = None
        self.modified_image = None
        self.hue = 70
        self.saturation = 255
        self.value = 50
        self.rotation = 180
        self.active_mask = False
        self.active_detection = False
        self.active_final = False

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        image_path = self.manager.image_path  

        if image_path:
            self.modified_image_path = str(base_dir / "tmp" / "modified.png" )
            self.original_image_path = image_path
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
        if self.active_detection or self.active_mask:
            self.rotation = angle
            self.modified_image = Image.open(self.modified_image_path)
            print(angle - 180)
            rotated_image = self.modified_image.rotate(angle - 180)
            
        elif self.original_image:
            self.rotation = angle
            rotated_image = self.original_image.rotate(angle - 180)

        if not self.active_final:
            rotated_image.save(self.modified_image_path)
            self.refresh_image()

    def apply_processing(self, processing_func, *args):
        if self.original_image:
            img = cv2.imread(self.original_image_path)
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

        create_image_detection(contours, img, True)
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
        self.rotate_image(self.rotation)


    def generate_files(self):
        write_files(self.modified_image_path, self.hue, self.saturation, self.value)

