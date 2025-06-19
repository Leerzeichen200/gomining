import streamlit as st
import requests
import json
import pandas as pd

# API URL + Access Token (Token bitte später sicherer verwalten!)
API_URL = "https://api.gomining.com/api/nft-game/round/get-last"
ACCESS_TOKEN = "DEIN_ACCESS_TOKEN_HIER"  # <-- hier deinen Access Token einsetzen

# Funktion zum Abrufen der API-Daten
def fetch_last_round():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API Fehler: {response.status_code}")
        return None

st.title("🏆 BTC Mining Wars Bot")
st.write("Automatische Auswertung der letzten Runde")

# API abrufen
data = fetch_last_round()

if data:
    st.json(data)  # Zeigt die Rohdaten zur Kontrolle

    # Beispiel: Extrahiere relevante Infos (je nach Struktur anpassen!)
    round_id = data.get("round_id", "unbekannt")
    winner = data.get("winner", "unbekannt")
    points = data.get("points", "unbekannt")

    st.write(f"**Runde:** {round_id}")
    st.write(f"**Gewinner:** {winner}")
    st.write(f"**Punkte:** {points}")

    # Optional: Tabelle erzeugen
    df = pd.DataFrame([{
        "Runde": round_id,
        "Gewinner": winner,
        "Punkte": points
    }])
    st.table(df)

else:
    st.warning("Keine Daten empfangen.")
