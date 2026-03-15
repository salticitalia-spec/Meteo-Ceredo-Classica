import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- STILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; }
    
    .current-meteo {
        background-color: #111; border: 2px solid #FFFFFF; padding: 15px;
        border-radius: 12px; text-align: center; margin-bottom: 15px;
    }
    
    .hourly-card {
        background-color: #080808; border-left: 2px solid #333; padding: 2px 10px;
        margin-bottom: 2px; display: flex; 
        justify-content: space-between; align-items: center;
        height: 28px; font-size: 11px;
    }
    
    .daily-card {
        background-color: #111; border: 1px solid #444; padding: 15px;
        border-radius: 12px; margin-bottom: 5px;
    }
    .daily-title { font-size: 18px; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 10px; display: block; }
    .daily-stats { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
    .stat-item { text-align: center; min-width: 60px; margin-bottom: 5px; }
    .stat-val { font-size: 18px; font-weight: 900; display: block; }
    .stat-lab { font-size: 9px; color: #888; text-transform: uppercase; }

    .bovino-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 5px; border-bottom: 1px solid #222;
    }
    .sector-name { font-size: 16px; font-weight: bold; }
    .sector-perc { font-size: 22px; font-weight: 900; }
    .sun-info { font-size: 10px; color: #FFCC00 !important; display: block; }
    
    [data-testid="stChart"] { height: 300px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI API ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration,shortwave_radiation_sum&timezone=Europe%2FRome"
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    # Storico orario per avere il grafico dettagliato
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=precipitation,windspeed_10m,shortwave_radiation&daily=precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    
    return requests.get(url_fc).json(), requests.get(url_hist).json()

try:
    data_fc, data_hist = get_all_data()
    curr = data_fc['current_weather']
except:
    st.error("Errore nel caricamento dati API.")
    st.stop()

st.title("🧗 METEO CEREDOLESO")

# --- 1. ORA ---
st.markdown(f"""
    <div class="current-meteo">
        <div style="font-size: 42px; font-weight: 900; line-height:1;">{curr['temperature']}°</div>
        <div style="font-size: 16px; color: #00FF00 !important; font-weight: bold; margin-top:5px;">💨 {curr['windspeed']} km/h</div>
    </div>
""", unsafe_allow_html=True)

# --- 2. TRIORARIE ---
with st.expander("🕒 DETTAGLIO ORE (3h)", expanded=False):
    for i in range(0, 24, 3):
        t = data_fc['hourly']['time'][i].split("T")[1]
        temp = data_fc['hourly']['temperature_2m'][i]
        rain = data_fc['hourly']['precipitation'][i]
        wind = data_fc['hourly']['windspeed_10m'][i]
        st.markdown(f"""
            <div class="hourly-card">
                <b>{t}</b> <span>{temp}°</span> <span style="color:#00CCFF;">💧{rain}mm</span> <span style="color:#00FF00;">💨{wind}k/h</span>
            </div>
        """, unsafe_allow_html=True)

# --- 3. 3 GIORNI ---
st.subheader("📅 Previsioni 3 Giorni")
for i in range(3):
    giorno = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%A %d %B').upper()
    t_max = data_fc['daily']['temperature_2m_max'][i]
    rain = data_fc['daily']['precipitation_sum'][i]
    wind = data_fc['daily']['wind_speed_10m_max'][i]
    irr_sum = round(data_fc['daily']['shortwave_radiation_sum'][i], 1)
    
    st.markdown(f"""
        <div class="daily-card">
            <span class="daily-title">{giorno}</span>
            <div class="daily-stats">
                <div class="stat-item"><span class="stat-lab">Max</span><span class="stat-val" style="color:#FF4B4B;">{t_max}°</span></div>
                <div class="stat-item"><span class="stat-lab">Pioggia</span><span class="stat-val" style="color:#00CCFF;">{rain}<small>mm</small></span></div>
                <div class="stat-item"><span class="stat-lab">Vento</span><span class="stat-val" style="color:#00FF00;">{wind}<small>k/h</small></span></div>
                <div class="stat-item"><span class="stat-lab">Irragg.</span><span class="stat-val" style="color:#FFCC00;">{irr_sum}<small>MJ</small></span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- 4. GRAFICO UNIFICATO (PREVISIONI 72h) ---
st.subheader("📊 Analisi Combinata (72h)")
st.markdown("<small>🟨 kW/m² | 🟦 Pioggia (mm) | 🟩 Vento (km/h)</small>", unsafe_allow_html=True)

df_fc_chart = pd.DataFrame({
    'Data': pd.to_datetime(data_fc['hourly']['time'][:72]),
    'kW/m²': [x / 1000 for x in data_fc['hourly']['shortwave_radiation'][:72]],
    'Pioggia (mm)': data_fc['hourly']['precipitation'][:72],
    'Vento (km/h)': data_fc['hourly']['windspeed_10m'][:72]
}).set_index('Data')

st.line_chart(df_fc_chart, color=["#FFCC00", "#00CCFF", "#00FF00"])

st.write("---")

# --- 5. MOSTRO BOVINO INDEX ---
st.header("🐂 MOSTRO BOVINO INDEX")
def get_bovino_score(day_offset, boost):
    h_rain = sum(data_hist['daily']['precipitation_sum'])
    h_sun = sum(data_hist['daily']['sunshine_duration']) / 3600
    f_rain = sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    f_sun = sum(data_fc['daily']['sunshine_duration'][:day_offset+1]) / 3600
    bias = ((h_sun + f_sun) * 0.005 * boost) - ((h_rain + f_rain) * 0.14)
    return np.clip(bias, -0.30, 0.15)

settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.40, "Sole: 09:30 → 13:30"),
    ("🎋 SUPERCANNA", 70, 5, 1.28, "Sole: 10:30 → 15:00"),
    ("🧠 CEREDOLESO", 77, 3, 1.10, "Sole: 12:00 → 16:00"),
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
                    <div><span class="sector-name">{nome}</span><span class="sun-info">{sun_time}</span></div>
                    <span class="sector-perc" style="color:{color};">{min_p}-{max_p}%</span>
                </div>
            """, unsafe_allow_html=True)

st.write("---")

# --- 6. STORICO 10 GIORNI (GRAFICO UNIFICATO) ---
st.subheader("📊 Storico 10 Giorni")
st.markdown("<small>🟨 kW/m² | 🟦 Pioggia (mm) | 🟩 Vento (km/h)</small>", unsafe_allow_html=True)

df_hist_chart = pd.DataFrame({
    'Data': pd.to_datetime(data_hist['hourly']['time']),
    'kW/m²': [x / 1000 for x in data_hist['hourly']['shortwave_radiation']],
    'Pioggia (mm)': data_hist['hourly']['precipitation'],
    'Vento (km/h)': data_hist['hourly']['windspeed_10m']
}).set_index('Data')

st.line_chart(df_hist_chart, color=["#FFCC00", "#00CCFF", "#00FF00"])

if st.button("🔄 AGGIORNA"):
    st.rerun()
