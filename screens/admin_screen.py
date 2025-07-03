from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
import pandas as pd
import os

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        main_layout.size_hint = (0.95, 0.95)
        main_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        # Title
        title = Label(text="Admin Settings", font_size='24sp', size_hint=(1, 0.1))
        main_layout.add_widget(title)
        
        # Events section
        events_label = Label(text="Events Management", font_size='18sp', size_hint=(1, 0.08))
        main_layout.add_widget(events_label)
        
        # Add new event button
        add_event_btn = Button(text="Add New Event", size_hint=(1, 0.08), font_size='14sp')
        add_event_btn.bind(on_press=self.show_add_event_popup)
        main_layout.add_widget(add_event_btn)
        
        # Manage meetup points button
        manage_meetups_btn = Button(text="Manage Meetup Points", size_hint=(1, 0.08), font_size='14sp')
        manage_meetups_btn.bind(on_press=self.show_meetup_management)
        main_layout.add_widget(manage_meetups_btn)
        
        # Refresh events button
        refresh_btn = Button(text="Refresh Events List", size_hint=(1, 0.08), font_size='14sp')
        refresh_btn.bind(on_press=self.refresh_events)
        main_layout.add_widget(refresh_btn)
        
        # Events list
        self.events_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.events_layout.bind(minimum_height=self.events_layout.setter('height'))
        
        # Scroll view for events
        scroll_view = ScrollView(size_hint=(1, 0.6))
        scroll_view.add_widget(self.events_layout)
        main_layout.add_widget(scroll_view)
        
        # Back button
        back_btn = Button(text="Back to Menu", size_hint=(1, 0.08), font_size='14sp')
        back_btn.bind(on_press=self.back_to_menu)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
        self.load_events()
    
    def on_enter(self):
        """Called when the screen is entered - refresh events list"""
        self.load_events()
    
    def refresh_events(self, instance):
        """Refresh the events list"""
        self.load_events()
        print("Events list refreshed")
    
    def load_events(self):
        """Load events from EventsDB.txt and display them"""
        self.events_layout.clear_widgets()
        
        try:
            # Read the extended EventsDB.txt
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 11:  # eventID;name;map;start;end;desc;coord1;coord2;coord3;coord4;hidden
                            event_id = parts[0]
                            event_name = parts[1]
                            map_file = parts[2]
                            start_date = parts[3]
                            end_date = parts[4]
                            description = parts[5]
                            is_hidden = parts[10] == "true"
                            
                            # Create event display
                            event_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
                            
                            # Event info
                            info_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
                            id_label = Label(text=f"ID: {event_id} | {event_name}", font_size='14sp')
                            date_label = Label(text=f"{start_date} to {end_date}", font_size='12sp')
                            status_label = Label(text=f"Hidden: {'Yes' if is_hidden else 'No'}", font_size='12sp')
                            info_layout.add_widget(id_label)
                            info_layout.add_widget(date_label)
                            info_layout.add_widget(status_label)
                            
                            # Buttons
                            button_layout = BoxLayout(orientation='horizontal', size_hint=(0.3, 1))
                            edit_btn = Button(text="Edit", size_hint=(0.5, 1), font_size='12sp')
                            edit_btn.bind(on_press=lambda x, eid=event_id: self.edit_event(eid))
                            delete_btn = Button(text="Delete", size_hint=(0.5, 1), font_size='12sp')
                            delete_btn.bind(on_press=lambda x, eid=event_id: self.delete_event(eid))
                            
                            button_layout.add_widget(edit_btn)
                            button_layout.add_widget(delete_btn)
                            
                            event_box.add_widget(info_layout)
                            event_box.add_widget(button_layout)
                            self.events_layout.add_widget(event_box)
        except Exception as e:
            print(f"Error loading events: {e}")
    
    def show_add_event_popup(self, instance):
        """Show popup to add a new event"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Event name input
        name_input = TextInput(hint_text="Event Name", multiline=False, size_hint=(1, 0.2))
        content.add_widget(name_input)
        
        # Map file input
        map_input = TextInput(hint_text="Map Image File (e.g., shambMap2023.PNG)", multiline=False, size_hint=(1, 0.2))
        content.add_widget(map_input)
        
        # Date range inputs
        date_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        start_date = TextInput(hint_text="Start Date (MM/DD/YYYY)", multiline=False, size_hint=(0.5, 1))
        end_date = TextInput(hint_text="End Date (MM/DD/YYYY)", multiline=False, size_hint=(0.5, 1))
        date_layout.add_widget(start_date)
        date_layout.add_widget(end_date)
        content.add_widget(date_layout)
        
        # Description input
        desc_input = TextInput(hint_text="Event Description", multiline=True, size_hint=(1, 0.3))
        content.add_widget(desc_input)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        save_btn = Button(text="Save", size_hint=(0.5, 1))
        cancel_btn = Button(text="Cancel", size_hint=(0.5, 1))
        
        def save_event(instance):
            if name_input.text and map_input.text:
                self.add_event(
                    name_input.text,
                    map_input.text,
                    start_date.text,
                    end_date.text,
                    desc_input.text
                )
                popup.dismiss()
                self.load_events()
        
        save_btn.bind(on_press=save_event)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)
        
        popup = Popup(title="Add New Event", content=content, size_hint=(0.8, 0.8))
        popup.open()
    
    def add_event(self, name, map_file, start_date, end_date, description):
        """Add a new event to EventsDB.txt"""
        try:
            # Generate new event ID
            next_id = self.get_next_event_id()
            
            # Create the extended event entry with ID and hidden status
            event_line = f"{next_id};{name};{map_file};{start_date};{end_date};{description};0,0;800,0;800,600;0,600;false\n"
            
            with open("EventsDB.txt", "a") as file:
                file.write(event_line)
            
            print(f"Added event: {name} with ID: {next_id}")
        except Exception as e:
            print(f"Error adding event: {e}")
    
    def get_next_event_id(self):
        """Get the next available event ID"""
        try:
            max_id = 0
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 1 and parts[0].isdigit():
                            max_id = max(max_id, int(parts[0]))
            return max_id + 1
        except Exception as e:
            print(f"Error getting next ID: {e}")
            return 1
    
    def edit_event(self, event_id):
        """Show popup to edit an existing event"""
        # Load event data
        event_data = self.load_event_data(event_id)
        if not event_data:
            return
        
        # Create edit form
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Event ID (read-only)
        id_label = Label(text=f"Event ID: {event_id}", size_hint=(1, 0.1))
        content.add_widget(id_label)
        
        # Event name input
        name_input = TextInput(text=event_data['name'], hint_text="Event Name", multiline=False, size_hint=(1, 0.1))
        content.add_widget(name_input)
        
        # Map file input
        map_input = TextInput(text=event_data['map_file'], hint_text="Map Image File", multiline=False, size_hint=(1, 0.1))
        content.add_widget(map_input)
        
        # Date range inputs
        date_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        start_date = TextInput(text=event_data['start_date'], hint_text="Start Date (MM/DD/YYYY)", multiline=False, size_hint=(0.5, 1))
        end_date = TextInput(text=event_data['end_date'], hint_text="End Date (MM/DD/YYYY)", multiline=False, size_hint=(0.5, 1))
        date_layout.add_widget(start_date)
        date_layout.add_widget(end_date)
        content.add_widget(date_layout)
        
        # Description input
        desc_input = TextInput(text=event_data['description'], hint_text="Event Description", multiline=True, size_hint=(1, 0.2))
        content.add_widget(desc_input)
        
        # Hidden status
        hidden_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        hidden_layout.add_widget(Label(text="Hidden:", size_hint=(0.3, 1)))
        hidden_spinner = Spinner(text="No" if not event_data['hidden'] else "Yes", values=["Yes", "No"], size_hint=(0.7, 1))
        hidden_layout.add_widget(hidden_spinner)
        content.add_widget(hidden_layout)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        save_btn = Button(text="Save Changes", size_hint=(0.5, 1))
        cancel_btn = Button(text="Cancel", size_hint=(0.5, 1))
        
        def save_changes(instance):
            # Validate inputs
            if not self.validate_event_inputs(name_input.text, start_date.text, end_date.text):
                return
            
            # Show confirmation popup
            self.show_edit_confirmation(
                event_id, name_input.text, map_input.text, start_date.text, 
                end_date.text, desc_input.text, hidden_spinner.text == "Yes",
                event_data  # Original data for revert
            )
            popup.dismiss()
        
        save_btn.bind(on_press=save_changes)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)
        
        popup = Popup(title="Edit Event", content=content, size_hint=(0.8, 0.8))
        popup.open()
    
    def load_event_data(self, event_id):
        """Load event data by ID"""
        try:
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 11 and parts[0] == str(event_id):
                            return {
                                'name': parts[1],
                                'map_file': parts[2],
                                'start_date': parts[3],
                                'end_date': parts[4],
                                'description': parts[5],
                                'coord1': parts[6],
                                'coord2': parts[7],
                                'coord3': parts[8],
                                'coord4': parts[9],
                                'hidden': parts[10] == "true"
                            }
            return None
        except Exception as e:
            print(f"Error loading event data: {e}")
            return None
    
    def validate_event_inputs(self, name, start_date, end_date):
        """Validate event input fields"""
        if not name.strip():
            print("Error: Event name is required")
            return False
        
        # Basic date validation (MM/DD/YYYY format)
        import re
        date_pattern = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(date_pattern, start_date) or not re.match(date_pattern, end_date):
            print("Error: Dates must be in MM/DD/YYYY format")
            return False
        
        return True
    
    def show_edit_confirmation(self, event_id, name, map_file, start_date, end_date, description, hidden, original_data):
        """Show confirmation popup for edit changes"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        content.add_widget(Label(text="Are you sure you want to save these changes?", size_hint=(1, 0.3)))
        
        # Show changes summary
        changes = []
        if name != original_data['name']:
            changes.append(f"Name: {original_data['name']} → {name}")
        if map_file != original_data['map_file']:
            changes.append(f"Map: {original_data['map_file']} → {map_file}")
        if start_date != original_data['start_date']:
            changes.append(f"Start: {original_data['start_date']} → {start_date}")
        if end_date != original_data['end_date']:
            changes.append(f"End: {original_data['end_date']} → {end_date}")
        if hidden != original_data['hidden']:
            changes.append(f"Hidden: {'Yes' if original_data['hidden'] else 'No'} → {'Yes' if hidden else 'No'}")
        
        if changes:
            changes_text = "\n".join(changes)
            content.add_widget(Label(text=f"Changes:\n{changes_text}", size_hint=(1, 0.4)))
        else:
            content.add_widget(Label(text="No changes detected", size_hint=(1, 0.4)))
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        confirm_btn = Button(text="Confirm Changes", size_hint=(0.5, 1))
        revert_btn = Button(text="Revert Changes", size_hint=(0.5, 1))
        
        def confirm_changes(instance):
            self.save_event_changes(event_id, name, map_file, start_date, end_date, description, hidden)
            confirmation_popup.dismiss()
        
        def revert_changes(instance):
            # Revert to original data
            self.save_event_changes(event_id, original_data['name'], original_data['map_file'], 
                                  original_data['start_date'], original_data['end_date'], 
                                  original_data['description'], original_data['hidden'])
            confirmation_popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_changes)
        revert_btn.bind(on_press=revert_changes)
        
        button_layout.add_widget(confirm_btn)
        button_layout.add_widget(revert_btn)
        content.add_widget(button_layout)
        
        confirmation_popup = Popup(title="Confirm Changes", content=content, size_hint=(0.7, 0.6))
        confirmation_popup.open()
    
    def show_meetup_management(self, instance):
        """Show meetup points management popup"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        content.add_widget(Label(text="Meetup Points Management", font_size='18sp', size_hint=(1, 0.1)))
        
        # Event selection
        event_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        event_layout.add_widget(Label(text="Select Event:", size_hint=(0.3, 1)))
        
        # Get list of events for dropdown
        events = self.get_event_list()
        event_spinner = Spinner(text="Choose Event", values=events, size_hint=(0.7, 1))
        event_layout.add_widget(event_spinner)
        content.add_widget(event_layout)
        
        # Meetup points list
        meetup_label = Label(text="Meetup Points:", font_size='14sp', size_hint=(1, 0.1))
        content.add_widget(meetup_label)
        
        # Scrollable meetup list
        self.meetup_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.meetup_layout.bind(minimum_height=self.meetup_layout.setter('height'))
        
        scroll_view = ScrollView(size_hint=(1, 0.4))
        scroll_view.add_widget(self.meetup_layout)
        content.add_widget(scroll_view)
        
        # Add new meetup button
        add_meetup_btn = Button(text="Add New Meetup Point", size_hint=(1, 0.1))
        add_meetup_btn.bind(on_press=lambda x: self.add_meetup_point(event_spinner.text))
        content.add_widget(add_meetup_btn)
        
        # Close button
        close_btn = Button(text="Close", size_hint=(1, 0.1))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        # Load meetup points when event is selected
        def on_event_select(spinner, text):
            if text != "Choose Event":
                self.load_meetup_points(text)
        
        event_spinner.bind(text=on_event_select)
        
        popup = Popup(title="Meetup Management", content=content, size_hint=(0.8, 0.8))
        popup.open()
    
    def get_event_list(self):
        """Get list of event names for dropdown"""
        events = []
        try:
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 2:
                            events.append(parts[1])  # Event name
        except Exception as e:
            print(f"Error getting event list: {e}")
        return events
    
    def load_meetup_points(self, event_name):
        """Load and display meetup points for an event"""
        self.meetup_layout.clear_widgets()
        
        try:
            # Get event ID from name
            event_id = self.get_event_id_by_name(event_name)
            if not event_id:
                return
            
            if os.path.exists("MeetupDB.txt"):
                with open("MeetupDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 5 and parts[0] == str(event_id):
                            meetup_name = parts[1]
                            location = parts[2]
                            description = parts[3]
                            image_path = parts[4]
                            
                            # Create meetup display
                            meetup_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
                            
                            # Meetup info
                            info_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
                            name_label = Label(text=f"{meetup_name} - {location}", font_size='12sp')
                            desc_label = Label(text=description, font_size='10sp')
                            icon_label = Label(text=f"Icon: {image_path}", font_size='9sp')
                            info_layout.add_widget(name_label)
                            info_layout.add_widget(desc_label)
                            info_layout.add_widget(icon_label)
                            
                            # Delete button
                            delete_btn = Button(text="Delete", size_hint=(0.3, 1), font_size='10sp')
                            delete_btn.bind(on_press=lambda x, mid=event_id, mname=meetup_name: self.delete_meetup_point(mid, mname))
                            
                            meetup_box.add_widget(info_layout)
                            meetup_box.add_widget(delete_btn)
                            self.meetup_layout.add_widget(meetup_box)
        except Exception as e:
            print(f"Error loading meetup points: {e}")
    
    def get_event_id_by_name(self, event_name):
        """Get event ID from event name"""
        try:
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 2 and parts[1] == event_name:
                            return parts[0]
        except Exception as e:
            print(f"Error getting event ID: {e}")
        return None
    
    def add_meetup_point(self, event_name):
        """Add a new meetup point"""
        if event_name == "Choose Event":
            print("Please select an event first")
            return
        
        event_id = self.get_event_id_by_name(event_name)
        if not event_id:
            return
        
        # Simple add meetup popup
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        content.add_widget(Label(text="Add New Meetup Point", font_size='16sp'))
        
        name_input = TextInput(hint_text="Meetup Name", multiline=False, size_hint=(1, 0.15))
        content.add_widget(name_input)
        
        location_input = TextInput(hint_text="Location (x,y)", multiline=False, size_hint=(1, 0.15))
        content.add_widget(location_input)
        
        desc_input = TextInput(hint_text="Description", multiline=True, size_hint=(1, 0.2))
        content.add_widget(desc_input)
        
        icon_input = TextInput(text="redpin.jpg", hint_text="Icon Image File (e.g., redpin.jpg, food_icon.png)", multiline=False, size_hint=(1, 0.15))
        content.add_widget(icon_input)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        save_btn = Button(text="Save", size_hint=(0.5, 1))
        cancel_btn = Button(text="Cancel", size_hint=(0.5, 1))
        
        def save_meetup(instance):
            name = name_input.text.strip()
            location = location_input.text.strip()
            description = desc_input.text.strip()
            icon_path = icon_input.text.strip()
            
            if name and location and description and icon_path:
                # Parse location to validate format
                try:
                    x, y = map(int, location.split(','))
                    location_str = f"{x},{y}"
                except:
                    print("Invalid location format. Use x,y")
                    return
                
                meetup_line = f"{event_id};{name};{location_str};{description};{icon_path}\n"
                with open("MeetupDB.txt", "a") as file:
                    file.write(meetup_line)
                print(f"Added meetup: {name} with icon: {icon_path}")
                add_popup.dismiss()
                self.load_meetup_points(event_name)  # Refresh list
            else:
                print("Please fill in all required fields")
        
        save_btn.bind(on_press=save_meetup)
        cancel_btn.bind(on_press=lambda x: add_popup.dismiss())
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        content.add_widget(button_layout)
        
        add_popup = Popup(title="Add Meetup Point", content=content, size_hint=(0.6, 0.6))
        add_popup.open()
    
    def delete_meetup_point(self, event_id, meetup_name):
        """Delete a meetup point"""
        try:
            with open("MeetupDB.txt", "r") as file:
                lines = file.readlines()
            
            with open("MeetupDB.txt", "w") as file:
                for line in lines:
                    parts = line.strip().split(";")
                    if len(parts) >= 2 and not (parts[0] == str(event_id) and parts[1] == meetup_name):
                        file.write(line)
            
            print(f"Deleted meetup: {meetup_name}")
            # Refresh the meetup list
            event_name = self.get_event_name_by_id(event_id)
            if event_name:
                self.load_meetup_points(event_name)
        except Exception as e:
            print(f"Error deleting meetup point: {e}")
    
    def get_event_name_by_id(self, event_id):
        """Get event name from event ID"""
        try:
            if os.path.exists("EventsDB.txt"):
                with open("EventsDB.txt", "r") as file:
                    for line in file:
                        parts = line.strip().split(";")
                        if len(parts) >= 2 and parts[0] == str(event_id):
                            return parts[1]
        except Exception as e:
            print(f"Error getting event name: {e}")
        return None
    
    def save_event_changes(self, event_id, name, map_file, start_date, end_date, description, hidden):
        """Save event changes to EventsDB.txt"""
        try:
            # Read all events
            with open("EventsDB.txt", "r") as file:
                lines = file.readlines()
            
            # Find and update the specific event
            with open("EventsDB.txt", "w") as file:
                for line in lines:
                    parts = line.strip().split(";")
                    if len(parts) >= 11 and parts[0] == str(event_id):
                        # Update the event line
                        updated_line = f"{event_id};{name};{map_file};{start_date};{end_date};{description};{parts[6]};{parts[7]};{parts[8]};{parts[9]};{str(hidden).lower()}\n"
                        file.write(updated_line)
                    else:
                        file.write(line)
            
            print(f"Updated event: {name} (ID: {event_id})")
            self.load_events()  # Refresh the display
        except Exception as e:
            print(f"Error saving event changes: {e}")
    
    def delete_event(self, event_id):
        """Delete an event from EventsDB.txt"""
        try:
            # Read all events
            with open("EventsDB.txt", "r") as file:
                lines = file.readlines()
            
            # Write back all events except the one to delete
            with open("EventsDB.txt", "w") as file:
                for line in lines:
                    parts = line.strip().split(";")
                    if len(parts) >= 1 and parts[0] != str(event_id):
                        file.write(line)
            
            # Also delete associated meetup points
            self.delete_event_meetups(event_id)
            
            print(f"Deleted event ID: {event_id}")
            self.load_events()
        except Exception as e:
            print(f"Error deleting event: {e}")
    
    def delete_event_meetups(self, event_id):
        """Delete all meetup points for an event"""
        try:
            if os.path.exists("MeetupDB.txt"):
                with open("MeetupDB.txt", "r") as file:
                    lines = file.readlines()
                
                with open("MeetupDB.txt", "w") as file:
                    for line in lines:
                        parts = line.strip().split(";")
                        if len(parts) >= 1 and parts[0] != str(event_id):
                            file.write(line)
        except Exception as e:
            print(f"Error deleting meetup points: {e}")
    
    def back_to_menu(self, instance):
        """Return to navigation menu"""
        self.parent.current = "nav_menu" 