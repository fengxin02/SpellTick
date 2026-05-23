import sys
import os
import requests
import urllib3
from flask import Flask, jsonify, render_template

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

# Try HTTP first (mock server), then HTTPS (real game)
LIVE_API_URLS = [
    "http://127.0.0.1:2999/liveclientdata/allgamedata",
    "https://127.0.0.1:2999/liveclientdata/allgamedata",
]

# Base cooldowns in seconds (patch 14.x+ values)
BASE_COOLDOWNS = {
    "Flash": 300,
    "Teleport": 360,
    "Ignite": 180,
    "Smite": 90,
    "Heal": 240,
    "Barrier": 180,
    "Exhaust": 210,
    "Cleanse": 210,
    "Ghost": 210,
    "Mark": 80,
    "Clarity": 240,
}

COSMIC_INSIGHT_IDS = {8347, 8365}
IONIAN_BOOTS_ID = 3158


def get_live_data():
    for url in LIVE_API_URLS:
        try:
            resp = requests.get(url, verify=False, timeout=2)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            continue
    return None


def calc_haste(player):
    """Calculate total summoner spell haste from runes and items."""
    haste = 0

    # Check rune perk IDs for Cosmic Insight (+18 summoner spell haste)
    runes = player.get("runes", {})
    perk_ids = runes.get("perkIds", [])
    if any(pid in COSMIC_INSIGHT_IDS for pid in perk_ids):
        haste += 18

    # Check items for Ionian Boots of Lucidity (+12 summoner spell haste)
    for item in player.get("items", []):
        if item.get("itemID") == IONIAN_BOOTS_ID:
            haste += 12
            break

    return haste


def calc_cd(spell_name, haste):
    """Calculate actual cooldown: base * 100 / (100 + haste)."""
    base = BASE_COOLDOWNS.get(spell_name, 300)
    return round(base * 100 / (100 + haste))


@app.route("/api/gamedata")
def api_game_data():
    data = get_live_data()
    if not data:
        return jsonify({"error": "Game not detected", "players": []})

    active_name = data.get("activePlayer", {}).get("summonerName", "")
    all_players = data.get("allPlayers", [])

    my_team = None
    for p in all_players:
        if p.get("summonerName") == active_name:
            my_team = p.get("team")
            break

    enemies = []
    for p in all_players:
        if p.get("team") != my_team:
            haste = calc_haste(p)
            spells = p.get("summonerSpells", {})
            s1 = spells.get("summonerSpellOne", {}).get("displayName", "")
            s2 = spells.get("summonerSpellTwo", {}).get("displayName", "")
            enemies.append(
                {
                    "champion": p.get("championName", "Unknown"),
                    "name": p.get("summonerName", ""),
                    "spells": [
                        {"name": s1, "cd": calc_cd(s1, haste)},
                        {"name": s2, "cd": calc_cd(s2, haste)},
                    ],
                    "haste": haste,
                }
            )

    resp = jsonify({"players": enemies})
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    print("SpellTick — Summoner Spell Timer")
    print("Open http://127.0.0.1:5000 in your browser")
    print("Mobile: connect to http://<your-ip>:5000 on same network")
    app.run(host="0.0.0.0", port=5000, debug=False)
