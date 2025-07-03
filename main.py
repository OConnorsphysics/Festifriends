# Import necessary modules
import kivy
import time
import pandas as pd
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.uix.mapview import MapView
from kivy_garden.mapview import MapView
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from user_classes import Squad, User
from database import check_password, set_current_user
from kivy.uix.spinner import Spinner
from screens.profile_screen import ProfileScreen
from screens.group_screen import GroupsScreen
from screens.map_screen import MapScreen
from screens.admin_screen import AdminScreen
from screens.friends_screen import FriendsScreen
from kivy.uix.screenmanager import FadeTransition
from user_classes import User, Squad
from Utilities.Notifications import send_notification  # Adjust path as needed

# Set size and orientation of the app window
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')
Window.size = (800, 600)
# Window.clearcolor = (1, 1, 1, 1)
Window.clearcolor = (0.7, 0.1, 0.9, 0.9)
purple = (0.8, 0, 0.6, 0.7)
buttonColor = purple  # variable to quickly change general button colours

UserDB = pd.read_csv("UserDB.txt", sep=";", header=None,
                     names=["firstn", "lastn", "usern", "email", "password", "birthday", "location", "friendList"])

EventDB = pd.read_csv("EventsDB.txt", sep=";", header=None,
                     names=["eventName", "mapFile"])
eventName = "Shambhala" #hardcoded variable for event name to help dynamically change the map image

current_user = set_current_user("username") #set a null user so the variable/object is defined outside the LoginScreen Class, can avoid somehow?

#meet up location variable, probably shouldn't be global
meetUpLoc = [600,300]
# Define screen manager for navigating between screens
class ScreenManagement(ScreenManager):
    pass

# Define login screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #global current_user #define current user as a variable in the class and make globally accesible, might eb bad practice

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        main_layout.size_hint = (0.9, 0.9)
        main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # App name label
        label = Label(text="Location Sharing App", font_size='24sp', size_hint=(1, 0.15))
        main_layout.add_widget(label)

        # Username and password fields
        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.12))
        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(1, 0.12))
        main_layout.add_widget(self.username)
        main_layout.add_widget(self.password)

        # Button row (login, signup, forgot) - much smaller buttons
        button_row = GridLayout(cols=3, size_hint=(1, 0.08), spacing=10)
        login_btn = Button(text="Login", background_color=buttonColor, size_hint=(1, 1), font_size='12sp')
        login_btn.bind(on_press=self.login)
        signup_btn = Button(text="Sign Up", background_color=buttonColor, size_hint=(1, 1), font_size='12sp')
        signup_btn.bind(on_press=self.signup)
        forgot_btn = Button(text="Forgot Password?", background_color=buttonColor, size_hint=(1, 1), font_size='12sp')
        forgot_btn.bind(on_press=self.forgot)
        button_row.add_widget(login_btn)
        button_row.add_widget(signup_btn)
        button_row.add_widget(forgot_btn)
        main_layout.add_widget(button_row)

        # Center everything
        container = BoxLayout(orientation='vertical')
        container.add_widget(main_layout)
        self.add_widget(container)

    # Function to handle login button press
    def login(self, instance):
        if self.username.text == "admin" and self.password.text == "admin":
            # Set a default admin user object
            self.current_user = User("Admin", "User", "admin", "admin@email.com", "admin", "01/01/2000", [0, 0], user_type="admin")
            App.get_running_app().current_user = self.current_user
            self.parent.current = "map"
        elif self.password.text != "" and check_password(self.username.text, self.password.text):
            self.current_user = set_current_user(self.username.text)

            if not self.current_user:
                send_notification("Login Error", "User data could not be loaded.")
                return

            App.get_running_app().current_user = self.current_user  # Set app-wide current user
            self.parent.current = "map"
        else:
            self.username.text = ""
            self.password.text = ""
            error_label = Label(text="Incorrect username or password", color=[0, 0, 0, 1])
            send_notification("Login Error",'Incorrect username or password')
            self.add_widget(error_label)

        return self.current_user #TODO need this to be set to current_user outside the function, currently only exists in the func, import flask?

    # Function to handle sign up button press
    def signup(self, instance):
        # Switch to sign up screen
        self.parent.current = "signup"

    def forgot(self, instance):
        self.parent.current = "signup"

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        main_layout.size_hint = (0.9, 0.9)
        main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # App name label
        label = Label(text="Sign Up", font_size='24sp', size_hint=(1, 0.15))
        main_layout.add_widget(label)

        # Create a text input for username
        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.12))
        main_layout.add_widget(self.username)

        # Create a text input for password
        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(1, 0.12))
        main_layout.add_widget(self.password)

        # Create a text input for email
        self.email = TextInput(hint_text="Email", multiline=False, size_hint=(1, 0.12))
        main_layout.add_widget(self.email)

        # Button row (signup, back) - much smaller buttons
        button_row = GridLayout(cols=2, size_hint=(1, 0.08), spacing=10)
        signup_btn = Button(text="Sign Up", background_color=buttonColor, size_hint=(1, 1), font_size='12sp')
        signup_btn.bind(on_press=self.signup)
        back_btn = Button(text="Back", background_color=buttonColor, size_hint=(1, 1), font_size='12sp')
        back_btn.bind(on_press=self.back)
        button_row.add_widget(signup_btn)
        button_row.add_widget(back_btn)
        main_layout.add_widget(button_row)

        # Center everything
        container = BoxLayout(orientation='vertical')
        container.add_widget(main_layout)
        self.add_widget(container)

    # Function to handle sign up button press
    def signup(self, instance):
        # Check if username, password, and email are valid
        # If valid, switch to map screen
        # Otherwise, display an error message
        if self.username.text != "" and self.password.text != "" and "@" in self.email.text:
            if (self.username.text in UserDB['usern'].unique()) == False:  # only works if username is not in "UserDB.txt"
                # Display confirmation message
                confirmation_label = Label(text="Sign up successful!", color=(0, 1, 0, 1))
                self.add_widget(confirmation_label)
                # Schedule function to remove the confirmation message after 5 seconds
                Clock.schedule_once(lambda dt: self.remove_widget(confirmation_label), 5)
                # Pause for 3 seconds
                time.sleep(3)
                self.parent.current = "map"

            elif (self.username.text in UserDB['usern'].unique()) == True:
                error_usern = Label(text="Username Taken", color=(1, 0, 0, 1))
                self.add_widget(error_usern)
                # Schedule function to remove the error message after 5 seconds
                Clock.schedule_once(lambda dt: self.remove_widget(error_usern), 3)

            elif (self.email.text in UserDB['email'].unique()) == True:  # TODO user can sign up with existing email, fix
                error_email = Label(text="An account with this email already exists", color=(1, 0, 0, 1))
                self.add_widget(error_email)
                # Schedule function to remove the error message after 5 seconds
                Clock.schedule_once(lambda dt: self.remove_widget(error_email), 3)

        else:
            self.username.text = ""
            self.password.text = ""
            self.email.text = ""
            error_label = Label(text="Please enter valid username, password, and email", color=(1, 0, 0, 1))
            self.add_widget(error_label)
            # Schedule function to remove the error message after 5 seconds
            Clock.schedule_once(lambda dt: self.remove_widget(error_label), 3)

    # Function to handle back button press
    def back(self, instance):
        # Switch to login screen
        self.parent.current = "login"

class NavMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.main_layout.size_hint = (0.8, 0.9)
        self.main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Center everything
        container = BoxLayout(orientation='vertical')
        container.add_widget(self.main_layout)
        self.add_widget(container)
    
    def on_enter(self):
        """Called when the screen is entered - rebuild buttons dynamically"""
        self.main_layout.clear_widgets()
        
        # Button list - much smaller buttons
        button_texts = [
            ("Friends", "friends"),
            ("Events/Trips", "events"),
            ("Groups", "groups"),
            ("Profile/Settings", "profile"),
        ]
        
        # Add admin button only for admin users
        app = App.get_running_app()
        if app and app.current_user and app.current_user.user_type == "admin":
            button_texts.append(("Admin Settings", "admin"))
        
        button_texts.append(("Back", "map"))
        
        for text, screen in button_texts:
            btn = Button(text=text, size_hint=(1, 0.06), background_color=buttonColor, font_size='11sp')
            btn.bind(on_press=lambda x, s=screen: self.switch_screen(s))
            self.main_layout.add_widget(btn)

    def switch_screen(self, screen_name):
        self.parent.current = screen_name

class Friend:
    def __init__(self, name, username, image, xlocation, ylocation):
        self.name = name
        self.username = username
        self.image = image
        self.xlocation = xlocation
        self.ylocation = ylocation

    # Define profile screen

class FProfileScreen(Screen):  # friends profile
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        main_layout.size_hint = (0.9, 0.95)
        main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Title label
        label = Label(text="Friend Profile Screen", font_size='22sp', size_hint=(1, 0.12))
        main_layout.add_widget(label)

        # Load the friends profile image
        fprofile_image = Image(source="josh.jpg", size_hint=(1, 0.6), allow_stretch=True, keep_ratio=True)
        main_layout.add_widget(fprofile_image)

        # Back button - much smaller
        back_btn = Button(text="Back", size_hint=(1, 0.08), font_size='12sp')
        back_btn.bind(on_press=self.back)
        main_layout.add_widget(back_btn)

        # Center everything
        container = BoxLayout(orientation='vertical')
        container.add_widget(main_layout)
        self.add_widget(container)

    # Function to handle back button press
    def back(self, instance):
        # Switch to friends screen
        self.parent.current = "friends"

# Define events screen
class EventsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.main_layout.size_hint = (0.8, 0.7)
        self.main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Title label
        self.label = Label(text="Events", font_size='18sp', size_hint=(1, 0.15))
        self.main_layout.add_widget(self.label)

        # Create a dropdown list (Spinner) for event selection - much smaller
        self.spinner = Spinner(
            text="Select Event",
            values=[],
            size_hint=(1, 0.1),
            font_size='12sp'
        )
        self.spinner.bind(text=self.on_event_select)
        self.main_layout.add_widget(self.spinner)

        # Go to Map button - much smaller
        map_btn = Button(text="Go to Map", size_hint=(1, 0.08), font_size='12sp')
        map_btn.bind(on_press=self.go_to_map)
        self.main_layout.add_widget(map_btn)

        # Back button - much smaller
        back_btn = Button(text="Back to Menu", size_hint=(1, 0.08), font_size='12sp')
        back_btn.bind(on_press=self.back_to_menu)
        self.main_layout.add_widget(back_btn)

        # Center everything
        container = BoxLayout(orientation='vertical')
        container.add_widget(self.main_layout)
        self.add_widget(container)
        
        # Initialize event data
        self.event_db = {}
        self.eventName = None
    
    def on_enter(self):
        """Called when the screen is entered - reload events dynamically"""
        self.load_events()
    
    def load_events(self):
        """Load events from the database and update spinner"""
        self.event_db = self.load_event_db("EventsDB.txt")
        event_names = list(self.event_db.keys())
        self.spinner.values = event_names
        if event_names and self.spinner.text not in event_names:
            self.spinner.text = "Select Event"

    def load_event_db(self, filename):
        """
        Load events from the database file into a dictionary.
        """
        event_db = {}
        try:
            with open(filename, "r") as file:
                for line in file:
                    parts = line.strip().split(";")
                    if len(parts) >= 11:  # eventID;name;map;start;end;desc;coord1;coord2;coord3;coord4;hidden
                        event_id = parts[0]
                        event_name = parts[1]
                        image = parts[2]
                        is_hidden = parts[10] == "true"
                        
                        # Only show non-hidden events to users
                        if not is_hidden:
                            event_db[event_name] = image
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
        return event_db

    def on_event_select(self, spinner, text):
        """
        Update the selected eventName.
        """
        self.eventName = text
        print(f"Selected Event: {self.eventName}")

    def go_to_map(self, instance):
        """
        Switch to the MapScreen and update the map based on the selected eventName.
        """
        if self.eventName:
            # Set app-wide current event
            app = App.get_running_app()
            if app:
                app.current_event = self.eventName
            
            # Access the MapScreen instance from the parent ScreenManager
            map_screen = self.parent.get_screen("map")
            map_screen.set_event_name(self.eventName, self.event_db)
            map_screen.event_db = self.event_db  # Pass the event database
            self.parent.current = "map"
        else:
            print("Please select an event before proceeding.")

    def back_to_menu(self, instance):
        """
        Return to navigation menu.
        """
        self.parent.current = "nav_menu"

# Define the screen manager
sm = ScreenManager(transition=FadeTransition())

# Add all screens to the screen manager
sm.add_widget(LoginScreen(name="login"))
sm.add_widget(SignupScreen(name="signup"))
sm.add_widget(MapScreen(name="map"))
sm.add_widget(NavMenuScreen(name="nav_menu"))
sm.add_widget(FriendsScreen(name="friends"))
sm.add_widget(EventsScreen(name="events"))
sm.add_widget(GroupsScreen(name="groups"))
sm.add_widget(ProfileScreen(name="profile"))
sm.add_widget(FProfileScreen(name="Fprofile"))
sm.add_widget(AdminScreen(name="admin"))


class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None  # This gets set after login
        self.current_event = None  # This gets set when an event is selected

    def build(self):
        self.title = 'Festifriends'
        return sm


# Run the app
if __name__ == '__main__':
    MyApp().run()
