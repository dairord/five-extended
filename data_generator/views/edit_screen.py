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
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from functools import partial
from PIL import Image, ImageTk
import numpy as np
from utils.image_transformations import create_mask, create_otsu
import time

Builder.load_file('views/edit_screen.kv')

class EditScreen(Screen):
    global original_image_path, modified_image_path, original_image, modified_image
    global hue, saturation, value, rotation
    global active_mask, active_detection

    active_mask = False
    active_detection = False

    hue = 70
    saturation = 255
    value = 50
    rotation = 180
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        global original_image_path, modified_image_path, original_image, modified_image
        # Access the shared image_path from the manager
        image_path = self.manager.image_path
        # If there's a path available, update the Image widget's source
        if image_path:
            modified_image_path = "tmp/modified.png"
            original_image_path = image_path
            modified_image = Image.open(original_image_path)
            original_image = Image.open(original_image_path)
            modified_image.save(modified_image_path)
            self.ids.map_image.source = modified_image_path

    # def update_map_image(self, instance, value):
    #     # Update the Image widget's source when image_path changes
    #     # self.ids.map_image.source = value
    #     self.girar(value - 180)

    # def on_pre_leave(self, *args):
    #     # Unbind the property when leaving the screen to avoid unnecessary updates
    #     self.manager.unbind(image_path=self.update_map_image)


    def girar(self, angulo):
        global modified_image_path, original_image, rotation
        rotation = angulo
        rotatedImage = original_image.rotate(angulo - 180)
        rotatedImage.save(modified_image_path)
        # Reload the image to apply the rotation
        self.ids.map_image.reload()
    
    def update_mask(self):
        global original_image_path, modified_image_path, hue, saturation, value
        upperbound = np.array([hue, saturation, value])  
        lowerbound = np.array([0, 0, 0])
        lowerbound = lowerbound.astype(np.uint8)
        upperbound = upperbound.astype(np.uint8)
        img = cv2.imread(original_image_path)
        mask = create_mask(img, lowerbound, upperbound)
        cv2.imwrite(modified_image_path, mask)
        modified_image = Image.open(modified_image_path)
        rotated_image = modified_image.rotate(rotation - 180)
        rotated_image.save(modified_image_path)
        self.ids.map_image.reload()


    def update_detection(self):
        global original_image_path, modified_image_path, hue, saturation, value
        upperbound = np.array([hue, saturation, value])  
        lowerbound = np.array([0, 0, 0])
        lowerbound = lowerbound.astype(np.uint8)
        upperbound = upperbound.astype(np.uint8)
        img = cv2.imread(original_image_path)
        mask = create_mask(img, lowerbound, upperbound)
        otsu = create_otsu(mask)
        cv2.imwrite(modified_image_path, otsu)
        modified_image = Image.open(modified_image_path)
        rotated_image = modified_image.rotate(rotation - 180)
        rotated_image.save(modified_image_path)
        self.ids.map_image.reload()

    def toggle_mask(self):
        global modified_image_path, hue, saturation, value, active_mask, active_detection
        if(active_detection):
            pass
        upperbound = np.array([hue, saturation, value])  
        lowerbound = np.array([0, 0, 0])
        lowerbound = lowerbound.astype(np.uint8)
        upperbound = upperbound.astype(np.uint8)

        img = cv2.imread(modified_image_path)
        mask = create_mask(img, lowerbound, upperbound)
        cv2.imwrite(modified_image_path, mask)
        self.ids.map_image.reload()
        active_mask = not active_mask
        pass

    def toggle_detection(self):
        global modified_image_path, active_detection, active_mask
        if(active_mask):
            pass
        upperbound = np.array([hue, saturation, value])  
        lowerbound = np.array([0, 0, 0])
        lowerbound = lowerbound.astype(np.uint8)
        upperbound = upperbound.astype(np.uint8)

        img = cv2.imread(modified_image_path)
        mask = create_mask(img, lowerbound, upperbound)
        otsu = create_otsu(mask)
        cv2.imwrite(modified_image_path, otsu)
        self.ids.map_image.reload()
        active_detection = not active_detection
        pass

    def update_hue(self, valor):
        global hue
        hue = valor
        if (active_mask): self.update_mask()
        if (active_detection): self.update_detection()
        

    def update_saturation(self, valor):
        global saturation
        saturation = valor
        if (active_mask): self.update_mask()
        if (active_detection): self.update_detection()

    def update_value(self, valor):
        global value
        value = valor
        if (active_mask): self.update_mask()
        if (active_detection): self.update_detection()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
