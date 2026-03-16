import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- UTILS ---
def get_santo(data_obj):
    santi = {
        "03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio",
        "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia"
    }
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

# --- STILE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Helvetica', sans-serif; }
    .main-banner {
        background: linear-gradient(90deg, #111 0%, #00FFFF 50%, #111 100%);
        padding: 2px; border-radius: 15px; margin-bottom: 20px;
    }
    .banner-content { background-color: #000; padding: 20px; border-radius: 13px; text-align: center; }
    .banner-title { font-size: 32px; font-weight: 900; letter-spacing: 2px; margin: 0; }
    .current-meteo {
        background-color: #000000; border: 3px solid #FFFFFF; padding: 20px;
        border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    .label-desc { font-size: 10px; color: #AAA !important; text-transform: uppercase; letter-spacing: 2px; }
    [data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    # Forecast
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation&daily=temperature_2m_max,precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    # Historical (10 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome"
    
    return requests.get(url_fc).json(), requests.get(url_hist).json()

try:
    data_fc, data_hist = get_weather_data()
    curr = data_fc['current_weather']
except:
    st.error("Errore API.")
    st.stop()

# --- HEADER ---
st.markdown('<div class="main-banner"><div class="banner-content"><div class="banner-title">CEREDOLESO PRO</div></div></div>', unsafe_allow_html=True)

# --- CURRENT ---
st.markdown(f"""
    <div class="current-meteo">
        <div style="font-size: 55px; font-weight: 900;">{curr['temperature']}°</div>
        <span class="label-desc">Temperatura Attuale</span>
    </div>
""", unsafe_allow_html=True)

# --- ANALISI STORICA 10 GIORNI (RICHIESTA) ---
st.header("📊 Analisi Storica (Ultimi 10 Giorni)")
st.markdown("""
<div style="margin-bottom: 10px;">
    <b style='color:#00FFFF;'>■ Pioggia (mm x10)</b> | 
    <b style='color:#00FF00;'>■ Vento (km/h)</b> | 
    <b style='color:#FFFF00;'>■ Irragg. (W/50)</b>
</div>
""", unsafe_allow_html=True)

# Creazione DataFrame Storico
df_hist = pd.DataFrame({
    'Data': pd.to_datetime(data_hist['hourly']['time']),
    'Pioggia (x10)': [x * 10 for x in data_hist['hourly']['precipitation']],
    'Vento (km/h)': data_hist['hourly']['windspeed_10m'],
    'Irragg (W/50)': [x / 50 for x in data_hist['hourly']['shortwave_radiation']]
}).set_index('Data')

# Grafico Lineare Storico
st.line_chart(df_hist, color=["#00FFFF", "#00FF00", "#FFFF00"])

# Tabella riassuntiva pioggia caduta
total_rain = sum(data_hist['hourly']['precipitation'])
st.info(f"💧 Pioggia totale accumulata negli ultimi 10 giorni: **{round(total_rain, 2)} mm**")

st.write("---")

# --- ANALISI PREVISIONI (72h) ---
st.subheader("🔮 Previsioni Prossime 72 Ore")
df_fc = pd.DataFrame({
    'Data': pd.to_datetime(data_fc['hourly']['time'][:72]),
    'Pioggia (x10)': [x * 10 for x in data_fc['hourly']['precipitation'][:72]],
    'Vento (km/h)': data_fc['hourly']['windspeed_10m'][:72],
    'Irragg (W/50)': [x / 50 for x in data_fc['hourly']['shortwave_radiation'][:72]]
}).set_index('Data')
st.line_chart(df_fc, color=["#00FFFF", "#00FF00", "#FFFF00"])

if st.button("🔄 REFRESH"):
    st.cache_data.clear()
    st.rerun()
