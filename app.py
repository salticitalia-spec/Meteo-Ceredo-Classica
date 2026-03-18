import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- 2. FUNZIONI TECNICHE ---
def get_weather_icon(code):
    icons = {0: "☀️", 1: "☀️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️", 51: "🌧️", 53: "🌧️", 55: "🌧️", 61: "🌧️", 63: "🌧️", 65: "🌧️", 71: "❄️", 95: "⚡"}
    return icons.get(code, "☁️")

def get_rain_start(hourly_data, start_index):
    day_rain = hourly_data[start_index : start_index + 24]
    for hour, mm in enumerate(day_rain):
        if mm > 0.1: return f"{hour}:00"
    return None

def calcola_percepita(T, rh):
    if T < 21: return T
    return round(0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (rh * 0.094)), 1)

def get_santo(data_obj):
    santi = {"03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio", "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia", "03-21": "S. Benedetto"}
    return santi.get(data_obj.strftime("%m-%d"), "S. del Giorno")

giorni_ita = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
mesi_ita = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# --- 3. CSS (DESIGN DARK & CLEAN) ---
st.markdown('''
<style>
    .stApp { background-color: #000000 !important; }
    .main-banner {
        background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), url("icona.png");
        background-size: cover; background-position: center;
        padding: 30px 10px; border-radius: 12px; border: 1px solid #1a1a1a;
        text-align: center; margin-bottom: 25px;
    }
    .title-ceredoleso { color: #0FF !important; font-weight: 100 !important; font-size: 26px; letter-spacing: 7px; text-transform: uppercase; font-family: sans-serif; }
    .title-pro { color: #0FF !important; font-weight: 100 !important; font-size: 18px; letter-spacing: 5px; text-transform: uppercase; font-family: sans-serif; opacity: 0.8; }
    .info-card { background-color: #0c0c0c !important; border: 1px solid #222 !important; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .date-text { font-family: sans-serif; font-weight: 100 !important; font-size: 24px; color: #ffffff !important; text-transform: uppercase; letter-spacing: 4px; margin-bottom: 5px; }
    .t-main { font-size: 45px; font-weight: bold; color: #fff; margin: 5px 0; }
    .val-box { display: flex; justify-content: center; gap: 15px; font-size: 17px; margin-top: 10px; }
    .status-alert { font-size: 11px; color: #FF0 !important; font-weight: bold; margin-top: 10px; text-transform: uppercase; letter-spacing: 1px; background: transparent !important; }
    .rain-tag { color: #F31; font-size: 11px; font-weight: bold; border: 1px solid #F31; padding: 4px 10px; border-radius: 5px; display: inline-block; margin: 10px 0; }
    [data-testid="stChart"] { background-color: #050505 !important; border: 1px solid #222; border-radius: 10px; }
    h3 { color: white !important; font-weight: 100 !important; letter-spacing: 2px !important; text-transform: uppercase; margin-top: 30px; }
</style>
''', unsafe_allow_html=True)

# --- 4. DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation,shortwave_radiation,weathercode,windspeed_10m&daily=temperature_2m_max,precipitation_sum,shortwave_radiation_sum,weathercode,windspeed_10m_max&timezone=Europe%2FRome"
    start_d = (datetime.now() - timedelta(days=11)).strftime('%Y-%m-%d')
    end_d = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url_hi = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_d}&end_date={end_d}&hourly=precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome"
    try:
        fc_res = requests.get(url_fc).json()
        hi_res = requests.get(url_hi).json()
        return fc_res, hi_res
    except: return None, None

dfc, dhi = fetch_data()
if dfc is None: st.error("Errore API"); st.stop()

# --- 5. HEADER ---
st.markdown('<div class="main-banner"><div class="title-ceredoleso">Ceredoleso</div><div class="title-pro">PRO</div></div>', unsafe_allow_html=True)

# --- 6. OGGI ---
curr, now = dfc['current_weather'], datetime.now()
c_temp, c_hum = curr["temperature"], dfc['hourly']['relativehumidity_2m'][now.hour]
perc_oggi = calcola_percepita(c_temp, c_hum)
rain_t = get_rain_start(dfc['hourly']['precipitation'], 0)
rain_h = f'<div class="rain-tag">🌧️ INIZIO PIOGGIA: ORE {rain_t}</div>' if rain_t else ""
msg_oggi = "🔥 AFA ELEVATA" if perc_oggi > 30 else ("⚠️ RISCHIO CONDENSA" if c_hum > 75 else "")

st.markdown(f'''
<div class="info-card">
    <div class="date-text">{giorni_ita[now.weekday()]} {now.day} {mesi_ita[now.month-1]}</div>
    <div style="color:#0FF; font-size:11px; margin-bottom:10px;">✨ {get_santo(now)}</div>
    <div style="font-size:50px;">{get_weather_icon(curr["weathercode"])}</div>
    <div class="t-main">{c_temp}°</div>
    <div style="font-size:14px; color:#FF0; font-weight:300;">Percepita: {perc_oggi}°</div>
    <div class="val-box">
        <div style="color:#0F0;">💨 {curr["windspeed"]}kph</div>
        <div style="color:#FF0;">💧 {c_hum}%</div>
        <div style="color:#0FF;">🌧️ {dfc['daily']['precipitation_sum'][0]}mm</div>
    </div>
    {rain_h}
    <div class="status-alert">{msg_oggi}</div>
</div>
''', unsafe_allow_html=True)

# --- 7. MOSTRO BOVINO ---
if dhi and 'hourly' in dhi:
    p_hist = dhi['hourly']['precipitation']
    carico = (sum(p_hist[-72:]) * 1.0) + (sum(p_hist[-168:-72]) * 0.7)
    m_t, m_c, m_d = ("SECCO ☀️", "#0FF", "🟢 Ottimo ovunque.") if carico < 5 else (("UMIDO 💧", "#FF0", "🟡 Peci umide.") if carico < 18 else ("BAGNATO ⚠️", "#F31", "🔴 Bosco saturo."))
    st.markdown(f'<div style="border:1px solid {m_c}; padding:15px; border-radius:12px; text-align:center; margin-bottom:25px;"><div style="font-size:10px; color:#666; text-transform:uppercase;">Mostro Bovino Index</div><div style="font-size:24px; color:{m_c}; font-weight:bold; margin:5px 0;">{m_t}</div><div style="font-size:13px; color:#999;">{m_d}</div></div>', unsafe_allow_html=True)

# --- 8. PREVISIONI 3 GIORNI ---
st.subheader("Prossimi 3 Giorni")
for i in range(1, 4):
    d_obj = datetime.strptime(dfc['daily']['time'][i], '%Y-%m-%d')
    max_t, hum_i = dfc['daily']['temperature_2m_max'][i], int(np.mean(dfc['hourly']['relativehumidity_2m'][i*24:(i+1)*24]))
    perc_i = calcola_percepita(max_t, hum_i)
    msg_i = "🔥 AFA ELEVATA" if perc_i > 30 else ("⚠️ RISCHIO CONDENSA" if hum_i > 75 else "")
    rain_ti = get_rain_start(dfc['hourly']['precipitation'], i*24)
    rain_hi = f'<div class="rain-tag">🌧️ INIZIO PIOGGIA: ORE {rain_ti}</div>' if rain_ti else ""
    
    st.markdown(f'''
    <div
