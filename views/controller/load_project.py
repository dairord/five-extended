from pathlib import Path
from kivy.uix.screenmanager import Screen
import os
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from utils.kmlGenerator import search_custom_fields_in_document, File_Type

local_dir = Path(__file__).parent.parent
base_dir = Path(__file__).parent.parent.parent
Builder.load_file(str(local_dir / "front" / "load_project.kv" ))

class LoadProject(Screen):

    project_spinner = ObjectProperty(None)
    coord1 = ObjectProperty(None)
    coord2 = ObjectProperty(None)
    preview = ObjectProperty(None)
    projects_folder_path = str(base_dir / "projects")
    selected_project = ""

    original_path = None
    elevation_path = None
    tif_path = None

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
        filechooser = FileChooserListView(dirselect=True, path=str(base_dir))
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
        project_kml_path = Path(self.projects_folder_path) / self.selected_project / "project.kml"
        
        if project_kml_path.is_file():
            project_settings = [
                File_Type.ORIGINAL_IMAGE.value,
                File_Type.GENERATED_TIF.value,
                File_Type.ELEVATION_TIF.value,
                File_Type.COORDINATES.value
            ]
            kml_data = search_custom_fields_in_document(str(project_kml_path), project_settings)

            if File_Type.ORIGINAL_IMAGE.value in kml_data and len(kml_data[File_Type.ORIGINAL_IMAGE.value]) > 0:
                self.original_path = Path(self.projects_folder_path) / self.selected_project / kml_data[File_Type.ORIGINAL_IMAGE.value][0]
                self.preview.source = str(self.original_path)
            else:
                self.original_path = None  

            print(kml_data[File_Type.COORDINATES.value])
            if File_Type.COORDINATES.value in kml_data and len(kml_data[File_Type.COORDINATES.value]) > 0:
                self.coord1.text = kml_data[File_Type.COORDINATES.value][0]
                self.coord2.text = kml_data[File_Type.COORDINATES.value][1]
            else:
                self.elevation_path = None  

            if File_Type.ELEVATION_TIF.value in kml_data and len(kml_data[File_Type.ELEVATION_TIF.value]) > 0:
                self.elevation_path = Path(self.projects_folder_path) / self.selected_project / kml_data[File_Type.ELEVATION_TIF.value][0]
            else:
                self.elevation_path = None  

            if File_Type.GENERATED_TIF.value in kml_data and len(kml_data[File_Type.GENERATED_TIF.value]) > 0:
                self.tif_path = Path(self.projects_folder_path) / self.selected_project / kml_data[File_Type.GENERATED_TIF.value][0]
            else:
                self.tif_path = None  


    def edit_project_data(self):
        print(self.original_path)
        self.manager.image_path = str(self.original_path)
        print(self.manager.image_path)
        self.manager.current = "process_image"