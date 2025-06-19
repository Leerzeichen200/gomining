import streamlit as st
import requests
import pandas as pd
import json

# API-URL
API_URL = "https://api.gomining.com/api/nft-game/round/get-last"

# Funktion: API-Daten holen
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

# Session-State: Rundenhistorie speichern
if "history" not in st.session_state:
    st.session_state.history = []

# Streamlit UI
st.title("⛏️ BTC Mining Wars Automatischer Bot")
st.write("Die App holt automatisch die Daten der letzten Runde von der GoMining API und zeigt live Statistiken.")

# API call
data = fetch_last_round()

if data:
    # Für Debug-Zwecke: rohe Antwort anzeigen
    with st.expander("Rohdaten"):
        st.json(data)

    # Werte extrahieren (anpassen an echte API-Antwort!)
    round_id = data.get("round_id", "unbekannt")
    winner = data.get("winner", "unbekannt")
    points = data.get("points", 0)
    duration = data.get("duration", 0)  # falls vorhanden

    # Neue Runde speichern, falls neu
    if not any(d["round_id"] == round_id for d in st.session_state.history):
        st.session_state.history.append({
            "round_id": round_id,
            "winner": winner,
            "points": points,
            "duration": duration
        })

    # Letzte Runde anzeigen
    st.subheader("Letzte Runde")
    df_last = pd.DataFrame([{
        "Runde": round_id,
        "Gewinner": winner,
        "Punkte": points,
        "Dauer": duration
    }])
    st.table(df_last)

    # Historie anzeigen
    st.subheader("Rundenhistorie")
    df_hist = pd.DataFrame(st.session_state.history)
    st.dataframe(df_hist)

    # Falls Dauer-Daten vorhanden: Chart + Statistik
    if not df_hist.empty and "duration" in df_hist.columns:
        if df_hist["duration"].notnull().any():
            st.line_chart(df_hist["duration"])
            st.write(f"⏱ Durchschnittliche Rundenlänge: {df_hist['duration'].mean():.2f} Minuten")

else:
    st.warning("Keine Daten empfangen oder API-Problem.")
