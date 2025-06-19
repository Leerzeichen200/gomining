import streamlit as st
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt

# Konfiguration
API_URL = "https://api.gomining.com/api/nft-game/round/get-last"
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]  # Speichere den Token in Streamlit Secrets!

# Session-State für Historie
if "history" not in st.session_state:
    st.session_state.history = []

# API-Daten abrufen
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

st.title("⛏️ BTC Mining Wars Automatischer Bot")

data = fetch_last_round()

if data:
    # Extrahiere (je nach API Struktur anpassen)
    round_id = data.get("round_id", None)
    winner = data.get("winner", "unbekannt")
    points = data.get("points", 0)
    duration = data.get("duration", None)  # falls vorhanden

    # Prüfe ob neue Runde
    if not any(d["round_id"] == round_id for d in st.session_state.history):
        st.session_state.history.append({
            "round_id": round_id,
            "winner": winner,
            "points": points,
            "duration": duration,
            "timestamp": time.time()
        })

    # Zeige letzte Runde
    st.subheader("Letzte Runde")
    df_last = pd.DataFrame([{
        "Runde": round_id,
        "Gewinner": winner,
        "Punkte": points,
        "Dauer": duration
    }])
    st.table(df_last)

    # Zeige Verlauf
    st.subheader("Historie der Rundenlängen")
    df_hist = pd.DataFrame(st.session_state.history)

    if not df_hist.empty:
        if "duration" in df_hist.columns:
            df_hist["Dauer"].fillna(0, inplace=True)
            st.line_chart(df_hist["Dauer"])

            # Statistiken
            avg_duration = df_hist["Dauer"].mean()
            st.write(f"⏱ Durchschnittliche Rundenlänge: {avg_duration:.2f} Minuten")

            # Wahrscheinlichkeit nächste Runde
            st.write("🔮 Wahrscheinlichkeit, dass nächste Runde <= X Minuten:")
            max_d = df_hist["Dauer"].max()
            bins = list(range(0, int(max_d) + 5, 5))
            hist = df_hist["Dauer"].value_counts(bins=bins, normalize=True).sort_index()
            st.bar_chart(hist)

else:
    st.warning("Keine Daten empfangen.")
