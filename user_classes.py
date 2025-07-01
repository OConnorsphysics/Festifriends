
class User:
    def __init__(self, firstn, lastn, usern, email, password, birthday, location=[0,0], friendList=[], squad =None):
        self.firstn = firstn
        self.lastn = lastn
        self.usern = usern
        self.email = email
        self.password = password
        self.birthday = birthday
        self.location = location
        self.friendList = friendList    #list of friends usernames, allows pulling user info from userDB.txt
        self.squad = squad

    def get_loc(self):
        #self.location =(200, 550) #TODO hardcoded but will be however you get a coordinate from phone gps
        return self.location
#self built class to store user info, idk how to implement this yet

class Squad:
    def __init__(self, name, max_members):
        self.name = name
        self.max_members = max_members
        self.members = []

    def add_member(self, member):
        if len(self.members) < self.max_members:
            self.members.append(member)
            return True
        return False

    def list_members(self):
        print(self.members)
        return self.members
