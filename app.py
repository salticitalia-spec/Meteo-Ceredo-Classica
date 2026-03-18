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
    # Database Santi 15-21 Marzo
    santi = {
        "03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio", 
        "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia", 
        "03-21": "S. Benedetto"
    }
    return santi.get(data_obj.strftime("%m-%d"), "S. del Giorno")

giorni_ita = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
mesi_ita = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# --- 3. CSS "TOTAL BLACK" (Nessun blocco bianco ammesso) ---
st.markdown('''
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
    }
    .main-card {
        border: 1px solid #333;
        border-radius: 20px;
        padding: 30px;
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
    .date-title {
        font-weight: 100;
        font-size: 24px;
        color: #FFFFFF !important;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .status-alert {
        display: inline-block;
        padding: 8px 15px;
        border: 1px solid #FFD700;
        border-radius: 5px;
        color: #FFD700 !important;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-top: 15px;
        background: transparent !important;
    }
</style>
''', unsafe_allow_html=True)

# --- 4. DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_meteo_data():
    lat, lon = 45.6117, 10.9710
    # Forecast + History per Mostro Bovino
    try:
        url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=temperature_2m_max,precipitation_sum,weathercode&timezone=Europe%2FRome"
        url_hi = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={(datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')}&end_date={(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')}&hourly=precipitation&timezone=Europe%2FRome"
        
        fc = requests.get(url_fc).json()
        hi = requests.get(url_hi).json()
        return fc, hi
    except:
        return None, None

dfc, dhi = fetch_meteo_data()

if not dfc:
    st.error("⚠️ Servizio meteo non raggiungibile.")
    st.stop()

# --- 5. INTERFACCIA ---
st.markdown('<div class="header-text">Ceredoleso PRO</div>', unsafe_allow_html=True)

curr, now = dfc['current_weather'], datetime.now()
c_temp, c_hum = curr['temperature'], dfc['hourly']['relativehumidity_2m'][now.hour]
perc = calcola_percepita(c_temp, c_hum)

# Card Principale Oggi
alert_msg = ""
if perc > 30: alert_msg = '<div class="status-alert">🔥 AFA ELEVATA</div>'
elif c_hum > 75: alert_msg = '<div class="status-alert">⚠️ RISCHIO CONDENSA</div>'

st.markdown(f'''
<div class="main-card">
    <div class="date-title">{giorni_ita[now.weekday()]} {now.day} {mesi_ita[now.month-1]}</div>
    <div style="color:#00FFFF; font-size:12px; margin:10px 0;">✨ {get_santo(now)}</div>
    <div style="font-size:60px;">{get_weather_icon(curr['weathercode'])}</div>
    <div style="font-size:55px; font-weight:bold; color:white;">{c_temp}°</div>
    <div style="color:#FFFF00; font-size:14px;">Percepita: {perc}°</div>
    <div style="display:flex; justify-content:center; gap:25px; margin-top:20px; color:#00FF00; font-weight:bold;">
        <span>💨 {curr['windspeed']} kph</span>
        <span style="color:#FFFF00;">💧 {c_hum}%</span>
    </div>
    {alert_msg}
</div>
''', unsafe_allow_html=True)

# --- 6. MOSTRO BOVINO INDEX (Integrità Legenda) ---
if dhi and 'hourly' in dhi:
    carico = sum(dhi['hourly']['precipitation'])
    if carico < 5: 
        m_t, m_c, m_d = "SECCO ☀️", "#00FFFF", "🟢 Ottimo ovunque"
    elif carico < 18: 
        m_t, m_c, m_d = "UMIDO 💧", "#FFFF00", "🟡 Peci & Ostramandra umide"
    else: 
        m_t, m_c, m_d = "BAGNATO ⚠️", "#FF3311", "🔴 Bosco saturo"
    
    st.markdown(f'''
    <div style="border:1px solid {m_c}; padding:15px; border-radius:15px; text-align:center;">
        <div style="font-size:10px; color:#666; letter-spacing:2px;">MOSTRO BOVINO INDEX</div>
        <div style="font-size:24px; color:{m_c}; font-weight:bold; margin:5px 0;">{m_t}</div>
        <div style="font-size:13px; color:#999;">{m_d}</div>
    </div>
    ''', unsafe_allow_html=True)

# --- 7. TENDENZA 3 GIORNI ---
st.markdown('<div style="margin-top:40px; color:white; font-weight:100; letter-spacing:2px; text-align:center;">PROSSIMI 3 GIORNI</div>', unsafe_allow_html=True)
cols = st.columns(3)
for i in range(1, 4):
    with cols[i-1]:
        d_obj = now + timedelta(days=i)
        st.markdown(f'''
        <div class="main-card" style="padding:15px; border-color:#222;">
            <div style="font-size:12px; color:white;">{giorni_ita[d_obj.weekday()][:3].upper()} {d_obj.day}</div>
            <div style="font-size:35px; margin:10px 0;">{get_weather_icon(dfc['daily']['weathercode'][i])}</div>
            <div style="font-size:22px; font-weight:bold; color:#00FFFF;">{dfc['daily']['temperature_2m_max'][i]}°</div>
            <div style="font-size:10px; color:#666;">{dfc['daily']['precipitation_sum'][i]}mm</div>
        </div>
        ''', unsafe_allow_html=True)

if st.button("🔄 AGGIORNA"):
    st.cache_data.clear()
    st.rerun()
