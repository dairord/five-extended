from pathlib import Path
import threading
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from PIL import Image as PILImage
from utils.elevation_manager import start_elevation_download
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Rectangle

from utils.tiffGenerator import add_elevations_to_tiff, generate_tif, get_actual_transform, pixel_to_geo, point_to_square_coordinates

local_dir = Path(__file__).parent.parent
base_dir = Path(__file__).parent.parent.parent
Builder.load_file(str(local_dir / "front" / "image_transformation.kv"))

class ImageTransformation(Screen):
    download_button = ObjectProperty(None)
    top_id = ObjectProperty(None)
    bottom_id = ObjectProperty(None)
    left_id = ObjectProperty(None)
    right_id = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_image_path = None
        self.modified_image_path = None
        self.original_image = None
        self.modified_image = None
        self.rotation = 0
        self.resolution = "02107"
        self.crop_pixels = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}  
        self.new_square_coordinates = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.original_image_path = self.manager.image_path  

        if self.original_image_path:
            self.modified_image_path = str(base_dir / "tmp" / "modified.png")
            self.load_images()
            self.refresh_image()

    def load_images(self):
        try:
            self.original_image = PILImage.open(self.original_image_path)
            self.modified_image = PILImage.open(self.original_image_path)
            self.modified_image.save(self.modified_image_path)
            self.ids.map_image.source = self.modified_image_path
        except IOError:
            print("Error in loading images")

    def rotate_image(self, angle):
        print(angle)
        self.rotation = angle
        rotated_image = self.original_image.rotate(angle, expand=True)
        rotated_image.save(self.modified_image_path)
        self.refresh_image()

    def refresh_image(self):
        self.ids.map_image.reload()

    def set_crop_pixels(self):
        try:
            left_input = int(self.left_id.text)
            right_input = int(self.right_id.text)
            top_input = int(self.top_id.text)
            bottom_input = int(self.bottom_id.text)

            self.crop_pixels['left'] = left_input
            self.crop_pixels['right'] = right_input
            self.crop_pixels['top'] = top_input
            self.crop_pixels['bottom'] = bottom_input

            point1, _, point2, _ = self.manager.square_coordinates
            generate_tif(self.original_image_path, point1[1], point1[0], point2[1], point2[0])

            self.crop_image()

        except ValueError:
            self.show_error("Invalid input for cropping dimensions.\nPlease enter valid numbers.")



    def crop_image(self):
        pil_image = PILImage.open(self.original_image_path)
        img_width, img_height = pil_image.size

        left = self.crop_pixels['left']
        right = img_width - self.crop_pixels['right']
        top = self.crop_pixels['top']
        bottom = img_height - self.crop_pixels['bottom']

        left = max(0, left)
        right = min(img_width, right)
        top = max(0, top)
        bottom = min(img_height, bottom)


        if right > left and bottom > top:
            cropped_image = pil_image.crop((left, top, right, bottom))
            cropped_image.save(self.modified_image_path)
            self.refresh_image()
            transform = get_actual_transform()
            top_left = pixel_to_geo(left, top, transform)
            bottom_right = pixel_to_geo(right, img_height, transform)
            generate_tif(self.modified_image_path, top_left[1], top_left[0], bottom_right[1], bottom_right[0])
            transform = get_actual_transform()
            self.new_square_coordinates = point_to_square_coordinates(0,0, img_width-right, img_height-bottom, transform)
            
        else:
            print("Invalid crop dimensions, crop area must have non-zero width and height.")

    def download_elevation(self):
        self.show_choice_popup("Do you want to download the elevation data?\nThis process may take a while.")

    def download_thread(self):
        process_image = self.manager.get_screen('process_image')
        process_image.ids.generate_button.disabled = True

        elevation_path = start_elevation_download(self.manager.square_coordinates, self.resolution)
        if elevation_path is None:
            self.download_button.text = "Download failed\nUse different settings"
        else:
            self.download_button.text = "Download successful"
            add_elevations_to_tiff(elevation_path, 0)
        
        self.download_button.disabled = False
        process_image.ids.generate_button.disabled = False

    def next_window(self):
        self.manager.rotation = self.rotation
        self.manager.modified_image_path = self.modified_image_path
        self.manager.square_coordinates = self.new_square_coordinates
        self.manager.current = "process_image"

    def start_slice(self):
        self.show_error("Slice not implemented yet")

    def use_own_file(self):
        self.open_filechooser()

    def select_resolution(self, resolution):
        if resolution == 2:
            self.resolution = "MDT02"
        if resolution == 5:
            self.resolution = "MDT05"
        if resolution == 25:
            self.resolution = "02107"

    def open_filechooser(self):
        filechooser = FileChooserListView(dirselect=False, path=str(base_dir))
        filechooser.bind(on_submit=self.on_file_select)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)

        # Select button
        select_button = Button(text='Select', size_hint=(1, 0.1))
        select_button.bind(on_press=lambda x: self.on_file_select(filechooser, filechooser.selection, popup))

        layout.add_widget(select_button)

        popup = Popup(title="Select elevation file", content=layout,
                      size_hint=(0.9, 0.9), size=(400, 400))
        popup.open()

    def on_file_select(self, instance, selection, popup):
        if selection:
            process_image = self.manager.get_screen('process_image')
            path = selection[0]
            add_elevations_to_tiff(path, 0)
        
            process_image.ids.generate_button.disabled = False
            popup.dismiss()

    def show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def show_choice_popup(self, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        accept_button = Button(text='Accept')
        cancel_button = Button(text='Cancel')
        
        accept_button.bind(on_release=lambda x: self.on_choice('Accept', popup))
        cancel_button.bind(on_release=lambda x: self.on_choice('Cancel', popup))
        
        button_layout.add_widget(accept_button)
        button_layout.add_widget(cancel_button)
        
        content.add_widget(button_layout)
        
        # Create and open the popup
        popup = Popup(
            title="CNIG Elevation Download",
            content=content,
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def on_choice(self, choice, popup):
        popup.dismiss()
        if choice == 'Accept':
            self.download_button.disabled = True
            self.download_button.text = "Downloading..."
            download_thread = threading.Thread(target=self.download_thread)
            download_thread.start()
        elif choice == 'Cancel':
            print("User canceled.")
