from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from pathlib import Path



Builder.load_file(str(Path(__file__).parent.parent / "front" / "init_screen.kv"))


class InitialScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    