from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from pathlib import Path
import os



Builder.load_file(str(Path(__file__).parent.parent / "front" / "init_screen.kv"))
base_dir = Path(__file__).parent.parent.parent


class InitialScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)

        elevations_path = base_dir / "elevations"
        out_path = base_dir / "out"
        tmp_path = base_dir / "tmp"
        project_path = base_dir / "projects"
        try:
            if elevations_path.is_dir() is False:
                os.mkdir(elevations_path)
            if out_path.is_dir() is False:
                os.mkdir(out_path)
            if tmp_path.is_dir() is False:
                os.mkdir(tmp_path)
            if project_path.is_dir() is False:
                os.mkdir(project_path)
        except:
            self.show_error("Error creating directories.\nPlease ensure that the folders ""elevations"", ""out"", ""tmp"" and ""projects"" exists in root folder.")
    def show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()