import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- PARAMETRI DI SOGLIA ---
THRESHOLD_LOW = 7000   
THRESHOLD_HIGH = 13500 

# --- UTILS ---
def get_santo(data_obj):
    santi = {
        "03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio",
        "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia",
        "03-21": "S. Benedetto"
    }
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

giorni_ita = {"Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì", "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"}
mesi_ita = {"March": "Marzo", "April": "Aprile", "May": "Maggio"}

# --- MOSTRO BOVINO INDEX (MODELLO BOSCO) ---
def calcola_stato_parete(data_hist):
    try:
        pioggia_oraria = data_hist['hourly']['precipitation']
        recent = sum(pioggia_oraria[-72:])     
        medium = sum(pioggia_oraria[-168:-72])  
        remote = sum(pioggia_oraria[-240:-168]) 
        
        carico_idrico = (recent * 1.0) + (medium * 0.7) + (remote * 0.4)
        
        if carico_idrico < 5:
            return "SECCO ☀️", "#00FFFF", "Ottimo ovunque, anche su Peci & Ostramandra."
        elif carico_idrico < 18:
            return "UMIDO 💧", "#FFFF00", "Mangiafuoco e Torre OK. Peci & Ostramandra: canne umide."
        else:
            return "BAGNATO ⚠️", "#FF3131", "Saturazione bosco. Peci & Ostramandra impraticabile."
    except:
        return "N.D.", "#333", "Errore sensori."

# --- STILE CSS ---
st.markdown(f'''
    <style>
    .stApp {{ background-color: #000000 !important; }}
    h1, h2, h3, h4, p, span, div {{ color: #FFFFFF !important; font-family: 'Inter', sans-serif; }}
    .main-banner {{ background: linear-gradient(90deg, #000 0%, #00FFFF 50%, #000 100%); padding: 1px; border-radius: 10px; margin-bottom: 25px; }}
    .banner-content {{ background-color: #000; padding: 12px; border-radius: 9px; text-align: center; }}
    .banner-title {{ font-size: 24px; font-weight: 300; letter-spacing: 5px; margin: 0; text-transform: uppercase; }}
    .info-block {{ background-color: #000000; border: 1px solid #333; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; }}
    .temp-main {{ font-size: 52px; font-weight: 200; line-height: 1.2; margin: 10px 0; }}
    .forecast-card {{ background-color: #050505; border: 1px solid #222; padding: 15px; border-radius: 10px; margin-bottom: 8px; }}
    .irr-low {{ color: #FF3131 !important; }}      
    .irr-mid {{ color: #FFFF00 !important; }}      
    .irr-high {{ color: #00FFFF !important; font-weight: 600 !important; }} 
    [data-testid="stChart"] {{ border: 1px solid #222; border-radius: 8px; padding: 10px; background-color: #020202; }}
    </style>
''', unsafe_allow_html=True)

# --- RECUPERO DATI (URL FORMATTATI PER SICUREZZA) ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    
    url_fc = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m,shortwave_radiation"
        f"&daily=temperature_2m_max,precipitation_sum,windspeed_10m_max,shortwave_radiation_sum"
        f"&timezone=Europe%2FRome"
    )
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    
    url_hist = (
        f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=precipitation,windspeed_10m,shortwave_radiation"
        f"&timezone=Europe%2FRome"
    )
    
    resp_fc = requests.get(url_fc).json()
    resp_hist = requests.get(url_hist).json()
    return resp_fc, resp_hist

try:
    data_fc, data_hist = get_weather_data()
    curr = data_fc['current_weather']
    now = datetime.now()
    data_str = f"{giorni_ita.get(now.strftime('%A'))}, {now.strftime('%d')} {mesi_ita.get(now.strftime('%B'))}"
except Exception as e:
    st.error(f"Errore API: {e}")
    st.stop()

# --- HEADER ---
st.markdown('<div class="main-banner"><div class="banner-content"><div class="banner-title">Meteo Ceredoleso Pro</div></div></div>', unsafe_allow_html=True)

# --- REAL-TIME ---
st.markdown(f'''
    <div class="info-block">
        <div style="font-size: 14px; font-weight: 300; color: #AAA !important;">{data_str}</div>
        <div style="font-size: 10px; color: #00FFFF !important; text-transform: uppercase; letter-spacing: 2px;">✨ {get_santo(now)}</div>
        <div class="temp-main">{curr['temperature']}°</div>
        <div style="font-size: 18px; color: #00FF00 !important; font-weight: 300;">💨 {curr['windspeed']} <span style="font-size:12px;">km/h</span></div>
    </div>
''', unsafe_allow_html=True)

# --- MOSTRO BOVINO INDEX ---
stato_t, stato_c, stato_d = calcola_stato_parete(data_hist)
st.markdown(f'''
    <div style="background-
