import csv
import ast
from user_classes import User, Squad

# ✅ Check if a username and password match what's in the database
def check_password(username, password):
    try:
        with open("UserDB.txt", newline='') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if row[2].lower() == username.lower() and row[4] == password:
                    return True
    except Exception as e:
        print("Error checking password:", e)
    return False

# ✅ Load the User object from the text file
def set_current_user(username):
    try:
        with open("UserDB.txt", newline='') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                print("Checking row:", row[2])  #debug line TODO remove once this works %100
                if row[2].lower() == username.lower():
                    print("Raw location value:", row[6])
                    # Parse location like: "[200, 300]" → [200, 300]
                    loc_string = row[6].strip("[]")
                    location = [int(val.strip()) for val in loc_string.split(",")]
                    print("Raw friend list:", row[7])
                    friendList = ast.literal_eval(row[7]) if row[7] else []
                    squad_name = str(row[8]).strip() if len(row) > 8 and row[8].strip() != "" else None

                    user = User(
                        firstn=row[0],
                        lastn=row[1],
                        usern=row[2],
                        email=row[3],
                        password=row[4],
                        birthday=row[5],
                        location=location,
                        friendList=friendList
                    )

                    if squad_name:
                        print("Creating squad with name:", squad_name)
                        squad = Squad(squad_name, max_members=4)
                        squad.add_member(user.usern)
                        user.squad = squad

                    return user

        print("User not found.")
        return None

    except Exception as e:
        print("Error loading user:", e)
        return None


# ✅ Local test (optional)
if __name__ == '__main__':
    testusername = "loc"
    testpass = "lem"

    print("Password check:", check_password(testusername, testpass))
    user = set_current_user(testusername)
    if user:
        print(f"Loaded user: {user.firstn} {user.lastn}, Birthday: {user.birthday}, Squad: {user.squad.name if user.squad else 'None'}")
