from pathlib import Path
from kivy.uix.screenmanager import Screen
import os
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button

base_dir = Path(__file__).parent.parent
Builder.load_file(str(base_dir / "views" / "load_project.kv" ))

class LoadProject(Screen):

    project_spinner = ObjectProperty(None)
    projects_folder_path = str(base_dir / "projects")
    selected_project = ""
    def __init__(self, **kw):
        super().__init__(**kw)
        
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        if self.project_spinner:
            self.project_spinner.values = self.get_project_names()

    def get_project_names(self):
        return [name for name in os.listdir(self.projects_folder_path) if os.path.isdir(os.path.join(self.projects_folder_path, name))]

    def set_projects_folder(self, path):
        self.projects_folder_path = path
        self.on_pre_enter()

    def open_filechooser(self):
        filechooser = FileChooserListView(dirselect=True)
        filechooser.bind(on_submit=self.on_file_select)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)

        # Select button
        select_button = Button(text='Select', size_hint=(1, 0.1))
        select_button.bind(on_press=lambda x: self.on_file_select(filechooser, filechooser.selection, popup))

        layout.add_widget(select_button)

        popup = Popup(title="Select project folder", content=layout,
                      size_hint=(0.9, 0.9), size=(400, 400))
        popup.open()

    def on_file_select(self, instance, selection, popup):
        if selection:
            path = selection[0]
            self.set_projects_folder(path)
            popup.dismiss()
    
    def set_project_data(self, path):
        self.selected_project = path
        print(Path(self.projects_folder_path) / self.selected_project / "project.kml")
        if Path(Path(self.projects_folder_path) / self.selected_project / "project.kml").is_file():
            print("yay")
            pass