from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from user_classes import Squad
from kivy.app import App


# Define groups screen
class GroupsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Temporary variable for the squad name (replace with dynamic logic as needed)
        current_squad_temporary = "HorseyCrew3"

        # Create a squad instance
        self.squad = Squad(current_squad_temporary, 4)

        # UI Elements
        label = Label(text="Groups Screen", font_size=24)

        # Display current squad name
        self.currentSquad = Label(text="Current Squad: " + current_squad_temporary, size_hint=(1, 0.1))

        # Squad members list
        self.currSqMembers = Label(text="Members: " + ", ".join(self.squad.list_members()), size_hint=(1, 0.1))

        # Input for new member
        self.friend = TextInput(hint_text="Enter Member Username", multiline=False, size_hint=(1, 0.1))

        # Inputs for meet-up coordinates
        self.meetup_x = TextInput(hint_text="X coordinate", multiline=False, size_hint=(1, 0.1))
        self.meetup_y = TextInput(hint_text="Y coordinate", multiline=False, size_hint=(1, 0.1))

        # Button to set the location
        self.set_meetup_button = Button(text="Set Meet-Up Location", size_hint=(1, 0.1))
        self.set_meetup_button.bind(on_press=self.set_meetup_location)


        # Button to add a member
        addSquad_btn = Button(text="Add to Squad", size_hint=(None, None), size=(150, 50))
        addSquad_btn.bind(on_press=self.addMember)

        # Back button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50))
        back_btn.bind(on_press=self.back)

        # Layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(label)
        layout.add_widget(self.currentSquad)
        layout.add_widget(self.currSqMembers)
        layout.add_widget(self.friend)
        layout.add_widget(addSquad_btn)
        layout.add_widget(back_btn)
        layout.add_widget(self.meetup_x)
        layout.add_widget(self.meetup_y)
        layout.add_widget(self.set_meetup_button)
        # Add layout to the screen
        self.add_widget(layout)

    def set_meetup_location(self, instance):
        try:
            x = int(self.meetup_x.text)
            y = int(self.meetup_y.text)
            App.get_running_app().meetup_location = (x, y)
            print(f"Meet-up location set to: {x}, {y}")
        except ValueError:
            print("Invalid input: Please enter numeric coordinates.")


    def addMember(self, instance):
        """
        Add a member to the squad and update the member list display.
        """
        new_member = self.friend.text.strip()

        if new_member:  # Ensure input is not empty
            if self.squad.add_member(new_member):
                # Update the member list display
                self.currSqMembers.text = "Members: " + ", ".join(self.squad.list_members())
                self.friend.text = ""  # Clear input field
            else:
                # Squad is full
                self.currSqMembers.text = "Squad is full! Max members: " + str(self.squad.max_members)
        else:
            # Invalid input
            self.currSqMembers.text = "Please enter a valid username!"

    def back(self, instance):
        self.parent.current = "map"
        print("Back button pressed")
