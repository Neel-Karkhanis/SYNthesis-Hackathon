# Movie Night Voter

> Built at SYNthesis — CNSA's Premier Hackathon (April 19, 2026)

A web app where a group of friends can collectively decide what movie to watch. One person creates a room and gets a 4-letter code. Others join with that code. Everyone swipes yes/no on the same set of movies. Once everyone finishes, the app reveals which movie won.

## How It Works

1. **Create a room** — the host gets a 4-letter join code and chooses either a premade catalog of 20 popular movies from TMDB or builds a custom list
2. **Everyone joins** — friends enter the code and a display name, no account needed
3. **Swipe yes/no** — each user votes on every movie in the catalog
4. **Winner revealed**
   - If one or more movies get unanimous yes votes, one is picked at random as the winner
   - Otherwise, the movie with the fewest no votes wins

## Tech Stack

- **Frontend:** React (web)
- **Backend:** Python + Flask
- **Movie data:** TMDB API
- **State:** in-memory (no database)
- **No WebSockets** — frontend polls the backend for status updates

## Backend API

Base URL: `http://localhost:5000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/rooms` | Create a room (body: `display_name`, `use_premade`) |
| `POST` | `/rooms/:code/join` | Join with a display name |
| `GET`  | `/rooms/:code/movies` | Get the room's movie list |
| `GET`  | `/rooms/:code/movies/search?q=&display_name=` | Host searches TMDB |
| `POST` | `/rooms/:code/movies` | Host adds a movie by TMDB ID |
| `DELETE` | `/rooms/:code/movies/:id` | Host removes a movie |
| `POST` | `/rooms/:code/vote` | Submit a yes/no vote |
| `POST` | `/rooms/:code/done` | Mark self as done voting |
| `GET`  | `/rooms/:code/status` | Poll voting progress |
| `GET`  | `/rooms/:code/results` | Get ranked results with winner |

Host-only endpoints reject non-host users. The catalog locks as soon as the first vote is cast.

## Running Locally

**Backend:**
```bash
cd src/backend
pip install -r requirements.txt
export TMDB_API_KEY=your_key_here
python main.py
```

**Frontend:**
```bash
# (coming soon)
```

## Project Structure

```
SYNthesis/
└── src/
    └── backend/
        ├── main.py              # Flask app and route handlers
        ├── room_generation.py   # Room creation, join, host checks
        ├── movie_catalog.py     # TMDB fetching, host catalog management
        ├── voting.py            # Swiping and done-tracking
        ├── movie_selection.py   # Winner calculation with fallback
        └── requirements.txt
```

## Team

- Neel Karkhanis
- John Michael Wittenberger
