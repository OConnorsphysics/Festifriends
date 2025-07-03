from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from Utilities.Notifications import send_notification  # Adjust path as needed

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        # Refresh profile info every time the screen is shown
        self.clear_widgets()  # Clear old widgets before adding new ones
        self.update_profile_ui()

    def update_profile_ui(self):
        # Get the current user from the app instance
        current_user = App.get_running_app().current_user

        # Title label
        title_label = Label(text="Profile", font_size='24sp', size_hint=(1, 0.1))

        # Check if user is logged in
        if not current_user:
            details_text = "No user logged in"
        else:
            # Create formatted multiline user detail text
            details_text = f"""
Name: {current_user.firstn} {current_user.lastn}
Username: {current_user.usern}
Email: {current_user.email}
Birthday: {current_user.birthday}
Location: {current_user.location}
User Type: {current_user.user_type}
"""

        # Label to display user details
        user_details = Label(text=details_text, halign='left', valign='top', size_hint=(1, 0.7))
        user_details.bind(size=user_details.setter('text_size'))  # Ensure text wraps properly

        # Create a back button
        back_btn = Button(text="Back to Menu", size_hint=(1, 0.08), font_size='12sp')
        back_btn.bind(on_press=self.back)

        # Layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(title_label)
        layout.add_widget(user_details)
        layout.add_widget(back_btn)

        # Add the layout to the screen
        self.add_widget(layout)

    def back(self, instance):
        send_notification("Back to Menu", "You returned from your profile.")
        self.parent.current = "nav_menu"
