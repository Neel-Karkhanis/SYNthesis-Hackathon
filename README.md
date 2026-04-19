# Votely

Movie night voting for groups. One person creates a room, everyone joins with a short code, and each player swipes yes or no on the same movie catalog until a winner is revealed.

## Features

- Create a room with a short join code
- Choose a premade catalog of 8 popular movies or build your own list
- Add and remove movies from the host catalog before voting starts
- Join from multiple devices or browser tabs with separate player identities
- Swipe-based voting with visual yes/no feedback
- Live polling for room start, completion status, and final results
- Winner reveal with ranking output

## How It Works

1. The host creates a room.
2. The host picks either `Most Popular` or `Pick My Own`.
3. Other players join with the room code and a display name.
4. The host starts the game.
5. Every player votes on every movie.
6. When everyone finishes, the app calculates the winning movie and shows the ranking.

Winner selection:

- If one or more movies receive unanimous yes votes, one of those unanimous picks is chosen at random.
- Otherwise, the movie with the fewest no votes wins.

## Tech Stack

- Frontend: static HTML, CSS, and vanilla JavaScript
- Backend: Python + Flask
- CORS: `flask-cors`
- Movie data: TMDB API
- State: in-memory room state

## Project Structure

```text
synthesis/
├── requirements.txt
├── server.py
└── src/
    ├── backend/
    │   ├── main.py
    │   ├── movie_catalog.py
    │   ├── movie_selection.py
    │   ├── room_generation.py
    │   ├── voting.py
    │   └── requirements.txt
    └── frontend/
        ├── index.html
        ├── host.html
        ├── player.html
        └── assets/
            ├── cloud-band.png
            └── star-sparkle.png
```

## API Overview

Base URL locally: `http://localhost:8000`

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/rooms` | Create a room |
| `POST` | `/rooms/<code>/join` | Join a room |
| `GET` | `/rooms/<code>/movies` | Get the room catalog |
| `GET` | `/rooms/<code>/movies/search?q=...&display_name=...` | Search TMDB as host |
| `POST` | `/rooms/<code>/movies` | Add a movie to the catalog |
| `DELETE` | `/rooms/<code>/movies/<movie_id>?display_name=...` | Remove a movie from the catalog |
| `POST` | `/rooms/<code>/vote` | Submit a yes/no vote |
| `POST` | `/rooms/<code>/done` | Mark a player finished |
| `GET` | `/rooms/<code>/status` | Poll room/voting state |
| `POST` | `/rooms/<code>/start` | Start the game as host |
| `GET` | `/rooms/<code>/results` | Fetch final ranking and winner |

Notes:

- Host-only catalog endpoints reject non-host users.
- The catalog locks once voting starts.
- Room state is in memory, so restarting the server clears all rooms.

## Local Setup

### 1. Install dependencies

From the repo root:

```bash
pip install -r requirements.txt
```

### 2. Set your TMDB key

```bash
export TMDB_API_KEY=your_key_here
```

If `TMDB_API_KEY` is not set, the backend falls back to the value currently hardcoded in `src/backend/main.py`.

### 3. Run the backend

```bash
cd src/backend
python main.py
```

The Flask app serves the frontend files directly, so after the backend starts you can open:

```text
http://localhost:8000
```

## Deploying on Render

Use a Python web service.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
cd src/backend && python main.py
```

Deployment notes:

- `main.py` binds to `0.0.0.0`
- `main.py` uses Render's `PORT` environment variable automatically
- You should set `TMDB_API_KEY` in Render environment variables
- Because room state is in memory, active rooms are not persistent across deploys or restarts

## Current Behavior Notes

- Premade rooms start with 8 popular movies.
- Host catalog cards support removing movies before the game starts.
- Player identity is stored per tab first via `sessionStorage`, with local fallback.
- The player screen includes swipe glow feedback, waiting animations, and a confetti winner reveal.

## Team

- Neel Karkhanis
- John Michael Wittenberger
