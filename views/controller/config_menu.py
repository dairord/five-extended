import json
import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from pathlib import Path
from kivy.properties import ObjectProperty
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button



Builder.load_file(str(Path(__file__).parent.parent / "front" / "config_menu.kv"))
base_dir = Path(__file__).parent.parent.parent


class ConfigMenu(Screen):
    google_api_key = ObjectProperty()
    maptiler_api_key = ObjectProperty()
    select_five_button = ObjectProperty()
    five_path = ""

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        try:
            with open(os.path.join(base_dir, "preferences.json"), "r", encoding="utf-8") as f:
                prefs = json.load(f)
                
            self.google_api_key.text = prefs.get("google_api_key", "")
            self.maptiler_api_key.text = prefs.get("maptiler_api_key", "")
            if Path(prefs.get("five_path", "")).is_file():
                self.select_five_button.text = "FIVE executable selected"
                
        except FileNotFoundError:
            print("preferences.json file not found")
        except json.JSONDecodeError:
            print("Error decoding preferences.json")


    def save_keys(self):
        google_key = self.google_api_key.text
        maptiler_key = self.maptiler_api_key.text
        
        prefs = {}
        try:
            with open(os.path.join(base_dir, "preferences.json"), "r", encoding="utf-8") as f:
                prefs = json.load(f)
        except FileNotFoundError:
            print("preferences.json file not found")
        except json.JSONDecodeError:
            print("Error decoding preferences.json")

        prefs["google_api_key"] = google_key
        prefs["maptiler_api_key"] = maptiler_key
        prefs["five_path"] = str(self.five_path)
        
        with open(os.path.join(base_dir, "preferences.json"), "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=4)

        print("API keys saved successfully.")

    def open_filechooser(self):
        filechooser = FileChooserListView(dirselect=True, path=str(base_dir))
        filechooser.bind(on_submit=self.on_file_select)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)

        # Select button
        select_button = Button(text='Select', size_hint=(1, 0.1))
        select_button.bind(on_press=lambda x: self.on_file_select(filechooser, filechooser.selection, popup))

        layout.add_widget(select_button)

        popup = Popup(title="Select file", content=layout,
                      size_hint=(0.9, 0.9), size=(400, 400))
        popup.open()

    def on_file_select(self, instance, selection, popup):
        if selection:
            self.five_path = Path(selection[0])
            self.select_five_button.text = "FIVE executable selected"
        popup.dismiss()