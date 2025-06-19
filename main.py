import streamlit as st
import pandas as pd

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Spieler", "Punkte", "Boosts", "Platz", "Gewonnen", "Rundenzeit"])

st.title("🎲 BTC-Mining Spiel Bot")
st.write("Gib die Daten einer Runde ein:")

with st.form("runde_form"):
    player = st.text_input("Spielername")
    points = st.number_input("Punktzahl", min_value=0, step=1)
    boosts = st.text_input("Verwendete Boosts (z.B. x2, lucky)")
    place = st.number_input("Platz im Ranking", min_value=1, step=1)
    won = st.radio("Block gewonnen?", ("ja", "nein"))
    time = st.number_input("Rundenzeit in Minuten", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Speichern")

if submitted and player:
    new = {"Spieler": player, "Punkte": points, "Boosts": boosts, "Platz": place, "Gewonnen": won, "Rundenzeit": time}
    st.session_state.data = st.session_state.data.append(new, ignore_index=True)
    st.success("Runde gespeichert!")

st.write("### 📋 Bisherige Runden")
st.dataframe(st.session_state.data)

if not st.session_state.data.empty:
    df = st.session_state.data
    avg_time = df["Rundenzeit"].mean()
    st.write(f"**🔹 Erwartete Rundenzeit:** {avg_time:.2f} Minuten")

    probs = df.groupby("Platz").apply(lambda grp: grp["Gewonnen"].value_counts().get("ja", 0) / len(grp))
    st.write("**🔹 Gewinnwahrscheinlichkeit je Platz:**")
    st.write(probs.fillna(0).mul(100).round(1).astype(str) + " %")

    best = probs.idxmax()
    st.write(f"🏆 **Am wahrscheinlichsten gewinnt Platz {best}** mit {probs[best]*100:.1f} %")

    st.write("### 📈 Punkte bei siegreichen Runden")
    st.bar_chart(df[df["Gewonnen"]=="ja"].groupby("Spieler")["Punkte"].mean())
