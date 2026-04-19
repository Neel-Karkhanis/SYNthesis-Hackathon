from room_generation import rooms


def swipe(code, display_name, movie_id, vote):
    """
    Record a yes/no vote for a movie.
    vote must be "yes" or "no".
    Raises ValueError for invalid room, unknown user, unknown movie, or bad vote value.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")

    room = rooms[code]

    if display_name not in room["users"]:
        raise ValueError(f"User '{display_name}' is not in room '{code}'.")

    if display_name in room["done"]:
        raise ValueError(f"User '{display_name}' has already finished voting.")

    movie_ids = {m["id"] for m in room["movies"]}
    if movie_id not in movie_ids:
        raise ValueError(f"Movie ID {movie_id} is not in room '{code}'.")

    if vote not in ("yes", "no"):
        raise ValueError("Vote must be 'yes' or 'no'.")

    if movie_id not in room["votes"]:
        room["votes"][movie_id] = {}

    room["votes"][movie_id][display_name] = vote
    room["voting_started"] = True
    room["results_cache"] = None


def finish_voting(code, display_name):
    """
    Mark a user as done voting (they've swiped on every movie).
    Raises ValueError if the user hasn't voted on all movies yet.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")

    room = rooms[code]

    if display_name not in room["users"]:
        raise ValueError(f"User '{display_name}' is not in room '{code}'.")

    movie_ids = {m["id"] for m in room["movies"]}
    voted_ids = {mid for mid, votes in room["votes"].items() if display_name in votes}

    if not movie_ids.issubset(voted_ids):
        missing = len(movie_ids - voted_ids)
        raise ValueError(f"'{display_name}' still has {missing} movie(s) left to vote on.")

    room["done"].add(display_name)
    room["results_cache"] = None


def get_voting_status(code):
    """
    Return how many users have finished voting vs total users in the room.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")

    room = rooms[code]
    return {
        "done": len(room["done"]),
        "total": len(room["users"]),
        "finished": len(room["done"]) == len(room["users"]) and len(room["users"]) > 0,
        "started": room.get("started", False),
    }
