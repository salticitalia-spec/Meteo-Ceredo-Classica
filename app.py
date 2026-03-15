import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import os

# --- CONFIGURAZIONE ---
if os.path.exists("icona.png"):
    img_icona = Image.open("icona.png")
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon=img_icona, layout="centered")
else:
    st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗")

# CSS AD ALTO CONTRASTO
st.markdown("""
    <style>
    /* Sfondo generale e font */
    .stApp { background-color: #0E1117; }
    
    /* Box Previsioni in alto */
    .meteo-card { 
        background-color: #000000; 
        border: 2px solid #FFFFFF; 
        border-radius: 12px; 
        padding: 12px; 
        text-align: center; 
        color: #FFFFFF !important;
        margin-bottom: 10px;
    }
    
    /* Box Mostro Bovino */
    .bovino-container { 
        background-color: #000000; 
        padding: 18px; 
        border-radius: 15px; 
        margin-bottom: 15px; 
        border: 3px solid #555; /* Bordo grigio chiaro molto visibile */
    }
    
    .bovino-name { font-size: 20px; font-weight: 900; color: #FFFFFF; }
    .bovino-perc { font-size: 24px; font-weight: 900; }
    
    /* Barra progresso */
    .progress-bg { 
        background-color: #333; 
        border: 1px solid #777;
        border-radius: 20px; 
        width: 100%; 
        height: 16px; 
        overflow: hidden; 
        margin-top: 10px;
    }
    
    /* Testi Metric (Pioggia) */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 900 !important; font-size: 30px !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-weight: bold !important; font-size: 16px !important; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold !important; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧗 Meteo Ceredo")

# --- FUNZIONI DATI ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,sunshine_duration&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data_fc, data_hist = get_all_data()

# --- 1. PREVISIONI GENERALI ---
cols_m = st.columns(3)
for i in range(3):
    giorno = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d')
    with cols_m[i]:
        st.markdown(f'''<div class="meteo-card">
            <b style="font-size:16px;">{giorno.upper()}</b><br>
            <span style="color:#FF3333; font-size:20px;">{data_fc["daily"]["temperature_2m_max"][i]}°</span><br>
            <span style="color:#33CCFF; font-size:20px;">{data_fc["daily"]["temperature_2m_min"][i]}°</span>
        </div>''', unsafe_allow_html=True)

st.write("---")

# --- 2. ANALISI PIOGGIA ---
st.markdown("### 💧 ANALISI PRECIPITAZIONI")
c1, c2 = st.columns(2)
rain_10d = sum(data_hist['daily']['precipitation_sum'])
rain_3d = sum(data_fc['daily']['precipitation_sum'][:3])

c1.metric("ULTIMI 10 GG", f"{rain_10d:.1f} mm")
c2.metric("PROSSIMI 3 GG", f"{rain_3d:.1f} mm")

st.write("---")

# --- 3. MOSTRO BOVINO INDEX ---
st.markdown("## 🐂 MOSTRO BOVINO INDEX")
st.caption("Percentuale di asciutto stimata per settore")

def get_bovino_score(day_offset, boost):
    rain_p = sum(data_hist['daily']['precipitation_sum'])
    rain_f = sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    sun_p = sum(data_hist['daily']['sunshine_duration']) / 3600
    sun_f = sum(data_fc['daily']['sunshine_duration'][:day_offset+1]) / 3600
    bias = ((sun_p + sun_f) * 0.005 * boost) - ((rain_p + rain_f) * 0.14)
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
            
            # Colori ad alto contrasto
            color = "#00FF00" if min_p > 70 else "#FFCC00" if min_p > 50 else "#FF0000"
            
            st.markdown(f"""
                <div class="bovino-container">
                    <div class="bovino-header">
                        <div class="bovino-name">🐂 {nome}</div>
                        <div class="bovino-perc" style="color:{color};">{min_p}-{max_p}%</div>
                    </div>
                    <div class="progress-bg">
                        <div style="width: {min_p}%; background-color: {color}; height:100%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.write("---")
if st.button("🔄 AGGIORNA DATI"):
    st.rerun()
