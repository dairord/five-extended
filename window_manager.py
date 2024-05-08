from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from views.load_project import LoadProject
from views.selectscreen import SelectScreen
from views.edit_screen import EditScreen
from views.start_menu import StartMenu

class MyAppScreenManager(ScreenManager):
    image_path = StringProperty()

    # def go_to_process_screen(self, coord1, coord2):
    #     process_screen = self.get_screen('process_image')
    #     process_screen.coord1 = coord1
    #     process_screen.coord2 = coord2
    #     self.current = 'process_image'

    def go_back_to_select(self):
        self.current = "select_image"


# Main App
class MyApp(App):
    def build(self):
        Builder.load_file("windows.kv")
        sm = MyAppScreenManager()
        # Add your screens to the manager
        sm.add_widget(StartMenu(name="start_menu"))
        sm.add_widget(SelectScreen(name="select_image"))
        sm.add_widget(EditScreen(name="process_image"))
        sm.add_widget(LoadProject(name="load_project"))
        return sm


if __name__ == "__main__":
    MyApp().run()
