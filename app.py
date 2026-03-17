import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="🧗", layout="centered")

# --- PARAMETRI DI SOGLIA (CALIBRATI SU MAPPA) ---
THRESHOLD_LOW = 6500   
THRESHOLD_HIGH = 12000 
CORR_VAJO = 0.8  # Coefficiente ombra vajo

# --- FUNZIONE CALCOLO PERCEPITA (HEAT INDEX) ---
def calcola_percepita(T, rh):
    if T < 21:
        return T 
    hi = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (rh * 0.094))
    return round(hi, 1)

# --- UTILS ---
def get_santo(data_obj):
    santi = {"03-15": "S. Zaccaria", "03-16": "S. Eriberto", "03-17": "S. Patrizio", "03-18": "S. Cirillo", "03-19": "S. Giuseppe", "03-20": "S. Claudia", "03-21": "S. Benedetto"}
    key = data_obj.strftime("%m-%d")
    return santi.get(key, "S. del Giorno")

giorni_ita = {"Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì", "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"}
mesi_ita = {"March": "Marzo", "April": "Aprile", "May": "Maggio"}

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
st.markdown('''
<style>
.stApp { background-color: #000000 !important; }
h1, h2, h3, h4, p, span, div { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
.main-banner { background: linear-gradient(90deg, #000 0%, #00FFFF 50%, #000 100%); padding: 1px; border-radius: 10px; margin-bottom: 25px; }
.banner-content { background-color: #000; padding: 12px; border-radius: 9px; text-align: center; }
.banner-title { font-size: 24px; font-weight: 300; letter-spacing: 5px; margin: 0; text-transform: uppercase; }
.info-block { background-color: #000000; border: 1px solid #333; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
.temp-main { font-size: 52px; font-weight: 200; line-height: 1.0; margin: 10px 0; }
.temp-perceived { font-size: 16px; color: #FFA500 !important; margin-bottom: 15px; font-weight: 300; }
.forecast-card { background-color: #050505; border: 1px solid #222; padding: 15px; border-radius: 10px; margin-bottom: 8px; }
.hum-alert { font-size: 11px; color: #FFA500; text-transform: uppercase; margin-top: 8px; font-weight: bold; }
.legenda-kj { font-size: 10px; color: #666; margin-bottom: 15px; border-left: 2px solid #333; padding-left: 10px; }
</style>
''', unsafe_allow_html=True)

# --- RECUPERO DATI ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation,shortwave_radiation&daily=temperature_2m_max,precipitation_sum,shortwave_radiation_sum&timezone=Europe%2FR
