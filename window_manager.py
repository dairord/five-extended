from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from views.controller.config_menu import ConfigMenu
from views.controller.init_screen import InitialScreen
from views.controller.load_project import LoadProject
from views.controller.path_adder import PathAdder
from views.controller.select_screen import SelectScreen
from views.controller.edit_screen import EditScreen
from views.controller.show_results import ShowResults
from views.controller.start_menu import StartMenu
from views.controller.image_tranformation import ImageTransformation

class MyAppScreenManager(ScreenManager):
    image_path = StringProperty()

    # def go_to_process_screen(self, coord1, coord2):
    #     process_screen = self.get_screen('process_image')
    #     process_screen.coord1 = coord1
    #     process_screen.coord2 = coord2
    #     self.current = 'process_image'

    def go_back_to_select(self):
        self.current = "select_image"

class MyApp(App):
    title = "Map generator"
    def build(self):
        Builder.load_file("windows.kv")
        sm = MyAppScreenManager()
        sm.add_widget(InitialScreen(name="init_screen"))
        sm.add_widget(ConfigMenu(name="config_menu"))
        sm.add_widget(StartMenu(name="start_menu"))
        sm.add_widget(SelectScreen(name="select_image"))
        sm.add_widget(ImageTransformation(name="image_transformation"))
        sm.add_widget(EditScreen(name="process_image"))
        sm.add_widget(LoadProject(name="load_project"))
        sm.add_widget(PathAdder(name="path_adder"))
        sm.add_widget(ShowResults(name="show_results"))
        return sm


if __name__ == "__main__":
    MyApp().run()
