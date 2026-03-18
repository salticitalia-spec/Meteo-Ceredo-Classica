import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE PAGINA (Obbligatoria come prima riga) ---
st.set_page_config(page_title="Meteo Ceredoleso Pro", page_icon="攀", layout="centered")

# --- 2. PARAMETRI TECNICI ---
THRESHOLD_LOW, THRESHOLD_HIGH, CORR_VAJO = 6500, 12000, 0.8

# --- 3. FUNZIONI DI SUPPORTO ---
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

# --- 4. CSS CUSTOM (UNIFORMATO E POTENZIATO +20%) ---
st.markdown('''
<style>
    .stApp { background-color: #000; }
    .main-banner {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("icona.png");
        background-size: cover; background-position: center;
        padding: 30px 5px; border-radius: 12px; border: 1px solid #1a1a1a;
        text-align: center; margin-bottom: 25px;
        display: flex; justify-content: center; align-items: center;
    }
    .title-wrapper { display: flex; flex-direction: column; align-items: flex-end; }
    
    .title-ceredoleso { 
        color: #0FF !important; 
        font-weight: 100 !important; 
        font-size: 26px; 
        letter-spacing: 7px; 
        margin: 0; 
        text-transform: uppercase; 
        line-height: 1; 
        font-family: sans-serif;
    }
    
    .title-pro { 
        color: #0FF !important; 
        font-weight: 100 !important; 
        font-size: 18px; 
        letter-spacing: 5px; 
        margin-top: 5px; 
        text-transform: uppercase; 
        font-family: sans-serif;
        opacity: 0.9; 
    }
    
    .date-text { 
        font-family: sans-serif;
        font-weight: 100 !important;
        font-size: 24px; 
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin-bottom: 5px;
    }

    .info-card {
        background-color: #0c0c0c; border: 1px solid #222;
        padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 15px;
    }
    .t-main { font-size: 45px; font-weight: bold; color: #fff; margin: 5px 0; }
    .t-perc { font-size: 14px; color: #FF0; margin-bottom: 10px; font-weight: 300; }
    .rain-tag { color: #F31; font-size: 11px; font-weight: bold; border: 1px solid #F31; padding: 4px 10px; border-radius: 5px; display: inline-block; margin: 10px 0; }
    .val-box { display: flex; justify-content: center; gap: 15px; font-size: 17px; margin-top: 10px; }
    .status-alert { font-size: 11px; color: #FF0; font-weight: bold; margin-top: 10px; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stChart"] { border: 1px solid #222; border-radius: 10px; padding: 10px; background-color:#020202; }
</style>
''', unsafe_allow_html=True)

# --- 5. DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation,shortwave_radiation,weathercode,windspeed_10m&daily=temperature_2m_max,precipitation_sum,shortwave_radiation_sum,weathercode,windspeed_10m_max&timezone=Europe%2FRome"
    end_d = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_d = (datetime.now() - timedelta(days=11)).
