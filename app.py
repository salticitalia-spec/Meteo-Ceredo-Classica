import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗", layout="centered")

# --- STILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; }
    .current-meteo {
        background-color: #111; border: 2px solid #FFFFFF; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    .fc-card {
        background-color: #000; border: 1px solid #444; padding: 10px;
        border-radius: 8px; text-align: center;
    }
    .bovino-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 15px 5px; border-bottom: 1px solid #222;
    }
    .sector-name { font-size: 18px; font-weight: bold; }
    .sector-perc { font-size: 22px; font-weight: 900; }
    .sun-info { font-size: 11px; color: #FFCC00 !important; display: block; text-transform: uppercase; font-weight: bold; }
    [data-testid="stChart"] { height: 180px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    url_hist_hourly = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=shortwave_radiation&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json(), requests.get(url_hist_hourly).json()

data_fc, data_hist, data_hourly = get_all_data()
curr = data_fc['current_weather']

st.title("🧗 METEO CEREDO")

# --- 1. ATTUALE ---
st.subheader("📍 Condizioni Attuali")
st.markdown(f"""
    <div class="current-meteo">
        <div style="font-size: 52px; font-weight: 900;">{curr['temperature']}°C</div>
        <div style="font-size: 18px; color: #00FF00 !important; font-weight: bold;">VENTO: {curr['windspeed']} km/h</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. PREVISIONI ---
st.subheader("📅 Prossimi 3 Giorni")
cols = st.columns(3)
for i in range(3):
    d = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d').upper()
    rain = data_fc['daily']['precipitation_sum'][i]
    with cols[i]:
        st.markdown(f"""
            <div class="fc-card">
                <b style="font-size:12px; color:#AAA;">{d}</b><br>
                <span style="color:#FF4B4B !important; font-weight:900; font-size:20px;">{data_fc['daily']['temperature_2m_max'][i]}°</span><br>
                <span style="font-size: 13px; color:#00CCFF !important; font-weight:bold;">{rain}mm</span>
            </div>
        """, unsafe_allow_html=True)

st.write("---")

# --- 3. STORICO GRAFICO ---
st.subheader("📊 Riepilogo Storico (10gg)")
dates_hist = [d[-5:] for d in data_hist['daily']['time']]

st.markdown("🔹 **Piovosità (mm)**")
df_rain = pd.DataFrame({'Data': dates_hist, 'Pioggia': data_hist['daily']['precipitation_sum']})
st.bar_chart(df_rain, x='Data', y='Pioggia', color="#00CCFF")

st.markdown("🔹 **Vento Max (km/h)**")
df_wind = pd.DataFrame({'Data': dates_hist, 'Vento': data_hist['daily']['wind_speed_10m_max']})
st.line_chart(df_wind, x='Data', y='Vento', color="#00FF00")

st.markdown("🔹 **Radiazione Solare (W/m²) - Ciclo 24h**")
df_sun = pd.DataFrame({'Time': data_hourly['hourly']['time'], 'Radiazione': data_hourly['hourly']['shortwave_radiation']})
st.area_chart(df_sun.set_index('Time'), color="#FFFF00")

st.write("---")

# --- 4. MOSTRO BOVINO INDEX (Indice di Asciugatura) ---
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

# SETTORI CON AGGIORNAMENTO SUPERCANNA (SOLE FINO ORE 15:00)
settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.40, "Sole: 09:30 → 13:30"),
    ("🎋 SUPERCANNA", 70, 5, 1.28, "Sole: 10:30 → 15:00"),
    ("🐕 MONDO CANO", 70, 5, 1.20, "Sole: 11:30 → 15:30"),
    ("🧠 CEREDOLESO", 77, 3, 1.10, "Sole: 12:00 → 16:00"),
    ("👴 DEL PECI", 67, 4, 0.95, "Sole: 13:00 → 16:30"),
    ("🏺 OSTRAMANDRA", 60, 6, 0.80, "Sole: 13:30 → 16:30 (Ponte Veja)")
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
