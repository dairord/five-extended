import json
import os
from pathlib import Path
import subprocess
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty

Builder.load_file(str(Path(__file__).parent.parent / "front" / "show_results.kv"))
base_dir = Path(__file__).parent.parent.parent

class ShowResults(Screen):
    final_image = ObjectProperty()
    show_button = ObjectProperty()
    five_button = ObjectProperty()
    is_original = False
    five_path = ""

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.final_image.source = str(self.manager.final_project_path / "colores.png")
        self.final_image.reload()
        with open(os.path.join(base_dir, "preferences.json"), "r", encoding="utf-8") as f:
                prefs = json.load(f)
        if Path(prefs.get("five_path", "")).is_file():
            self.five_button.disabled = False
            self.five_path = prefs.get("five_path", "")

    def change_image(self):
        self.is_original = not self.is_original
        if self.is_original:
            self.final_image.source = str(self.manager.final_project_path / "original.png")
        else:
            self.final_image.source = str(self.manager.final_project_path / "colores.png")
        self.final_image.reload()

    def show_kml(self):
        os.startfile(str(self.manager.final_project_path / "project.kml"))

    def finish(self):
        subprocess.run(self.five_path, check=True)

        


        