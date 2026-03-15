import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗", layout="centered")

# CSS AD ALTO CONTRASTO
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #FFFFFF !important; font-weight: bold !important; }
    .meteo-card { 
        background-color: #111111; border: 2px solid #FFFFFF; 
        border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 10px;
    }
    .bovino-container { 
        background-color: #111111; padding: 15px; border-radius: 12px; 
        margin-bottom: 15px; border: 2px solid #FFFFFF;
    }
    .bovino-name { font-size: 22px; font-weight: 900; color: #FFFFFF; }
    .progress-bg { 
        background-color: #333333; border: 1px solid #FFFFFF;
        border-radius: 10px; width: 100%; height: 20px; margin-top: 10px;
    }
    .data-table {
        width: 100%; border-collapse: collapse; color: white; margin-top: 10px;
    }
    .data-table th, .data-table td {
        border: 1px solid #444; padding: 8px; text-align: center; font-size: 14px;
    }
    .data-table th { background-color: #222; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧗 METEO CEREDO")

# --- RECUPERO DATI ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    # Forecast 3gg
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    # Storico 10gg
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data_fc, data_hist = get_all_data()

# --- PREVISIONI RAPIDE ---
cols_m = st.columns(3)
for i in range(3):
    giorno = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d').upper()
    with cols_m[i]:
        st.markdown(f'''<div class="meteo-card">
            <span style="color:#FFF;">{giorno}</span><br>
            <span style="color:#FF0000; font-size:20px;">{data_fc["daily"]["temperature_2m_max"][i]}°</span> | 
            <span style="color:#00CCFF; font-size:20px;">{data_fc["daily"]["temperature_2m_min"][i]}°</span>
        </div>''', unsafe_allow_html=True)

st.write("---")

# --- ANALISI DETTAGLIATA (SPLIT GIORNO PER GIORNO) ---
st.subheader("📊 ANALISI DETTAGLIATA (10gg Passati + 3gg Futuri)")

# Preparazione DataFrame per la tabella
history_dates = [datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m') for d in data_hist['daily']['time']]
future_dates = [datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m') for d in data_fc['daily']['time'][:3]]

all_dates = history_dates + future_dates
all_rain = data_hist['daily']['precipitation_sum'] + data_fc['daily']['precipitation_sum'][:3]
all_wind = data_hist['daily']['wind_speed_10m_max'] + data_fc['daily']['wind_speed_10m_max'][:3]

df_dettaglio = pd.DataFrame({
    'Data': all_dates,
    'Pioggia (mm)': all_rain,
    'Vento (km/h)': all_wind
})

# Mostriamo lo split in un expander per non intasare lo schermo
with st.expander("👁️ VEDI SPLIT GIORNALIERO PIOGGIA E VENTO"):
    st.write("Dati usati per il calcolo del Mostro Bovino Index:")
    # Formattazione condizionale: pioggia in azzurro, vento in bianco
    st.dataframe(df_dettaglio.style.format({'Pioggia (mm)': '{:.1f}', 'Vento (km/h)': '{:.1f}'})
                 .highlight_max(subset=['Vento (km/h)'], color='#111')
                 .highlight_between(left=0.1, subset=['Pioggia (mm)'], color='#004466'))

st.write("---")

# --- MOSTRO BOVINO INDEX ---
st.header("🐂 MOSTRO BOVINO INDEX")

def get_bovino_score(day_offset, boost):
    # Somma pioggia (10gg passati + n giorni futuri)
    total_rain = sum(data_hist['daily']['precipitation_sum']) + sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    # Media vento
    avg_wind = np.mean(data_hist['daily']['wind_speed_10m_max'] + data_fc['daily']['wind_speed_10m_max'][:day_offset+1])
    # Sole
    total_sun = (sum(data_hist['daily']['sunshine_duration']) + sum(data_fc['daily']['sunshine_duration'][:day_offset+1])) / 3600
    
    # Formula: Sole e Vento aiutano, Pioggia penalizza pesantemente
    bias = (total_sun * 0.005 * boost) + (avg_wind * 0.002) - (total_rain * 0.14)
    return np.clip(bias, -0.30, 0.15)

settori = [
    ("🔥 MANGIAFUOCO", 75, 4, 1.25), ("🎋 SUPERCANNA", 70, 5, 1.20),
    ("🐕 MONDO CANO", 70, 5, 1.10), ("🧠 CEREDOLESO", 77, 3, 1.00),
    ("👴 DEL PECI", 67, 4, 0.85), ("🏺 OSTRAMANDRA", 60, 6, 0.70)
]

tabs = st.tabs(["OGGI", "DOMANI", "DOPODOMANI"])
for day in range(3):
    with tabs[day]:
        for nome, base, toll, boost in settori:
            bias = get_bovino_score(day, boost)
            prob = int(base + (bias * 100))
            min_p, max_p = np.clip([prob-toll, prob+toll], 0, 100)
            color = "#00FF00" if min_p > 70 else "#FFFF00" if min_p > 50 else "#FF0000"
            
            st.markdown(f"""
                <div class="bovino-container">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="bovino-name">🐂 {nome}</div>
                        <div style="font-size: 26px; font-weight: 900; color:{color};">{min_p}-{max_p}%</div>
                    </div>
                    <div class="progress-bg">
                        <div style="width: {min_p}%; background-color: {color}; height:100%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

if st.button("🔄 AGGIORNA DATI"):
    st.rerun()
