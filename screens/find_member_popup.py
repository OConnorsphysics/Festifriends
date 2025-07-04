import math
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from database import set_current_user
import os

class FindMemberPopup(Popup):
    def __init__(self, member_name=None, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Find Member: {member_name}" if member_name else "Find Member"
        self.size_hint = (0.7, 0.5)
        self.auto_dismiss = True
        
        self.member_name = member_name
        self.distance = self.calculate_distance()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Member info
        if member_name:
            layout.add_widget(Label(text=f"Member: {member_name}", font_size='16sp', size_hint=(1, 0.2)))
        
        # Distance display
        if self.distance is not None:
            distance_text = f"Distance: {self.distance:.1f} meters"
        else:
            distance_text = "Distance: Unable to calculate"
        
        layout.add_widget(Label(text=distance_text, font_size='14sp', size_hint=(1, 0.2)))
        
        # Additional info placeholder
        layout.add_widget(Label(text="(Future: Direction, Last seen, etc.)", size_hint=(1, 0.3)))
        
        close_btn = Button(text="Close", size_hint=(1, 0.2))
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)
        self.add_widget(layout)

    def calculate_distance(self):
        """Calculate distance between current user and selected friend"""
        try:
            app = App.get_running_app()
            if not app or not app.current_user or not self.member_name:
                return None
            
            current_user = app.current_user
            
            # Load the friend's user object
            friend_user = set_current_user(self.member_name)
            if not friend_user:
                print(f"Could not load user data for {self.member_name}")
                return None
            
            # Get current event's pixel to meter value
            pixel_to_meter = self.get_current_event_pixel_to_meter()
            if pixel_to_meter is None:
                print("Could not get pixel to meter value for current event")
                return None
            
            # Calculate distance using the existing function
            return self.FriendDistance(friend_user, pixel_to_meter)
            
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return None

    def get_current_event_pixel_to_meter(self):
        """Get the pixel to meter value for the current event"""
        try:
            app = App.get_running_app()
            if not app or not app.current_event:
                return None
            
            current_event = app.current_event
            
            # Load events from EventsDB.txt
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 12 and parts[1] == current_event:
                            # Pixel to meter is at index 6 (7th field)
                            pixel_to_meter_str = parts[6]
                            try:
                                return float(pixel_to_meter_str)
                            except ValueError:
                                print(f"Invalid pixel to meter value: {pixel_to_meter_str}")
                                return None
            
            return None
        except Exception as e:
            print(f"Error getting pixel to meter: {e}")
            return None

    def FriendDistance(self, friendUser, PixeltoMeter):
        current_user = App.get_running_app().current_user

        userLocX = current_user.get_loc()[0]
        userLocY = current_user.get_loc()[1]
        friendLocX = friendUser.get_loc()[0]
        friendLocY = friendUser.get_loc()[1]
        square = (userLocX-friendLocX)**2 + (userLocY-friendLocY)**2
        DistancePixels = math.sqrt(square)
        DistanceMeters = DistancePixels * PixeltoMeter
        return DistanceMeters

    #def FriendDirection(self):
