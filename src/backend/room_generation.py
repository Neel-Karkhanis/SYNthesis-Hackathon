import random
import string

# In-memory room store: { code: { "host": str, "users": [...], "movies": [...], "votes": {}, "done": set() } }
rooms = {}


def _generate_code():
    while True:
        code = "".join(random.choices(string.ascii_uppercase, k=6))
        if code not in rooms:
            return code


def create_room(host_name):
    """Create a new room, set the host, and return its join code."""
    code = _generate_code()
    rooms[code] = {
        "host": host_name,
        "users": [host_name],
        "movies": [],
        "votes": {},           # { movie_id: { user: "yes"/"no" } }
        "done": set(),         # users who finished voting
        "voting_started": False,
    }
    return code


def join_room(code, display_name):
    """
    Add a user to an existing room.
    Returns the room dict on success, raises ValueError if room not found
    or display name is already taken.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")
    room = rooms[code]
    if display_name in room["users"]:
        raise ValueError(f"Display name '{display_name}' is already taken in this room.")
    room["users"].append(display_name)
    return room


def is_host(code, display_name):
    """Return True if display_name is the host of the room."""
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")
    return rooms[code]["host"] == display_name


def get_room(code):
    """Return the room dict for a given code, or None if it doesn't exist."""
    return rooms.get(code.upper())
