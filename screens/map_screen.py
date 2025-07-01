from kivy.uix.screenmanager import Screen  # Base class for creating screens
from kivy.uix.boxlayout import BoxLayout  # For creating vertical and horizontal layouts
from kivy.uix.button import Button  # For the navigation menu and toggle button
from kivy.uix.image import Image  # To display the map image
from kivy.graphics import Color, Ellipse, Rectangle  # For drawing shapes on the canvas
from kivy.clock import Clock  # To schedule tasks (e.g., drawing squad symbols later)
import csv
from kivy.app import App
from user_classes import User
from kivy.graphics import InstructionGroup
from kivy.core.image import Image as CoreImage
from kivy.properties import BooleanProperty
from kivy.graphics import InstructionGroup
from plyer import gps
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.widget import Widget
from kivy.core.window import Window



class MapScreen(Screen):
    show_meetup_flag = BooleanProperty(True)  # Default: visible, boolean toggle for squad meetup symbol visibility

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_db = None
        self.show_symbols = False
        self.squad_symbols = {}
        
        # Create main vertical layout
        self.layout = BoxLayout(orientation="vertical")
        self.eventName = None
        self.map_image = None

        # Navigation Menu - centered and third width
        self.nav_layout = BoxLayout(size_hint=(1, 0.1))
        self.navigation_button = Button(
            text="Navigation Menu",
            background_color=(0, 0, 1, 1),
            size_hint=(None, 1),  # Fixed width, full height
            size=(Window.width * 0.33, 0),  # One third of window width
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        self.navigation_button.bind(on_press=lambda x: self.switch_screen("nav_menu"))
        self.nav_layout.add_widget(self.navigation_button)
        self.layout.add_widget(self.nav_layout)
        
        # Toggle button for friend locations - centered and third width
        self.toggle_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.toggle_button = Button(
            text="Show Locations", 
            size_hint=(None, 1),  # Fixed width, full height
            size=(Window.width * 0.33, 0),  # One third of window width
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        self.toggle_button.bind(on_press=self.toggle_symbols)
        self.toggle_layout.add_widget(self.toggle_button)
        self.layout.add_widget(self.toggle_layout)

        # Toggle button for meet-up flag - centered and third width
        self.flag_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.flag_toggle_button = Button(
            text="Toggle Meet-Up Flag", 
            size_hint=(None, 1),  # Fixed width, full height
            size=(Window.width * 0.33, 0),  # One third of window width
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        self.flag_toggle_button.bind(on_press=self.toggle_meetup_flag)
        self.flag_layout.add_widget(self.flag_toggle_button)
        self.layout.add_widget(self.flag_layout)
        
        # GPS button - centered and third width
        self.gps_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.gps_button = Button(
            text="Start GPS", 
            size_hint=(None, 1),  # Fixed width, full height
            size=(Window.width * 0.33, 0),  # One third of window width
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        self.gps_button.bind(on_press=lambda instance: self.start_gps())
        self.gps_layout.add_widget(self.gps_button)
        self.layout.add_widget(self.gps_layout)
        
        self.add_widget(self.layout)
        self.shape_group = InstructionGroup()   #draw shapes in instruction group, not canvas

    def update_symbols_visibility(self):
        """
        Show or hide friend symbols based on the toggle state by adding or removing their canvas instructions.
        """
        if self.map_image:
            for usern, symbol_dict in self.squad_symbols.items():
                group = symbol_dict.get("group")
                if group:
                    if self.show_symbols:
                        if group not in self.map_image.canvas.children:
                            self.map_image.canvas.add(group)
                        print(f"Showing symbol for {usern}.")
                    else:
                        if group in self.map_image.canvas.children:
                            self.map_image.canvas.remove(group)
                        print(f"Hiding symbol for {usern}.")
            self.map_image.canvas.ask_update()

    def toggle_symbols(self, instance):
        self.show_symbols = not self.show_symbols  # Toggle state
        self.toggle_button.text = "Hide Friend Locations" if self.show_symbols else "Show Friend Locations"
        self.update_symbols_visibility()


    def toggle_meetup_flag(self, instance):
        self.show_meetup_flag = not self.show_meetup_flag
        self.redraw_map()

    def redraw_map(self):
        if self.map_image:
            self.map_image.canvas.remove(self.shape_group)  # Remove old shapes
            self.shape_group = InstructionGroup()  # Reset group
            self.add_map_shapes(self.map_image)  # Re-add shapes

    def set_event_name(self, event_name, event_db):
        """
        Dynamically update the map image based on the selected event name.
        """
        self.eventName = event_name
        map_file = event_db.get(event_name, "disney.jpg")  # Get the map file, fallback to default

        # Clear the previous map_image if it exists
        if self.map_image:
            self.layout.remove_widget(self.map_image)

        # Load the new map image with scaling properties
        self.map_image = Image(
            source=map_file,
            size_hint=(1, 0.9),
            allow_stretch=True,
            keep_ratio=True
        )

        # Add shapes/icons dynamically to the map canvas
        self.add_map_shapes(self.map_image)

        # Insert the updated map_image at the top of the layout
        self.layout.add_widget(self.map_image, index=0)  # Add below the nav button
        print(f"Map updated to: {map_file}")

        # Schedule squad symbol display after the map image is loaded
        Clock.schedule_once(lambda dt: self.load_and_display_friends(), 0.6)

    def add_map_shapes(self, map_image):
        """
        Add shapes/icons dynamically on the map_image's canvas.
        Only adds to the InstructionGroup so the base map is not erased.
        """
        from kivy.graphics import Color, Rectangle
        from kivy.core.image import Image as CoreImage

       #meetUpLoc = (350, 250)  # This will later be dynamic
        meetUpLoc = getattr(App.get_running_app(), 'meetup_location', (350, 250))

        current_user = App.get_running_app().current_user

        if not map_image:
            return

        # Clear previous shapes by replacing the group
        if hasattr(self, 'shape_group'):
            map_image.canvas.remove(self.shape_group)

        self.shape_group = InstructionGroup()

        # Draw current user location as green square
        self.shape_group.add(Color(0, 1, 0, 1))  # Green
        self.shape_group.add(Rectangle(pos=current_user.get_loc(), size=(10, 10)))

        # Conditionally draw meet-up flag icon
        if self.show_meetup_flag:
            flag_texture = CoreImage("flag_icon.png").texture
            # Flag size reduced to 32x32 (half of original 64x64) for better visual balance
            self.shape_group.add(Rectangle(texture=flag_texture, pos=meetUpLoc, size=(32, 32)))

        # Add updated group to the canvas
        map_image.canvas.add(self.shape_group)

    def add_squad_member_symbol(self, user):
        x, y = user.location
        color = self.generate_unique_color(user.usern)

        if self.map_image:
            group = InstructionGroup()
            group.add(Color(*color))
            ellipse = Ellipse(pos=(x, y), size=(20, 20))
            group.add(ellipse)
            self.map_image.canvas.add(group)

            self.squad_symbols[user.usern] = {
                "group": group,
                "ellipse": ellipse,
                "color": color,
                "orig_pos": (x, y)
            }
            print(f"Adding symbol for {user.usern} at {x}, {y}")

    def generate_unique_color(self, username):
        """
        Generate a unique color for a username.
        Args:
            username (str): The username of the squad member.
        Returns:
            tuple: RGBA color values in the range (0, 1).
        """
        # Simple hash to generate color
        hash_val = hash(username)
        r = ((hash_val & 0xFF0000) >> 16) / 255.0
        g = ((hash_val & 0x00FF00) >> 8) / 255.0
        b = (hash_val & 0x0000FF) / 255.0
        return (r, g, b, 1)  # Return RGBA with full opacity
    def display_squad_symbols(self):
        """
        Loop through the squad list and add symbols for each member.
        """
        for member in self.squad_list:
            self.add_squad_member_symbol(member)

    def switch_screen(self, screen_name):
        """
        Navigate to another screen.
        """
        self.parent.current = screen_name


    def load_and_display_friends(self):
        current_user = App.get_running_app().current_user

        try:
            with open("UserDB.txt", newline='') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if row[2].lower() in [f.lower() for f in current_user.friendList]:  # row[2] = username
                        # Parse their pixel location string
                        loc_string = row[6].strip("[]")
                        friend_location = [int(val.strip()) for val in loc_string.split(",")]
                        friend = User(
                            firstn=row[0], lastn=row[1], usern=row[2], email=row[3],
                            password=row[4], birthday=row[5], location=friend_location
                        )
                        self.add_squad_member_symbol(friend)
        except Exception as e:
            print("Error loading friend locations:", e)

    def start_gps(self):
        if platform == 'android':
            try:
                gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
                gps.start(minTime=1000, minDistance=1)  # Update every 1 second or 1 meter
            except NotImplementedError:
                print("GPS is not implemented on this platform")
        else:
            print("GPS only works on Android in this setup")

    def on_gps_location(self, **kwargs):
        print(f"GPS Location: {kwargs}")
        # Example: update user location if keys exist
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat and lon:
            print(f"Received location: ({lat}, {lon})")
            # You could assign this to App.get_running_app().current_user.location

    def on_gps_status(self, stype, status):
        print(f"GPS status update: {stype} - {status}")

