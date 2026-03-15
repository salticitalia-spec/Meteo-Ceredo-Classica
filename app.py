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

# CSS Migliorato
st.markdown("""
    <style>
    .meteo-card { background-color: #1E1E1E; border: 2px solid #444; border-radius: 15px; padding: 10px; text-align: center; color: white !important; }
    .bovino-container { background-color: #262730; padding: 15px; border-radius: 15px; margin-bottom: 15px; border: 1px solid #444; }
    .bovino-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .bovino-name { font-size: 18px; font-weight: bold; color: white; }
    .bovino-perc { font-size: 20px; font-weight: bold; }
    .progress-bg { background-color: #444; border-radius: 20px; width: 100%; height: 12px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 20px; transition: width 0.5s ease-in-out; }
    .stMetric { background-color: #1E1E1E; padding: 10px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧗 Meteo Ceredo")

# --- FUNZIONI DATI ---
def get_all_data():
    lat, lon = 45.6117, 10.9710
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,sunshine_duration,precipitation_probability_max&timezone=Europe%2FRome"
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
        st.markdown(f'<div class="meteo-card"><b>{giorno}</b><br><b style="color:#FF4B4B">{data_fc["daily"]["temperature_2m_max"][i]}°</b> | <b style="color:#00ACF2">{data_fc["daily"]["temperature_2m_min"][i]}°</b></div>', unsafe_allow_html=True)

st.write("---")

# --- 2. ANALISI PIOGGIA (STORICO + FUTURO) ---
st.subheader("💧 Analisi Precipitazioni")
c1, c2 = st.columns(2)

# Storico 10gg
rain_10d = sum(data_hist['daily']['precipitation_sum'])
c1.metric("Pioggia ultimi 10gg", f"{rain_10d:.1f} mm", delta="- asciutto" if rain_10d > 0 else "secco", delta_color="inverse")

# Previsione 3gg
rain_3d = sum(data_fc['daily']['precipitation_sum'][:3])
c2.metric("Stima pioggia prossimi 3gg", f"{rain_3d:.1f} mm", delta="+ bagnato" if rain_3d > 0 else "stabile", delta_color="inverse")

# Grafico combinato pioggia (Storico 10gg)
with st.expander("Vedi dettaglio pioggia giornaliera (10gg passati)"):
    df_hist = pd.DataFrame({
        'Giorno': [d[-5:] for d in data_hist['daily']['time']],
        'Pioggia (mm)': data_hist['daily']['precipitation_sum']
    })
    st.bar_chart(df_hist, x='Giorno', y='Pioggia (mm)', color="#00ACF2")

st.write("---")

# --- 3. MOSTRO BOVINO INDEX ---
st.header("🐂 Mostro Bovino Index (analisi asciugatura)")

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
            color = "#28a745" if min_p > 70 else "#fd7e14" if min_p > 50 else "#dc3545"
            st.markdown(f"""
                <div class="bovino-container">
                    <div class="bovino-header">
                        <div class="bovino-name">🐂 {nome}</div>
                        <div class="bovino-perc" style="color:{color};">{min_p}-{max_p}%</div>
                    </div>
                    <div class="progress-bg"><div class="progress-fill" style="width: {min_p}%; background-color: {color};"></div></div>
                </div>
            """, unsafe_allow_html=True)

if st.button("🔄 AGGIORNA DATI"):
    st.rerun()
