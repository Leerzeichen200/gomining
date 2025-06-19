import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "https://api.gomining.com/api/nft-game/round/get-last"

def fetch_last_round():
    headers = {
        "Authorization": f"Bearer {st.secrets['ACCESS_TOKEN']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        "Origin": "https://app.gomining.com",
        "Referer": "https://app.gomining.com/",
        "x-device-type": "desktop",
        "Accept": "application/json"
    }
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API Fehler: {response.status_code}")
        return None

st.title("⛏️ BTC Mining Wars Automatischer Bot")

# Session State initialisieren
if "round_history" not in st.session_state:
    st.session_state.round_history = []

data = fetch_last_round()

if data and "data" in data:
    rd = data["data"]
    block_number = rd.get("blockNumber", "unbekannt")
    started_at = rd.get("startedAt")
    ended_at = rd.get("endedAt")
    winner_clan = rd.get("winnerClanId", "unbekannt")
    clans_info = rd.get("allClansState", [])

    # Dauer berechnen
    if started_at and ended_at:
        start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
        duration_min = (end_dt - start_dt).total_seconds() / 60
    else:
        duration_min = None

    # Historie updaten (nur neue Blöcke speichern)
    if not any(r["block_number"] == block_number for r in st.session_state.round_history):
        st.session_state.round_history.append({
            "block_number": block_number,
            "started_at": started_at,
            "ended_at": ended_at,
            "duration": duration_min,
            "clans": clans_info
        })
        # Nur die letzten 15 speichern
        st.session_state.round_history = st.session_state.round_history[-15:]

    # Letzte Runde anzeigen
    st.subheader("Letzte Runde")
    st.write(f"**Block Number:** {block_number}")
    st.write(f"**Winner Clan ID:** {winner_clan}")
    st.write(f"**Dauer (min):** {duration_min:.2f}" if duration_min else "Dauer: läuft noch oder unvollständig")

    # Clans-Tabelle mit Boost-Übersicht
    clans_table = []
    for clan in clans_info:
        clans_table.append({
            "Clan ID": clan.get("clanId"),
            "Score": clan.get("currentAddedScore"),
            "Boost": clan.get("activeBoostScore"),
            "Power": clan.get("clanPower")
        })
    df_clans = pd.DataFrame(clans_table).sort_values(by="Score", ascending=False)
    st.table(df_clans)

    # Rundenlängen-Graph
    df_hist = pd.DataFrame(st.session_state.round_history)
    df_hist = df_hist.dropna(subset=["duration"])
    if not df_hist.empty:
        st.subheader("Rundenlängen der letzten 15 Runden")
        st.line_chart(df_hist.set_index("block_number")["duration"])
        avg_dur = df_hist["duration"].mean()
        st.write(f"⏱ Geschätzte Rundenlänge: {avg_dur:.2f} Minuten")

    # Boost-Graph
    st.subheader("Boost-Übersicht")
    boost_data = []
    for round_data in st.session_state.round_history:
        for clan in round_data["clans"]:
            boost_data.append({
                "Block": round_data["block_number"],
                "Clan": clan.get("clanId"),
                "Boost": clan.get("activeBoostScore")
            })
    df_boost = pd.DataFrame(boost_data)
    if not df_boost.empty:
        boost_pivot = df_boost.pivot_table(index="Block", columns="Clan", values="Boost", fill_value=0)
        st.bar_chart(boost_pivot)

else:
    st.warning("Keine gültigen Runden-Daten empfangen.")
