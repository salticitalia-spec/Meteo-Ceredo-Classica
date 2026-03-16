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
        "03-15": "S. Zaccaria", 
        "03-16": "S. Eriberto", 
        "03-17": "S. Patrizio",
        "03-18": "S. Cirillo", 
        "03-19": "S. Giuseppe", 
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
    "January": "Gennaio", "February": "Febbraio", "March": "Marzo", "April": "Aprile",
    "May": "Maggio", "June": "Giugno", "July": "Luglio", "August": "Agosto",
    "September": "Settembre", "October": "Ottobre", "November": "Novembre", "December": "Dicembre"
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
    .banner-title { font-size: 28px; font-weight: 900; letter-spacing: 2px; margin: 0; line-height: 1.2; }
    .banner-desc { font-size: 14px; color: #00FFFF !important; font-weight: 300; margin-top: 5px; letter-spacing: 1px; }
    
    .info-block {
        background-color: #000000; border: 2px solid #FFFFFF; padding: 25px;
        border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    
    .date-text { font-size: 20px; font-weight: 700; color: #FFFFFF !important; margin-bottom: 2px; }
    .santo-text { font-size: 12px; color: #00FFFF !important; text-transform: uppercase; letter-spacing: 3px; font-weight: bold; }
    
    .main-temp { font-size: 70px; font-weight: 900; line-height: 1; margin: 20px 0; }
    .wind-text { font-size: 26px; color: #00FF00 !important; font-weight: 800; }
    
    .label-desc { font-size: 10px; color: #AAA !important; text-transform: uppercase; letter-spacing: 2px; display: block; margin-top: 4px; }
    
    [data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

# --- RECUPERO DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome"
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

# --- BLOCCO 1: BANNER CON DESCRIZIONE CIANO ---
st.markdown(f"""
    <div class="main-banner">
        <div class="banner-content">
            <div class="banner-title">CEREDOLESO PRO</div>
            <div class="banner-desc">previsioni meteo falesia di ceredo</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- BLOCCO 2: DATA, SANTO, TEMP, VENTO ---
st.markdown(f"""
    <div class="info-block">
        <div class="date-text">{data_str}</div>
        <div class="santo-text">✨ {get_santo(now)}</div>
        <div class="main-temp">{curr['temperature']}°</div>
        <span class="label-desc">Temperatura Attuale</span>
        <div style="margin-top: 20px; border-top: 1px solid #222; padding-top: 15px;">
            <div class="wind-text">💨 {curr['windspeed']} km/h</div>
            <span class="label-desc">Velocità Vento</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- BLOCCO 3: ANALISI STORICA 10 GIORNI ---
st.header("📊 Analisi Storica (10 GG)")
st.markdown("<b style='color:#00FFFF;'>■ Pioggia (mm x10)</b> | <b style='color:#00FF00;'>■ Vento (km/h)</b> | <b style='color:#FFFF00;'>■ Irragg. (W/50)</b>", unsafe_allow_html=True)

df_hist = pd.DataFrame({
    'Data': pd.to_datetime(data_hist['hourly']['time']),
    'Pioggia (x10)': [x * 10 for x in data_hist['hourly']['precipitation']],
    'Vento (km/h)': data_hist['hourly']['windspeed_10m'],
    'Irragg (W/50)': [x / 50 for x in data_hist['hourly']['shortwave_radiation']]
}).set_index('Data')

st.line_chart(df_hist, color=["#00FFFF", "#00FF00", "#FFFF00"])

# --- BLOCCO 4: PREVISIONI 72H ---
st.header("🔮 Previsioni (Prossime 72 Ore)")
df_fc = pd.DataFrame({
    'Data': pd.to_datetime(data_fc['hourly']['time'][:72]),
    'Pioggia (x10)': [x * 10 for x in data_fc['hourly']['precipitation'][:72]],
    'Vento (km/h)': data_fc['hourly']['windspeed_10m'][:72],
    'Irragg (W/50)': [x / 50 for x in data_fc['hourly']['shortwave_radiation'][:72]]
}).set_index('Data')

st.line_chart(df_fc, color=["#00FFFF", "#00FF00", "#FFFF00"])

if st.button("🔄 REFRESH DATI"):
    st.cache_data.clear()
    st.rerun()
