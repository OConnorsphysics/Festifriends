class User:
    def __init__(self, firstn, lastn, usern, email, password, birthday, location=[0,0], user_type="free"):
        self.firstn = firstn
        self.lastn = lastn
        self.usern = usern
        self.email = email
        self.password = password
        self.birthday = birthday
        self.location = location
        self.user_type = user_type  # "admin", "premium", or "free"
        self.squads = {}  # Dictionary: {event_name: squad_id}

    def get_loc(self):
        #self.location =(200, 550) #TODO hardcoded but will be however you get a coordinate from phone gps
        return self.location

    def is_admin(self):
        return self.user_type == "admin"

    def is_premium(self):
        return self.user_type == "premium" or self.user_type == "admin"
    
    def can_have_multiple_squads(self):
        """Check if user can have multiple squads per event (premium feature)"""
        return self.is_premium()
    
    def get_squad_limit_per_event(self):
        """Get the maximum number of squads per event for this user"""
        if self.is_premium():
            return 3  # Premium users can have up to 3 squads per event
        return 1  # Free users can have only 1 squad per event

#self built class to store user info, idk how to implement this yet

class Squad:
    def __init__(self, squad_id, name, max_members, event_name, owner_username):
        self.squad_id = squad_id
        self.name = name
        self.max_members = max_members
        self.event_name = event_name
        self.owner_username = owner_username
        self.members = []

    def add_member(self, member):
        if len(self.members) < self.max_members and member not in self.members:
            self.members.append(member)
            return True
        return False
    
    def remove_member(self, member):
        if member in self.members:
            self.members.remove(member)
            return True
        return False

    def list_members(self):
        return self.members
    
    def get_member_count(self):
        return len(self.members)
    
    def is_full(self):
        return len(self.members) >= self.max_members
