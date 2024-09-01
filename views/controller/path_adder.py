import os
from pathlib import Path
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from utils.kmlGenerator import add_paths_to_kml

# print(os.getcwd())
local_dir = Path(__file__).parent.parent
base_dir = Path(__file__).parent.parent.parent

Builder.load_file(str(Path(__file__).parent.parent / "front" / "path_adder.kv"))


class PathAdder(Screen):
    save_button = ObjectProperty()
    project_spinner = ObjectProperty()
    path_input = ObjectProperty()

    projects_folder_path = str(base_dir / "projects")
    config_file_path = ""

    def __init__(self, **kw):
        super().__init__(**kw)

    def add_paths_file(self):
        pass

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        if self.project_spinner:
            self.project_spinner.values = self.get_project_names()


    def select_project_folder(self, project_name):
        project_kml_path = Path(self.projects_folder_path) / project_name / "project.kml"
        if project_kml_path.is_file():
            self.config_file_path = project_kml_path
            self.save_button.disabled = False
        else:
            self.show_error("The selected project does not have a project.kml file")
        

    def select_path_file(self, path):
        with open(path, "r") as f:
            self.path_input.text = f.read()

    def get_project_names(self):
        return [name for name in os.listdir(self.projects_folder_path) if os.path.isdir(os.path.join(self.projects_folder_path, name))]

    def open_filechooser(self, is_config):
        filechooser = FileChooserListView(dirselect=True, path=str(base_dir))
        filechooser.bind(on_submit=self.on_file_select)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)

        # Select button
        select_button = Button(text='Select', size_hint=(1, 0.1))
        select_button.bind(on_press=lambda x: self.on_file_select(filechooser, filechooser.selection, popup, is_config))

        layout.add_widget(select_button)

        popup = Popup(title="Select file", content=layout,
                      size_hint=(0.9, 0.9), size=(400, 400))
        popup.open()

    def on_file_select(self, instance, selection, popup, is_config):
        if selection:
            if is_config:
                self.config_file_path = Path(selection[0])
                self.save_button.disabled = False
            else:
                self.select_path_file(Path(selection[0]))
        popup.dismiss()

    def show_error(self, message, title="Error"):

        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def set_paths(self):
        add_paths_to_kml(self.config_file_path, self.path_input.text)
        self.show_error("Paths added successfully", "Info")
        
