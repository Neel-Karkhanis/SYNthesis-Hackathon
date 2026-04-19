import random
from room_generation import rooms


def get_results(code):
    """
    Tally yes votes for every movie in the room and return a ranked list.
    The movie with the most yes votes is the winner.

    Each entry in the returned list:
        { "movie": {...}, "yes": int, "no": int, "winner": bool }

    Raises ValueError if the room doesn't exist or voting isn't finished yet.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")

    room = rooms[code]

    if room.get("results_cache") is not None:
        return room["results_cache"]

    if not room["users"]:
        raise ValueError("Room has no users.")
    if not room["movies"]:
        raise ValueError("Room has no movies.")
    if room["done"] != set(room["users"]):
        still_voting = set(room["users"]) - room["done"]
        raise ValueError(f"Voting not finished. Still waiting on: {', '.join(still_voting)}")

    movies = {m["id"]: m for m in room["movies"]}
    votes = room["votes"]

    tally = []
    for movie_id, movie in movies.items():
        movie_votes = votes.get(movie_id, {})
        yes_count = sum(1 for v in movie_votes.values() if v == "yes")
        no_count = sum(1 for v in movie_votes.values() if v == "no")
        tally.append({"movie": movie, "yes": yes_count, "no": no_count})

    total_users = len(room["users"])
    tally.sort(key=lambda x: x["yes"], reverse=True)

    # A movie wins outright if everyone voted yes — randomly pick one winner
    unanimous = [e for e in tally if e["yes"] == total_users]
    if unanimous:
        winner = random.choice(unanimous)
        for entry in tally:
            entry["winner"] = entry is winner
        room["results_cache"] = tally
        return tally

    # Fallback: fewest no votes wins
    min_no = min(e["no"] for e in tally)
    for entry in tally:
        entry["winner"] = entry["no"] == min_no

    room["results_cache"] = tally
    return tally
