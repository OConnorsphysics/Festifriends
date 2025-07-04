from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from user_classes import Squad
from kivy.app import App
import os
from datetime import datetime
from screens.find_member_popup import FindMemberPopup


# Define groups screen
class GroupsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.main_layout.size_hint = (0.9, 0.95)
        self.main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Title
        title_label = Label(text="Squads", font_size='24sp', size_hint=(1, 0.08))
        self.main_layout.add_widget(title_label)

        # Current event display
        self.event_label = Label(text="Event: None", font_size='16sp', size_hint=(1, 0.06))
        self.main_layout.add_widget(self.event_label)

        # Squad selection (for premium users)
        self.squad_selection_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        self.squad_selection_layout.add_widget(Label(text="Squad:", size_hint=(0.3, 1)))
        self.squad_spinner = Spinner(
            text="Select Squad",
            values=[],
            size_hint=(0.7, 1)
        )
        self.squad_spinner.bind(text=self.on_squad_select)
        self.squad_selection_layout.add_widget(self.squad_spinner)
        self.main_layout.add_widget(self.squad_selection_layout)

        # Current squad info
        self.squad_info_label = Label(text="No squad selected", font_size='14sp', size_hint=(1, 0.06))
        self.main_layout.add_widget(self.squad_info_label)

        # Squad members list
        members_label = Label(text="Squad Members:", font_size='16sp', size_hint=(1, 0.06))
        self.main_layout.add_widget(members_label)

        # Scrollable members list
        self.members_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.members_layout.bind(minimum_height=self.members_layout.setter('height'))
        
        self.members_scroll_view = ScrollView(size_hint=(1, 0.4))
        self.members_scroll_view.add_widget(self.members_layout)
        self.main_layout.add_widget(self.members_scroll_view)

        # Add member section
        add_member_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        self.member_username_input = TextInput(
            hint_text="Enter friend's username", 
            multiline=False, 
            size_hint=(0.7, 1)
        )
        add_member_btn = Button(
            text="Add to Squad", 
            size_hint=(0.3, 1),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        add_member_btn.bind(on_press=self.add_member)
        add_member_layout.add_widget(self.member_username_input)
        add_member_layout.add_widget(add_member_btn)
        self.main_layout.add_widget(add_member_layout)

        # Create new squad section (for premium users)
        self.create_squad_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        self.new_squad_name_input = TextInput(
            hint_text="New squad name", 
            multiline=False, 
            size_hint=(0.7, 1)
        )
        create_squad_btn = Button(
            text="Create Squad", 
            size_hint=(0.3, 1),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        create_squad_btn.bind(on_press=self.create_squad)
        self.create_squad_layout.add_widget(self.new_squad_name_input)
        self.create_squad_layout.add_widget(create_squad_btn)
        self.main_layout.add_widget(self.create_squad_layout)

        # Meetup location section
        meetup_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=10)
        self.meetup_x = TextInput(hint_text="X coordinate", multiline=False, size_hint=(0.3, 1))
        self.meetup_y = TextInput(hint_text="Y coordinate", multiline=False, size_hint=(0.3, 1))
        set_meetup_btn = Button(text="Set Meetup", size_hint=(0.4, 1))
        set_meetup_btn.bind(on_press=self.set_meetup_location)
        meetup_layout.add_widget(self.meetup_x)
        meetup_layout.add_widget(self.meetup_y)
        meetup_layout.add_widget(set_meetup_btn)
        self.main_layout.add_widget(meetup_layout)

        # Back button
        back_btn = Button(text="Back to Menu", size_hint=(1, 0.08), font_size='14sp')
        back_btn.bind(on_press=self.back_to_menu)
        self.main_layout.add_widget(back_btn)

        # Center everything
        container = BoxLayout(orientation='vertical')
        container.add_widget(self.main_layout)
        self.add_widget(container)

        # Initialize variables
        self.current_event = None
        self.current_squad_id = None
        self.user_squads = {}

    def on_enter(self):
        """Called when screen is entered - load current event and squads"""
        self.load_current_event()
        self.update_ui_for_user_type()

    def load_current_event(self):
        """Load the current event from the map screen"""
        app = App.get_running_app()
        if app and hasattr(app, 'current_event'):
            self.current_event = app.current_event
        else:
            # Default to first available event
            events = self.get_available_events()
            if events:
                self.current_event = events[0]
        
        if self.current_event:
            self.event_label.text = f"Event: {self.current_event}"
            self.load_user_squads()
        else:
            self.event_label.text = "Event: None"

    def get_available_events(self):
        """Get list of available events from EventsDB.txt"""
        events = []
        try:
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 11 and parts[10] != "true":  # Not hidden
                            events.append(parts[1])  # Event name
        except Exception as e:
            print(f"Error loading events: {e}")
        return events

    def update_ui_for_user_type(self):
        """Update UI based on user type (premium vs free)"""
        app = App.get_running_app()
        if not app or not app.current_user:
            return
        
        current_user = app.current_user
        
        # Show/hide squad selection for premium users
        if current_user.can_have_multiple_squads():
            self.squad_selection_layout.opacity = 1
            self.create_squad_layout.opacity = 1
        else:
            self.squad_selection_layout.opacity = 0.5
            self.create_squad_layout.opacity = 0.5

    def load_user_squads(self):
        """Load user's squads for the current event"""
        app = App.get_running_app()
        if not app or not app.current_user or not self.current_event:
            return
        
        current_user = app.current_user
        self.user_squads = self.get_user_squads(current_user.usern, self.current_event)
        
        # Update squad spinner
        squad_names = [squad['name'] for squad in self.user_squads.values()]
        if squad_names:
            self.squad_spinner.values = squad_names
            if self.squad_spinner.text not in squad_names:
                self.squad_spinner.text = squad_names[0]
        else:
            self.squad_spinner.values = []
            self.squad_spinner.text = "No squads"
        
        self.load_squad_members()

    def get_user_squads(self, username, event_name):
        """Get user's squads for a specific event from SquadsDB.txt"""
        squads = {}
        try:
            if os.path.exists("SquadsDB.txt"):
                with open("SquadsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 6 and parts[1] == username and parts[2] == event_name:
                            squad_id = parts[0]
                            squads[squad_id] = {
                                'id': squad_id,
                                'name': parts[3],
                                'max_members': int(parts[4]),
                                'created_date': parts[5]
                            }
        except Exception as e:
            print(f"Error loading user squads: {e}")
        return squads

    def on_squad_select(self, spinner, text):
        """Handle squad selection"""
        if text == "No squads":
            return
        
        # Find the selected squad
        for squad_id, squad_info in self.user_squads.items():
            if squad_info['name'] == text:
                self.current_squad_id = squad_id
                break
        
        self.load_squad_members()  # Refresh immediately when squad changes

    def load_squad_members(self):
        """Load and display squad members"""
        self.members_layout.clear_widgets()
        
        if not self.current_squad_id:
            self.squad_info_label.text = "No squad selected"
            return
        
        squad_info = self.user_squads.get(self.current_squad_id, {})
        self.squad_info_label.text = f"Squad: {squad_info.get('name', 'Unknown')} ({len(self.get_squad_members(self.current_squad_id))}/{squad_info.get('max_members', 4)} members)"
        
        members = self.get_squad_members(self.current_squad_id)
        
        if not members:
            no_members_label = Label(
                text="No members in this squad yet.\nAdd friends to get started!",
                size_hint_y=None,
                height=80,
                halign='center'
            )
            self.members_layout.add_widget(no_members_label)
            return
        
        # Load user data for display
        user_data = self.load_user_data()
        
        for member_username in members:
            member_info = user_data.get(member_username, {})
            member_name = f"{member_info.get('firstname', 'Unknown')} {member_info.get('lastname', 'User')}"
            
            # Create member row
            member_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
            
            # Member info
            info_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
            name_label = Label(
                text=member_name, 
                font_size='14sp',
                size_hint=(1, 0.6),
                halign='left'
            )
            username_label = Label(
                text=f"@{member_username}", 
                font_size='10sp',
                size_hint=(1, 0.4),
                halign='left'
            )
            info_layout.add_widget(name_label)
            info_layout.add_widget(username_label)
            
            # Remove button
            remove_btn = Button(
                text="Remove", 
                size_hint=(0.15, 1),
                background_color=(0.8, 0.2, 0.2, 1),
                font_size='10sp'
            )
            remove_btn.bind(on_press=lambda x, username=member_username: self.remove_member(username))

            # Find Me button
            find_me_btn = Button(
                text="Find Me",
                size_hint=(0.15, 1),
                background_color=(0.2, 0.6, 1, 1),
                font_size='10sp'
            )
            find_me_btn.bind(on_press=lambda x, username=member_username: FindMemberPopup(member_name=username).open())
            
            member_row.add_widget(info_layout)
            member_row.add_widget(remove_btn)
            member_row.add_widget(find_me_btn)
            self.members_layout.add_widget(member_row)

    def get_squad_members(self, squad_id):
        """Get members of a squad from SquadMembersDB.txt"""
        members = []
        try:
            if os.path.exists("SquadMembersDB.txt"):
                with open("SquadMembersDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 2 and parts[0] == squad_id:
                            members.append(parts[1])
        except Exception as e:
            print(f"Error loading squad members: {e}")
        return members

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

    def add_member(self, instance):
        """Add a member to the current squad"""
        if not self.current_squad_id:
            self.show_error_popup("Please select a squad first")
            return
        
        member_username = self.member_username_input.text.strip()
        
        if not member_username:
            self.show_error_popup("Please enter a username")
            return
        
        app = App.get_running_app()
        if not app or not app.current_user:
            self.show_error_popup("User session error")
            return
        
        current_user = app.current_user
        
        # Check if user is a friend
        if not self.are_friends(current_user.usern, member_username):
            self.show_error_popup(f"{member_username} is not in your friends list")
            return
        
        # Check if already in squad
        if member_username in self.get_squad_members(self.current_squad_id):
            self.show_error_popup(f"{member_username} is already in this squad")
            return
        
        # Check squad capacity
        squad_info = self.user_squads.get(self.current_squad_id, {})
        current_members = len(self.get_squad_members(self.current_squad_id))
        max_members = squad_info.get('max_members', 4)
        
        if current_members >= max_members:
            self.show_error_popup(f"Squad is full! Max members: {max_members}")
            return
        
        # Add member
        if self.add_member_to_squad(self.current_squad_id, member_username):
            self.member_username_input.text = ""
            self.load_squad_members()  # Refresh immediately
            self.show_success_popup(f"Added {member_username} to squad")
        else:
            self.show_error_popup("Failed to add member")

    def remove_member(self, member_username):
        """Remove a member from the current squad"""
        if not self.current_squad_id:
            return
        
        if self.remove_member_from_squad(self.current_squad_id, member_username):
            self.load_squad_members()  # Refresh immediately
            self.show_success_popup(f"Removed {member_username} from squad")
        else:
            self.show_error_popup("Failed to remove member")

    def create_squad(self, instance):
        """Create a new squad"""
        app = App.get_running_app()
        if not app or not app.current_user or not self.current_event:
            self.show_error_popup("Cannot create squad")
            return
        
        current_user = app.current_user
        squad_name = self.new_squad_name_input.text.strip()
        
        if not squad_name:
            self.show_error_popup("Please enter a squad name")
            return
        
        # Check if user can create more squads
        current_squads = len(self.user_squads)
        max_squads = current_user.get_squad_limit_per_event()
        
        if current_squads >= max_squads:
            self.show_error_popup(f"You can only have {max_squads} squad(s) per event")
            return
        
        # Create squad
        squad_id = self.create_squad_in_db(current_user.usern, self.current_event, squad_name)
        if squad_id:
            self.new_squad_name_input.text = ""
            self.load_user_squads()  # Refresh immediately
            self.show_success_popup(f"Created squad: {squad_name}")
        else:
            self.show_error_popup("Failed to create squad")

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

    def add_member_to_squad(self, squad_id, member_username):
        """Add member to squad in SquadMembersDB.txt"""
        try:
            with open("SquadMembersDB.txt", "a") as file:
                file.write(f"{squad_id};{member_username}\n")
            return True
        except Exception as e:
            print(f"Error adding member to squad: {e}")
            return False

    def remove_member_from_squad(self, squad_id, member_username):
        """Remove member from squad in SquadMembersDB.txt"""
        try:
            with open("SquadMembersDB.txt", "r") as file:
                lines = file.readlines()
            
            with open("SquadMembersDB.txt", "w") as file:
                for line in lines:
                    parts = line.strip().split(";")
                    if len(parts) >= 2 and not (parts[0] == squad_id and parts[1] == member_username):
                        file.write(line)
            return True
        except Exception as e:
            print(f"Error removing member from squad: {e}")
            return False

    def create_squad_in_db(self, username, event_name, squad_name):
        """Create a new squad in SquadsDB.txt"""
        try:
            # Generate squad ID
            squad_id = self.get_next_squad_id()
            
            with open("SquadsDB.txt", "a") as file:
                date_created = datetime.now().strftime("%Y-%m-%d")
                file.write(f"{squad_id};{username};{event_name};{squad_name};4;{date_created}\n")
            return squad_id
        except Exception as e:
            print(f"Error creating squad: {e}")
            return None

    def get_next_squad_id(self):
        """Get the next available squad ID"""
        max_id = 0
        try:
            if os.path.exists("SquadsDB.txt"):
                with open("SquadsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 1:
                            try:
                                squad_id = int(parts[0])
                                max_id = max(max_id, squad_id)
                            except ValueError:
                                continue
        except Exception as e:
            print(f"Error getting next squad ID: {e}")
        return str(max_id + 1)

    def set_meetup_location(self, instance):
        """Set meetup location for the current squad"""
        try:
            x = int(self.meetup_x.text)
            y = int(self.meetup_y.text)
            
            if not self.current_squad_id:
                self.show_error_popup("Please select a squad first")
                return
            
            # Save meetup location to database
            if self.save_meetup_location(self.current_squad_id, x, y):
                self.show_success_popup(f"Meetup location set to: ({x}, {y})")
                
                # Refresh meetup locations on map screen immediately
                map_screen = self.parent.get_screen("map")
                if hasattr(map_screen, 'refresh_meetup_locations'):
                    map_screen.refresh_meetup_locations()
            else:
                self.show_error_popup("Failed to save meetup location")
                
        except ValueError:
            self.show_error_popup("Please enter valid numeric coordinates")

    def save_meetup_location(self, squad_id, x, y):
        """Save meetup location to database"""
        try:
            # Update or create meetup location entry
            locations = {}
            if os.path.exists("SquadMeetupLocationsDB.txt"):
                with open("SquadMeetupLocationsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 3:
                            locations[parts[0]] = (parts[1], parts[2])
            
            locations[squad_id] = (str(x), str(y))
            
            with open("SquadMeetupLocationsDB.txt", "w") as file:
                for squad, coords in locations.items():
                    file.write(f"{squad};{coords[0]};{coords[1]}\n")
            return True
        except Exception as e:
            print(f"Error saving meetup location: {e}")
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
        # Refresh meetup locations on map screen before returning
        map_screen = self.parent.get_screen("map")
        if hasattr(map_screen, 'refresh_meetup_locations'):
            map_screen.refresh_meetup_locations()
        
        self.parent.current = "nav_menu"
