from flask import Flask, request, jsonify
import os
import requests
import sqlite3
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

SPOTIFY_SERVICE_URL = "http://127.0.0.1:5001"
DEEPSEEK_SERVICE_URL = "http://127.0.0.1:5000"

DB_PATH = "history.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            tracks TEXT
        )''')

def save_to_history(tracks):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO history (timestamp, tracks) VALUES (?, ?)", 
                     (datetime.utcnow().isoformat(), "\n".join(tracks)))

def get_token():
    response = requests.post(f"{SPOTIFY_SERVICE_URL}/v1/token", json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    })
    response.raise_for_status()
    return f"Bearer {response.json()['access_token']}"

def get_saved_tracks(token):
    headers = {"Authorization": token}
    response = requests.get(f"{SPOTIFY_SERVICE_URL}/v1/saved-tracks", headers=headers)
    response.raise_for_status()
    return response.json()

def recommend_tracks(track_list):
    response = requests.post(f"{DEEPSEEK_SERVICE_URL}/recommend", json={"tracks": track_list})
    response.raise_for_status()
    return response.json()

def send_to_playlist(token, tracks, title=None, playlist_id=None):
    headers = {"Authorization": token}
    payload = {"tracks": tracks}
    if title:
        payload["title"] = title

    if playlist_id:
        url = f"{SPOTIFY_SERVICE_URL}/v1/playlist/{playlist_id}"
    else:
        url = f"{SPOTIFY_SERVICE_URL}/v1/playlist"

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

@app.route("/v1/playlist", methods=["POST"])
def create_playlist_from_saved():
    try:
        token = get_token()
        saved_tracks = get_saved_tracks(token)
        recommended = recommend_tracks(saved_tracks)
        result = send_to_playlist(token, recommended["tracks"], title=recommended["title"])
        save_to_history(recommended["tracks"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/v1/playlist/<playlist_id>", methods=["POST"])
def add_to_specific_playlist(playlist_id):
    try:
        token = get_token()
        saved_tracks = get_saved_tracks(token)
        recommended = recommend_tracks(saved_tracks)
        result = send_to_playlist(token, recommended["tracks"], playlist_id=playlist_id)
        save_to_history(recommended["tracks"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
		
@app.route("/v1/history", methods=["GET"])
def get_history():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT timestamp, tracks FROM history ORDER BY id DESC")
            history = [
                {"timestamp": row[0], "tracks": row[1].split("\n")}
                for row in cursor.fetchall()
            ]
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=8000)
