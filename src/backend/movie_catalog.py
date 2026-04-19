import requests
from room_generation import rooms

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def initialize_catalog(code, api_key, use_premade=True):
    """
    Called right after create_room().
    use_premade=True  → fills the room with 20 popular movies from TMDB.
    use_premade=False → leaves the catalog empty; host adds movies manually via add_movie_to_room().
    Returns the catalog (empty list or 20 movies).
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")

    if use_premade:
        return fetch_movies_for_room(code, api_key)

    rooms[code]["movies"] = []
    return []


def fetch_movies_for_room(code, api_key):
    """
    Fetch 20 popular movies from TMDB and store them in the given room.
    Raises ValueError if the room doesn't exist.
    Raises RuntimeError if the TMDB request fails.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")

    response = requests.get(
        f"{TMDB_BASE}/movie/popular",
        params={"api_key": api_key, "language": "en-US", "page": 1},
        timeout=10,
    )
    if not response.ok:
        raise RuntimeError(f"TMDB request failed: {response.status_code} {response.text}")

    raw = response.json().get("results", [])[:20]

    movies = [
        {
            "id": m["id"],
            "title": m["title"],
            "overview": m["overview"],
            "poster": f"{TMDB_IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
            "rating": m.get("vote_average"),
        }
        for m in raw
    ]

    rooms[code]["movies"] = movies
    return movies


def search_movies(query, api_key):
    """
    Search TMDB for movies matching a query string.
    Returns a list of up to 10 results the host can pick from.
    """
    response = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={"api_key": api_key, "language": "en-US", "query": query, "page": 1},
        timeout=10,
    )
    if not response.ok:
        raise RuntimeError(f"TMDB request failed: {response.status_code} {response.text}")

    raw = response.json().get("results", [])[:10]
    return [
        {
            "id": m["id"],
            "title": m["title"],
            "overview": m["overview"],
            "poster": f"{TMDB_IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
            "rating": m.get("vote_average"),
        }
        for m in raw
    ]


def add_movie_to_room(code, movie_id, api_key):
    """
    Look up a movie by TMDB ID and add it to the room's catalog.
    Skips silently if the movie is already in the room.
    Raises ValueError if the room doesn't exist or voting has started.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")
    if rooms[code]["voting_started"]:
        raise ValueError("Cannot modify the catalog after voting has started.")

    existing_ids = {m["id"] for m in rooms[code]["movies"]}
    if movie_id in existing_ids:
        return rooms[code]["movies"]

    response = requests.get(
        f"{TMDB_BASE}/movie/{movie_id}",
        params={"api_key": api_key, "language": "en-US"},
        timeout=10,
    )
    if not response.ok:
        raise RuntimeError(f"TMDB request failed: {response.status_code} {response.text}")

    m = response.json()
    rooms[code]["movies"].append({
        "id": m["id"],
        "title": m["title"],
        "overview": m["overview"],
        "poster": f"{TMDB_IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
        "rating": m.get("vote_average"),
    })
    return rooms[code]["movies"]


def remove_movie_from_room(code, movie_id):
    """
    Remove a movie from the room's catalog by TMDB ID.
    Raises ValueError if the room doesn't exist, voting has started,
    or the movie isn't in the room.
    """
    code = code.upper()
    if code not in rooms:
        raise ValueError(f"Room '{code}' does not exist.")
    if rooms[code]["voting_started"]:
        raise ValueError("Cannot modify the catalog after voting has started.")

    catalog = rooms[code]["movies"]
    updated = [m for m in catalog if m["id"] != movie_id]
    if len(updated) == len(catalog):
        raise ValueError(f"Movie ID {movie_id} is not in room '{code}'.")

    rooms[code]["movies"] = updated
    return updated
