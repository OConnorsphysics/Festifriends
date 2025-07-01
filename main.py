
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

        # Create a grid layout with two rows and one column
        layout = GridLayout(cols=1)

        # Create a label for the app name
        label = Label(text="Location Sharing App", font_size='20sp')

        # Create a text input for username
        self.username = TextInput(hint_text="Username", multiline=False)

        # Create a text input for password
        self.password = TextInput(hint_text="Password", password=True, multiline=False)

        # Create a login button
        login_btn = Button(text="Login", size_hint=(None, None), size=(150, 50), background_color=buttonColor)
        login_btn.bind(on_press=self.login)

        # Create a sign up button
        signup_btn = Button(text="Sign Up", size_hint=(None, None), size=(150, 50), background_color=buttonColor)
        signup_btn.bind(on_press=self.signup)

        # forgot password button
        forgot_btn = Button(text="Forgot Password?", size_hint=(None, None), size=(150, 50),
                            background_color=buttonColor)
        forgot_btn.bind(on_press=self.forgot)

        # Add all widgets to the layout
        layout.add_widget(label)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_btn)
        layout.add_widget(signup_btn)
        layout.add_widget(forgot_btn)

        # Add the layout to the login screen
        self.add_widget(layout)

    # Function to handle login button press


    def login(self, instance):
        if self.username.text == "admin" and self.password.text == "admin":
            # Set a default admin user object
            self.current_user = User("Admin", "User", "admin", "admin@email.com", "admin", "01/01/2000", [0, 0], [])
            App.get_running_app().current_user = self.current_user
            self.parent.current = "map"
        elif self.password.text != "" and check_password(self.username.text, self.password.text):
            self.current_user = set_current_user(self.username.text)

            if not self.current_user:
                send_notification("Login Error", "User data could not be loaded.")
                return

            if not self.current_user.squad:             #Only assign a default squad if user doesn't already have one
                test_squad = Squad("DefaultSquad", 4)   #TODO assigns default squad to all users, doesnt load from DB
                test_squad.add_member(self.current_user.usern)  # Add the current user to the squad
                self.current_user.squad = test_squad

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

        # Create a grid layout with two rows and one column
        layout = GridLayout(rows=5)

        # Create a label for the app name
        label = Label(text="Location Sharing App", font_size='20sp')

        # Create a text input for username
        self.username = TextInput(hint_text="Username", multiline=False)

        # Create a text input for password
        self.password = TextInput(hint_text="Password", password=True, multiline=False)

        # Create a text input for email
        self.email = TextInput(hint_text="Email", multiline=False)

        # TODO link the user inout to a creation of a user class instance in user_classes.py
        # not sure if I should do it before or after the sign up button
        # current_user = User(firstn, lastn, usern, email, birthday, location)
        # current_user = User("Liam", "O'Connor", "LOC", "oconnor@gmail.com", "17/02/1996", [200, 200])

        # Create a sign up button
        signup_btn = Button(text="Sign Up", size_hint=(None, None), size=(100, 50), background_color=buttonColor)
        signup_btn.bind(on_press=self.signup)

        # Create a back button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50), background_color=buttonColor)
        back_btn.bind(on_press=self.back)

        # Add all widgets to the layout
        # layout.add_widget(label)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.email)
        layout.add_widget(signup_btn)
        layout.add_widget(back_btn)

        # Add the layout to the sign up screen
        self.add_widget(layout)

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

        # Create a grid layout with four rows and one column
        layout = GridLayout(rows=5)

        # Create buttons for each menu option
        friends_btn = Button(text="Friends", size_hint=(None, None), size=(500, 100), background_color=buttonColor)
        events_btn = Button(text="Events/Trips", size_hint=(None, None), size=(500, 100), background_color=buttonColor)
        groups_btn = Button(text="Groups", size_hint=(None, None), size=(500, 100), background_color=buttonColor)
        profile_btn = Button(text="Profile/Settings", size_hint=(None, None), size=(500, 100),
                             background_color=buttonColor)
        back_btn = Button(text="Back", size_hint=(None, None), size=(500, 100), background_color=buttonColor)

        # Bind each button to a function that switches to the corresponding screen
        friends_btn.bind(on_press=lambda x: self.switch_screen("friends"))
        events_btn.bind(on_press=lambda x: self.switch_screen("events"))
        groups_btn.bind(on_press=lambda x: self.switch_screen("groups"))
        profile_btn.bind(on_press=lambda x: self.switch_screen("profile"))
        back_btn.bind(on_press=lambda x: self.switch_screen("map"))

        # Add all buttons to the layout
        layout.add_widget(friends_btn)
        layout.add_widget(events_btn)
        layout.add_widget(groups_btn)
        layout.add_widget(profile_btn)
        layout.add_widget(back_btn)

        # Add the layout to the navigation menu screen
        self.add_widget(layout)

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

        # Create a label for the screen
        label = Label(text="Friend Profile Screen", size_hint=(None, None))

        # Load the friends profile image
        fprofile_image = Image(source="josh.jpg", size_hint=(1, 0.9))

        # Create a back button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
        back_btn.bind(on_press=self.back)

        # Create a layout and add widgets
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(label)
        layout.add_widget(back_btn)

        # Add the friend profile image to the layout
        layout.add_widget(fprofile_image)

        # Add the layout to the events screen
        self.add_widget(layout)

    # Function to handle back button press
    def back(self, instance):
        # Switch to friends screen
        self.parent.current = "friends"

class FriendsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a label for the screen
        label = Label(text="Friends Screen")
        # Create a grid layout with four rows and one column
        layout = GridLayout(rows=4, cols=1)

        # Create buttons for each friend option
        friend1_btn = Button(text="Friend Name 1", size_hint=(None, None), size=(500, 100))
        friend2_btn = Button(text="Friend Name 2", size_hint=(None, None), size=(500, 100))

        # Bind each button to a function that switches to the corresponding friend's profile screen
        friend1_btn.bind(on_press=lambda x: self.switch_screen("Fprofile"))
        friend2_btn.bind(on_press=lambda x: self.switch_screen("Fprofile"))

        # Add all friend buttons to the layout
        layout.add_widget(friend1_btn)
        layout.add_widget(friend2_btn)

        # Create a back button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
        back_btn.bind(on_press=self.back)

        # Create a layout and add widgets
        # layout = BoxLayout(orientation='vertical')
        layout.add_widget(label)
        layout.add_widget(back_btn)

        # Add the layout to the friends screen
        self.add_widget(layout)

    def switch_screen(self, screen_name):  # allows the switch screen option, to switch to a user profile of a friend
        self.parent.current = screen_name

    # Function to handle back button press
    def back(self, instance):
        # Switch to map screen
        self.parent.current = "nav_menu"

# Define events screen
class EventsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load events from the database
        self.event_db = self.load_event_db("eventsDB.txt")
        self.eventName = None  # Variable to store the selected event

        # Create the layout
        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        # Create a label for the screen
        label = Label(text="Events Screen", font_size=24, size_hint=(1, 0.2))

        # Create a dropdown list (Spinner) for event selection
        self.spinner = Spinner(
            text="Select Event",
            values=list(self.event_db.keys()),
            size_hint=(1, 0.2)
        )
        self.spinner.bind(text=self.on_event_select)

        # Back button to navigate to MapScreen
        back_btn = Button(text="Go to Map", size_hint=(None, None), size=(150, 50))
        back_btn.bind(on_press=self.go_to_map)

        # Add widgets to the layout
        layout.add_widget(label)
        layout.add_widget(self.spinner)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def load_event_db(self, filename):
        """
        Load events from the database file into a dictionary.
        """
        event_db = {}
        try:
            with open(filename, "r") as file:
                for line in file:
                    event, image = line.strip().split(";")
                    event_db[event] = image
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
            # Access the MapScreen instance from the parent ScreenManager
            map_screen = self.parent.get_screen("map")
            map_screen.set_event_name(self.eventName, self.event_db)
            map_screen.event_db = self.event_db  # Pass the event database
            self.parent.current = "map"
        else:
            print("Please select an event before proceeding.")

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
sm.add_widget(ProfileScreen( name="profile"))
sm.add_widget(FProfileScreen(name="Fprofile"))


class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None  # This gets set after login

    def build(self):
        self.title = 'Festifriends'
        return sm


# Run the app
if __name__ == '__main__':
    MyApp().run()
