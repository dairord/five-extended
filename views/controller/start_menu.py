from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from pathlib import Path


# print(Path(__file__).parent / "start_menu.kv")

Builder.load_file(str(Path(__file__).parent.parent / "front" / "start_menu.kv"))


class StartMenu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)


    def new_project(self, instance):
        self.manager.current = "select_image"

    def load_project(self, instance):
        self.manager.current = "load_project"

    def see_project(self, instance):
        self.manager.current = "see_project"