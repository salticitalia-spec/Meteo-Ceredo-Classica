import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗", layout="centered")

# CSS AD ALTO CONTRASTO
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 900 !important; }
    p, span, div { color: #FFFFFF !important; }
    
    .current-meteo {
        background-color: #111; border: 2px solid #FFFFFF; padding: 15px;
        border-radius: 12px; text-align: center; margin-bottom: 25px;
    }
    
    .fc-card {
        background-color: #000; border: 1px solid #444; padding: 8px;
        border-radius: 8px; text-align: center;
    }

    .historic-section {
        background-color: #111; border: 1px solid #333; padding: 10px;
        border-radius: 8px; margin-bottom: 15px;
    }

    .bovino-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 5px; border-bottom: 1px solid #222;
    }
    .sector-name { font-size: 19px; font-weight: bold; }
    .sector-perc { font-size: 24px; font-weight: 900; }
    .sun-info { font-size: 11px; color: #888 !important; display: block; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data_fc, data_hist = get_all_data()
curr = data_fc['current_weather']

st.title("🧗 METEO CEREDO")

# --- 1. CONDIZIONI ATTUALI ---
st.subheader("📍 Condizioni Attuali")
st.markdown(f"""
    <div class="current-meteo">
        <div style="font-size: 48px; font-weight: 900;">{curr['temperature']}°C</div>
        <div style="font-size: 18px; color: #00FF00 !important; font-weight: bold;">VENTO: {curr['windspeed']} km/h</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. PREVISIONI 3 GIORNI ---
st.subheader("📅 Previsioni 3 Giorni")
cols = st.columns(3)
for i in range(3):
    d = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d').upper()
    rain = data_fc['daily']['precipitation_sum'][i]
    with cols[i]:
        st.markdown(f"""
            <div class="fc-card">
                <b style="font-size:13px;">{d}</b><br>
                <span style="color:#FF4B4B !important; font-weight:bold; font-size:18px;">{data_fc['daily']['temperature_2m_max'][i]}°</span><br>
                <span style="font-size: 12px; color:#00CCFF !important; font-weight:bold;">{rain}mm</span>
            </div>
        """, unsafe_allow_html=True)

st.write("---")

# --- 3. STORICO 10 GIORNI ---
st.subheader("📊 Riepilogo Storico (Ultimi 10gg)")

# Calcolo totali e medie
total_rain = sum(data_hist['daily']['precipitation_sum'])
total_sun_hours = sum(data_hist['daily']['sunshine_duration']) / 3600
avg_wind = np.mean(data_hist['daily']['wind_speed_10m_max'])

st.markdown(f"""
    <div class="historic-section">
        <small>PIOVOSITÀ TOTALE</small>
        <div style="font-size: 22px; font-weight: bold; color: #00CCFF;">{total_rain:.1f} mm</div>
    </div>
    <div class="historic-section">
        <small>IRRAGGIAMENTO TOTALE</small>
        <div style="font-size: 22px; font-weight: bold; color: #FFFF00;">{total_sun_hours:.1f} ore di sole</div>
    </div>
    <div class="historic-section">
        <small>VENTO MEDIO MAX</small>
        <div style="font-size: 22px; font-weight: bold; color: #00FF00;">{avg_wind:.1f} km/h</div>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# --- 4. MOSTRO BOVINO INDEX ---
st.header("🐂 MOSTRO BOVINO INDEX")

def get_bovino_score(day_offset, boost):
    rain_score = (total_rain + sum(data_fc['daily']['precipitation_sum'][:day_offset+1])) * 0.14
    sun_score = (total_sun_hours + (sum(data_fc['daily']['sunshine_duration'][:day_offset+1]) / 3600)) * 0.005 * boost
    wind_score = (avg_wind + np.mean(data_fc['daily']['wind_speed_10m_max'][:day_offset+1])) / 2 * 0.002
    bias = sun_score + wind_score - rain_score
    return np.clip(bias, -0.30, 0.15)

settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.30, "Sole dalle ore 09:30"),
    ("🎋 SUPERCANNA", 70, 5, 1.25, "Sud-Ovest"),
    ("🐕 MONDO CANO", 70, 5, 1.15, "Tarda mattinata"),
    ("🧠 CEREDOLESO", 77, 3, 1.05, "Pieno Mezzogiorno"),
    ("👴 DEL PECI", 67, 4, 0.90, "Primo pomeriggio"),
    ("🏺 OSTRAMANDRA", 60, 6, 0.70, "Ovest / Solo pomeriggio")
]

tabs = st.tabs(["OGGI", "DOMANI", "DOPODOMANI"])
for day in range(3):
    with tabs[day]:
        for nome, base, toll, boost, sun_time in settori:
            bias = get_bovino_score(day, boost)
            prob = int(base + (bias * 100))
            min_p, max_p = np.clip([prob-toll, prob+toll], 0, 100)
            color = "#00FF00" if min_p > 70 else "#FFFF00" if min_p > 50 else "#FF0000"
            
            st.markdown(f"""
                <div class="bovino-row">
                    <div>
                        <span class="sector-name">{nome}</span>
                        <span class="sun-info">{sun_time}</span>
                    </div>
                    <span class="sector-perc" style="color:{color};">{min_p}-{max_p}%</span>
                </div>
            """, unsafe_allow_html=True)

if st.button("🔄 AGGIORNA"):
    st.rerun()
