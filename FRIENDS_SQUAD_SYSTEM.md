# Friends and Squad System Implementation

## Overview
This document describes the new friends and squad system implemented for the Festifriends app, which provides comprehensive friend management and event-specific squad creation capabilities.

## Database Structure

### 1. FriendsDB.txt
Stores friend relationships between users.
```
user_username;friend_username;date_added
loc;Dix;2024-01-01
loc;Jane;2024-01-01
...
```

### 2. SquadsDB.txt
Stores squad information with event-specific squads.
```
squad_id;user_username;event_name;squad_name;max_members;created_date
1;loc;Shambhala 2025;OConnorClan;4;2024-01-01
2;Dix;Shambhala 2025;HorseyCrew3;4;2024-01-01
...
```

### 3. SquadMembersDB.txt
Stores squad member relationships.
```
squad_id;member_username
1;loc
1;Jane
1;Tom
...
```

### 4. SquadMeetupLocationsDB.txt
Stores meetup locations for each squad.
```
squad_id;x_coordinate;y_coordinate
1;400;300
2;500;400
...
```

## Key Features

### Friends System
- **Add Friends**: Users can add friends by entering their username
- **Remove Friends**: Users can remove friends from their list
- **Validation**: 
  - Username must exist in UserDB
  - Cannot add yourself as a friend
  - Cannot add duplicate friends
- **Scrollable List**: Supports hundreds of friends with scrollable interface
- **Real-time Updates**: Changes are saved immediately to database

### Squad System
- **Event-Specific**: Squads are tied to specific events
- **Premium Features**: 
  - Free users: 1 squad per event
  - Premium users: Up to 3 squads per event
- **Squad Management**:
  - Create new squads (premium users)
  - Add friends to squads
  - Remove members from squads
  - Set meetup locations
- **Member Validation**:
  - Only friends can be added to squads
  - Squad capacity limits (default 4 members)
  - No duplicate members

## User Interface

### Friends Screen (`screens/friends_screen.py`)
- **Add Friend Section**: Text input + "Add Friend" button
- **Friends List**: Scrollable list showing:
  - Friend's full name
  - Username (@username)
  - Remove button for each friend
- **Error Handling**: Popup messages for validation errors
- **Success Feedback**: Confirmation popups for successful actions

### Groups Screen (`screens/group_screen.py`)
- **Event Display**: Shows current event name
- **Squad Selection**: Dropdown for premium users to select squad
- **Squad Info**: Shows squad name and member count
- **Members List**: Scrollable list of squad members with remove buttons
- **Add Member**: Text input + "Add to Squad" button
- **Create Squad**: Text input + "Create Squad" button (premium users)
- **Meetup Location**: X/Y coordinate inputs + "Set Meetup" button

## User Types and Permissions

### Free Users
- Can add/remove friends
- Can create 1 squad per event
- Can add friends to their squad
- Can set meetup locations

### Premium Users
- All free user features
- Can create up to 3 squads per event
- Squad selection dropdown for multiple squads
- Enhanced squad management capabilities

### Admin Users
- All premium user features
- Additional admin capabilities (separate admin screen)

## Technical Implementation

### Updated Classes

#### User Class (`user_classes.py`)
```python
class User:
    def __init__(self, firstn, lastn, usern, email, password, birthday, location=[0,0], user_type="free"):
        # Removed friendList and squad fields
        self.squads = {}  # Dictionary: {event_name: squad_id}
    
    def can_have_multiple_squads(self):
        return self.is_premium()
    
    def get_squad_limit_per_event(self):
        return 3 if self.is_premium() else 1
```

#### Squad Class (`user_classes.py`)
```python
class Squad:
    def __init__(self, squad_id, name, max_members, event_name, owner_username):
        self.squad_id = squad_id
        self.event_name = event_name
        self.owner_username = owner_username
        # ... other fields
```

### Database Operations
- **Atomic Operations**: All database changes are atomic
- **Error Handling**: Comprehensive try/catch blocks
- **Validation**: Input validation before database operations
- **Immediate Persistence**: Changes saved immediately

### Performance Considerations
- **Scrollable Lists**: Efficient rendering for large friend lists
- **Lazy Loading**: User data loaded only when needed
- **Caching**: User data cached during screen sessions
- **Optimized Queries**: Efficient database lookups

## Usage Examples

### Adding a Friend
1. Navigate to Friends screen
2. Enter friend's username in text field
3. Click "Add Friend"
4. System validates username exists
5. System checks for duplicates
6. Friend added to database
7. List refreshes automatically

### Creating a Squad
1. Navigate to Groups screen
2. Enter squad name in "New squad name" field
3. Click "Create Squad"
4. System validates user permissions
5. Squad created in database
6. Squad appears in dropdown

### Adding Member to Squad
1. Select squad from dropdown (if multiple)
2. Enter friend's username
3. Click "Add to Squad"
4. System validates friendship
5. System checks squad capacity
6. Member added to squad
7. Member list refreshes

## Error Handling

### Common Error Messages
- "User 'username' not found"
- "You cannot add yourself as a friend"
- "You are already friends with username"
- "username is not in your friends list"
- "Squad is full! Max members: 4"
- "You can only have X squad(s) per event"

### Validation Rules
- Username must exist in UserDB
- Cannot add self as friend
- Cannot add duplicate friends
- Only friends can be added to squads
- Squad capacity limits enforced
- Premium features restricted to premium users

## Future Enhancements
- Friend request system (two-way friendships)
- Squad invitations
- Squad member permissions
- Squad chat functionality
- Friend activity status
- Squad meetup notifications 