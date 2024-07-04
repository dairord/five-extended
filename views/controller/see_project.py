from pathlib import Path
from kivy.uix.screenmanager import Screen
import os
from kivy.lang import Builder


local_dir = Path(__file__).parent.parent
base_dir = Path(__file__).parent.parent.parent
Builder.load_file(str(local_dir / "front" / "see_project.kv" ))

class SeeProject(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)