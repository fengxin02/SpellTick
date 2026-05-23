import requests
import urllib3
from flask import Flask, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Real game uses HTTPS, mock server uses plain HTTP
LIVE_API_URLS = [
    "https://127.0.0.1:2999/liveclientdata/allgamedata",
    "http://127.0.0.1:2999/liveclientdata/allgamedata",
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

    return jsonify({"players": enemies})


@app.route("/")
def index():
    return HTML_PAGE


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SpellTick</title>
<style>
  :root {
    --bg: #0b0b12;
    --card-bg: #151525;
    --card-border: #252540;
    --text: #cdd1d9;
    --text-dim: #7b7f8a;
    --flash: #f0c060;
    --tp: #c88af0;
    --ignite: #f06050;
    --smite: #60b8f0;
    --heal: #60f080;
    --ghost: #80d0ff;
    --default-spell: #8890a0;
    --active-ring: #00e060;
    --haste-tag: #50d0a0;
    --btn-reset: #3a3a55;
  }
  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', 'PingFang SC', system-ui, sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
    user-select: none;
    -webkit-user-select: none;
  }

  header {
    text-align: center;
    margin-bottom: 20px;
  }
  header h1 {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #c0a0ff 0%, #60d0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  header .status {
    font-size: 12px;
    color: var(--text-dim);
    margin-top: 4px;
  }
  header .status.live { color: #40d060; }
  header .status.offline { color: #e05050; }

  .toolbar {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .toolbar button {
    padding: 8px 18px;
    border: 1px solid var(--card-border);
    border-radius: 6px;
    background: var(--btn-reset);
    color: var(--text);
    cursor: pointer;
    font-size: 13px;
    transition: background .15s;
  }
  .toolbar button:hover { background: #4a4a65; }
  .toolbar button.primary { background: #5b40c0; border-color: #7b60e0; }
  .toolbar button.primary:hover { background: #6b50d0; }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 14px;
    width: 100%;
    max-width: 1100px;
  }

  .card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 14px 12px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    transition: border-color .2s;
  }
  .card:hover { border-color: #404060; }

  .card .champ {
    font-size: 15px;
    font-weight: 600;
    color: #e8e8f0;
    text-align: center;
  }
  .card .haste-tag {
    font-size: 10px;
    color: var(--haste-tag);
    background: #1a3030;
    padding: 2px 8px;
    border-radius: 10px;
    display: none;
  }
  .card .haste-tag.show { display: inline-block; }

  .spell-row {
    display: flex;
    gap: 10px;
    width: 100%;
    justify-content: center;
  }

  .spell-btn {
    position: relative;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    border: 3px solid var(--card-border);
    background: var(--card-bg);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: transform .1s, border-color .15s, box-shadow .15s;
    outline: none;
    -webkit-tap-highlight-color: transparent;
    overflow: hidden;
  }
  .spell-btn:active { transform: scale(0.93); }

  .spell-btn .label {
    font-size: 10px;
    font-weight: 600;
    color: var(--default-spell);
    letter-spacing: 0.5px;
    text-align: center;
    line-height: 1.15;
    z-index: 1;
  }
  .spell-btn .cd-num {
    font-size: 11px;
    color: var(--text-dim);
    z-index: 1;
  }

  /* spell type colors */
  .spell-btn[data-spell="Flash"]     .label { color: var(--flash); }
  .spell-btn[data-spell="Teleport"]   .label { color: var(--tp); }
  .spell-btn[data-spell="Ignite"]     .label { color: var(--ignite); }
  .spell-btn[data-spell="Smite"]      .label { color: var(--smite); }
  .spell-btn[data-spell="Heal"]       .label { color: var(--heal); }
  .spell-btn[data-spell="Ghost"]      .label { color: var(--ghost); }
  .spell-btn[data-spell="Exhaust"]    .label { color: #e0b060; }
  .spell-btn[data-spell="Barrier"]    .label { color: #f0c870; }
  .spell-btn[data-spell="Cleanse"]    .label { color: #80e0d0; }

  /* cooldown active state */
  .spell-btn.on-cd {
    border-color: #404050;
    cursor: default;
  }
  .spell-btn.on-cd .label { color: #555560 !important; }
  .spell-btn.on-cd .cd-num { color: #909090; }
  .spell-btn.on-cd:active { transform: none; }

  /* countdown overlay ring */
  .spell-btn svg {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
  }
  .spell-btn svg circle.bg {
    fill: none;
    stroke: transparent;
    stroke-width: 3;
  }
  .spell-btn svg circle.fg {
    fill: none;
    stroke: var(--active-ring);
    stroke-width: 3;
    stroke-linecap: round;
    transform: rotate(-90deg);
    transform-origin: center;
    transition: stroke-dashoffset 1s linear, stroke .3s;
  }

  .spell-btn .timer-text {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 18px;
    font-weight: 700;
    color: #e0e0e0;
    z-index: 2;
    pointer-events: none;
    display: none;
    text-shadow: 0 1px 6px rgba(0,0,0,.7);
  }
  .spell-btn.on-cd .timer-text { display: block; }
  .spell-btn.on-cd .label { visibility: hidden; }
  .spell-btn.on-cd .cd-num { visibility: hidden; }

  .empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    color: var(--text-dim);
  }
  .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
</style>
</head>
<body>

<header>
  <h1>SpellTick</h1>
  <div class="status offline" id="status">Not connected — start a game or mock server</div>
</header>

<div class="toolbar">
  <button class="primary" onclick="fetchData()">Refresh</button>
  <button onclick="resetAll()">Reset All Timers</button>
</div>

<div class="grid" id="grid">
  <div class="empty-state">
    <div class="icon">&#9881;</div>
    <div>Click <strong>Refresh</strong> to load enemy summoner spells</div>
  </div>
</div>

<script>
// --- Timer engine ---

// Base CD map (matched with Python backend)
const BASE_CD = {
    "Flash":300,"Teleport":360,"Ignite":180,"Smite":90,"Heal":240,
    "Barrier":180,"Exhaust":210,"Cleanse":210,"Ghost":210,"Mark":80,"Clarity":240
};

// Each active timer: { cd, startMs, intervalId }
const timers = new Map();

function timerKey(champion, spellName) {
    return champion + "::" + spellName;
}

function startTimer(champion, spellName, cdSeconds) {
    const key = timerKey(champion, spellName);

    // Clear existing timer for this spell if any
    stopTimer(key);

    const startMs = Date.now();
    const intervalId = setInterval(() => tick(key), 100);

    timers.set(key, { cd: cdSeconds, startMs, intervalId });
    updateButtonUI(key, cdSeconds);
}

function stopTimer(key) {
    const t = timers.get(key);
    if (t) {
        clearInterval(t.intervalId);
        timers.delete(key);
    }
}

function tick(key) {
    const t = timers.get(key);
    if (!t) return;

    const elapsed = (Date.now() - t.startMs) / 1000;
    const remaining = t.cd - elapsed;

    if (remaining <= 0) {
        stopTimer(key);
        updateButtonUI(key, 0);
        resetButtonUI(key);
        return;
    }

    updateButtonUI(key, remaining);
}

function updateButtonUI(key, remaining) {
    const el = document.querySelector(`[data-timer-key="${CSS.escape(key)}"]`);
    if (!el) return;

    const cd = parseFloat(el.dataset.cd);
    const pct = cd > 0 ? Math.max(0, remaining / cd) : 0;
    const mins = Math.floor(remaining / 60);
    const secs = Math.floor(remaining % 60);
    const text = mins > 0
        ? `${mins}:${String(secs).padStart(2,'0')}`
        : String(secs);

    const timerText = el.querySelector('.timer-text');
    if (timerText) timerText.textContent = text;

    const circle = el.querySelector('circle.fg');
    if (circle) {
        const r = circle.getAttribute('r');
        const C = 2 * Math.PI * r;
        circle.setAttribute('stroke-dasharray', C);
        circle.setAttribute('stroke-dashoffset', C * (1 - pct));

        // Color shift: red (low) -> yellow -> green (full)
        if (remaining <= 15) {
            circle.setAttribute('stroke', '#f05050');
        } else if (remaining <= 60) {
            circle.setAttribute('stroke', '#f0c040');
        } else {
            circle.setAttribute('stroke', '#00e060');
        }
    }

    if (remaining <= 0) {
        el.classList.remove('on-cd');
        resetButtonUI(key);
    } else {
        el.classList.add('on-cd');
    }
}

function resetButtonUI(key) {
    const el = document.querySelector(`[data-timer-key="${CSS.escape(key)}"]`);
    if (!el) return;
    el.classList.remove('on-cd');
    const timerText = el.querySelector('.timer-text');
    if (timerText) timerText.textContent = '';
    const circle = el.querySelector('circle.fg');
    if (circle) circle.setAttribute('stroke-dashoffset', '0');
}

function resetAll() {
    for (const key of timers.keys()) {
        clearInterval(timers.get(key).intervalId);
        resetButtonUI(key);
    }
    timers.clear();
}

function onSpellClick(el) {
    // If already on cooldown, ignore click (no resetting individual spells by clicking)
    if (el.classList.contains('on-cd')) return;

    const key = el.dataset.timerKey;
    const cd = parseInt(el.dataset.cd, 10);
    const [champion, spellName] = key.split('::');
    startTimer(champion, spellName, cd);
}

// --- Data fetching ---

async function fetchData() {
    const grid = document.getElementById('grid');
    const status = document.getElementById('status');

    grid.innerHTML = '<div class="empty-state"><div class="icon">&#8987;</div><div>Loading...</div></div>';

    try {
        const resp = await fetch('/api/gamedata');
        const data = await resp.json();

        if (data.error || data.players.length === 0) {
            status.textContent = 'Not connected — start a game or mock server';
            status.className = 'status offline';
            grid.innerHTML = `<div class="empty-state">
                <div class="icon">&#9881;</div>
                <div>No game data. Run <strong>mock_server.py</strong> for testing, or enter a real game.</div>
            </div>`;
            return;
        }

        status.textContent = 'Live — ' + data.players.length + ' enemies detected';
        status.className = 'status live';

        renderPlayers(data.players);
    } catch (e) {
        status.textContent = 'Connection error — is app.py running?';
        status.className = 'status offline';
        grid.innerHTML = `<div class="empty-state">
            <div class="icon">&#9888;</div>
            <div>Could not reach the backend.</div>
        </div>`;
    }
}

function renderPlayers(players) {
    const grid = document.getElementById('grid');
    grid.innerHTML = '';

    for (const p of players) {
        const card = document.createElement('div');
        card.className = 'card';

        const champEl = document.createElement('div');
        champEl.className = 'champ';
        champEl.textContent = p.champion;
        card.appendChild(champEl);

        // Haste tag
        if (p.haste > 0) {
            const tag = document.createElement('div');
            tag.className = 'haste-tag show';
            tag.textContent = '+' + p.haste + ' haste';
            card.appendChild(tag);
        }

        const row = document.createElement('div');
        row.className = 'spell-row';

        for (const spell of p.spells) {
            const key = timerKey(p.champion, spell.name);
            const existing = timers.get(key);
            let remaining = 0;
            if (existing) {
                remaining = existing.cd - (Date.now() - existing.startMs) / 1000;
                if (remaining < 0) remaining = 0;
            }

            const btn = buildSpellButton(p.champion, spell, key, remaining);
            row.appendChild(btn);
        }

        card.appendChild(row);
        grid.appendChild(card);
    }

    // Resume active timer ticks for the newly rendered buttons
    for (const [key, t] of timers) {
        const remaining = t.cd - (Date.now() - t.startMs) / 1000;
        if (remaining <= 0) {
            stopTimer(key);
            resetButtonUI(key);
        } else {
            updateButtonUI(key, remaining);
        }
    }
}

function buildSpellButton(champion, spell, key, remaining) {
    const btn = document.createElement('button');
    btn.className = 'spell-btn';
    btn.dataset.spell = spell.name;
    btn.dataset.timerKey = key;
    btn.dataset.cd = spell.cd;
    btn.title = `${spell.name} — ${spell.cd}s CD`;
    btn.onclick = () => onSpellClick(btn);

    const r = 32; // radius for the SVG ring
    const C = 2 * Math.PI * r;

    // SVG ring
    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 72 72');

    const bgCircle = document.createElementNS(svgNS, 'circle');
    bgCircle.setAttribute('class', 'bg');
    bgCircle.setAttribute('cx', '36');
    bgCircle.setAttribute('cy', '36');
    bgCircle.setAttribute('r', String(r));
    svg.appendChild(bgCircle);

    const fgCircle = document.createElementNS(svgNS, 'circle');
    fgCircle.setAttribute('class', 'fg');
    fgCircle.setAttribute('cx', '36');
    fgCircle.setAttribute('cy', '36');
    fgCircle.setAttribute('r', String(r));
    fgCircle.setAttribute('stroke-dasharray', String(C));
    fgCircle.setAttribute('stroke-dashoffset', '0');
    svg.appendChild(fgCircle);

    btn.appendChild(svg);

    // Spell label
    const label = document.createElement('span');
    label.className = 'label';
    label.textContent = spell.name;
    btn.appendChild(label);

    // Base CD number
    const cdNum = document.createElement('span');
    cdNum.className = 'cd-num';
    cdNum.textContent = spell.cd + 's';
    btn.appendChild(cdNum);

    // Countdown text overlay
    const timerText = document.createElement('span');
    timerText.className = 'timer-text';
    btn.appendChild(timerText);

    // Restore active timer state
    if (remaining > 0) {
        btn.classList.add('on-cd');
        const mins = Math.floor(remaining / 60);
        const secs = Math.floor(remaining % 60);
        timerText.textContent = mins > 0
            ? `${mins}:${String(secs).padStart(2, '0')}`
            : String(Math.floor(remaining));
        const pct = remaining / spell.cd;
        fgCircle.setAttribute('stroke-dashoffset', String(C * (1 - pct)));
    }

    return btn;
}

// Auto-refresh on page load
fetchData();
</script>
</body>
</html>"""

if __name__ == "__main__":
    print("SpellTick — Summoner Spell Timer")
    print("Open http://127.0.0.1:5000 in your browser")
    print("(Run mock_server.py first for testing without a real game)")
    app.run(host="0.0.0.0", port=5000, debug=True)
