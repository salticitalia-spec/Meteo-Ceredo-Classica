import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- STILE CSS ULTRA-COMPATTO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; }
    
    .current-meteo {
        background-color: #111; border: 2px solid #FFFFFF; padding: 12px;
        border-radius: 12px; text-align: center; margin-bottom: 15px;
    }
    
    .hourly-card {
        background-color: #111; border-left: 3px solid #444; padding: 4px 10px;
        border-radius: 6px; margin-bottom: 3px; display: flex; 
        justify-content: space-between; align-items: center;
        height: 38px;
    }
    .hourly-card.rain { border-left: 3px solid #00CCFF; background-color: #001a33; }
    
    .daily-box {
        background-color: #111; border: 1px solid #333; padding: 6px;
        border-radius: 6px; margin-bottom: 5px; font-size: 12px;
    }

    .bovino-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 5px; border-bottom: 1px solid #222;
    }
    .sector-name { font-size: 15px; font-weight: bold; }
    .sector-perc { font-size: 19px; font-weight: 900; }
    .sun-info { font-size: 9px; color: #FFCC00 !important; display: block; text-transform: uppercase; }
    
    [data-testid="stChart"] { height: 140px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 14px !important; padding: 10px 5px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI API ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,weathercode,shortwave_radiation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    url_hist_hourly = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=shortwave_radiation&timezone=Europe%2FRome"
    
    return requests.get(url_fc).json(), requests.get(url_hist).json(), requests.get(url_hist_hourly).json()

try:
    data_fc, data_hist, data_hourly_hist = get_all_data()
    curr = data_fc['current_weather']
except:
    st.error("Dati non disponibili. Controlla connessione.")
    st.stop()

def get_weather_desc(code):
    mapping = {0: "Sereno", 1: "Quasi Sereno", 2: "Parz. Nuvoloso", 3: "Coperto", 45: "Nebbia", 51: "Pioggerella", 61: "Pioggia", 80: "Rovesci"}
    return mapping.get(code, "Variabile")

st.title("🧗 METEO CEREDOLESO")

# --- 1. ORA ---
st.markdown(f"""
    <div class="current-meteo">
        <div style="font-size: 12px; color: #AAA !important;">{get_weather_desc(curr['weathercode']).upper()}</div>
        <div style="font-size: 38px; font-weight: 900; line-height:1;">{curr['temperature']}°</div>
        <div style="font-size: 15px; color: #00FF00 !important; font-weight: bold;">💨 {curr['windspeed']} km/h</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. TRIORARIE COMPATTE ---
st.markdown("🕒 **Prossime 24 Ore (3h)**")
for i in range(0, 24, 3):
    t = data_fc['hourly']['time'][i].split("T")[1]
    temp = data_fc['hourly']['temperature_2m'][i]
    rain = data_fc['hourly']['precipitation'][i]
    wind = data_fc['hourly']['windspeed_10m'][i]
    rain_class = "rain" if rain > 0 else ""
    st.markdown(f"""
        <div class="hourly-card {rain_class}">
            <div style="font-size:14px; font-weight:bold;">{t}</div>
            <div style="font-size:15px; font-weight:900; color:#FF4B4B;">{temp}°</div>
            <div style="font-size:11px; text-align:right;">
                <span style="color:#00CCFF;">💧 {rain}mm</span> | 💨 {wind} <small>k/h</small>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 3. 3 GIORNI DETTAGLIO ---
st.markdown("📅 **Dettaglio 3 Giorni**")
for i in range(3):
    giorno = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d').upper()
    t_max = data_fc['daily']['temperature_2m_max'][i]
    rain_sum = data_fc['daily']['precipitation_sum'][i]
    sun_h = round(data_fc['daily']['sunshine_duration'][i] / 3600, 1)
    st.markdown(f"""
        <div class="daily-box">
            <b>{giorno}</b>: 🌡️ <b style="color:#FF4B4B;">{t_max}°</b> | 💧 <b>{rain_sum}mm</b> | ☀️ <b>{sun_h}h sole</b>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 4. MOSTRO BOVINO INDEX ---
st.header("🐂 MOSTRO BOVINO INDEX")
st.markdown("<h4 style='color: #888 !important; margin-top: -25px; font-weight: 400;'>(indice di asciugatura)</h4>", unsafe_allow_html=True)

def get_bovino_score(day_offset, boost):
    h_rain = sum(data_hist['daily']['precipitation_sum'])
    h_sun = sum(data_hist['daily']['sunshine_duration']) / 3600
    h_wind = np.mean(data_hist['daily']['wind_speed_10m_max'])
    f_rain = sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    f_sun = sum(data_fc['daily']['sunshine_duration'][:day_offset+1]) / 3600
    bias = ((h_sun + f_sun) * 0.005 * boost) + (h_wind * 0.002) - ((h_rain + f_rain) * 0.14)
    return np.clip(bias, -0.30, 0.15)

settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.40, "09:30 → 13:30"),
    ("🎋 SUPERCANNA", 70, 5, 1.28, "10:30 → 15:00"),
    ("🐕 MONDO CANO", 70, 5, 1.20, "11:30 → 15:30"),
    ("🧠 CEREDOLESO", 77, 3, 1.10, "12:00 → 16:00"),
    ("👴 DEL PECI", 67, 4, 0.95, "13:00 → 16:30"),
    ("🏺 OSTRAMANDRA", 60, 6, 0.80, "13:30 → 16:30")
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

# --- 5. STORICO 10GG (CON TITOLI) ---
st.subheader("📊 Storico 10 Giorni")
dates_h = [d[-5:] for d in data_hist['daily']['time']]

st.markdown("🔹 **Piovosità Giornaliera (mm)**")
st.bar_chart(pd.DataFrame({'D': dates_h, 'mm': data_hist['daily']['precipitation_sum']}), x='D', y='mm', color="#00CCFF")

st.markdown("🔹 **Vento Massimo (km/h)**")
st.line_chart(pd.DataFrame({'D': dates_h, 'kmh': data_hist['daily']['wind_speed_10m_max']}), x='D', y='kmh', color="#00FF00")

st.markdown("🔹 **Radiazione Solare (W/m²)**")
st.area_chart(pd.DataFrame({'T': data_hourly_hist['hourly']['time'], 'W': data_hourly_hist['hourly']['shortwave_radiation']}).set_index('T'), color="#FFFF00")

if st.button("🔄 AGGIORNA"):
    st.rerun()
