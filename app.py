from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = "db.json"


def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "users": {},
            "cookie": "",
            "all_games": [],
            "done_games": []
        }
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {
                "users": {},
                "cookie": "",
                "all_games": [],
                "done_games": []
            }


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


@app.get("/")
def index():
    return "✅ Chess DB API is running", 200


# ===== Users =====
@app.get("/api/users")
def get_users():
    db = load_db()
    return jsonify({"users": db.get("users", {})})


@app.post("/api/users")
def set_user():
    data = request.get_json(force=True)
    chat_id = str(data.get("chat_id"))
    username = (data.get("username") or "").strip().lower()

    if not chat_id or not username:
        return jsonify({"ok": False, "error": "missing chat_id or username"}), 400

    db = load_db()
    users = db.get("users", {})
    users[chat_id] = username
    db["users"] = users
    save_db(db)

    return jsonify({"ok": True})


# ===== Cookie =====
@app.get("/api/cookie")
def get_cookie():
    db = load_db()
    return jsonify({"token": db.get("cookie", "")})


@app.post("/api/cookie")
def set_cookie():
    data = request.get_json(force=True)
    token = data.get("token", "")
    db = load_db()
    db["cookie"] = token
    save_db(db)
    return jsonify({"ok": True})


# ===== ALL_GAMES =====
@app.get("/api/all_games")
def get_all_games():
    db = load_db()
    return jsonify({"games": db.get("all_games", [])})


@app.post("/api/all_games")
def set_all_games():
    data = request.get_json(force=True)
    games = data.get("games", [])
    if not isinstance(games, list):
        return jsonify({"ok": False, "error": "games must be a list"}), 400

    db = load_db()
    db["all_games"] = games
    save_db(db)
    return jsonify({"ok": True, "count": len(games)})


# ===== done_games =====
@app.get("/api/done_games")
def get_done_games():
    db = load_db()
    return jsonify({"games": db.get("done_games", [])})


@app.post("/api/done_games/add")
def add_done_game():
    data = request.get_json(force=True)
    game_id = data.get("game_id")
    if not game_id:
        return jsonify({"ok": False, "error": "missing game_id"}), 400

    db = load_db()
    done = db.get("done_games", [])
    if game_id not in done:
        done.append(game_id)
    db["done_games"] = done
    save_db(db)

    return jsonify({"ok": True, "count": len(done)})


if __name__ == "__main__":
    # للتشغيل المحلي
    app.run(host="0.0.0.0", port=8000, debug=True)
