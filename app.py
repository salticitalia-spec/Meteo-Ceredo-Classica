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

st.title("🧗 Meteo Ceredo - Mostro Bovino")

lat, lon = 45.6117, 10.9710

def get_all_data():
    url_fc = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation_probability,weathercode&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,sunshine_duration,wind_speed_10m_max&timezone=Europe%2FRome"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)
    url_hist = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,sunshine_duration,wind_speed_10m_max&timezone=Europe%2FRome"
    return requests.get(url_fc).json(), requests.get(url_hist).json()

data_fc, data_hist = get_all_data()

# --- ALGORITMO MOSTRÒ BOVINO AVANZATO ---
def get_bovino_for_day(day_offset, h_data, f_data, expo_boost):
    # expo_boost simula il vantaggio del sole mattutino rispetto a quello pomeridiano
    rain = sum(h_data['daily']['precipitation_sum']) + sum(f_data['daily']['precipitation_sum'][:day_offset+1])
    sun = (sum(h_data['daily']['sunshine_duration']) + sum(f_data['daily']['sunshine_duration'][:day_offset+1])) / 3600
    
    # Parametro dinamico: il sole mattutino (Mangiafuoco) asciuga prima la condensa
    bias = (sun * 0.005 * expo_boost) - (rain * 0.14)
    return np.clip(bias, -0.30, 0.15)

# --- DATABASE SETTORI CON CRONOLOGIA SOLE ---
# Ordine cronologico di arrivo del sole (09:30 -> Pomeriggio tardi)
settori_ordinati = [
    ("🔥 MANGIAFUOCO", (75, 4, 1.25)), # Sole ore 09:30 - Top asciugatura
    ("🎋 SUPERCANNA", (70, 5, 1.20)),  # Segue a ruota
    ("🐕 MONDO CANO", (70, 5, 1.10)),  # Sole tarda mattinata
    ("🧠 CEREDOLESO", (77, 3, 1.00)),  # Sole intorno a mezzogiorno
    ("👴 DEL PECI", (67, 4, 0.85)),    # Sole primo pomeriggio
    ("🏺 OSTRAMANDRA", (60, 6, 0.70))  # Sole tardi - Molto lenta
]

# --- UI PREVISIONI ---
st.subheader("📅 Previsioni Meteo")
cols_m = st.columns(3)
for i in range(3):
    giorno = datetime.strptime(data_fc['daily']['time'][i], '%Y-%m-%d').strftime('%a %d')
    ico, txt = get_weather_info(data_fc['daily']['weathercode'][i]) if 'get_weather_info' in globals() else ("🌤️", "Variabile")
    with cols_m[i]:
        st.markdown(f"<div style='background:#1E1E1E;padding:8px;border-radius:10px;text-align:center;border:1px solid #444;'>"
                    f"<b>{giorno}</b><br>{data_fc['daily']['temperature_2m_max'][i]}°C</div>", unsafe_allow_html=True)

st.write("---")

# --- UI INDEX ---
st.header("🐂 MOSTRO BOVINO INDEX")
st.caption("Stima in base a: pioggia 10gg + vento + cronologia sole")

tabs = st.tabs(["OGGI", "DOMANI", "DOPODOMANI"])

for day in range(3):
    with tabs[day]:
        for nome, (base, toll, boost) in settori_ordinati:
            bias = get_bovino_for_day(day, data_hist, data_fc, boost)
            prob_base = base + (bias * 100)
            min_p, max_p = int(prob_base - toll), int(prob_base + toll)
            min_p, max_p = np.clip([min_p, max_p], 0, 100)
            
            color = "#28a745" if min_p > 70 else "#fd7e14" if min_p > 50 else "#dc3545"
            st.markdown(f"""
            <div style='background:#262730; padding:12px; border-radius:10px; margin-bottom:10px; border-left: 10px solid {color}; display: flex; justify-content: space-between; align-items: center;'>
                <div style='font-weight: bold; color: white; font-size: 16px;'>{nome}</div>
                <div style='font-weight: bold; color: {color}; font-size: 20px;'>{min_p}-{max_p}%</div>
            </div>
            """, unsafe_allow_html=True)

# Grafico veloce pioggia per conferma visiva
with st.expander("📊 Verifica Pioggia ultimi 10gg"):
    df_p = pd.DataFrame({'Giorno': [d[-5:] for d in data_hist['daily']['time']], 'mm': data_hist['daily']['precipitation_sum']})
    st.bar_chart(df_p, x='Giorno', y='mm')

if st.button("🔄 AGGIORNA"):
    st.rerun()
