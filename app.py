import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Meteo Ceredo Pro", page_icon="🧗", layout="centered")

# CSS AD ALTO CONTRASTO SENZA ICONE NEI DATI
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3, p, span, label { color: #FFFFFF !important; font-weight: bold !important; }
    
    /* Box Indice */
    .bovino-container { 
        background-color: #111111; padding: 15px; border-radius: 12px; 
        margin-bottom: 15px; border: 2px solid #FFFFFF;
    }
    .bovino-name { font-size: 22px; font-weight: 900; color: #FFFFFF; }
    
    /* Barra progresso */
    .progress-bg { 
        background-color: #333333; border: 1px solid #FFFFFF;
        border-radius: 10px; width: 100%; height: 20px; margin-top: 10px;
    }
    
    /* Tabella Dati */
    .stDataFrame { background-color: #000000 !important; border: 1px solid #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧗 METEO CEREDO")

# --- RECUPERO DATI ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,wind_speed_10m_max,sunshine_duration&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data_fc, data_hist = get_all_data()

# --- SPLIT GIORNALIERO (SOLO NUMERI) ---
st.subheader("📊 DATI PIOGGIA E VENTO (13 GG)")

# Creazione array dati
history_dates = [datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m') for d in data_hist['daily']['time']]
future_dates = [datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m') for d in data_fc['daily']['time'][:3]]

all_dates = history_dates + future_dates
all_rain = data_hist['daily']['precipitation_sum'] + data_fc['daily']['precipitation_sum'][:3]
all_wind = data_hist['daily']['wind_speed_10m_max'] + data_fc['daily']['wind_speed_10m_max'][:3]

# DataFrame pulito
df_clean = pd.DataFrame({
    'DATA': all_dates,
    'PIOGGIA mm': all_rain,
    'VENTO km/h': all_wind
})

# Visualizzazione tabella diretta (no icone)
st.dataframe(
    df_clean, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "DATA": st.column_config.TextColumn("DATA"),
        "PIOGGIA mm": st.column_config.NumberColumn("PIOGGIA mm", format="%.1f"),
        "VENTO km/h": st.column_config.NumberColumn("VENTO km/h", format="%.0f")
    }
)

st.write("---")

# --- MOSTRO BOVINO INDEX ---
st.header("🐂 MOSTRO BOVINO INDEX")

def get_bovino_score(day_offset, boost):
    total_rain = sum(data_hist['daily']['precipitation_sum']) + sum(data_fc['daily']['precipitation_sum'][:day_offset+1])
    avg_wind = np.mean(data_hist['daily']['wind_speed_10m_max'] + data_fc['daily']['wind_speed_10m_max'][:day_offset+1])
    total_sun = (sum(data_hist['daily']['sunshine_duration']) + sum(data_fc['daily']['sunshine_duration'][:day_offset+1])) / 3600
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

if st.button("🔄 AGGIORNA"):
    st.rerun()
