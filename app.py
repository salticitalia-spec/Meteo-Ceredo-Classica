import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗", layout="centered")

# --- STILE CSS OTTIMIZZATO PER LEGGIBILITÀ ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; }
    
    /* Box Condizioni Attuali */
    .current-meteo {
        background-color: #111; border: 2px solid #FFFFFF; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    
    /* Card Triorarie (Mobile Friendly) */
    .hourly-card {
        background-color: #111; border-left: 5px solid #444; padding: 12px;
        border-radius: 8px; margin-bottom: 8px; display: flex; 
        justify-content: space-between; align-items: center;
    }
    .hourly-card.rain { border-left: 5px solid #00CCFF; background-color: #001a33; }
    .hour-text { font-size: 18px; font-weight: bold; width: 60px; }
    .temp-text { font-size: 20px; font-weight: 900; color: #FF4B4B; width: 60px; }
    .data-text { font-size: 14px; text-align: right; }

    /* Box Mostro Bovino */
    .bovino-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 15px 5px; border-bottom: 1px solid #222;
    }
    .sector-name { font-size: 18px; font-weight: bold; }
    .sector-perc { font-size: 24px; font-weight: 900; }
    .sun-info { font-size: 11px; color: #FFCC00 !important; display: block; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,weathercode&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    url_hist_hourly = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=shortwave_radiation&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json(), requests.get(url_hist_hourly).json()

data_fc, data_hist, data_hourly_hist = get_all_data()
curr = data_fc['current_weather']

def get_weather_desc(code):
    mapping = {0: "Sereno", 1: "Quasi Sereno", 2: "Parz. Nuvoloso", 3: "Coperto", 45: "Nebbia", 51: "Pioggerella", 61: "Pioggia", 80: "Rovesci"}
    return mapping.get(code, "Variabile")

st.title("🧗 METEO CEREDO")

# --- 1. ATTUALE ---
st.subheader("📍 Ora")
st.markdown(f"""
    <div class="current-meteo">
        <div style="font-size: 16px; color: #AAA !important;">{get_weather_desc(curr['weathercode']).upper()}</div>
        <div style="font-size: 52px; font-weight: 900;">{curr['temperature']}°</div>
        <div style="font-size: 18px; color: #00FF00 !important; font-weight: bold;">💨 {curr['windspeed']} km/h</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. PREVISIONI TRIORARIE (CARD LEGGIBILI) ---
st.subheader("🕒 Prossime 24 Ore (Ogni 3h)")
h_times = data_fc['hourly']['time'][:24:3]
h_temps = data_fc['hourly']['temperature_2m'][:24:3]
h_rain = data_fc['hourly']['precipitation'][:24:3]
h_wind = data_fc['hourly']['windspeed_10m'][:24:3]

for t, temp, rain, wind in zip(h_times, h_temps, h_rain, h_wind):
    ora = t.split("T")[1]
    rain_class = "rain" if rain > 0 else ""
    rain_text = f"<span style='color:#00CCFF;'>💧 {rain}mm</span>" if rain > 0 else "💧 0mm"
    
    st.markdown(f"""
        <div class="hourly-card {rain_class}">
            <div class="hour-text">{ora}</div>
            <div class="temp-text">{temp}°</div>
            <div class="data-text">
                {rain_text}<br>
                💨 {wind} <small>km/h</small>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 3. MOSTR0 BOVINO INDEX ---
st.header("🐂 MOSTRO BOVINO INDEX")
st.markdown("<h4 style='color: #888 !important; margin-top: -25px; font-weight: 400;'>(indice di asciugatura)</h4>", unsafe_allow_html=True)

def get_bovino_score(day_offset, boost):
    hist_rain = sum(data_hist['daily']['precipitation_sum'])
    hist_sun = sum(data_hist['daily']['sunshine_duration']) / 3600
    hist_wind = np.mean(data_hist['daily']['wind_speed_10m_max'])
    fc_rain = sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    fc_sun = sum(data_fc['daily']['sunshine_duration'][:day_offset+1]) / 3600
    bias = ((hist_sun + fc_sun) * 0.005 * boost) + (hist_wind * 0.002) - ((hist_rain + fc_rain) * 0.14)
    return np.clip(bias, -0.30, 0.15)

settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.40, "Sole: 09:30 → 13:30"),
    ("🎋 SUPERCANNA", 70, 5, 1.28, "Sole: 10:30 → 15:00"),
    ("🐕 MONDO CANO", 70, 5, 1.20, "Sole: 11:30 → 15:30"),
    ("🧠 CEREDOLESO", 77, 3, 1.10, "Sole: 12:00 → 16:00"),
    ("👴 DEL PECI", 67, 4, 0.95, "Sole: 13:00 → 16:30"),
    ("🏺 OSTRAMANDRA", 60, 6, 0.80, "Sole: 13:30 → 16:30")
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

st.write("---")
# --- 4. STORICO (GRAFICI PICCOLI) ---
st.subheader("📊 Storico 10gg")
dates_h = [d[-5:] for d in data_hist['daily']['time']]
st.bar_chart(pd.DataFrame({'D': dates_h, 'mm': data_hist['daily']['precipitation_sum']}), x='D', y='mm', color="#00CCFF")

if st.button("🔄 AGGIORNA"):
    st.rerun()
