from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from views.controller.load_project import LoadProject
from views.controller.select_screen import SelectScreen
from views.controller.edit_screen import EditScreen
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

    def toggle_nav_drawer(self):
        nav_drawer = self.ids.nav_drawer
        nav_drawer.set_state("toggle")

# Main App
class MyApp(App):
    def build(self):
        Builder.load_file("windows.kv")
        sm = MyAppScreenManager()
        # Add your screens to the manager
        sm.add_widget(StartMenu(name="start_menu"))
        sm.add_widget(SelectScreen(name="select_image"))
        sm.add_widget(ImageTransformation(name="image_transformation"))
        sm.add_widget(EditScreen(name="process_image"))
        sm.add_widget(LoadProject(name="load_project"))
        return sm


if __name__ == "__main__":
    MyApp().run()
