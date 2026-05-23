# LoL Local API Explorer

A technical demonstration of parsing real-time JSON data from the League of
Legends local client API, serving it through a Flask web interface accessible
across devices on the same network.

## Motivation

Modern games expose rich local APIs that developers can inspect and learn from.
This project explores how to:

- Discover and consume undocumented local HTTP endpoints
- Parse nested JSON structures with Python
- Build a lightweight Flask backend that bridges local data to any browser
- Serve a responsive web UI that works on desktop and mobile simultaneously

It is purely educational: a hands-on way to study local API communication,
real-time data processing, and cross-device web serving with Python.

## How it works

1. The League client exposes a local REST API on `127.0.0.1:2999` during a game.
2. A Python Flask server queries this endpoint, processes the JSON response, and
   extracts structured player data.
3. The processed data is served at `http://127.0.0.1:5000` as a web page.


## Quick start


1. Git clone the project. 

```bash
pip install flask requests urllib3
python app.py
```
2. Start a League of Legends custom/practice game. (Do not use it in other game modes)
4. Open `http://127.0.0.1:5000` in your browser.


### Testing without a live game

A mock server is included for development and testing without needing the
actual game client running:

```bash
python mock_server.py    # terminal 1 — starts the fake data server
python app.py            # terminal 2 — starts the web server
```

Open `http://127.0.0.1:5000` and you will see simulated stats.

## Build the .exe

```bash
pip install pyinstaller
python -m PyInstaller spelltick.spec --clean --noconfirm
```

The output is at `dist/SpellTick.exe`. Copy this single file to any Windows
machine; no Python installation is needed.

( if you want .exe :D )

## Tech stack

| Layer       | Technology                              |
| ----------- | --------------------------------------- |
| Backend     | Python 3, Flask                         |
| Data source | Local LCU REST API (JSON over HTTP/HTTPS) |
| Frontend    | Vanilla HTML, CSS, JavaScript           |
| Packaging   | PyInstaller                             |

## Project structure

```
├── app.py              # Flask server & data processing
├── mock_server.py      # Mock game data for offline development
├── templates/
│   └── index.html      # Single-page web UI
├── spelltick.spec       # PyInstaller build config
└── README.md
```

## Disclaimer

This project is an independent educational tool for exploring local API
communication and web development techniques. It does not modify game files,
inject code, or interact with the game process in any way. It only reads
publicly available data from a local HTTP endpoint that the game client
intentionally exposes on the user's own machine.

All player-visible data is already accessible in-game. This tool simply
presents it in a different format.
