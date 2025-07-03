from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.app import App
import os
from datetime import datetime

class FriendsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.main_layout.size_hint = (0.9, 0.95)
        self.main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Title
        title_label = Label(text="Friends", font_size='24sp', size_hint=(1, 0.08))
        self.main_layout.add_widget(title_label)

        # Add friend section
        add_friend_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        self.friend_username_input = TextInput(
            hint_text="Enter friend's username", 
            multiline=False, 
            size_hint=(0.7, 1)
        )
        add_btn = Button(
            text="Add Friend", 
            size_hint=(0.3, 1),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        add_btn.bind(on_press=self.add_friend)
        add_friend_layout.add_widget(self.friend_username_input)
        add_friend_layout.add_widget(add_btn)
        self.main_layout.add_widget(add_friend_layout)

        # Friends list section
        friends_label = Label(text="Your Friends:", font_size='18sp', size_hint=(1, 0.06))
        self.main_layout.add_widget(friends_label)

        # Scrollable friends list
        self.friends_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.friends_layout.bind(minimum_height=self.friends_layout.setter('height'))
        
        self.scroll_view = ScrollView(size_hint=(1, 0.7))
        self.scroll_view.add_widget(self.friends_layout)
        self.main_layout.add_widget(self.scroll_view)

        # Back button
        back_btn = Button(text="Back to Menu", size_hint=(1, 0.08), font_size='14sp')
        back_btn.bind(on_press=self.back_to_menu)
        self.main_layout.add_widget(back_btn)

        # Center everything
        container = BoxLayout(orientation='vertical')
        container.add_widget(self.main_layout)
        self.add_widget(container)

    def on_enter(self):
        """Called when screen is entered - load friends list"""
        self.load_friends()

    def load_friends(self):
        """Load and display the current user's friends"""
        self.friends_layout.clear_widgets()
        
        app = App.get_running_app()
        if not app or not app.current_user:
            return
        
        current_user = app.current_user
        friends = self.get_user_friends(current_user.usern)
        
        if not friends:
            # Show "no friends" message
            no_friends_label = Label(
                text="You haven't added any friends yet.\nAdd friends by entering their username above!",
                size_hint_y=None,
                height=100,
                halign='center'
            )
            self.friends_layout.add_widget(no_friends_label)
            return
        
        # Load user data for display
        user_data = self.load_user_data()
        
        for friend_username in friends:
            friend_info = user_data.get(friend_username, {})
            friend_name = f"{friend_info.get('firstname', 'Unknown')} {friend_info.get('lastname', 'User')}"
            
            # Create friend row
            friend_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
            
            # Friend info
            info_layout = BoxLayout(orientation='vertical', size_hint=(0.8, 1))
            name_label = Label(
                text=friend_name, 
                font_size='16sp',
                size_hint=(1, 0.6),
                halign='left'
            )
            username_label = Label(
                text=f"@{friend_username}", 
                font_size='12sp',
                size_hint=(1, 0.4),
                halign='left'
            )
            info_layout.add_widget(name_label)
            info_layout.add_widget(username_label)
            
            # Remove button
            remove_btn = Button(
                text="Remove", 
                size_hint=(0.2, 1),
                background_color=(0.8, 0.2, 0.2, 1),
                font_size='12sp'
            )
            remove_btn.bind(on_press=lambda x, username=friend_username: self.remove_friend(username))
            
            friend_row.add_widget(info_layout)
            friend_row.add_widget(remove_btn)
            self.friends_layout.add_widget(friend_row)

    def get_user_friends(self, username):
        """Get list of friends for a user from FriendsDB.txt"""
        friends = []
        try:
            if os.path.exists("FriendsDB.txt"):
                with open("FriendsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 2 and parts[0] == username:
                            friends.append(parts[1])
        except Exception as e:
            print(f"Error loading friends: {e}")
        return friends

    def load_user_data(self):
        """Load all user data from UserDB.txt"""
        user_data = {}
        try:
            if os.path.exists("UserDB.txt"):
                with open("UserDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 4:
                            username = parts[2]
                            user_data[username] = {
                                'firstname': parts[0],
                                'lastname': parts[1],
                                'email': parts[3]
                            }
        except Exception as e:
            print(f"Error loading user data: {e}")
        return user_data

    def add_friend(self, instance):
        """Add a new friend"""
        friend_username = self.friend_username_input.text.strip()
        
        if not friend_username:
            self.show_error_popup("Please enter a username")
            return
        
        app = App.get_running_app()
        if not app or not app.current_user:
            self.show_error_popup("User session error")
            return
        
        current_user = app.current_user
        
        # Validate username exists
        if not self.user_exists(friend_username):
            self.show_error_popup(f"User '{friend_username}' not found")
            return
        
        # Prevent adding yourself
        if friend_username == current_user.usern:
            self.show_error_popup("You cannot add yourself as a friend")
            return
        
        # Check if already friends
        if self.are_friends(current_user.usern, friend_username):
            self.show_error_popup(f"You are already friends with {friend_username}")
            return
        
        # Add friend
        if self.add_friend_to_db(current_user.usern, friend_username):
            self.friend_username_input.text = ""
            self.load_friends()  # Refresh the list immediately
            self.show_success_popup(f"Added {friend_username} as a friend!")
        else:
            self.show_error_popup("Failed to add friend")

    def remove_friend(self, friend_username):
        """Remove a friend"""
        app = App.get_running_app()
        if not app or not app.current_user:
            return
        
        current_user = app.current_user
        
        if self.remove_friend_from_db(current_user.usern, friend_username):
            self.load_friends()  # Refresh the list immediately
            self.show_success_popup(f"Removed {friend_username} from friends")
        else:
            self.show_error_popup("Failed to remove friend")

    def user_exists(self, username):
        """Check if a user exists in UserDB.txt"""
        try:
            if os.path.exists("UserDB.txt"):
                with open("UserDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 3 and parts[2] == username:
                            return True
        except Exception as e:
            print(f"Error checking user existence: {e}")
        return False

    def are_friends(self, user1, user2):
        """Check if two users are friends"""
        try:
            if os.path.exists("FriendsDB.txt"):
                with open("FriendsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 2 and parts[0] == user1 and parts[1] == user2:
                            return True
        except Exception as e:
            print(f"Error checking friendship: {e}")
        return False

    def add_friend_to_db(self, user_username, friend_username):
        """Add friend relationship to FriendsDB.txt"""
        try:
            with open("FriendsDB.txt", "a") as file:
                date_added = datetime.now().strftime("%Y-%m-%d")
                file.write(f"{user_username};{friend_username};{date_added}\n")
            return True
        except Exception as e:
            print(f"Error adding friend to database: {e}")
            return False

    def remove_friend_from_db(self, user_username, friend_username):
        """Remove friend relationship from FriendsDB.txt"""
        try:
            with open("FriendsDB.txt", "r") as file:
                lines = file.readlines()
            
            with open("FriendsDB.txt", "w") as file:
                for line in lines:
                    parts = line.strip().split(";")
                    if len(parts) >= 2 and not (parts[0] == user_username and parts[1] == friend_username):
                        file.write(line)
            return True
        except Exception as e:
            print(f"Error removing friend from database: {e}")
            return False

    def show_error_popup(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=20)
        content.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint=(1, 0.3))
        popup = Popup(title="Error", content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def show_success_popup(self, message):
        """Show success popup"""
        content = BoxLayout(orientation='vertical', padding=20)
        content.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint=(1, 0.3))
        popup = Popup(title="Success", content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def back_to_menu(self, instance):
        """Return to navigation menu"""
        self.parent.current = "nav_menu" 