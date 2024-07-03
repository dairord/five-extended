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
from pathlib import Path
import numpy as np


# print(Path(__file__).parent / "start_menu.kv")

Builder.load_file(str(Path(__file__).parent.parent / "front" / "start_menu.kv"))


class StartMenu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)


    def new_project(self, instance):
        self.manager.current = "select_image"

    def load_project(self, instance):
        self.manager.current = "load_project"

    def watch_projects(self, instance):
        self.manager.current = "watch_projects"