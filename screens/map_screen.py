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
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
import os


class MapScreen(Screen):
    show_meetup_flag = BooleanProperty(True)  # Default: visible, boolean toggle for squad meetup symbol visibility
    show_event_pins = BooleanProperty(False)  # Default: hidden, boolean toggle for event meetup pins visibility

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_db = None
        self.show_symbols = False
        self.squad_symbols = {}
        self.meetup_pins = {}  # Store meetup pin groups
        
        # Create main layout - FloatLayout for precise positioning
        self.layout = FloatLayout()
        self.eventName = None
        self.map_image = None

        # Create button container with 2x3 grid to accommodate more buttons
        self.button_container = GridLayout(
            cols=2,  # 2 columns
            size_hint=(0.9, 0.3),  # 90% width, 30% height (increased for more buttons)
            pos_hint={'center_x': 0.5, 'y': 0.02},  # Center horizontally, 2% from bottom
            spacing=10,  # Reduced spacing for more buttons
            padding=10   # Reduced padding for more buttons
        )

        # Navigation Menu button
        self.navigation_button = Button(
            text="Navigation Menu",
            background_color=(0, 0, 1, 1),
            size_hint=(1, 1),
            font_size='14sp'
        )
        self.navigation_button.bind(on_press=lambda x: self.switch_screen("nav_menu"))
        self.button_container.add_widget(self.navigation_button)
        
        # Toggle button for friend locations
        self.toggle_button = Button(
            text="Show Locations",
            size_hint=(1, 1),
            font_size='14sp'
        )
        self.toggle_button.bind(on_press=self.toggle_symbols)
        self.button_container.add_widget(self.toggle_button)

        # Toggle button for meet-up flag
        self.flag_toggle_button = Button(
            text="Toggle Meet-Up Flag",
            size_hint=(1, 1),
            font_size='14sp'
        )
        self.flag_toggle_button.bind(on_press=self.toggle_meetup_flag)
        self.button_container.add_widget(self.flag_toggle_button)
        
        # GPS button
        self.gps_button = Button(
            text="Start GPS",
            size_hint=(1, 1),
            font_size='14sp'
        )
        self.gps_button.bind(on_press=lambda instance: self.start_gps())
        self.button_container.add_widget(self.gps_button)
        
        # Event Pins button
        self.event_pins_button = Button(
            text="Event Pins",
            size_hint=(1, 1),
            font_size='14sp'
        )
        self.event_pins_button.bind(on_press=self.toggle_event_pins)
        self.button_container.add_widget(self.event_pins_button)
        
        # Logout button
        self.logout_button = Button(
            text="Logout",
            size_hint=(1, 1),
            font_size='14sp'
        )
        self.logout_button.bind(on_press=self.logout)
        self.button_container.add_widget(self.logout_button)
        
        # Add button container to main layout
        self.layout.add_widget(self.button_container)
        
        # Don't load default map here - wait until screen is entered
        # self.load_default_map()
        
        self.add_widget(self.layout)
        self.shape_group = InstructionGroup()   #draw shapes in instruction group, not canvas

    def on_enter(self):
        """
        Called when the screen is entered - ensure default map is loaded if no event is selected
        """
        if not self.eventName:
            print("No event selected, loading default map")
            # Clear any existing map
            if self.map_image:
                self.layout.remove_widget(self.map_image)
                self.map_image = None
            self.load_default_map()
        elif self.eventName:
            print(f"Event selected: {self.eventName}, map should already be loaded")

    def load_default_map(self):
        """
        Load the default map image on startup
        """
        try:
            print("Loading default map: festiMap.jpg")
            self.map_image = Image(
                source="festiMap.jpg",  # Default map
                size_hint=(0.7, 0.7),  # 70% of screen width and height
                pos_hint={'center_x': 0.5, 'center_y': 0.65},  # Center horizontally, 65% from bottom (above buttons)
                allow_stretch=True,
                keep_ratio=True
            )
            print("Default map image created successfully")
            self.add_map_shapes(self.map_image)
            print("Map shapes added successfully")
            self.layout.add_widget(self.map_image)
            print("Default map added to layout successfully")
        except Exception as e:
            print(f"Error loading default map: {e}")
            import traceback
            traceback.print_exc()

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

    def toggle_event_pins(self, instance):
        self.show_event_pins = not self.show_event_pins
        self.event_pins_button.text = "Hide Event Pins" if self.show_event_pins else "Event Pins"
        self.update_event_pins_visibility()

    def redraw_map(self):
        if self.map_image:
            self.map_image.canvas.remove(self.shape_group)  # Remove old shapes
            self.shape_group = InstructionGroup()  # Reset group
            self.add_map_shapes(self.map_image)  # Re-add shapes
            self.load_event_meetup_pins()  # Load meetup pins for current event

    def set_event_name(self, event_name, event_db):
        """
        Dynamically update the map image based on the selected event name.
        """
        self.eventName = event_name
        
        # Set app-wide current event
        app = App.get_running_app()
        if app:
            app.current_event = event_name
        
        map_file = event_db.get(event_name, "festiMap.jpg")  # Get the map file, fallback to default

        # Clear the previous map_image if it exists
        if self.map_image:
            self.layout.remove_widget(self.map_image)

        # Load the new map image with 70% screen size and centered
        self.map_image = Image(
            source=map_file,
            size_hint=(0.7, 0.7),  # 70% of screen width and height
            pos_hint={'center_x': 0.5, 'center_y': 0.65},  # Center horizontally, 65% from bottom (above buttons)
            allow_stretch=True,
            keep_ratio=True
        )

        # Add shapes/icons dynamically to the map canvas
        self.add_map_shapes(self.map_image)

        # Add the map image to the layout
        self.layout.add_widget(self.map_image)
        print(f"Map updated to: {map_file}")

        # Schedule squad symbol display after the map image is loaded
        Clock.schedule_once(lambda dt: self.load_and_display_friends(), 0.6)
        
        # Load meetup pins for the current event
        Clock.schedule_once(lambda dt: self.load_event_meetup_pins(), 0.7)

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
            try:
                map_image.canvas.remove(self.shape_group)
            except ValueError:
                # Shape group not in canvas, ignore
                pass

        self.shape_group = InstructionGroup()

        # Draw current user location as green square (only if user is logged in)
        if current_user:
            self.shape_group.add(Color(0, 1, 0, 1))  # Green
            self.shape_group.add(Rectangle(pos=current_user.get_loc(), size=(10, 10)))

        # Conditionally draw meet-up flag icon
        if self.show_meetup_flag:
            try:
                flag_texture = CoreImage("flag_icon.png").texture
                # Flag size reduced to 32x32 (half of original 64x64) for better visual balance
                self.shape_group.add(Rectangle(texture=flag_texture, pos=meetUpLoc, size=(32, 32)))
            except Exception as e:
                print(f"Error loading flag icon: {e}")

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
        
        if not current_user:
            return

        try:
            # Get friends from FriendsDB.txt instead of using friendList attribute
            friends = []
            if os.path.exists("FriendsDB.txt"):
                with open("FriendsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 2 and parts[0] == current_user.usern:
                            friends.append(parts[1])
            
            # Load friend locations from UserDB.txt
            with open("UserDB.txt", newline='') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if len(row) >= 7 and row[2].lower() in [f.lower() for f in friends]:  # row[2] = username
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

    def load_event_meetup_pins(self):
        """Load meetup pins for the current event from MeetupDB.txt"""
        if not self.eventName or not self.map_image:
            return
        
        # Clear existing meetup pins
        self.clear_meetup_pins()
        
        try:
            # Get event ID from event name
            event_id = self.get_event_id_by_name(self.eventName)
            if not event_id:
                return
            
            # Load meetup points from MeetupDB.txt
            with open("MeetupDB.txt", "r") as file:
                for line in file:
                    parts = line.strip().split(";")
                    if len(parts) >= 5 and parts[0] == str(event_id):
                        meetup_name = parts[1]
                        location_str = parts[2]
                        description = parts[3]
                        image_path = parts[4]
                        
                        # Parse location
                        try:
                            x, y = map(int, location_str.split(','))
                            self.add_meetup_pin(meetup_name, (x, y), description, image_path)
                        except ValueError:
                            print(f"Invalid location format for {meetup_name}: {location_str}")
                            
        except Exception as e:
            print(f"Error loading meetup pins: {e}")
    
    def get_event_id_by_name(self, event_name):
        """Get event ID from event name"""
        try:
            with open("EventsDB.txt", "r") as file:
                for line in file:
                    parts = line.strip().split(";")
                    if len(parts) >= 2 and parts[1] == event_name:
                        return parts[0]
        except Exception as e:
            print(f"Error getting event ID: {e}")
        return None
    
    def add_meetup_pin(self, name, location, description, image_path):
        """Add a meetup pin to the map"""
        if not self.map_image:
            return
        
        try:
            from kivy.core.image import Image as CoreImage
            
            # Create instruction group for this pin
            pin_group = InstructionGroup()
            
            # Try to load the custom icon, fallback to red circle if image fails
            try:
                # Load the pin image using the same method as flag_icon
                pin_texture = CoreImage(image_path).texture
                # Add the pin image (32x32 like the flag icon)
                pin_group.add(Rectangle(texture=pin_texture, pos=location, size=(32, 32)))
                print(f"Added meetup pin with custom icon: {name} at {location} using {image_path}")
            except Exception as img_error:
                # Fallback to red circle if image loading fails
                pin_group.add(Color(1, 0, 0, 1))  # Red color
                from kivy.graphics import Ellipse
                pin_group.add(Ellipse(pos=location, size=(20, 20)))
                print(f"Added meetup pin with fallback circle: {name} at {location} (image failed: {img_error})")
            
            # Store the pin group
            pin_key = f"{name}_{location[0]}_{location[1]}"
            self.meetup_pins[pin_key] = {
                "group": pin_group,
                "name": name,
                "description": description,
                "location": location,
                "image_path": image_path
            }
            
            # Add to canvas if pins are visible
            if self.show_event_pins:
                self.map_image.canvas.add(pin_group)
                
        except Exception as e:
            print(f"Error adding meetup pin {name}: {e}")
    
    def clear_meetup_pins(self):
        """Clear all meetup pins from the map"""
        if not self.map_image:
            return
        
        for pin_key, pin_data in self.meetup_pins.items():
            group = pin_data["group"]
            if group in self.map_image.canvas.children:
                self.map_image.canvas.remove(group)
        
        self.meetup_pins.clear()
    
    def update_event_pins_visibility(self):
        """Show or hide event pins based on toggle state"""
        if not self.map_image:
            return
        
        for pin_key, pin_data in self.meetup_pins.items():
            group = pin_data["group"]
            if self.show_event_pins:
                if group not in self.map_image.canvas.children:
                    self.map_image.canvas.add(group)
            else:
                if group in self.map_image.canvas.children:
                    self.map_image.canvas.remove(group)
        
        self.map_image.canvas.ask_update()

    def logout(self, instance):
        """
        Logout the current user and return to login screen.
        """
        # Clear current user
        app = App.get_running_app()
        if app:
            app.current_user = None
            app.current_event = None
        
        # Return to login screen
        self.switch_screen("login")

