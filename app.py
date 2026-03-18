import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- 2. FUNZIONI TECNICHE ---
def get_weather_icon(code):
    icons = {0: "☀️", 1: "☀️", 2: "⛅", 3: "☁️", 45: "🌫️", 51: "🌧️", 61: "🌧️", 95: "⚡"}
    return icons.get(code, "☁️")

def calcola_percepita(T, rh):
    if T < 21: return T
    return round(0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (rh * 0.094)), 1)

def get_santo(data_obj):
    santi = {
        "03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio", 
        "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia", 
        "03-21": "S. Benedetto", "03-22": "S. Lea", "03-23": "S. Turibio"
    }
    return santi.get(data_obj.strftime("%m-%d"), "S. del Giorno")

giorni_ita = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
mesi_ita = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# --- 3. CSS "BLACKOUT" ---
st.markdown('''
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
    }
    .main-card {
        border: 1px solid #333;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        text-align: center;
        background: #000000 !important;
    }
    .header-text {
        color: #00FFFF !important;
        font-weight: 100 !important;
        letter-spacing: 7px;
        text-transform: uppercase;
        font-size: 26px;
        text-align: center;
        margin: 20px 0;
    }
    .status-alert {
        display: inline-block;
        padding: 8px 15px;
        border: 1px solid #FFD700;
        border-radius: 5px;
        color: #FFD700 !important;
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-top: 15px;
        background: transparent !important;
    }
    [data-testid="stChart"] {
        background-color: #080808 !important;
        border: 1px solid #222;
        border-radius: 10px;
        padding: 10px;
    }
</style>
''', unsafe_allow_html=True)

# --- 4. DATA FETCHING (Forecast + 10gg History) ---
@st.cache_data(ttl=3600)
def fetch_all_data():
    lat, lon = 45.6117, 10.9710
    try:
        # Previsioni
        url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=temperature_2m_max,precipitation_sum,weathercode&timezone=Europe%2FRome"
        # Storico 10 giorni
        start_hi = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        end_hi = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        url_hi = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_hi}&end_date={end_hi}&hourly=precipitation,windspeed_10m,shortwave_radiation&timezone=Europe%2FRome"
        
        fc = requests.get(url_fc).json()
        hi = requests.get(url_hi).json()
        return fc, hi
    except:
        return None, None

dfc, dhi = fetch_all_data()

if not dfc:
    st.error("Connessione fallita.")
    st.stop()

# --- 5. RENDER OGGI ---
st.markdown('<div class="header-text">Ceredoleso PRO</div>', unsafe_allow_html=True)

curr, now = dfc['current_weather'], datetime.now()
c_temp, c_hum = curr['temperature'], dfc['hourly']['relativehumidity_2m'][now.hour]
perc = calcola_percepita(c_temp, c_hum)

alert_msg = ""
if perc > 30: alert_msg = '<div class="status-alert">🔥 AFA ELEVATA</div>'
elif c_hum > 75: alert_msg = '<div class="status-alert">⚠️ RISCHIO CONDENSA</div>'

st.markdown(f'''
<div class="main-card">
    <div style="font-weight:100; font-size:22px; color:white; letter-spacing:3px; text-transform:uppercase;">
        {giorni_ita[now.weekday()]} {now.day} {mesi_ita[now.month-1]}
    </div>
    <div style="color:#00FFFF; font-size:11px; margin:8px 0;">✨ {get_santo(now)}</div>
    <div style="font-size:55px; margin:15px 0;">{get_weather_icon(curr['weathercode'])}</div>
    <div style="font-size:50px; font-weight:bold; color:white;">{c_temp}°</div>
    <div style="color:#FFFF00; font-size:13px;">Percepita: {perc}°</div>
    <div style="display:flex; justify-content:center; gap:25px; margin-top:20px; color:#00FF00; font-weight:bold; font-size:14px;">
        <span>💨 {curr['windspeed']} kph</span>
        <span style="color:#FFFF00;">💧 {c_hum}%</span>
    </div>
    {alert_msg}
</div>
''', unsafe_allow_html=True)

# --- 6. MOSTRO BOVINO ---
if dhi and 'hourly' in dhi:
    carico = sum(dhi['hourly']['precipitation'][-168:]) # Ultimi 7 giorni
    if carico < 5: m_t, m_c, m_d = "SECCO ☀️", "#00FFFF", "🟢 Ottimo ovunque"
    elif carico < 18: m_t, m_c, m_d = "UMIDO 💧", "#FFFF00", "🟡 Peci & Ostramandra umide"
    else: m_t, m_c, m_d = "BAGNATO ⚠️", "#FF3311", "🔴 Bosco saturo"
    
    st.markdown(f'''
    <div style="border:1px solid {m_c}; padding:15px; border-radius:15px; text-align:center;">
        <div style="font-size:9px; color:#666; letter-spacing:2px;">MOSTRO BOVINO INDEX</div>
        <div style="font-size:22px; color:{m_c}; font-weight:bold; margin:3px 0;">{m_t}</div>
        <div style="font-size:12px; color:#999;">{m_d}</div>
    </div>
    ''', unsafe_allow_html=True)

# --- 7. TENDENZA 3 GIORNI (Con Santi) ---
st.write("")
st.markdown('<div style="color:white; font-weight:100; letter-spacing:2px; text-align:center; font-size:14px; margin-bottom:15px;">TENDENZA 3 GIORNI</div>', unsafe_allow_html=True)
cols = st.columns(3)
for i in range(1, 4):
    with cols[i-1]:
        d_future = now + timedelta(days=i)
        st.markdown(f'''
        <div class="main-card" style="padding:15px; border-color:#222;">
            <div style="font-size:11px; color:white; font-weight:bold;">{giorni_ita[d_future.weekday()][:3].upper()} {d_future.day}</div>
            <div style="font-size:9px; color:#00FFFF; margin-top:4px;">{get_santo(d_future)}</div>
            <div style="font-size:32px; margin:10px 0;">{get_weather_icon(dfc['daily']['weathercode'][i])}</div>
            <div style="font-size:20px; font-weight:bold; color:white;">{dfc['daily']['temperature_2m_max'][i]}°</div>
            <div style="font-size:10px; color:#666;">{dfc['daily']['precipitation_sum'][i]}mm</div>
        </div>
        ''', unsafe_allow_html=True)

# --- 8. STORICO 10 GIORNI ---
if dhi and 'hourly' in dhi:
    st.write("")
    st.markdown('<div style="color:white; font-weight:100; letter-spacing:2px; text-align:center; font-size:14px; margin-bottom:15px;">STORICO 10 GIORNI</div>', unsafe_allow_html=True)
    df_h = pd.DataFrame({
        'Pioggia (mmx10)': [x*10 for x in dhi['hourly']['precipitation']],
        'Vento (kph)': dhi['hourly']['windspeed_10m'],
        'Asciugatura': [x/50 for x in dhi['hourly']['shortwave_radiation']]
    }, index=pd.to_datetime(dhi['hourly']['time']))
    st.line_chart(df_h, color=["#00FFFF", "#00FF00", "#FFFF00"])

if st.button("🔄 AGGIORNA"):
    st.cache_data.clear()
    st.rerun()
