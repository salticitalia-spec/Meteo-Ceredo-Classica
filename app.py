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

# CSS per il layout "Mostro Bovino"
st.markdown("""
    <style>
    .meteo-card {
        background-color: #1E1E1E;
        border: 2px solid #444;
        border-radius: 15px;
        padding: 10px;
        text-align: center;
        color: white !important;
    }
    .bovino-container {
        background-color: #262730;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #444;
    }
    .bovino-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .bovino-name { font-size: 18px; font-weight: bold; color: white; }
    .bovino-perc { font-size: 20px; font-weight: bold; }
    
    .progress-bg {
        background-color: #444;
        border-radius: 20px;
        width: 100%;
        height: 12px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 20px;
        transition: width 0.5s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧗 Meteo Ceredo")

# --- FUNZIONI DATI ---
def get_weather_info(code):
    mapping = {0: ("☀️", "Sereno"), 1: ("🌤️", "Quasi Sereno"), 2: ("⛅", "Poco Nuvoloso"), 3: ("☁️", "Nuvoloso"), 61: ("🌧️", "Pioggia"), 95: ("⛈️", "Temporale")}
    return mapping.get(code, ("☁️", "Nuvole"))

def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data_fc, data_hist = get_all_data()

def get_bovino_score(day_offset, boost):
    rain = sum(data_hist['daily']['precipitation_sum']) + sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    sun = (sum(data_hist['daily']['sunshine_duration']) + sum(data_fc['daily']['sunshine_duration'][:day_offset+1])) / 3600
    bias = (sun * 0.005 * boost) - (rain * 0.14)
    return np.clip(bias, -0.30, 0.15)

# --- SETTORI ---
settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.25),
    ("🎋 SUPERCANNA", 70, 5, 1.20),
    ("🐕 MONDO CANO", 70, 5, 1.10),
    ("🧠 CEREDOLESO", 77, 3, 1.00),
    ("👴 DEL PECI", 67, 4, 0.85),
    ("🏺 OSTRAMANDRA", 60, 6, 0.70)
]

# --- UI PREVISIONI ---
cols_m = st.columns(3)
for i in range(3):
    giorno = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d')
    ico, txt = get_weather_info(data_fc['daily']['weathercode'][i])
    with cols_m[i]:
        st.markdown(f'<div class="meteo-card"><b>{giorno}</b><br><span style="font-size:30px">{ico}</span><br><small>{txt}</small></div>', unsafe_allow_html=True)

st.write("---")
# TITOLO AGGIORNATO
st.header("🐂 Mostro Bovino Index (analisi asciugatura)")

tabs = st.tabs(["OGGI", "DOMANI", "DOPODOMANI"])

for day in range(3):
    with tabs[day]:
        for nome, base, toll, boost in settori:
            bias = get_bovino_score(day, boost)
            prob = int(base + (bias * 100))
            min_p, max_p = np.clip([prob-toll, prob+toll], 0, 100)
            color = "#28a745" if min_p > 70 else "#fd7e14" if min_p > 50 else "#dc3545"
            
            st.markdown(f"""
                <div class="bovino-container">
                    <div class="bovino-header">
                        <div class="bovino-name">🐂 {nome}</div>
                        <div class="bovino-perc" style="color:{color};">{min_p}-{max_p}%</div>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" style="width: {min_p}%; background-color: {color};"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

if st.button("🔄 AGGIORNA DATI"):
    st.rerun()
