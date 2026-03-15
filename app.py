import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import os

# --- CONFIGURAZIONE ---
if os.path.exists("icona.png"):
    img_icona = Image.open("icona.png")
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon=img_icona, layout="centered")
else:
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗")

st.title("🧗 Meteo Ceredo - Mostro Bovino")

lat, lon = 45.6117, 10.9710

def get_all_data():
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability,weathercode&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,sunshine_duration,wind_speed_10m_max&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data, hist = get_all_data()

# --- CALCOLO MOSTRO BOVINO INDEX ---
def calculate_bovino_index(hist_data):
    rain = sum(hist_data['daily']['precipitation_sum'])
    sun_hours = sum(hist_data['daily']['sunshine_duration']) / 3600
    avg_wind = np.mean(hist_data['daily']['wind_speed_10m_max'])
    
    # Fattore meteo: il sole asciuga molto (peso 1.5), il vento aiuta (peso 0.8), la pioggia distrugge (peso -5.0)
    # Calcoliamo un "bias" rispetto a una condizione ideale (es. 60h sole, 15kmh vento, 0 pioggia)
    meteo_factor = (sun_hours * 0.01) + (avg_wind * 0.02) - (rain * 0.15)
    return np.clip(meteo_factor, -0.2, 0.2) # Limita l'oscillazione al +/- 20%

bovino_bias = calculate_bovino_index(hist)

settori = {
    "Mangiafuoco": (75, 5),     # (Media base, deviazione)
    "Ceredoleso": (77, 3),
    "Supercanna": (70, 5),
    "Mondo Cano": (70, 5),
    "Del Peci": (67, 4),
    "Ostramandra": (60, 6)
}

# --- INTERFACCIA ---
curr = data['current_weather']
st.subheader(f"Temp: {curr['temperature']}°C | Vento: {curr['windspeed']} km/h")

st.write("---")
st.header("🐂 Mostro Bovino Index")
st.caption("Stima probabilità roccia asciutta per settore")

cols = st.columns(2)
for i, (nome, params) in enumerate(settori.items()):
    # Interpolazione "Gaussiana": base + bias meteo + un piccolo rumore random controllato
    prob_base = params[0] + (bovino_bias * 100)
    min_p = int(prob_base - params[1])
    max_p = int(prob_base + params[1])
    
    # Clip per non uscire da 0-100%
    min_p, max_p = max(0, min_p), min(100, max_p)
    
    col_idx = i % 2
    with cols[col_idx]:
        color = "green" if min_p > 70 else "orange" if min_p > 50 else "red"
        st.markdown(f"""
        <div style='background:#262730; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 5px solid {color};'>
            <h3 style='margin:0; color:white;'>{nome}</h3>
            <p style='font-size:24px; margin:0; color:{color}; font-weight:bold;'>{min_p}-{max_p}%</p>
        </div>
        """, unsafe_allow_html=True)

# --- GRAFICI STORICI (Sotto i settori) ---
with st.expander("Vedi grafici dettagliati 10gg"):
    df_hist = pd.DataFrame({
        'Giorno': [d[-5:] for d in hist['daily']['time']],
        'Pioggia (mm)': hist['daily']['precipitation_sum'],
        'Sole (ore)': [round(s / 3600, 1) for s in hist['daily']['sunshine_duration']],
        'Vento Max (km/h)': hist['daily']['wind_speed_10m_max']
    })
    st.bar_chart(df_hist, x='Giorno', y='Pioggia (mm)')
    st.line_chart(df_hist, x='Giorno', y='Vento Max (km/h)')

if st.button("🔄 AGGIORNA"):
    st.rerun()
