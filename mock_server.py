from flask import Flask, jsonify

app = Flask(__name__)

# Simulated game data with runes and items for CDR testing
mock_game_data = {
    "activePlayer": {
        "summonerName": "TEST1"
    },
    "allPlayers": [
        # --- Ally team (ORDER) ---
        {
            "summonerName": "TEST1",
            "team": "ORDER",
            "championName": "Ahri",
            "summonerSpells": {
                "summonerSpellOne": {"displayName": "Flash"},
                "summonerSpellTwo": {"displayName": "Ignite"}
            },
            "runes": {"perkIds": [8112, 8126, 8135, 8138, 8304, 8347]},
            "items": []
        },
        # --- Enemy team (CHAOS) ---
        {
            "summonerName": "EnemyYasuo",
            "team": "CHAOS",
            "championName": "Yasuo",
            "summonerSpells": {
                "summonerSpellOne": {"displayName": "Flash"},
                "summonerSpellTwo": {"displayName": "Teleport"}
            },
            "runes": {"perkIds": [8005, 9111, 9104, 8299, 8444, 5007]},
            "items": [{"itemID": 3158}]  
        },
        {
            "summonerName": "EnemyLeeSin",
            "team": "CHAOS",
            "championName": "LeeSin",
            "summonerSpells": {
                "summonerSpellOne": {"displayName": "Flash"},
                "summonerSpellTwo": {"displayName": "Smite"}
            },
            # Lee Sin has Cosmic Insight (+18 haste) + Ionian Boots (+12 haste) = 30 total
            "runes": {"perkIds": [8010, 9111, 9105, 8299, 8347, 5008]},
            "items": [{"itemID": 3158}]
        },
        {
            "summonerName": "EnemyLux",
            "team": "CHAOS",
            "championName": "Lux",
            "summonerSpells": {
                "summonerSpellOne": {"displayName": "Flash"},
                "summonerSpellTwo": {"displayName": "Barrier"}
            },
            "runes": {"perkIds": [8214, 8226, 8234, 8237, 8306, 8410]},
            "items": [{"itemID": 1056}, {"itemID": 1001}]
        },
        {
            "summonerName": "EnemyJinx",
            "team": "CHAOS",
            "championName": "Jinx",
            "summonerSpells": {
                "summonerSpellOne": {"displayName": "Flash"},
                "summonerSpellTwo": {"displayName": "Heal"}
            },
            "runes": {"perkIds": [8005, 9111, 9104, 9105, 8299, 8347]},
            "items": [{"itemID": 3158}]
        }
    ]
}


@app.route("/liveclientdata/allgamedata", methods=["GET"])
def fake_lol_client():
    return jsonify(mock_game_data)


if __name__ == "__main__":
    print("====== Mock League client started! ======")
    print("Serving mock data on http://127.0.0.1:2999")
    app.run(port=2999, debug=True)
