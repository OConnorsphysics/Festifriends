#main GTP3 assisted, different totally

# Import necessary modules
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
#from kivy.uix.mapview import MapView
from kivy_garden.mapview import MapView
from kivy.config import Config
from kivy.core.window import Window

# Set size and orientation of the app window
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')
Window.size = (400, 600)
Window.clearcolor = (1, 1, 1, 1)


# Define screen manager for navigating between screens
class ScreenManagement(ScreenManager):
    pass


# Define login screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a grid layout with two rows and one column
        layout = GridLayout(rows=2, cols=3) #TODO changing cols=1 to 3 works but looks bad

        # Create a label for the app name
        label = Label(text="Location Sharing App", font_size='20sp')

        # Create a text input for username
        self.username = TextInput(hint_text="Username", multiline=False)

        # Create a text input for password
        self.password = TextInput(hint_text="Password", password=True, multiline=False)

        # Create a login button
        login_btn = Button(text="Login", size_hint=(None, None), size=(100, 50))
        login_btn.bind(on_press=self.login)

        # Create a sign up button
        signup_btn = Button(text="Sign Up", size_hint=(None, None), size=(100, 50))
        signup_btn.bind(on_press=self.signup)

        # Add all widgets to the layout
        layout.add_widget(label)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_btn)
        layout.add_widget(signup_btn)

        # Add the layout to the login screen
        self.add_widget(layout)

    # Function to handle login button press
    def login(self, instance):
        # Check if username and password are correct
        # If correct, switch to map screen
        # Otherwise, display an error message
        if self.username.text == "admin" and self.password.text == "admin":
            self.parent.current = "map"
        else:
            self.username.text = ""
            self.password.text = ""
            error_label = Label(text="Incorrect username or password")
            self.add_widget(error_label)

    # Function to handle sign up button press
    def signup(self, instance):
        # Switch to sign up screen
        self.parent.current = "signup"

# Define sign up screen
class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a grid layout with two rows and one column
        layout = GridLayout(rows=2, cols=3)

        # Create a label for the app name
        label = Label(text="Location Sharing App", font_size='20sp')

        # Create a text input for username
        self.username = TextInput(hint_text="Username", multiline=False)

        # Create a text input for password
        self.password = TextInput(hint_text="Password", password=True, multiline=False)

        # Create a text input for email
        self.email = TextInput(hint_text="Email", multiline=False)

        # Create a sign up button
        signup_btn = Button(text="Sign Up", size_hint=(None, None), size=(100, 50))
        signup_btn.bind(on_press=self.signup)

        # Create a back button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
        back_btn.bind(on_press=self.back)

        # Add all widgets to the layout
        layout.add_widget(label)
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
            self.parent.current = "map"
        else:
            self.username.text = ""
            self.password.text = ""
            self.email.text = ""
            error_label = Label(text="Please enter valid username, password, and email")
            self.add_widget(error_label)

        # Function to handle back button press

    def back(self, instance):
        # Switch to login screen
        self.parent.current = "login"

        # Create a text input for email
        self.email = TextInput(hint_text="Email", multiline=False)

        # Create a sign up button
        signup_btn = Button(text="Sign Up", size_hint=(None, None), size=(100, 50))
        signup_btn.bind(on_press=self.signup)

        # Create a back button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
        back_btn.bind(on_press=self.back)

        # Add all widgets to the layout
        #layout.add_widget(label)
        #layout.add_widget(self.username)
        #layout.add_widget(self.password)           #These 7 lines gave erros so were commented out, idk what they do...
        #layout.add_widget(self.email)
        #layout.add_widget(signup_btn)
        #layout.add_widget(back_btn)

        # Add the layout to the sign up screen
        #self.add_widget(layout)

# Define map screen
class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a box layout with one row and two columns
        layout = BoxLayout(orientation='vertical')

        # Create a map view
        mapview = MapView()

        # Create a navigation button
        nav_btn = Button(text="Navigation Menu", size_hint=(None, None), size=(100, 50))
        nav_btn.bind(on_press=self.show_nav_menu)

        # Add the map view and navigation button to the layout
        layout.add_widget(mapview)
        layout.add_widget(nav_btn)

        # Add the layout to the map screen
        self.add_widget(layout)

    # Function to show navigation menu
    def show_nav_menu(self, instance):
        # Switch to navigation menu screen
        self.parent.current = "nav_menu"

# Define navigation menu screen
class NavMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a grid layout with four rows and one column
        layout = GridLayout(rows=4, cols=1)

        # Create buttons for each menu option
        friends_btn = Button(text="Friends", size_hint=(None, None), size=(100, 50))
        events_btn = Button(text="Events/Trips", size_hint=(None, None), size=(100, 50))
        groups_btn = Button(text="Groups", size_hint=(None, None), size=(100, 50))
        profile_btn = Button(text="Profile/Settings", size_hint=(None, None), size=(100, 50))

        # Bind each button to a function that switches to the corresponding screen
        friends_btn.bind(on_press=lambda x: self.switch_screen("friends"))
        events_btn.bind(on_press=lambda x: self.switch_screen("events"))
        groups_btn.bind(on_press=lambda x: self.switch_screen("groups"))
        profile_btn.bind(on_press=lambda x: self.switch_screen("profile"))

        # Add all buttons to the
        layout.add_widget(friends_btn)
        layout.add_widget(events_btn)
        layout.add_widget(groups_btn)
        layout.add_widget(profile_btn)

        # Add the layout to the navigation menu screen
        self.add_widget(layout)

        # Function to switch to the selected screen

    def switch_screen(self, screen_name):
        self.parent.current = screen_name

    # Define friends screen
class FriendsScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            # Create a label for the screen
            label = Label(text="Friends Screen")

            # Create a back button
            back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
            back_btn.bind(on_press=self.back)

            # Create a layout and add widgets
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(label)
            layout.add_widget(back_btn)

            # Add the layout to the friends screen
            self.add_widget(layout)

        # Function to handle back button press
        def back(self, instance):
            # Switch to map screen
            self.parent.current = "map"

    # Define events screen
class EventsScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            # Create a label for the screen
            label = Label(text="Events Screen")

            # Create a back button
            back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
            back_btn.bind(on_press=self.back)

            # Create a layout and add widgets
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(label)
            layout.add_widget(back_btn)

            # Add the layout to the events screen
            self.add_widget(layout)

        # Function to handle back button press
        def back(self, instance):
            # Switch to map screen
            self.parent.current = "map"

    # Define groups screen
class GroupsScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            # Create a label for the screen
            label = Label(text="Groups Screen")

            # Create a back button
            back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
            back_btn.bind(on_press=self.back)

            # Create a layout and add widgets
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(label)
            layout.add_widget(back_btn)

            # Add the layout to the groups screen
            self.add_widget(layout)

        # Function to handle back button press
        def back(self, instance):
            # Switch to map screen
            self.parent.current = "map"

    # Define profile screen

class ProfileScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            # Create a label for the screen
            label = Label(text="Profile Screen")

            # Create a back button
            back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
            back_btn.bind(on_press=self.back)

            # Create a layout and add widgets
            layout = BoxLayout(orientation='vertical')
            layout.add_widget(label)
            layout.add_widget(back_btn)

            # Add the layout to the profile screen
            self.add_widget(layout)

        # Function to handle back button press
        def back(self, instance):
            # Switch to map screen
            self.parent.current = "map"

    # Define the screen manager
# Define the screen manager
sm = ScreenManager()

# Add all screens to the screen manager
sm.add_widget(LoginScreen(name="login"))
sm.add_widget(SignupScreen(name="signup"))
sm.add_widget(MapScreen(name="map"))
sm.add_widget(NavMenuScreen(name="nav_menu"))
sm.add_widget(FriendsScreen(name="friends"))
sm.add_widget(EventsScreen(name="events"))
sm.add_widget(GroupsScreen(name="groups"))
sm.add_widget(ProfileScreen(name="profile"))

# Create the app class
class MyApp(App):
    def build(self):
        # Return the screen manager
        return sm

# Run the app
if __name__ == '__main__':
    MyApp().run()

