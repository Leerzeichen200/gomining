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
st.write("Die App holt automatisch die Daten der letzten Runde von der GoMining API und zeigt live Statistiken.")

data = fetch_last_round()

if data and "data" in data:
    rd = data["data"]
    block_number = rd.get("blockNumber", "unbekannt")
    started_at = rd.get("startedAt")
    ended_at = rd.get("endedAt")
    winner_clan = rd.get("winnerClanId", "unbekannt")

    # Berechne Dauer falls möglich
    if started_at and ended_at:
        start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
        duration_min = (end_dt - start_dt).total_seconds() / 60
    else:
        duration_min = None

    # Zeige Block-Infos
    st.subheader("Letzte Runde")
    st.write(f"**Block Number:** {block_number}")
    st.write(f"**Winner Clan ID:** {winner_clan}")
    st.write(f"**Started At:** {started_at}")
    st.write(f"**Ended At:** {ended_at if ended_at else 'läuft noch'}")
    st.write(f"**Dauer (min):** {duration_min:.2f}" if duration_min else "Dauer: läuft noch oder unvollständig")

    # Clans-Tabelle
    if "allClansState" in rd:
        clans = []
        for clan in rd["allClansState"]:
            clans.append({
                "Clan ID": clan.get("clanId"),
                "Score": clan.get("currentAddedScore"),
                "Active Boost": clan.get("activeBoostScore"),
                "Clan Power": clan.get("clanPower")
            })
        df_clans = pd.DataFrame(clans).sort_values(by="Score", ascending=False)
        st.subheader("Clans dieser Runde")
        st.table(df_clans)

else:
    st.warning("Keine gültigen Runden-Daten empfangen.")
