import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from room_generation import create_room, join_room, get_room, is_host
from movie_catalog import initialize_catalog, search_movies, add_movie_to_room, remove_movie_from_room
from voting import swipe, finish_voting, get_voting_status
from movie_selection import get_results

app = Flask(__name__, static_folder="../frontend", static_url_path="")


@app.route("/")
def index():
    return app.send_static_file("index.html")
CORS(app)
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "63b4352868de674f090b64851438594e")


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        from flask import make_response
        res = make_response()
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type"
        res.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        return res

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    return response


def err(msg, status=400):
    return jsonify({"error": msg}), status


# --- Room endpoints ---

@app.route("/rooms", methods=["POST"])
def create():
    body = request.get_json() or {}
    host = body.get("display_name", "").strip()
    use_premade = body.get("use_premade", True)
    if not host:
        return err("display_name is required.")
    code = create_room(host)
    movies = initialize_catalog(code, TMDB_API_KEY, use_premade=use_premade)
    return jsonify({"code": code, "host": host, "movies": movies}), 201


@app.route("/rooms/<code>/join", methods=["POST"])
def join(code):
    body = request.get_json() or {}
    name = body.get("display_name", "").strip()
    if not name:
        return err("display_name is required.")
    try:
        room = join_room(code, name)
    except ValueError as e:
        return err(str(e))
    return jsonify({"code": code.upper(), "users": room["users"]}), 200


# --- Movie catalog endpoints (host only) ---

@app.route("/rooms/<code>/movies", methods=["GET"])
def get_movies(code):
    room = get_room(code)
    if not room:
        return err("Room not found.", 404)
    return jsonify(room["movies"]), 200


@app.route("/rooms/<code>/movies/search", methods=["GET"])
def search(code):
    query = request.args.get("q", "").strip()
    requester = request.args.get("display_name", "").strip()
    if not query:
        return err("Query parameter 'q' is required.")
    try:
        if not is_host(code, requester):
            return err("Only the host can search for movies.", 403)
        results = search_movies(query, TMDB_API_KEY)
    except ValueError as e:
        return err(str(e), 404)
    return jsonify(results), 200


@app.route("/rooms/<code>/movies", methods=["POST"])
def add_movie(code):
    body = request.get_json() or {}
    requester = body.get("display_name", "").strip()
    movie_id = body.get("movie_id")
    if not movie_id:
        return err("movie_id is required.")
    try:
        if not is_host(code, requester):
            return err("Only the host can add movies.", 403)
        catalog = add_movie_to_room(code, movie_id, TMDB_API_KEY)
    except (ValueError, RuntimeError) as e:
        return err(str(e))
    return jsonify(catalog), 200


@app.route("/rooms/<code>/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(code, movie_id):
    requester = request.args.get("display_name", "").strip()
    try:
        if not is_host(code, requester):
            return err("Only the host can remove movies.", 403)
        catalog = remove_movie_from_room(code, movie_id)
    except ValueError as e:
        return err(str(e))
    return jsonify(catalog), 200


# --- Voting endpoints ---

@app.route("/rooms/<code>/vote", methods=["POST"])
def vote(code):
    body = request.get_json() or {}
    name = body.get("display_name", "").strip()
    movie_id = body.get("movie_id")
    vote_value = body.get("vote", "").strip()
    if not name or not movie_id or not vote_value:
        return err("display_name, movie_id, and vote are required.")
    try:
        swipe(code, name, movie_id, vote_value)
    except ValueError as e:
        return err(str(e))
    return jsonify({"ok": True}), 200


@app.route("/rooms/<code>/done", methods=["POST"])
def done(code):
    body = request.get_json() or {}
    name = body.get("display_name", "").strip()
    if not name:
        return err("display_name is required.")
    try:
        finish_voting(code, name)
    except ValueError as e:
        return err(str(e))
    return jsonify({"ok": True}), 200


@app.route("/rooms/<code>/status", methods=["GET"])
def status(code):
    try:
        return jsonify(get_voting_status(code)), 200
    except ValueError as e:
        return err(str(e), 404)


@app.route("/rooms/<code>/start", methods=["POST"])
def start(code):
    body = request.get_json() or {}
    requester = body.get("display_name", "").strip()
    room = get_room(code)
    if not room:
        return err("Room not found.", 404)
    try:
        if not is_host(code, requester):
            return err("Only the host can start the game.", 403)
    except ValueError as e:
        return err(str(e), 404)
    if not room["movies"]:
        return err("Add at least one movie before starting.")
    room["started"] = True
    return jsonify({"ok": True}), 200


# --- Results endpoint ---

@app.route("/rooms/<code>/results", methods=["GET"])
def results(code):
    try:
        return jsonify(get_results(code)), 200
    except ValueError as e:
        return err(str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug)
