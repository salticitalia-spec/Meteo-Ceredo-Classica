import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- UTILS ---
def get_santo(data_obj):
    # Calendario santi aggiornato per il periodo attuale
    santi = {
        "03-16": "S. Eriberto", 
        "03-17": "S. Patrizio",
        "03-18": "S. Cirillo", 
        "03-19": "S. Giuseppe (Festa del Papà)", 
        "03-20": "S. Claudia",
        "03-21": "S. Benedetto"
    }
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

giorni_ita = {
    "Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì",
    "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"
}

mesi_ita = {
    "March": "Marzo", "April": "Aprile", "May": "Maggio"
}

# --- STILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; }
    
    .main-banner {
        background: linear-gradient(90deg, #111 0%, #00FFFF 50%, #111 100%);
        padding: 2px; border-radius: 15px; margin-bottom: 20px;
    }
    .banner-content { background-color: #000; padding: 15px; border-radius: 13px; text-align: center; }
    .banner-title { font-size: 28px; font-weight: 900; letter-spacing: 2px; margin: 0; }
    .banner-desc { font-size: 14px; color: #00FFFF !important; font-weight: 300; margin-top: 5px; }
    
    .info-block {
        background-color: #000000; border: 2px solid #FFFFFF; padding: 25px;
        border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    
    .forecast-card {
        background-color: #0a0a0a; border: 1px solid #333; padding: 15px;
        border-radius: 12px; margin-bottom: 10px;
    }
    .forecast-date { font-size: 18px; font-weight: 800; color: #FFFFFF !important; }
    .santo-mini { font-size: 11px; color: #00FFFF !important; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    
    .stat-val { font-size: 18px; font-weight: 900; display: block; }
    .stat-lab { font-size: 9px; color: #AAA; text-transform: uppercase; font-weight: bold; }
    
    [data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

try:
    data_fc, data_hist = get_weather_data()
    curr = data_fc['current_weather']
    now = datetime.now()
    data_str = f"{giorni_ita.get(now.strftime('%A'))} {now.strftime('%d')} {mesi_ita.get(now.strftime('%B'))}"
except:
    st.error("Errore nel caricamento dati.")
    st.stop()

# --- BLOCCO 1: BANNER ---
st.markdown(f"""
    <div class="main-banner">
        <div class="banner-content">
            <div class="banner-title">CEREDOLESO PRO</div>
            <div class="banner-desc">previsioni meteo falesia di ceredo</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- BLOCCO 2: DATA & REAL-TIME ---
st.markdown(f"""
    <div class="info-block">
        <div class="date-text" style="font-size:20px; font-weight:700;">{data_str}</div>
        <div class="santo-text" style="color:#00FFFF; font-size:12px; font-weight:bold; letter-spacing:2px;">✨ {get_santo(now)}</div>
        <div style="font-size: 70px; font-weight: 900; margin: 15px 0;">{curr['temperature']}°</div>
        <div style="color:#00FF00; font-size:24px; font-weight:800;">💨 {curr['windspeed']} km/h</div>
        <span style="font-size:10px; color:#AAA; text-transform:uppercase;">Vento Attuale</span>
    </div>
""", unsafe_allow_html=True)

# --- NUOVO BLOCCO: PREVISIONI 3 GIORNI ---
st.header("📅 Previsioni 3 Giorni")
for i in range(3):
    d_obj = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d')
    d_label = f"{giorni_ita.get(d_obj.strftime('%A'))} {d_obj.strftime('%d')} {mesi_ita.get(d_obj.strftime('%B'))}"
    
    st.markdown(f"""
        <div class="forecast-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <span class="forecast-date">{d_label}</span><br>
                    <span class="santo-mini">✨ {get_santo(d_obj)}</span>
                </div>
                <div style="text-align: right;">
                    <span style="color:#FF3131; font-weight:900; font-size:20px;">{data_fc['daily']['temperature_2m_max'][i]}°</span>
                    <span style="color:#AAA; font-size:14px;"> / {data_fc['daily']['temperature_2m_min'][i]}°</span>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; border-top: 1px solid #222; padding-top: 10px;">
                <div style="text-align:center;"><span class="stat-lab">Pioggia</span><span class="stat-val" style="color:#00FFFF;">{data_fc['daily']['precipitation_sum'][i]}mm</span></div>
                <div style="text-align:center;"><span class="stat-lab">Vento Max</span><span class="stat-val" style="color:#00FF00;">{data_fc['daily']['windspeed_10m_max'][i]}k/h</span></div>
                <div style="text-align:center;"><span class="stat-lab">Umidità</span><span class="stat-val">Media</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- BLOCCO 3: ANALISI STORICA ---
st.header("📊 Analisi Storica (10 GG)")
st.markdown("<b style='color:#00FFFF;'>■ Pioggia (mm x10)</b> | <b style='color:#00FF00;'>■ Vento (km/h)</b> | <b style='color:#FFFF00;'>■ Irragg. (W/50)</b>", unsafe_allow_html=True)

df_hist = pd.DataFrame({
    'Data': pd.to_datetime(data_hist['hourly']['time']),
    'Pioggia (x10)': [x * 10 for x in data_hist['hourly']['precipitation']],
    'Vento (km/h)': data_hist['hourly']['windspeed_10m'],
    'Irragg (W/50)': [x / 50 for x in data_hist['hourly']['shortwave_radiation']]
}).set_index('Data')
st.line_chart(df_hist, color=["#00FFFF", "#00FF00", "#FFFF00"])

if st.button("🔄 AGGIORNA"):
    st.cache_data.clear()
    st.rerun()
